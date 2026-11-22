"""Sensitivity of TTSC to the feedback window W (gamma re-selected for each W by the same LOBO rule) and frequency
with which the radius is at the cap. Main protocol, 90 %, both datasets, 5 seeds. Output: tables/TT_window.csv."""
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from src import experiments as ex  # noqa: E402
from src import experiments_ttsc as T  # noqa: E402
from src.training import pipeline as pl  # noqa: E402
from src.models import calibration as cb  # noqa: E402


def main():
    rows = []
    stages = np.arange(1, pl.NH + 1)
    sb = cb.stage_bin(stages)
    for dsn in ["BDG2", "UCI"]:
        ds = ex.get_ds(dsn)
        for s in range(5):
            obj = ex.prepared(dsn, dsn, s, "random", None, ds["temp"] is not None, 0.4, True)
            PC, PT = obj["PC"], obj["PT"]
            a = 0.1
            Sc, St = pl.scores_cqr(PC), pl.scores_cqr(PT)
            ccc, cct = cb.cum_counts(Sc), cb.cum_counts(St)
            binc, _ = cb.bin_cdfs(ccc, stages)
            base_w = PC["qhi"] / PC["s"][:, :, None] - PC["qlo"] / PC["s"][:, :, None]
            br, tab = pl.tune_hsc(Sc, base_w, PC["z"], a, stage_matched=False, Ks=[None], objective="cov",
                                  decay=pl.RECENCY)
            kap = br["kappa"]
            ref_is = float(tab[np.isinf(tab.kappa.astype(float))].IS.min())
            cap_lobo = cb.pooled_quantile_lobo(binc, a / 10)[:, sb]
            q_cap = cb.pooled_quantile(binc, a / 10, True)[sb][None]
            sc = PT["s"][:, :, None]
            for W in [3, 7, 14, 28]:
                T.WINDOW = W
                g, _ = T.tune_ttsc(Sc, ccc, binc, a, kap, ref_is, cap_lobo, base_w)
                q = cb.hsc_aci_quantiles(St, cct, binc, a, kap, g, stages, decay=pl.RECENCY, window=W)
                at_cap = float(np.mean(q >= q_cap))
                q = np.minimum(q, q_cap)
                out = {"TTSC": (PT["qlo"] - q[:, :, None] * sc, PT["qhi"] + q[:, :, None] * sc)}
                df, _ = T.evaluate(out, PT, a)
                c = df[[f"cov_w{i}" for i in range(1, 9)]].values
                rows.append(dict(dataset=dsn, seed=s, W=W, gamma=g, at_cap=at_cap,
                                 wk1=float(np.mean(c[:, 0] < 0.85)),
                                 wk_late=float(np.nanmean(np.where(np.isnan(c[:, 1:]), np.nan, c[:, 1:] < 0.85))),
                                 any80=float(np.mean(np.nanmin(c, 1) < 0.80)),
                                 rel_IS_median=float(df.rel_IS.median())))
            T.WINDOW = 7
            print(dsn, s, flush=True)
    d = pd.DataFrame(rows)
    d.to_csv(os.path.join(ROOT, "tables", "TT_window_runs.csv"), index=False)
    g = d.groupby(["dataset", "W"]).mean(numeric_only=True).drop(columns="seed").reset_index()
    g.to_csv(os.path.join(ROOT, "tables", "TT_window.csv"), index=False)
    with open(os.path.join(ROOT, "tables", "TT_window.md"), "w") as f:
        f.write("**Sensitivity of TTSC to the feedback window W (gamma re-selected per W; mean over 5 seeds; at_cap = "
                "share of building-days at the radius cap)**\n\n" + g.round(4).to_markdown(index=False) + "\n")
    print(g.round(4).to_string())


if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore")
    main()
