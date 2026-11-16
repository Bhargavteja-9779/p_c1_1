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
    for _, r in t.iterrows():
        if r.baseline in ("HSC-CQR -stage", "HSC-CQR -kNN", "HSC-CQR -shrink", "HSC-CQR simple", "SCP-stage", "ACI",
                          "Self-CP", "Mondrian-usage", "Naive+SCP", "HSC"):
            continue
        ci = ([float(x) for x in r.ci95_mean_diff.strip("[]").split(",")] if isinstance(r.ci95_mean_diff, str)
              else r.ci95_mean_diff)
        rows.append({"Data": r.dataset, "Baseline": r.baseline,
                     "Metric": "Rel. IS" if r.metric == "rel_IS" else "|cov − 0.9|",
                     "n": int(r.n_buildings), "Mean diff. [95 % CI]": f"{r.mean_diff:+.4f} [{ci[0]:+.4f}, {ci[1]:+.4f}]",
                     "HSC-CQR better (%)": f"{100 * r.share_proposed_better:.0f}",
                     "r_rb": f"{r.rank_biserial:+.2f}",
                     "p (Holm)": "<0.001" if r.p_holm < 0.001 else f"{r.p_holm:.3f}"})
    _write("MS_tests", pd.DataFrame(rows),
           "Paired per-building comparison of HSC-CQR with each baseline (random-building protocol, 90 %). Mean diff. = "
           "HSC-CQR minus baseline (negative = HSC-CQR better), averaged over buildings; 95 % CI by site-cluster bootstrap "
           "(BDG2) or building bootstrap (UCI); r_rb = matched-pairs rank-biserial correlation (positive = HSC-CQR "
           "better); p = two-sided Wilcoxon signed-rank, Holm-adjusted within dataset and metric.")


def ablation_table(s):
    rows = []
    meths = ["HSC-CQR", "HSC-CQR -stage", "HSC-CQR -kNN", "HSC-CQR simple", "HSC-CQR -shrink", "Self-CQR", "CQR",
             "HSC", "HSC -stage", "HSC -kNN", "HSC simple", "HSC -shrink", "HSC fixed-kappa", "Self-CP",
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
           "all onboarding stages; '-kNN': prior from all calibration buildings (K = all); '-shrink': prior only "
           "(κ = ∞); 'fixed-kappa': κ = 168 h instead of the leave-one-building-out choice; Self-*: κ = 0 with "
           "fallback to the pooled quantile. Every variant is re-tuned on calibration buildings.")


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
    info = json.load(open(os.path.join(RES, "run_info.json")))
    rows = []
    for d in ["BDG2", "UCI"]:
        parts = [k for k in info if k.startswith(f"main_{d}_s") and k.endswith("a0.1")]
        if not parts:
            continue
        g = lambda key: np.mean([info[k][key] for k in parts if info[k].get(key) is not None])  # noqa: E731
        rows.append({"Data": d, "Training rows (M)": f"{g('n_train_rows') / 1e6:.2f}",
                     "LightGBM training, 3 models (s)": f"{g('lgb'):.0f}",
                     "MLP training, 2 models (s)": f"{g('mlp'):.0f}",
                     "LightGBM inference (ms / building-day)": f"{1e3 * g('pred_lgb_per_target_day'):.3f}",
                     "HSC tuning, LOBO (s)": f"{g('t_tune_hsc'):.1f}",
                     "HSC update (ms / building-day)": f"{1e3 * g('t_hsc_apply_per_target_day'):.3f}",
                     "HSC store (MB)": f"{g('hsc_store_MB'):.1f}"})
    _write("MS_cost", pd.DataFrame(rows),
           "Computational cost on a 4-core CPU (mean over 5 seeds). HSC tuning = leave-one-building-out grid search "
           "over (κ, K) on all calibration buildings; HSC update = computing one building's radius for one day "
           "(including neighbour search) once its scores are stored.")


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


if __name__ == "__main__":
    run()
