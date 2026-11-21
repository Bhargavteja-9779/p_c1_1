"""Data rules: no imputation, training-period eligibility, no onboarding fallback, DST mask."""
import numpy as np
import pandas as pd

from src.data import datasets as d
from src.training import pipeline as pl


def test_no_interpolation_and_long_gap_share():
    v = np.r_[1.0, [np.nan] * 10, 12.0, np.nan, 3.0]
    df = pd.DataFrame({"a": v})
    out = d._clean_hourly(df)["a"].values
    assert np.isnan(out[1:11]).all() and np.isnan(out[12])  # nothing filled
    assert abs(d.long_gap_share(v) - 10 / len(v)) < 1e-12   # 1-h gap not counted, 10-h gap counted


def test_onboard_dates_no_fallback():
    load = np.ones((2, 120, 24))
    load[1, :, :] = np.nan  # building without any valid window
    t0 = pl.onboard_dates(dict(load=load), np.array([0, 1]), (0, 119), np.random.default_rng(0))
    assert t0[0] >= 0 and t0[1] == -1


def test_dst_hours():
    idx = pd.date_range("2014-01-01", "2014-12-31 23:00", freq="h")
    m = d.dst_hours(idx)
    assert m.sum() == 2
    assert set(idx[m]) == {pd.Timestamp("2014-03-30 01:00"), pd.Timestamp("2014-10-26 01:00")}
