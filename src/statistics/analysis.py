"""Statistical analysis and automatic table generation (all numbers come from results/raw_results.csv).

Unit of analysis: target building. A building can be a target in several partition seeds; its
metrics are first averaged over those seeds, so each building contributes one paired observation.
Tests: two-sided Wilcoxon signed-rank (paired, non-parametric: per-building metric differences are
skewed and heavy-tailed), Holm correction within each comparison family, matched-pairs rank-biserial
correlation as effect size, 95 % CI of the mean paired difference by cluster bootstrap over sites
(BDG2; buildings within a site share weather/operation) or over buildings (UCI; single site).
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RES = os.path.join(ROOT, "results")
TAB = os.path.join(ROOT, "tables")
NOM = {0.1: 0.9, 0.05: 0.95, 0.2: 0.8}

PROPOSED = ["HSC-CQR", "HSC"]
FAMILY_CQR = ["CQR", "Self-CQR", "ACI-CQR", "QR-LGBM", "MLP-QR", "MLP-Gauss", "SCP-stage", "ACI", "Self-CP",
              "Mondrian-usage", "Naive+SCP", "HSC"]
FAMILY_ABS = ["SCP", "SCP-stage", "Mondrian-usage", "Self-CP", "ACI", "Raw-SCP"]
ABLATIONS = ["HSC -stage", "HSC -kNN", "HSC -shrink", "HSC fixed-kappa", "HSC -kNN -stage"]
ABLATIONS_CQR = ["HSC-CQR -stage", "HSC-CQR -kNN", "HSC-CQR -shrink", "Self-CQR", "CQR"]
ORDER = ["HSC-CQR", "HSC", "CQR", "Self-CQR", "ACI-CQR", "QR-LGBM", "MLP-QR", "MLP-Gauss", "ACI", "Self-CP",
         "SCP-stage", "SCP", "Mondrian-usage", "Naive+SCP", "Raw-SCP"] + ABLATIONS + ABLATIONS_CQR[:3]


def load():
    df = pd.read_csv(os.path.join(RES, "raw_results.csv"))
    df["nominal"] = df["alpha"].map(NOM)
    df["abs_dev"] = (df["coverage"] - df["nominal"]).abs()
    df["under"] = (df["coverage"] < df["nominal"] - 0.05).astype(float)
    return df


def seed_level(df):
    g = df.groupby(["exp", "dataset", "protocol", "perturb", "alpha", "method", "seed"])
    s = g.agg(mean_cov=("coverage", "mean"), macd=("abs_dev", "mean"), under_rate=("under", "mean"),
              p10_cov=("coverage", lambda c: np.quantile(c, 0.1)), rel_width=("rel_width", "median"),
              rel_IS_mean=("rel_IS", "mean"), rel_IS=("rel_IS", "median"),
              rel_IS_early=("rel_IS_early", "median"), cov_early=("coverage_early", "mean"),
              n=("coverage", "size")).reset_index()
    return s


def summary_table(s, exp, dataset=None, protocol=None, perturb="none", alpha=0.1, methods=None):
    q = (s.exp == exp) & (s.perturb == perturb) & (s.alpha == alpha)
    if dataset is not None:
        q &= s.dataset == dataset
    if protocol is not None:
        q &= s.protocol == protocol
    t = s[q]
    cols = ["mean_cov", "cov_early", "macd", "under_rate", "p10_cov", "rel_width", "rel_IS", "rel_IS_mean"]
    agg = t.groupby("method")[cols].agg(["mean", "std"])
    out = pd.DataFrame(index=agg.index)
    for c in cols:
        out[c] = agg[(c, "mean")]
        out[c + "_sd"] = agg[(c, "std")].fillna(0)
    out["n_seeds"] = t.groupby("method").seed.nunique()
    order = [m for m in (methods or ORDER) if m in out.index]
    return out.loc[order]


def fmt_table(t, path_stub, caption):
    rows = []
    for m, r in t.iterrows():
        rows.append(dict(Method=m,
                         Coverage=f"{r.mean_cov:.3f} ± {r.mean_cov_sd:.3f}",
                         **{"Coverage (week 1)": f"{r.cov_early:.3f} ± {r.cov_early_sd:.3f}"},
                         MACD=f"{r.macd:.3f} ± {r.macd_sd:.3f}",
                         **{"Under-covered share": f"{r.under_rate:.3f} ± {r.under_rate_sd:.3f}"},
                         **{"P10 coverage": f"{r.p10_cov:.3f} ± {r.p10_cov_sd:.3f}"},
                         **{"Rel. width (median)": f"{r.rel_width:.3f} ± {r.rel_width_sd:.3f}"},
                         **{"Rel. IS (median)": f"{r.rel_IS:.3f} ± {r.rel_IS_sd:.3f}"}))
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


def _cluster_boot_ci(d, clusters, n_boot=2000, seed=0):
    rng = np.random.default_rng(seed)
    d = np.asarray(d)
    cl = np.asarray(clusters)
    u = np.unique(cl)
    idx = {c: np.where(cl == c)[0] for c in u}
    if len(u) < 5:  # too few clusters: bootstrap units instead
        u = np.arange(len(d))
        idx = {i: np.array([i]) for i in u}
    means = []
    for _ in range(n_boot):
        pick = rng.choice(u, len(u), replace=True)
        ii = np.concatenate([idx[c] for c in pick])
        means.append(d[ii].mean())
    return [float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))]


def holm(p):
    p = np.asarray(p)
    o = np.argsort(p)
    m = len(p)
    adj = np.empty(m)
    run = 0
    for k, i in enumerate(o):
        run = max(run, (m - k) * p[i])
        adj[i] = min(run, 1.0)
    return adj


def paired_tests(df, exp, dataset, protocol, proposed, baselines, alpha=0.1, perturb="none"):
    q = (df.exp == exp) & (df.dataset == dataset) & (df.protocol == protocol) & (df.alpha == alpha) & \
        (df.perturb == perturb)
    t = df[q]
    b = t.groupby(["method", "building_id"]).agg(rel_IS=("rel_IS", "mean"), abs_dev=("abs_dev", "mean"),
                                                 site=("site_id", "first")).reset_index()
    P = b[b.method == proposed].set_index("building_id")
    res = []
    for bl in baselines:
        if bl not in set(b.method) or bl == proposed:
            continue
        B = b[b.method == bl].set_index("building_id")
        common = P.index.intersection(B.index)
        for metric in ["rel_IS", "abs_dev"]:
            d = (P.loc[common, metric] - B.loc[common, metric]).values  # negative = proposed better
            stat, p = wilcoxon(d, zero_method="wilcox", alternative="two-sided") if np.any(d != 0) else (np.nan, 1.0)
            res.append(dict(dataset=dataset, protocol=protocol, alpha=alpha, perturb=perturb, proposed=proposed,
                            baseline=bl, metric=metric, n_buildings=len(common), mean_diff=float(d.mean()),
                            median_diff=float(np.median(d)), share_proposed_better=float(np.mean(d < 0)),
                            rank_biserial=_rank_biserial(-d),  # positive = proposed better
                            ci95_mean_diff=_cluster_boot_ci(d, P.loc[common, "site"].values),
                            W=float(stat), p=float(p)))
    r = pd.DataFrame(res)
    if len(r):
        for metric in ["rel_IS", "abs_dev"]:
            m = r.metric == metric
            r.loc[m, "p_holm"] = holm(r.loc[m, "p"].values)
    return r


def run(mode="full"):
    df = load()
    tag = "_quick" if mode == "quick" else ""
    df = df[df.part.str.contains("_quick") == (mode == "quick")]
    s = seed_level(df)
    s.to_csv(os.path.join(RES, "seed_level_metrics.csv"), index=False)
    os.makedirs(TAB, exist_ok=True)
    stats = []
    metrics = {}
    # ---- E1/E2 main
    for ds in ["BDG2", "UCI"]:
        t = summary_table(s, "main", ds, "random")
        if len(t):
            fmt_table(t, os.path.join(TAB, f"T_main_{ds}"), f"Main results, {ds}, 90 % nominal, mean ± s.d. over seeds")
            metrics[f"main_{ds}"] = t.round(4).to_dict(orient="index")
            stats.append(paired_tests(df, "main", ds, "random", "HSC-CQR", FAMILY_CQR))
            stats.append(paired_tests(df, "main", ds, "random", "HSC", FAMILY_ABS))
            stats.append(paired_tests(df, "main", ds, "random", "HSC", ABLATIONS))
            stats.append(paired_tests(df, "main", ds, "random", "HSC-CQR", ABLATIONS_CQR[:3]))
        for a in [0.05, 0.2]:
            t = summary_table(s, "main", ds, "random", alpha=a)
            if len(t):
                fmt_table(t, os.path.join(TAB, f"T_alpha{a}_{ds}"), f"{ds}, nominal {NOM[a]:.0%}")
                metrics[f"alpha{a}_{ds}"] = t.round(4).to_dict(orient="index")
                stats.append(paired_tests(df, "main", ds, "random", "HSC", FAMILY_ABS, alpha=a))
    # ---- ablation table (BDG2+UCI)
    for ds in ["BDG2", "UCI"]:
        t = summary_table(s, "main", ds, "random", methods=["HSC"] + ABLATIONS + ["SCP-stage", "Self-CP",
                                                                                    "HSC-CQR"] + ABLATIONS_CQR)
        if len(t):
            fmt_table(t, os.path.join(TAB, f"T_ablation_{ds}"), f"Ablation, {ds}")
    # ---- E5 generalisation
    for exp, ds, prot in [("lso", "BDG2", "leave-site-out")] + \
            [("xds", d, p) for d, p in [("UCI", "BDG2->UCI (no weather)"), ("BDG2", "UCI->BDG2 (no weather)"),
                                        ("BDG2", "BDG2->BDG2 (no weather)")]]:
        t = summary_table(s, exp, ds, prot)
        if len(t):
            nm = prot.replace("->", "to").replace(" (no weather)", "_nw").replace(" ", "")
            fmt_table(t, os.path.join(TAB, f"T_gen_{nm}"), f"Generalisation: {prot}")
            metrics[f"gen_{nm}"] = t.round(4).to_dict(orient="index")
            stats.append(paired_tests(df, exp, ds, prot, "HSC-CQR", FAMILY_CQR))
            stats.append(paired_tests(df, exp, ds, prot, "HSC", FAMILY_ABS))
    # ---- E4 robustness
    rb = s[s.exp == "robust"]
    if len(rb):
        keep = ["HSC-CQR", "HSC", "CQR", "Self-CQR", "ACI-CQR", "QR-LGBM", "MLP-QR", "ACI", "SCP-stage", "Self-CP"]
        rt = rb[rb.method.isin(keep)].groupby(["perturb", "method"])[["mean_cov", "macd", "under_rate", "rel_IS",
                                                                      "rel_width"]].mean().reset_index()
        rt.to_csv(os.path.join(TAB, "T_robustness.csv"), index=False)
        with open(os.path.join(TAB, "T_robustness.md"), "w") as f:
            f.write("**Robustness (BDG2, mean over seeds)**\n\n" + rt.round(3).to_markdown(index=False) + "\n")
        metrics["robustness"] = rt.round(4).to_dict(orient="records")
        for p in rb.perturb.unique():
            stats.append(paired_tests(df, "robust", "BDG2", "random", "HSC-CQR", ["CQR", "Self-CQR", "ACI-CQR",
                                                                                  "QR-LGBM", "MLP-QR"],
                                      perturb=p))
            stats.append(paired_tests(df, "robust", "BDG2", "random", "HSC", ["SCP-stage", "ACI", "Self-CP"],
                                      perturb=p))
    st = pd.concat([x for x in stats if len(x)], ignore_index=True)
    st.to_csv(os.path.join(RES, "statistics.csv"), index=False)
    with open(os.path.join(RES, "statistics.json"), "w") as f:
        json.dump(st.to_dict(orient="records"), f, indent=1)
    with open(os.path.join(RES, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=1, default=float)
    # compact test table for the manuscript
    main_t = st[(st.perturb == "none") & (st.alpha == 0.1)].copy()
    main_t["CI95"] = main_t.ci95_mean_diff.apply(lambda c: f"[{c[0]:.3f}, {c[1]:.3f}]")
    main_t = main_t[["dataset", "protocol", "proposed", "baseline", "metric", "n_buildings", "mean_diff", "CI95",
                     "median_diff", "share_proposed_better", "rank_biserial", "p_holm"]]
    main_t.to_csv(os.path.join(TAB, "T_tests.csv"), index=False)
    with open(os.path.join(TAB, "T_tests.md"), "w") as f:
        f.write("**Paired Wilcoxon signed-rank tests (per building; Holm-adjusted)**\n\n" +
                main_t.round(4).to_markdown(index=False) + "\n")
    _efficiency(tag)
    return st


def _efficiency(tag):
    info = json.load(open(os.path.join(RES, "run_info.json")))
    rows = []
    for k, v in info.items():
        if not k.startswith("main" + tag + "_") or not k.endswith("a0.1"):
            continue
        rows.append(dict(part=k, train_total_s=v.get("train_total"), lgb_train_s=v.get("lgb"),
                         mlp_train_s=v.get("mlp"), n_train_rows=v.get("n_train_rows"),
                         lgb_pred_ms_per_target_day=1e3 * v.get("pred_lgb_per_target_day", np.nan),
                         hsc_tune_s=v.get("t_tune_hsc"),
                         hsc_apply_ms_per_target_day=1e3 * v.get("t_hsc_apply_per_target_day", np.nan),
                         scp_s=v.get("t_scp"), calibration_total_s=v.get("t_calibration_total"),
                         hsc_store_MB=v.get("hsc_store_MB")))
    if rows:
        e = pd.DataFrame(rows)
        e.to_csv(os.path.join(TAB, "T_efficiency.csv"), index=False)
        with open(os.path.join(TAB, "T_efficiency.md"), "w") as f:
            f.write("**Computational cost (4 CPU cores)**\n\n" + e.round(4).to_markdown(index=False) + "\n")
