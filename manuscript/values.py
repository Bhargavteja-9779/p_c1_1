"""All numbers quoted in the manuscript text, computed from machine-generated result files.
Token naming: <condition>_<method>_<metric>; method names are sanitised (PCS-CQR κ=168 -> PCSCQR_kappa168).
Conditions: main_BDG2, main_UCI (suffix _a5 / _a20 for nominal 95 % / 80 %), lso_BDG2, xds_B2U, xds_U2B, xds_B2B,
rob_<perturbation>, pools_n<k>. Test tokens: test_<family>_<cond>_<baseline>_<metric>_{diff,ci,p,better,meddiff}."""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
PCT = ("under_rate", "book_fail", "under_w1", "under_w2", "under_w34", "under_w58", "reserve_cost")
METS = ["mean_cov", "macd", "under_rate", "p10_cov", "rel_width", "rel_IS", "rel_IS_mean", "book_fail", "reserve_cost",
        "under_w1", "under_w2", "under_w34", "under_w58", "p10_w1", "macd_w1", "width_p90"]


def _san(m):
    return (m.replace("-", "").replace("+", "").replace(" ", "_").replace("(", "").replace(")", "")
            .replace("κ", "kappa").replace("λ", "lambda").replace("=", ""))


def _fmt(met, val):
    if pd.isna(val):
        return "n/a"
    return f"{100 * val:.1f}%" if met in PCT else f"{val:.3f}"


def _kset(vals):
    out = sorted({float(x) for x in vals if x is not None}, key=lambda x: (np.isinf(x), x))
    return ", ".join("∞" if np.isinf(x) else str(int(x)) for x in out)


def compute(mode="full"):
    import sys
    sys.path.insert(0, ROOT)
    from src.experiments import get_ds
    from src.statistics.analysis import load, seed_level
    v = {}
    b, u = get_ds("BDG2"), get_ds("UCI")
    v["n_bdg2"] = b["load"].shape[0]
    v["n_sites"] = b["meta"].site_id.nunique()
    v["n_uci"] = u["load"].shape[0]
    fl = os.path.join(ROOT, "data", "processed", "BDG2_exclusion.json")
    if os.path.exists(fl):
        f = json.load(open(fl))["flow"]
        v["flow_bdg2_raw"] = f"{f[0]['n']:,}"
        v["flow_bdg2_sites_raw"] = f[0]["sites"]
        v["flow_bdg2_removed_missing"] = f"{f[1]['n'] - f[2]['n']:,}"
        v["flow_bdg2_removed_floor"] = f"{f[2]['n'] - f[3]['n']:,}"
    fu = os.path.join(ROOT, "data", "processed", "UCI_exclusion.json")
    v["n_uci_raw"] = json.load(open(fu))["flow"][0]["n"] if os.path.exists(fu) else 370
    df = load()
    df = df[df.part.str.contains("_quick") == (mode == "quick")]
    s = seed_level(df)
    st = pd.read_csv(os.path.join(RES, "statistics.csv"))
    conds = {("main", "BDG2", "random", "none"): "main_BDG2", ("main", "UCI", "random", "none"): "main_UCI",
             ("lso", "BDG2", "leave-site-out", "none"): "lso_BDG2",
             ("xds", "UCI", "BDG2->UCI (no weather)", "none"): "xds_B2U",
             ("xds", "BDG2", "UCI->BDG2 (no weather)", "none"): "xds_U2B",
             ("xds", "BDG2", "BDG2->BDG2 (no weather)", "none"): "xds_B2B"}
    for p in s[s.exp == "robust"].perturb.unique():
        conds[("robust", "BDG2", "random", p)] = "rob_" + p.replace("+", "p").replace("-", "m").replace("@", "_")
    for p in s[s.exp == "pools"].perturb.unique():
        conds[("pools", "BDG2", "random", p)] = "pools_n" + p.split("=")[1]
    for (e, d, p, pert), name in conds.items():
        for a in [0.1, 0.05, 0.2]:
            t = s[(s.exp == e) & (s.dataset == d) & (s.protocol == p) & (s.alpha == a) & (s.perturb == pert)]
            if not len(t):
                continue
            g = t.groupby("method").mean(numeric_only=True)
            sd = t.groupby("method").std(numeric_only=True)
            suf = "" if a == 0.1 else f"_a{int(a * 100)}"
            for m in g.index:
                for met in METS:
                    if met not in g:
                        continue
                    k = f"{name}{suf}_{_san(m)}_{met}"
                    v[k] = _fmt(met, g.loc[m, met])
                    v[k + "_sd"] = (f"{100 * sd.loc[m, met]:.1f}" if met in PCT else f"{sd.loc[m, met]:.3f}") \
                        if not pd.isna(sd.loc[m, met]) else "0"
            v[f"{name}{suf}_nseeds"] = t.seed.nunique()
            if "PCS-CQR" in set(t.method):
                v[f"{name}{suf}_ntargets"] = int(t[t.method == "PCS-CQR"].n.mean())
    # relative reductions of the under-covered share and MACD vs CQR
    for name in ["main_BDG2", "main_UCI", "lso_BDG2", "xds_B2U", "xds_U2B"]:
        for a_ in ["PCSCQR", "PCSCQR_kappa168", "HSCCQR", "QShrinkCQR_MACD", "SelfCQR"]:
            for met in ["macd", "under_rate", "book_fail"]:
                ka, kb = f"{name}_{a_}_{met}", f"{name}_CQR_{met}"
                if ka in v and kb in v and v[kb] != "n/a":
                    x, y = float(v[ka].rstrip("%")), float(v[kb].rstrip("%"))
                    v[f"red_{name}_{a_}_{met}"] = f"{100 * (y - x) / y:.0f}%" if y else "n/a"
    # statistics tokens
    pn = {"random": "main", "leave-site-out": "lso", "BDG2->UCI (no weather)": "xds_B2U",
          "UCI->BDG2 (no weather)": "xds_U2B", "BDG2->BDG2 (no weather)": "xds_B2B"}
    for _, r in st.iterrows():
        cond = pn.get(r.protocol, "x")
        if r.perturb != "none":
            cond = "rob_" + str(r.perturb).replace("+", "p").replace("-", "m").replace("@", "_")
        suf = "" if r.alpha == 0.1 else f"_a{int(r.alpha * 100)}"
        k = f"test_{cond}{suf}_{r.dataset}_{_san(r.proposed)}_vs_{_san(r.baseline)}_{r.metric}"
        sc = 100 if r.metric in ("under", "book_fail") else 1
        dd = 1 if sc == 100 else 4
        ci = json.loads(r.ci95_mean_diff) if isinstance(r.ci95_mean_diff, str) else r.ci95_mean_diff
        v[k + "_p"] = "p < 0.001" if r.p_holm < 0.001 else f"p = {r.p_holm:.3f}"
        v[k + "_diff"] = f"{sc * r.mean_diff:+.{dd}f}"
        v[k + "_ci"] = f"[{sc * ci[0]:+.{dd}f}, {sc * ci[1]:+.{dd}f}]"
        v[k + "_meddiff"] = f"{sc * r.median_diff:+.{dd}f}"
        v[k + "_better"] = f"{100 * r.share_proposed_better:.0f}%"
        v[k + "_r"] = f"{r.rank_biserial:.2f}"
        v[k + "_n"] = int(r.n_buildings)
    # tuned parameters
    info = json.load(open(os.path.join(RES, "run_info.json")))
    tag = "_quick" if mode == "quick" else ""
    for d in ["BDG2", "UCI"]:
        parts = [k for k in info if k.startswith(f"main{tag}_{d}_s") and k.endswith("a0.1")]
        if not parts:
            continue
        g = lambda key, sub="kappa": [(info[k].get(key) or {}).get(sub) for k in parts]  # noqa: E731
        v[f"tuned_{d}_pcs"] = _kset(g("pcs_cqr"))
        v[f"tuned_{d}_pcs_is"] = _kset(g("hsc_cqr_simple"))
        v[f"tuned_{d}_hsccqr_kappa"] = _kset(g("hsc_cqr"))
        v[f"tuned_{d}_hsccqr_K"] = ", ".join(sorted({"all" if x is None else str(x) for x in g("hsc_cqr", "K")}))
        v[f"tuned_{d}_pcs_abs"] = _kset(g("pcs"))
        v[f"tuned_{d}_pcs_mlp"] = _kset(g("pcs_cqr_mlp"))
        v[f"tuned_{d}_qshrink_is"] = _kset([info[k].get("qshrink_lambda") for k in parts])
        v[f"tuned_{d}_qshrink_macd"] = _kset([info[k].get("qshrink_lambda_macd") for k in parts])
        v[f"tuned_{d}_aci_is"] = ", ".join(sorted({str(info[k].get("aci_cqr_gamma")) for k in parts}))
        v[f"tuned_{d}_aci_macd"] = ", ".join(sorted({str(info[k].get("aci_cqr_gamma_macdc")) for k in parts}))
        v[f"tuned_{d}_aci_cov"] = ", ".join(sorted({str(info[k].get("aci_cqr_gamma_cov")) for k in parts}))
        # flatness of the LOBO interval-score objective of PCS-CQR (relative range over finite kappa > 0)
        fl = []
        for k in parts:
            tb = pd.DataFrame(info[k]["tune_pcs_cqr"])
            tb["kappa"] = tb.kappa.replace("inf", np.inf).astype(float)
            fin = tb[(tb.kappa > 0) & np.isfinite(tb.kappa)]
            fl.append(100 * (fin.obj.max() - fin.obj.min()) / fin.obj.min())
            inf_ = tb[np.isinf(tb.kappa)]
            v.setdefault(f"tune_{d}_inf_vs_best", [])
            v[f"tune_{d}_inf_vs_best"].append(100 * (inf_.obj.iloc[0] - tb.obj.min()) / tb.obj.min())
        v[f"tune_{d}_is_range_pct"] = f"{np.median(fl):.1f}"
        v[f"tune_{d}_inf_vs_best"] = f"{np.median(v[f'tune_{d}_inf_vs_best']):.1f}"
        md = lambda key: np.median([info[k][key] for k in parts if info[k].get(key) is not None])  # noqa: E731
        v[f"cost_{d}_pcs_apply_ms"] = f"{1e3 * md('t_pcs_apply_incl_hist_per_target_day'):.3f}"
        v[f"cost_{d}_lgb_s"] = f"{md('lgb'):.0f}"
        v[f"cost_{d}_train_rows"] = f"{md('n_train_rows') / 1e6:.2f}"
        v[f"cost_{d}_pcs_tune_s"] = f"{np.median([info[k]['t_method']['PCS-CQR tuning'] for k in parts]):.1f}"
        v[f"cost_{d}_hsc_tune_s"] = f"{np.median([info[k]['t_method']['HSC-CQR'] for k in parts if 'HSC-CQR' in info[k]['t_method']]):.1f}"
        v[f"point_{d}_cvrmse_lgb"] = f"{np.mean([info[k]['point']['cvrmse'] for k in parts]):.3f}"
        v[f"point_{d}_cvrmse_naive"] = f"{np.mean([info[k]['point_naive']['cvrmse'] for k in parts]):.3f}"
        if all("point_mlp" in info[k] for k in parts):
            v[f"point_{d}_cvrmse_mlp"] = f"{np.mean([info[k]['point_mlp']['cvrmse'] for k in parts]):.3f}"
    # selected kappa under leave-one-site-out and small pools
    lso = [k for k in info if k.startswith("loso") and "pcs_cqr" in info[k]]
    if lso:
        v["tuned_lso_pcs"] = _kset([info[k]["pcs_cqr"]["kappa"] for k in lso])
    lat = os.path.join(RES, "latency.json")
    if os.path.exists(lat):
        L = json.load(open(lat))
        v["lat_single_ms"] = f"{L['single_ms_median']:.3f}"
        v["lat_batch10k_s"] = f"{L['batch_10k_buildings_s']:.1f}"
        v["lat_state_kB"] = f"{L['state_kB']:.0f}"
    # sensitivity (PCS-CQR: no stage matching, K = all)
    sp = os.path.join(RES, f"sensitivity{tag}.csv")
    if os.path.exists(sp):
        sens = pd.read_csv(sp)
        if "stage_matched" in sens:
            for d in ["BDG2", "UCI"]:
                x = sens[(sens.dataset == d) & (sens.score == "cqr") & (sens.K.astype(str) == "all") &
                         (sens.stage_matched == "no")]
                g = x.groupby("kappa")[["macd", "under", "rel_IS", "under_w1"]].mean()
                fin = g[(g.index > 0) & np.isfinite(g.index)]
                v[f"sens_{d}_macd_min"] = f"{fin.macd.min():.3f}"
                v[f"sens_{d}_kappa_best"] = str(int(fin.macd.idxmin()))
                v[f"sens_{d}_macd_inf"] = f"{g.loc[np.inf, 'macd']:.3f}" if np.inf in g.index else "n/a"
                v[f"sens_{d}_is_range"] = f"{fin.rel_IS.min():.3f}–{fin.rel_IS.max():.3f}"
                v[f"sens_{d}_macd_range"] = f"{fin.macd.min():.3f}–{fin.macd.max():.3f}"
    # sampling-noise floor of MACD for perfectly calibrated intervals with independent misses
    rng = np.random.default_rng(0)
    for d in ["BDG2", "UCI"]:
        nv = df[(df.exp == "main") & (df.dataset == d) & (df.alpha == 0.1) & (df.method == "PCS-CQR")].n_valid.values
        if len(nv):
            sim = rng.binomial(nv[None, :].repeat(200, 0), 0.9) / nv[None, :]
            v[f"floor_{d}_macd"] = f"{np.abs(sim - 0.9).mean():.4f}"
            v[f"floor_{d}_under"] = f"{100 * (sim < 0.85).mean():.2f}%"
            w1 = rng.binomial(168, 0.9, size=100000) / 168
            v["floor_w1_under"] = f"{100 * (w1 < 0.85).mean():.1f}%"
            v[f"nvalid_{d}_median"] = int(np.median(nv))
    v["ERROR_ANALYSIS_TEXT"] = _error_text()
    v["n_bdg2_plus_uci"] = f"{v['n_bdg2'] + v['n_uci']:,}"
    v["ABSTRACT"] = _abstract(v)
    json.dump(v, open(os.path.join(RES, f"manuscript_values{tag}.json"), "w"), indent=1, default=str)
    return v


def _p(p):
    return "p < 0.001" if p < 0.001 else f"p = {p:.3f}"


def _error_text():
    """Error-analysis paragraph whose wording follows the actual test outcomes (building-level units)."""
    f = os.path.join(RES, "error_analysis.json")
    if not os.path.exists(f):
        return "(error analysis not available)"
    e = json.load(open(f))
    b = e.get("BDG2", {})
    t = []
    if "rho_cov_cvrmse_CQR" in b:
        t.append(f"On BDG2 the Spearman correlation between per-building coverage and CV(RMSE) is "
                 f"{b['rho_cov_cvrmse_CQR']:.2f} for CQR and {b['rho_cov_cvrmse_PCS-CQR']:.2f} for PCS-CQR, i.e. PCS "
                 + ("weakens" if abs(b['rho_cov_cvrmse_PCS-CQR']) < abs(b['rho_cov_cvrmse_CQR']) else "does not weaken")
                 + " the dependence of reliability on forecast difficulty.")
    if "usage_largest_reduction" in b:
        tie = b.get("usage_largest_reduction_tie")
        t.append("Across usage classes with at least 30 building × seed units, the coverage deviation falls in every "
                 "class" if all(r["reduction"] > 0 for r in b["usage_table"]) else
                 "Across usage classes with at least 30 building × seed units, the coverage deviation does not fall in "
                 "every class")
        t[-1] += ("" if tie else f"; the reduction is largest for '{b['usage_largest_reduction']}'") + \
            f" and smallest for '{b['usage_smallest_reduction']}'."
    if "shift_median_under" in b:
        txt = (f"Of {b['n_units']} BDG2 target buildings (seed-averaged), {b['n_under']} remain under-covered by "
               f"PCS-CQR. Their median within-window level change |log(mean load weeks 5–8 / weeks 1–4)| is "
               f"{b['shift_median_under']:.3f} versus {b['shift_median_other']:.3f} for the others")
        if "shift_p" in b:
            sig = b["shift_p"] < 0.05
            txt += (f" (Mann–Whitney {_p(b['shift_p'])}); "
                    + ("the remaining failures are associated with regime changes during onboarding"
                       if sig and b['shift_median_under'] > b['shift_median_other'] else
                       "level changes alone do not explain the remaining failures")
                    + f". Their first-week volatility is {b['vol_median_under']:.3f} versus "
                      f"{b['vol_median_other']:.3f} ({_p(b['vol_p'])}).")
        else:
            txt += " (too few buildings for a test; descriptive only)."
        t.append(txt)
    u = e.get("UCI", {})
    if "n_under" in u:
        t.append(f"On UCI, {u['n_under']} of {u['n_units']} clients remain under-covered (descriptive only).")
    return " ".join(t)


def _abstract(v):
    g = lambda k: v.get(k, "n/a")  # noqa: E731
    a = (
        "Demand response, flexibility bidding and measurement-and-verification need day-ahead prediction intervals for "
        "individual buildings, often from the first days after metering starts. Interval methods are usually judged by "
        "coverage pooled over many buildings, which can hide buildings whose intervals are systematically too narrow. "
        f"We evaluate per-building interval reliability during onboarding on {g('n_bdg2')} buildings at "
        f"{g('n_sites')} sites (Building Data Genome 2) and {g('n_uci')} Portuguese electricity clients, under a "
        "building- and period-disjoint protocol with five seeds, every site held out in turn, cross-country transfer "
        "and stress tests. On one global quantile forecaster we compare pooled conformalised quantile regression (CQR) "
        "with self-only, adaptive (ACI), temporal-quantile-adjustment, hierarchical and quantile-shrinkage calibration "
        "and with a pseudo-count shrinkage of the score distribution towards each building's accumulating own scores "
        "(PCS). Pooled CQR left "
        f"{g('main_BDG2_CQR_under_rate')} (BDG2) and {g('main_UCI_CQR_under_rate')} (UCI) of new buildings more than "
        "five points below the 90 % target. PCS, with its pseudo-count chosen by leave-one-building-out for "
        f"reliability, reduced these shares to {g('main_BDG2_PCSCQR_under_rate')} and "
        f"{g('main_UCI_PCSCQR_under_rate')} without loss of sharpness; quantile shrinkage tuned the same way performed "
        "similarly, whereas ACI reached comparable reliability only with intervals about twice as wide. No strategy "
        "repaired first-week under-coverage. Similarity-weighted priors and onboarding-stage matching added nothing, "
        "leaving a one-parameter layer that costs well under a millisecond per building-day."
    )
    n = len(a.split())
    assert n <= 250, f"abstract has {n} words (> 250)"
    return a
