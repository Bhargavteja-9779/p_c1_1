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

from src.statistics.names import disp

PRIMARY = "HSC-CQR cov-κ"
# compact main table (revision 1: <= ~12 rows; full tables T_main_*.md go to the Supplementary Material)
MAIN_METHODS = ["HSC-CQR cov-κ", "HSC-CQR fixed-κ", "HSC-CQR simple", "Self-CQR", "Switch-CQR", "QShrink-CQR",
                "QShrink-CQR fixed-λ", "ACI-CQR clip", "GHCP-CQR", "TQA-B-CQR", "Mondrian-site CQR", "CQR", "QR-LGBM",
                "MLP-QR", "SCP-stage"]
KEY = ["HSC-CQR cov-κ", "HSC-CQR fixed-κ", "Self-CQR", "Switch-CQR", "QShrink-CQR", "ACI-CQR clip", "CQR"]
FULL_METHODS = MAIN_METHODS + ["ACI-CQR", "HSC-CQR", "MLP-Gauss", "HSC-CQR (MLP)", "CQR (MLP)", "HSC", "HSC simple",
                               "ACI", "Self-CP", "SCP", "Mondrian-usage", "Naive+SCP", "Raw-SCP"]


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


def main_table(s, ds, methods=None, name=None):
    t = s[(s.exp == "main") & (s.dataset == ds) & (s.alpha == 0.1) & (s.perturb == "none")]
    g = t.groupby("method")
    rows = []
    for m in (methods or FULL_METHODS):
        if m not in g.groups:
            continue
        x = g.get_group(m)
        rows.append({"Method": disp(m),
                     "Coverage": _pm(x.mean_cov.mean(), x.mean_cov.std()),
                     "MACD": _pm(x.macd.mean(), x.macd.std()),
                     "MACD wk 1": _pm(x.macd_early.mean(), x.macd_early.std()),
                     "Under-cov. (%)": _pm(x.under_rate.mean(), x.under_rate.std(), pct=True),
                     "Under-cov. wk 1 (%)": _pm(x.under_early.mean(), x.under_early.std(), pct=True),
                     "P10 cov.": _pm(x.p10_cov.mean(), x.p10_cov.std()),
                     "Rel. width": _pm(x.rel_width.mean(), x.rel_width.std()),
                     "Rel. IS": _pm(x.rel_IS.mean(), x.rel_IS.std())})
    n_b = int(t[t.method == PRIMARY].n.mean()) if len(t) and (t.method == PRIMARY).any() else 0
    _write(name or f"MS_main_{ds}", pd.DataFrame(rows),
           f"Per-building interval reliability and sharpness on {ds} (random-building protocol, out-of-time "
           f"calibration, nominal 90 %, {t.seed.nunique()} seeds, ≈{n_b} target buildings per seed). Coverage: mean "
           f"per-building coverage over the 56-day onboarding window; MACD: mean |coverage − 0.90| over buildings; "
           f"wk 1: first 7 forecast days only; Under-cov.: share of buildings with coverage < 0.85; P10: 10th "
           f"percentile of per-building coverage; Rel. width and Rel. IS: medians over buildings of width and "
           f"interval score divided by the building's mean load. Mean ± s.d. over seeds.")


def _ci(c):
    if isinstance(c, str):
        c = [float(x) for x in c.strip("[]").split(",")]
    return c


def tests_table(st, family="primary", name="MS_tests", proposed=PRIMARY):
    rows = []
    t = st[(st.perturb == "none") & (st.alpha == 0.1) & (st.proposed == proposed) & (st.protocol == "random") &
           (st.family == family)]
    for ds in ["BDG2", "UCI"]:
        for bl in t[t.dataset == ds].baseline.unique():
            for metric, lab in [("abs_dev", "CD"), ("rel_IS", "IS")]:
                r = t[(t.dataset == ds) & (t.baseline == bl) & (t.metric == metric)]
                if not len(r):
                    continue
                r = r.iloc[0]
                ci = _ci(r.ci95_hl)
                site = "" if ds != "BDG2" or pd.isna(r.p_site_sign) else \
                    f"{int(r.sites_proposed_better)}/{int(r.n_sites)} (p={r.p_site_sign:.3f})"
                rows.append({"Data": ds, "Comparator": disp(bl), "Metric": lab, "n": int(r.n_buildings),
                             "HL diff.": f"{r.hl_diff:+.4f}",
                             "95 % CI": f"[{ci[0]:+.4f}, {ci[1]:+.4f}]" if np.isfinite(ci[0]) else "–",
                             "Better (%)": f"{100 * r.share_proposed_better:.0f}",
                             "r_rb": f"{r.rank_biserial:+.2f}",
                             "p (Holm)": "<0.001" if r.p_holm < 0.001 else f"{r.p_holm:.3f}",
                             "Sites better": site})
    _write(name, pd.DataFrame(rows),
           f"Paired per-building comparison of {disp(proposed)} with each comparator ({family} family of "
           "Amendment 1; random-building protocol, nominal 90 %). CD = |cov_b − 0.9|; IS = relative interval score. "
           "HL diff. = Hodges–Lehmann estimate of the paired difference (proposed minus comparator; negative = "
           f"{disp(proposed)} better) with 95 % CI by site-cluster bootstrap (BDG2, 11 sites) or building bootstrap "
           "(UCI); Better = share of buildings for which the proposed method is better; r_rb = matched-pairs "
           "rank-biserial correlation (positive = proposed better); p = two-sided Wilcoxon signed-rank test, "
           "Holm-adjusted within dataset × metric of this family; Sites better = sites whose mean difference favours "
           "the proposed method, with a two-sided sign test over sites (cluster-level check).")


def ablation_table(s):
    rows = []
    meths = ["HSC-CQR cov-κ", "HSC-CQR fixed-κ", "HSC-CQR simple", "HSC-CQR -kNN", "HSC-CQR -stage", "HSC-CQR",
             "HSC-CQR -shrink", "Self-CQR", "Switch-CQR", "CQR", "HSC simple", "HSC", "Self-CP", "SCP-stage"]
    for m in meths:
        row = {"Variant": disp(m)}
        for ds in ["BDG2", "UCI"]:
            x = s[(s.exp == "main") & (s.dataset == ds) & (s.alpha == 0.1) & (s.perturb == "none") & (s.method == m)]
            if not len(x):
                continue
            row[f"{ds} MACD"] = _pm(x.macd.mean(), x.macd.std())
            row[f"{ds} MACD wk 1"] = _pm(x.macd_early.mean(), x.macd_early.std())
            row[f"{ds} Under (%)"] = _pm(x.under_rate.mean(), x.under_rate.std(), pct=True)
            row[f"{ds} Rel. IS"] = _pm(x.rel_IS.mean(), x.rel_IS.std())
        rows.append(row)
    _write("MS_ablation", pd.DataFrame(rows),
           "Variants of the pseudo-count mixture (random-building protocol, 90 %, mean ± s.d. over 5 seeds). κ by "
           "LOBO-CD (primary) or LOBO-IS: pseudo-count chosen on calibration buildings by leave-one-building-out "
           "coverage deviation or interval score; '+ stage': prior restricted to the same onboarding-stage bin; "
           "'+ kNN': prior from the K most similar calibration buildings (K tuned); κ = ∞: prior only; Self-CQR: κ = 0 "
           "with pooled fallback; Switch-CQR: pooled CQR for the first n* days, then Self-CQR (n* by LOBO); PCM-abs: "
           "the same layer on absolute-residual scores of the LightGBM point forecast.")


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
        for m in KEY:
            y = x[x.method == m]
            if not len(y):
                continue
            rows.append({"Setting": lab, "Runs": y.seed.nunique(), "Method": disp(m),
                         "Coverage": _pm(y.mean_cov.mean(), y.mean_cov.std()),
                         "MACD": _pm(y.macd.mean(), y.macd.std()),
                         "Under-cov. (%)": _pm(y.under_rate.mean(), y.under_rate.std(), pct=True),
                         "Rel. IS": _pm(y.rel_IS.mean(), y.rel_IS.std())})
    _write("MS_generalisation", pd.DataFrame(rows),
           "Generalisation to unseen sites (BDG2 leave-site-out, 5 folds) and across datasets/countries (models and "
           "calibration scores from the source dataset, no weather features; 3 seeds). The BDG2→BDG2 (no wx) rows "
           "are the within-dataset reference without weather features. Mean ± s.d. over runs; per-site "
           "leave-site-out results in Supplementary Table S-site.")


def robust_table(s):
    rb = s[s.exp == "robust"]
    if not len(rb):
        return
    lab = {"noise5": "Meter noise 5 %", "noise15": "Meter noise 15 %",
           "noise15 (cal+target)": "Meter noise 15 % (cal. + target)", "missing20": "Missing 20 %",
           "missing40": "Missing 40 %", "outage 3d@d10": "Outage 3 days (day 10)",
           "shift+40": "Level +40 % (day 28)", "shift-40": "Level −40 % (day 28)",
           "shift+40@d5": "Level +40 % (day 5)", "vol x2@d28": "Volatility ×2 (day 28)",
           "temp-forecast error 2°C": "Temperature-forecast error 2 °C",
           "calpool10": "Cal. pool 10 %", "calpool25": "Cal. pool 25 %", "calpool50": "Cal. pool 50 %",
           "weak-forecaster": "Weak forecaster (10 % training buildings)"}
    rows = []
    for ds in ["BDG2", "UCI"]:
        for p in lab:
            x = rb[(rb.perturb == p) & (rb.dataset == ds)]
            if not len(x):
                continue
            row = {"Data": ds, "Condition": lab[p]}
            for m in KEY:
                y = x[x.method == m]
                row[disp(m)] = "–" if not len(y) else f"{y.macd.mean():.3f} / {100 * y.under_rate.mean():.0f}"
            rows.append(row)
    _write("MS_robustness", pd.DataFrame(rows),
           "Stress tests (3 seeds per dataset): MACD / share of under-covered buildings (%). Unless stated otherwise, "
           "perturbations are applied to the target buildings' onboarding windows (history and truth); '(cal. + "
           "target)' perturbs the calibration windows as well; the temperature-forecast error is AR(1) noise "
           "(s.d. 2 °C, lag-1 correlation 0.8 per hour) on the temperature input of all calibration and target "
           "windows; calibration-pool conditions keep a random fraction of calibration buildings; the weak "
           "forecaster is trained on 10 % of the training buildings. Paired tests per condition: Supplementary "
           "Table S-robust.")


def robust_tests_table(st):
    t = st[(st.family == "exploratory") & (st.proposed == PRIMARY) & (st.metric == "abs_dev") &
           (st.protocol == "random") & (st.perturb != "none")]
    rows = []
    for (ds, p), g in t.groupby(["dataset", "perturb"]):
        for _, r in g.iterrows():
            rows.append({"Data": ds, "Condition": p, "Comparator": disp(r.baseline), "n": int(r.n_buildings),
                         "HL diff. CD": f"{r.hl_diff:+.4f}", "Better (%)": f"{100 * r.share_proposed_better:.0f}",
                         "r_rb": f"{r.rank_biserial:+.2f}",
                         "p (Holm)": "<0.001" if r.p_holm < 0.001 else f"{r.p_holm:.3f}"})
    _write("MS_robust_tests", pd.DataFrame(rows),
           f"Paired tests of {disp(PRIMARY)} against each comparator per stress condition (coverage deviation; "
           "exploratory, Holm within condition).")


def cost_table():
    """Training cost from run_info (single 4-thread training process, nothing else running); calibration cost
    from the isolated single-thread benchmark (src/statistics/timing.py -> tables/T_timing.csv)."""
    info = json.load(open(os.path.join(RES, "run_info.json")))
    tp = os.path.join(TAB, "T_timing.csv")
    tim = pd.read_csv(tp) if os.path.exists(tp) else None
    rows = []
    for d in ["BDG2", "UCI"]:
        parts = [k for k in info if k.startswith(f"main_{d}_s") and k.endswith("a0.1")]
        if not parts:
            continue
        v = lambda key: [info[k][key] for k in parts if info[k].get(key) is not None]  # noqa: E731
        med = lambda key: f"{np.median(v(key)):.0f} [{np.min(v(key)):.0f}–{np.max(v(key)):.0f}]"  # noqa: E731
        row = {"Data": d, "Training rows (M)": f"{np.mean(v('n_train_rows')) / 1e6:.2f}",
               "LightGBM training, 3 models (s)": med("lgb"), "MLP training, 2 models (s)": med("mlp"),
               "LightGBM inference (ms / building-day)": f"{1e3 * np.median(v('pred_lgb_per_target_day')):.3f}"}
        if tim is not None:
            for step, lab, f in [("LOBO tuning", "PCM tuning, LOBO (s)", "{:.1f}"),
                                 ("single-building daily update", "PCM daily update, one building (ms)", "{:.3f}"),
                                 ("online state", "PCM state per building (kB)", "{:.0f}")]:
                r = tim[(tim.dataset == d) & tim.step.str.startswith(step)]
                if len(r):
                    r = r.iloc[0]
                    row[lab] = f.format(r.median_s) + ("" if pd.isna(r.q25_s) else
                                                       f" [{f.format(r.q25_s)}–{f.format(r.q75_s)}]")
        rows.append(row)
    _write("MS_cost", pd.DataFrame(rows),
           "Computational cost. Training: one process with 4 CPU threads, median [range] over 5 seeds. PCM: isolated "
           "single-thread benchmark on cached scores (median [IQR] over repetitions); the daily update bins a "
           "building's 24 new scores into its count vector, mixes it with the pooled prior and searches the "
           "quantile; the state is one 4,000-bin count vector per building.")


def run():
    s = pd.read_csv(os.path.join(RES, "seed_level_metrics.csv"))
    s = s[~s.exp.isna()]
    st = pd.read_csv(os.path.join(RES, "statistics.csv"))
    for ds in ["BDG2", "UCI"]:
        main_table(s, ds, MAIN_METHODS)
        main_table(s, ds, FULL_METHODS, name=f"MS_main_full_{ds}")
    tests_table(st)
    tests_table(st, family="secondary", name="MS_tests_variants")
    ablation_table(s)
    gen_table(s)
    robust_table(s)
    robust_tests_table(st)
    cost_table()


if __name__ == "__main__":
    run()
