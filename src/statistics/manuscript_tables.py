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

MAIN_METHODS = ["HSC-CQR", "HSC-CQR simple", "Self-CQR", "ACI-CQR", "TQA-B-CQR", "QShrink-CQR", "GHCP-CQR", "CQR",
                "QR-LGBM", "MLP-QR", "MLP-Gauss", "HSC-CQR (MLP)", "CQR (MLP)", "HSC", "HSC simple", "ACI", "Self-CP",
                "SCP-stage", "SCP", "Mondrian-usage", "Naive+SCP", "Raw-SCP"]
KEY = ["HSC-CQR", "HSC-CQR simple", "ACI-CQR", "Self-CQR", "TQA-B-CQR", "QShrink-CQR", "GHCP-CQR", "CQR", "QR-LGBM",
       "MLP-QR", "HSC", "ACI", "SCP-stage"]


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


def main_table(s, ds, quick=False):
    t = s[(s.exp == "main") & (s.dataset == ds) & (s.alpha == 0.1) & (s.perturb == "none")]
    g = t.groupby("method")
    rows = []
    for m in MAIN_METHODS:
        if m not in g.groups:
            continue
        x = g.get_group(m)
        rows.append({"Method": m,
                     "Coverage": _pm(x.mean_cov.mean(), x.mean_cov.std()),
                     "Coverage wk 1": _pm(x.cov_early.mean(), x.cov_early.std()),
                     "MACD": _pm(x.macd.mean(), x.macd.std()),
                     "Under-cov. (%)": _pm(x.under_rate.mean(), x.under_rate.std(), pct=True),
                     "P10 cov.": _pm(x.p10_cov.mean(), x.p10_cov.std()),
                     "Rel. width": _pm(x.rel_width.mean(), x.rel_width.std()),
                     "Rel. IS": _pm(x.rel_IS.mean(), x.rel_IS.std())})
    n_b = int(t[t.method == "HSC-CQR"].n.mean()) if len(t) else 0
    _write(f"MS_main_{ds}", pd.DataFrame(rows),
           f"Per-building interval reliability and sharpness on {ds} (random-building protocol, nominal 90 %, "
           f"{t.seed.nunique()} seeds, ≈{n_b} target buildings per seed). Coverage: mean per-building coverage over the "
           f"56-day onboarding window; wk 1: first 7 forecast days; MACD: mean |coverage − 0.90|; Under-cov.: share of "
           f"buildings with coverage < 0.85; P10: 10th percentile of per-building coverage; Rel. width and Rel. IS: "
           f"medians over buildings of width and interval score divided by the building's mean load. Mean ± s.d. over seeds.")


def tests_table(st):
    rows = []
    t = st[(st.perturb == "none") & (st.alpha == 0.1) & (st.proposed == "HSC-CQR") & (st.protocol == "random")]
    keep = ["CQR", "QShrink-CQR", "Self-CQR", "ACI-CQR", "TQA-B-CQR", "GHCP-CQR", "QR-LGBM", "MLP-QR", "MLP-Gauss",
            "HSC-CQR fixed-κ"]
    for ds in ["BDG2", "UCI"]:
        for bl in keep:
            for metric, lab in [("abs_dev", "CD"), ("rel_IS", "IS")]:
                r = t[(t.dataset == ds) & (t.baseline == bl) & (t.metric == metric)]
                if not len(r):
                    continue
                r = r.iloc[0]
                ci = ([float(x) for x in r.ci95_mean_diff.strip("[]").split(",")] if isinstance(r.ci95_mean_diff, str)
                      else r.ci95_mean_diff)
                rows.append({"Data": ds, "Baseline": bl, "Metric": lab, "n": int(r.n_buildings),
                             "Mean diff.": f"{r.mean_diff:+.4f}", "95 % CI": f"[{ci[0]:+.4f}, {ci[1]:+.4f}]",
                             "Better (%)": f"{100 * r.share_proposed_better:.0f}",
                             "r_rb": f"{r.rank_biserial:+.2f}",
                             "p (Holm)": "<0.001" if r.p_holm < 0.001 else f"{r.p_holm:.3f}"})
    _write("MS_tests", pd.DataFrame(rows),
           "Paired per-building comparison of HSC-CQR with each baseline (random-building protocol, nominal 90 %). "
           "CD = absolute coverage deviation |cov_b − 0.9|; IS = relative interval score. Mean diff. = HSC-CQR minus "
           "baseline, averaged over buildings (negative = HSC-CQR better); 95 % CI by site-cluster bootstrap (BDG2) or "
           "building bootstrap (UCI); Better = share of buildings for which HSC-CQR is better; r_rb = matched-pairs "
           "rank-biserial correlation (positive = HSC-CQR better); p = two-sided Wilcoxon signed-rank, Holm-adjusted "
           "within dataset and metric.")


def ablation_table(s):
    rows = []
    meths = ["HSC-CQR", "HSC-CQR -stage", "HSC-CQR -kNN", "HSC-CQR simple", "HSC-CQR fixed-κ", "HSC-CQR -shrink",
             "Self-CQR", "CQR",
             "HSC", "HSC -stage", "HSC -kNN", "HSC simple", "HSC -shrink", "Self-CP",
             "SCP-stage"]
    for m in meths:
        row = {"Variant": m}
        for ds in ["BDG2", "UCI"]:
            x = s[(s.exp == "main") & (s.dataset == ds) & (s.alpha == 0.1) & (s.perturb == "none") & (s.method == m)]
            if not len(x):
                continue
            row[f"{ds} MACD"] = _pm(x.macd.mean(), x.macd.std())
            row[f"{ds} Under (%)"] = _pm(x.under_rate.mean(), x.under_rate.std(), pct=True)
            row[f"{ds} Rel. IS"] = _pm(x.rel_IS.mean(), x.rel_IS.std())
        rows.append(row)
    _write("MS_ablation", pd.DataFrame(rows),
           "Component ablation (random-building protocol, 90 %, mean ± s.d. over 5 seeds). '-stage': prior pooled over "
           "all onboarding stages; '-kNN': prior from all calibration buildings (K = all); 'simple': both removed; "
           "'-shrink': prior only (κ = ∞); 'fixed-κ': simple variant with κ = 168 h (one week) instead of the "
           "leave-one-building-out choice (a donor–local mixture with fixed pseudo-count); Self-*: κ = 0 with "
           "fallback to the pooled quantile. Except for fixed-κ, every variant is re-tuned on calibration buildings "
           "with the component removed.")


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
        for m in ["HSC-CQR", "HSC-CQR simple", "ACI-CQR", "Self-CQR", "TQA-B-CQR", "QShrink-CQR", "GHCP-CQR", "CQR",
                  "MLP-QR"]:
            y = x[x.method == m]
            if not len(y):
                continue
            rows.append({"Setting": lab, "Runs": y.seed.nunique(), "Method": m,
                         "Coverage": _pm(y.mean_cov.mean(), y.mean_cov.std()),
                         "MACD": _pm(y.macd.mean(), y.macd.std()),
                         "Under-cov. (%)": _pm(y.under_rate.mean(), y.under_rate.std(), pct=True),
                         "Rel. IS": _pm(y.rel_IS.mean(), y.rel_IS.std())})
    _write("MS_generalisation", pd.DataFrame(rows),
           "Generalisation to unseen sites (BDG2 leave-site-out, 5 folds) and across datasets/countries (models and "
           "calibration scores from the source dataset, no weather features; 3 seeds). The BDG2→BDG2 (no wx) rows "
           "are the within-dataset reference without weather features.")


def robust_table(s):
    rb = s[s.exp == "robust"]
    if not len(rb):
        return
    order = ["noise5", "noise15", "missing20", "missing40", "shift+40", "shift-40", "calpool10", "calpool25",
             "calpool50", "weak-forecaster"]
    lab = {"noise5": "Meter noise 5 %", "noise15": "Meter noise 15 %", "missing20": "Missing 20 %",
           "missing40": "Missing 40 %", "shift+40": "Level +40 % (day 28)", "shift-40": "Level −40 % (day 28)",
           "calpool10": "Cal. pool 10 %", "calpool25": "Cal. pool 25 %", "calpool50": "Cal. pool 50 %",
           "weak-forecaster": "Weak forecaster (10 % training buildings)"}
    rows = []
    for p in order:
        x = rb[rb.perturb == p]
        if not len(x):
            continue
        row = {"Condition": lab[p]}
        for m in ["HSC-CQR", "HSC-CQR simple", "ACI-CQR", "Self-CQR", "TQA-B-CQR", "QShrink-CQR", "GHCP-CQR", "CQR",
                  "MLP-QR"]:
            y = x[x.method == m]
            row[m] = "–" if not len(y) else f"{y.macd.mean():.3f} / {100 * y.under_rate.mean():.0f}"
        rows.append(row)
    _write("MS_robustness", pd.DataFrame(rows),
           "Stress tests on BDG2 (3 seeds): MACD / share of under-covered buildings (%). Noise, missing data and level "
           "shifts are applied to the target buildings' onboarding windows (history and truth); calibration-pool "
           "conditions keep a random fraction of calibration buildings; the weak forecaster is trained on 10 % of the "
           "training buildings (no MLP baselines, '–').")


def cost_table():
    """Cycle 2 (R7): isolated benchmark only (results/timing.json; scripts/timing_benchmark.py)."""
    f = os.path.join(RES, "timing.json")
    if not os.path.exists(f):
        return
    tm = json.load(open(f))
    rows = []
    q = lambda x: f"{x['median']:.3g} [{x['q25']:.3g}, {x['q75']:.3g}]"  # noqa: E731
    for d in ["BDG2", "UCI"]:
        if d not in tm or "online_step_ms_recency" not in tm[d]:
            continue
        r = tm[d]
        rows.append({"Data": d, "Calibration / target buildings": f"{r['n_cal']} / {r['n_targets']}",
                     "LightGBM training, 3 models (s; seed 0, 4 threads)": f"{r['lgb_3models_train_s_seed0']:.0f}",
                     "LightGBM inference (ms / building-day)": q(r["lgb_inference_ms_per_building_day"]),
                     "Layer tuning, LOBO (s)": q(r["recency_tune_s"]),
                     "Layer online step (ms / building-day)": q(r["online_step_ms_recency"]),
                     "Tuning store (MB)": f"{r['memory_MB']['tuning_counts']:.0f}",
                     "State per building (KB)": f"{1e3 * r['memory_MB']['per_building_state']:.0f}"})
    if rows:
        _write("MS_cost", pd.DataFrame(rows),
               f"Computational cost, isolated benchmark ({tm.get('cpu', '')}, calibration single-threaded); median "
               "[IQR] over repetitions and 5 seeds. Online step = binning one day's 24 scores into the building's "
               "decayed count state and computing its radius; deployment needs one prior vector and one state "
               "vector per building (16 KB each).")


# ---------------------------------------------------------------- revision (cycle 1): compact main tables
def primary():
    f = os.path.join(RES, "recommended.json")
    return json.load(open(f))["recommended"] if os.path.exists(f) else "HSC-CQR"


def _main_methods():
    p = primary()
    rest = ["HSC-CQR recency", "HSC-SSC-CQR", "SSC-CQR", "HSC-CQR simple (cov)", "HSC-CQR", "QShrink-CQR (cov)",
            "QShrink-CQR", "Self-CQR", "ACI-CQR", "ACI-CQR (cov)", "TQA-B-CQR", "GHCP-CQR", "CQR", "MLP-QR", "MLP-Gauss"]
    return [p] + [m for m in rest if m != p]


def ms_main_combined(s):
    rows = []
    for ds in ["BDG2", "UCI"]:
        t = s[(s.exp == "main") & (s.dataset == ds) & (s.alpha == 0.1) & (s.perturb == "none")]
        for m in _main_methods():
            x = t[t.method == m]
            if not len(x):
                continue
            rows.append({"Data": ds, "Method": m,
                         "Coverage": _pm(x.mean_cov.mean(), x.mean_cov.std()),
                         "Under-cov. (%)": _pm(x.under_rate.mean(), x.under_rate.std(), pct=True),
                         "Under-cov. wk 1 (%)": _pm(x.under_wk1.mean(), x.under_wk1.std(), pct=True),
                         "P10 cov.": _pm(x.p10_cov.mean(), x.p10_cov.std()),
                         "Under-prot. (%)": (_pm(x.underprot.mean(), x.underprot.std(), pct=True)
                                             if "underprot" in x else "–"),
                         "Rel. IS": _pm(x.rel_IS.mean(), x.rel_IS.std())})
    _write("MS2_main", pd.DataFrame(rows),
           "Per-building reliability and sharpness of the calibration strategies (random-building protocol, nominal "
           "90 %, 5 seeds; all strategies except MLP-QR/MLP-Gauss use the same LightGBM quantile models and CQR "
           "scores). Coverage: mean per-building coverage over the 56-day onboarding window; Under-cov.: share of "
           "buildings with coverage < 0.85 (over the window and in the first week); P10: 10th percentile of "
           "per-building coverage; Under-prot.: share of buildings whose upper bound is exceeded in more than 10 % of "
           "hours (nominal 5 %); Rel. IS: median over buildings of the interval score divided by the building's mean "
           "load. Mean ± s.d. over seeds. '(cov)': parameter selected with the per-building coverage objective.")


def ms_tests_primary(st):
    p = primary()
    t = st[(st.perturb == "none") & (st.alpha == 0.1) & (st.proposed == p) & (st.protocol == "random")]
    rows = []
    for ds in ["BDG2", "UCI"]:
        for bl in ["CQR", "QShrink-CQR (cov)", "ACI-CQR", "ACI-CQR (cov)", "Self-CQR", "HSC-CQR fixed-κ",
                   "HSC-CQR simple (cov)", "HSC-CQR", "HSC-SSC-CQR", "HSC-CQR recency", "GHCP-CQR", "TQA-B-CQR"]:
            if bl == p:
                continue
            for metric, lab in [("abs_dev", "CD"), ("abs_dev_early", "CD wk 1"), ("rel_IS", "IS")]:
                r = t[(t.dataset == ds) & (t.baseline == bl) & (t.metric == metric)]
                if not len(r):
                    continue
                r = r.iloc[0]
                ps = r.get("p_site", np.nan)
                rows.append({"Data": ds, "Baseline": bl, "Metric": lab, "n": int(r.n_buildings),
                             "Mean diff.": f"{r.mean_diff:+.4f}", "Better (%)": f"{100 * r.share_proposed_better:.0f}",
                             "r_rb": f"{r.rank_biserial:+.2f}",
                             "p (Holm)": "<0.001" if r.p_holm < 0.001 else f"{r.p_holm:.3f}",
                             "p (sites)": "–" if pd.isna(ps) else ("<0.001" if ps < 0.001 else f"{ps:.3f}")})
    _write("MS2_tests", pd.DataFrame(rows),
           f"Paired per-building comparison of {p} with the strongest alternatives (random-building protocol, 90 %). "
           "CD = |cov_b − 0.9| over the window; CD wk 1 = the same for the first week; IS = relative interval score. "
           f"Mean diff. = {p} minus baseline (negative = {p} better); Better = share of buildings for which {p} is "
           "better; r_rb = matched-pairs rank-biserial correlation (positive = better); p (Holm) = two-sided Wilcoxon "
           "signed-rank over buildings, Holm-adjusted within dataset, metric and family; p (sites) = Wilcoxon on "
           "site-mean differences (BDG2, 10 sites; unadjusted; '–' for UCI, a single site).")


def ms_operational(s):
    rows = []
    for ds in ["BDG2", "UCI"]:
        t = s[(s.exp == "main") & (s.dataset == ds) & (s.alpha == 0.1) & (s.perturb == "none")]
        if "cost20" not in t:
            return
        base = t[t.method == "CQR"].groupby("seed")[["cost10", "cost20", "cost40"]].mean()
        for m in _main_methods():
            x = t[t.method == m]
            if not len(x):
                continue
            xs = x.groupby("seed")[["cost10", "cost20", "cost40", "underprot", "up_exc"]].mean()
            row = {"Data": ds, "Method": m,
                   "Upper exceed. (%)": _pm(xs.up_exc.mean(), xs.up_exc.std(), pct=True),
                   "Under-prot. (%)": _pm(xs.underprot.mean(), xs.underprot.std(), pct=True)}
            for r in [10, 20, 40]:
                d = 100 * (xs[f"cost{r}"] / base[f"cost{r}"] - 1)
                row[f"Cost Δ ρ={r} (%)"] = f"{d.mean():+.1f} ± {d.std():.1f}"
            rows.append(row)
    _write("MS2_operational", pd.DataFrame(rows),
           "Operational consequence: day-ahead capacity-headroom offers planned on the upper bound (Eq. 9). Upper "
           "exceed.: mean share of hours above the upper bound (nominal 5 %); Under-prot.: share of buildings with "
           "more than 10 % exceedance; Cost Δ: change of the mean relative cost (planning load + ρ × violation) versus "
           "pooled CQR for penalty ratios ρ (ρ = 20 is cost-optimal for a calibrated 95 % upper bound); mean ± s.d. "
           "over seeds.")


def ms_robgen(s):
    """Under-covered share (%) of the key strategies under every stress and transfer condition (mean over runs)."""
    meths = [primary(), "QShrink-CQR (cov)", "HSC-CQR simple (cov)", "ACI-CQR", "Self-CQR", "CQR", "MLP-QR"]
    conds = [("robust", "noise5", "BDG2", None, "Meter noise 5 %"), ("robust", "noise15", "BDG2", None, "Meter noise 15 %"),
             ("robust", "missing20", "BDG2", None, "Missing hours 20 %"), ("robust", "missing40", "BDG2", None, "Missing hours 40 %"),
             ("robust", "shift+40", "BDG2", None, "Level shift +40 % (day 28)"),
             ("robust", "shift-40", "BDG2", None, "Level shift −40 % (day 28)"),
             ("robust", "calpool10", "BDG2", None, "Calibration pool 10 %"),
             ("robust", "calpool25", "BDG2", None, "Calibration pool 25 %"),
             ("robust", "weak-forecaster", "BDG2", None, "Weak forecaster"),
             ("lso", "none", "BDG2", "leave-site-out", "Unseen sites (BDG2, 5 folds)"),
             ("xds", "none", "BDG2", "BDG2->BDG2 (no weather)", "BDG2 → BDG2, no weather"),
             ("xds", "none", "UCI", "BDG2->UCI (no weather)", "BDG2 → UCI (Portugal)"),
             ("xds", "none", "BDG2", "UCI->BDG2 (no weather)", "UCI → BDG2")]
    rows = []
    for e, p_, ds, prot, lab in conds:
        q = (s.exp == e) & (s.perturb == p_) & (s.dataset == ds) & (s.alpha == 0.1)
        if prot:
            q &= s.protocol == prot
        x = s[q]
        if not len(x):
            continue
        row = {"Condition": lab, "Runs": int(x.seed.nunique())}
        for m in meths:
            y = x[x.method == m]
            row[m] = "–" if not len(y) else f"{100 * y.under_rate.mean():.1f}"
        y = x[x.method == primary()]
        row["Δ rel. IS vs CQR (%)"] = "–"
        c = x[x.method == "CQR"]
        if len(y) and len(c):
            row["Δ rel. IS vs CQR (%)"] = f"{100 * (y.rel_IS.mean() / c.rel_IS.mean() - 1):+.1f}"
        rows.append(row)
    _write("MS2_robgen", pd.DataFrame(rows),
           f"Robustness and generalisation: share of under-covered buildings (%, coverage < 0.85 over the 56-day window), "
           f"mean over runs (stress tests: 3 seeds on BDG2; unseen sites: 5 folds; cross-dataset: 3 seeds, no weather "
           f"features). Last column: change of the median relative interval score of {primary()} versus pooled CQR. "
           "MLP-QR is not available for the weak-forecaster condition ('–').")


def run():
    s = pd.read_csv(os.path.join(RES, "seed_level_metrics.csv"))
    s = s[~s.exp.isna()]
    st = pd.read_csv(os.path.join(RES, "statistics.csv"))
    for ds in ["BDG2", "UCI"]:
        main_table(s, ds)
    tests_table(st)
    ablation_table(s)
    gen_table(s)
    robust_table(s)
    cost_table()
    if (s.method == "HSC-CQR recency").any():
        ms_main_combined(s)
        ms_tests_primary(st)
        ms_operational(s)
        ms_robgen(s)


if __name__ == "__main__":
    run()
