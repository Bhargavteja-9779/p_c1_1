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
KAPPAS = [0, 24, 48, 96, 168, 336, 672, 1344, np.inf]
KS = [10, 25, 50, 100, None]
GAMMAS = [0.0, 0.0001, 0.0002, 0.0005, 0.001, 0.002, 0.005, 0.01]  # 0 and 1e-4/2e-4 added after audit


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
    elif protocol == "loso":  # v2: leave-one-SITE-out; fold = site index (sorted site names)
        sites = sorted(ds["meta"].site_id.unique())
        is_t = (ds["meta"].site_id == sites[fold]).values
        tgt = np.where(is_t)[0]
        rest = rng.permutation(np.where(~is_t)[0])
        a = int(0.7 * len(rest))
        tr, cal = rest[:a], rest[a:]
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


def train_models(ds, sp, seed, use_weather, alpha=0.1, frac=0.5, with_mlp=True, log=print, period=None):
    rng = np.random.default_rng(seed)
    per = periods(ds)[0] if period is None else period
    Xtr, ytr = build_xy(ds, *sample_training(ds, sp["train"], per, rng, frac), use_weather)
    Xv, yv = build_xy(ds, *sample_training(ds, sp["val"], per, rng, 0.5), use_weather)
    log(f"  training rows {len(ytr):,}  validation rows {len(yv):,}")
    m = {}
    t0 = time.time()
    m["lgb"] = fc.fit_lgb(Xtr, ytr, Xv, yv, seed)
    m["lgb_lo"] = fc.fit_lgb(Xtr, ytr, Xv, yv, seed, "quantile", alpha / 2)
    m["lgb_hi"] = fc.fit_lgb(Xtr, ytr, Xv, yv, seed, "quantile", 1 - alpha / 2)
    m["time_lgb"] = time.time() - t0
    if with_mlp:
        t0 = time.time()
        m["mlp_g"] = fc.fit_mlp(Xtr, ytr, Xv, yv, seed, kind="gauss")
        m["mlp_q"] = fc.fit_mlp(Xtr, ytr, Xv, yv, seed, kind="quantile", quantiles=(alpha / 2, 1 - alpha / 2))
        m["time_mlp"] = time.time() - t0
    m["use_weather"] = use_weather
    m["n_train_rows"] = len(ytr)
    return m


def onboard_dates(ds, bidx, period, rng, min_valid=0.8):
    """Random onboarding day per building such that >= 80 % of the window's hours are valid."""
    p0, p1 = period
    starts = np.arange(p0, p1 - NH + 1)
    out = np.empty(len(bidx), dtype=int)
    for i, b in enumerate(bidx):
        v = (~np.isnan(ds["load"][b, p0:p1 + 1])).mean(axis=1)  # valid share per day
        cs = np.concatenate([[0], np.cumsum(v)])
        frac = (cs[starts - p0 + NH + 1] - cs[starts - p0]) / (NH + 1)
        ok = starts[frac >= min_valid]
        if not len(ok):
            ONBOARD_FALLBACKS.append(int(b))
        out[i] = rng.choice(ok) if len(ok) else rng.choice(starts)
    return out


ONBOARD_FALLBACKS: list = []  # buildings without any window with >= 80 % valid hours (logged per run)


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
    if "obs" in ds:  # (v2) score only actually observed hours (interpolated/masked hours are history only)
        y = np.where(ds["obs"][B, T, :].ravel(), y, np.nan)
    out = dict(y=y.reshape(n, NH, 24), s=s.reshape(n, NH))
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


def nbrs_by_stage(z_t, z_c, K, exclude_self=False):
    if K is None:
        return None
    return [cb.neighbours(z_t[h], z_c[h], K, exclude_self) for h in range(NH)]


IS_TOL = 0.02  # v2: admissible relative loss in LOBO interval score for the reliability-aware objective


def _select(df, objective):
    """LOBO selection rule on calibration buildings.
    'IS'   : minimum mean normalised interval score (pre-registered objective);
    'MACD' : minimum mean absolute coverage deviation of the pseudo-targets, unconstrained (reference only:
             it can buy coverage with much wider, erratic intervals, e.g. ACI with large steps);
    'MACDc': (v2 default) minimum MACD among grid values whose LOBO interval score is within IS_TOL of the
             minimum, i.e. the most reliable setting without a material sharpness loss. Ties -> lower IS."""
    if objective == "IS":
        return df.loc[df.obj.idxmin()]
    d = df if objective == "MACD" else df[df.obj <= df.obj.min() * (1 + IS_TOL) + 1e-12]
    m = d.macd.min()
    return d[d.macd <= m + 1e-9].sort_values("obj").iloc[0]


def tune_hsc(cal_scores, cal_base_w, z_cal, alpha, stage_matched=True, Ks=KS, kappas=KAPPAS, objective="IS",
             groups=None):
    """Leave-one-building-out selection of (kappa, K) on calibration buildings. Both objectives are stored;
    `objective` decides. groups: optional site labels -> leave-one-group-out (uniform prior only)."""
    stages = np.arange(1, NH + 1)
    cc = cb.cum_counts(cal_scores)
    binc, _ = cb.bin_cdfs(cc, stages)
    res = []
    for K in Ks:
        nb = nbrs_by_stage(z_cal, z_cal, K, exclude_self=True)
        excl = np.arange(cal_scores.shape[0]) if K is None else None
        q = cb.hsc_quantiles(cc, binc, nb, alpha, kappas, stages, excl=excl, stage_matched=stage_matched,
                             groups=groups if K is None else None)
        obj = cb.normalized_IS(q, cal_scores, cal_base_w, alpha)
        macd, under = cb.coverage_objective(q, cal_scores, alpha)
        for ki, kap in enumerate(kappas):
            res.append(dict(K=K, kappa=kap, obj=float(obj[ki]), macd=float(macd[ki]), under=float(under[ki])))
    df = pd.DataFrame(res)
    best = _select(df, objective)
    return dict(K=None if pd.isna(best.K) else int(best.K), kappa=float(best.kappa)), df


def tune_aci(cal_scores, alpha, gammas=GAMMAS, objective="IS"):
    stages = np.arange(1, NH + 1)
    cc = cb.cum_counts(cal_scores)
    binc, _ = cb.bin_cdfs(cc, stages)
    tot = binc.sum(axis=0)
    prior = tot[None] - binc  # leave-one-building-out pooled prior per pseudo-target
    res = []
    for g in gammas:
        q = cb.aci_quantiles(cal_scores, prior, alpha, g, stages)
        obj = cb.normalized_IS(q[None], cal_scores, np.zeros_like(cal_scores), alpha)
        macd, under = cb.coverage_objective(q[None], cal_scores, alpha)
        res.append(dict(gamma=g, obj=float(obj[0]), macd=float(macd[0]), under=float(under[0])))
    df = pd.DataFrame(res)
    return float(_select(df, objective).gamma), df


def tune_qshrink(cal_scores, cal_base_w, alpha, lams=tuple(KAPPAS), objective="IS"):
    """Leave-one-building-out choice of lambda for quantile-level shrinkage (same objective and grid as HSC;
    lambda = 0: own quantile when defined, lambda = inf: pooled radius)."""
    stages = np.arange(1, NH + 1)
    cc = cb.cum_counts(cal_scores)
    binc, _ = cb.bin_cdfs(cc, stages)
    q_pool = cb.pooled_quantile_lobo(binc, alpha)[:, cb.stage_bin(stages)]  # (ncal, NH), score-weighted
    res = []
    for lam in lams:
        q = cb.qshrink_quantiles(cc, q_pool, alpha, lam, stages)
        macd, under = cb.coverage_objective(q[None], cal_scores, alpha)
        res.append(dict(lam=lam, obj=float(cb.normalized_IS(q[None], cal_scores, cal_base_w, alpha)[0]),
                        macd=float(macd[0]), under=float(under[0])))
    df = pd.DataFrame(res)
    return float(_select(df, objective).lam), df


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
    out["ACI"] = band(cb.aci_quantiles(St, binc.sum(axis=0), alpha, g, stages))
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
    # 12 HSC (abs score; pre-registered configuration: kNN prior + stage matching, IS-tuned)
    light = methods == "light"  # v2: skip the kNN-tuned HSC variants (small-pool resampling runs)
    t0 = time.time()
    if light:
        tdf = None
    elif fixed is None:
        best, tdf = tune_hsc(Sc, np.zeros_like(Sc), zc, alpha)
    else:
        best, tdf = fixed["hsc"], None
    if not light:
        info["hsc_K"], info["hsc_kappa"] = best["K"], best["kappa"]
        info["t_tune_hsc"] = time.time() - t0
        t0 = time.time()
        nb = nbrs_by_stage(zt, zc, best["K"])
        q = cb.hsc_quantiles(cc_t, binc, nb, alpha, [best["kappa"]], stages)[0]
        info["t_hsc_apply_per_target_day"] = (time.time() - t0) / (St.shape[0] * NH)
        info["hsc_store_MB"] = binc.astype(np.float32).nbytes / 1e6 + zc.nbytes / 1e6  # score CDFs + descriptors
        out["HSC"] = band(q)
    info["tune_table"] = tdf
    T = info.setdefault("t_method", {})  # v2: wall-clock seconds per strategy (tuning + application)
    bwq_cal = PC["qhi"] / PC["s"][:, :, None] - PC["qlo"] / PC["s"][:, :, None]
    t0 = time.time()
    cct_q = cb.cum_counts(Stq)
    T["own-score histograms (CQR)"] = time.time() - t0
    # 13 HSC on CQR scores: kNN prior + stage matching, IS-tuned (pre-registered variant configuration)
    t0 = time.time()
    if not light:
        bq, tq_tab = tune_hsc(Scq, bwq_cal, zc, alpha)
        info["tune_hsc_cqr"] = tq_tab.replace({np.inf: "inf"}).to_dict(orient="records")
        qq = cb.hsc_quantiles(cct_q, bincq, nbrs_by_stage(zt, zc, bq["K"]), alpha, [bq["kappa"]], stages)[0]
        out["HSC-CQR"] = band(qq, lo=PT["qlo"], hi=PT["qhi"])
        info["hsc_cqr"] = bq
        T["HSC-CQR"] = time.time() - t0
    # same-score competitors: self-only CQR (fallback to pooled CQR) and ACI on CQR scores
    t0 = time.time()
    q_sq = cb.hsc_quantiles(cct_q, bincq, None, alpha, [0], stages)[0]
    q_fbq = cb.pooled_quantile(bincq, alpha, True)[sb]
    q_sq = np.where(cb.own_defined(cb.own_counts_before(cct_q), alpha), q_sq, q_fbq[None, :])
    out["Self-CQR"] = band(q_sq, lo=PT["qlo"], hi=PT["qhi"])
    T["Self-CQR"] = time.time() - t0
    t0 = time.time()
    gq, gq_tab = tune_aci(Scq, alpha) if fixed is None else (fixed["gamma"], None)
    info["aci_cqr_gamma"] = gq
    out["ACI-CQR"] = band(cb.aci_quantiles(Stq, bincq.sum(axis=0), alpha, gq, stages), lo=PT["qlo"], hi=PT["qhi"])
    T["ACI-CQR"] = time.time() - t0
    if gq_tab is not None:
        info["tune_aci_cqr"] = gq_tab.to_dict(orient="records")
        gqc = float(_select(gq_tab, "MACDc").gamma)
        info["aci_cqr_gamma_macdc"] = gqc
        out["ACI-CQR (MACD)"] = band(cb.aci_quantiles(Stq, bincq.sum(axis=0), alpha, gqc, stages),
                                     lo=PT["qlo"], hi=PT["qhi"])
        gqu = float(_select(gq_tab, "MACD").gamma)
        info["aci_cqr_gamma_cov"] = gqu
        out["ACI-CQR (coverage only)"] = band(cb.aci_quantiles(Stq, bincq.sum(axis=0), alpha, gqu, stages),
                                              lo=PT["qlo"], hi=PT["qhi"])
    # closest prior-art mechanisms, on the same CQR scores (see calibration.py docstrings)
    t0 = time.time()
    tot_all_q = bincq.sum(axis=1)
    n_sur = float(np.median(tot_all_q[:, -1]))
    out["GHCP-CQR"] = band(cb.ghcp_quantiles(cct_q, tot_all_q, alpha, stages, n_sur), lo=PT["qlo"], hi=PT["qhi"])
    T["GHCP-CQR"] = time.time() - t0
    t0 = time.time()
    lam, lam_tab = tune_qshrink(Scq, bwq_cal, alpha)
    info["qshrink_lambda"] = lam
    info["tune_qshrink"] = lam_tab.replace({np.inf: "inf"}).to_dict(orient="records")
    qpool_t = cb.pooled_quantile(bincq, alpha, True)[sb]
    out["QShrink-CQR"] = band(cb.qshrink_quantiles(cct_q, qpool_t, alpha, lam, stages), lo=PT["qlo"], hi=PT["qhi"])
    T["QShrink-CQR"] = time.time() - t0
    lam_m = float(_select(lam_tab, "MACDc").lam)
    info["qshrink_lambda_macd"] = lam_m
    out["QShrink-CQR (MACD)"] = band(cb.qshrink_quantiles(cct_q, qpool_t, alpha, lam_m, stages), lo=PT["qlo"],
                                     hi=PT["qhi"])
    out["QShrink-CQR λ=168"] = band(cb.qshrink_quantiles(cct_q, qpool_t, alpha, 168, stages), lo=PT["qlo"],
                                    hi=PT["qhi"])
    t0 = time.time()
    out["TQA-B-CQR"] = band(cb.tqab_quantiles(Stq, Scq, bincq.sum(axis=0), alpha, stages), lo=PT["qlo"],
                            hi=PT["qhi"])
    T["TQA-B-CQR"] = time.time() - t0
    # ---- v2 recommended layer: pseudo-count score shrinkage (PCS) on CQR scores. Uniform prior over all
    # calibration buildings, no stage matching, kappa by leave-one-building-out on the reliability objective.
    t0 = time.time()
    bp, bp_tab = tune_hsc(Scq, bwq_cal, zc, alpha, stage_matched=False, Ks=[None], objective="MACDc")
    T["PCS-CQR tuning"] = time.time() - t0
    info["pcs_cqr"] = bp
    info["tune_pcs_cqr"] = bp_tab.replace({np.inf: "inf"}).to_dict(orient="records")
    t0 = time.time()
    out["PCS-CQR"] = band(cb.hsc_quantiles(cct_q, bincq, None, alpha, [bp["kappa"]], stages, stage_matched=False)[0],
                          lo=PT["qlo"], hi=PT["qhi"])
    T["PCS-CQR apply"] = time.time() - t0
    info["t_pcs_apply_per_target_day"] = T["PCS-CQR apply"] / (St.shape[0] * NH)
    info["t_pcs_apply_incl_hist_per_target_day"] = (T["PCS-CQR apply"] + T["own-score histograms (CQR)"]) / (
        St.shape[0] * NH)
    info["pcs_store_MB"] = bincq.sum(axis=(0, 1)).astype(np.float32).nbytes / 1e6  # pooled prior CDF only
    k_is = float(_select(bp_tab, "IS").kappa)  # same layer, pre-registered IS objective
    info["hsc_cqr_simple"] = dict(K=None, kappa=k_is)
    out["PCS-CQR (IS-tuned)"] = band(cb.hsc_quantiles(cct_q, bincq, None, alpha, [k_is], stages,
                                                      stage_matched=False)[0], lo=PT["qlo"], hi=PT["qhi"])
    # fixed pseudo-count of one week of hourly scores = donor-local mixture with fixed kappa (prior art)
    out["PCS-CQR κ=168"] = band(cb.hsc_quantiles(cct_q, bincq, None, alpha, [168], stages,
                                                 stage_matched=False)[0], lo=PT["qlo"], hi=PT["qhi"])
    groups = None
    if meta_cal is not None and meta_cal.site_id.nunique() > 2:
        groups = meta_cal.site_id.values.astype(str)
        bg, _ = tune_hsc(Scq, bwq_cal, zc, alpha, stage_matched=False, Ks=[None], objective="MACDc", groups=groups)
        info["pcs_cqr_grouped"] = bg
        out["PCS-CQR site-grouped"] = band(cb.hsc_quantiles(cct_q, bincq, None, alpha, [bg["kappa"]], stages,
                                                            stage_matched=False)[0], lo=PT["qlo"], hi=PT["qhi"])
    # PCS on the absolute score
    bpa, bpa_tab = tune_hsc(Sc, np.zeros_like(Sc), zc, alpha, stage_matched=False, Ks=[None], objective="MACDc")
    info["pcs"] = bpa
    out["PCS"] = band(cb.hsc_quantiles(cc_t, binc, None, alpha, [bpa["kappa"]], stages, stage_matched=False)[0])
    ka = float(_select(bpa_tab, "IS").kappa)
    info["hsc_simple"] = dict(K=None, kappa=ka)
    out["PCS (IS-tuned)"] = band(cb.hsc_quantiles(cc_t, binc, None, alpha, [ka], stages, stage_matched=False)[0])
    # model-agnostic check: the same layer on the MLP quantile model
    if "mqlo" in PT and "mqlo" in PC:
        Scm = np.maximum(PC["mqlo"] - PC["y"], PC["y"] - PC["mqhi"]) / PC["s"][:, :, None]
        Stm = np.maximum(PT["mqlo"] - PT["y"], PT["y"] - PT["mqhi"]) / PT["s"][:, :, None]
        bincm, _ = cb.bin_cdfs(cb.cum_counts(Scm), stages)
        out["CQR (MLP)"] = band(cb.pooled_quantile(bincm, alpha, True), lo=PT["mqlo"], hi=PT["mqhi"])
        bm, _ = tune_hsc(Scm, PC["mqhi"] / PC["s"][:, :, None] - PC["mqlo"] / PC["s"][:, :, None], zc, alpha,
                         stage_matched=False, Ks=[None], objective="MACDc")
        info["pcs_cqr_mlp"] = bm
        out["PCS-CQR (MLP)"] = band(cb.hsc_quantiles(cb.cum_counts(Stm), bincm, None, alpha, [bm["kappa"]], stages,
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
        # design elements added to PCS-CQR (each re-tuned on calibration buildings, reliability objective)
        abl = {}
        for name, stg, Ks_ in [("PCS-CQR +stage", True, [None]), ("PCS-CQR +kNN", False, KS),
                               ("PCS-CQR +kNN+stage", True, KS)]:
            c, _ = tune_hsc(Scq, bwq_cal, zc, alpha, stage_matched=stg, Ks=Ks_, objective="MACDc")
            abl[name] = c
            out[name] = band(cb.hsc_quantiles(cct_q, bincq, nbrs_by_stage(zt, zc, c["K"]), alpha, [c["kappa"]],
                                              stages, stage_matched=stg)[0], lo=PT["qlo"], hi=PT["qhi"])
        # no own scores (kappa = inf): uniform building-weighted prior only
        out["PCS-CQR -shrink"] = band(cb.hsc_quantiles(cct_q, bincq, None, alpha, [np.inf], stages,
                                                       stage_matched=False)[0], lo=PT["qlo"], hi=PT["qhi"])
        info["ablation_params_cqr"] = abl
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
