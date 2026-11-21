"""Downstream case study (revision 1, reviewer R9): day-ahead upper-reserve sizing from the interval.

For each target building and onboarding day, an aggregator books an hourly upper reserve
r_t = hi_t - yhat_t above the point forecast (capacity cost c_r per kWh) and pays a shortfall penalty
c_p per kWh when the realised load exceeds hi_t. With c_p / c_r = 2 / alpha (= 20 at alpha = 0.1) the
cost-minimising booking is the (1 - alpha/2) quantile, i.e. the upper bound of the central (1 - alpha)
interval. Reported per building (normalised by mean load): cost, shortfall rate, and whether the
shortfall rate exceeds twice its nominal value (a 'breach' that would trigger contract review).
Writes results/case_study.csv (per building) and tables/T_case_study.{md,csv}.
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

from src import experiments as ex
from src.training import pipeline as pl

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
METHODS = ["HSC-CQR cov-κ", "HSC-CQR fixed-κ", "HSC-CQR simple", "HSC-CQR", "CQR", "Self-CQR", "Switch-CQR",
           "QShrink-CQR", "QShrink-CQR fixed-λ", "ACI-CQR clip", "Mondrian-site CQR", "QR-LGBM"]


def run(seeds=(0, 1, 2, 3, 4), alpha=0.1):
    rows = []
    for dsn in ["BDG2", "UCI"]:
        ds = ex.get_ds(dsn)
        for s in seeds:
            obj = ex.prepared(dsn, dsn, s, "random", None, ds["temp"] is not None, 0.4, True)
            PT = obj["PT"]
            mc, mt_ = ds["meta"].iloc[obj["sp"]["cal"]], ds["meta"].iloc[obj["tgt_idx"]]
            out, _ = pl.run_calibration(obj["PC"], PT, alpha, mc, mt_, methods="core")
            ok = pl.common_mask(out, PT)
            y = np.where(ok, PT["y"], np.nan)
            ybar = np.nanmean(y, axis=(1, 2))
            for m in METHODS:
                if m not in out:
                    continue
                hi = out[m][1]
                short = np.maximum(y - hi, 0)
                cost = (np.maximum(hi - PT["yhat"], 0) + (2 / alpha) * short)
                miss = (y > hi) & ok
                rate = miss.sum(axis=(1, 2)) / ok.sum(axis=(1, 2))
                for i, b in enumerate(obj["tgt_idx"]):
                    rows.append(dict(dataset=dsn, seed=s, method=m, building_id=ds["meta"].building_id.iloc[b],
                                     cost=float(np.nanmean(cost[i]) / ybar[i]), shortfall_rate=float(rate[i]),
                                     breach=float(rate[i] > 2 * alpha / 2)))
    d = pd.DataFrame(rows)
    d.to_csv(os.path.join(ROOT, "results", "case_study.csv"), index=False)
    t = d.groupby(["dataset", "method"]).agg(mean_cost=("cost", "mean"), p90_cost=("cost", lambda c: c.quantile(0.9)),
                                             mean_shortfall=("shortfall_rate", "mean"),
                                             breach_share=("breach", "mean")).reset_index()
    t.to_csv(os.path.join(ROOT, "tables", "T_case_study.csv"), index=False)
    with open(os.path.join(ROOT, "tables", "T_case_study.md"), "w") as f:
        f.write("**Day-ahead upper-reserve sizing (cost per unit mean load; shortfall nominal 5 %; breach = "
                "shortfall rate > 10 %), building-seed rows**\n\n" + t.round(4).to_markdown(index=False) + "\n")
    return t
