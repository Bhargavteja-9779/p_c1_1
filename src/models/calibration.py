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


def make_grid(lo=-10.0, hi=60.0, n=3000, c=0.01):
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
    """K nearest calibration buildings (standardised Euclidean). z_*: (n, d)."""
    mu = z_cal.mean(axis=0)
    sd = z_cal.std(axis=0) + 1e-6
    a = (z_target - mu) / sd
    c = (z_cal - mu) / sd
    d = ((a[:, None, :] - c[None, :, :]) ** 2).sum(-1)
    if exclude_self:
        np.fill_diagonal(d, np.inf)
    K = min(K, c.shape[0] - (1 if exclude_self else 0))
    return np.argsort(d, axis=1)[:, :K]


def prior_cdf(cal_cdf_k, cal_tot_k, nbr=None, excl=None):
    """Population prior CDF for one stage bin.

    cal_cdf_k: (ncal, NG) per-building CDFs in this bin; cal_tot_k: (ncal,) number of scores.
    nbr: (nt, K) neighbour indices or None (uniform over all calibration buildings, excluding
    `excl` (nt,) if given -- used for leave-one-building-out tuning).
    returns FP (nt, NG), n_prior (nt,)
    """
    if nbr is not None:
        return cal_cdf_k[nbr].mean(axis=1), cal_tot_k[nbr].sum(axis=1)
    S = cal_cdf_k.sum(axis=0)
    T = cal_tot_k.sum()
    n = cal_cdf_k.shape[0]
    if excl is None:
        return S[None, :] / n, np.array([T])
    return (S[None, :] - cal_cdf_k[excl]) / (n - 1), T - cal_tot_k[excl]


def hsc_quantiles(self_cc, cal_bin_counts, nbr_by_stage, alpha, kappas, stages, excl=None,
                  stage_matched=True):
    """Proposed HSC radius for each target building and stage, for several kappa values.

    self_cc        : (nt, NH, NG) cumulative counts of the target's own scores per stage
    cal_bin_counts : (ncal, nbins, NG) cumulative counts of calibration buildings per stage bin
    nbr_by_stage   : list (len NH) of (nt, K) neighbour indices, or None (uniform prior)
    kappas         : iterable of prior pseudo-counts (np.inf -> prior only; 0 -> self only)
    excl           : (nt,) calibration index of each target (leave-one-building-out tuning) or None
    stage_matched  : if False the prior pools all onboarding stages (ablation)
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
        self_before += self_cc[:, hi, :]
    return q


def aci_quantiles(target_scores, prior_counts_bin, alpha, gamma, stages):
    """ACI (Gibbs & Candes, 2021) with daily batches of 24 hourly feedback signals.

    alpha_{h+1} = alpha_h + gamma * sum_j (alpha - err_{h,j}); radius = prior quantile at 1-alpha_h.
    target_scores: (nt, NH, 24); prior_counts_bin: (nbins, NG) or (nt, nbins, NG) cumulative counts.
    """
    nt, NH, _ = target_scores.shape
    P = prior_counts_bin.astype(np.float32)
    if P.ndim == 2:
        P = np.broadcast_to(P, (nt,) + P.shape)
    F = P / np.maximum(P[..., -1:], 1)
    a = np.full(nt, alpha, dtype=float)
    q = np.empty((nt, NH), dtype=np.float32)
    for hi, h in enumerate(stages):
        k = int(stage_bin(h))
        lev = 1 - a
        idx = _first_ge(F[:, k, :], np.clip(lev, 0, 1))
        idx = np.where(lev >= 1, len(GRID) - 1, np.where(lev <= 0, 0, idx))
        q[:, hi] = GRID[idx]
        e = target_scores[:, hi, :]
        valid = ~np.isnan(e)
        err = (e > q[:, hi:hi + 1]) & valid
        a = a + gamma * (alpha * valid.sum(1) - err.sum(1))
    return q


def normalized_IS(q, scores, base_w, alpha):
    """Mean normalised interval score (units of s) for radius q (..., nt, NH) -- tuning objective."""
    e = scores[None]
    valid = ~np.isnan(e)
    qq = q[..., None]
    v = base_w[None] + 2 * qq + (2 / alpha) * np.maximum(np.where(valid, e, 0) - qq, 0)
    v = np.where(valid, v, 0)
    return v.sum(axis=(-1, -2, -3)) / valid.sum(axis=(-1, -2, -3))
