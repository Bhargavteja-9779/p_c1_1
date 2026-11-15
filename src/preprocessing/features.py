"""Cold-start feature construction for day-ahead (24 h) load forecasting.

For a building b, forecast day t and available history length h (days t-h .. t-1, i.e. only
data measured *after* the building was metered), we build features for the 24 hours of day t.
Every load-derived feature is divided by the scale

    s_{b,t,h} = mean(load[b, t-min(h,7) : t, :])          (Eq. 1 in the manuscript)

so that a single global model can be shared across buildings of very different size.
Nothing from day t or later, and nothing earlier than t-h, is ever used (leakage guard; unit-tested).
"""
from __future__ import annotations

import warnings

import numpy as np

H_CAP = 28  # history beyond 28 days does not change the features
FEATURES_BASE = [
    "hour", "dow", "weekend", "month", "hist_len",
    "lag1d", "lag2d", "lag7d", "lag14d",
    "prev_mean", "prev_max", "prev_min",
    "hour_prof", "daytype_prof", "dowhour_prof", "daily_var",
]
FEATURES_WEATHER = ["temp", "temp_daymean", "temp_dev_hist", "temp_dev_prev"]


def feature_names(use_weather: bool) -> list[str]:
    return FEATURES_BASE + (FEATURES_WEATHER if use_weather else [])


def _nanmean(a, axis):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        return np.nanmean(a, axis=axis)


def build(load: np.ndarray, temp: np.ndarray | None, dates, b_idx: np.ndarray, t_idx: np.ndarray,
          h: np.ndarray, use_weather: bool):
    """Return X (n*24, F), y (n*24,), scale (n,) for samples (b_idx[i], t_idx[i], h[i]).

    Rows are ordered sample-major then hour (row = i*24 + hour).
    """
    n = len(b_idx)
    b_idx = np.asarray(b_idx)
    t_idx = np.asarray(t_idx)
    h = np.asarray(h)
    assert np.all(t_idx - h >= 0), "history window starts before data"
    hc = np.minimum(h, H_CAP)
    F = feature_names(use_weather)
    X = np.full((n, 24, len(F)), np.nan, dtype=np.float32)
    y = load[b_idx, t_idx, :]  # (n,24)

    # history stack for up to H_CAP days: hist[:, k-1, :] = load[b, t-k, :] if k<=h else NaN
    K = int(hc.max())
    hist = np.full((n, K, 24), np.nan, dtype=np.float32)
    for k in range(1, K + 1):
        m = hc >= k
        hist[m, k - 1, :] = load[b_idx[m], t_idx[m] - k, :]
    # scale: mean over last min(h,7) days
    k7 = np.minimum(hc, 7)
    mask7 = (np.arange(K)[None, :] < k7[:, None])
    h7 = np.where(mask7[:, :, None], hist, np.nan)
    s = _nanmean(h7.reshape(n, -1), axis=1)
    s = np.where(s > 0, s, np.nan).astype(np.float32)
    ns = hist / s[:, None, None]

    dts = dates[t_idx]
    dow = dts.dayofweek.values
    month = dts.month.values
    col = {f: i for i, f in enumerate(F)}
    X[:, :, col["hour"]] = np.arange(24)[None, :]
    X[:, :, col["dow"]] = dow[:, None]
    X[:, :, col["weekend"]] = (dow >= 5)[:, None]
    X[:, :, col["month"]] = month[:, None]
    X[:, :, col["hist_len"]] = hc[:, None]
    X[:, :, col["lag1d"]] = ns[:, 0, :]
    for name, k in (("lag2d", 2), ("lag7d", 7), ("lag14d", 14)):
        if K >= k:
            X[:, :, col[name]] = ns[:, k - 1, :]
    X[:, :, col["prev_mean"]] = _nanmean(ns[:, 0, :], axis=1)[:, None]
    with np.errstate(invalid="ignore"):
        X[:, :, col["prev_max"]] = np.nanmax(np.where(np.isnan(ns[:, 0, :]), -np.inf, ns[:, 0, :]), axis=1)[:, None]
        X[:, :, col["prev_min"]] = np.nanmin(np.where(np.isnan(ns[:, 0, :]), np.inf, ns[:, 0, :]), axis=1)[:, None]
    X[:, :, col["prev_max"]][~np.isfinite(X[:, :, col["prev_max"]])] = np.nan
    X[:, :, col["prev_min"]][~np.isfinite(X[:, :, col["prev_min"]])] = np.nan
    X[:, :, col["hour_prof"]] = _nanmean(ns, axis=1)
    # day-type (weekday/weekend) profile over history
    hist_dow = (dow[:, None] - np.arange(1, K + 1)[None, :]) % 7
    same_type = ((hist_dow >= 5) == (dow[:, None] >= 5)) & (np.arange(K)[None, :] < hc[:, None])
    X[:, :, col["daytype_prof"]] = _nanmean(np.where(same_type[:, :, None], ns, np.nan), axis=1)
    # same-dow profile (k = 7,14,21,28)
    if K >= 7:
        idx = [k - 1 for k in (7, 14, 21, 28) if k <= K]
        X[:, :, col["dowhour_prof"]] = _nanmean(ns[:, idx, :], axis=1)
    # day-to-day variability of normalised profile
    if K >= 2:
        dd = np.abs(ns[:, 1:, :] - ns[:, :-1, :])
        X[:, :, col["daily_var"]] = _nanmean(dd.reshape(n, -1), axis=1)[:, None]
    if use_weather:
        assert temp is not None
        tt = temp[b_idx, t_idx, :]
        X[:, :, col["temp"]] = tt
        tdm = tt.mean(axis=1)
        X[:, :, col["temp_daymean"]] = tdm[:, None]
        th = np.full((n, K), np.nan, dtype=np.float32)
        for k in range(1, K + 1):
            m = hc >= k
            th[m, k - 1] = temp[b_idx[m], t_idx[m] - k, :].mean(axis=1)
        th7 = np.where(np.arange(K)[None, :] < k7[:, None], th, np.nan)
        X[:, :, col["temp_dev_hist"]] = (tdm - _nanmean(th7, axis=1))[:, None]
        X[:, :, col["temp_dev_prev"]] = (tdm - th[:, 0])[:, None]
    X = X.reshape(n * 24, len(F))
    return X, y.reshape(-1), s


def descriptor(load: np.ndarray, b_idx: np.ndarray, t_idx: np.ndarray, h: np.ndarray):
    """Similarity descriptor of a building from its own first h days (used by the localised prior).

    z = [normalised mean daily profile (24), mean |day-to-day change| (1), log mean load (1)].
    Computed from days t-min(h,28) .. t-1 only.
    """
    n = len(b_idx)
    hc = np.minimum(np.asarray(h), H_CAP)
    K = int(hc.max())
    hist = np.full((n, K, 24), np.nan, dtype=np.float32)
    for k in range(1, K + 1):
        m = hc >= k
        hist[m, k - 1, :] = load[b_idx[m], t_idx[m] - k, :]
    mu = _nanmean(hist.reshape(n, -1), axis=1)
    prof = _nanmean(hist, axis=1) / mu[:, None]
    if K >= 2:
        dv = _nanmean((np.abs(hist[:, 1:, :] - hist[:, :-1, :]) / mu[:, None, None]).reshape(n, -1), axis=1)
    else:
        dv = np.zeros(n)
    dv = np.where(np.isnan(dv), 0.0, dv)
    z = np.concatenate([np.nan_to_num(prof, nan=1.0), dv[:, None], np.log(np.maximum(mu, 1e-3))[:, None]], axis=1)
    return z.astype(np.float32)
