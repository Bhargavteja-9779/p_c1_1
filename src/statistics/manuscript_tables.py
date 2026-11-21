"""Compact manuscript tables (tables/MS_*.md), generated from results/seed_level_metrics.csv and
results/statistics.csv. Values: mean ± s.d. over seeds/folds."""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RES = os.path.join(ROOT, "results")
TAB = os.path.join(ROOT, "tables")

# display names (revision 1): the one-parameter layer is called SSC (score-shrinkage conformal); code names unchanged
DISPLAY = {"HSC-CQR simple": "SSC-CQR (primary)", "HSC-CQR fixed-κ": "SSC-CQR (κ=168)",
           "HSC-CQR simple (IS-tuned)": "SSC-CQR (IS-tuned)", "HSC-CQR": "SSC-CQR +stage+kNN",
           "HSC-CQR -stage": "SSC-CQR +kNN", "HSC-CQR -kNN": "SSC-CQR +stage", "HSC-CQR -shrink": "+stage+kNN, κ=∞",
           "HSC": "SSC +stage+kNN (abs; pre-reg.)", "HSC -stage": "SSC +kNN (abs)", "HSC -kNN": "SSC +stage (abs)",
           "HSC simple": "SSC (abs)", "HSC -shrink": "+stage+kNN, κ=∞ (abs)", "HSC-CQR (MLP)": "SSC-CQR (MLP)",
           "QShrink-CQR fixed-λ": "QShrink-CQR (λ=168)"}


def dn(m):
    return DISPLAY.get(m, m)


MAIN_METHODS = ["HSC-CQR simple", "HSC-CQR fixed-κ", "HSC-CQR simple (IS-tuned)", "HSC-CQR", "QShrink-CQR",
                "QShrink-CQR fixed-λ", "Self-CQR-fb", "Self-CQR", "ACI-CQR", "TQA-B-CQR", "GHCP-CQR", "Mondrian-CQR",
                "CQR", "QR-LGBM", "MLP-QR", "MLP-Gauss", "HSC-CQR (MLP)", "CQR (MLP)", "Naive+SCP"]
SI_METHODS = ["HSC", "HSC simple", "ACI", "Self-CP", "SCP-stage", "SCP", "Mondrian-usage", "Raw-SCP"]
GEN_METHODS = ["HSC-CQR simple", "HSC-CQR fixed-κ", "HSC-CQR", "QShrink-CQR", "Self-CQR-fb", "Self-CQR", "ACI-CQR",
               "TQA-B-CQR", "GHCP-CQR", "CQR"]
WIN_METHODS = ["HSC-CQR simple", "HSC-CQR fixed-κ", "HSC-CQR", "QShrink-CQR", "Self-CQR-fb", "ACI-CQR", "TQA-B-CQR",
               "GHCP-CQR", "CQR"]


def _pm(m, s, d=3, pct=False):
    if pd.isna(m):
        return "–"
    if pct:
        return f"{100 * m:.1f} ± {100 * (0 if pd.isna(s) else s):.1f}"
    return f"{m:.{d}f} ± {(0 if pd.isna(s) else s):.{d}f}"


def _write(name, df, caption):
    os.makedirs(TAB, exist_ok=True)
    df.to_csv(os.path.join(TAB, name + ".csv"), index=False)
    with open(os.path.join(TAB, name + ".md"), "w") as f:
        f.write(df.to_markdown(index=False) + "\n")
    with open(os.path.join(TAB, name + ".caption.txt"), "w") as f:
        f.write(caption)


def main_table(s, ds, methods=None, name=None, note=""):
    t = s[(s.exp == "main") & (s.dataset == ds) & (s.alpha == 0.1) & (s.perturb == "none")]
    g = t.groupby("method")
    rows = []
    for m in (methods or MAIN_METHODS):
        if m not in g.groups:
            continue
        x = g.get_group(m)
        rows.append({"Method": dn(m),
                     "Coverage": _pm(x.mean_cov.mean(), x.mean_cov.std()),
                     "MACD": _pm(x.macd.mean(), x.macd.std()),
                     "Under-cov. (%)": _pm(x.under_rate.mean(), x.under_rate.std(), pct=True),
                     "P10 cov.": _pm(x.p10_cov.mean(), x.p10_cov.std()),
                     "Rel. width": _pm(x.rel_width.mean(), x.rel_width.std()),
                     "Rel. IS": _pm(x.rel_IS.mean(), x.rel_IS.std())})
    n_b = int(t[t.method == "CQR"].n.mean()) if len(t) else 0
    _write(name or f"MS_main_{ds}", pd.DataFrame(rows),
           f"Per-building interval reliability and sharpness on {ds} (random-building protocol, nominal 90 %, "
           f"{t.seed.nunique()} seeds, ≈{n_b} target buildings per seed). Coverage: mean per-building coverage over the "
           f"56-day onboarding window; MACD: mean |coverage − 0.90|; Under-cov.: share of buildings with coverage < "
           f"0.85; P10: 10th percentile of per-building coverage; Rel. width and Rel. IS: medians over buildings of "
           f"width and interval score divided by the building's mean load. Mean ± s.d. over seeds.{note}")


def window_table():
    rows = []
    for ds in ["BDG2", "UCI"]:
        f = os.path.join(TAB, f"T_windows_{ds}.csv")
        if not os.path.exists(f):
            continue
        w = pd.read_csv(f, index_col=0)
        for m in WIN_METHODS:
            if m not in w.index:
                continue
            r = w.loc[m]
            row = {"Data": ds, "Method": dn(m)}
            for k, lab in (("w1", "Week 1"), ("w2", "Week 2"), ("w3_8", "Weeks 3–8")):
                if f"macd_{k}_mean" in r:
                    row[f"{lab} MACD"] = _pm(r[f"macd_{k}_mean"], r[f"macd_{k}_std"])
                    row[f"{lab} under (%)"] = _pm(r[f"under_{k}_mean"], r[f"under_{k}_std"], pct=True)
            rows.append(row)
        floor = float(w["iid_floor_under_168h"].iloc[0])
    if rows:
        _write("MS_windows", pd.DataFrame(rows),
               "Per-building reliability by onboarding window (random-building protocol, 90 %, mean ± s.d. over seeds). "
               "Under = share of buildings with window coverage < 0.85. For a perfectly calibrated building with "
               f"168 independent hourly outcomes this share would be {100 * floor:.1f} % (higher under autocorrelation).")


def tests_table(st):
    rows = []
    t = st[(st.perturb == "none") & (st.alpha == 0.1) & (st.proposed == "HSC-CQR simple") & (st.protocol == "random")]
    keep = ["CQR", "Self-CQR-fb", "ACI-CQR", "TQA-B-CQR", "GHCP-CQR", "QShrink-CQR",  # confirmatory
            "HSC-CQR fixed-κ", "QShrink-CQR fixed-λ", "HSC-CQR", "Self-CQR", "QR-LGBM", "MLP-QR"]
    for ds in ["BDG2", "UCI"]:
        for bl in keep:
            for metric, lab in [("abs_dev", "CD"), ("under", "Under"), ("rel_IS", "IS")]:
                r = t[(t.dataset == ds) & (t.baseline == bl) & (t.metric == metric)]
                if not len(r):
                    continue
                r = r.iloc[0]
                ci = r.ci95_median_diff
                ci = [float(x) for x in ci.strip("[]").split(",")] if isinstance(ci, str) else ci
                ps = r.p_site_holm if pd.notna(r.get("p_site_holm", np.nan)) else r.get("p_site", np.nan)
                rows.append({"Data": ds, "Baseline": dn(bl), "Family": "conf." if r.family == "confirmatory" else "expl.",
                             "Metric": lab, "Median diff.": f"{r.median_diff:+.4f}",
                             "95 % CI": f"[{ci[0]:+.4f}, {ci[1]:+.4f}]", "Mean diff.": f"{r.mean_diff:+.4f}",
                             "r_rb": f"{r.rank_biserial:+.2f}",
                             "p site": "–" if pd.isna(ps) else ("<0.001" if ps < 0.001 else f"{ps:.3f}"),
                             "p bldg": "<0.001" if r.p_holm < 0.001 else f"{r.p_holm:.3f}"})
    _write("MS_tests", pd.DataFrame(rows),
           "Paired per-building comparison of SSC-CQR (primary) with each baseline (random-building protocol, 90 %). "
           "CD = |cov_b − 0.9|; Under = under-coverage indicator (seed-averaged); IS = relative interval score. "
           "Differences = SSC-CQR minus baseline (negative = SSC-CQR better); median with 95 % site-cluster bootstrap CI "
           "(BDG2) or building bootstrap (UCI); r_rb = rank-biserial correlation (positive = SSC-CQR better). "
           "p site = exact sign-flip permutation test on site means (BDG2; primary, cluster-aware); p bldg = building-"
           "level Wilcoxon signed-rank (assumes independent buildings). Holm within family × metric; conf. = "
           "confirmatory family, expl. = exploratory.")


def ablation_table(s):
    rows = []
    meths = ["HSC-CQR simple", "HSC-CQR fixed-κ", "HSC-CQR simple (IS-tuned)", "HSC-CQR", "HSC-CQR -stage",
             "HSC-CQR -kNN", "HSC-CQR -shrink", "Self-CQR", "CQR",
             "HSC simple", "HSC", "HSC -stage", "HSC -kNN", "HSC -shrink", "Self-CP", "SCP-stage"]
    for m in meths:
        row = {"Variant": dn(m)}
        for ds in ["BDG2", "UCI"]:
            x = s[(s.exp == "main") & (s.dataset == ds) & (s.alpha == 0.1) & (s.perturb == "none") & (s.method == m)]
            if not len(x):
                continue
            row[f"{ds} MACD"] = _pm(x.macd.mean(), x.macd.std())
            row[f"{ds} Under (%)"] = _pm(x.under_rate.mean(), x.under_rate.std(), pct=True)
            row[f"{ds} Cov. wk 1"] = _pm(x.cov_early.mean(), x.cov_early.std())
            row[f"{ds} Rel. IS"] = _pm(x.rel_IS.mean(), x.rel_IS.std())
        rows.append(row)
    _write("MS_ablation", pd.DataFrame(rows),
           "Variants and ablations (random-building protocol, 90 %, mean ± s.d. over 5 seeds). '+stage': stage-matched "
           "prior; '+kNN': similarity-localised prior; 'κ=∞': prior only; κ=168: fixed one-week pseudo-count; IS-tuned: "
           "κ selected on the interval score instead of MACD; Self-*: κ = 0 with fallback to the pooled quantile. The "
           "+stage/+kNN variants are tuned on the interval score (pre-registered objective).")


def gen_table(s):
    combos = [("main", "BDG2", "random", "BDG2 random"), ("lso", "BDG2", "leave-site-out", "BDG2 leave-site-out"),
              ("xds", "BDG2", "BDG2->BDG2 (no weather)", "BDG2→BDG2 (no wx)"),
              ("xds", "BDG2", "UCI->BDG2 (no weather)", "UCI→BDG2 (no wx)"),
              ("main", "UCI", "random", "UCI random"), ("xds", "UCI", "BDG2->UCI (no weather)", "BDG2→UCI (no wx)")]
    rows = []
    for e, ds, p, lab in combos:
        x = s[(s.exp == e) & (s.dataset == ds) & (s.protocol == p) & (s.alpha == 0.1) & (s.perturb == "none")]
        if not len(x):
            continue
        for m in GEN_METHODS:
            y = x[x.method == m]
            if not len(y):
                continue
            rows.append({"Setting": lab, "Runs": y.seed.nunique(), "Method": dn(m),
                         "MACD": _pm(y.macd.mean(), y.macd.std()),
                         "Under-cov. (%)": _pm(y.under_rate.mean(), y.under_rate.std(), pct=True),
                         "Cov. wk 1": _pm(y.cov_early.mean(), y.cov_early.std()),
                         "Rel. IS": _pm(y.rel_IS.mean(), y.rel_IS.std())})
    _write("MS_generalisation", pd.DataFrame(rows),
           "Generalisation to unseen sites (BDG2 leave-site-out, 5 folds) and across datasets/countries (models and "
           "calibration scores from the source dataset, no weather features; 3 seeds). Paired tests for every setting: "
           "supplementary Table S-tests.")


ROB_ORDER = ["noise5", "noise15", "noise15-hist", "spikes2-hist", "missing20", "missing40", "outage3d", "shift+40",
             "shift-40", "shift+40@d7", "calpool10", "calpool25", "calpool50", "reduced-training-pool",
             "weak-forecaster"]
ROB_LAB = {"noise5": "Added noise 5 % (history and truth)", "noise15": "Added noise 15 % (history and truth)",
           "noise15-hist": "Input noise 15 % (truth clean)", "spikes2-hist": "Input spikes/zeros 2 % (truth clean)",
           "missing20": "Missing 20 % (random hours)", "missing40": "Missing 40 % (random hours)",
           "outage3d": "Outage block 3 days", "shift+40": "Level +40 % (day 28)", "shift-40": "Level −40 % (day 28)",
           "shift+40@d7": "Level +40 % (day 7)", "calpool10": "Cal. pool 10 %", "calpool25": "Cal. pool 25 %",
           "calpool50": "Cal. pool 50 %", "reduced-training-pool": "Reduced training pool (10 % of buildings)",
           "weak-forecaster": "Weak forecaster (no lag/profile features)"}
ROB_METHODS = ["HSC-CQR simple", "HSC-CQR fixed-κ", "QShrink-CQR", "Self-CQR-fb", "Self-CQR", "ACI-CQR", "TQA-B-CQR",
               "GHCP-CQR", "CQR"]


def robust_table(s, st):
    rb = s[s.exp == "robust"]
    if not len(rb):
        return
    rows = []
    for p in ROB_ORDER:
        x = rb[rb.perturb == p]
        if not len(x):
            continue
        row = {"Condition": ROB_LAB[p]}
        means = {m: x[x.method == m].macd.mean() for m in ROB_METHODS if len(x[x.method == m])}
        best = min(means, key=means.get) if means else None
        for m in ROB_METHODS:
            y = x[x.method == m]
            if not len(y):
                row[dn(m)] = "–"
                continue
            cell = f"{y.macd.mean():.3f} / {100 * y.under_rate.mean():.0f}"
            if m == best:
                cell = f"**{cell}**"
            if m != "HSC-CQR simple":
                r = st[(st.perturb == p) & (st.proposed == "HSC-CQR simple") & (st.baseline == m) &
                       (st.metric == "abs_dev")]
                if len(r):
                    r = r.iloc[0]
                    ps = r.get("p_site_holm", np.nan)
                    sig = (ps < 0.05) if pd.notna(ps) else (r.p_holm < 0.05)
                    if sig:
                        cell += "‡" if r.mean_diff > 0 else "†"
            row[dn(m)] = cell
        rows.append(row)
    _write("MS_robustness", pd.DataFrame(rows),
           "Stress tests on BDG2 (3 seeds): MACD / share of under-covered buildings (%); bold = lowest MACD per "
           "condition. † (‡): SSC-CQR significantly better (worse) on |cov − 0.9| (site sign-flip test, Holm within "
           "condition, p < 0.05). Added noise perturbs history and the evaluated truth (irreducible noise); input-only "
           "conditions perturb the observed history and the building's own scores but evaluate against clean readings. "
           "s.d. over seeds: supplementary table.")


def site_table():
    f = os.path.join(TAB, "T_sites_BDG2.csv")
    if not os.path.exists(f):
        return
    w = pd.read_csv(f, index_col=0)
    keep = [c for c in w.columns if c.startswith("under | ") or c == "n_buildings"]
    d = w[keep].copy()
    for c in keep[1:]:
        d[c] = (100 * d[c]).map(lambda x: "–" if pd.isna(x) else f"{x:.1f}")
    d.columns = ["Buildings"] + [dn(c.split(" | ")[1]) + " under (%)" for c in keep[1:]]
    d = d.reset_index().rename(columns={"site_id": "Site"})
    d["Buildings"] = d["Buildings"].map(lambda x: "" if pd.isna(x) else f"{int(x)}")
    _write("MS_sites", d, "Share of under-covered building × seed units per BDG2 site (random-building protocol, 90 %), "
                          "with the site-mean (macro) and building-weighted averages.")


def downstream_table():
    rows = []
    for ds in ["BDG2", "UCI"]:
        f = os.path.join(TAB, f"T_downstream_{ds}.csv")
        if not os.path.exists(f):
            continue
        w = pd.read_csv(f, index_col=0)
        for m, r in w.iterrows():
            rows.append({"Data": ds, "Method": dn(m), "Exceedance rate (%)": f"{100 * r.exceed_rate:.2f}",
                         "Buildings > 2× contracted (%)": f"{100 * r.share_breach_2x:.1f}",
                         "Reserved capacity (× mean load)": f"{r.reserve:.3f}",
                         "Shortfall (× mean load)": f"{r.shortfall:.4f}",
                         "Cost r=10": f"{r.cost_r10:.3f}", "Cost r=20": f"{r.cost_r20:.3f}"})
    if rows:
        _write("MS_downstream", pd.DataFrame(rows),
               "Downstream case study: each building reserves its day-ahead upper bound as import capacity (contracted "
               "exceedance probability 5 %). Exceedance rate: hours with load above the reservation; Buildings > 2× "
               "contracted: share of buildings exceeding in more than 10 % of hours; Cost = reserved capacity + r × "
               "shortfall (both per hour, relative to the building's mean load) for penalty ratios r. Means over "
               "building × seed units.")


def cost_table():
    f = os.path.join(TAB, "T_timing.csv")
    if not os.path.exists(f):
        return
    tm = pd.read_csv(f)
    tm["Method"] = tm.method.map(lambda m: m.replace("HSC-CQR simple (primary)", "SSC-CQR (primary)")
                                 .replace("HSC-CQR full", "SSC-CQR +stage+kNN"))
    d = tm[["dataset", "Method", "operation", "median_ms", "iqr_ms", "reps"]].rename(
        columns={"dataset": "Data", "operation": "Operation", "median_ms": "Median (ms; MB for store)",
                 "iqr_ms": "IQR (ms)", "reps": "Reps"})
    d["Median (ms; MB for store)"] = d["Median (ms; MB for store)"].map(lambda x: f"{x:.4g}")
    _write("MS_cost", d, "Isolated timing benchmark (seed 0; single thread; no concurrent jobs; median and interquartile "
                         "range over repetitions after warm-up). Tuning = leave-one-building-out selection on all "
                         "calibration buildings; batch = radii for all targets × 56 days divided by building-days; "
                         "incremental = adding one day of 24 scores to one building and recomputing its radius.")


def run():
    s = pd.read_csv(os.path.join(RES, "seed_level_metrics.csv"))
    s = s[~s.exp.isna()]
    st = pd.read_csv(os.path.join(RES, "statistics.csv"))
    for ds in ["BDG2", "UCI"]:
        main_table(s, ds)
        main_table(s, ds, methods=SI_METHODS + ["HSC-CQR simple", "CQR"], name=f"SI_abs_{ds}",
                   note=" Absolute-score methods (supplementary).")
    window_table()
    tests_table(st)
    ablation_table(s)
    gen_table(s)
    robust_table(s, st)
    site_table()
    downstream_table()
    cost_table()


if __name__ == "__main__":
    run()
