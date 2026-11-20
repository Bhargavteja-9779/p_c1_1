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

MAIN_METHODS = ["PCS-CQR", "PCS-CQR κ=168", "HSC-CQR", "QShrink-CQR (MACD)", "QShrink-CQR", "Self-CQR", "ACI-CQR",
                "ACI-CQR (MACD)", "ACI-CQR (coverage only)", "TQA-B-CQR", "GHCP-CQR", "CQR", "QR-LGBM", "MLP-QR",
                "MLP-Gauss", "PCS-CQR (MLP)", "CQR (MLP)"]
FULL_METHODS = MAIN_METHODS + ["PCS-CQR (IS-tuned)", "PCS-CQR site-grouped", "PCS", "HSC", "ACI", "Self-CP",
                               "SCP-stage", "SCP", "Mondrian-usage", "Naive+SCP", "Raw-SCP"]
COND_METHODS = ["PCS-CQR", "PCS-CQR κ=168", "HSC-CQR", "QShrink-CQR (MACD)", "Self-CQR", "ACI-CQR", "TQA-B-CQR",
                "GHCP-CQR", "CQR"]
LAB = {"HSC-CQR": "HSC-CQR (pre-reg.)"}


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


def _sel(s, exp, ds, prot, perturb="none", alpha=0.1):
    return s[(s.exp == exp) & (s.dataset == ds) & (s.protocol == prot) & (s.alpha == alpha) & (s.perturb == perturb)]


def main_table(s, ds, methods=MAIN_METHODS, name=None, alpha=0.1):
    t = _sel(s, "main", ds, "random", alpha=alpha)
    g = t.groupby("method")
    rows = []
    for m in methods:
        if m not in g.groups:
            continue
        x = g.get_group(m)
        rows.append({"Method": LAB.get(m, m),
                     "Coverage": _pm(x.mean_cov.mean(), x.mean_cov.std()),
                     "MACD": _pm(x.macd.mean(), x.macd.std()),
                     "Under-cov. (%)": _pm(x.under_rate.mean(), x.under_rate.std(), pct=True),
                     "Under-cov. wk 1 (%)": _pm(x.under_w1.mean(), x.under_w1.std(), pct=True),
                     "P10 cov.": _pm(x.p10_cov.mean(), x.p10_cov.std()),
                     "Rel. width": _pm(x.rel_width.mean(), x.rel_width.std()),
                     "Rel. IS": _pm(x.rel_IS.mean(), x.rel_IS.std()),
                     "Booking failures (%)": _pm(x.book_fail.mean(), x.book_fail.std(), pct=True),
                     "Reserve cost (%)": _pm(x.reserve_cost.mean(), x.reserve_cost.std(), d=2, pct=True)})
    n_b = int(t[t.method == "PCS-CQR"].n.mean()) if len(t) else 0
    nom = 1 - alpha
    _write(name or f"MS_main_{ds}", pd.DataFrame(rows),
           f"Per-building interval reliability and sharpness on {ds} (random-building protocol, nominal {nom:.0%}, "
           f"{t.seed.nunique()} seeds, ≈{n_b} target buildings per seed). MACD: mean |coverage − {nom:.2f}| over "
           f"buildings (coverage over the 56-day onboarding window); Under-cov.: share of buildings with coverage below "
           f"{nom - 0.05:.2f} (wk 1: first 7 forecast days only); P10: 10th percentile of per-building coverage; Rel. "
           f"width and Rel. IS: medians over buildings of width and interval score divided by the building's mean "
           f"load; Booking failures: share of buildings whose upper bound is exceeded in more than {100 * alpha:.0f} % of "
           f"hours (twice the nominal {50 * alpha:.1f} %), e.g. a capacity reservation sized by the upper bound; Reserve "
           f"cost: capacity-booking cost of the upper bound (pinball loss at {1 - alpha / 2:.3f}) in % of mean load. Mean ± s.d. over seeds. HSC-CQR = the pre-registered configuration (similarity prior, stage "
           f"matching, κ tuned on the interval score).")


def _ci(c):
    if isinstance(c, str):
        return [float(x) for x in c.strip("[]").split(",")]
    return c


def tests_table(st):
    rows = []
    t = st[(st.perturb == "none") & (st.alpha == 0.1) & (st.proposed == "PCS-CQR") & (st.protocol == "random")]
    keep = ["CQR", "QShrink-CQR (MACD)", "QShrink-CQR", "Self-CQR", "ACI-CQR", "ACI-CQR (MACD)", "TQA-B-CQR",
            "GHCP-CQR", "HSC-CQR", "PCS-CQR κ=168", "PCS-CQR +kNN+stage"]
    for ds in ["BDG2", "UCI"]:
        for bl in keep:
            row = {"Data": ds, "Baseline": LAB.get(bl, bl)}
            ok = False
            for metric, lab in [("abs_dev", "CD"), ("under", "Under"), ("rel_IS", "IS")]:
                r = t[(t.dataset == ds) & (t.baseline == bl) & (t.metric == metric)]
                if not len(r):
                    continue
                ok = True
                r = r.iloc[0]
                ci = _ci(r.ci95_mean_diff)
                sc = 100 if metric == "under" else 1
                dd = 1 if metric == "under" else 4
                p = "<0.001" if r.p_holm < 0.001 else f"{r.p_holm:.3f}"
                row[f"{lab}: diff. [95 % CI]"] = f"{sc * r.mean_diff:+.{dd}f} [{sc * ci[0]:+.{dd}f}, {sc * ci[1]:+.{dd}f}]"
                row[f"{lab}: p"] = p
            if ok:
                rows.append(row)
    _write("MS_tests", pd.DataFrame(rows),
           "Paired per-building comparison of PCS-CQR with each strategy (random-building protocol, nominal 90 %). "
           "CD = |coverage − 0.9|; Under = under-covered indicator (percentage points); IS = relative interval score. "
           "Diff. = PCS-CQR minus baseline, building-weighted mean (negative = PCS-CQR better); 95 % CI by site-"
           "cluster bootstrap (BDG2, 10 sites) or building bootstrap (UCI); p = two-sided sign-flip randomisation test "
           "with whole sites flipped (BDG2; exact, 1024 patterns, so p ≥ 0.002) or buildings flipped (UCI), Holm-"
           "adjusted within dataset, family and metric. Median differences, rank-biserial correlations and building-"
           "level Wilcoxon tests are in Supplementary Table S-tests.")


def ablation_table(s):
    rows = []
    meths = ["PCS-CQR", "PCS-CQR κ=168", "PCS-CQR (IS-tuned)", "PCS-CQR site-grouped", "PCS-CQR +stage",
             "PCS-CQR +kNN", "PCS-CQR +kNN+stage", "HSC-CQR", "PCS-CQR -shrink", "Self-CQR", "CQR",
             "QShrink-CQR (MACD)", "QShrink-CQR λ=168", "QShrink-CQR",
             "PCS", "PCS (IS-tuned)", "HSC", "HSC -stage", "HSC -kNN", "HSC -shrink", "Self-CP", "SCP-stage"]
    for m in meths:
        row = {"Variant": LAB.get(m, m)}
        for ds in ["BDG2", "UCI"]:
            x = _sel(s, "main", ds, "random")
            x = x[x.method == m]
            if not len(x):
                continue
            row[f"{ds} MACD"] = _pm(x.macd.mean(), x.macd.std())
            row[f"{ds} Under (%)"] = _pm(x.under_rate.mean(), x.under_rate.std(), pct=True)
            row[f"{ds} Under wk 1 (%)"] = _pm(x.under_w1.mean(), x.under_w1.std(), pct=True)
            row[f"{ds} Rel. IS"] = _pm(x.rel_IS.mean(), x.rel_IS.std())
        rows.append(row)
    _write("MS_ablation", pd.DataFrame(rows),
           "Design elements (random-building protocol, 90 %, mean ± s.d. over 5 seeds). PCS-CQR: uniform prior over "
           "all calibration buildings, no stage matching, κ by leave-one-building-out (LOBO) on the reliability "
           "objective (minimum coverage deviation among κ within 2 % of the best LOBO interval score). κ=168: fixed one-"
           "week pseudo-count (donor–local mixture); IS-tuned: κ by LOBO on the interval score (pre-registered "
           "objective); site-grouped: LOBO leaving out the whole site; +stage / +kNN: stage-matched / similarity-"
           "localised prior (re-tuned); HSC-CQR: pre-registered configuration (kNN + stage, IS-tuned); -shrink: prior "
           "only (κ = ∞); Self-*: κ = 0 with pooled fallback. QShrink: quantile-level shrinkage (λ by LOBO-IS, by the "
           "reliability objective, or fixed at 168). Lower block: the same on the absolute-residual score.")


def conditions_table(s):
    combos = [("main", "BDG2", "random", "none", "BDG2, random buildings"),
              ("lso", "BDG2", "leave-site-out", "none", "BDG2, leave-one-site-out"),
              ("xds", "BDG2", "BDG2->BDG2 (no weather)", "none", "BDG2, no weather"),
              ("xds", "BDG2", "UCI->BDG2 (no weather)", "none", "UCI → BDG2"),
              ("main", "UCI", "random", "none", "UCI, random clients"),
              ("xds", "UCI", "BDG2->UCI (no weather)", "none", "BDG2 → UCI"),
              ("robust", "BDG2", "random", "disjoint-cal-period", "Calibration period disjoint from training"),
              ("robust", "BDG2", "random", "weak-forecaster", "Weak forecaster"),
              ("robust", "BDG2", "random", "noise15", "Meter noise 15 % (history and truth)"),
              ("robust", "BDG2", "random", "noise15-history", "Meter noise 15 % (history only)"),
              ("robust", "BDG2", "random", "missing40", "Missing hours 40 %"),
              ("robust", "BDG2", "random", "outage7d", "7-day outage in weeks 1-3"),
              ("robust", "BDG2", "random", "shift+40@d7", "Level +40 % from day 7"),
              ("robust", "BDG2", "random", "shift+40", "Level +40 % from day 28"),
              ("robust", "BDG2", "random", "volatility25", "Day-to-day volatility from day 28"),
              ("pools", "BDG2", "random", "n_cal=10", "10 calibration buildings"),
              ("pools", "BDG2", "random", "n_cal=20", "20 calibration buildings")]
    rows = []
    for e, ds, p, pert, lab in combos:
        x = _sel(s, e, ds, p, perturb=pert)
        if not len(x):
            continue
        row = {"Condition": lab, "Runs": x.seed.nunique()}
        for m in COND_METHODS:
            y = x[x.method == m]
            row[LAB.get(m, m)] = "–" if not len(y) else f"{100 * y.under_rate.mean():.1f}"
        rows.append(row)
    _write("MS_conditions", pd.DataFrame(rows),
           "Share of under-covered buildings (%, coverage < 0.85 at nominal 90 %) across protocols and stress tests "
           "(mean over runs). Leave-one-site-out: every BDG2 site held out in turn, 3 training seeds per site; "
           "cross-dataset: forecaster and calibration scores from the source dataset, no weather features (3 seeds); "
           "stress tests on BDG2 (3 seeds) perturb the target buildings' onboarding windows; small pools: 5 random "
           "calibration subsets per seed. MACD, interval scores and paired tests for every condition are in the "
           "Supplementary Tables.")


def weeks_table(s):
    rows = []
    for ds in ["BDG2", "UCI"]:
        x = _sel(s, "main", ds, "random")
        for m in ["PCS-CQR", "PCS-CQR κ=168", "PCS-CQR +stage", "HSC-CQR", "QShrink-CQR (MACD)", "Self-CQR",
                  "ACI-CQR", "TQA-B-CQR", "GHCP-CQR", "CQR"]:
            y = x[x.method == m]
            if not len(y):
                continue
            row = {"Data": ds, "Method": LAB.get(m, m)}
            for w, lab in [("w1", "wk 1"), ("w2", "wk 2"), ("w34", "wk 3-4"), ("w58", "wk 5-8")]:
                row[f"Under {lab} (%)"] = f"{100 * y[f'under_{w}'].mean():.1f}"
                row[f"P10 {lab}"] = f"{y[f'p10_{w}'].mean():.3f}"
            rows.append(row)
    _write("MS_weeks", pd.DataFrame(rows),
           "Per-building reliability by onboarding week (random-building protocol, 90 %, mean over 5 seeds): share of "
           "buildings whose coverage within the week is below 0.85, and the 10th percentile of per-building weekly "
           "coverage. With 168 hourly forecasts per week, sampling noise alone puts roughly 5–10 % of perfectly "
           "calibrated buildings below 0.85 in a single week.")


def cost_table():
    info = json.load(open(os.path.join(RES, "run_info.json")))
    rows = []
    for d in ["BDG2", "UCI"]:
        parts = [k for k in info if k.startswith(f"main_{d}_s") and k.endswith("a0.1")]
        if not parts:
            continue
        def g(key, f=np.median):
            v = [info[k][key] for k in parts if info[k].get(key) is not None]
            return f(v) if v else np.nan
        tm = lambda name: np.median([info[k]["t_method"][name] for k in parts  # noqa: E731
                                     if name in (info[k].get("t_method") or {})])
        rows.append({"Data": d, "Training rows (M)": f"{g('n_train_rows') / 1e6:.2f}",
                     "LightGBM training, 3 models (s)": f"{g('lgb'):.0f} ({g('lgb', min):.0f}–{g('lgb', max):.0f})",
                     "LightGBM inference (ms / building-day)": f"{1e3 * g('pred_lgb_per_target_day'):.2f}",
                     "PCS-CQR tuning (s)": f"{tm('PCS-CQR tuning'):.1f}",
                     "HSC-CQR tuning + apply (s)": f"{tm('HSC-CQR'):.1f}",
                     "QShrink-CQR (s)": f"{tm('QShrink-CQR'):.1f}", "ACI-CQR (s)": f"{tm('ACI-CQR'):.1f}",
                     "PCS-CQR update (ms / building-day)": f"{1e3 * g('t_pcs_apply_incl_hist_per_target_day'):.3f}"})
    lat = os.path.join(RES, "latency.json")
    extra = ""
    if os.path.exists(lat):
        L = json.load(open(lat))
        extra = (f" Single-building latency of the daily PCS update (own-score histogram update + radius, measured "
                 f"separately on one core, {L['reps']} repetitions): median {L['single_ms_median']:.3f} ms "
                 f"(IQR {L['single_ms_q25']:.3f}–{L['single_ms_q75']:.3f}); state per building "
                 f"{L['state_kB']:.0f} kB.")
    _write("MS_cost", pd.DataFrame(rows),
           "Computational cost (median over 5 seeds; range in brackets). Calibration ran in single-threaded worker "
           "processes, four in parallel on a 4-core CPU; LightGBM training used 4 threads. Tuning times are for "
           "leave-one-building-out selection on all calibration buildings; 'update' is the batch time for all "
           "targets and stages divided by the number of building-days (amortised), including the own-score "
           "histograms." + extra)


def run():
    s = pd.read_csv(os.path.join(RES, "seed_level_metrics.csv"))
    s = s[~s.exp.isna()]
    st = pd.read_csv(os.path.join(RES, "statistics.csv"))
    for ds in ["BDG2", "UCI"]:
        main_table(s, ds)
        main_table(s, ds, methods=FULL_METHODS, name=f"MS_main_full_{ds}")
        for a in (0.05, 0.2):
            main_table(s, ds, methods=["PCS-CQR", "PCS-CQR κ=168", "HSC-CQR", "QShrink-CQR (MACD)", "Self-CQR",
                                       "ACI-CQR", "TQA-B-CQR", "GHCP-CQR", "CQR", "PCS", "HSC", "Self-CP",
                                       "SCP-stage"], name=f"MS_alpha{a}_{ds}", alpha=a)
    tests_table(st)
    ablation_table(s)
    conditions_table(s)
    weeks_table(s)
    cost_table()


if __name__ == "__main__":
    run()
