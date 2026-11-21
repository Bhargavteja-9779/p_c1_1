"""E8 error analysis (uses cached predictions + per-building results; writes results/error_analysis.json).

Questions (pre-specified):
 1. Does per-building coverage depend on forecast difficulty (CV(RMSE))? Spearman rho for CQR vs HSC-CQR.
 2. Are the buildings that HSC-CQR still under-covers characterised by a regime change inside the
    onboarding window? Indicator: |log(mean load days 29-56 / mean load days 1-28)|; Mann-Whitney U test
    under-covered vs others.
 3. Are they characterised by early-window volatility (normalised day-to-day variability, first week)?
 4. Usage-type pattern (BDG2): mean |coverage - 0.9| by usage for CQR and HSC-CQR.
"""
from __future__ import annotations

import glob
import json
import os
import pickle

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu, spearmanr

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RES = os.path.join(ROOT, "results")


def _indicators(ds_name, seed, frac=0.4):
    tag = "w1" if ds_name == "BDG2" else "w0"
    f = os.path.join(RES, "cache", f"{ds_name}_{ds_name}_random_s{seed}_{tag}_f{frac}_m1_tb1.0.pkl")
    if not os.path.exists(f):
        return None
    obj = pickle.load(open(f, "rb"))
    y = obj["PT"]["y"]  # (n, 56, 24)
    early = np.nanmean(y[:, :28], axis=(1, 2))
    late = np.nanmean(y[:, 28:], axis=(1, 2))
    shift = np.abs(np.log(np.maximum(late, 1e-6) / np.maximum(early, 1e-6)))
    wk = y[:, :7]
    mu = np.nanmean(wk, axis=(1, 2))
    vol = np.nanmean(np.abs(np.diff(wk, axis=1)), axis=(1, 2)) / mu
    return pd.DataFrame(dict(tgt_pos=np.arange(len(shift)), shift=shift, vol=vol))


def _primary():
    f = os.path.join(RES, "recommended.json")
    return json.load(open(f))["recommended"] if os.path.exists(f) else "HSC-CQR"


def run():
    P = _primary()
    f = os.path.join(RES, "raw_results.csv")
    df = pd.read_csv(f if os.path.exists(f) else f + ".gz")
    out = {}
    for ds in ["BDG2", "UCI"]:
        d = df[(df.exp == "main") & (df.dataset == ds) & (df.alpha == 0.1)]
        if not len(d):
            continue
        r = {}
        for m in ["CQR", P, "HSC-CQR", "SCP-stage", "HSC"]:
            x = d[d.method == m]
            rho, p = spearmanr(x.cvrmse_lgb, x.coverage)
            r[f"rho_cov_cvrmse_{m}"] = float(rho)
            r[f"p_cov_cvrmse_{m}"] = float(p)
        # indicators per (seed, building)
        rows = []
        for seed in sorted(d.seed.unique()):
            ind = _indicators(ds, int(seed))
            if ind is None:
                continue
            x = d[(d.method == P) & (d.seed == seed)].reset_index(drop=True)
            ind = ind.iloc[:len(x)]
            rows.append(pd.concat([x[["building_id", "coverage", "usage"]], ind[["shift", "vol"]]], axis=1))
        if rows:
            z = pd.concat(rows)
            under = z.coverage < 0.85
            for k in ["shift", "vol"]:
                a, b = z.loc[under, k], z.loc[~under, k]
                if len(a) >= 3:
                    u, p = mannwhitneyu(a, b, alternative="two-sided")
                    r[f"{k}_median_under"] = float(a.median())
                    r[f"{k}_median_other"] = float(b.median())
                    r[f"{k}_p"] = float(p)
            r["n_under"] = int(under.sum())
            r["n_units"] = int(len(z))
            rho, p = spearmanr(z["shift"], (z.coverage - 0.9).abs())
            r["rho_absdev_shift"] = float(rho)
            r["p_absdev_shift"] = float(p)
        if ds == "BDG2":
            u = d[d.method.isin(["CQR", P])].assign(absdev=lambda x: (x.coverage - 0.9).abs())
            g = u.groupby(["usage", "method"]).absdev.mean().unstack()
            n = u[u.method == "CQR"].groupby("usage").size()
            g = g[n >= 30]
            g["reduction"] = g["CQR"] - g[P]
            r["usage_table"] = g.round(4).reset_index().to_dict(orient="records")
            r["usage_largest_reduction"] = str(g.reduction.idxmax())
            r["usage_smallest_reduction"] = str(g.reduction.idxmin())
        r["primary"] = P
        out[ds] = r
    json.dump(out, open(os.path.join(RES, "error_analysis.json"), "w"), indent=1)
    return out


if __name__ == "__main__":
    print(json.dumps(run(), indent=1))
