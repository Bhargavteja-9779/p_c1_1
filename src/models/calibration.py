"""Interval calibration layers for newly metered (cold-start) buildings.

Notation (manuscript Section 4):
  e_{b,h,j}  normalised nonconformity score of building b, onboarding stage h (= days of history
             available when the forecast was issued), hour j.
             Absolute-residual score:  e = |y - yhat| / s
             CQR score:                e = max(lo - y, y - hi) / s
  Interval:  [lo_base - q*s, hi_base + q*s]  (lo_base = hi_base = yhat for the absolute score).

All score distributions are represented by cumulative counts on a common, fine, monotone grid
G (asinh-spaced), so that quantiles of weighted mixtures are computed exactly up to grid
resolution; the grid quantile is rounded *up* (conservative) for every method alike.

Methods implemented
  pooled_quantile     : split conformal on all calibration-building scores (optionally stage-matched)
  hsc_quantiles       : proposed hierarchical-shrinkage conformal (HSC):
                        F_mix = (kappa * F_prior + sum_self 1{e_i <= .}) / (kappa + n_self + 1)
                        with F_prior = average CDF of the K most similar calibration buildings at the
                        same onboarding-stage bin, and the "+1" a point mass at +inf (test point).
  aci_quantiles       : adaptive conformal inference (Gibbs & Candes 2021) on top of the pooled prior.
"""
from __future__ import annotations

import numpy as np

# onboarding-stage bins (days of history): 1,2,3,4-6,7-13,14-27,28+
STAGE_EDGES = np.array([1, 2, 3, 4, 7, 14, 28, 10_000])


def stage_bin(h: np.ndarray | int) -> np.ndarray:
    return np.searchsorted(STAGE_EDGES, np.asarray(h), side="right") - 1


def make_grid(lo=-10.0, hi=500.0, n=4000, c=0.01):
    a, b = np.arcsinh(lo / c), np.arcsinh(hi / c)
    g = np.sinh(np.linspace(a, b, n)) * c
    g[np.argmin(np.abs(g))] = 0.0
    return g.astype(np.float64)


GRID = make_grid()
INF_RADIUS = GRID[-1]


def cum_counts(scores: np.ndarray, grid: np.ndarray = GRID) -> np.ndarray:
    """scores (nb, NH, 24) -> cumulative counts (nb, NH, NG): #{e <= grid[g]} per building & stage."""
    nb, NH, _ = scores.shape
    out = np.zeros((nb, NH, len(grid)), dtype=np.int16)
    for b in range(nb):
        for h in range(NH):
            v = scores[b, h]
            v = v[~np.isnan(v)]
            if v.size:
                idx = np.searchsorted(grid, v, side="left")  # e <= grid[idx]
                cnt = np.bincount(np.minimum(idx, len(grid) - 1), minlength=len(grid))
                out[b, h] = np.cumsum(cnt)
    return out


def bin_cdfs(cc: np.ndarray, stages: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Aggregate per-stage cumulative counts into per-stage-bin counts.

    cc: (nb, NH, NG) cumulative counts for stages `stages` (1..NH).
    returns counts (nb, nbins, NG) [float32] and totals (nb, nbins)
    """
    sb = stage_bin(stages)
    nbins = len(STAGE_EDGES) - 1
    out = np.zeros((cc.shape[0], nbins, cc.shape[2]), dtype=np.float32)
    for k in range(nbins):
        m = sb == k
        if m.any():
            out[:, k] = cc[:, m].sum(axis=1)
    tot = out[:, :, -1].copy()
    return out, tot


def _first_ge(F: np.ndarray, level: np.ndarray | float) -> np.ndarray:
    """index of first grid point with F >= level along last axis; INF if none."""
    ok = F >= np.asarray(level)[..., None] - 1e-6  # float32 tolerance (<1 score in 1e6)
    idx = np.where(ok.any(axis=-1), ok.argmax(axis=-1), len(GRID) - 1)
    return idx


def own_defined(n_own, alpha):
    """Split-conformal quantile of n own scores at level 1-alpha exists iff ceil((1-alpha)(n+1)) <= n."""
    n_own = np.asarray(n_own, dtype=float)
    return np.ceil((1 - alpha) * (n_own + 1)) <= n_own


def own_counts_before(self_cc, decay=1.0):
    """(nt, NH) number of own scores available before each stage (effective, decayed count if decay < 1)."""
    tot = self_cc[:, :, -1].astype(float)
    if decay == 1.0:
        return np.concatenate([np.zeros((tot.shape[0], 1)), np.cumsum(tot, axis=1)[:, :-1]], axis=1)
    out = np.zeros_like(tot)
    for h in range(1, tot.shape[1]):
        out[:, h] = decay * out[:, h - 1] + tot[:, h - 1]
    return out


def delay_counts(self_cc, lag=1):
    """Own-score counts delayed by `lag` stages (data-latency variant: the stage-h radius uses own scores up to
    stage h-1-lag only). self_cc: (nt, NH, NG)."""
    z = np.zeros_like(self_cc[:, :lag])
    return np.concatenate([z, self_cc[:, :-lag]], axis=1)


def pooled_quantile_lobo(cal_counts_bin, alpha):
    """Leave-one-building-out pooled (score-weighted) split-conformal radius: (ncal, nbins)."""
    C = cal_counts_bin.astype(np.float64)
    tot = C.sum(axis=0)[None] - C  # (ncal, nbins, NG)
    N = tot[:, :, -1]
    level = np.minimum(np.ceil((1 - alpha) * (N + 1)) / np.maximum(N, 1), 1.0)
    F = tot / np.maximum(N, 1)[:, :, None]
    return GRID[_first_ge(F, level)]


def pooled_quantile(cal_counts_bin: np.ndarray, alpha: float, stage_matched: bool = True,
                    weights: np.ndarray | None = None) -> np.ndarray:
    """Split-conformal radius per stage bin from pooled calibration scores.

    cal_counts_bin: (ncal, nbins, NG) cumulative counts; weights: optional (ncal,) building mask/weights.
    returns q (nbins,)
    """
    w = np.ones(cal_counts_bin.shape[0]) if weights is None else weights
    C = (cal_counts_bin * w[:, None, None]).sum(axis=0)  # (nbins, NG)
    if not stage_matched:
        C = np.repeat(C.sum(axis=0, keepdims=True), C.shape[0], axis=0)
    N = C[:, -1]
    level = np.minimum(np.ceil((1 - alpha) * (N + 1)) / np.maximum(N, 1), 1.0)
    F = C / np.maximum(N, 1)[:, None]
    return GRID[_first_ge(F, level)]


def neighbours(z_target: np.ndarray, z_cal: np.ndarray, K: int, exclude_self: bool = False) -> np.ndarray:
    """K nearest calibration buildings (standardised Euclidean). z_*: (n, d).

    NaN-safe: calibration buildings with an undefined descriptor are never chosen (distance +inf) unless
    fewer than K valid buildings exist; undefined target components are set to the calibration mean.
    With exclude_self, each pseudo-target's own index is removed explicitly (LOBO tuning).
    """
    ok_c = np.isfinite(z_cal).all(axis=1)
    zc_valid = z_cal[ok_c] if ok_c.any() else np.nan_to_num(z_cal)
    mu = zc_valid.mean(axis=0)
    sd = zc_valid.std(axis=0) + 1e-6
    a = (np.where(np.isfinite(z_target), z_target, mu) - mu) / sd
    c = (np.where(np.isfinite(z_cal), z_cal, mu) - mu) / sd
    d = ((a[:, None, :] - c[None, :, :]) ** 2).sum(-1)
    d[:, ~ok_c] = np.inf
    n = c.shape[0]
    if exclude_self:
        order = np.argsort(d, axis=1, kind="stable")
        keep = order != np.arange(order.shape[0])[:, None]
        order = order[keep].reshape(order.shape[0], n - 1)
        return order[:, :min(K, n - 1)]
    return np.argsort(d, axis=1, kind="stable")[:, :min(K, n)]


def prior_cdf(cal_cdf_k, cal_tot_k, nbr=None, excl=None):
    """Population prior CDF for one stage bin.

    cal_cdf_k: (ncal, NG) per-building CDFs in this bin; cal_tot_k: (ncal,) number of scores.
    nbr: (nt, K) neighbour indices or None (uniform over all calibration buildings, excluding
    `excl` (nt,) if given -- used for leave-one-building-out tuning).
    Only buildings with at least one score in the bin enter the average (an empty bin has no EDF).
    returns FP (nt, NG), n_prior (nt,)
    """
    ne = (cal_tot_k > 0).astype(np.float32)
    if nbr is not None:
        w = ne[nbr]  # (nt, K)
        sw = w.sum(axis=1)
        FP = (cal_cdf_k[nbr] * w[:, :, None]).sum(axis=1) / np.maximum(sw, 1)[:, None]
        if (sw == 0).any():  # all neighbours empty in this bin: fall back to all non-empty buildings
            FP[sw == 0] = (cal_cdf_k * ne[:, None]).sum(axis=0) / max(ne.sum(), 1)
        return FP, cal_tot_k[nbr].sum(axis=1)
    S = (cal_cdf_k * ne[:, None]).sum(axis=0)
    T = cal_tot_k.sum()
    n = ne.sum()
    if excl is None:
        return S[None, :] / max(n, 1), np.array([T])
    own = ne[excl]
    return (S[None, :] - cal_cdf_k[excl] * own[:, None]) / np.maximum(n - own, 1)[:, None], T - cal_tot_k[excl]


def hsc_quantiles(self_cc, cal_bin_counts, nbr_by_stage, alpha, kappas, stages, excl=None,
                  stage_matched=True, decay=1.0):
    """Proposed HSC radius for each target building and stage, for several kappa values.

    self_cc        : (nt, NH, NG) cumulative counts of the target's own scores per stage
    cal_bin_counts : (ncal, nbins, NG) cumulative counts of calibration buildings per stage bin
    nbr_by_stage   : list (len NH) of (nt, K) neighbour indices, or None (uniform prior)
    kappas         : iterable of prior pseudo-counts (np.inf -> prior only; 0 -> self only)
    excl           : (nt,) calibration index of each target (leave-one-building-out tuning) or None
    stage_matched  : if False the prior pools all onboarding stages (ablation)
    decay          : per-day down-weighting of the building's own past scores (1 = none; recency variant)
    returns q (n_kappa, nt, NH)
    """
    kappas = list(kappas)
    nt, NH, NG = self_cc.shape
    cbc = cal_bin_counts.astype(np.float32)
    if not stage_matched:
        cbc = np.repeat(cbc.sum(axis=1, keepdims=True), cbc.shape[1], axis=1)
    tot = cbc[:, :, -1]
    cal_cdf = cbc / np.maximum(tot, 1)[:, :, None]
    q = np.empty((len(kappas), nt, NH), dtype=np.float32)
    self_before = np.zeros((nt, NG), dtype=np.float32)
    for hi, h in enumerate(stages):
        k = int(stage_bin(h))
        nbr = None if nbr_by_stage is None else nbr_by_stage[hi]
        FP, n_prior = prior_cdf(cal_cdf[:, k, :], tot[:, k], nbr, excl)
        FP = np.broadcast_to(FP, (nt, NG))
        n_self = self_before[:, -1]
        for ki, kappa in enumerate(kappas):
            if np.isinf(kappa):
                N = np.broadcast_to(np.asarray(n_prior, dtype=float), (nt,))
                level = np.minimum(np.ceil((1 - alpha) * (N + 1)) / np.maximum(N, 1), 1.0)
                idx = _first_ge(FP, level)
            else:
                M = (kappa * FP + self_before) / (kappa + n_self + 1.0)[:, None]
                idx = _first_ge(M, np.full(nt, 1 - alpha))
            q[ki, :, hi] = GRID[idx]
        self_before = decay * self_before + self_cc[:, hi, :] if decay != 1.0 else self_before + self_cc[:, hi, :]
    return q


def aci_quantiles(target_scores, prior_counts_bin, alpha, gamma, stages, return_capped=False, delay=0):
    """ACI (Gibbs & Candes, 2021) with daily batches of 24 hourly feedback signals.

    alpha_{h+1} = alpha_h + gamma * sum_j (alpha - err_{h,j}); radius = prior quantile at 1-alpha_h.
    target_scores: (nt, NH, 24); prior_counts_bin: (nbins, NG) or (nt, nbins, NG) cumulative counts.
    delay: number of extra stages before a day's feedback is applied (data-latency variant; 0 = next day).
    """
    nt, NH, _ = target_scores.shape
    pending = []
    P = prior_counts_bin.astype(np.float32)
    if P.ndim == 2:
        P = np.broadcast_to(P, (nt,) + P.shape)
    F = P / np.maximum(P[..., -1:], 1)
    a = np.full(nt, alpha, dtype=float)
    q = np.empty((nt, NH), dtype=np.float32)
    capped = 0
    for hi, h in enumerate(stages):
        k = int(stage_bin(h))
        lev = 1 - a
        idx = _first_ge(F[:, k, :], np.clip(lev, 0, 1))
        idx_min = _first_ge(F[:, k, :], np.full(nt, 1e-5))  # smallest observed score (empty-set convention)
        idx_max = _first_ge(F[:, k, :], np.full(nt, 1.0 - 1e-6))  # largest observed score (finite surrogate of
        # the infinite interval of the original method when alpha_h <= 0)
        idx = np.where(lev >= 1, idx_max, np.where(lev <= 0, idx_min, idx))
        capped += (lev >= 1).sum()
        q[:, hi] = GRID[idx]
        e = target_scores[:, hi, :]
        valid = ~np.isnan(e)
        err = (e > q[:, hi:hi + 1]) & valid
        pending.append(gamma * (alpha * valid.sum(1) - err.sum(1)))
        if len(pending) > delay:
            a = a + pending.pop(0)
    if return_capped:
        return q, capped / float(nt * len(stages))
    return q


def normalized_IS(q, scores, base_w, alpha):
    """Mean normalised interval score (units of s) for radius q (..., nt, NH) -- tuning objective."""
    e = scores[None]
    valid = ~np.isnan(e)
    qq = q[..., None]
    v = base_w[None] + 2 * qq + (2 / alpha) * np.maximum(np.where(valid, e, 0) - qq, 0)
    v = np.where(valid, v, 0)
    return v.sum(axis=(-1, -2, -3)) / valid.sum(axis=(-1, -2, -3))


# ----------------------------------------------------------------------------------------------
# Baselines from the closest prior art
# ----------------------------------------------------------------------------------------------
def ghcp_quantiles(self_cc, cal_counts_allstages, alpha, stages, n_surrogate):
    """GHCP-style calibration (Mallick, Tchetgen Tchetgen, Dobriban & Lee, arXiv:2608.15500, Eq. 5), adapted:
    each calibration building ("reference group") receives total weight 1/(K+1) spread over its scores;
    the new building receives the same group share 1/(K+1), spread over its observed own scores and a point
    mass at +inf for its not-yet-observed scores (surrogate group size n_surrogate). The local-predictor
    step of GHCP is omitted (our global forecaster already conditions on the building's own history).
    self_cc: (nt, NH, NG) cumulative own counts; cal_counts_allstages: (ncal, NG) cumulative counts.
    """
    nt, NH, NG = self_cc.shape
    tot = np.maximum(cal_counts_allstages[:, -1:], 1).astype(np.float64)
    Ssum = (cal_counts_allstages / tot).sum(axis=0)  # sum of reference CDFs
    K = cal_counts_allstages.shape[0]
    q = np.empty((nt, NH), dtype=np.float32)
    own = np.zeros((nt, NG), dtype=np.float64)
    for hi, h in enumerate(stages):
        n_own = own[:, -1]
        denom = np.maximum(n_surrogate, n_own)  # own share never exceeds one group share
        F = (Ssum[None, :] + own / denom[:, None]) / (K + 1.0)
        q[:, hi] = GRID[_first_ge(F, np.full(nt, 1 - alpha))]
        own += self_cc[:, hi, :]
    return q


def qshrink_quantiles(self_cc, q_pool, alpha, lam, stages, decay=1.0):
    """Quantile-level shrinkage ("regularised Mondrian", Rafe & Das, arXiv:2605.05562):
    q = w q_own + (1-w) q_pool, w = n/(n+lam); q_own = split-conformal quantile of the building's own past
    scores; w = 0 while q_own does not exist (decided from the number of own scores). lam = 0 -> own only
    (with pooled fallback), lam = inf -> pooled. q_pool: (nt, NH) or (NH,) pooled radius.
    decay < 1: recency variant (own counts decayed per day; n is then the effective count)."""
    nt, NH, NG = self_cc.shape
    q_own = hsc_quantiles(self_cc, np.zeros((1, len(STAGE_EDGES) - 1, NG), dtype=np.float32), None, alpha, [0],
                          stages, decay=decay)[0]
    n_own = own_counts_before(self_cc, decay)
    defined = own_defined(n_own, alpha)
    w = np.where(defined, 1.0 if lam == 0 else (0.0 if np.isinf(lam) else n_own / (n_own + lam)), 0.0)
    qp = np.broadcast_to(q_pool, (nt, NH))
    return (w * np.where(defined, q_own, 0.0) + (1 - w) * qp).astype(np.float32)


def tqab_quantiles(target_scores, cal_scores, prior_counts_bin, alpha, stages, beta=0.8):
    """TQA-B (Lin, Trivedi & Sun, NeurIPS 2022), adapted to daily batches: the building's exponentially
    decayed mean own score (decay beta per day, normalised by the weight sum) is ranked among the
    calibration buildings' decayed means at the same onboarding stage; the rank r is mapped to a quantile
    adjustment by the budgeting function g^B (C = alpha^2/(1-alpha)^2), a = clip(alpha - g^B(r), 0.01, 1);
    radius = pooled stage-matched quantile at level 1-a."""
    def decayed(sc):
        m = np.nanmean(sc, axis=2)  # (n, NH) daily mean scores
        n, NHh = m.shape
        out = np.full((n, NHh), np.nan)
        num = np.zeros(n)
        den = np.zeros(n)
        for hi in range(NHh):
            out[:, hi] = np.where(den > 0, num / np.maximum(den, 1e-12), np.nan)  # uses days < hi only
            v = m[:, hi]
            ok = ~np.isnan(v)
            num = beta * num + np.where(ok, v, 0.0)
            den = beta * den + ok.astype(float)
        return out
    et, ec = decayed(target_scores), decayed(cal_scores)
    nt, NH, _ = target_scores.shape
    N = cal_scores.shape[0]
    P = prior_counts_bin.astype(np.float64)
    F = P / np.maximum(P[:, -1:], 1)
    C = alpha ** 2 / (1 - alpha) ** 2
    q = np.empty((nt, NH), dtype=np.float32)
    Npool = P[:, -1]
    for hi, h in enumerate(stages):
        k = int(stage_bin(h))
        a = np.full(nt, alpha)
        if hi > 0:
            r = (ec[None, :, hi] < et[:, hi, None]).sum(axis=1) / (N + 1.0)
            g = np.where(r < 1 - alpha, C * (r - (1 - alpha)), r - (1 - alpha))
            g = np.where(np.isnan(et[:, hi]), 0.0, g)
            # budget scale lambda from the CALIBRATION buildings (each ranked among the others), never from
            # the target batch
            rc = (ec[None, :, hi] < ec[:, hi, None]).sum(axis=1) / float(N)
            gc = np.where(rc < 1 - alpha, C * (rc - (1 - alpha)), rc - (1 - alpha))
            gc = np.where(np.isnan(ec[:, hi]), 0.0, gc)
            gmax = gc.max() if gc.size else 0.0
            lam = min(1.0, (alpha - 0.01) / gmax) if gmax > alpha - 0.01 else 1.0  # original: scale g so a>=0.01
            a = alpha - lam * g
        # quantile of pooled scores together with a point at +inf (original TQA): level (1-a)(N+1)/N
        lev = np.minimum((1 - a) * (Npool[k] + 1) / max(Npool[k], 1), 1.0)
        idx = _first_ge(np.broadcast_to(F[k], (nt, F.shape[1])), lev)
        q[:, hi] = GRID[idx]
    return q


# ----------------------------------------------------------------------------------------------
# Additional variants (pre-registered in experiments/PREREGISTRATION.md, Addendum A)
# ----------------------------------------------------------------------------------------------
def coverage_deviation(q, scores, alpha):
    """Mean over buildings of |coverage_b - (1-alpha)| for radius q (..., n, NH) and scores (n, NH, 24)
    (LOBO-MACD tuning objective; per-building coverage over the whole onboarding window)."""
    e = scores[None]
    valid = ~np.isnan(e)
    hit = (np.where(valid, e, np.inf) <= q[..., None]) & valid
    cov = hit.sum(axis=(-1, -2)) / np.maximum(valid.sum(axis=(-1, -2)), 1)
    return np.abs(cov - (1 - alpha)).mean(axis=-1)


def running_scale_ratio(abs_scores, sigma0, kappa_s):
    """r_{b,h} = sigma_hat_{b,h} / sigma0 with sigma_hat = (kappa_s*sigma0 + sum own |res|/s) / (kappa_s + n),
    using only the building's own scores from stages < h. abs_scores: (n, NH, 24); sigma0: scalar or (n,)."""
    a = np.where(np.isnan(abs_scores), 0.0, abs_scores).sum(axis=2)
    c = (~np.isnan(abs_scores)).sum(axis=2).astype(float)
    S = np.concatenate([np.zeros((a.shape[0], 1)), np.cumsum(a, axis=1)[:, :-1]], axis=1)
    n = np.concatenate([np.zeros((c.shape[0], 1)), np.cumsum(c, axis=1)[:, :-1]], axis=1)
    s0 = np.broadcast_to(np.asarray(sigma0, dtype=float).reshape(-1, 1) if np.ndim(sigma0) else
                         np.asarray(sigma0, dtype=float), S.shape)
    return (kappa_s * s0 + S) / (kappa_s + n) / s0


def ssc_quantiles(stud_cal, alpha, nt):
    """Stage-wise pooled-CDF conformal radius (Dunn, Wasserman & Ramdas 2023, 'pooling CDFs'):
    at each exact stage h every calibration building with valid scores gets weight 1/(M+1), spread
    uniformly over its scores at that stage, and the new building a point mass 1/(M+1) at +inf.
    stud_cal: (M, NH, 24) studentised calibration scores. Returns q (nt, NH)."""
    cc = cum_counts(stud_cal)  # (M, NH, NG)
    tot = cc[:, :, -1]
    NH = stud_cal.shape[1]
    q = np.empty((nt, NH), dtype=np.float32)
    for hi in range(NH):
        ok = tot[:, hi] > 0
        M = int(ok.sum())
        F = (cc[ok, hi, :] / tot[ok, hi, None]).sum(axis=0) / (M + 1.0)
        q[:, hi] = GRID[_first_ge(F[None, :], np.array([1 - alpha]))[0]]
    return q


# ----------------------------------------------------------------------------------------------
# Two-timescale calibration: shrinkage prior (slow, distributional) + level feedback (fast, per building)
# ----------------------------------------------------------------------------------------------
def hsc_aci_quantiles(target_scores, self_cc, cal_bin_counts, alpha, kappa, gamma, stages, decay=1.0,
                      excl=None, window=None, delay=0):
    """Shrinkage-conformal radius evaluated at a building-specific level 1 - a_{b,h} that is updated online
    from the building's own misses (ACI-type feedback on top of the shrinkage mixture).

    Mixture (stage-agnostic population prior, recency-weighted own scores, +1 mass at +inf):
        M_{b,h} = (kappa F_pop + S^rho_{b,h}) / (kappa + n^rho_{b,h} + 1)
    Level feedback with daily batches of 24 hourly signals:
        cumulative (window=None): a_{h+1} = a_h + gamma * sum_j (alpha - err_{h,j})
        windowed (window=W days): a_{h+1} = alpha + gamma * sum over the last W days of (alpha - err)
    gamma = 0 recovers the shrinkage radius. The level is clipped to the attainable range of M, so the radius
    stays finite (largest observed score) and non-negative (smallest observed score).

    target_scores: (nt, NH, 24); self_cc: (nt, NH, NG) cumulative counts of the same scores;
    cal_bin_counts: (ncal, nbins, NG); excl: (nt,) calibration index of each target (leave-one-out tuning).
    returns q (nt, NH)
    """
    nt, NH, NG = self_cc.shape
    cbc = cal_bin_counts.astype(np.float32).sum(axis=1)  # stage-agnostic prior
    tot = cbc[:, -1]
    cal_cdf = cbc / np.maximum(tot, 1)[:, None]
    FP, _ = prior_cdf(cal_cdf, tot, None, excl)
    FP = np.broadcast_to(FP, (nt, NG)).astype(np.float32)
    self_before = np.zeros((nt, NG), dtype=np.float32)
    a = np.full(nt, alpha, dtype=float)
    hist = []
    pending = []
    q = np.empty((nt, NH), dtype=np.float32)
    for hi, h in enumerate(stages):
        n_self = self_before[:, -1]
        M = (kappa * FP + self_before) / (kappa + n_self + 1.0)[:, None]
        mmax = M[:, -1]
        lev = np.clip(1 - a, 1e-5, None)
        lev = np.minimum(lev, mmax)
        q[:, hi] = GRID[_first_ge(M, lev)]
        e = target_scores[:, hi, :]
        valid = ~np.isnan(e)
        err = (e > q[:, hi:hi + 1]) & valid
        sig = alpha * valid.sum(1) - err.sum(1)
        pending.append(sig)
        if len(pending) > delay:
            s_ = pending.pop(0)
            if window is None:
                a = a + gamma * s_
            else:
                hist.append(s_)
                a = alpha + gamma * np.sum(hist[-window:], axis=0)
        self_before = decay * self_before + self_cc[:, hi, :]
    return q
