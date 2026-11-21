"""Data audit (revision 1, reviewer R5): attrition of the quality filter per rule and site, retained vs
excluded buildings, interpolated weather share per site, and load-temperature lag alignment per site.
Writes tables/T_attrition.{md,csv}, tables/T_site_audit.{md,csv}."""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

from src.data.datasets import _clean_hourly

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW = os.path.join(ROOT, "data", "raw", "bdg2")
TAB = os.path.join(ROOT, "tables")


def run():
    e = pd.read_csv(os.path.join(RAW, "electricity_cleaned.csv"), parse_dates=["timestamp"], index_col=0)
    meta = pd.read_csv(os.path.join(RAW, "metadata.csv")).set_index("building_id")
    w = pd.read_csv(os.path.join(RAW, "weather.csv"), parse_dates=["timestamp"])
    raw_miss = {yr: e.loc[yr].isna().mean() for yr in ("2016", "2017")}
    c = _clean_hourly(e)
    c.attrs.pop("interp", None)
    rows = []
    for b in e.columns:
        r = dict(building_id=b, site_id=meta.loc[b, "site_id"], usage=meta.loc[b, "primaryspaceusage"],
                 sqm=meta.loc[b, "sqm"])
        for yr in ("2016", "2017"):
            s = c.loc[yr, b]
            r[f"miss_raw_{yr}"] = float(raw_miss[yr][b])
            r[f"miss_clean_{yr}"] = float(s.isna().mean())
            r[f"mean_{yr}"] = float(s.mean())
        r["fail_missing_raw"] = max(r["miss_raw_2016"], r["miss_raw_2017"]) > 0.05
        r["fail_missing_after_stuck_mask"] = (not r["fail_missing_raw"]) and \
            max(r["miss_clean_2016"], r["miss_clean_2017"]) > 0.05
        r["fail_low_load"] = min(r["mean_2016"], r["mean_2017"]) < 1.0 if np.isfinite(
            min(r["mean_2016"], r["mean_2017"])) else True
        r["fail_due_to_2017_only"] = (r["miss_clean_2016"] <= 0.05 and r["miss_clean_2017"] > 0.05)
        r["kept"] = max(r["miss_clean_2016"], r["miss_clean_2017"]) <= 0.05 and not r["fail_low_load"]
        rows.append(r)
    a = pd.DataFrame(rows)
    a.to_csv(os.path.join(TAB, "attrition_buildings.csv"), index=False)
    g = a.groupby("site_id").agg(n_raw=("kept", "size"), kept=("kept", "sum"),
                                 fail_missing_raw=("fail_missing_raw", "sum"),
                                 fail_stuck_mask=("fail_missing_after_stuck_mask", "sum"),
                                 fail_low_load=("fail_low_load", "sum"),
                                 fail_2017_only=("fail_due_to_2017_only", "sum")).reset_index()
    tot = g.drop(columns="site_id").sum()
    g = pd.concat([g, pd.DataFrame([dict(site_id="All", **tot.to_dict())])], ignore_index=True)
    comp = a.groupby("kept").agg(n=("kept", "size"), median_sqm=("sqm", "median"),
                                 median_mean_load_2016=("mean_2016", "median")).reset_index()
    us = pd.crosstab(a.usage, a.kept, normalize="columns").round(3)
    g.to_csv(os.path.join(TAB, "T_attrition.csv"), index=False)
    with open(os.path.join(TAB, "T_attrition.md"), "w") as f:
        f.write("**Attrition of the BDG2 quality filter by site and rule** (a building can fail several rules; "
                "'fail_stuck_mask' = passes the 5 % missing rule on the raw data but fails after stuck-run masking; "
                "'fail_2017_only' = fails only because of the target year)\n\n" + g.to_markdown(index=False) +
                "\n\n**Retained vs excluded buildings**\n\n" + comp.round(1).to_markdown(index=False) +
                "\n\n**Primary-use mix (column shares), excluded (False) vs retained (True)**\n\n" +
                us.to_markdown() + "\n")
    # site audit: weather interpolation share and load-temperature lag alignment (kept buildings)
    srows = []
    full = pd.date_range("2016-01-01", "2017-12-31 23:00", freq="h")
    for site, gw in w.groupby("site_id"):
        t = gw.drop_duplicates("timestamp").set_index("timestamp")["airTemperature"].reindex(full)
        bs = a[(a.site_id == site) & a.kept].building_id.tolist()
        r = dict(site_id=site, n_kept=len(bs), temp_missing_share=float(t.isna().mean()))
        if bs:
            ti = t.interpolate(limit_direction="both")
            L = c[bs].reindex(full)
            Ld = L - L.rolling(24 * 7, center=True, min_periods=24).mean()  # remove weekly level
            Td = ti - ti.rolling(24 * 7, center=True, min_periods=24).mean()
            m = Ld.mean(axis=1)
            cc = {lag: float(m.corr(Td.shift(lag))) for lag in range(-12, 13)}
            best = max(cc, key=lambda k: abs(cc[k]))
            r.update(best_lag_h=best, corr_at_best=cc[best], corr_lag0=cc[0])
            # diurnal phase: hour of mean daily peak (local-time sanity check)
            prof = L.groupby(L.index.hour).mean().mean(axis=1)
            r["peak_hour"] = int(prof.idxmax())
        srows.append(r)
    sa = pd.DataFrame(srows)
    sa.to_csv(os.path.join(TAB, "T_site_audit.csv"), index=False)
    with open(os.path.join(TAB, "T_site_audit.md"), "w") as f:
        f.write("**Site audit (BDG2): missing raw temperature share, lag (h) maximising |corr| between de-trended "
                "site-mean load and temperature, and hour of the mean daily load peak**\n\n" +
                sa.round(3).to_markdown(index=False) + "\n")
    return g, sa


if __name__ == "__main__":
    import sys
    sys.path.insert(0, ROOT)
    print(run())
