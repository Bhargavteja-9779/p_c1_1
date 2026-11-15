"""Unit tests: leakage guards for features, correctness of conformal calibration primitives."""
import numpy as np
import pandas as pd

from src.preprocessing import features as fe
from src.models import calibration as cb
from src.evaluation import metrics as mt


def _toy(nb=3, nd=60, seed=0):
    rng = np.random.default_rng(seed)
    load = (rng.random((nb, nd, 24)) * 10 + 5).astype(np.float32)
    temp = (rng.random((nb, nd, 24)) * 20).astype(np.float32)
    dates = pd.date_range("2016-01-01", periods=nd, freq="D")
    return load, temp, dates


def test_features_use_only_history_window():
    load, temp, dates = _toy()
    b, t, h = np.array([1]), np.array([30]), np.array([5])
    X0, y0, s0 = fe.build(load, temp, dates, b, t, h, True)
    L2 = load.copy()
    L2[1, t[0]:, :] += 1000.0          # future (target day and later) changed
    L2[1, : t[0] - h[0], :] += 1000.0  # data before onboarding window changed
    X1, _, s1 = fe.build(L2, temp, dates, b, t, h, True)
    assert np.allclose(np.nan_to_num(X0, nan=-9), np.nan_to_num(X1, nan=-9))
    assert np.allclose(s0, s1)


def test_lags_masked_beyond_history():
    load, temp, dates = _toy()
    names = fe.feature_names(False)
    X, _, _ = fe.build(load, None, dates, np.array([0]), np.array([30]), np.array([3]), False)
    assert np.isnan(X[:, names.index("lag7d")]).all()
    assert not np.isnan(X[:, names.index("lag2d")]).any()


def test_scale_definition():
    load, temp, dates = _toy()
    _, _, s = fe.build(load, None, dates, np.array([2]), np.array([40]), np.array([10]), False)
    assert np.isclose(s[0], load[2, 33:40].mean(), rtol=1e-5)


def test_pooled_quantile_matches_split_conformal():
    rng = np.random.default_rng(1)
    sc = rng.exponential(size=(50, 56, 24)).astype(np.float32)
    stages = np.arange(1, 57)
    cc = cb.cum_counts(sc)
    binc, _ = cb.bin_cdfs(cc, stages)
    q = cb.pooled_quantile(binc, 0.1, stage_matched=False)[0]
    v = np.sort(sc.ravel())
    k = int(np.ceil(0.9 * (len(v) + 1))) - 1
    exact = v[k]
    # grid quantile is conservative and within grid resolution
    assert q >= exact - 1e-9 and q <= exact * 1.01 + 1e-4


def test_hsc_limits():
    rng = np.random.default_rng(2)
    cal = rng.exponential(size=(40, 56, 24)).astype(np.float32)
    tgt = (3 * rng.exponential(size=(5, 56, 24))).astype(np.float32)
    stages = np.arange(1, 57)
    binc, _ = cb.bin_cdfs(cb.cum_counts(cal), stages)
    cct = cb.cum_counts(tgt)
    q = cb.hsc_quantiles(cct, binc, None, 0.1, [np.inf, 1e9, 24, 0], stages)
    # kappa=inf equals pooled stage-matched quantile
    qp = cb.pooled_quantile(binc, 0.1, True)[cb.stage_bin(stages)]
    assert np.allclose(q[0], qp[None, :])
    # huge kappa ~ prior; small kappa adapts toward 3x larger target scores late in the window
    assert np.allclose(q[1, :, 0], q[0, :, 0], rtol=0.02)
    assert (q[2, :, -1] > 2 * q[0, :, -1]).all()
    # kappa=0: no own scores at stage 1 -> infinite radius
    assert np.all(q[3, :, 0] >= cb.INF_RADIUS * 0.999)


def test_interval_metrics():
    y = np.ones((2, 56, 24))
    lo, hi = y * 0.5, y * 1.5
    m, sc, _ = mt.interval_metrics(y, lo, hi, 0.1)
    assert np.allclose(m["coverage"], 1) and np.allclose(m["rel_width"], 1.0)
    hi2 = y * 0.9
    m2, _, _ = mt.interval_metrics(y, lo, hi2, 0.1)
    assert np.allclose(m2["coverage"], 0)
    assert np.allclose(m2["rel_IS"], 0.4 + 20 * 0.1)


def test_metrics_ignore_undefined_intervals():
    y = np.ones((1, 56, 24))
    lo, hi = y * 0.5, y * 1.5
    lo[0, 3, :] = np.nan  # forecast not issued on stage 4
    m, _, _ = mt.interval_metrics(y, lo, hi, 0.1)
    assert np.allclose(m["coverage"], 1.0) and np.isfinite(m["rel_IS"]).all()
