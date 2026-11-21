"""Dataset loading and cleaning for BDG2 (electricity) and UCI ElectricityLoadDiagrams20112014.

Both datasets are converted to a common representation:
    load    : float array (n_buildings, n_days, 24), kWh per hour, NaN = missing/invalid
    temp    : float array (n_buildings, n_days, 24) air temperature (deg C) or None
    dates   : DatetimeIndex of the n_days days
    meta    : DataFrame with one row per building (building_id, site_id, usage, ...)

Cleaning rules (identical for all methods):
  * runs of >= 24 consecutive identical readings (zero or constant: outage / stuck meter) are missing;
  * no value is imputed in the stored series (revision 1): missing hours stay NaN, the features are
    NaN-tolerant and missing hours are excluded from every metric, so no reading from the future can
    enter a feature or a ground truth;
  * eligibility (revision 1, no look-ahead): a building is kept if, in the *training/calibration*
    period only, the fraction of missing hours -- not counting gaps of <= 6 h, which are short enough
    to be bridged -- is <= 5 % and its mean load is >= 1 kWh/h. The target (evaluation) period is not
    used for selection; target windows only need >= 80 % valid hours (operational rule, pipeline.py).
  * UCI: the two daylight-saving transition hours per year (zero / doubled readings) are missing.
"""
from __future__ import annotations

import os
import zipfile
import urllib.request

import numpy as np
import pandas as pd

BDG2_BASE = "https://media.githubusercontent.com/media/buds-lab/building-data-genome-project-2/master/data/"
BDG2_FILES = {
    "electricity_cleaned.csv": "meters/cleaned/electricity_cleaned.csv",
    "metadata.csv": "metadata/metadata.csv",
    "weather.csv": "weather/weather.csv",
}
UCI_URL = "https://archive.ics.uci.edu/static/public/321/electricityloaddiagrams20112014.zip"


def download(raw_dir: str) -> None:
    """Download raw files if absent (BDG2: CC-BY-4.0; UCI: CC-BY-4.0)."""
    b = os.path.join(raw_dir, "bdg2")
    u = os.path.join(raw_dir, "uci")
    os.makedirs(b, exist_ok=True)
    os.makedirs(u, exist_ok=True)
    for fname, rel in BDG2_FILES.items():
        p = os.path.join(b, fname)
        if not os.path.exists(p):
            print("downloading", rel)
            urllib.request.urlretrieve(BDG2_BASE + rel, p)
    p = os.path.join(u, "eld.zip")
    if not os.path.exists(p):
        print("downloading UCI ElectricityLoadDiagrams20112014")
        urllib.request.urlretrieve(UCI_URL, p)


def long_gap_share(v: np.ndarray, max_short: int = 6) -> float:
    """Share of hours that are missing and belong to a gap longer than `max_short` hours."""
    m = np.isnan(np.asarray(v, dtype=float))
    if not m.any():
        return 0.0
    d = np.diff(np.concatenate([[0], m.astype(int), [0]]))
    starts, ends = np.where(d == 1)[0], np.where(d == -1)[0]
    n_long = sum(e - s for s, e in zip(starts, ends) if e - s > max_short)
    return n_long / len(m)


def eligible(s: pd.Series) -> bool:
    """Quality rule applied to the training/calibration period of a building."""
    return long_gap_share(s.values) <= 0.05 and np.nanmean(s.values) >= 1.0


def _clean_hourly(df: pd.DataFrame) -> pd.DataFrame:
    """Stuck-meter masking, column-wise (no imputation).

    Runs of >= 24 consecutive *identical* readings (zeros or any constant value, i.e. a flat-lined /
    stuck meter) are set to missing.
    """
    df = df.astype("float64")
    out = df.copy()
    for c in df.columns:
        v = df[c].values.copy()
        same = np.concatenate([[False], np.diff(v) == 0])  # equal to previous reading
        if same.any():
            d = np.diff(np.concatenate([[0], same.astype(int), [0]]))
            starts, ends = np.where(d == 1)[0], np.where(d == -1)[0]
            for s_, e_ in zip(starts, ends):
                if e_ - s_ + 1 >= 24:  # run of >= 24 identical values incl. the first one
                    v[s_ - 1:e_] = np.nan
        out[c] = v
    return out


def _to_cube(df: pd.DataFrame) -> tuple[np.ndarray, pd.DatetimeIndex]:
    """(hours, buildings) -> (buildings, days, 24); requires full days."""
    df = df.loc[df.index.hour.notna()]
    days = pd.DatetimeIndex(sorted(set(df.index.normalize())))
    full = pd.date_range(days[0], days[-1] + pd.Timedelta(hours=23), freq="h")
    df = df.reindex(full)
    arr = df.values.T.reshape(df.shape[1], len(days), 24)
    return arr, days


def load_bdg2(raw_dir: str, cache_dir: str) -> dict:
    cache = os.path.join(cache_dir, "bdg2_r1.npz")
    if os.path.exists(cache):
        z = np.load(cache, allow_pickle=True)
        meta = pd.read_csv(os.path.join(cache_dir, "bdg2_r1_meta.csv"))
        return dict(load=z["load"], temp=z["temp"], dates=pd.DatetimeIndex(z["dates"]), meta=meta, name="BDG2")
    b = os.path.join(raw_dir, "bdg2")
    e = pd.read_csv(os.path.join(b, "electricity_cleaned.csv"), parse_dates=["timestamp"], index_col=0)
    meta = pd.read_csv(os.path.join(b, "metadata.csv"))
    w = pd.read_csv(os.path.join(b, "weather.csv"), parse_dates=["timestamp"])
    e = _clean_hourly(e)
    keep = [eligible(e.loc["2016", c]) for c in e.columns]  # training/calibration year only
    e = e.loc[:, keep]
    load, dates = _to_cube(e)
    meta = meta.set_index("building_id").loc[list(e.columns)]
    meta.index.name = "building_id"
    meta = meta.reset_index()
    # temperature per site, interpolated, aligned
    temp = np.full_like(load, np.nan)
    full = pd.date_range(dates[0], dates[-1] + pd.Timedelta(hours=23), freq="h")
    site_t = {}
    for site, g in w.groupby("site_id"):
        s = g.drop_duplicates("timestamp").set_index("timestamp")["airTemperature"].reindex(full)
        s = s.interpolate(limit_direction="both")
        site_t[site] = s.values.reshape(len(dates), 24)
    for i, site in enumerate(meta["site_id"].values):
        if site in site_t:
            temp[i] = site_t[site]
    meta = meta.rename(columns={"primaryspaceusage": "usage"})
    meta = meta[["building_id", "site_id", "usage", "sqm", "timezone"]].copy()
    meta["usage"] = meta["usage"].fillna("Unknown")
    os.makedirs(cache_dir, exist_ok=True)
    np.savez_compressed(cache, load=load.astype("float32"), temp=temp.astype("float32"), dates=dates.values)
    meta.to_csv(os.path.join(cache_dir, "bdg2_r1_meta.csv"), index=False)
    return dict(load=load.astype("float32"), temp=temp.astype("float32"), dates=dates, meta=meta, name="BDG2")


def dst_hours(idx: pd.DatetimeIndex) -> np.ndarray:
    """UCI: hour 01:00 on the last Sunday of March (zeros) and of October (two hours aggregated)."""
    m = np.zeros(len(idx), dtype=bool)
    for yr in sorted(set(idx.year)):
        for month in (3, 10):
            last = pd.Timestamp(yr, month, 1) + pd.offsets.MonthEnd(0)
            sun = last - pd.Timedelta(days=(last.dayofweek - 6) % 7)
            m |= idx == sun + pd.Timedelta(hours=1)
    return m


def load_uci(raw_dir: str, cache_dir: str) -> dict:
    """UCI clients; 15-min kW readings converted to hourly kWh (sum of 4 readings / 4)."""
    cache = os.path.join(cache_dir, "uci_r1.npz")
    if os.path.exists(cache):
        z = np.load(cache, allow_pickle=True)
        meta = pd.read_csv(os.path.join(cache_dir, "uci_r1_meta.csv"))
        return dict(load=z["load"], temp=None, dates=pd.DatetimeIndex(z["dates"]), meta=meta, name="UCI")
    zf = zipfile.ZipFile(os.path.join(raw_dir, "uci", "eld.zip"))
    with zf.open("LD2011_2014.txt") as f:
        d = pd.read_csv(f, sep=";", decimal=",", index_col=0, parse_dates=True)
    # timestamps mark the END of each 15-min interval: shift back so hour h covers [h, h+1)
    d.index = d.index - pd.Timedelta(minutes=15)
    h = d.resample("h").sum() / 4.0
    h = h.loc["2012-01-01":"2014-12-31"]
    h.loc[dst_hours(h.index)] = np.nan
    h = _clean_hourly(h)
    keep = [eligible(h.loc["2012":"2013", c]) for c in h.columns]  # training/calibration years only
    h = h.loc[:, keep]
    load, dates = _to_cube(h)
    meta = pd.DataFrame({"building_id": h.columns, "site_id": "UCI", "usage": "Unknown", "sqm": np.nan,
                         "timezone": "Europe/Lisbon"})
    os.makedirs(cache_dir, exist_ok=True)
    np.savez_compressed(cache, load=load.astype("float32"), dates=dates.values)
    meta.to_csv(os.path.join(cache_dir, "uci_r1_meta.csv"), index=False)
    return dict(load=load.astype("float32"), temp=None, dates=dates, meta=meta, name="UCI")
