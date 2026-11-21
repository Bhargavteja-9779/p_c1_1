"""Unit tests: leakage guards for features, correctness of conformal calibration primitives."""
import numpy as np
import pandas as pd

from src.preprocessing import features as fe
from src.models import calibration as cb
from src.evaluation import metrics as mt
from src.training import pipeline as pl


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


# ---------------------------------------------------------------- tests added after the code audit
def test_neighbours_nan_safe_and_self_excluded():
    rng = np.random.default_rng(3)
    zc = rng.normal(size=(12, 4))
    zc_nan = zc.copy()
    zc_nan[5, 2] = np.nan  # undefined descriptor of calibration building 5
    zt = rng.normal(size=(7, 4))
    nb = cb.neighbours(zt, zc_nan, 3)
    assert not (nb == 5).any()  # never chosen
    # same neighbours as when building 5 is removed (indices mapped back)
    keep = np.array([i for i in range(12) if i != 5])
    nb_ref = keep[cb.neighbours(zt, zc[keep], 3)]
    assert np.array_equal(np.sort(nb, axis=1), np.sort(nb_ref, axis=1))
    # LOBO: self never selected, even with NaN present
    nb_self = cb.neighbours(zc_nan, zc_nan, 4, exclude_self=True)
    assert not (nb_self == np.arange(12)[:, None]).any()


def test_prior_ignores_empty_bins():
    rng = np.random.default_rng(4)
    cal = rng.exponential(size=(20, 56, 24)).astype(np.float32)
    cal_empty = cal.copy()
    cal_empty[3, 0, :] = np.nan  # building 3 has no score in stage bin {1}
    stages = np.arange(1, 57)
    b_full, _ = cb.bin_cdfs(cb.cum_counts(cal[np.arange(20) != 3]), stages)
    b_emp, _ = cb.bin_cdfs(cb.cum_counts(cal_empty), stages)
    tgt = cb.cum_counts(rng.exponential(size=(4, 56, 24)).astype(np.float32))
    q_ref = cb.hsc_quantiles(tgt, b_full, None, 0.1, [24, np.inf], stages)
    q_emp = cb.hsc_quantiles(tgt, b_emp, None, 0.1, [24, np.inf], stages)
    # stage 1: building 3 is ignored -> prior identical to the one without building 3
    assert np.allclose(q_ref[0][:, 0], q_emp[0][:, 0])
    assert (q_emp < cb.INF_RADIUS * 0.999).all()


def test_own_defined_from_counts_and_qshrink_keeps_large_own_quantile():
    assert not cb.own_defined(8, 0.1) and cb.own_defined(9, 0.1)
    stages = np.arange(1, 57)
    own = np.full((1, 56, 24), 80.0, dtype=np.float32)  # extreme but plentiful own scores
    cc = cb.cum_counts(own)
    q = cb.qshrink_quantiles(cc, np.full(56, 0.5), 0.1, 168, stages)
    assert q[0, 10] > 30  # own quantile (80) enters with weight n/(n+168), not the pooled fallback


def test_aci_level_below_zero_gives_noninverted_interval():
    rng = np.random.default_rng(5)
    prior = cb.cum_counts(rng.exponential(size=(30, 56, 24)).astype(np.float32))
    binc, _ = cb.bin_cdfs(prior, np.arange(1, 57))
    tgt = np.zeros((2, 56, 24), dtype=np.float32)  # always covered -> alpha_h drifts above 1 with large gamma
    q = cb.aci_quantiles(tgt, binc.sum(axis=0), 0.1, 0.05, np.arange(1, 57))
    assert (q >= 0).all()


# ---------------------------------------------------------------- revision 1 (review cycle 1)
def _toy_ds(name="BDG2"):
    import pandas as pd
    dates = pd.date_range("2016-01-01", "2017-12-31", freq="D") if name == "BDG2" else \
        pd.date_range("2012-01-01", "2014-12-31", freq="D")
    n = len(dates)
    return dict(name=name, dates=dates, load=np.ones((3, n, 24), np.float32), temp=None)


def test_out_of_time_windows_are_ordered():
    """training period < every calibration window < every target window."""
    for name in ["BDG2", "UCI"]:
        ds = _toy_ds(name)
        tr, _ = pl.periods(ds)
        cal, tgt = pl.onboard_periods(ds)
        rng = np.random.default_rng(0)
        t0c = pl.onboard_dates(ds, np.arange(3), cal, rng)
        t0t = pl.onboard_dates(ds, np.arange(3), tgt, rng)
        assert tr[1] < t0c.min()
        assert (t0c + pl.NH).max() < t0t.min()
        assert (t0t + pl.NH).max() <= tgt[1]


def test_switch_rule_uses_pooled_then_own():
    stages = np.arange(1, 57)
    own = np.full((1, 56, 24), 3.0, dtype=np.float32)
    q = pl.switch_quantiles(cb.cum_counts(own), np.full((1, 56), 0.5), 0.1, 7)
    assert np.allclose(q[0, :7], 0.5)  # stages 1..7: fewer than 7 days of own scores
    assert np.all(q[0, 7:] > 2.9)  # own radius afterwards


def test_aci_clip_bounds_working_level():
    rng = np.random.default_rng(1)
    prior = cb.cum_counts(rng.exponential(size=(30, 56, 24)).astype(np.float32))
    binc, _ = cb.bin_cdfs(prior, np.arange(1, 57))
    tgt = np.full((1, 56, 24), 1e3, dtype=np.float32)  # always missed -> level would go to 1 (infinite radius)
    q = cb.aci_quantiles(tgt, binc.sum(axis=0), 0.1, 0.05, np.arange(1, 57), clip=(0.005, 0.5))
    assert (q < cb.INF_RADIUS * 0.999).all()


def test_interpolated_truth_excluded():
    import pandas as pd
    df = pd.DataFrame({"a": [1.0, np.nan, np.nan, 4.0, 5.0]})
    from src.data.datasets import _clean_hourly
    out = _clean_hourly(df)
    assert out.attrs["interp"]["a"].tolist() == [False, True, True, False, False]
