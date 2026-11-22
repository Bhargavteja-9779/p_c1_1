"""Two-timescale shrinkage conformal calibration (TTSC): evaluation over every protocol of the study.

TTSC = recency-weighted shrinkage of the CQR score distribution (slow timescale, kappa by the same constrained
leave-one-building-out rule as HSC-CQR recency) + a building-specific level correction from the misses of the last
W = 7 days (fast timescale; one week = the settlement period of the application), with the radius capped at the
pooled 99 % score quantile. The feedback gain gamma is selected by leave-one-building-out on calibration
buildings: smallest weekly coverage deviation subject to an interval score at most 2 % above pooled CQR.

The same cached forecasts as in the main study are used (results/cache). Output: results/ttsc/<part>.csv with one
row per (target building, method), weekly coverage and weekly upper-bound exceedance included.
"""
import os
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from src import experiments as ex  # noqa: E402
from src.training import pipeline as pl  # noqa: E402
from src.models import calibration as cb  # noqa: E402
from src.evaluation import metrics as mt  # noqa: E402

OUT = os.path.join(ROOT, "results", "ttsc")
WINDOW = 7
GAMMAS_T = [0.0, 0.0005, 0.001, 0.0015, 0.002, 0.003, 0.005, 0.0075, 0.01]
NW = 8


def weekly_macd(q, scores, alpha):
    """Mean over building-weeks of |weekly coverage - (1 - alpha)| (tuning objective of TTSC)."""
    valid = ~np.isnan(scores)
    hit = (np.where(valid, scores, np.inf) <= q[..., None]) & valid
    n = scores.shape[0]
    hw = hit.reshape(n, NW, -1).sum(-1)
    vw = valid.reshape(n, NW, -1).sum(-1)
    cw = np.where(vw > 0, hw / np.maximum(vw, 1), np.nan)
    return float(np.nanmean(np.abs(cw - (1 - alpha))))


def tune_ttsc(Sc, cc, binc, alpha, kappa, ref_is, cap_lobo, base_w, delay=0):
    stages = np.arange(1, pl.NH + 1)
    excl = np.arange(Sc.shape[0])
    rows = []
    for g in GAMMAS_T:
        q = cb.hsc_aci_quantiles(Sc, cc, binc, alpha, kappa, g, stages, decay=pl.RECENCY, excl=excl,
                                 window=WINDOW, delay=delay)
        q = np.minimum(q, cap_lobo)
        rows.append(dict(gamma=g, IS=float(cb.normalized_IS(q[None], Sc, base_w, alpha)[0]),
                         WMACD=weekly_macd(q, Sc, alpha)))
    df = pd.DataFrame(rows)
    feas = df[df.IS <= pl.IS_TOL * ref_is + 1e-12]
    best = (feas if len(feas) else df.iloc[[0]]).sort_values(["WMACD", "IS"]).iloc[0]
    return float(best.gamma), df


def evaluate(out, PT, alpha):
    """Per building: window/weekly coverage, weekly upper exceedance, relative IS and width."""
    y = PT["y"]
    ok = np.ones_like(y, dtype=bool) & ~np.isnan(y)
    for lo, hi in out.values():
        ok &= np.isfinite(lo) & np.isfinite(hi)
    nt = y.shape[0]
    ybar = np.nanmean(np.where(ok, y, np.nan).reshape(nt, -1), 1)
    rows = []
    for m, (lo, hi) in out.items():
        hit = (y >= lo) & (y <= hi) & ok
        up = (y > hi) & ok
        v = ok.reshape(nt, -1).sum(1)
        isv = (hi - lo) + 2 / alpha * np.maximum(lo - y, 0) + 2 / alpha * np.maximum(y - hi, 0)
        is_b = np.where(ok, isv, 0).reshape(nt, -1).sum(1) / np.maximum(v, 1) / ybar
        w_b = np.where(ok, hi - lo, 0).reshape(nt, -1).sum(1) / np.maximum(v, 1) / ybar
        vw = ok.reshape(nt, NW, -1).sum(-1)
        cw = np.where(vw > 0, hit.reshape(nt, NW, -1).sum(-1) / np.maximum(vw, 1), np.nan)
        uw = np.where(vw > 0, up.reshape(nt, NW, -1).sum(-1) / np.maximum(vw, 1), np.nan)
        # capacity-headroom planning on the upper bound: planned level and violation, relative to mean load
        u_rel = np.where(ok, hi, 0).reshape(nt, -1).sum(1) / np.maximum(v, 1) / ybar
        viol_rel = np.where(ok, np.maximum(y - hi, 0), 0).reshape(nt, -1).sum(1) / np.maximum(v, 1) / ybar
        r = pd.DataFrame(dict(method=m, u_rel=u_rel, viol_rel=viol_rel,
                              cov=hit.reshape(nt, -1).sum(1) / np.maximum(v, 1),
                              up=up.reshape(nt, -1).sum(1) / np.maximum(v, 1), rel_IS=is_b, rel_width=w_b))
        for w in range(NW):
            r[f"cov_w{w + 1}"] = cw[:, w]
            r[f"up_w{w + 1}"] = uw[:, w]
        rows.append(r)
    return pd.concat(rows, ignore_index=True), ok


def calibrate(PC, PT, alpha):
    stages = np.arange(1, pl.NH + 1)
    sb = cb.stage_bin(stages)
    Sc, St = pl.scores_cqr(PC), pl.scores_cqr(PT)
    ccc, cct = cb.cum_counts(Sc), cb.cum_counts(St)
    binc, _ = cb.bin_cdfs(ccc, stages)
    base_w = PC["qhi"] / PC["s"][:, :, None] - PC["qlo"] / PC["s"][:, :, None]  # as in the main pipeline
    s = PT["s"][:, :, None]
    band = lambda q: (PT["qlo"] - np.asarray(q)[:, :, None] * s, PT["qhi"] + np.asarray(q)[:, :, None] * s)  # noqa
    nt = St.shape[0]
    info = {}
    out = {}
    q_pool = cb.pooled_quantile(binc, alpha, True)[sb]
    out["CQR"] = band(np.broadcast_to(q_pool, (nt, pl.NH)))
    br, tab = pl.tune_hsc(Sc, base_w, PC["z"], alpha, stage_matched=False, Ks=[None], objective="cov",
                          decay=pl.RECENCY)
    kap = br["kappa"]
    ref_is = float(tab[np.isinf(tab.kappa.astype(float))].IS.min())
    info["kappa"] = kap
    q_rec = cb.hsc_quantiles(cct, binc, None, alpha, [kap], stages, stage_matched=False, decay=pl.RECENCY)[0]
    q_cap = cb.pooled_quantile(binc, alpha / 10, True)[sb][None]
    out["HSC-CQR recency"] = band(q_rec)
    out["HSC-CQR recency (capped)"] = band(np.minimum(q_rec, q_cap))
    lamc, _ = pl.tune_qshrink(Sc, base_w, alpha, objective="cov")
    out["QShrink-CQR (cov)"] = band(cb.qshrink_quantiles(cct, q_pool, alpha, lamc, stages))
    gqc, _ = pl.tune_aci(Sc, alpha, objective="cov", base_w=base_w)
    out["ACI-CQR (cov)"] = band(cb.aci_quantiles(St, binc.sum(axis=0), alpha, gqc, stages))
    # TTSC: LOBO cap from the other calibration buildings
    cap_lobo = cb.pooled_quantile_lobo(binc, alpha / 10)[:, sb]
    g, gtab = tune_ttsc(Sc, ccc, binc, alpha, kap, ref_is, cap_lobo, base_w)
    info["gamma"] = g
    info["gamma_edge"] = bool(g == max(GAMMAS_T))
    q_t = cb.hsc_aci_quantiles(St, cct, binc, alpha, kap, g, stages, decay=pl.RECENCY, window=WINDOW)
    out["TTSC"] = band(np.minimum(q_t, q_cap))
    # uncapped and one-day-delayed variants (same kappa and gamma)
    out["TTSC (uncapped)"] = band(q_t)
    q_d = cb.hsc_aci_quantiles(St, cb.delay_counts(cct, 1), binc, alpha, kap, g, stages, decay=pl.RECENCY,
                               window=WINDOW, delay=1)
    out["TTSC (delay 1d)"] = band(np.minimum(q_d, q_cap))
    # fixed-gain ablation: cumulative (non-windowed) feedback with the same gamma
    q_c = cb.hsc_aci_quantiles(St, cct, binc, alpha, kap, g, stages, decay=pl.RECENCY, window=None)
    out["TTSC (cumulative feedback)"] = band(np.minimum(q_c, q_cap))
    # fairness check: feedback-only strategies tuned with the SAME weekly objective, constraint and cap as TTSC
    KINF = 1e9  # kappa -> infinity: the building-weighted population distribution only (no shrinkage)
    g_w, _ = tune_ttsc(Sc, ccc, binc, alpha, KINF, ref_is, cap_lobo, base_w)
    q_w = cb.hsc_aci_quantiles(St, cct, binc, alpha, KINF, g_w, stages, decay=pl.RECENCY, window=WINDOW)
    out["Windowed ACI (weekly-tuned)"] = band(np.minimum(q_w, q_cap))
    info["gamma_windowed_aci"] = g_w
    rows = []
    for gg in pl.GAMMAS:
        qa = np.minimum(cb.aci_quantiles(Sc, binc.sum(axis=0)[None] - binc, alpha, gg, stages), cap_lobo)
        rows.append(dict(gamma=gg, IS=float(cb.normalized_IS(qa[None], Sc, base_w, alpha)[0]),
                         WMACD=weekly_macd(qa, Sc, alpha)))
    ta = pd.DataFrame(rows)
    feas = ta[ta.IS <= pl.IS_TOL * ref_is + 1e-12]
    g_a = float((feas if len(feas) else ta.iloc[[0]]).sort_values(["WMACD", "IS"]).iloc[0].gamma)
    out["ACI (weekly-tuned)"] = band(np.minimum(cb.aci_quantiles(St, binc.sum(axis=0), alpha, g_a, stages), q_cap))
    info["gamma_aci_weekly"] = g_a
    return out, info, gtab


def run_one(pid, obj, alpha, cols, PT=None, PC=None, meta_idx=None, dsT=None):
    f = os.path.join(OUT, pid + ".csv")
    if os.path.exists(f):
        return
    t0 = time.time()
    PC = obj["PC"] if PC is None else PC
    PT = obj["PT"] if PT is None else PT
    out, info, gtab = calibrate(PC, PT, alpha)
    df, ok = evaluate(out, PT, alpha)
    nt = PT["y"].shape[0]
    ref = mt.oracle_reference(pl.scores_cqr(PT), ok, alpha, seed=int(cols.get("seed", 0)))
    meta = dsT["meta"].iloc[obj["tgt_idx"]]
    df["building_id"] = np.tile(meta.building_id.values, len(out))
    df["site_id"] = np.tile(meta.site_id.values, len(out))
    for k, v in ref.items():
        df[k] = np.tile(v, len(out))
    for k, v in dict(cols, alpha=alpha, part=pid, kappa=info["kappa"], gamma=info["gamma"],
                     gamma_edge=info["gamma_edge"], gamma_windowed_aci=info["gamma_windowed_aci"],
                     gamma_aci_weekly=info["gamma_aci_weekly"]).items():
        df[k] = v
    os.makedirs(OUT, exist_ok=True)
    gtab.assign(part=pid).to_csv(os.path.join(OUT, pid + "_tune.csv"), index=False)
    df.to_csv(f + ".tmp", index=False)
    os.replace(f + ".tmp", f)  # atomic: an interrupted run never leaves a truncated part behind
    ex._log(f"ttsc {pid}: kappa={info['kappa']} gamma={info['gamma']} n={nt} ({time.time() - t0:.0f}s)",
            "ttsc.log")


def main(kinds=("main", "lso", "xds", "robust", "weak")):
    frac = 0.4
    if "main" in kinds:
        for dsn in ["BDG2", "UCI"]:
            ds = ex.get_ds(dsn)
            for s in range(5):
                obj = ex.prepared(dsn, dsn, s, "random", None, ds["temp"] is not None, frac, True)
                for a in [0.1, 0.05, 0.2]:
                    run_one(f"main_{dsn}_s{s}_a{a}", obj, a, dict(exp="main", dataset=dsn, seed=s, perturb="none"),
                            dsT=ds)
    if "lso" in kinds:
        ds = ex.get_ds("BDG2")
        for f_ in range(5):
            obj = ex.prepared("BDG2", "BDG2", f_, "lso", f_, True, frac, True)
            run_one(f"lso_BDG2_f{f_}", obj, 0.1, dict(exp="lso", dataset="BDG2", seed=f_, perturb="none"), dsT=ds)
    if "xds" in kinds:
        for s in range(3):
            for src, tgt in [("BDG2", "UCI"), ("UCI", "BDG2"), ("BDG2", "BDG2")]:
                obj = ex.prepared(src, tgt, s, "random", None, False, frac, True)
                run_one(f"xds_{src}to{tgt}_s{s}", obj, 0.1,
                        dict(exp="xds", dataset=tgt, seed=s, perturb=f"{src}->{tgt}"), dsT=ex.get_ds(tgt))
    if "robust" in kinds:
        ds = ex.get_ds("BDG2")
        for s in range(3):
            obj = ex.prepared("BDG2", "BDG2", s, "random", None, True, frac, True)
            perts = {"noise5": ex.perturb_noise(0.05, s), "noise15": ex.perturb_noise(0.15, s),
                     "missing20": ex.perturb_missing(0.2, s), "missing40": ex.perturb_missing(0.4, s),
                     "shift+40": ex.perturb_shift(1.4), "shift-40": ex.perturb_shift(0.6),
                     "outage1-3d": ex.perturb_outage(s), "spikes2": ex.perturb_spikes(s),
                     "shift+40@d3-14": ex.perturb_shift_random(1.4, s), "ramp+40": ex.perturb_ramp(0.4)}
            for name, fn in perts.items():
                pid = f"robust_BDG2_s{s}_{name}"
                if os.path.exists(os.path.join(OUT, pid + ".csv")):
                    continue
                PT = pl.window_predictions(ds, obj["tgt_idx"], obj["t0t"], obj["models"], perturb=fn)
                run_one(pid, obj, 0.1, dict(exp="robust", dataset="BDG2", seed=s, perturb=name), PT=PT, dsT=ds)
            for fr in [0.1, 0.25, 0.5]:
                PCs, _ = ex.subsample_cal(obj["PC"], fr, s)
                run_one(f"robust_BDG2_s{s}_cal{int(fr * 100)}", obj, 0.1,
                        dict(exp="robust", dataset="BDG2", seed=s, perturb=f"calpool{int(fr * 100)}"), PC=PCs, dsT=ds)
    if "weak" in kinds:
        ds = ex.get_ds("BDG2")
        for s in range(3):
            obj = ex.prepared("BDG2", "BDG2", s, "random", None, True, frac, False, train_frac_buildings=0.1)
            run_one(f"robust_BDG2_s{s}_weak", obj, 0.1,
                    dict(exp="robust", dataset="BDG2", seed=s, perturb="weak-forecaster"), dsT=ds)
    ex._log("=== ttsc all done ===", "ttsc.log")


if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore")
    main(tuple(sys.argv[1:]) if len(sys.argv) > 1 else ("main", "lso", "xds", "robust", "weak"))
