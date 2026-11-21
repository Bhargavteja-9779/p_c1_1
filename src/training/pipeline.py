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
GAMMAS = [0.0, 0.0001, 0.0002, 0.0005, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05]  # 0-2e-4 added after audit; 0.02, 0.05 in revision 1 (upper edge hit after clipping)


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


# revision 1 (R6): a genuinely weak forecaster sees calendar, history length, the previous-day mean level and
# weather only (no lags, no daily extremes, no load profiles, no variability)
WEAK_DROP = ["lag1d", "lag2d", "lag7d", "lag14d", "prev_max", "prev_min", "hour_prof", "daytype_prof",
             "dowhour_prof", "daily_var"]


def drop_cols(X, use_weather, drop):
    if drop:
        names = fe.feature_names(use_weather)
        X[:, [names.index(c) for c in drop]] = np.nan
    return X


def build_xy(ds, B, T, H, use_weather, drop=None):
    X, y, s = fe.build(ds["load"], ds["temp"], ds["dates"], B, T, H, use_weather)
    X = drop_cols(X, use_weather, drop)
    yn = y / np.repeat(s, 24)
    # training-only artefact filter: normalised targets > 20 arise from meter restarts after
    # near-zero/flat-lined history (data errors), not from consumption behaviour
    ok = ~np.isnan(yn) & (yn <= 20)
    return X[ok], yn[ok]


def train_models(ds, sp, seed, use_weather, alpha=0.1, frac=0.5, with_mlp=True, log=print, drop=None):
    rng = np.random.default_rng(seed)
    per, _ = periods(ds)
    Xtr, ytr = build_xy(ds, *sample_training(ds, sp["train"], per, rng, frac), use_weather, drop)
    Xv, yv = build_xy(ds, *sample_training(ds, sp["val"], per, rng, 0.5), use_weather, drop)
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
    m["drop"] = drop
    m["n_train_rows"] = len(ytr)
    return m


def onboard_dates(ds, bidx, period, rng, min_valid=0.8):
    """Random onboarding day per building such that >= 80 % of the window's hours are valid.

    Returns -1 for a building without any such window (it cannot be onboarded; operational rule, no
    look-ahead beyond the window itself). Callers drop these buildings."""
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
    X = drop_cols(X, models["use_weather"], models.get("drop"))
    srep = np.repeat(s, 24)
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


SELF_MIN_HOURS = [72, 168, 336]
GHCP_NSUR = [24, 168, 672]
TQA_BETAS = [0.5, 0.8, 0.95]


def tune_hsc(cal_scores, cal_base_w, z_cal, alpha, stage_matched=True, Ks=KS, kappas=KAPPAS, objective="IS"):
    """Leave-one-building-out selection of (kappa, K) on calibration buildings.

    objective "IS": pre-registered mean normalised interval score; "macd" (revision 1): LOBO per-building
    coverage deviation with IS tie-break (cb.pick)."""
    stages = np.arange(1, NH + 1)
    cc = cb.cum_counts(cal_scores)
    binc, _ = cb.bin_cdfs(cc, stages)
    res = []
    for K in Ks:
        nb = nbrs_by_stage(z_cal, z_cal, K, exclude_self=True)
        excl = np.arange(cal_scores.shape[0]) if K is None else None
        q = cb.hsc_quantiles(cc, binc, nb, alpha, kappas, stages, excl=excl, stage_matched=stage_matched)
        macd, IS = cb.macd_objective(q, cal_scores, cal_base_w, alpha)
        for ki, kap in enumerate(kappas):
            res.append(dict(K=K, kappa=kap, obj=float(IS[ki]), macd=float(macd[ki])))
    df = pd.DataFrame(res)
    best = df.loc[df.obj.idxmin()] if objective == "IS" else df.iloc[cb.pick((df.macd.values, df.obj.values))]
    return dict(K=None if pd.isna(best.K) else int(best.K), kappa=float(best.kappa)), df


def tune_aci(cal_scores, alpha, gammas=GAMMAS):
    stages = np.arange(1, NH + 1)
    cc = cb.cum_counts(cal_scores)
    binc, _ = cb.bin_cdfs(cc, stages)
    tot = binc.sum(axis=0)
    prior = tot[None] - binc  # leave-one-building-out pooled prior per pseudo-target
    res = []
    for g in gammas:
        q = cb.aci_quantiles(cal_scores, prior, alpha, g, stages)
        macd, IS = cb.macd_objective(q[None], cal_scores, np.zeros_like(cal_scores), alpha)
        res.append(dict(gamma=g, obj=float(IS[0]), macd=float(macd[0])))
    df = pd.DataFrame(res)
    return float(df.gamma.values[cb.pick((df.macd.values, df.obj.values))]), df


def tune_qshrink(cal_scores, cal_base_w, alpha, lams=tuple(KAPPAS)):
    """Leave-one-building-out choice of lambda for quantile-level shrinkage (same objective and grid as HSC;
    lambda = 0: own quantile when defined, lambda = inf: pooled radius)."""
    stages = np.arange(1, NH + 1)
    cc = cb.cum_counts(cal_scores)
    binc, _ = cb.bin_cdfs(cc, stages)
    q_pool = cb.pooled_quantile_lobo(binc, alpha)[:, cb.stage_bin(stages)]  # (ncal, NH), score-weighted
    res = []
    for lam in lams:
        q = cb.qshrink_quantiles(cc, q_pool, alpha, lam, stages)
        macd, IS = cb.macd_objective(q[None], cal_scores, cal_base_w, alpha)
        res.append(dict(lam=lam, obj=float(IS[0]), macd=float(macd[0])))
    df = pd.DataFrame(res)
    return float(df.lam.values[cb.pick((df.macd.values, df.obj.values))]), df


def tune_selffb(cal_scores, cal_base_w, alpha, grid=tuple(SELF_MIN_HOURS)):
    """LOBO choice of the minimum own history (hours) for Self-CQR with pooled fallback (revision 1)."""
    stages = np.arange(1, NH + 1)
    cc = cb.cum_counts(cal_scores)
    binc, _ = cb.bin_cdfs(cc, stages)
    q_pool = cb.pooled_quantile_lobo(binc, alpha)[:, cb.stage_bin(stages)]
    res = []
    for m in grid:
        q = cb.selffb_quantiles(cc, q_pool, alpha, m, stages)
        macd, IS = cb.macd_objective(q[None], cal_scores, cal_base_w, alpha)
        res.append(dict(min_hours=m, obj=float(IS[0]), macd=float(macd[0])))
    df = pd.DataFrame(res)
    return int(df.min_hours.values[cb.pick((df.macd.values, df.obj.values))]), df


def tune_ghcp(cal_scores, cal_base_w, alpha, grid=tuple(GHCP_NSUR)):
    stages = np.arange(1, NH + 1)
    cc = cb.cum_counts(cal_scores)
    tot_all = cb.bin_cdfs(cc, stages)[0].sum(axis=1)
    excl = np.arange(cal_scores.shape[0])
    res = []
    for n in grid:
        q = cb.ghcp_quantiles(cc, tot_all, alpha, stages, n, excl=excl)
        macd, IS = cb.macd_objective(q[None], cal_scores, cal_base_w, alpha)
        res.append(dict(n_sur=n, obj=float(IS[0]), macd=float(macd[0])))
    df = pd.DataFrame(res)
    return float(df.n_sur.values[cb.pick((df.macd.values, df.obj.values))]), df


def tune_tqab(cal_scores, cal_base_w, alpha, grid=tuple(TQA_BETAS)):
    """LOBO-style choice of the TQA-B decay (pseudo-targets ranked among all calibration buildings incl.
    themselves -- a slight approximation -- with a leave-one-out pooled reference distribution)."""
    stages = np.arange(1, NH + 1)
    binc, _ = cb.bin_cdfs(cb.cum_counts(cal_scores), stages)
    tot = binc.sum(axis=0)
    res = []
    for beta in grid:
        q = np.stack([cb.tqab_quantiles(cal_scores[i:i + 1], cal_scores, tot - binc[i], alpha, stages, beta)[0]
                      for i in range(cal_scores.shape[0])])
        macd, IS = cb.macd_objective(q[None], cal_scores, cal_base_w, alpha)
        res.append(dict(beta=beta, obj=float(IS[0]), macd=float(macd[0])))
    df = pd.DataFrame(res)
    return float(df.beta.values[cb.pick((df.macd.values, df.obj.values))]), df


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
        l2, h2 = lo - q[:, :, None] * s, hi + q[:, :, None] * s
        # revision 1 (R2): a negative CQR radius larger than half the quantile spread would invert the
        # interval; such hours get the degenerate interval at the midpoint (counted in info["inverted"])
        inv = l2 > h2
        info["inverted_hours"] = info.get("inverted_hours", 0) + int(inv.sum())
        if inv.any():
            mid = (l2 + h2) / 2
            l2, h2 = np.where(inv, mid, l2), np.where(inv, mid, h2)
        return l2, h2

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
    gq, gq_tab = tune_aci(Scq, alpha) if fixed is None else (fixed["gamma"], None)
    info["aci_cqr_gamma"] = gq
    if gq_tab is not None:
        info["tune_aci_cqr"] = gq_tab.to_dict(orient="records")
    q_aciq = cb.aci_quantiles(Stq, bincq.sum(axis=0), alpha, gq, stages)
    info["aci_cqr_cap_share"] = float(np.mean(q_aciq >= cb.INF_RADIUS))
    out["ACI-CQR"] = band(q_aciq, lo=PT["qlo"], hi=PT["qhi"])
    # revision 1 (R10): self-only CQR with a minimum-history fallback to pooled CQR (switching rule)
    mh, mh_tab = tune_selffb(Scq, PC["qhi"] / PC["s"][:, :, None] - PC["qlo"] / PC["s"][:, :, None], alpha)
    info["selffb_min_hours"] = mh
    info["tune_selffb"] = mh_tab.to_dict(orient="records")
    out["Self-CQR-fb"] = band(cb.selffb_quantiles(cct_q, q_fbq, alpha, mh, stages), lo=PT["qlo"], hi=PT["qhi"])
    # Mondrian by usage on CQR scores (completeness, R10)
    if meta_cal is not None and meta_cal.usage.nunique() > 1:
        lo_m, hi_m = out["CQR"][0].copy(), out["CQR"][1].copy()
        for u in np.unique(meta_tgt.usage.values):
            mc = (meta_cal.usage.values == u)
            if mc.sum() < 10:
                continue
            l2, h2 = band(cb.pooled_quantile(bincq, alpha, True, weights=mc.astype(float)), lo=PT["qlo"], hi=PT["qhi"])
            mtg = meta_tgt.usage.values == u
            lo_m[mtg], hi_m[mtg] = l2[mtg], h2[mtg]
        out["Mondrian-CQR"] = (lo_m, hi_m)
    # closest prior-art mechanisms, on the same CQR scores (see calibration.py docstrings)
    bwq_cal = PC["qhi"] / PC["s"][:, :, None] - PC["qlo"] / PC["s"][:, :, None]
    tot_all_q = bincq.sum(axis=1)
    n_sur, ns_tab = tune_ghcp(Scq, bwq_cal, alpha)  # revision 1 (R3): surrogate group size by LOBO
    info["ghcp_n_sur"] = n_sur
    info["tune_ghcp"] = ns_tab.to_dict(orient="records")
    out["GHCP-CQR"] = band(cb.ghcp_quantiles(cct_q, tot_all_q, alpha, stages, n_sur), lo=PT["qlo"], hi=PT["qhi"])
    lam, lam_tab = tune_qshrink(Scq, bwq_cal, alpha)
    info["qshrink_lambda"] = lam
    info["tune_qshrink"] = lam_tab.replace({np.inf: "inf"}).to_dict(orient="records")
    out["QShrink-CQR"] = band(cb.qshrink_quantiles(cct_q, cb.pooled_quantile(bincq, alpha, True)[sb], alpha, lam,
                                                   stages), lo=PT["qlo"], hi=PT["qhi"])
    out["QShrink-CQR fixed-λ"] = band(cb.qshrink_quantiles(cct_q, cb.pooled_quantile(bincq, alpha, True)[sb], alpha,
                                                          168, stages), lo=PT["qlo"], hi=PT["qhi"])
    beta, b_tab = tune_tqab(Scq, bwq_cal, alpha)  # revision 1 (R3): decay by LOBO
    info["tqab_beta"] = beta
    info["tune_tqab"] = b_tab.to_dict(orient="records")
    out["TQA-B-CQR"] = band(cb.tqab_quantiles(Stq, Scq, bincq.sum(axis=0), alpha, stages, beta), lo=PT["qlo"],
                            hi=PT["qhi"])
    # PRIMARY (revision 1): one-parameter layer -- uniform prior (K = all), no stage matching, kappa by LOBO
    # with the reliability objective (MACD, IS tie-break); the IS-tuned version is kept for comparison
    t0 = time.time()
    bs, bs_tab = tune_hsc(Scq, bwq_cal, zc, alpha, stage_matched=False, Ks=[None], objective="macd")
    info["t_tune_primary"] = time.time() - t0
    bsi = bs_tab.loc[bs_tab.obj.idxmin()]
    info["hsc_cqr_simple_IS"] = dict(K=None, kappa=float(bsi.kappa))
    out["HSC-CQR simple (IS-tuned)"] = band(cb.hsc_quantiles(cct_q, bincq, None, alpha, [float(bsi.kappa)], stages,
                                                             stage_matched=False)[0], lo=PT["qlo"], hi=PT["qhi"])
    info["hsc_cqr_simple"] = bs
    info["tune_hsc_cqr_simple"] = bs_tab.replace({np.inf: "inf"}).to_dict(orient="records")
    # fixed pseudo-count (one week of hourly scores), i.e. a donor-local mixture with fixed kappa
    out["HSC-CQR fixed-κ"] = band(cb.hsc_quantiles(cct_q, bincq, None, alpha, [168], stages,
                                                   stage_matched=False)[0], lo=PT["qlo"], hi=PT["qhi"])
    t0 = time.time()
    out["HSC-CQR simple"] = band(cb.hsc_quantiles(cct_q, bincq, None, alpha, [bs["kappa"]], stages,
                                                  stage_matched=False)[0], lo=PT["qlo"], hi=PT["qhi"])
    info["t_apply_primary_per_target_day"] = (time.time() - t0) / (Stq.shape[0] * NH)
    bsa, _ = tune_hsc(Sc, np.zeros_like(Sc), zc, alpha, stage_matched=False, Ks=[None], objective="macd")
    info["hsc_simple"] = bsa
    out["HSC simple"] = band(cb.hsc_quantiles(cc_t, binc, None, alpha, [bsa["kappa"]], stages,
                                              stage_matched=False)[0])
    # model-agnostic check: the same layer on the MLP quantile model
    if "mqlo" in PT and "mqlo" in PC:
        Scm = np.maximum(PC["mqlo"] - PC["y"], PC["y"] - PC["mqhi"]) / PC["s"][:, :, None]
        Stm = np.maximum(PT["mqlo"] - PT["y"], PT["y"] - PT["mqhi"]) / PT["s"][:, :, None]
        bincm, _ = cb.bin_cdfs(cb.cum_counts(Scm), stages)
        out["CQR (MLP)"] = band(cb.pooled_quantile(bincm, alpha, True), lo=PT["mqlo"], hi=PT["mqhi"])
        bm, _ = tune_hsc(Scm, PC["mqhi"] / PC["s"][:, :, None] - PC["mqlo"] / PC["s"][:, :, None], zc, alpha,
                         stage_matched=False, Ks=[None], objective="macd")
        info["hsc_cqr_mlp"] = bm
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
