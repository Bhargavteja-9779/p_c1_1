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
