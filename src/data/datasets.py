"""Dataset loading and cleaning for BDG2 (electricity) and UCI ElectricityLoadDiagrams20112014.

Both datasets are converted to a common representation:
    load    : float array (n_buildings, n_days, 24), kWh per hour, NaN = missing/invalid
    temp    : float array (n_buildings, n_days, 24) air temperature (deg C) or None
    dates   : DatetimeIndex of the n_days days
    meta    : DataFrame with one row per building (building_id, site_id, usage, ...)

Cleaning rules (pre-specified, identical for all methods):
  * gaps of <= 6 consecutive hours are linearly interpolated;
  * runs of >= 24 consecutive identical readings (zero or constant: outage / stuck meter) are missing;
  * a building is kept if, in every period used (train/calibration/test year), the fraction
    of missing hours is <= 5 % and its mean load is >= 1 kWh/h.
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


def _clean_hourly(df: pd.DataFrame) -> pd.DataFrame:
    """Stuck-meter masking and short-gap interpolation, column-wise.

    Runs of >= 24 consecutive *identical* readings (zeros or any constant value, i.e. a flat-lined /
    stuck meter) are set to missing; then gaps of <= 6 h are linearly interpolated.
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
    out = out.interpolate(limit=6, limit_area="inside", axis=0)
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
    cache = os.path.join(cache_dir, "bdg2.npz")
    if os.path.exists(cache):
        z = np.load(cache, allow_pickle=True)
        meta = pd.read_csv(os.path.join(cache_dir, "bdg2_meta.csv"))
        return dict(load=z["load"], temp=z["temp"], dates=pd.DatetimeIndex(z["dates"]), meta=meta, name="BDG2")
    b = os.path.join(raw_dir, "bdg2")
    e = pd.read_csv(os.path.join(b, "electricity_cleaned.csv"), parse_dates=["timestamp"], index_col=0)
    meta = pd.read_csv(os.path.join(b, "metadata.csv"))
    w = pd.read_csv(os.path.join(b, "weather.csv"), parse_dates=["timestamp"])
    e = _clean_hourly(e)
    keep = []
    for c in e.columns:
        ok = True
        for yr in ("2016", "2017"):
            s = e.loc[yr, c]
            if s.isna().mean() > 0.05 or s.mean() < 1.0:
                ok = False
        keep.append(ok)
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
    meta.to_csv(os.path.join(cache_dir, "bdg2_meta.csv"), index=False)
    return dict(load=load.astype("float32"), temp=temp.astype("float32"), dates=dates, meta=meta, name="BDG2")


def load_uci(raw_dir: str, cache_dir: str) -> dict:
    """UCI clients; 15-min kW readings converted to hourly kWh (sum of 4 readings / 4)."""
    cache = os.path.join(cache_dir, "uci.npz")
    if os.path.exists(cache):
        z = np.load(cache, allow_pickle=True)
        meta = pd.read_csv(os.path.join(cache_dir, "uci_meta.csv"))
        return dict(load=z["load"], temp=None, dates=pd.DatetimeIndex(z["dates"]), meta=meta, name="UCI")
    zf = zipfile.ZipFile(os.path.join(raw_dir, "uci", "eld.zip"))
    with zf.open("LD2011_2014.txt") as f:
        d = pd.read_csv(f, sep=";", decimal=",", index_col=0, parse_dates=True)
    # timestamps mark the END of each 15-min interval: shift back so hour h covers [h, h+1)
    d.index = d.index - pd.Timedelta(minutes=15)
    h = d.resample("h").sum() / 4.0
    h = h.loc["2012-01-01":"2014-12-31"]
    h = _clean_hourly(h)
    keep = []
    for c in h.columns:
        ok = True
        for yr in ("2012", "2013", "2014"):
            s = h.loc[yr, c]
            if s.isna().mean() > 0.05 or s.mean() < 1.0:
                ok = False
        keep.append(ok)
    h = h.loc[:, keep]
    load, dates = _to_cube(h)
    meta = pd.DataFrame({"building_id": h.columns, "site_id": "UCI", "usage": "Unknown", "sqm": np.nan,
                         "timezone": "Europe/Lisbon"})
    os.makedirs(cache_dir, exist_ok=True)
    np.savez_compressed(cache, load=load.astype("float32"), dates=dates.values)
    meta.to_csv(os.path.join(cache_dir, "uci_meta.csv"), index=False)
    return dict(load=load.astype("float32"), temp=None, dates=dates, meta=meta, name="UCI")
