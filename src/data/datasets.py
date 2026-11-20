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
  * (v2) ``obs`` marks hours whose reading was actually observed (not interpolated, not masked): only these
    hours are scored (calibration scores and evaluation); interpolated values are used as history only.
  * (v2) UCI: the documented daylight-saving artefacts (zero hour on the March change day, double-counted
    hour on the October change day) are masked; BDG2 weather: gaps interpolated over at most 6 h.
  * (v2) the number of buildings/sites removed by each rule is written to ``<cache>/<name>_exclusion.json``.
"""
from __future__ import annotations

import os
import zipfile
import urllib.request
import json

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
    obs = out.notna()
    out = out.interpolate(limit=6, limit_area="inside", axis=0)
    return out, obs


def _filter_flow(e, obs, years, name):
    """Apply the quality rules sequentially and record how many columns each removes."""
    flow = [dict(rule="after stuck-meter masking", n=int(e.shape[1]))]
    miss = np.ones(e.shape[1], bool)
    for yr in years:
        miss &= (e.loc[yr].isna().mean() <= 0.05).values
    flow.append(dict(rule="<= 5 % missing hours in every period", n=int(miss.sum())))
    keep = miss.copy()
    for yr in years:
        keep &= (e.loc[yr].mean() >= 1.0).values
    flow.append(dict(rule="mean load >= 1 kWh/h in every period", n=int(keep.sum())))
    return keep, flow


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
        return dict(load=z["load"], temp=z["temp"], obs=z["obs"], dates=pd.DatetimeIndex(z["dates"]), meta=meta,
                    name="BDG2")
    b = os.path.join(raw_dir, "bdg2")
    e = pd.read_csv(os.path.join(b, "electricity_cleaned.csv"), parse_dates=["timestamp"], index_col=0)
    meta = pd.read_csv(os.path.join(b, "metadata.csv"))
    w = pd.read_csv(os.path.join(b, "weather.csv"), parse_dates=["timestamp"])
    n_raw, sites_raw = e.shape[1], meta.set_index("building_id").loc[list(e.columns), "site_id"].nunique()
    e, obs = _clean_hourly(e)
    keep, flow = _filter_flow(e, obs, ("2016", "2017"), "BDG2")
    flow.insert(0, dict(rule="BDG2 cleaned electricity meters", n=int(n_raw), sites=int(sites_raw)))
    e, obs = e.loc[:, keep], obs.loc[:, keep]
    flow[-1]["sites"] = int(meta.set_index("building_id").loc[list(e.columns), "site_id"].nunique())
    load, dates = _to_cube(e)
    obsc, _ = _to_cube(obs.astype(float))
    obsc = np.nan_to_num(obsc, nan=0.0) > 0.5
    meta = meta.set_index("building_id").loc[list(e.columns)]
    meta.index.name = "building_id"
    meta = meta.reset_index()
    # temperature per site, interpolated, aligned
    temp = np.full_like(load, np.nan)
    full = pd.date_range(dates[0], dates[-1] + pd.Timedelta(hours=23), freq="h")
    site_t = {}
    for site, g in w.groupby("site_id"):
        s = g.drop_duplicates("timestamp").set_index("timestamp")["airTemperature"].reindex(full)
        s = s.interpolate(limit=6, limit_area="inside")
        site_t[site] = s.values.reshape(len(dates), 24)
    for i, site in enumerate(meta["site_id"].values):
        if site in site_t:
            temp[i] = site_t[site]
    meta = meta.rename(columns={"primaryspaceusage": "usage"})
    meta = meta[["building_id", "site_id", "usage", "sqm", "timezone"]].copy()
    meta["usage"] = meta["usage"].fillna("Unknown")
    os.makedirs(cache_dir, exist_ok=True)
    np.savez_compressed(cache, load=load.astype("float32"), temp=temp.astype("float32"), obs=obsc,
                        dates=dates.values)
    meta.to_csv(os.path.join(cache_dir, "bdg2_meta.csv"), index=False)
    json.dump(dict(flow=flow, sites=meta.site_id.value_counts().to_dict(),
                   share_obs=float(obsc.mean()), share_finite=float(np.isfinite(load).mean())),
              open(os.path.join(cache_dir, "BDG2_exclusion.json"), "w"), indent=1)
    return dict(load=load.astype("float32"), temp=temp.astype("float32"), obs=obsc, dates=dates, meta=meta,
                name="BDG2")


def load_uci(raw_dir: str, cache_dir: str) -> dict:
    """UCI clients; 15-min kW readings converted to hourly kWh (sum of 4 readings / 4)."""
    cache = os.path.join(cache_dir, "uci.npz")
    if os.path.exists(cache):
        z = np.load(cache, allow_pickle=True)
        meta = pd.read_csv(os.path.join(cache_dir, "uci_meta.csv"))
        return dict(load=z["load"], temp=None, obs=z["obs"], dates=pd.DatetimeIndex(z["dates"]), meta=meta,
                    name="UCI")
    zf = zipfile.ZipFile(os.path.join(raw_dir, "uci", "eld.zip"))
    with zf.open("LD2011_2014.txt") as f:
        d = pd.read_csv(f, sep=";", decimal=",", index_col=0, parse_dates=True)
    # timestamps mark the END of each 15-min interval: shift back so hour h covers [h, h+1)
    d.index = d.index - pd.Timedelta(minutes=15)
    h = d.resample("h").sum() / 4.0
    h = h.loc["2012-01-01":"2014-12-31"]
    # documented DST artefacts: 01:00-02:00 on the last Sunday of March (zeros) and of October (two hours summed)
    for yr in (2012, 2013, 2014):
        for mon in (3, 10):
            last = pd.Timestamp(yr, mon, 1) + pd.offsets.MonthEnd(0)
            sun = last - pd.Timedelta(days=(last.dayofweek + 1) % 7)
            h.loc[sun + pd.Timedelta(hours=1)] = np.nan
    # clients not yet connected report zeros before their first reading: not a building property -> leave to rules
    n_raw = h.shape[1]
    h, obs = _clean_hourly(h)
    keep, flow = _filter_flow(h, obs, ("2012", "2013", "2014"), "UCI")
    flow.insert(0, dict(rule="UCI clients", n=int(n_raw)))
    h, obs = h.loc[:, keep], obs.loc[:, keep]
    load, dates = _to_cube(h)
    obsc, _ = _to_cube(obs.astype(float))
    obsc = np.nan_to_num(obsc, nan=0.0) > 0.5
    meta = pd.DataFrame({"building_id": h.columns, "site_id": "UCI", "usage": "Unknown", "sqm": np.nan,
                         "timezone": "Europe/Lisbon"})
    os.makedirs(cache_dir, exist_ok=True)
    np.savez_compressed(cache, load=load.astype("float32"), obs=obsc, dates=dates.values)
    meta.to_csv(os.path.join(cache_dir, "uci_meta.csv"), index=False)
    json.dump(dict(flow=flow, share_obs=float(obsc.mean()), share_finite=float(np.isfinite(load).mean())),
              open(os.path.join(cache_dir, "UCI_exclusion.json"), "w"), indent=1)
    return dict(load=load.astype("float32"), temp=None, obs=obsc, dates=dates, meta=meta, name="UCI")
