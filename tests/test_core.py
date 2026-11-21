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


# ---------------------------------------------------------------- review-cycle-1 additions
def test_ssc_stagewise_marginal_coverage_exchangeable_buildings():
    """With exchangeable buildings (heterogeneous error scales), SSC-CQR attains >= 1-alpha coverage averaged
    over new buildings at every stage (Dunn et al. pooled-CDF argument), up to Monte-Carlo error."""
    import numpy as np
    from src.models import calibration as cb
    rng = np.random.default_rng(0)
    alpha, NH, M, nt = 0.1, 6, 150, 3000
    def draw(n):
        scale = np.exp(rng.normal(0, 0.6, size=(n, 1, 1)))
        a = np.abs(rng.normal(0, 1, size=(n, NH, 24))) * scale * 0.1
        e = a - 0.12 * scale  # CQR-like score: negative inside the band
        return a, e
    ac, ec = draw(M)
    at, et = draw(nt)
    s0 = float(np.mean(ac))
    rc = cb.running_scale_ratio(ac, s0, 24.0)
    rt = cb.running_scale_ratio(at, s0, 24.0)
    q = cb.ssc_quantiles(ec / rc[:, :, None], alpha, nt)
    cov = ((et / rt[:, :, None]) <= q[:, :, None]).mean(axis=(0, 2))
    assert np.all(cov >= 1 - alpha - 0.01), cov


def test_tqab_does_not_depend_on_other_targets():
    import numpy as np
    from src.models import calibration as cb
    rng = np.random.default_rng(1)
    NH = 10
    cal = np.abs(rng.normal(size=(40, NH, 24)))
    tgt = np.abs(rng.normal(size=(5, NH, 24)))
    stages = np.arange(1, NH + 1)
    binc, _ = cb.bin_cdfs(cb.cum_counts(cal), stages)
    q1 = cb.tqab_quantiles(tgt, cal, binc.sum(axis=0), 0.1, stages)
    tgt2 = tgt.copy()
    tgt2[1:] *= 25.0  # change all OTHER targets drastically
    q2 = cb.tqab_quantiles(tgt2, cal, binc.sum(axis=0), 0.1, stages)
    assert np.allclose(q1[0], q2[0])


def test_hsc_decay_one_equals_default_and_aci_finite():
    import numpy as np
    from src.models import calibration as cb
    rng = np.random.default_rng(2)
    NH = 8
    cal = np.abs(rng.normal(size=(30, NH, 24)))
    tgt = np.abs(rng.normal(size=(4, NH, 24))) * 3
    stages = np.arange(1, NH + 1)
    binc, _ = cb.bin_cdfs(cb.cum_counts(cal), stages)
    cct = cb.cum_counts(tgt)
    a = cb.hsc_quantiles(cct, binc, None, 0.1, [48], stages)
    b = cb.hsc_quantiles(cct, binc, None, 0.1, [48], stages, decay=1.0)
    c = cb.hsc_quantiles(cct, binc, None, 0.1, [48], stages, decay=0.5)
    assert np.allclose(a, b) and not np.allclose(a, c)
    q, frac = cb.aci_quantiles(tgt, binc.sum(axis=0), 0.1, 0.05, stages, return_capped=True)
    assert np.all(q <= np.nanmax(cal) * 1.01 + 1e-3) and frac >= 0
