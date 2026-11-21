"""Clean computational-cost benchmark (review cycle 2, R7). Run ALONE, after all models are cached:

    OMP_NUM_THREADS=1 python scripts/timing_benchmark.py

* calibration (single thread): for every seed of each dataset, LOBO tuning of the recommended layer and the
  per-building-day cost of the WHOLE online step -- binning the new day's 24 scores into the building's state
  (decayed cumulative counts) plus one radius -- for the recommended layer, QShrink-CQR (cov) and ACI-CQR;
  batch application; median and IQR over repetitions and seeds;
* forecaster: LightGBM inference of the three models per building-day (1 thread), seed 0; training time of the
  three LightGBM models and two MLPs (4 threads), seed 0, one run (reported as such);
* memory per component: tuning store (calibration counts), deployment prior (one grid vector), per-building state.
Output: results/timing.json (manuscript/values.py, manuscript_tables.cost_table).
"""
import json
import os
import platform
import sys
import time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from src import experiments as ex  # noqa: E402
from src.training import pipeline as pl  # noqa: E402
from src.models import calibration as cb  # noqa: E402
from src.preprocessing import features as fe  # noqa: E402

SEEDS = [0, 1, 2, 3, 4]


def reps_time(f, reps):
    f()
    ts = []
    for _ in range(reps):
        t0 = time.perf_counter()
        f()
        ts.append(time.perf_counter() - t0)
    return ts


def stat(ts, scale=1.0):
    a = np.asarray(ts) * scale
    return dict(median=float(np.median(a)), q25=float(np.quantile(a, 0.25)), q75=float(np.quantile(a, 0.75)),
                n=int(len(a)))


def online_step(state, new_scores, prior, kappa, decay, alpha):
    """One building, one day: bin 24 new scores, update the decayed state, compute the radius."""
    v = new_scores[~np.isnan(new_scores)]
    c = np.cumsum(np.bincount(np.minimum(np.searchsorted(cb.GRID, v, side="left"), len(cb.GRID) - 1),
                              minlength=len(cb.GRID)))
    state *= decay
    state += c
    M = (kappa * prior + state) / (kappa + state[-1] + 1.0)
    return cb.GRID[np.argmax(M >= 1 - alpha - 1e-6)]


def main():
    out = dict(cpu=platform.processor() or platform.machine(), logical_cpus=os.cpu_count(),
               omp_threads=os.environ.get("OMP_NUM_THREADS", "unset"), python=platform.python_version())
    stages = np.arange(1, pl.NH + 1)
    for dsn in ["BDG2", "UCI"]:
        ds = ex.get_ds(dsn)
        w = ds["temp"] is not None
        T = {k: [] for k in ["tune", "online_recency", "online_qshrink", "batch_recency", "batch_aci", "batch_cqr"]}
        r = {}
        for s in SEEDS:
            obj = ex.prepared(dsn, dsn, s, "random", None, w, 0.4, True)
            PC, PT = obj["PC"], obj["PT"]
            Scq, Stq = pl.scores_cqr(PC), pl.scores_cqr(PT)
            bw = PC["qhi"] / PC["s"][:, :, None] - PC["qlo"] / PC["s"][:, :, None]
            nt, per = Stq.shape[0], Stq.shape[0] * pl.NH
            T["tune"] += reps_time(lambda: pl.tune_hsc(Scq, bw, PC["z"], 0.1, stage_matched=False, Ks=[None],
                                                       objective="cov", decay=pl.RECENCY), 3)
            best, _ = pl.tune_hsc(Scq, bw, PC["z"], 0.1, stage_matched=False, Ks=[None], objective="cov",
                                  decay=pl.RECENCY)
            kap = best["kappa"]
            binc, _ = cb.bin_cdfs(cb.cum_counts(Scq), stages)
            pooled = binc.sum(axis=(0, 1)).astype(np.float64)
            prior = pooled / max(pooled[-1], 1)
            # whole online step for one building-day (binning + state update + radius), many building-days
            days = Stq[:, :, :].reshape(-1, 24)[:2000]

            def run_online(dec, kp):
                st = np.zeros(len(cb.GRID))
                for d in days:
                    online_step(st, d, prior, kp, dec, 0.1)
            T["online_recency"] += [t / len(days) for t in reps_time(lambda: run_online(pl.RECENCY, kap), 5)]
            T["online_qshrink"] += [t / len(days) for t in reps_time(lambda: run_online(1.0, 0.0), 5)]
            # batch application including binning of all target scores
            T["batch_recency"] += [t / per for t in reps_time(lambda: cb.hsc_quantiles(
                cb.cum_counts(Stq), binc, None, 0.1, [kap], stages, stage_matched=False, decay=pl.RECENCY), 5)]
            T["batch_aci"] += [t / per for t in reps_time(lambda: cb.aci_quantiles(
                Stq, binc.sum(axis=0), 0.1, 0.002, stages), 5)]
            T["batch_cqr"] += [t / per for t in reps_time(lambda: cb.pooled_quantile(binc, 0.1, True)[None]
                                                         * np.ones((nt, 1)), 5)]
            if s == 0:
                m = obj["models"]
                b, t0 = obj["tgt_idx"][:1], obj["t0t"][:1]
                X, _, _ = fe.build(ds["load"], ds["temp"], ds["dates"], b, t0 + 28, np.array([28]), m["use_weather"])
                r["lgb_inference_ms_per_building_day"] = stat(reps_time(
                    lambda: [m[k].predict(X, num_threads=1) for k in ("lgb", "lgb_lo", "lgb_hi")], 50), 1e3)
                r["feature_ms_per_building_day"] = stat(reps_time(lambda: fe.build(
                    ds["load"], ds["temp"], ds["dates"], b, t0 + 28, np.array([28]), m["use_weather"]), 50), 1e3)
                r["lgb_3models_train_s_seed0"] = float(m["time_lgb"])
                r["mlp_2models_train_s_seed0"] = float(m.get("time_mlp") or np.nan)
                r["n_train_rows"] = int(m["n_train_rows"])
                ncal = Scq.shape[0]
                r["memory_MB"] = dict(
                    tuning_counts=float(ncal * pl.NH * len(cb.GRID) * 2 / 1e6),  # int16 LOBO counts
                    deployment_prior=float(len(cb.GRID) * 4 / 1e6),
                    per_building_state=float(len(cb.GRID) * 4 / 1e6))
                r["n_cal"], r["n_targets"], r["kappa_seed0"] = int(ncal), int(nt), float(kap)
        r["recency_tune_s"] = stat(T["tune"])
        r["online_step_ms_recency"] = stat(T["online_recency"], 1e3)
        r["online_step_ms_self_counts"] = stat(T["online_qshrink"], 1e3)
        r["batch_ms_per_building_day"] = {k[6:]: stat(T[k], 1e3) for k in T if k.startswith("batch_")}
        # backwards-compatible keys used by values.py
        r["recency_apply_ms_per_building_day"] = r["online_step_ms_recency"]["median"]
        r["cqr_apply_ms_per_building_day"] = r["batch_ms_per_building_day"]["cqr"]["median"]
        r["aci_apply_ms_per_building_day"] = r["batch_ms_per_building_day"]["aci"]["median"]
        r["store_MB"] = r["memory_MB"]["tuning_counts"]
        r["lgb_3models_s"] = r["lgb_3models_train_s_seed0"]
        r["mlp_2models_s"] = r["mlp_2models_train_s_seed0"]
        r["recency_tune_s_median"] = r["recency_tune_s"]["median"]
        out[dsn] = r
        print(dsn, json.dumps(r, default=float)[:600], flush=True)
    json.dump(out, open(os.path.join(ROOT, "results", "timing.json"), "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
