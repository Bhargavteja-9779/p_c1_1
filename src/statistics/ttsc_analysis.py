"""Analysis of the two-timescale shrinkage conformal (TTSC) experiment (results/ttsc/*.csv).

Unit of analysis: the target building (metrics averaged over the seeds in which it was a target).
Outputs: tables/TT_*.{csv,md}, results/ttsc_summary.json.
"""
import glob
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RES = os.path.join(ROOT, "results")
TAB = os.path.join(ROOT, "tables")
NW = 8
THR_MARGIN = 0.05
BREACH = 0.10  # weekly-settled contract: upper bound exceeded in > 10 % of a week's hours (2 x nominal 5 %)
METHODS = ["TTSC", "HSC-CQR recency (capped)", "HSC-CQR recency", "QShrink-CQR (cov)", "ACI-CQR (cov)", "CQR",
           "ACI (weekly-tuned)", "Windowed ACI (weekly-tuned)",
           "TTSC (cumulative feedback)", "TTSC (uncapped)", "TTSC (delay 1d)"]
COMPARE = ["HSC-CQR recency (capped)", "QShrink-CQR (cov)", "ACI-CQR (cov)", "CQR", "ACI (weekly-tuned)",
           "Windowed ACI (weekly-tuned)"]
CW = [f"cov_w{i}" for i in range(1, NW + 1)]
UW = [f"up_w{i}" for i in range(1, NW + 1)]


def load():
    fs = [f for f in glob.glob(os.path.join(RES, "ttsc", "*.csv"))
          if not f.endswith("_tune.csv") and os.path.getsize(f) > 0]
    return pd.concat([pd.read_csv(f) for f in fs], ignore_index=True)


def unit_metrics(d):
    """Per (building, seed) row -> reliability indicators."""
    a = d.alpha.iloc[0] if "alpha" in d else 0.1
    thr = 1 - a - THR_MARGIN
    c = d[CW].values
    u = d[UW].values
    out = pd.DataFrame(dict(
        method=d.method.values, building_id=d.building_id.values, site_id=d.site_id.values, seed=d.seed.values,
        under=(d["cov"].values < thr).astype(float),
        wk1=(c[:, 0] < thr).astype(float),
        wk_late=np.nanmean(np.where(np.isnan(c[:, 1:]), np.nan, c[:, 1:] < thr), axis=1),
        any80=(np.nanmin(c, axis=1) < 0.80).astype(float),
        any85=(np.nanmin(c, axis=1) < thr).astype(float),
        breach_wk=np.nanmean(np.where(np.isnan(u), np.nan, u > (a / 2) * 2), axis=1),
        breach_any=(np.nanmax(u, axis=1) > (a / 2) * 2).astype(float),
        rel_IS=d.rel_IS.values, rel_width=d.rel_width.values,
        cost10=(d.u_rel + 10 * d.viol_rel).values if "u_rel" in d else np.nan,
        cost20=(d.u_rel + 20 * d.viol_rel).values if "u_rel" in d else np.nan,
        cost40=(d.u_rel + 40 * d.viol_rel).values if "u_rel" in d else np.nan,
        ref_win=d.ref_under_win.values, ref_week=d.ref_under_week.values, ref_any=d.ref_anyweek.values))
    return out


def per_building(df):
    u = unit_metrics(df)
    return u.groupby(["method", "building_id", "site_id"], as_index=False).mean(numeric_only=True)


def cluster_ci(diff, clusters, n_boot=2000, seed=0):
    rng = np.random.default_rng(seed)
    cl = pd.Series(diff).groupby(np.asarray(clusters))
    sums, cnts = cl.sum().values, cl.count().values
    k = len(sums)
    idx = rng.integers(0, k, size=(n_boot, k))
    bs = sums[idx].sum(1) / cnts[idx].sum(1)
    return float(np.mean(diff)), float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975))


def summarise(b, ds):
    rows = []
    for m in METHODS:
        x = b[b.method == m]
        if not len(x):
            continue
        rows.append(dict(dataset=ds, method=m, n=len(x), under=x.under.mean(), wk1=x.wk1.mean(),
                         wk_late=x.wk_late.mean(), any85=x.any85.mean(), any80=x.any80.mean(),
                         breach_wk=x.breach_wk.mean(), breach_any=x.breach_any.mean(),
                         rel_IS_median=x.rel_IS.median(), rel_IS_mean=x.rel_IS.mean(),
                         rel_width_median=x.rel_width.median(),
                         cost10=x.cost10.mean(), cost20=x.cost20.mean(), cost40=x.cost40.mean(),
                         cost20_worst10=x.cost20[x.cost20 >= x.cost20.quantile(0.9)].mean(),
                         ref_win=x.ref_win.mean(), ref_week=x.ref_week.mean(), ref_any=x.ref_any.mean()))
    out = pd.DataFrame(rows)
    if len(out) and (out.method == "CQR").any():
        c = out[out.method == "CQR"].iloc[0]
        for k in ["cost10", "cost20", "cost40", "cost20_worst10", "rel_IS_median", "rel_IS_mean"]:
            out[k + "_vs_cqr"] = out[k] / c[k] - 1
    return out


def paired(b, ds, prim="TTSC"):
    rows = []
    p = b[b.method == prim].set_index("building_id")
    cl_key = "site_id" if ds.startswith("BDG2") else None
    for m in COMPARE:
        if not (b.method == m).any():
            continue
        q = b[b.method == m].set_index("building_id").reindex(p.index)
        for met in ["wk_late", "any80", "breach_wk", "under", "wk1"]:
            d = (p[met] - q[met]).values
            cl = p["site_id"].values if cl_key else np.arange(len(d))
            est, lo, hi = cluster_ci(d, cl)
            try:
                pv = float(stats.wilcoxon(p[met].values, q[met].values, zero_method="zsplit").pvalue)
            except ValueError:
                pv = 1.0
            rows.append(dict(dataset=ds, baseline=m, metric=met, diff=est, lo=lo, hi=hi, p=pv,
                             better=float(np.mean(d < 0)), worse=float(np.mean(d > 0))))
        r = np.log(p.rel_IS.values / q.rel_IS.values)
        est, lo, hi = cluster_ci(r, p["site_id"].values if cl_key else np.arange(len(r)))
        rows.append(dict(dataset=ds, baseline=m, metric="log_rel_IS", diff=est, lo=lo, hi=hi,
                         p=float(stats.wilcoxon(r).pvalue), better=float(np.mean(r < 0)), worse=float(np.mean(r > 0)),
                         tost_3pct=bool(lo > np.log(0.97) and hi < np.log(1.03))))
    out = pd.DataFrame(rows)
    # Holm over the declared family (TTSC vs four baselines x {wk_late, any80, breach_wk} x dataset) per dataset
    fam = out.metric.isin(["wk_late", "any80", "breach_wk"])
    pv = out.loc[fam, "p"].values
    order = np.argsort(pv)
    adj = np.empty_like(pv)
    run = 0.0
    for i, j in enumerate(order):
        run = max(run, min(1.0, (len(pv) - i) * pv[j]))
        adj[j] = run
    out["p_holm"] = np.nan
    out.loc[fam, "p_holm"] = adj
    return out


def _md(df, name, cap, fmt=None):
    os.makedirs(TAB, exist_ok=True)
    df.to_csv(os.path.join(TAB, name + ".csv"), index=False)
    d = df.copy()
    if fmt:
        for c, f in fmt.items():
            if c in d:
                d[c] = d[c].map(f)
    with open(os.path.join(TAB, name + ".md"), "w") as f:
        f.write(f"**{cap}**\n\n" + d.to_markdown(index=False, disable_numparse=True) + "\n")


def run():
    df = load()
    pc = lambda x: "–" if pd.isna(x) else f"{100 * x:.1f}"  # noqa: E731
    f3 = lambda x: f"{x:.3f}"  # noqa: E731
    summ, tests, held = [], [], []
    main = df[(df.exp == "main") & (df.alpha == 0.1)]
    for ds in ["BDG2", "UCI"]:
        b = per_building(main[main.dataset == ds])
        summ.append(summarise(b, ds))
        tests.append(paired(b, ds))
        h = per_building(main[(main.dataset == ds) & (main.seed >= 2)])
        held.append(summarise(h, ds + " (seeds 2–4)"))
        tests.append(paired(h, ds + " (seeds 2–4)"))
    S = pd.concat(summ + held, ignore_index=True)
    T = pd.concat(tests, ignore_index=True)
    # other protocols and nominal levels
    other = []
    for (e, ds, pert, a), g in df.groupby(["exp", "dataset", "perturb", "alpha"]):
        if e == "main" and a == 0.1:
            continue
        b = per_building(g)
        s = summarise(b, ds)
        s.insert(0, "condition", f"{e}:{pert}" + ("" if a == 0.1 else f":alpha={a}"))
        other.append(s)
    O = pd.concat(other, ignore_index=True)
    tune = pd.concat([pd.read_csv(f) for f in glob.glob(os.path.join(RES, "ttsc", "*_tune.csv"))])
    gam = df.groupby("part")[["gamma", "kappa", "gamma_edge"]].first().reset_index()
    fmt = {c: pc for c in ["under", "wk1", "wk_late", "any85", "any80", "breach_wk", "breach_any", "ref_win",
                           "ref_week", "ref_any"]}
    fmt.update({c: f3 for c in ["rel_IS_median", "rel_IS_mean", "rel_width_median", "cost10", "cost20", "cost40",
                                "cost20_worst10"]})
    fmt.update({c: (lambda x: "–" if pd.isna(x) else f"{100 * x:+.1f}") for c in
                ["cost10_vs_cqr", "cost20_vs_cqr", "cost40_vs_cqr", "cost20_worst10_vs_cqr", "rel_IS_median_vs_cqr",
                 "rel_IS_mean_vs_cqr"]})
    _md(S, "TT_main", "TTSC and comparators, main protocol (90 %), unit = building; shares in %", fmt)
    _md(T, "TT_tests", "Paired per-building comparisons of TTSC (difference TTSC minus baseline; 95 % site-cluster "
                       "(BDG2) or building (UCI) bootstrap CI; Wilcoxon signed-rank; Holm over the declared family)",
        {"diff": lambda x: f"{x:+.4f}", "lo": lambda x: f"{x:+.4f}", "hi": lambda x: f"{x:+.4f}",
         "p": lambda x: f"{x:.2g}", "p_holm": lambda x: "–" if pd.isna(x) else f"{x:.2g}",
         "better": lambda x: f"{100 * x:.0f}", "worse": lambda x: f"{100 * x:.0f}"})
    _md(O, "TT_other", "TTSC and comparators under all other protocols, stress tests and nominal levels", fmt)
    _md(gam, "TT_params", "Selected kappa and gamma per run (gamma_edge: largest grid value selected)")
    summary = dict(gamma_edge_share=float(gam.gamma_edge.mean()),
                   gamma_median_main=float(gam[gam.part.str.contains("_a0.1")].gamma.median()),
                   n_parts=int(df.part.nunique()))
    json.dump(summary, open(os.path.join(RES, "ttsc_summary.json"), "w"), indent=1)
    return S, T, O


if __name__ == "__main__":
    S, T, O = run()
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 30)
    print(S.round(4).to_string())
