"""Clean computational-cost benchmark (run ALONE, nothing else on the CPU): for seed 0 of each dataset,
times (i) training the three LightGBM models and the two MLPs (4 threads), (ii) LightGBM inference per
building-day, (iii) leave-one-building-out tuning and per-building-day application of the recommended
calibration layer (HSC-CQR recency), CQR, QShrink-CQR (cov) and ACI-CQR; (iv) calibration-store memory.
Output: results/timing.json (used by manuscript/values.py)."""
import json
import os
import sys
import time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from src import experiments as ex  # noqa: E402
from src.training import pipeline as pl  # noqa: E402
from src.models import calibration as cb  # noqa: E402


def main():
    out = {}
    for dsn in ["BDG2", "UCI"]:
        ds = ex.get_ds(dsn)
        w = ds["temp"] is not None
        obj = ex.prepared(dsn, dsn, 0, "random", None, w, 0.4, True)
        sp = pl.split(ds, 0, "random", None)
        t0 = time.time()
        m = pl.train_models(ds, sp, 0, w, frac=0.4, with_mlp=True, log=lambda *a: None)
        r = dict(train_total_s=time.time() - t0, lgb_3models_s=m["time_lgb"], mlp_2models_s=m["time_mlp"],
                 n_train_rows=m["n_train_rows"])
        PC, PT = obj["PC"], obj["PT"]
        stages = np.arange(1, pl.NH + 1)
        Scq, Stq = pl.scores_cqr(PC), pl.scores_cqr(PT)
        bw = PC["qhi"] / PC["s"][:, :, None] - PC["qlo"] / PC["s"][:, :, None]
        nt = Stq.shape[0]
        t0 = time.time()
        best, _ = pl.tune_hsc(Scq, bw, PC["z"], 0.1, stage_matched=False, Ks=[None], objective="cov",
                              decay=pl.RECENCY)
        r["recency_tune_s"] = time.time() - t0
        t0 = time.time()
        binc, _ = cb.bin_cdfs(cb.cum_counts(Scq), stages)
        r["store_build_s"] = time.time() - t0
        r["store_MB"] = binc.astype(np.float32).nbytes / 1e6
        cct = cb.cum_counts(Stq)
        reps = 5
        t0 = time.time()
        for _ in range(reps):
            cb.hsc_quantiles(cct, binc, None, 0.1, [best["kappa"]], stages, stage_matched=False, decay=pl.RECENCY)
        r["recency_apply_ms_per_building_day"] = 1e3 * (time.time() - t0) / reps / (nt * pl.NH)
        t0 = time.time()
        for _ in range(reps):
            cb.pooled_quantile(binc, 0.1, True)
        r["cqr_apply_ms_per_building_day"] = 1e3 * (time.time() - t0) / reps / (nt * pl.NH)
        t0 = time.time()
        for _ in range(reps):
            cb.aci_quantiles(Stq, binc.sum(axis=0), 0.1, 0.002, stages)
        r["aci_apply_ms_per_building_day"] = 1e3 * (time.time() - t0) / reps / (nt * pl.NH)
        Xn = PT["yhat"]
        r["n_targets"] = int(nt)
        r["kappa"] = best["kappa"]
        out[dsn] = r
        print(dsn, r, flush=True)
    json.dump(out, open(os.path.join(ROOT, "results", "timing.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
