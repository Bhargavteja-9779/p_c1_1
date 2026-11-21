"""Per-building interval and point-forecast metrics.

Unit of analysis = target building. For building b with valid hourly truths y over its 56-day
onboarding window and interval [lo, hi]:
  coverage_b   = mean 1{lo <= y <= hi}
  rel_width_b  = mean(hi - lo) / mean(y)
  rel_IS_b     = mean( (hi-lo) + 2/alpha*(lo-y)_+ + 2/alpha*(y-hi)_+ ) / mean(y)   (Winkler / interval score,
                 Gneiting & Raftery 2007; strictly proper for the central (1-alpha) interval)
Stage-resolved versions use the 24 hourly values of each onboarding stage h.
"""
from __future__ import annotations

import numpy as np

EARLY = 7  # stages h <= 7 = first week after metering starts


def interval_metrics(y, lo, hi, alpha):
    """y, lo, hi: (nt, NH, 24) kWh. Returns dict of per-building arrays and stage curves."""
    valid = ~np.isnan(y) & np.isfinite(lo) & np.isfinite(hi)
    yv = np.where(valid, y, 0.0)
    lo = np.where(valid, lo, 0.0)
    hi = np.where(valid, hi, 0.0)
    cov = ((lo <= yv) & (yv <= hi)) & valid
    w = np.where(valid, hi - lo, 0.0)
    pen = (2 / alpha) * (np.maximum(lo - yv, 0) + np.maximum(yv - hi, 0))
    IS = np.where(valid, w + pen, 0.0)
    n = valid.sum(axis=(1, 2))
    ybar = yv.sum(axis=(1, 2)) / np.maximum(n, 1)
    nh = np.arange(1, y.shape[1] + 1)
    early = nh <= EARLY
    ne = valid[:, early].sum(axis=(1, 2))
    out = dict(
        coverage=cov.sum(axis=(1, 2)) / np.maximum(n, 1),
        coverage_early=cov[:, early].sum(axis=(1, 2)) / np.maximum(ne, 1),
        coverage_late=cov[:, ~early].sum(axis=(1, 2)) / np.maximum(n - ne, 1),
        rel_width=w.sum(axis=(1, 2)) / np.maximum(n, 1) / ybar,
        rel_IS=IS.sum(axis=(1, 2)) / np.maximum(n, 1) / ybar,
        rel_IS_early=IS[:, early].sum(axis=(1, 2)) / np.maximum(ne, 1) / ybar,
        n_valid=n,
        # operational measures (Addendum A): tail exceedances, capacity-headroom cost components,
        # day-block standard error of the building's coverage
        up_exc=((yv > hi) & valid).sum(axis=(1, 2)) / np.maximum(n, 1),
        lo_exc=((yv < lo) & valid).sum(axis=(1, 2)) / np.maximum(n, 1),
        U_rel=np.where(valid, hi, 0.0).sum(axis=(1, 2)) / np.maximum(n, 1) / ybar,
        viol_rel=np.where(valid, np.maximum(yv - hi, 0), 0.0).sum(axis=(1, 2)) / np.maximum(n, 1) / ybar,
        cov_se_day=_day_block_se(cov, valid),
    )
    # per-building weekly coverage (weeks 1..8 of the onboarding window) -> days-to-reliable analysis
    nwk = y.shape[1] // 7
    for w in range(nwk):
        sl = slice(7 * w, 7 * (w + 1))
        nw = valid[:, sl].sum(axis=(1, 2))
        out[f"cov_w{w + 1}"] = np.where(nw > 0, cov[:, sl].sum(axis=(1, 2)) / np.maximum(nw, 1), np.nan)
    stage_cov = cov.sum(axis=2) / np.maximum(valid.sum(axis=2), 1)  # (nt, NH)
    stage_IS = IS.sum(axis=2) / np.maximum(valid.sum(axis=2), 1) / ybar[:, None]
    return out, stage_cov, stage_IS


def _day_block_se(cov, valid):
    """Standard error of a building's window coverage from its daily coverage values (day blocks keep the
    within-day dependence of misses): s.d. of daily coverage / sqrt(#days with data)."""
    nd = valid.sum(axis=2)
    dc = np.where(nd > 0, cov.sum(axis=2) / np.maximum(nd, 1), np.nan)
    k = (nd > 0).sum(axis=1)
    sd = np.nanstd(dc, axis=1, ddof=1)
    return sd / np.sqrt(np.maximum(k, 1))


def point_metrics(y, yhat):
    valid = ~np.isnan(y) & np.isfinite(yhat)
    e = np.where(valid, yhat - y, 0.0)
    n = valid.sum(axis=(1, 2))
    ybar = np.where(valid, y, 0).sum(axis=(1, 2)) / np.maximum(n, 1)
    rmse = np.sqrt((e ** 2).sum(axis=(1, 2)) / np.maximum(n, 1))
    mae = np.abs(e).sum(axis=(1, 2)) / np.maximum(n, 1)
    return dict(cvrmse=rmse / ybar, nmae=mae / ybar)


def summarize(cov, nominal):
    """Aggregate per-building coverage into reliability statistics."""
    cov = np.asarray(cov)
    return dict(
        mean_cov=float(np.mean(cov)),
        macd=float(np.mean(np.abs(cov - nominal))),          # mean absolute coverage deviation
        under_rate=float(np.mean(cov < nominal - 0.05)),     # share of buildings under-covered by >5 pp
        p10_cov=float(np.quantile(cov, 0.10)),
    )


def oracle_reference(scores, valid, alpha, n_boot=400, block=7, seed=0, margin=0.05):
    """Method-independent sampling-noise reference (review cycle 2, #3).

    For each building an *oracle* radius is set to its own in-window (1-alpha) score quantile, so its window
    coverage is nominal by construction while its daily misses keep the building's real autocorrelation.
    A circular moving-block bootstrap with `block`-day blocks of the oracle's daily (hits, valid) counts gives the
    probability that a perfectly calibrated building with these error dynamics shows window coverage, a single
    week's coverage, or the worst of its 8 weeks below (1 - alpha - margin).
    scores: (nt, NH, 24) CQR scores (NaN = missing); valid: (nt, NH, 24) evaluation mask.
    Returns dict of (nt,) arrays: ref_under_win, ref_under_week, ref_anyweek.
    """
    rng = np.random.default_rng(seed)
    nt, NH, _ = scores.shape
    e = np.where(valid, scores, np.nan)
    thr = 1 - alpha - margin
    out = {k: np.full(nt, np.nan) for k in ("ref_under_win", "ref_under_week", "ref_anyweek")}
    nb = int(np.ceil(NH / block))
    starts = rng.integers(0, NH, size=(n_boot, nb))
    idx = (starts[:, :, None] + np.arange(block)[None, None, :]).reshape(n_boot, -1)[:, :NH] % NH  # (n_boot, NH)
    for i in range(nt):
        v = e[i][~np.isnan(e[i])]
        if len(v) < 24:
            continue
        k = int(np.ceil((1 - alpha) * len(v))) - 1
        q = np.sort(v)[min(k, len(v) - 1)]
        hits = np.nansum(e[i] <= q, axis=1).astype(float)          # (NH,) covered hours per day
        nval = (~np.isnan(e[i])).sum(axis=1).astype(float)         # (NH,) valid hours per day
        H, V = hits[idx], nval[idx]                                # (n_boot, NH)
        win = H.sum(1) / np.maximum(V.sum(1), 1)
        out["ref_under_win"][i] = np.mean(win < thr)
        wk_h = H[:, :NH - NH % 7].reshape(n_boot, -1, 7).sum(2)
        wk_v = V[:, :NH - NH % 7].reshape(n_boot, -1, 7).sum(2)
        wk = np.where(wk_v > 0, wk_h / np.maximum(wk_v, 1), np.nan)
        out["ref_under_week"][i] = np.nanmean(wk < thr)
        out["ref_anyweek"][i] = np.mean(np.nanmin(wk, axis=1) < thr)
    return out
