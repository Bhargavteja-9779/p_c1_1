"""Extended analyses: weekly/worst-week reliability with a method-independent oracle
noise reference, paired under-coverage tests with cluster CIs and one confirmatory family, tails and
equivalence, nested selection and bootstrap selection frequencies, matched-kappa attribution,
robustness with week-1/one-sided/post-shift metrics, offset/heterogeneity decomposition, threshold and
nominal-level sensitivity of the recommendation rule.

Unit of analysis: one building (metrics averaged over the seeds in which it was a target), unless stated.
Outputs: tables/T2_*.{csv,md}, results/selection.json, results/extended_analysis.json.
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd
from scipy.stats import binomtest, wilcoxon

from src.statistics.analysis import RES, TAB, NOM, CQR_STRATEGIES, _cluster_boot_ci, holm

MAIN = ["HSC-CQR recency", "HSC-CQR recency (capped)", "QShrink-CQR recency", "Self-CQR recency", "HSC-SSC-CQR",
        "HSC-CQR simple (cov)", "QShrink-CQR (cov)", "ACI-CQR (cov)", "HSC-CQR fixed-κ", "Self-CQR", "ACI-CQR",
        "TQA-B-CQR", "GHCP-CQR", "HSC-CQR recency κ=∞", "CQR"]
DELAY = ["HSC-CQR recency (delay 1d)", "QShrink-CQR (cov, delay 1d)", "ACI-CQR (cov, delay 1d)"]
CONF_BASELINES = ["CQR", "QShrink-CQR (cov)", "ACI-CQR (cov)", "Self-CQR"]
WEEKS = [f"cov_w{i}" for i in range(1, 9)]


def _md(df, path, title):
    df.to_csv(path + ".csv", index=False)
    with open(path + ".md", "w") as f:
        f.write(f"**{title}**\n\n" + df.round(4).to_markdown(index=False) + "\n")


def _sel(df, exp="main", dataset=None, alpha=0.1, perturb="none", protocol=None):
    q = (df.exp == exp) & (df.alpha == alpha) & (df.perturb == perturb)
    if dataset is not None:
        q &= df.dataset == dataset
    if protocol is not None:
        q &= df.protocol == protocol
    return df[q]


def add_flags(df):
    nom = df["alpha"].map(NOM)
    thr = nom - 0.05
    w = df[WEEKS].values
    df["wk_under_n"] = (w < thr.values[:, None]).sum(1)
    df["wk_under_late"] = (w[:, 1:] < thr.values[:, None]).mean(1)
    for c in (0.85, 0.80, 0.75):
        df[f"anyweek_{int(c * 100)}"] = (np.nanmin(w, axis=1) < c - (0.9 - nom.values)).astype(float)
    if "cov_w5" in df:
        df["cov_post"] = df[["cov_w5", "cov_w6", "cov_w7", "cov_w8"]].mean(1)
    return df


def per_building(t, cols):
    return t.groupby(["method", "building_id"]).agg(site=("site_id", "first"),
                                                     **{c: (c, "mean") for c in cols}).reset_index()


def weekly_table(df, methods):
    """window, week-1, weeks 2-8 and worst-week under-coverage per method, with the oracle reference."""
    rows = []
    for ds in ["BDG2", "UCI"]:
        t = _sel(df, dataset=ds)
        t = t[t.method.isin(methods)]
        if not len(t):
            continue
        cols = ["under", "under_wk1", "wk_under_late", "anyweek_85", "anyweek_80", "anyweek_75", "wk_under_n"]
        refc = [c for c in ["ref_under_win", "ref_under_week", "ref_anyweek"] if c in t]
        b = per_building(t, cols + refc)
        for m in methods:
            x = b[b.method == m]
            if not len(x):
                continue
            r = dict(dataset=ds, method=m, n_buildings=len(x), **{c: float(x[c].mean()) for c in cols})
            if refc:
                r.update({c: float(x[c].mean()) for c in refc})
                cl = x.site.values if ds == "BDG2" else x.building_id.values
                for obs, ref, nm in [("under", "ref_under_win", "excess_win"),
                                     ("wk_under_late", "ref_under_week", "excess_wk2_8"),
                                     ("under_wk1", "ref_under_week", "excess_wk1"),
                                     ("anyweek_85", "ref_anyweek", "excess_anyweek")]:
                    d = (x[obs] - x[ref]).values
                    r[nm] = float(d.mean())
                    r[nm + "_ci"] = _cluster_boot_ci(d, cl, n_boot=1000)
            rows.append(r)
    out = pd.DataFrame(rows)
    if len(out):
        show = out.copy()
        for c in [c for c in show if c.endswith("_ci")]:
            show[c] = show[c].apply(lambda v: f"[{100 * v[0]:.1f}, {100 * v[1]:.1f}]")
        _md(show, os.path.join(TAB, "T2_weekly"),
            "Per-building reliability at window and weekly resolution (main, 90 %; unit = building; shares; "
            "ref_* = oracle-calibrated building with the same error dynamics, 7-day block bootstrap; "
            "excess CI in percentage points, site-cluster bootstrap for BDG2, building bootstrap for UCI)")
    return out


def share_tests(df, primary, baselines, exp="main", dataset="BDG2", protocol=None, perturb="none", alpha=0.1):
    """paired comparisons of under-coverage (window, week 1) and IS: McNemar exact test on building x seed
    pairs, mean difference of per-building shares with cluster-bootstrap CI; IS: Wilcoxon on per-building
    log-ratio and TOST at +-2 % (90 % bootstrap CI of the median log-ratio inside [log .98, log 1.02])."""
    t = _sel(df, exp, dataset, alpha, perturb, protocol)
    res = []
    key = ["building_id", "seed"]
    P = t[t.method == primary].set_index(key)
    if not len(P):
        return pd.DataFrame()
    for bl in baselines:
        B = t[t.method == bl].set_index(key)
        idx = P.index.intersection(B.index)
        if not len(idx) or bl == primary:
            continue
        site = P.loc[idx, "site_id"].values
        bid = np.array([i[0] for i in idx])
        for metric in ["under", "under_wk1"]:
            a, b = P.loc[idx, metric].values, B.loc[idx, metric].values
            n01, n10 = int(((a == 0) & (b == 1)).sum()), int(((a == 1) & (b == 0)).sum())  # primary better / worse
            p = binomtest(n10, n01 + n10, 0.5).pvalue if n01 + n10 else 1.0
            d = pd.Series(a - b).groupby(bid).mean()
            cl = pd.Series(site).groupby(bid).first().reindex(d.index).values if dataset == "BDG2" else d.index.values
            res.append(dict(exp=exp, dataset=dataset, protocol=protocol or "", perturb=perturb, alpha=alpha,
                            primary=primary, baseline=bl, metric=metric, n_buildings=len(d),
                            share_primary=float(pd.Series(a).groupby(bid).mean().mean()),
                            share_baseline=float(pd.Series(b).groupby(bid).mean().mean()),
                            diff=float(d.mean()), ci95=_cluster_boot_ci(d.values, cl, n_boot=1000),
                            discordant_better=n01, discordant_worse=n10, p=float(p)))
        lr = np.log(P.loc[idx, "rel_IS"].values) - np.log(B.loc[idx, "rel_IS"].values)
        d = pd.Series(lr).groupby(bid).mean().dropna()
        rng = np.random.default_rng(0)
        meds = [np.median(rng.choice(d.values, len(d))) for _ in range(1000)]
        lo, hi = np.quantile(meds, [0.05, 0.95])
        p = wilcoxon(d.values).pvalue if np.any(d.values != 0) else 1.0
        res.append(dict(exp=exp, dataset=dataset, protocol=protocol or "", perturb=perturb, alpha=alpha,
                        primary=primary, baseline=bl, metric="log_rel_IS", n_buildings=len(d),
                        diff=float(np.median(d)), ci95=[float(lo), float(hi)], p=float(p),
                        mean_ratio=float(P.loc[idx, "rel_IS"].mean() / B.loc[idx, "rel_IS"].mean()),
                        tost_equiv_2pct=bool(lo > np.log(0.98) and hi < np.log(1.02))))
    return pd.DataFrame(res)


def confirmatory(df, primary):
    r = pd.concat([share_tests(df, primary, CONF_BASELINES, dataset=ds) for ds in ["BDG2", "UCI"]],
                  ignore_index=True)
    if len(r):
        r["p_holm"] = holm(r["p"].values)  # one declared family: primary x 4 baselines x 3 metrics x 2 datasets
        r["family"] = "confirmatory"
    return r


def tails(df, methods):
    """mean/median IS, width-ratio tail vs CQR and worst-decile cost, per building x seed (main, 90 %)."""
    rows = []
    for ds in ["BDG2", "UCI"]:
        t = _sel(df, dataset=ds)
        c = t[t.method == "CQR"].set_index(["building_id", "seed"])
        for m in methods:
            x = t[t.method == m].set_index(["building_id", "seed"])
            if not len(x):
                continue
            idx = x.index.intersection(c.index)
            wr = (x.loc[idx, "rel_width"] / c.loc[idx, "rel_width"]).values
            r = dict(dataset=ds, method=m, rel_IS_median=float(x.rel_IS.median()), rel_IS_mean=float(x.rel_IS.mean()),
                     width_ratio_p99=float(np.nanquantile(wr, 0.99)), width_ratio_max=float(np.nanmax(wr)),
                     n_width_gt5x=int(np.nansum(wr > 5)), rel_IS_early_median=float(x.rel_IS_early.median()))
            if "cost20" in x:
                cs = np.sort(x.cost20.dropna().values)
                r.update(cost20_mean=float(cs.mean()), cost20_worst10=float(cs[-max(1, len(cs) // 10):].mean()),
                         cost20_max=float(cs[-1]))
            if "underprot" in x:
                r["underprot"] = float(x.underprot.mean())
            rows.append(r)
    out = pd.DataFrame(rows)
    if len(out):
        _md(out, os.path.join(TAB, "T2_tails"), "Sharpness tails (main, 90 %; building x seed units; width ratio vs "
                                                  "pooled CQR for the same building and seed)")
    return out


def _rule(t, cands, tol=1.02):
    g = t[t.method.isin(cands)].groupby(["dataset", "method"]).agg(under=("under", "mean"),
                                                                    rel_IS=("rel_IS", "median")).reset_index()
    rows = []
    dsets = sorted(g.dataset.unique())
    for m in cands:
        x = g[g.method == m].set_index("dataset")
        c = g[g.method == "CQR"].set_index("dataset")
        if not set(dsets) <= set(x.index):
            continue
        ratio = max(float(x.loc[d, "rel_IS"] / c.loc[d, "rel_IS"]) for d in dsets)
        rows.append(dict(method=m, under=float(x.under.mean()), is_ratio_max=ratio, eligible=ratio <= tol))
    r = pd.DataFrame(rows).sort_values("under")
    el = r[r.eligible]
    return (str(el.iloc[0].method) if len(el) else None), r


def selection(df, cands=None, n_boot=300):
    """rule A.1 as originally stated (both datasets), nested (select on BDG2, confirm on UCI,
    leave-site-out and cross-dataset), at 95 % and 80 % nominal, and bootstrap selection frequencies."""
    cands = [c for c in (cands or CQR_STRATEGIES) if c in set(df.method)]
    out = {}
    base = _sel(df)
    out["A1_both"], tab = _rule(base, cands)
    out["A1_table"] = tab.to_dict(orient="records")
    out["nested_BDG2_pick"], _ = _rule(base[base.dataset == "BDG2"], cands)
    pick = out["nested_BDG2_pick"]
    conf = {}
    for nm, (exp, ds, prot) in {"UCI": ("main", "UCI", None), "LSO": ("lso", "BDG2", None),
                                "BDG2->UCI": ("xds", "UCI", "BDG2->UCI (no weather)"),
                                "UCI->BDG2": ("xds", "BDG2", "UCI->BDG2 (no weather)")}.items():
        t = _sel(df, exp, ds, protocol=prot)
        if not len(t):
            continue
        _, r = _rule(t, cands)
        r = r.reset_index(drop=True)
        conf[nm] = dict(rank_of_pick=int(r.index[r.method == pick][0]) + 1 if pick in set(r.method) else None,
                        pick_under=float(r.loc[r.method == pick, "under"].iloc[0]) if pick in set(r.method) else None,
                        best=str(r[r.eligible].iloc[0].method) if r.eligible.any() else None,
                        best_under=float(r[r.eligible].iloc[0].under) if r.eligible.any() else None)
    out["nested_confirmation"] = conf
    for a in (0.05, 0.2):
        t = _sel(df, alpha=a)
        if len(t):
            out[f"A1_alpha{a}"], r = _rule(t, cands)
            out[f"A1_alpha{a}_table"] = r.to_dict(orient="records")
    rng = np.random.default_rng(0)
    cnt = {}
    groups = {ds: base[base.dataset == ds] for ds in ["BDG2", "UCI"]}
    ids = {ds: g.building_id.unique() for ds, g in groups.items()}
    for _ in range(n_boot):
        parts = []
        for ds, g in groups.items():
            pickb = rng.choice(ids[ds], len(ids[ds]), replace=True)
            vc = pd.Series(pickb).value_counts()
            gi = g[g.building_id.isin(vc.index)]
            parts.append(gi.loc[gi.index.repeat(gi.building_id.map(vc).values)])
        w, _ = _rule(pd.concat(parts), cands)
        cnt[w] = cnt.get(w, 0) + 1
    out["bootstrap_selection_freq"] = {str(k): v / n_boot for k, v in sorted(cnt.items(), key=lambda kv: -kv[1])}
    with open(os.path.join(RES, "selection.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    return out


def matched_kappa():
    """recency vs no recency at equal kappa (frontier, main 90 %)."""
    f = os.path.join(RES, "frontier.csv")
    if not os.path.exists(f):
        return None
    fr = pd.read_csv(f)
    if "alpha" in fr:
        fr = fr[fr.alpha == 0.1]
    fr = fr[fr.family.str.startswith("HSC")]
    g = fr.groupby(["dataset", "family", "param"])[["under", "under_wk1", "rel_IS"]].mean().reset_index()
    w = g.pivot_table(index=["dataset", "param"], columns="family", values=["under", "under_wk1"])
    w.columns = [f"{a} | {b}" for a, b in w.columns]
    w = w.reset_index()
    _md(w, os.path.join(TAB, "T2_matched_kappa"), "Own-score decay at matched kappa (frontier; 5-seed means; shares)")
    return w


def robustness(df, primary, methods):
    """per stress condition: window, week-1, upper-tail under-protection, post-shift coverage, IS; seed s.d.;
    McNemar of the primary vs each method on window under-coverage."""
    rb = df[df.exp == "robust"]
    if not len(rb):
        return None
    rows = []
    for p in sorted(rb.perturb.unique()):
        t = rb[rb.perturb == p]
        for m in methods:
            x = t[t.method == m]
            if not len(x):
                continue
            sd = x.groupby("seed")["under"].mean().std()
            r = dict(perturb=p, method=m, under=float(x.under.mean()), under_sd_seeds=float(sd),
                     under_wk1=float(x.under_wk1.mean()), rel_IS=float(x.rel_IS.median()),
                     rel_IS_mean=float(x.rel_IS.mean()))
            if "underprot" in x:
                r["underprot"] = float(x.underprot.mean())
            if "cov_post" in x:
                r["cov_post_mean"] = float(x.cov_post.mean())
            if m != primary:
                st = share_tests(df, primary, [m], exp="robust", dataset="BDG2", perturb=p)
                if len(st):
                    s1 = st[st.metric == "under"].iloc[0]
                    r.update(diff_vs_primary=-float(s1["diff"]), p_mcnemar=float(s1["p"]))
            rows.append(r)
    out = pd.DataFrame(rows)
    _md(out, os.path.join(TAB, "T2_robustness"), f"Robustness (BDG2, 3 seeds; shares; diff_vs_primary = method − "
                                                 f"{primary} in window under-covered share, McNemar exact p)")
    return out


def offset_decomposition(df):
    """share of pooled-CQR under-coverage explained by a uniform level offset."""
    out = {}
    for ds in ["BDG2", "UCI"]:
        t = _sel(df, dataset=ds)
        c = t[t.method == "CQR"]
        if not len(c):
            continue
        b = c.groupby("building_id").coverage.mean()
        bias = 0.9 - float(b.mean())
        out[ds] = dict(mean_cov=float(b.mean()), under=float((b < 0.85).mean()),
                       under_offset_removed=float((b + bias < 0.85).mean()), offset=bias)
    return out


def threshold_sensitivity(df, methods):
    rows = []
    for ds in ["BDG2", "UCI"]:
        t = _sel(df, dataset=ds)
        for m in methods:
            b = t[t.method == m].groupby("building_id").coverage.mean()
            if len(b):
                rows.append(dict(dataset=ds, method=m, **{f"under_{int(100 * d)}pt": float((b < 0.9 - d).mean())
                                                          for d in (0.02, 0.03, 0.05, 0.10)}))
    out = pd.DataFrame(rows)
    if len(out):
        _md(out, os.path.join(TAB, "T2_threshold"), "Under-covered share at alternative tolerances (per building)")
    return out


def run(df):
    df = add_flags(df.copy())
    sel = selection(df)
    primary = sel["nested_BDG2_pick"] or sel["A1_both"] or "HSC-CQR recency"
    res = dict(primary=primary)
    weekly_table(df, MAIN + DELAY)
    conf = confirmatory(df, primary)
    if len(conf):
        show = conf.copy()
        show["ci95"] = show.ci95.apply(lambda v: f"[{v[0]:.4f}, {v[1]:.4f}]")
        _md(show, os.path.join(TAB, "T2_confirmatory"), f"Confirmatory family ({primary}; Holm over the whole family)")
        res["confirmatory"] = conf.to_dict(orient="records")
    ex = []
    for ds in ["BDG2", "UCI"]:
        ex.append(share_tests(df, primary, [m for m in MAIN + DELAY if m not in CONF_BASELINES], dataset=ds))
    ex = pd.concat([e for e in ex if len(e)], ignore_index=True) if any(len(e) for e in ex) else pd.DataFrame()
    if len(ex):
        ex["family"] = "exploratory"
        show = ex.copy()
        show["ci95"] = show.ci95.apply(lambda v: f"[{v[0]:.4f}, {v[1]:.4f}]")
        _md(show, os.path.join(TAB, "T2_exploratory"), f"Exploratory paired comparisons ({primary}; unadjusted)")
    tails(df, MAIN + DELAY + ["HSC-CQR recency (MLP)", "HSC-CQR (MLP)", "CQR (MLP)"])
    matched_kappa()
    robustness(df, primary, MAIN)
    res["offset"] = offset_decomposition(df)
    threshold_sensitivity(df, MAIN)
    res["selection"] = {k: v for k, v in sel.items() if not k.endswith("table")}
    with open(os.path.join(RES, "extended_analysis.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)
    return res
