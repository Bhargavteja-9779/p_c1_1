"""End-to-end experiment pipeline (one partition seed / fold per call).

Protocol (manuscript Section 5):
  * buildings are split into disjoint sets: model-training (incl. 10 % validation buildings for early
    stopping), calibration (source buildings used only to collect nonconformity scores) and targets
    (newly metered buildings);
  * the forecaster and all calibration scores use the *training period* only (BDG2: 2016,
    UCI: 2012-2013); targets are onboarded at a random date in the *test period* (BDG2: 2017,
    UCI: 2014) and followed for NH = 56 daily forecasts (stage h = 1..56 days of history);
  * every hyper-parameter (kappa, K for HSC; gamma for ACI) is selected by leave-one-building-out on
    the calibration buildings with a pre-specified objective (mean normalised interval score);
    target buildings are never used for any choice.
"""
from __future__ import annotations

import os
import time

import numpy as np
import pandas as pd

from src.preprocessing import features as fe
from src.models import forecasters as fc
from src.models import calibration as cb
from src.evaluation import metrics as mt

NH = 56
KAPPAS = [0, 6, 12, 24, 48, 96, 168, 336, 672, 1344, np.inf]  # 6, 12 added in cycle 2 (grid-edge choices)
KS = [10, 25, 50, 100, None]
RECENCY = 0.95  # per-day decay of own scores (Addendum A, fixed a priori)
KAPPA_S = 24.0  # pseudo-count of the running scale estimate in SSC (Addendum A, fixed a priori)
GAMMAS = [0.0, 0.0001, 0.0002, 0.0005, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05]  # 0.02/0.05 added in cycle 2
IS_TOL = 1.02  # sharpness constraint of the coverage objective (cycle 2): LOBO-IS <= IS_TOL x pooled LOBO-IS


def periods(ds):
    d = ds["dates"]
    if ds["name"] == "BDG2":
        tr = np.where(d.year == 2016)[0]
        te = np.where(d.year == 2017)[0]
    else:
        tr = np.where(d.year <= 2013)[0]
        te = np.where(d.year == 2014)[0]
    return (tr[0], tr[-1]), (te[0], te[-1])


def site_folds(meta, n_folds=5):
    """Deterministic grouping of sites into folds of similar size (largest-first greedy)."""
    sizes = meta.site_id.value_counts()
    folds = [[] for _ in range(n_folds)]
    load = np.zeros(n_folds)
    for site, n in sizes.items():
        i = int(np.argmin(load))
        folds[i].append(site)
        load[i] += n
    return folds


def split(ds, seed, protocol="random", fold=None, frac=(0.5, 0.2, 0.3)):
    rng = np.random.default_rng(1000 + seed)
    n = ds["load"].shape[0]
    if protocol == "random":
        perm = rng.permutation(n)
        a, b = int(frac[0] * n), int((frac[0] + frac[1]) * n)
        tr, cal, tgt = perm[:a], perm[a:b], perm[b:]
    elif protocol == "lso":
        sites = site_folds(ds["meta"])[fold]
        is_t = ds["meta"].site_id.isin(sites).values
        tgt = np.where(is_t)[0]
        rest = rng.permutation(np.where(~is_t)[0])
        a = int(0.7 * len(rest))
        tr, cal = rest[:a], rest[a:]
    else:
        raise ValueError(protocol)
    nv = max(5, int(0.1 * len(tr)))
    return dict(train=np.sort(tr[nv:]), val=np.sort(tr[:nv]), cal=np.sort(cal), tgt=np.sort(tgt))


def sample_training(ds, bidx, period, rng, frac):
    p0, p1 = period
    B, T = [], []
    for b in bidx:
        t = np.arange(p0 + 1, p1 + 1)
        t = t[rng.random(len(t)) < frac]
        B.append(np.full(len(t), b))
        T.append(t)
    B = np.concatenate(B)
    T = np.concatenate(T)
    H = np.array([rng.integers(1, min(fe.H_CAP, t - p0) + 1) for t in T])
    return B, T, H


def build_xy(ds, B, T, H, use_weather):
    X, y, s = fe.build(ds["load"], ds["temp"], ds["dates"], B, T, H, use_weather)
    yn = y / np.repeat(s, 24)
    # training-only artefact filter: normalised targets > 20 arise from meter restarts after
    # near-zero/flat-lined history (data errors), not from consumption behaviour
    ok = ~np.isnan(yn) & (yn <= 20)
    return X[ok], yn[ok]


def train_models(ds, sp, seed, use_weather, alpha=0.1, frac=0.5, with_mlp=True, log=print):
    rng = np.random.default_rng(seed)
    per, _ = periods(ds)
    Xtr, ytr = build_xy(ds, *sample_training(ds, sp["train"], per, rng, frac), use_weather)
    Xv, yv = build_xy(ds, *sample_training(ds, sp["val"], per, rng, 0.5), use_weather)
    log(f"  training rows {len(ytr):,}  validation rows {len(yv):,}")
    m = {}
    t0 = time.time()
    m["lgb"] = fc.fit_lgb(Xtr, ytr, Xv, yv, seed)
    m["lgb_lo"] = fc.fit_lgb(Xtr, ytr, Xv, yv, seed, "quantile", alpha / 2)
    m["lgb_hi"] = fc.fit_lgb(Xtr, ytr, Xv, yv, seed, "quantile", 1 - alpha / 2)
    m["time_lgb"] = time.time() - t0
    # SSC reference scale sigma0 (cycle 2): mean |normalised residual| on validation buildings, which are
    # disjoint from calibration and target buildings, so the studentised score is the same function for all
    m["s0_val"] = float(np.mean(np.abs(yv - m["lgb"].predict(Xv))))
    if with_mlp:
        t0 = time.time()
        m["mlp_g"] = fc.fit_mlp(Xtr, ytr, Xv, yv, seed, kind="gauss")
        m["mlp_q"] = fc.fit_mlp(Xtr, ytr, Xv, yv, seed, kind="quantile", quantiles=(alpha / 2, 1 - alpha / 2))
        m["time_mlp"] = time.time() - t0
    m["use_weather"] = use_weather
    m["n_train_rows"] = len(ytr)
    return m


def onboard_dates(ds, bidx, period, rng, min_valid=0.8):
    """Random onboarding day per building such that >= 80 % of the window's hours are valid.

    Returns -1 for a building without any such window (no fallback; the caller drops it and logs the count)."""
    p0, p1 = period
    starts = np.arange(p0, p1 - NH + 1)
    out = np.empty(len(bidx), dtype=int)
    for i, b in enumerate(bidx):
        v = (~np.isnan(ds["load"][b, p0:p1 + 1])).mean(axis=1)  # valid share per day
        cs = np.concatenate([[0], np.cumsum(v)])
        frac = (cs[starts - p0 + NH + 1] - cs[starts - p0]) / (NH + 1)
        ok = starts[frac >= min_valid]
        out[i] = rng.choice(ok) if len(ok) else -1
    return out


def seasonal_naive(load, B, T, H):
    """Seasonal naive: same hour one week earlier if available (h >= 7), else same hour yesterday."""
    n = len(B)
    out = np.empty((n, 24), dtype=np.float32)
    for i, (b, t, h) in enumerate(zip(B, T, H)):
        if h >= 7:
            out[i] = load[b, t - 7]
            continue
        out[i] = load[b, t - 1]
    return out


def window_predictions(ds, bidx, t0, models, perturb=None):
    """Forecasts for stages h=1..NH of each building's onboarding window starting at t0."""
    load = ds["load"]
    if perturb is not None:
        load = perturb(load.copy(), bidx, t0)
    dsx = dict(ds, load=load)
    n = len(bidx)
    B = np.repeat(bidx, NH)
    H = np.tile(np.arange(1, NH + 1), n)
    T = np.repeat(t0, NH) + H
    X, y, s = fe.build(dsx["load"], dsx["temp"], dsx["dates"], B, T, H, models["use_weather"])
    srep = np.repeat(s, 24)
    out = dict(y=y.reshape(n, NH, 24), s=s.reshape(n, NH), s0_val=models.get("s0_val"))
    t1 = time.time()
    nt_ = int(os.environ.get("OMP_NUM_THREADS", "4"))  # respect single-threaded calibration workers
    out["yhat"] = (models["lgb"].predict(X, num_threads=nt_) * srep).reshape(n, NH, 24)
    out["t_pred_lgb"] = (time.time() - t1) / (n * NH)
    out["qlo"] = (models["lgb_lo"].predict(X, num_threads=nt_) * srep).reshape(n, NH, 24)
    out["qhi"] = (models["lgb_hi"].predict(X, num_threads=nt_) * srep).reshape(n, NH, 24)
    if "mlp_g" in models:
        mu, sd = fc.predict_mlp(models["mlp_g"], X)
        out["mu"] = (mu * srep).reshape(n, NH, 24)
        out["sd"] = (sd * srep).reshape(n, NH, 24)
        qq = fc.predict_mlp(models["mlp_q"], X)
        out["mqlo"] = (qq[:, 0] * srep).reshape(n, NH, 24)
        out["mqhi"] = (qq[:, 1] * srep).reshape(n, NH, 24)
    out["naive"] = seasonal_naive(dsx["load"], B, T, H).reshape(n, NH, 24)
    z = fe.descriptor(dsx["load"], B, T, H)
    out["z"] = z.reshape(n, NH, -1).transpose(1, 0, 2)  # (NH, n, d)
    return out


def scores_abs(P, key="yhat"):
    return np.abs(P["y"] - P[key]) / P["s"][:, :, None]


def scores_cqr(P):
    return np.maximum(P["qlo"] - P["y"], P["y"] - P["qhi"]) / P["s"][:, :, None]


def select(df, objective, ref_mask, tol=IS_TOL):
    """Pick the tuning row. objective 'is': smallest LOBO interval score. 'cov' (cycle 2, applied identically to
    every family): smallest LOBO-MACD among settings whose LOBO-IS <= tol x the family's pooled limit
    (ref_mask rows: kappa = inf, lambda = inf or gamma = 0), ties by IS; if none qualifies, smallest IS."""
    if objective == "is":
        return df.sort_values(["IS", "MACD"]).iloc[0]
    ref = float(df.loc[ref_mask, "IS"].min())
    feas = df[df["IS"] <= tol * ref + 1e-12]
    return (feas if len(feas) else df).sort_values(["MACD", "IS"] if len(feas) else ["IS"]).iloc[0]


def nbrs_by_stage(z_t, z_c, K, exclude_self=False):
    if K is None:
        return None
    return [cb.neighbours(z_t[h], z_c[h], K, exclude_self) for h in range(NH)]


def tune_hsc(cal_scores, cal_base_w, z_cal, alpha, stage_matched=True, Ks=KS, kappas=KAPPAS, objective="is",
             decay=1.0):
    """Leave-one-building-out selection of (kappa, K) on calibration buildings.
    objective: 'is' = mean normalised interval score (pre-registered); 'cov' = mean per-building absolute
    coverage deviation (LOBO-MACD; Addendum A) subject to the sharpness constraint of `select` (cycle 2)."""
    stages = np.arange(1, NH + 1)
    cc = cb.cum_counts(cal_scores)
    binc, _ = cb.bin_cdfs(cc, stages)
    res = []
    for K in Ks:
        nb = nbrs_by_stage(z_cal, z_cal, K, exclude_self=True)
        excl = np.arange(cal_scores.shape[0]) if K is None else None
        q = cb.hsc_quantiles(cc, binc, nb, alpha, kappas, stages, excl=excl, stage_matched=stage_matched,
                             decay=decay)
        isv = cb.normalized_IS(q, cal_scores, cal_base_w, alpha)
        cdv = cb.coverage_deviation(q, cal_scores, alpha)
        for ki, kap in enumerate(kappas):
            res.append(dict(K=K, kappa=kap, IS=float(isv[ki]), MACD=float(cdv[ki])))
    df = pd.DataFrame(res)
    best = select(df, objective, np.isinf(df["kappa"].astype(float)).values)
    return dict(K=None if pd.isna(best.K) else int(best.K), kappa=float(best.kappa)), df


def tune_aci(cal_scores, alpha, gammas=GAMMAS, objective="is", base_w=None):
    stages = np.arange(1, NH + 1)
    cc = cb.cum_counts(cal_scores)
    binc, _ = cb.bin_cdfs(cc, stages)
    tot = binc.sum(axis=0)
    prior = tot[None] - binc  # leave-one-building-out pooled prior per pseudo-target
    res = []
    for g in gammas:
        q = cb.aci_quantiles(cal_scores, prior, alpha, g, stages)
        isv = float(cb.normalized_IS(q[None], cal_scores, np.zeros_like(cal_scores) if base_w is None else base_w,
                                     alpha)[0])
        cdv = float(cb.coverage_deviation(q[None], cal_scores, alpha)[0])
        res.append(dict(gamma=g, IS=isv, MACD=cdv))
    df = pd.DataFrame(res)
    return float(select(df, objective, (df["gamma"] == 0).values)["gamma"]), df


def tune_qshrink(cal_scores, cal_base_w, alpha, lams=tuple(KAPPAS), objective="is", decay=1.0):
    """Leave-one-building-out choice of lambda for quantile-level shrinkage (same objective and grid as HSC;
    lambda = 0: own quantile when defined, lambda = inf: pooled radius)."""
    stages = np.arange(1, NH + 1)
    cc = cb.cum_counts(cal_scores)
    binc, _ = cb.bin_cdfs(cc, stages)
    q_pool = cb.pooled_quantile_lobo(binc, alpha)[:, cb.stage_bin(stages)]  # (ncal, NH), score-weighted
    res = []
    for lam in lams:
        q = cb.qshrink_quantiles(cc, q_pool, alpha, lam, stages, decay=decay)
        isv = float(cb.normalized_IS(q[None], cal_scores, cal_base_w, alpha)[0])
        cdv = float(cb.coverage_deviation(q[None], cal_scores, alpha)[0])
        res.append(dict(lam=lam, IS=isv, MACD=cdv))
    df = pd.DataFrame(res)
    return float(select(df, objective, np.isinf(df["lam"].astype(float)).values)["lam"]), df


def run_calibration(PC, PT, alpha, meta_cal=None, meta_tgt=None, methods="all", fixed=None, log=print):
    """Compute (lo, hi) for every interval method on the targets. Returns dict name->(lo,hi), info."""
    stages = np.arange(1, NH + 1)
    out, info = {}, {}
    zt, zc = PT["z"], PC["z"]
    # ---- scores
    Sc, St = scores_abs(PC), scores_abs(PT)
    cc_c, cc_t = cb.cum_counts(Sc), cb.cum_counts(St)
    binc, _ = cb.bin_cdfs(cc_c, stages)
    sb = cb.stage_bin(stages)
    yh, s = PT["yhat"], PT["s"][:, :, None]

    def band(q, center=yh, lo=None, hi=None):
        q = np.asarray(q)
        if q.ndim == 1:  # per stage-bin radius
            q = np.broadcast_to(q[sb], PT["s"].shape)
        lo = center if lo is None else lo
        hi = center if hi is None else hi
        return lo - q[:, :, None] * s, hi + q[:, :, None] * s

    t0 = time.time()
    # 1 classical: seasonal naive + stage-matched split conformal
    Snc = scores_abs(PC, "naive")
    q = cb.pooled_quantile(cb.bin_cdfs(cb.cum_counts(Snc), stages)[0], alpha, True)
    out["Naive+SCP"] = band(q, center=PT["naive"])
    # 2 raw (unnormalised) pooled conformal
    r = np.abs(PC["y"] - PC["yhat"]).ravel()
    r = np.sort(r[~np.isnan(r)])
    k = int(np.ceil((1 - alpha) * (len(r) + 1))) - 1
    qr = r[min(k, len(r) - 1)]
    out["Raw-SCP"] = (yh - qr, yh + qr)
    # 3 pooled normalised SCP (stage-agnostic) and 4 stage-matched
    out["SCP"] = band(cb.pooled_quantile(binc, alpha, stage_matched=False))
    out["SCP-stage"] = band(cb.pooled_quantile(binc, alpha, stage_matched=True))
    info["t_scp"] = time.time() - t0
    # 5 Mondrian by usage (BDG2 metadata)
    if meta_cal is not None and meta_cal.usage.nunique() > 1:
        lo, hi = out["SCP-stage"][0].copy(), out["SCP-stage"][1].copy()
        for u in np.unique(meta_tgt.usage.values):
            mc = (meta_cal.usage.values == u)
            if mc.sum() < 10:
                continue
            q = cb.pooled_quantile(binc, alpha, True, weights=mc.astype(float))
            mtg = meta_tgt.usage.values == u
            l2, h2 = band(q)
            lo[mtg], hi[mtg] = l2[mtg], h2[mtg]
        out["Mondrian-usage"] = (lo, hi)
    # 6 self-only conformal with fallback to SCP-stage until enough own scores exist
    q_self = cb.hsc_quantiles(cc_t, binc, None, alpha, [0], stages)[0]
    q_fb = cb.pooled_quantile(binc, alpha, True)[sb]
    q_self = np.where(cb.own_defined(cb.own_counts_before(cc_t), alpha), q_self, q_fb[None, :])
    out["Self-CP"] = band(q_self)
    # 7 ACI
    g, gdf = tune_aci(Sc, alpha) if fixed is None else (fixed["gamma"], None)
    info["aci_gamma"] = g
    if gdf is not None:
        info["tune_aci"] = gdf.to_dict(orient="records")
    qa, info["aci_capped_frac"] = cb.aci_quantiles(St, binc.sum(axis=0), alpha, g, stages, return_capped=True)
    out["ACI"] = band(qa)
    # 8 direct quantile regression and 9 CQR
    out["QR-LGBM"] = (PT["qlo"], PT["qhi"])
    Scq, Stq = scores_cqr(PC), scores_cqr(PT)
    bincq, _ = cb.bin_cdfs(cb.cum_counts(Scq), stages)
    out["CQR"] = band(cb.pooled_quantile(bincq, alpha, True), lo=PT["qlo"], hi=PT["qhi"])
    # 10-11 deep probabilistic baselines
    if "mu" in PT:
        from scipy.stats import norm
        z = norm.ppf(1 - alpha / 2)
        out["MLP-Gauss"] = (PT["mu"] - z * PT["sd"], PT["mu"] + z * PT["sd"])
        out["MLP-QR"] = (PT["mqlo"], PT["mqhi"])
    # 12 proposed HSC (abs score) and ablations
    t0 = time.time()
    if fixed is None:
        best, tdf = tune_hsc(Sc, np.zeros_like(Sc), zc, alpha)
    else:
        best, tdf = fixed["hsc"], None
    info["hsc_K"], info["hsc_kappa"] = best["K"], best["kappa"]
    info["t_tune_hsc"] = time.time() - t0
    t0 = time.time()
    nb = nbrs_by_stage(zt, zc, best["K"])
    q = cb.hsc_quantiles(cc_t, binc, nb, alpha, [best["kappa"]], stages)[0]
    info["t_hsc_apply_per_target_day"] = (time.time() - t0) / (St.shape[0] * NH)
    info["hsc_store_MB"] = binc.astype(np.float32).nbytes / 1e6 + zc.nbytes / 1e6  # score CDFs + descriptors
    out["HSC"] = band(q)
    info["tune_table"] = tdf
    # 13 HSC applied to CQR scores (proposed variant)
    bq, tq_tab = tune_hsc(Scq, PC["qhi"] / PC["s"][:, :, None] - PC["qlo"] / PC["s"][:, :, None], zc, alpha)
    info["tune_hsc_cqr"] = tq_tab.replace({np.inf: "inf"}).to_dict(orient="records")
    qq = cb.hsc_quantiles(cb.cum_counts(Stq), bincq, nbrs_by_stage(zt, zc, bq["K"]), alpha, [bq["kappa"]],
                          stages)[0]
    out["HSC-CQR"] = band(qq, lo=PT["qlo"], hi=PT["qhi"])
    info["hsc_cqr"] = bq
    # same-score competitors for HSC-CQR: self-only CQR (fallback to pooled CQR) and ACI on CQR scores
    cct_q = cb.cum_counts(Stq)
    q_sq = cb.hsc_quantiles(cct_q, bincq, None, alpha, [0], stages)[0]
    q_fbq = cb.pooled_quantile(bincq, alpha, True)[sb]
    q_sq = np.where(cb.own_defined(cb.own_counts_before(cct_q), alpha), q_sq, q_fbq[None, :])
    out["Self-CQR"] = band(q_sq, lo=PT["qlo"], hi=PT["qhi"])
    bwq_cal = PC["qhi"] / PC["s"][:, :, None] - PC["qlo"] / PC["s"][:, :, None]
    gq, gq_tab = tune_aci(Scq, alpha, base_w=bwq_cal) if fixed is None else (fixed["gamma"], None)
    info["aci_cqr_gamma"] = gq
    if gq_tab is not None:
        info["tune_aci_cqr"] = gq_tab.to_dict(orient="records")
    qa, info["aci_cqr_capped_frac"] = cb.aci_quantiles(Stq, bincq.sum(axis=0), alpha, gq, stages, return_capped=True)
    out["ACI-CQR"] = band(qa, lo=PT["qlo"], hi=PT["qhi"])
    # closest prior-art mechanisms, on the same CQR scores (see calibration.py docstrings)
    bwq_cal = PC["qhi"] / PC["s"][:, :, None] - PC["qlo"] / PC["s"][:, :, None]
    tot_all_q = bincq.sum(axis=1)
    n_sur = float(np.median(tot_all_q[:, -1]))
    out["GHCP-CQR"] = band(cb.ghcp_quantiles(cct_q, tot_all_q, alpha, stages, n_sur), lo=PT["qlo"], hi=PT["qhi"])
    lam, lam_tab = tune_qshrink(Scq, bwq_cal, alpha)
    info["qshrink_lambda"] = lam
    info["tune_qshrink"] = lam_tab.replace({np.inf: "inf"}).to_dict(orient="records")
    out["QShrink-CQR"] = band(cb.qshrink_quantiles(cct_q, cb.pooled_quantile(bincq, alpha, True)[sb], alpha, lam,
                                                   stages), lo=PT["qlo"], hi=PT["qhi"])
    out["TQA-B-CQR"] = band(cb.tqab_quantiles(Stq, Scq, bincq.sum(axis=0), alpha, stages), lo=PT["qlo"],
                            hi=PT["qhi"])
    # recommended simplest variant: uniform prior (K = all), no stage matching, kappa by LOBO
    bs, bs_tab = tune_hsc(Scq, bwq_cal, zc, alpha, stage_matched=False, Ks=[None])
    info["hsc_cqr_simple"] = bs
    info["tune_hsc_cqr_simple"] = bs_tab.replace({np.inf: "inf"}).to_dict(orient="records")
    # fixed pseudo-count (one week of hourly scores), i.e. a donor-local mixture with fixed kappa
    out["HSC-CQR fixed-κ"] = band(cb.hsc_quantiles(cct_q, bincq, None, alpha, [168], stages,
                                                   stage_matched=False)[0], lo=PT["qlo"], hi=PT["qhi"])
    out["HSC-CQR simple"] = band(cb.hsc_quantiles(cct_q, bincq, None, alpha, [bs["kappa"]], stages,
                                                  stage_matched=False)[0], lo=PT["qlo"], hi=PT["qhi"])
    bsa, _ = tune_hsc(Sc, np.zeros_like(Sc), zc, alpha, stage_matched=False, Ks=[None])
    info["hsc_simple"] = bsa
    out["HSC simple"] = band(cb.hsc_quantiles(cc_t, binc, None, alpha, [bsa["kappa"]], stages,
                                              stage_matched=False)[0])
    # ---- review-cycle-1 additions (PREREGISTRATION Addendum A)
    t0 = time.time()
    # H-A: per-building-coverage (LOBO-MACD) tuning objective, applied alike to HSC, QShrink and ACI
    bc, bc_tab = tune_hsc(Scq, bwq_cal, zc, alpha, stage_matched=False, Ks=[None], objective="cov")
    info["hsc_cqr_simple_cov"] = bc
    info["tune_hsc_cqr_simple_cov"] = bc_tab.replace({np.inf: "inf"}).to_dict(orient="records")
    out["HSC-CQR simple (cov)"] = band(cb.hsc_quantiles(cct_q, bincq, None, alpha, [bc["kappa"]], stages,
                                                        stage_matched=False)[0], lo=PT["qlo"], hi=PT["qhi"])
    info["t_tune_hsc_cov"] = time.time() - t0
    lamc, _ = tune_qshrink(Scq, bwq_cal, alpha, objective="cov")
    info["qshrink_lambda_cov"] = lamc
    out["QShrink-CQR (cov)"] = band(cb.qshrink_quantiles(cct_q, cb.pooled_quantile(bincq, alpha, True)[sb], alpha,
                                                         lamc, stages), lo=PT["qlo"], hi=PT["qhi"])
    gqc, gqc_tab = tune_aci(Scq, alpha, objective="cov", base_w=bwq_cal) if fixed is None else (fixed["gamma"], None)
    info["aci_cqr_gamma_cov"] = gqc
    if gqc_tab is not None:
        info["tune_aci_cqr_cov"] = gqc_tab.to_dict(orient="records")
    out["ACI-CQR (cov)"] = band(cb.aci_quantiles(Stq, bincq.sum(axis=0), alpha, gqc, stages), lo=PT["qlo"],
                                hi=PT["qhi"])
    # H-C: recency-weighted own scores (0.95 per day), kappa by LOBO-MACD
    br, _ = tune_hsc(Scq, bwq_cal, zc, alpha, stage_matched=False, Ks=[None], objective="cov", decay=RECENCY)
    info["hsc_cqr_recency"] = br
    q_rec = cb.hsc_quantiles(cct_q, bincq, None, alpha, [br["kappa"]], stages, stage_matched=False,
                             decay=RECENCY)[0]
    out["HSC-CQR recency"] = band(q_rec, lo=PT["qlo"], hi=PT["qhi"])
    # ---- review-cycle-2 additions (REVIEW/review_02.md)
    # kappa -> inf limit of the same (building-weighted, stage-agnostic) variant (#12)
    out["HSC-CQR recency κ=∞"] = band(cb.hsc_quantiles(cct_q, bincq, None, alpha, [np.inf], stages,
                                                       stage_matched=False)[0], lo=PT["qlo"], hi=PT["qhi"])
    # recency for the other own-score families, same constrained objective (#8)
    lamr, lamr_tab = tune_qshrink(Scq, bwq_cal, alpha, objective="cov", decay=RECENCY)
    info["qshrink_lambda_recency"] = lamr
    info["tune_qshrink_recency"] = lamr_tab.replace({np.inf: "inf"}).to_dict(orient="records")
    out["QShrink-CQR recency"] = band(cb.qshrink_quantiles(cct_q, q_fbq[None, :], alpha, lamr, stages,
                                                           decay=RECENCY), lo=PT["qlo"], hi=PT["qhi"])
    q_sr = cb.hsc_quantiles(cct_q, bincq, None, alpha, [0], stages, decay=RECENCY)[0]
    q_sr = np.where(cb.own_defined(cb.own_counts_before(cct_q, RECENCY), alpha), q_sr, q_fbq[None, :])
    out["Self-CQR recency"] = band(q_sr, lo=PT["qlo"], hi=PT["qhi"])
    # radius safeguard (#6): never wider than the pooled radius at level 1 - alpha/10
    q_cap = cb.pooled_quantile(bincq, alpha / 10, True)[sb]
    info["recency_capped_share"] = float(np.mean(q_rec > q_cap[None, :]))
    out["HSC-CQR recency (capped)"] = band(np.minimum(q_rec, q_cap[None, :]), lo=PT["qlo"], hi=PT["qhi"])
    # data-latency variants (#4): own scores / feedback delayed by one day, parameters as tuned above
    cct_d = cb.delay_counts(cct_q, 1)
    out["HSC-CQR recency (delay 1d)"] = band(cb.hsc_quantiles(cct_d, bincq, None, alpha, [br["kappa"]], stages,
                                                              stage_matched=False, decay=RECENCY)[0],
                                             lo=PT["qlo"], hi=PT["qhi"])
    out["QShrink-CQR (cov, delay 1d)"] = band(cb.qshrink_quantiles(cct_d, q_fbq[None, :], alpha, lamc, stages),
                                              lo=PT["qlo"], hi=PT["qhi"])
    out["ACI-CQR (cov, delay 1d)"] = band(cb.aci_quantiles(Stq, bincq.sum(axis=0), alpha, gqc, stages, delay=1),
                                          lo=PT["qlo"], hi=PT["qhi"])
    # grid-edge reporting (#2)
    info["grid_edge"] = dict(
        hsc_recency_kappa=bool(br["kappa"] in (min(k for k in KAPPAS if k > 0), max(k for k in KAPPAS if np.isfinite(k)))),
        aci_cqr_gamma_cov=bool(gqc in (max(GAMMAS),)), qshrink_lambda_cov=bool(lamc in (6, 1344)))
    # H-B: stage-wise studentised conformal (SSC-CQR) and its combination with shrinkage
    t0 = time.time()
    mabs_c = np.nanmean(Sc.reshape(Sc.shape[0], -1), axis=1)  # per calibration building mean |res|/s
    M = len(mabs_c)
    s0_all = float(np.nanmean(mabs_c))
    # cycle 2: one fixed sigma0 for calibration and target buildings alike, estimated on validation buildings
    # (disjoint from both); falls back to the calibration mean only for caches without s0_val
    s0 = PC.get("s0_val") if PC.get("s0_val") is not None else s0_all
    info["ssc_sigma0_source"] = "validation" if PC.get("s0_val") is not None else "calibration"
    r_c = cb.running_scale_ratio(Sc, s0, KAPPA_S)
    r_t = cb.running_scale_ratio(St, s0, KAPPA_S)
    Zc, Zt = Scq / r_c[:, :, None], Stq / r_t[:, :, None]
    q_ssc = cb.ssc_quantiles(Zc, alpha, St.shape[0])
    rq = r_t[:, :, None] * s
    out["SSC-CQR"] = (PT["qlo"] - q_ssc[:, :, None] * rq, PT["qhi"] + q_ssc[:, :, None] * rq)
    info["t_ssc_apply_per_target_day"] = (time.time() - t0) / (St.shape[0] * NH)
    info["ssc_sigma0"] = s0
    bwz = bwq_cal / r_c[:, :, None]
    bz, _ = tune_hsc(Zc, bwz, zc, alpha, stage_matched=False, Ks=[None], objective="cov")
    info["hsc_ssc_cqr"] = bz
    q_hz = cb.hsc_quantiles(cb.cum_counts(Zt), cb.bin_cdfs(cb.cum_counts(Zc), stages)[0], None, alpha,
                            [bz["kappa"]], stages, stage_matched=False)[0]
    out["HSC-SSC-CQR"] = (PT["qlo"] - q_hz[:, :, None] * rq, PT["qhi"] + q_hz[:, :, None] * rq)
    # model-agnostic check: the same layer on the MLP quantile model
    if "mqlo" in PT and "mqlo" in PC:
        Scm = np.maximum(PC["mqlo"] - PC["y"], PC["y"] - PC["mqhi"]) / PC["s"][:, :, None]
        Stm = np.maximum(PT["mqlo"] - PT["y"], PT["y"] - PT["mqhi"]) / PT["s"][:, :, None]
        bincm, _ = cb.bin_cdfs(cb.cum_counts(Scm), stages)
        out["CQR (MLP)"] = band(cb.pooled_quantile(bincm, alpha, True), lo=PT["mqlo"], hi=PT["mqhi"])
        bm, _ = tune_hsc(Scm, PC["mqhi"] / PC["s"][:, :, None] - PC["mqlo"] / PC["s"][:, :, None], zc, alpha,
                         stage_matched=False, Ks=[None])
        info["hsc_cqr_mlp"] = bm
        # the recommended configuration (recency, constrained coverage objective) on the MLP quantiles (#17)
        bmr, _ = tune_hsc(Scm, PC["mqhi"] / PC["s"][:, :, None] - PC["mqlo"] / PC["s"][:, :, None], zc, alpha,
                          stage_matched=False, Ks=[None], objective="cov", decay=RECENCY)
        info["hsc_cqr_recency_mlp"] = bmr
        out["HSC-CQR recency (MLP)"] = band(cb.hsc_quantiles(cb.cum_counts(Stm), bincm, None, alpha, [bmr["kappa"]],
                                                             stages, stage_matched=False, decay=RECENCY)[0],
                                            lo=PT["mqlo"], hi=PT["mqhi"])
        out["HSC-CQR (MLP)"] = band(cb.hsc_quantiles(cb.cum_counts(Stm), bincm, None, alpha, [bm["kappa"]], stages,
                                                     stage_matched=False)[0], lo=PT["mqlo"], hi=PT["mqhi"])
    if methods == "all":
        # ablations (each re-tuned on calibration buildings with the component removed)
        b2, _ = tune_hsc(Sc, np.zeros_like(Sc), zc, alpha, stage_matched=False)
        q = cb.hsc_quantiles(cc_t, binc, nbrs_by_stage(zt, zc, b2["K"]), alpha, [b2["kappa"]], stages,
                             stage_matched=False)[0]
        out["HSC -stage"] = band(q)
        b3, _ = tune_hsc(Sc, np.zeros_like(Sc), zc, alpha, Ks=[None])
        out["HSC -kNN"] = band(cb.hsc_quantiles(cc_t, binc, None, alpha, [b3["kappa"]], stages)[0])
        b4, _ = tune_hsc(Sc, np.zeros_like(Sc), zc, alpha, kappas=[np.inf])
        out["HSC -shrink"] = band(cb.hsc_quantiles(cc_t, binc, nbrs_by_stage(zt, zc, b4["K"]), alpha,
                                                   [np.inf], stages)[0])
        info["ablation_params"] = dict(nostage=b2, noknn=b3, noshrink=b4)
        # ablations of the CQR-score variant
        bwq = PC["qhi"] / PC["s"][:, :, None] - PC["qlo"] / PC["s"][:, :, None]
        c2, _ = tune_hsc(Scq, bwq, zc, alpha, stage_matched=False)
        out["HSC-CQR -stage"] = band(cb.hsc_quantiles(cct_q, bincq, nbrs_by_stage(zt, zc, c2["K"]), alpha,
                                                      [c2["kappa"]], stages, stage_matched=False)[0],
                                     lo=PT["qlo"], hi=PT["qhi"])
        c3, _ = tune_hsc(Scq, bwq, zc, alpha, Ks=[None])
        out["HSC-CQR -kNN"] = band(cb.hsc_quantiles(cct_q, bincq, None, alpha, [c3["kappa"]], stages)[0],
                                   lo=PT["qlo"], hi=PT["qhi"])
        c4, _ = tune_hsc(Scq, bwq, zc, alpha, kappas=[np.inf])
        out["HSC-CQR -shrink"] = band(cb.hsc_quantiles(cct_q, bincq, nbrs_by_stage(zt, zc, c4["K"]), alpha,
                                                       [np.inf], stages)[0], lo=PT["qlo"], hi=PT["qhi"])
        info["ablation_params_cqr"] = dict(nostage=c2, noknn=c3, noshrink=c4)
    return out, info


def common_mask(out, PT):
    """Hours evaluated: truth observed AND every method issued a finite interval (a forecast cannot be
    issued when the building's whole scale window is missing; such hours are excluded for all methods)."""
    ok = ~np.isnan(PT["y"])
    for lo, hi in out.values():
        ok &= np.isfinite(lo) & np.isfinite(hi)
    return ok


def evaluate(out, PT, alpha):
    rows, curves = [], {}
    ok = common_mask(out, PT)
    y = np.where(ok, PT["y"], np.nan)
    for name, (lo, hi) in out.items():
        m, sc, sis = mt.interval_metrics(y, lo, hi, alpha)
        curves[name] = (sc.mean(axis=0), sis.mean(axis=0), np.median(sis, axis=0))
        rows.append(pd.DataFrame(dict(method=name, **m)))
    return pd.concat(rows, ignore_index=True), curves
