"""Isolated timing benchmark (revision 1, reviewer R7).

Run ALONE (no concurrent experiment processes), after all models are cached:
    OMP_NUM_THREADS=1 python scripts/benchmark_timing.py
Reports median and IQR over repetitions, for the primary one-parameter layer (HSC-CQR simple) and the main
competitors, on seed 0 of each dataset: LOBO tuning, batch application (all targets x 56 days) and the
incremental single-building daily update (one new day of 24 scores + one radius), plus LightGBM inference of
the three models for one building-day and feature construction. Output: tables/T_timing.{csv,md}.
"""
import os
import platform
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from src import experiments as ex  # noqa: E402
from src.training import pipeline as pl  # noqa: E402
from src.models import calibration as cb  # noqa: E402
from src.preprocessing import features as fe  # noqa: E402

REPS_FAST, REPS_TUNE = 20, 5


def timeit(f, reps):
    f()  # warm-up
    ts = []
    for _ in range(reps):
        t0 = time.perf_counter()
        f()
        ts.append(time.perf_counter() - t0)
    return np.median(ts), np.quantile(ts, 0.25), np.quantile(ts, 0.75)


def main():
    rows = []
    stages = np.arange(1, pl.NH + 1)
    for dsn in ["BDG2", "UCI"]:
        ds = ex.get_ds(dsn)
        obj = ex.prepared(dsn, dsn, 0, "random", None, ds["temp"] is not None, 0.4, True)
        PC, PT, models = obj["PC"], obj["PT"], obj["models"]
        Scq, Stq = pl.scores_cqr(PC), pl.scores_cqr(PT)
        bw = PC["qhi"] / PC["s"][:, :, None] - PC["qlo"] / PC["s"][:, :, None]
        nt, ncal = Stq.shape[0], Scq.shape[0]
        bincq, _ = cb.bin_cdfs(cb.cum_counts(Scq), stages)
        cct = cb.cum_counts(Stq)
        best, _ = pl.tune_hsc(Scq, bw, PC["z"], 0.1, stage_matched=False, Ks=[None], objective="macd")
        kap = best["kappa"]
        sb = cb.stage_bin(stages)
        qpool = cb.pooled_quantile(bincq, 0.1, True)[sb]

        def add(method, what, f, reps, per=1):
            m, a, b = timeit(f, reps)
            rows.append(dict(dataset=dsn, method=method, operation=what, median_ms=1e3 * m / per,
                             iqr_ms=f"[{1e3 * a / per:.4g}, {1e3 * b / per:.4g}]", reps=reps, n_cal=ncal, n_tgt=nt))

        add("HSC-CQR simple (primary)", "LOBO tuning (9 kappa)", lambda: pl.tune_hsc(
            Scq, bw, PC["z"], 0.1, stage_matched=False, Ks=[None], objective="macd"), REPS_TUNE)
        add("HSC-CQR full", "LOBO tuning (5 K x 9 kappa)", lambda: pl.tune_hsc(Scq, bw, PC["z"], 0.1), 2)
        add("QShrink-CQR", "LOBO tuning", lambda: pl.tune_qshrink(Scq, bw, 0.1), REPS_TUNE)
        add("Self-CQR-fb", "LOBO tuning", lambda: pl.tune_selffb(Scq, bw, 0.1), REPS_TUNE)
        add("ACI-CQR", "LOBO tuning", lambda: pl.tune_aci(Scq, 0.1), REPS_TUNE)
        per = nt * pl.NH
        add("HSC-CQR simple (primary)", "apply, per building-day (batch)", lambda: cb.hsc_quantiles(
            cct, bincq, None, 0.1, [kap], stages, stage_matched=False), REPS_FAST, per)
        add("CQR", "apply, per building-day (batch)", lambda: cb.pooled_quantile(bincq, 0.1, True), REPS_FAST, per)
        add("QShrink-CQR", "apply, per building-day (batch)", lambda: cb.qshrink_quantiles(
            cct, qpool, 0.1, 168, stages), REPS_FAST, per)
        add("ACI-CQR", "apply, per building-day (batch)", lambda: cb.aci_quantiles(
            Stq, bincq.sum(axis=0), 0.1, 0.001, stages), REPS_FAST, per)

        # incremental daily update of one building: add 24 new scores to its counts, recompute one radius
        prior = (bincq.sum(axis=(0, 1)) / max(bincq.sum(axis=(0, 1))[-1], 1)).astype(np.float64)
        own = np.zeros(len(cb.GRID))
        new = Stq[0, 10]

        def incr():
            idx = np.searchsorted(cb.GRID, new[~np.isnan(new)], side="left")
            c = np.cumsum(np.bincount(np.minimum(idx, len(cb.GRID) - 1), minlength=len(cb.GRID)))
            o = own + c
            M = (kap * prior + o) / (kap + o[-1] + 1.0)
            return cb.GRID[np.argmax(M >= 0.9 - 1e-6)]
        add("HSC-CQR simple (primary)", "incremental update, one building-day", incr, 200)

        # forecaster: features + 3 LightGBM predictions for one building-day (1 thread)
        b, t0 = obj["tgt_idx"][:1], obj["t0t"][:1]

        def feat():
            return fe.build(ds["load"], ds["temp"], ds["dates"], b, t0 + 28, np.array([28]),
                            models["use_weather"])
        X = feat()[0]
        add("forecaster", "feature construction, one building-day", feat, 50)
        add("forecaster", "3 LightGBM predictions, one building-day", lambda: [
            models[k].predict(X, num_threads=1) for k in ("lgb", "lgb_lo", "lgb_hi")], 50)
        rows.append(dict(dataset=dsn, method="store", operation="pooled score CDF (MB, float32)",
                         median_ms=bincq.astype(np.float32).nbytes / 1e6, iqr_ms="", reps=0, n_cal=ncal, n_tgt=nt))
    df = pd.DataFrame(rows)
    os.makedirs(os.path.join(ex.ROOT, "tables"), exist_ok=True)
    df.to_csv(os.path.join(ex.ROOT, "tables", "T_timing.csv"), index=False)
    hdr = (f"**Isolated timing benchmark** ({platform.processor() or platform.machine()}, "
           f"{os.cpu_count()} logical CPUs, OMP_NUM_THREADS={os.environ.get('OMP_NUM_THREADS', 'unset')}, "
           f"no concurrent jobs; median and IQR over repetitions; 'store' row in MB)\n\n")
    with open(os.path.join(ex.ROOT, "tables", "T_timing.md"), "w") as f:
        f.write(hdr + df.to_markdown(index=False) + "\n")
    print(df.to_string())


if __name__ == "__main__":
    main()
