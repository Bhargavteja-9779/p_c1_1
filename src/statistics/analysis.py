"""Statistical analysis and automatic table generation (all numbers come from results/raw_results.csv).

Unit of analysis: target building. A building can be a target in several partition seeds; its metrics are
first averaged over those seeds, so each building contributes one paired observation.

Inference (v2, after review cycle 1):
  * estimand: building-weighted mean paired difference (proposed minus baseline; negative = proposed better);
  * BDG2: buildings are clustered in 10 very unequal sites, so the primary p-value is an exact site-level
    sign-flip randomisation test of the building-weighted mean difference (all 2^n_sites sign patterns) and the
    95 % CI is a site-cluster percentile bootstrap; UCI (one site): building-level sign-flip test (20,000 Monte-
    Carlo draws) and building bootstrap;
  * Holm correction within each comparison family and metric (a family = one proposed method, one protocol,
    one perturbation, one nominal level, one metric);
  * robust companions: median paired difference with the same bootstrap, share of buildings better, matched-
    pairs rank-biserial correlation and the building-level Wilcoxon p-value (secondary; ignores clustering);
  * metrics tested: |coverage - nominal| (CD), building under-covered indicator (cov < nominal - 5 pp; the
    test of the under-covered share), relative interval score (IS) and reserve cost (RC).
"""
from __future__ import annotations

import itertools
import json
import os

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RES = os.path.join(ROOT, "results")
TAB = os.path.join(ROOT, "tables")
NOM = {0.1: 0.9, 0.05: 0.95, 0.2: 0.8}

PRIMARY = "PCS-CQR"
FAMILY_MAIN = ["CQR", "Self-CQR", "ACI-CQR", "ACI-CQR (MACD)", "TQA-B-CQR", "GHCP-CQR", "QShrink-CQR",
               "QShrink-CQR (MACD)", "HSC-CQR"]  # same forecaster, same CQR scores: the confirmatory family
FAMILY_OTHER = ["QR-LGBM", "MLP-QR", "MLP-Gauss", "ACI-CQR (coverage only)", "SCP-stage", "Self-CP", "HSC"]
FAMILY_DESIGN = ["PCS-CQR κ=168", "PCS-CQR (IS-tuned)", "PCS-CQR +stage", "PCS-CQR +kNN", "PCS-CQR +kNN+stage",
                 "PCS-CQR site-grouped", "QShrink-CQR λ=168"]
FAMILY_PREREG = ["SCP", "SCP-stage", "Mondrian-usage", "Self-CP", "ACI", "Raw-SCP", "HSC -stage", "HSC -kNN",
                 "HSC -shrink"]
FAMILY_SHORT = ["CQR", "Self-CQR", "ACI-CQR", "ACI-CQR (MACD)", "TQA-B-CQR", "GHCP-CQR", "QShrink-CQR",
                "QShrink-CQR (MACD)", "PCS-CQR κ=168", "HSC-CQR"]
ORDER = ["PCS-CQR", "PCS-CQR κ=168", "PCS-CQR (IS-tuned)", "PCS-CQR site-grouped", "PCS-CQR +stage", "PCS-CQR +kNN",
         "PCS-CQR +kNN+stage", "PCS-CQR -shrink", "HSC-CQR", "CQR", "Self-CQR", "ACI-CQR", "ACI-CQR (MACD)",
         "ACI-CQR (coverage only)", "TQA-B-CQR", "GHCP-CQR", "QShrink-CQR", "QShrink-CQR (MACD)",
         "QShrink-CQR λ=168", "QR-LGBM", "MLP-QR", "MLP-Gauss", "CQR (MLP)", "PCS-CQR (MLP)", "PCS",
         "PCS (IS-tuned)", "HSC", "HSC -stage", "HSC -kNN", "HSC -shrink", "ACI", "Self-CP", "SCP-stage", "SCP",
         "Mondrian-usage", "Naive+SCP", "Raw-SCP"]
WEEKS = [("w1", "week 1"), ("w2", "week 2"), ("w34", "weeks 3-4"), ("w58", "weeks 5-8")]


def load():
    f = os.path.join(RES, "raw_results.csv")
    df = pd.read_csv(f if os.path.exists(f) else f + ".gz")
    df["nominal"] = df["alpha"].map(NOM)
    df["abs_dev"] = (df["coverage"] - df["nominal"]).abs()
    df["under"] = (df["coverage"] < df["nominal"] - 0.05).astype(float)
    df["book_fail"] = (df["exceed_hi"] > df["alpha"]).astype(float)  # upper bound exceeded > 2x nominal (alpha/2)
    for w, _ in WEEKS:
        df["under_" + w] = (df["coverage_" + w] < df["nominal"] - 0.05).astype(float).where(df["coverage_" + w].notna())
        df["abs_dev_" + w] = (df["coverage_" + w] - df["nominal"]).abs()
    if "fold" not in df:
        df["fold"] = np.nan
    if "rep" not in df:
        df["rep"] = np.nan
    return df


def seed_level(df):
    keys = ["exp", "dataset", "protocol", "perturb", "alpha", "method", "seed"]
    g = df.groupby(keys + (["rep"] if df.rep.notna().any() else []), dropna=False)
    agg = dict(mean_cov=("coverage", "mean"), macd=("abs_dev", "mean"), under_rate=("under", "mean"),
               p10_cov=("coverage", lambda c: np.quantile(c, 0.1)), rel_width=("rel_width", "median"),
               rel_IS_mean=("rel_IS", "mean"), rel_IS=("rel_IS", "median"),
               cov_early=("coverage_early", "mean"), exceed_hi=("exceed_hi", "mean"),
               reserve_cost=("reserve_cost", "mean"), width_p90=("rel_width_p90", "median"),
               book_fail=("book_fail", "mean"),
               n=("coverage", "size"))
    for w, _ in WEEKS:
        agg["under_" + w] = ("under_" + w, "mean")
        agg["macd_" + w] = ("abs_dev_" + w, "mean")
        agg["p10_" + w] = ("coverage_" + w, lambda c: np.nanquantile(c, 0.1))
    s = g.agg(**agg).reset_index()
    if "rep" in s:  # small-pool resamples: average over resamples first (one value per seed)
        s = s.groupby(keys, dropna=False).mean(numeric_only=True).reset_index()
    return s


def summary_table(s, exp, dataset=None, protocol=None, perturb="none", alpha=0.1, methods=None):
    q = (s.exp == exp) & (s.perturb == perturb) & (s.alpha == alpha)
    if dataset is not None:
        q &= s.dataset == dataset
    if protocol is not None:
        q &= s.protocol == protocol
    t = s[q]
    cols = ["mean_cov", "cov_early", "macd", "under_rate", "p10_cov", "rel_width", "rel_IS", "rel_IS_mean",
            "exceed_hi", "reserve_cost", "width_p90", "book_fail"] + [f"{a}_{w}" for w, _ in WEEKS for a in ("under", "macd", "p10")]
    cols = [c for c in cols if c in t]
    agg = t.groupby("method")[cols].agg(["mean", "std"])
    out = pd.DataFrame(index=agg.index)
    for c in cols:
        out[c] = agg[(c, "mean")]
        out[c + "_sd"] = agg[(c, "std")].fillna(0)
    out["n_seeds"] = t.groupby("method").seed.nunique()
    order = list(dict.fromkeys(m for m in (methods or ORDER) if m in out.index))
    return out.loc[order]


def fmt_table(t, path_stub, caption):
    rows = []
    for m, r in t.iterrows():
        rows.append({"Method": m,
                     "Coverage": f"{r.mean_cov:.3f} ± {r.mean_cov_sd:.3f}",
                     "MACD": f"{r.macd:.3f} ± {r.macd_sd:.3f}",
                     "Under-covered share": f"{r.under_rate:.3f} ± {r.under_rate_sd:.3f}",
                     "P10 coverage": f"{r.p10_cov:.3f} ± {r.p10_cov_sd:.3f}",
                     "Under-covered, week 1": f"{r.under_w1:.3f} ± {r.under_w1_sd:.3f}",
                     "Rel. width (median)": f"{r.rel_width:.3f} ± {r.rel_width_sd:.3f}",
                     "Rel. IS (median)": f"{r.rel_IS:.3f} ± {r.rel_IS_sd:.3f}",
                     "Reserve cost": f"{r.reserve_cost:.4f} ± {r.reserve_cost_sd:.4f}"})
    d = pd.DataFrame(rows)
    os.makedirs(TAB, exist_ok=True)
    t.to_csv(path_stub + "_raw.csv")
    d.to_csv(path_stub + ".csv", index=False)
    with open(path_stub + ".md", "w") as f:
        f.write(f"**{caption}**\n\n" + d.to_markdown(index=False) + "\n")
    return d


def _rank_biserial(d):
    d = d[d != 0]
    if len(d) == 0:
        return 0.0
    r = pd.Series(np.abs(d)).rank().values
    wp, wm = r[d > 0].sum(), r[d < 0].sum()
    return float((wp - wm) / (wp + wm))


def _cluster_boot(d, clusters, n_boot=2000, seed=0):
    """Percentile CIs of the mean and of the median paired difference (cluster bootstrap if >= 5 clusters)."""
    rng = np.random.default_rng(seed)
    d = np.asarray(d, dtype=float)
    cl = np.asarray(clusters)
    u = np.unique(cl)
    if len(u) < 5:
        u = np.arange(len(d))
        cl = u
    idx = {c: np.where(cl == c)[0] for c in u}
    means, meds = [], []
    for _ in range(n_boot):
        ii = np.concatenate([idx[c] for c in rng.choice(u, len(u), replace=True)])
        means.append(d[ii].mean())
        meds.append(np.median(d[ii]))
    q = lambda v: [float(np.quantile(v, 0.025)), float(np.quantile(v, 0.975))]  # noqa: E731
    return q(means), q(meds), len(u)


def _signflip_p(d, clusters, n_mc=20000, seed=0):
    """Two-sided sign-flip randomisation test of the building-weighted mean difference.
    Clusters (sites) are flipped as wholes; exact enumeration for <= 16 clusters, Monte Carlo otherwise."""
    d = np.asarray(d, dtype=float)
    cl = np.asarray(clusters)
    u, inv = np.unique(cl, return_inverse=True)
    sums = np.bincount(inv, weights=d)
    obs = abs(sums.sum())
    if len(u) <= 16:
        signs = np.array(list(itertools.product([1, -1], repeat=len(u))))
    else:
        rng = np.random.default_rng(seed)
        signs = rng.choice([1, -1], size=(n_mc, len(u)))
    stat = np.abs(signs @ sums)
    return float((np.sum(stat >= obs - 1e-12)) / len(stat)), len(u)


def holm(p):
    p = np.asarray(p, dtype=float)
    o = np.argsort(p)
    m = len(p)
    adj = np.empty(m)
    run = 0
    for k, i in enumerate(o):
        run = max(run, (m - k) * p[i])
        adj[i] = min(run, 1.0)
    return adj


METRICS = ["abs_dev", "under", "rel_IS", "reserve_cost", "book_fail"]


def paired_tests(df, exp, dataset, protocol, proposed, baselines, alpha=0.1, perturb="none", family="",
                 metrics=METRICS):
    q = (df.exp == exp) & (df.dataset == dataset) & (df.protocol == protocol) & (df.alpha == alpha) & \
        (df.perturb == perturb)
    t = df[q]
    b = t.groupby(["method", "building_id"]).agg(**{m: (m, "mean") for m in metrics},
                                                 site=("site_id", "first")).reset_index()
    if proposed not in set(b.method):
        return pd.DataFrame()
    P = b[b.method == proposed].set_index("building_id")
    res = []
    for bl in baselines:
        if bl not in set(b.method) or bl == proposed:
            continue
        B = b[b.method == bl].set_index("building_id")
        common = P.index.intersection(B.index)
        common = [c for c in common if np.isfinite(P.loc[c, "rel_IS"]) and np.isfinite(B.loc[c, "rel_IS"])]
        sites = P.loc[common, "site"].values
        clusters = sites if len(np.unique(sites)) >= 5 else np.arange(len(common))
        for metric in metrics:
            d = (P.loc[common, metric] - B.loc[common, metric]).values  # negative = proposed better
            if np.any(d != 0):
                _, pw = wilcoxon(d, zero_method="wilcox", alternative="two-sided")
                pr, ncl = _signflip_p(d, clusters)
            else:
                pw, pr, ncl = 1.0, 1.0, len(np.unique(clusters))
            ci_mean, ci_med, _ = _cluster_boot(d, clusters)
            res.append(dict(family=family, exp=exp, dataset=dataset, protocol=protocol, alpha=alpha, perturb=perturb,
                            proposed=proposed, baseline=bl, metric=metric, n_buildings=len(common),
                            n_clusters=int(ncl), mean_diff=float(d.mean()), ci95_mean_diff=ci_mean,
                            median_diff=float(np.median(d)), ci95_median_diff=ci_med,
                            share_proposed_better=float(np.mean(d < 0)), share_tied=float(np.mean(d == 0)),
                            rank_biserial=_rank_biserial(-d), p_rand=float(pr), p_wilcoxon=float(pw)))
    r = pd.DataFrame(res)
    if len(r):
        for metric in metrics:
            m = r.metric == metric
            r.loc[m, "p_holm"] = holm(r.loc[m, "p_rand"].values)
            r.loc[m, "p_wilcoxon_holm"] = holm(r.loc[m, "p_wilcoxon"].values)
    return r


def _md(df, path, caption, digits=3):
    df.to_csv(path + ".csv", index=False)
    with open(path + ".md", "w") as f:
        f.write(f"**{caption}**\n\n" + df.round(digits).to_markdown(index=False) + "\n")


def week_table(s, ds, methods):
    t = summary_table(s, "main", ds, "random", methods=methods)
    rows = []
    for m, r in t.iterrows():
        row = {"Method": m}
        for w, lab in WEEKS:
            row[f"Under-cov. {lab}"] = r[f"under_{w}"]
            row[f"P10 {lab}"] = r[f"p10_{w}"]
        rows.append(row)
    return pd.DataFrame(rows)


def run(mode="full"):
    df = load()
    tag = "_quick" if mode == "quick" else ""
    df = df[df.part.str.contains("_quick") == (mode == "quick")]
    s = seed_level(df)
    s.to_csv(os.path.join(RES, "seed_level_metrics.csv"), index=False)
    os.makedirs(TAB, exist_ok=True)
    stats, metrics = [], {}
    # ---- main protocol
    for ds in ["BDG2", "UCI"]:
        t = summary_table(s, "main", ds, "random")
        if not len(t):
            continue
        fmt_table(t, os.path.join(TAB, f"T_main_{ds}"), f"Main results, {ds}, 90 % nominal, mean ± s.d. over seeds")
        metrics[f"main_{ds}"] = t.round(4).to_dict(orient="index")
        stats.append(paired_tests(df, "main", ds, "random", PRIMARY, FAMILY_MAIN, family="main"))
        stats.append(paired_tests(df, "main", ds, "random", PRIMARY, FAMILY_OTHER, family="other"))
        stats.append(paired_tests(df, "main", ds, "random", PRIMARY, FAMILY_DESIGN, family="design"))
        stats.append(paired_tests(df, "main", ds, "random", "HSC", FAMILY_PREREG, family="preregistered-abs"))
        stats.append(paired_tests(df, "main", ds, "random", "HSC-CQR", ["CQR", "Self-CQR", "ACI-CQR", "QShrink-CQR",
                                                                         "TQA-B-CQR", "GHCP-CQR"],
                                  family="preregistered-cqr-variant"))
        stats.append(paired_tests(df, "main", ds, "random", "PCS-CQR (MLP)", ["CQR (MLP)", "MLP-QR"], family="mlp"))
        stats.append(paired_tests(df, "main", ds, "random", "PCS", ["Self-CP", "SCP-stage", "ACI", "HSC"],
                                  family="abs-score"))
        wt = week_table(s, ds, ["PCS-CQR", "PCS-CQR κ=168", "PCS-CQR +stage", "HSC-CQR", "QShrink-CQR (MACD)",
                                "Self-CQR", "ACI-CQR", "ACI-CQR (MACD)", "TQA-B-CQR", "GHCP-CQR", "CQR"])
        _md(wt, os.path.join(TAB, f"T_weeks_{ds}"), f"Per-building reliability by onboarding week, {ds}")
        metrics[f"weeks_{ds}"] = wt.round(4).to_dict(orient="records")
        for a in [0.05, 0.2]:
            ta = summary_table(s, "main", ds, "random", alpha=a)
            if len(ta):
                fmt_table(ta, os.path.join(TAB, f"T_alpha{a}_{ds}"), f"{ds}, nominal {NOM[a]:.0%}")
                metrics[f"alpha{a}_{ds}"] = ta.round(4).to_dict(orient="index")
                stats.append(paired_tests(df, "main", ds, "random", PRIMARY, FAMILY_SHORT, alpha=a,
                                          family=f"alpha{a}"))
    # ---- design / ablation table
    for ds in ["BDG2", "UCI"]:
        t = summary_table(s, "main", ds, "random", methods=["PCS-CQR"] + FAMILY_DESIGN + ["CQR", "Self-CQR", "HSC",
                                                                                         "HSC -stage", "HSC -kNN",
                                                                                         "HSC -shrink", "PCS",
                                                                                         "Self-CP", "SCP-stage"])
        if len(t):
            fmt_table(t, os.path.join(TAB, f"T_ablation_{ds}"), f"Design elements and ablations, {ds}")
    # ---- generalisation
    for exp, ds, prot in [("lso", "BDG2", "leave-site-out")] + \
            [("xds", d, p) for d, p in [("UCI", "BDG2->UCI (no weather)"), ("BDG2", "UCI->BDG2 (no weather)"),
                                        ("BDG2", "BDG2->BDG2 (no weather)")]]:
        t = summary_table(s, exp, ds, prot)
        if len(t):
            nm = prot.replace("->", "to").replace(" (no weather)", "_nw").replace(" ", "")
            fmt_table(t, os.path.join(TAB, f"T_gen_{nm}"), f"Generalisation: {prot}")
            metrics[f"gen_{nm}"] = t.round(4).to_dict(orient="index")
            stats.append(paired_tests(df, exp, ds, prot, PRIMARY, FAMILY_SHORT + ["PCS-CQR +kNN+stage",
                                                                                  "PCS-CQR site-grouped"],
                                      family="generalisation"))
    _loso_sites(df)
    # ---- robustness (BDG2): every perturbation with s.d. and tests
    rb = s[s.exp == "robust"]
    if len(rb):
        keep = ["PCS-CQR", "PCS-CQR κ=168", "HSC-CQR", "CQR", "Self-CQR", "ACI-CQR", "ACI-CQR (MACD)", "TQA-B-CQR",
                "GHCP-CQR", "QShrink-CQR", "QShrink-CQR (MACD)", "QR-LGBM", "SCP-stage", "Self-CP"]
        g = rb[rb.method.isin(keep)].groupby(["perturb", "method"])
        rt = g[["mean_cov", "macd", "under_rate", "under_w1", "under_w58", "rel_IS", "rel_width", "book_fail"]] \
            .mean().reset_index()
        sd = g[["macd", "under_rate"]].std().reset_index().rename(columns={"macd": "macd_sd",
                                                                          "under_rate": "under_rate_sd"})
        rt = rt.merge(sd, on=["perturb", "method"])
        rt.to_csv(os.path.join(TAB, "T_robustness.csv"), index=False)
        with open(os.path.join(TAB, "T_robustness.md"), "w") as f:
            f.write("**Robustness (BDG2, mean over 3 seeds; s.d. over seeds)**\n\n" + rt.round(3).to_markdown(index=False)
                    + "\n")
        metrics["robustness"] = rt.round(4).to_dict(orient="records")
        for p in rb.perturb.unique():
            stats.append(paired_tests(df, "robust", "BDG2", "random", PRIMARY, FAMILY_SHORT, perturb=p,
                                      family="robustness"))
    # ---- small calibration pools
    pools = s[s.exp == "pools"]
    if len(pools):
        keep = ["PCS-CQR", "PCS-CQR κ=168", "PCS-CQR (IS-tuned)", "CQR", "Self-CQR", "ACI-CQR", "QShrink-CQR (MACD)",
                "TQA-B-CQR", "GHCP-CQR"]
        g = pools[pools.method.isin(keep)].groupby(["perturb", "method"])
        pt = g[["macd", "under_rate", "under_w1", "rel_IS", "mean_cov"]].mean().reset_index()
        pt = pt.merge(g[["under_rate"]].std().reset_index().rename(columns={"under_rate": "under_rate_sd"}),
                      on=["perturb", "method"])
        pt["n_cal"] = pt.perturb.str.extract(r"(\d+)").astype(int)
        pt = pt.sort_values(["n_cal", "method"]).drop(columns="n_cal")
        _md(pt, os.path.join(TAB, "T_pools"), "Small calibration pools (BDG2; mean over 3 seeds x 5 resamples)")
        metrics["pools"] = pt.round(4).to_dict(orient="records")
    st = pd.concat([x for x in stats if len(x)], ignore_index=True)
    st.to_csv(os.path.join(RES, "statistics.csv"), index=False)
    with open(os.path.join(RES, "statistics.json"), "w") as f:
        json.dump(st.to_dict(orient="records"), f, indent=1)
    with open(os.path.join(RES, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=1, default=float)
    main_t = st[(st.perturb == "none") & (st.alpha == 0.1)].copy()
    main_t["CI95"] = main_t.ci95_mean_diff.apply(lambda c: f"[{c[0]:.4f}, {c[1]:.4f}]")
    main_t["CI95_median"] = main_t.ci95_median_diff.apply(lambda c: f"[{c[0]:.4f}, {c[1]:.4f}]")
    main_t = main_t[["family", "dataset", "protocol", "proposed", "baseline", "metric", "n_buildings", "n_clusters",
                     "mean_diff", "CI95", "median_diff", "CI95_median", "share_proposed_better", "rank_biserial",
                     "p_holm", "p_wilcoxon_holm"]]
    _md(main_t, os.path.join(TAB, "T_tests"), "Paired per-building comparisons (site-cluster randomisation tests for "
        "BDG2, building-level for UCI; Holm-adjusted)", digits=4)
    _tuning(tag)
    _efficiency(tag)
    if mode != "quick":
        from src.statistics import manuscript_tables, error_analysis
        manuscript_tables.run()
        error_analysis.run()
    return st


def _loso_sites(df):
    """Per held-out site (leave-one-site-out, 3 training seeds): under-covered share and MACD."""
    t = df[(df.exp == "lso") & (df.alpha == 0.1)]
    if not len(t):
        return
    keep = ["PCS-CQR", "PCS-CQR κ=168", "PCS-CQR +kNN+stage", "HSC-CQR", "CQR", "Self-CQR", "QShrink-CQR (MACD)",
            "ACI-CQR", "TQA-B-CQR", "GHCP-CQR"]
    t = t[t.method.isin(keep)]
    g = t.groupby(["site_id", "method"]).agg(n_buildings=("building_id", "nunique"), under=("under", "mean"),
                                              macd=("abs_dev", "mean")).reset_index()
    w = g.pivot(index=["site_id", "n_buildings"], columns="method", values="under").reset_index()
    w = w[["site_id", "n_buildings"] + [m for m in keep if m in w]]
    _md(w, os.path.join(TAB, "T_loso_sites"), "Leave-one-site-out: under-covered share per held-out site "
        "(building x seed units, 3 training seeds)")
    # site-balanced summary: mean over sites of the per-site share
    bal = g.groupby("method")[["under", "macd"]].mean().reset_index()
    _md(bal, os.path.join(TAB, "T_loso_site_balanced"), "Leave-one-site-out, site-balanced means")


def _tuning(tag):
    """Selected pseudo-counts and flatness of the LOBO objectives (main protocol)."""
    info = json.load(open(os.path.join(RES, "run_info.json")))
    rows, curves = [], []
    for k, v in info.items():
        if "tune_pcs_cqr" not in v:
            continue
        rows.append(dict(part=k, pcs_kappa=v["pcs_cqr"]["kappa"], pcs_is_kappa=v.get("hsc_cqr_simple", {}).get("kappa"),
                         hsc_cqr_K=(v.get("hsc_cqr") or {}).get("K"), hsc_cqr_kappa=(v.get("hsc_cqr") or {}).get("kappa"),
                         qshrink_is=v.get("qshrink_lambda"), qshrink_macd=v.get("qshrink_lambda_macd"),
                         aci_gamma_is=v.get("aci_cqr_gamma"), aci_gamma_macdc=v.get("aci_cqr_gamma_macdc"),
                         aci_gamma_cov=v.get("aci_cqr_gamma_cov"),
                         grouped_kappa=(v.get("pcs_cqr_grouped") or {}).get("kappa")))
        if k.startswith("main" + tag + "_") and k.endswith("a0.1"):
            for r in v["tune_pcs_cqr"]:
                curves.append(dict(part=k, **r))
    if rows:
        _md(pd.DataFrame(rows), os.path.join(TAB, "T_tuning"), "Selected tuning parameters per run")
    if curves:
        c = pd.DataFrame(curves)
        _md(c, os.path.join(TAB, "T_tuning_curves"), "LOBO objectives of PCS-CQR on calibration buildings", digits=4)


def _efficiency(tag):
    info = json.load(open(os.path.join(RES, "run_info.json")))
    rows, meth = [], []
    for k, v in info.items():
        if not k.startswith("main" + tag + "_") or not k.endswith("a0.1"):
            continue
        rows.append(dict(part=k, train_total_s=v.get("train_total"), lgb_train_s=v.get("lgb"),
                         mlp_train_s=v.get("mlp"), n_train_rows=v.get("n_train_rows"),
                         lgb_pred_ms_per_target_day=1e3 * v.get("pred_lgb_per_target_day", np.nan),
                         pcs_apply_ms_per_target_day=1e3 * v.get("t_pcs_apply_per_target_day", np.nan),
                         pcs_apply_incl_hist_ms=1e3 * v.get("t_pcs_apply_incl_hist_per_target_day", np.nan),
                         calibration_total_s=v.get("t_calibration_total"), pcs_store_MB=v.get("pcs_store_MB")))
        for m, t in (v.get("t_method") or {}).items():
            meth.append(dict(part=k, strategy=m, seconds=t))
    if rows:
        e = pd.DataFrame(rows)
        _md(e, os.path.join(TAB, "T_efficiency"), "Computational cost per run (calibration in single-threaded workers)", 4)
    if meth:
        m = pd.DataFrame(meth)
        m["dataset"] = m.part.str.extract(r"main_(\w+?)_s")[0]
        mt = m.groupby(["dataset", "strategy"]).seconds.agg(["median", "min", "max"]).reset_index()
        _md(mt, os.path.join(TAB, "T_cost_strategies"), "Wall-clock time per calibration strategy and run "
            "(tuning + application for all targets; median and range over seeds)", 3)
