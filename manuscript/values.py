"""All numbers quoted in the manuscript text, computed from machine-generated result files.
Token naming: <table>_<dataset>_<method>_<metric>; method names are sanitised (HSC-CQR -> HSCCQR)."""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")


def _san(m):
    return (m.replace("-", "").replace("+", "").replace(" ", "_").replace("(", "").replace(")", "")
            .replace("κ", "kappa"))


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
    v["n_uci_raw"] = 370
    df = load()
    df = df[df.part.str.contains("_quick") == (mode == "quick")]
    s = seed_level(df)
    st = pd.read_csv(os.path.join(RES, "statistics.csv"))
    st = st[np.isfinite(st.p_holm)] if "p_holm" in st else st
    # seed-level summaries for every experiment/dataset/method
    keys = {("main", "BDG2", "random"): "main_BDG2", ("main", "UCI", "random"): "main_UCI",
            ("lso", "BDG2", "leave-site-out"): "lso_BDG2",
            ("xds", "UCI", "BDG2->UCI (no weather)"): "xds_B2U", ("xds", "BDG2", "UCI->BDG2 (no weather)"): "xds_U2B",
            ("xds", "BDG2", "BDG2->BDG2 (no weather)"): "xds_B2B"}
    for (e, d, p), name in keys.items():
        for a in [0.1, 0.05, 0.2]:
            t = s[(s.exp == e) & (s.dataset == d) & (s.protocol == p) & (s.alpha == a) & (s.perturb == "none")]
            if not len(t):
                continue
            g = t.groupby("method").mean(numeric_only=True)
            sd = t.groupby("method").std(numeric_only=True)
            suf = "" if a == 0.1 else f"_a{int(a * 100)}"
            for m in g.index:
                for met in ["mean_cov", "cov_early", "macd", "under_rate", "p10_cov", "rel_width", "rel_IS",
                            "rel_IS_early", "rel_IS_mean", "under_wk1", "underprot", "under_floor", "under_floor_week",
                            "up_exc", "floor", "cost10", "cost20", "cost40", "cost20_worst10"]:
                    if met not in g.columns:
                        continue
                    val = g.loc[m, met]
                    k = f"{name}{suf}_{_san(m)}_{met}"
                    if met in ("under_rate", "under_wk1", "underprot", "under_floor", "under_floor_week", "up_exc"):
                        v[k] = f"{100 * val:.1f}%"
                        v[k + "_sd"] = f"{100 * sd.loc[m, met]:.1f}"
                    else:
                        v[k] = f"{val:.3f}"
                        v[k + "_sd"] = f"{sd.loc[m, met]:.3f}"
            v[f"{name}{suf}_nseeds"] = t.seed.nunique()
            v[f"{name}{suf}_ntargets"] = int(t[t.method == "HSC"].n.mean()) if "HSC" in set(t.method) else 0
    # relative improvements HSC-CQR vs CQR and HSC vs SCP-stage on MACD and IS
    for name in ["main_BDG2", "main_UCI", "lso_BDG2", "xds_B2U", "xds_U2B"]:
        for a_, b_ in [("HSCCQR", "CQR"), ("HSC", "SCPstage"), ("HSCCQR", "MLPQR"), ("HSCCQR", "QRLGBM"),
                       ("HSC", "ACI"), ("HSC", "SelfCP")]:
            for met in ["macd", "rel_IS", "under_rate"]:
                ka, kb = f"{name}_{a_}_{met}", f"{name}_{b_}_{met}"
                if ka in v and kb in v:
                    x = float(v[ka].rstrip("%"))
                    y = float(v[kb].rstrip("%"))
                    v[f"red_{name}_{a_}_vs_{b_}_{met}"] = f"{100 * (y - x) / y:.0f}%" if y else "n/a"
    # statistics tokens
    for _, r in st.iterrows():
        if r.perturb != "none" or r.alpha != 0.1:
            continue
        nm = {"random": "main", "leave-site-out": "lso"}.get(r.protocol, "xds_" + r.protocol[:9].replace("->", "2"))
        k = f"test_{nm}_{r.dataset}_{_san(r.proposed)}_vs_{_san(r.baseline)}_{r.metric}"
        v[k + "_p"] = "< 0.001" if r.p_holm < 0.001 else f"= {r.p_holm:.3f}"
        v[k + "_r"] = f"{r.rank_biserial:.2f}"
        v[k + "_better"] = f"{100 * r.share_proposed_better:.0f}%"
        v[k + "_n"] = int(r.n_buildings)
    # tuned parameters and cost
    info = json.load(open(os.path.join(RES, "run_info.json")))
    tag = "_quick" if mode == "quick" else ""
    for d in ["BDG2", "UCI"]:
        parts = [k for k in info if k.startswith(f"main{tag}_{d}_s") and k.endswith("a0.1")]
        if not parts:
            continue
        kap = [info[k]["hsc_cqr"]["kappa"] for k in parts]
        K = [info[k]["hsc_cqr"]["K"] for k in parts]
        v[f"tuned_{d}_kappa"] = ", ".join(sorted({("∞" if np.isinf(x) else str(int(x))) for x in kap}))
        v[f"tuned_{d}_K"] = ", ".join(sorted({"all" if x is None else str(x) for x in K}))
        kap2 = [info[k]["hsc_kappa"] for k in parts]
        v[f"tuned_{d}_kappa_abs"] = ", ".join(sorted({("∞" if np.isinf(x) else str(int(x))) for x in kap2}))
        v[f"tuned_{d}_gamma"] = ", ".join(sorted({str(info[k]["aci_gamma"]) for k in parts}))
        v[f"tuned_{d}_gamma_cqr"] = ", ".join(sorted({str(info[k]["aci_cqr_gamma"]) for k in parts}))
        v[f"tuned_{d}_lambda_qshrink"] = ", ".join(sorted({("∞" if np.isinf(info[k]["qshrink_lambda"]) else
                                                             str(int(info[k]["qshrink_lambda"]))) for k in parts}))
        v[f"tuned_{d}_kappa_simple"] = ", ".join(sorted({("∞" if np.isinf(info[k]["hsc_cqr_simple"]["kappa"]) else
                                                           str(int(info[k]["hsc_cqr_simple"]["kappa"]))) for k in parts}))
        v[f"tuned_{d}_kappa_mlp"] = ", ".join(sorted({("∞" if np.isinf(info[k]["hsc_cqr_mlp"]["kappa"]) else
                                                        str(int(info[k]["hsc_cqr_mlp"]["kappa"]))) for k in parts}))
        v[f"cost_{d}_tune_s"] = f"{np.mean([info[k]['t_tune_hsc'] for k in parts]):.1f}"
        v[f"cost_{d}_apply_ms"] = f"{1e3 * np.mean([info[k]['t_hsc_apply_per_target_day'] for k in parts]):.3f}"
        v[f"cost_{d}_store_MB"] = f"{np.mean([info[k]['hsc_store_MB'] for k in parts]):.1f}"
        v[f"cost_{d}_lgb_s"] = f"{np.mean([info[k]['lgb'] for k in parts]):.0f}"
        v[f"cost_{d}_mlp_s"] = f"{np.mean([info[k]['mlp'] for k in parts]):.0f}"
        v[f"cost_{d}_train_rows"] = f"{np.mean([info[k]['n_train_rows'] for k in parts]) / 1e6:.2f}"
        v[f"point_{d}_cvrmse_lgb"] = f"{np.mean([info[k]['point']['cvrmse'] for k in parts]):.3f}"
        v[f"point_{d}_cvrmse_naive"] = f"{np.mean([info[k]['point_naive']['cvrmse'] for k in parts]):.3f}"
        v[f"point_{d}_cvrmse_mlp"] = f"{np.mean([info[k]['point_mlp']['cvrmse'] for k in parts]):.3f}"
    # robustness tokens
    rb = s[s.exp == "robust"]
    if len(rb):
        g = rb.groupby(["perturb", "method"]).mean(numeric_only=True)
        for (p, m), r in g.iterrows():
            for met in ["macd", "under_rate", "rel_IS", "mean_cov"]:
                val = r[met]
                v[f"rob_{p}_{_san(m)}_{met}"] = f"{100 * val:.1f}%" if met == "under_rate" else f"{val:.3f}"
    # sensitivity
    sp = os.path.join(RES, f"sensitivity{tag}.csv")
    if os.path.exists(sp):
        sens = pd.read_csv(sp)
        for d in ["BDG2", "UCI"]:
            x = sens[(sens.dataset == d) & (sens.score == "cqr") & (sens.kappa > 0)]
            g = x.groupby(["K", "kappa"]).macd.mean()
            v[f"sens_{d}_macd_min"] = f"{g.min():.3f}"
            v[f"sens_{d}_macd_max_finite"] = f"{g[[k for k in g.index if np.isfinite(k[1])]].max():.3f}"
            v[f"sens_{d}_macd_inf"] = f"{g[[k for k in g.index if np.isinf(k[1])]].mean():.3f}"
    # sampling-noise floor of MACD for perfectly calibrated intervals with independent misses:
    # E|Binomial(n, 0.9)/n - 0.9| evaluated by Monte Carlo at each building's number of valid hours
    rng = np.random.default_rng(0)
    for d in ["BDG2", "UCI"]:
        nv = df[(df.exp == "main") & (df.dataset == d) & (df.alpha == 0.1) & (df.method == "HSC-CQR")].n_valid.values
        if len(nv):
            sim = np.abs(rng.binomial(nv[None, :].repeat(200, 0), 0.9) / nv[None, :] - 0.9).mean()
            v[f"floor_{d}_macd"] = f"{sim:.4f}"
            v[f"nvalid_{d}_median"] = int(np.median(nv))
    # ---- tokens: recommended method (rule A.1), cost changes, weekly curves, frontier
    rec = json.load(open(os.path.join(RES, "recommended.json"))) if os.path.exists(os.path.join(RES, "recommended.json")) else None
    if rec:
        v["PRIMARY"] = rec["recommended"]
        v["primary_san"] = _san(rec["recommended"])
        for r in rec["table"]:
            v[f"rec_{_san(r['method'])}_is_ratio_BDG2"] = f"{100 * (r['is_ratio_BDG2'] - 1):+.1f}%"
            v[f"rec_{_san(r['method'])}_is_ratio_UCI"] = f"{100 * (r['is_ratio_UCI'] - 1):+.1f}%"
    for name, d in [("main_BDG2", "BDG2"), ("main_UCI", "UCI")]:
        t = s[(s.exp == "main") & (s.dataset == d) & (s.alpha == 0.1) & (s.perturb == "none")]
        if "cost20" not in t:
            continue
        base = t[t.method == "CQR"].set_index("seed")
        for m in t.method.unique():
            x = t[t.method == m].set_index("seed")
            for c in ["cost10", "cost20", "cost40", "cost20_worst10"]:
                dlt = 100 * (x[c] / base.loc[x.index, c] - 1)
                v[f"{name}_{_san(m)}_{c}_delta"] = f"{dlt.mean():+.1f}%"
    wf = os.path.join(RES, "weekly_coverage.csv")
    if os.path.exists(wf):
        w = pd.read_csv(wf)
        g = w.groupby(["dataset", "method", "week"]).under.mean()
        for (d, m, wk), val in g.items():
            v[f"wk_{d}_{_san(m)}_w{wk}"] = f"{100 * val:.1f}%"
    ff = os.path.join(RES, f"frontier{tag}.csv")
    if os.path.exists(ff):
        fr = pd.read_csv(ff)
        g = fr.groupby(["dataset", "family", "param"])[["under", "rel_IS", "under_wk1"]].mean().reset_index()
        for _, r in g.iterrows():
            par = "inf" if np.isinf(r.param) else (f"{r.param:g}")
            k = f"fr_{r.dataset}_{_san(r.family)}_{par}"
            v[k + "_under"] = f"{100 * r.under:.1f}%"
            v[k + "_IS"] = f"{r.rel_IS:.3f}"
            v[k + "_wk1"] = f"{100 * r.under_wk1:.1f}%"
    for d in ["BDG2", "UCI"]:
        parts = [k for k in info if k.startswith(f"main{tag}_{d}_s") and k.endswith("a0.1")]
        def _set(key, sub="kappa"):
            vals = [info[k][key][sub] if isinstance(info[k].get(key), dict) else info[k].get(key) for k in parts
                    if info[k].get(key) is not None]
            return ", ".join(sorted({("∞" if np.isinf(float(x)) else f"{float(x):g}") for x in vals}))
        for key in ["hsc_cqr_simple_cov", "hsc_cqr_recency", "hsc_ssc_cqr"]:
            if parts and key in info[parts[0]]:
                v[f"tuned_{d}_{key}"] = _set(key)
        for key in ["qshrink_lambda_cov", "aci_cqr_gamma_cov"]:
            if parts and key in info[parts[0]]:
                v[f"tuned_{d}_{key}"] = _set(key, None)
        if parts and "aci_cqr_capped_frac" in info[parts[0]]:
            v[f"aci_{d}_capped"] = f"{100 * np.mean([info[k]['aci_cqr_capped_frac'] for k in parts]):.2f}%"
            v[f"aci_{d}_capped_abs"] = f"{100 * np.mean([info[k]['aci_capped_frac'] for k in parts]):.2f}%"
        if parts and "t_ssc_apply_per_target_day" in info[parts[0]]:
            v[f"cost_{d}_ssc_apply_ms"] = f"{1e3 * np.mean([info[k]['t_ssc_apply_per_target_day'] for k in parts]):.3f}"
            v[f"cost_{d}_tune_cov_s"] = f"{np.mean([info[k]['t_tune_hsc_cov'] for k in parts]):.1f}"
    q = st[(st.proposed == v.get("PRIMARY", "")) & (st.protocol == "random") & (st.perturb == "none") &
           (st.alpha == 0.1) & (st.dataset == "BDG2") & st.metric.isin(["abs_dev", "abs_dev_early"]) &
           (st.share_proposed_better > 0.5)] if "p_site" in st else st.iloc[:0]
    if len(q):
        v["max_psite_primary_BDG2"] = f"{q.p_site.max():.3f}"
    tf = os.path.join(RES, "timing.json")
    if os.path.exists(tf):
        tm = json.load(open(tf))
        for d, r in ((d, tm[d]) for d in ("BDG2", "UCI") if d in tm):
            v[f"time_{d}_recency_apply_ms"] = f"{r['recency_apply_ms_per_building_day']:.3f}"
            if "lgb_inference_ms_per_building_day" in r:
                v[f"time_{d}_lgb_infer_ms"] = f"{r['lgb_inference_ms_per_building_day']['median']:.2f}"
                v[f"time_{d}_state_KB"] = f"{1e3 * r['memory_MB']['per_building_state']:.0f}"
                v[f"time_{d}_tuning_MB"] = f"{r['memory_MB']['tuning_counts']:.0f}"
            v[f"time_{d}_cqr_apply_ms"] = f"{r['cqr_apply_ms_per_building_day']:.4f}"
            v[f"time_{d}_aci_apply_ms"] = f"{r['aci_apply_ms_per_building_day']:.3f}"
            v[f"time_{d}_recency_tune_s"] = f"{r.get('recency_tune_s_median', r['recency_tune_s']):.1f}"
            v[f"time_{d}_store_MB"] = f"{r['store_MB']:.1f}"
            v[f"time_{d}_lgb_s"] = f"{r['lgb_3models_s']:.0f}"
            v[f"time_{d}_mlp_s"] = f"{r['mlp_2models_s']:.0f}"
    if os.path.exists(ff):
        for d in ["BDG2", "UCI"]:
            ref = g[(g.dataset == d) & (g.family == "HSC (decay 1.0)") & np.isinf(g.param)].rel_IS
            if len(ref):
                for _, r in g[(g.dataset == d) & (g.family == "ACI")].iterrows():
                    v[f"fr_{d}_ACI_{r.param:g}_ISdelta"] = f"{100 * (r.rel_IS / ref.iloc[0] - 1):+.0f}%"
    eaf = os.path.join(RES, "error_analysis.json")
    if os.path.exists(eaf):
        ea = json.load(open(eaf))
        for d in ["BDG2", "UCI"]:
            if d in ea:
                v[f"ea_{d}_rho_CQR"] = f"{ea[d]['rho_cov_cvrmse_CQR']:.2f}"
                v[f"ea_{d}_rho_primary"] = f"{ea[d]['rho_cov_cvrmse_' + ea[d]['primary']]:.2f}"
    v["ERROR_ANALYSIS_TEXT"] = _error_text()
    v["ABSTRACT"] = _abstract(v)
    v["n_bdg2_plus_uci"] = f"{v['n_bdg2'] + v['n_uci']:,}"
    json.dump(v, open(os.path.join(RES, f"manuscript_values{tag}.json"), "w"), indent=1, default=str)
    return v


def _p(p):
    return "p < 0.001" if p < 0.001 else f"p = {p:.3f}"


def _error_text():
    """Error-analysis paragraph whose wording follows the actual test outcomes (recommended method)."""
    f = os.path.join(RES, "error_analysis.json")
    if not os.path.exists(f):
        return "(error analysis not available)"
    e = json.load(open(f))
    b = e.get("BDG2", {})
    P = b.get("primary", "HSC-CQR")
    t = []
    if "rho_cov_cvrmse_CQR" in b:
        t.append(f"With pooled CQR, a building's coverage falls with its forecast difficulty (Spearman correlation "
                 f"between per-building coverage and CV(RMSE): {b['rho_cov_cvrmse_CQR']:.2f} on BDG2, "
                 f"{e['UCI']['rho_cov_cvrmse_CQR']:.2f} on UCI); with the proposed layer the correlation is "
                 f"{b['rho_cov_cvrmse_' + P]:.2f} and {e['UCI']['rho_cov_cvrmse_' + P]:.2f} (Fig. [-@fig:errors]a).")
    if "usage_largest_reduction" in b:
        t.append(f"Across usage classes with at least 30 building × seed units, the largest reduction of the absolute "
                 f"coverage deviation is observed for '{b['usage_largest_reduction']}' and the smallest for "
                 f"'{b['usage_smallest_reduction']}' (Fig. [-@fig:errors]b).")
    if "n_under" in b:
        s_ = (f"Of the {b['n_units']} BDG2 building × seed units, {b['n_under']} remain under-covered")
        if "shift_p" in b:
            sig = b["shift_p"] < 0.05
            s_ += (f"; their median within-window level change |log(mean load weeks 5–8 / weeks 1–4)| is "
                   f"{b['shift_median_under']:.3f} versus {b['shift_median_other']:.3f} for the others "
                   f"(Mann–Whitney {_p(b['shift_p'])}), and their first-week volatility is {b['vol_median_under']:.3f} "
                   f"versus {b['vol_median_other']:.3f} ({_p(b['vol_p'])}). With so few failures, these comparisons "
                   + ("indicate an association with level changes" if sig else "are not conclusive") + "")
        t.append(s_ + ".")
    u = e.get("UCI", {})
    if "n_under" in u:
        t.append(f"On UCI, {u['n_under']} of {u['n_units']} units remain under-covered.")
    return " ".join(t)


def _abstract(v):
    a = (
        "Demand response, flexibility offers and measurement-and-verification need day-ahead load intervals for "
        "individual buildings, often from the first days after a building is metered. Interval methods are usually "
        "judged by coverage pooled over many buildings, which can hide buildings whose intervals are systematically "
        "too narrow. We propose a recency-weighted shrinkage conformal calibration layer that mixes each new "
        "building's exponentially down-weighted nonconformity scores with the score distribution of previously "
        "onboarded buildings, with a pseudo-count selected by leave-one-building-out for per-building coverage. "
        "Under a building- and period-disjoint protocol on "
        f"{v['n_bdg2']} buildings at {v['n_sites']} sites (Building Data Genome 2) and {v['n_uci']} Portuguese "
        "electricity clients, we compare it with pooled, self-only, adaptive, temporal, hierarchical and "
        "quantile-shrinkage conformal calibration and with direct probabilistic forecasters. Pooled conformalised "
        f"quantile regression left {v['main_BDG2_CQR_under_rate']} (BDG2) and {v['main_UCI_CQR_under_rate']} (UCI) of "
        "new buildings with coverage more than five points below the 90 % target; the proposed layer reduced these "
        f"shares to {v['main_BDG2_HSCCQR_recency_under_rate']} and {v['main_UCI_HSCCQR_recency_under_rate']}, the level "
        "expected from sampling noise, with first-week shares falling from "
        f"{v['wk_BDG2_CQR_w1']} to {v['wk_BDG2_HSCCQR_recency_w1']} and from {v['wk_UCI_CQR_w1']} to "
        f"{v['wk_UCI_HSCCQR_recency_w1']}, at an interval score within {v['rec_HSCCQR_recency_is_ratio_BDG2']} of the "
        "pooled baseline. Gains held on unseen sites, after cross-country transfer and under noise, missing data, level "
        "shifts and small calibration pools. Online level control matched window-level reliability only in a narrow "
        "parameter band and not in the first week. In day-ahead capacity-headroom offers, the layer left average cost "
        "unchanged but removed systematically under-protected buildings, at "
        f"{v['time_BDG2_recency_apply_ms']} ms per building-day."
    )
    n = len(a.split())
    assert n <= 250, f"abstract has {n} words (> 250)"
    return a
