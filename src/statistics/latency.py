"""Single-building latency of the daily PCS update (v2, review cycle 1: cost of the recommended layer).

State kept per building: cumulative own-score counts on the score grid (int32, len(GRID)). Daily update:
insert the 24 new hourly scores, then compute the radius of the mixture (kappa * F_prior + own counts) /
(kappa + n + 1) at level 1 - alpha. The pooled prior CDF (one float vector) is shared by all buildings.
Run single-threaded:  OMP_NUM_THREADS=1 python -m src.statistics.latency
"""
from __future__ import annotations

import json
import os
import time

import numpy as np

from src.models import calibration as cb

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def daily_update(own_cc, FP, scores, kappa, alpha):
    idx = np.searchsorted(cb.GRID, scores[~np.isnan(scores)], side="left")
    own_cc += np.cumsum(np.bincount(np.minimum(idx, len(cb.GRID) - 1), minlength=len(cb.GRID)), dtype=np.int32)
    n = own_cc[-1]
    M = (kappa * FP + own_cc) / (kappa + n + 1.0)
    return cb.GRID[int(np.argmax(M >= 1 - alpha - 1e-9)) if M[-1] >= 1 - alpha - 1e-9 else len(cb.GRID) - 1]


def run(reps=2000, seed=0):
    rng = np.random.default_rng(seed)
    FP = np.cumsum(np.histogram(rng.exponential(size=100000), bins=np.r_[-np.inf, cb.GRID])[0])[:len(cb.GRID)]
    FP = (FP / FP[-1]).astype(np.float64)
    times = []
    for r in range(reps):
        own = np.zeros(len(cb.GRID), dtype=np.int32)
        for h in range(56):
            sc = rng.exponential(size=24)
            t0 = time.perf_counter()
            daily_update(own, FP, sc, 96.0, 0.1)
            if h == 28:
                times.append(time.perf_counter() - t0)
    t = np.array(times) * 1e3
    # batch: one update for 10,000 buildings (loop) -> throughput
    own = np.zeros((10000, len(cb.GRID)), dtype=np.int32)
    sc = rng.exponential(size=(10000, 24))
    t0 = time.perf_counter()
    for b in range(10000):
        daily_update(own[b], FP, sc[b], 96.0, 0.1)
    batch = (time.perf_counter() - t0)
    out = dict(reps=reps, single_ms_median=float(np.median(t)), single_ms_q25=float(np.quantile(t, 0.25)),
               single_ms_q75=float(np.quantile(t, 0.75)), batch_10k_buildings_s=float(batch),
               state_kB=own[0].nbytes / 1e3, prior_kB=FP.nbytes / 1e3, grid_points=len(cb.GRID))
    json.dump(out, open(os.path.join(ROOT, "results", "latency.json"), "w"), indent=1)
    return out


if __name__ == "__main__":
    print(run())
