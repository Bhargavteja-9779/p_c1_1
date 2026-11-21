"""Isolated timing benchmark (revision 1, reviewer R7). One process, OMP_NUM_THREADS=1, run after all
other jobs finished; cached models/predictions only. Reports median and IQR over repetitions for
  * LOBO tuning of the recommended layer (uniform prior, kappa grid; both objectives computed),
  * batch application to all targets (per target-day, amortised),
  * single-building daily update latency: bin the 24 new scores into the building's count vector, mix
    with the prior CDF and search the quantile (what runs once per building per day in deployment),
and the per-building online state size. Writes tables/T_timing.{md,csv}."""
from __future__ import annotations

import os
import time

import numpy as np
import pandas as pd

from src import experiments as ex
from src.models import calibration as cb
from src.training import pipeline as pl

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _rep(f, n):
    ts = []
    for _ in range(n):
        t0 = time.perf_counter()
        f()
        ts.append(time.perf_counter() - t0)
    return np.median(ts), np.quantile(ts, 0.25), np.quantile(ts, 0.75)


def run(seed=0):
    rows = []
    stages = np.arange(1, pl.NH + 1)
    for dsn in ["BDG2", "UCI"]:
        ds = ex.get_ds(dsn)
        obj = ex.prepared(dsn, dsn, seed, "random", None, ds["temp"] is not None, 0.4, True)
        PC, PT = obj["PC"], obj["PT"]
        Scq, Stq = pl.scores_cqr(PC), pl.scores_cqr(PT)
        bw = PC["qhi"] / PC["s"][:, :, None] - PC["qlo"] / PC["s"][:, :, None]
        ncal, nt = Scq.shape[0], Stq.shape[0]
        m, a, b = _rep(lambda: pl.tune_hsc(Scq, bw, PC["z"], 0.1, stage_matched=False, Ks=[None],
                                           objective="MACD"), 3)
        rows.append(dict(dataset=dsn, step="LOBO tuning (κ grid, uniform prior)", n_cal=ncal, median_s=m, q25_s=a,
                         q75_s=b))
        bincq, _ = cb.bin_cdfs(cb.cum_counts(Scq), stages)
        cct = cb.cum_counts(Stq)
        m, a, b = _rep(lambda: cb.hsc_quantiles(cct, bincq, None, 0.1, [168], stages, stage_matched=False), 5)
        rows.append(dict(dataset=dsn, step="batch application, per target-day (ms)", n_cal=ncal,
                         median_s=1e3 * m / (nt * pl.NH), q25_s=1e3 * a / (nt * pl.NH), q75_s=1e3 * b / (nt * pl.NH)))
        # single-building daily update
        C = bincq.sum(axis=(0, 1)).astype(np.float64)
        FP = C / C[-1]
        own = np.zeros(len(cb.GRID))
        new = Stq[0, 10]

        def upd():
            v = new[~np.isnan(new)]
            idx = np.minimum(np.searchsorted(cb.GRID, v, side="left"), len(cb.GRID) - 1)
            own_ = own + np.cumsum(np.bincount(idx, minlength=len(cb.GRID)))
            n = own_[-1]
            M = (168 * FP + own_) / (168 + n + 1.0)
            return cb.GRID[np.searchsorted(M, 0.9 - 1e-9)]
        m, a, b = _rep(upd, 2000)
        rows.append(dict(dataset=dsn, step="single-building daily update (ms)", n_cal=ncal, median_s=1e3 * m,
                         q25_s=1e3 * a, q75_s=1e3 * b))
        rows.append(dict(dataset=dsn, step="online state per building (kB, float32 counts)", n_cal=ncal,
                         median_s=len(cb.GRID) * 4 / 1e3, q25_s=np.nan, q75_s=np.nan))
    t = pd.DataFrame(rows)
    t.to_csv(os.path.join(ROOT, "tables", "T_timing.csv"), index=False)
    with open(os.path.join(ROOT, "tables", "T_timing.md"), "w") as f:
        f.write("**Isolated timing (one process, 1 thread; median [IQR] over repetitions). Units in the step "
                "name, otherwise seconds.**\n\n" + t.round(5).to_markdown(index=False) + "\n")
    return t
