"""Experiment definitions E1-E8 (see experiments/PREREGISTRATION.md). Resumable: each experiment part
writes results/parts/<id>.csv (+ curves, info) and is skipped if it already exists."""
from __future__ import annotations

import json
import os
import pickle
import time

import numpy as np
import pandas as pd

from src.data.datasets import load_bdg2, load_uci, download
from src.training import pipeline as pl
from src.evaluation import metrics as mt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
PARTS = os.path.join(RES, "parts")
CACHE = os.path.join(RES, "cache")
LOGS = os.path.join(RES, "experiment_logs")


def _log(msg, fname="run.log"):
    os.makedirs(LOGS, exist_ok=True)
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(os.path.join(LOGS, fname), "a") as f:
        f.write(line + "\n")


_DS = {}


def get_ds(name):
    if name not in _DS:
        raw, proc = os.path.join(ROOT, "data", "raw"), os.path.join(ROOT, "data", "processed")
        download(raw)
        _DS[name] = load_bdg2(raw, proc) if name == "BDG2" else load_uci(raw, proc)
    return _DS[name]


def _done(pid):
    return os.path.exists(os.path.join(PARTS, pid + ".csv"))


def _save(pid, df, curves, info):
    os.makedirs(PARTS, exist_ok=True)
    cv = []
    for m, (c, s, smed) in curves.items():
        cv.append(pd.DataFrame(dict(method=m, stage=np.arange(1, len(c) + 1), coverage=c, rel_IS=s, rel_IS_median=smed)))
    pd.concat(cv).assign(part=pid).to_csv(os.path.join(PARTS, pid + "_curves.csv"), index=False)
    info = {k: v for k, v in info.items() if k != "tune_table"}
    with open(os.path.join(PARTS, pid + "_info.json"), "w") as f:
        json.dump(info, f, default=lambda o: o if not isinstance(o, (np.floating, np.integer)) else o.item(), indent=1)
    df.to_csv(os.path.join(PARTS, pid + ".csv"), index=False)


def prepared(src, tgt, seed, protocol, fold, use_weather, frac, with_mlp, train_frac_buildings=1.0, tag=""):
    """Train (or load cached) models and window predictions for calibration and target buildings."""
    key = f"{src}_{tgt}_{protocol}{'' if fold is None else fold}_s{seed}_w{int(use_weather)}_f{frac}_m{int(with_mlp)}_tb{train_frac_buildings}{tag}"
    path = os.path.join(CACHE, key + ".pkl")
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    dsS, dsT = get_ds(src), get_ds(tgt)
    sp = pl.split(dsS, seed, protocol, fold)
    if train_frac_buildings < 1.0:
        rng = np.random.default_rng(500 + seed)
        sp["train"] = np.sort(rng.choice(sp["train"], max(10, int(train_frac_buildings * len(sp["train"]))), replace=False))
    tgt_idx = sp["tgt"] if src == tgt else pl.split(dsT, seed, "random")["tgt"]
    # trained models depend only on the source configuration (not on the target dataset): cache them separately
    mkey = f"MODELS_{src}_{protocol}{'' if fold is None else fold}_s{seed}_w{int(use_weather)}_f{frac}_m{int(with_mlp)}_tb{train_frac_buildings}{tag}"
    mpath = os.path.join(CACHE, mkey + ".pkl")
    t0 = time.time()
    if os.path.exists(mpath):
        with open(mpath, "rb") as f:
            models = pickle.load(f)
        _log(f"reuse models {mkey} for {key}")
    else:
        _log(f"train {key}: train={len(sp['train'])} cal={len(sp['cal'])} tgt={len(tgt_idx)}")
        models = pl.train_models(dsS, sp, seed, use_weather, frac=frac, with_mlp=with_mlp, log=_log)
        models["time_train_total"] = time.time() - t0
        os.makedirs(CACHE, exist_ok=True)
        with open(mpath, "wb") as f:
            pickle.dump(models, f)
    rng = np.random.default_rng(2000 + seed)
    trS, _ = pl.periods(dsS)
    _, teT = pl.periods(dsT)
    t0c = pl.onboard_dates(dsS, sp["cal"], trS, rng)
    t0t = pl.onboard_dates(dsT, tgt_idx, teT, rng)
    PC = pl.window_predictions(dsS, sp["cal"], t0c, models)
    PT = pl.window_predictions(dsT, tgt_idx, t0t, models)
    obj = dict(PC=PC, PT=PT, sp=sp, tgt_idx=tgt_idx, t0c=t0c, t0t=t0t, models=models,
               timing=dict(train_total=models.get("time_train_total", time.time() - t0), lgb=models["time_lgb"],
                           mlp=models.get("time_mlp"),
                           n_train_rows=models["n_train_rows"], pred_lgb_per_target_day=PT["t_pred_lgb"]))
    os.makedirs(CACHE, exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(obj, f)
    return obj


def _rows(df, **kw):
    for k, v in kw.items():
        df[k] = v
    return df


def run_part(pid, obj, dsS, dsT, alpha, methods="all", PT=None, PC=None, extra=None, model_alpha=0.1):
    if _done(pid):
        return
    PC = obj["PC"] if PC is None else PC
    PT = obj["PT"] if PT is None else PT
    mc = dsS["meta"].iloc[obj["sp"]["cal"]] if PC is obj["PC"] else None
    mtg = dsT["meta"].iloc[obj["tgt_idx"]]
    if mc is None and extra and "cal_idx" in extra:
        mc = dsS["meta"].iloc[extra["cal_idx"]]
    t0 = time.time()
    out, info = pl.run_calibration(PC, PT, alpha, mc if dsS is dsT else None, mtg if dsS is dsT else None,
                                   methods=methods)
    if alpha != model_alpha:  # quantile models were trained for alpha=0.1: uncalibrated QR intervals are not
        for k in ["QR-LGBM", "MLP-QR"]:  # meaningful at other levels; conformalised (CQR-based) ones are kept
            out.pop(k, None)
    df, curves = pl.evaluate(out, PT, alpha)
    ok = pl.common_mask(out, PT)
    PT = dict(PT, y=np.where(ok, PT["y"], np.nan))  # same evaluation mask for point metrics
    nb = len(mtg)
    df["building_id"] = np.tile(mtg.building_id.values, len(out))
    df["site_id"] = np.tile(mtg.site_id.values, len(out))
    df["usage"] = np.tile(mtg.usage.values, len(out))
    pm = mt.point_metrics(PT["y"], PT["yhat"])
    df["cvrmse_lgb"] = np.tile(pm["cvrmse"], len(out))
    info["t_calibration_total"] = time.time() - t0
    info.update(obj["timing"])
    info["point"] = {k: float(np.nanmedian(v)) for k, v in pm.items()}
    for key, nm in (("naive", "naive"), ("mu", "mlp")):
        if key in PT:
            p = mt.point_metrics(PT["y"], PT[key])
            info["point_" + nm] = {k: float(np.nanmedian(v)) for k, v in p.items()}
    _rows(df, part=pid, alpha=alpha, **(extra.get("cols", {}) if extra else {}))
    _save(pid, df, curves, info)
    s = df.groupby("method").agg(cov=("coverage", "mean"), IS=("rel_IS", "mean"))
    _log(f"done {pid} ({time.time() - t0:.0f}s): HSC IS={s.loc['HSC', 'IS']:.3f} cov={s.loc['HSC', 'cov']:.3f} | "
         f"SCP-stage IS={s.loc['SCP-stage', 'IS']:.3f}")


# ---------------------------------------------------------------- perturbations (E4)
def perturb_noise(level, seed):
    def f(load, bidx, t0):
        rng = np.random.default_rng(3000 + seed)
        for b, t in zip(bidx, t0):
            seg = load[b, t:t + pl.NH + 1]
            mu = np.nanmean(seg)
            load[b, t:t + pl.NH + 1] = np.maximum(seg + rng.normal(0, level * mu, seg.shape), 0)
        return load
    return f


def perturb_missing(rate, seed):
    def f(load, bidx, t0):
        rng = np.random.default_rng(4000 + seed)
        for b, t in zip(bidx, t0):
            seg = load[b, t:t + pl.NH + 1]
            seg[rng.random(seg.shape) < rate] = np.nan
            load[b, t:t + pl.NH + 1] = seg
        return load
    return f


def perturb_shift(factor, day=28):
    def f(load, bidx, t0):
        for b, t in zip(bidx, t0):
            load[b, t + day:t + pl.NH + 1] *= factor
        return load
    return f


def subsample_cal(PC, frac, seed):
    n = PC["y"].shape[0]
    rng = np.random.default_rng(5000 + seed)
    idx = np.sort(rng.choice(n, max(10, int(frac * n)), replace=False))
    out = {}
    for k, v in PC.items():
        if k == "z":
            out[k] = v[:, idx]
        elif isinstance(v, np.ndarray) and v.shape[0] == n:
            out[k] = v[idx]
        else:
            out[k] = v
    return out, idx


# ---------------------------------------------------------------- experiment plan
def plan(mode):
    quick = mode == "quick"
    seeds = [0] if quick else [0, 1, 2, 3, 4]
    rseeds = [0] if quick else [0, 1, 2]
    frac = 0.1 if quick else 0.4
    mlp = True
    jobs = []
    # E1/E2/E3/E7(alpha): main, both datasets
    for ds in ["BDG2", "UCI"]:
        for s in seeds:
            jobs.append(dict(kind="main", ds=ds, seed=s))
    # E5: leave-site-out (BDG2)
    for f in ([0] if quick else range(5)):
        jobs.append(dict(kind="lso", ds="BDG2", seed=f))
    # E5: cross-dataset (no-weather models)
    for s in rseeds:
        jobs.append(dict(kind="xds", src="BDG2", tgt="UCI", seed=s))
        jobs.append(dict(kind="xds", src="UCI", tgt="BDG2", seed=s))
        jobs.append(dict(kind="xds", src="BDG2", tgt="BDG2", seed=s))  # within, no weather (reference)
    # E4: robustness (BDG2)
    for s in rseeds:
        jobs.append(dict(kind="robust", ds="BDG2", seed=s))
        jobs.append(dict(kind="weak", ds="BDG2", seed=s))
    return jobs, frac, mlp, quick


def train_only(mode="full"):
    """Train (and cache) every model/prediction set needed by the plan, without calibration."""
    jobs, frac, mlp, quick = plan(mode)
    tag = "_quick" if quick else ""
    for j in jobs:
        try:
            k = j["kind"]
            if k in ("main", "robust"):
                ds = get_ds(j["ds"])
                prepared(j["ds"], j["ds"], j["seed"], "random", None, ds["temp"] is not None, frac, mlp, tag=tag)
            elif k == "lso":
                prepared("BDG2", "BDG2", j["seed"], "lso", j["seed"], True, frac, mlp, tag=tag)
            elif k == "xds":
                prepared(j["src"], j["tgt"], j["seed"], "random", None, False, frac, mlp, tag=tag)
            elif k == "weak":
                prepared("BDG2", "BDG2", j["seed"], "random", None, True, frac, False, train_frac_buildings=0.1,
                         tag=tag)
        except Exception as e:
            import traceback
            _log(f"FAILED training {j}: {e}\n{traceback.format_exc()}")
    _log("=== all trainings cached ===")


def execute(mode="full", kinds=None, select=None):
    """Run the experiment plan. kinds: restrict to job kinds; select: optional predicate on the job dict
    (used to split the calibration pass over several single-threaded processes)."""
    jobs, frac, mlp, quick = plan(mode)
    if kinds is not None:
        jobs = [j for j in jobs if j["kind"] in kinds]
    if select is not None:
        jobs = [j for j in jobs if select(j)]
    tag = "_quick" if quick else ""
    _log(f"=== run_all mode={mode}: {len(jobs)} jobs ===")
    for j in jobs:
        try:
            _execute_job(j, frac, mlp, tag, quick)
        except Exception as e:  # keep going; failures are logged and reported
            import traceback
            _log(f"FAILED job {j}: {e}\n{traceback.format_exc()}")
    _log("=== all jobs finished ===")


def _execute_job(j, frac, mlp, tag, quick):
    k = j["kind"]
    if k == "main":
        ds = get_ds(j["ds"])
        obj = prepared(j["ds"], j["ds"], j["seed"], "random", None, ds["temp"] is not None, frac, mlp, tag=tag)
        for a in [0.1, 0.05, 0.2]:
            pid = f"main{tag}_{j['ds']}_s{j['seed']}_a{a}"
            run_part(pid, obj, ds, ds, a, methods="all" if a == 0.1 else "core",
                     extra=dict(cols=dict(exp="main", dataset=j["ds"], protocol="random", seed=j["seed"],
                                          perturb="none")))
    elif k == "lso":
        ds = get_ds("BDG2")
        obj = prepared("BDG2", "BDG2", j["seed"], "lso", j["seed"], True, frac, mlp, tag=tag)
        run_part(f"lso{tag}_BDG2_f{j['seed']}", obj, ds, ds, 0.1, methods="all",
                 extra=dict(cols=dict(exp="lso", dataset="BDG2", protocol="leave-site-out", seed=j["seed"],
                                      perturb="none")))
    elif k == "xds":
        dS, dT = get_ds(j["src"]), get_ds(j["tgt"])
        obj = prepared(j["src"], j["tgt"], j["seed"], "random", None, False, frac, mlp, tag=tag)
        run_part(f"xds{tag}_{j['src']}to{j['tgt']}_s{j['seed']}", obj, dS, dT, 0.1, methods="all",
                 extra=dict(cols=dict(exp="xds", dataset=j["tgt"], protocol=f"{j['src']}->{j['tgt']} (no weather)",
                                      seed=j["seed"], perturb="none")))
    elif k == "robust":
        ds = get_ds("BDG2")
        obj = prepared("BDG2", "BDG2", j["seed"], "random", None, True, frac, mlp, tag=tag)
        s = j["seed"]
        perts = {"noise5": perturb_noise(0.05, s), "noise15": perturb_noise(0.15, s),
                 "missing20": perturb_missing(0.2, s), "missing40": perturb_missing(0.4, s),
                 "shift+40": perturb_shift(1.4), "shift-40": perturb_shift(0.6)}
        for name, f in perts.items():
            pid = f"robust{tag}_BDG2_s{s}_{name}"
            if _done(pid):
                continue
            PT = pl.window_predictions(ds, obj["tgt_idx"], obj["t0t"], obj["models"], perturb=f)
            run_part(pid, obj, ds, ds, 0.1, methods="core", PT=PT,
                     extra=dict(cols=dict(exp="robust", dataset="BDG2", protocol="random", seed=s, perturb=name)))
        for fr in [0.1, 0.25, 0.5]:
            pid = f"robust{tag}_BDG2_s{s}_cal{int(fr * 100)}"
            if _done(pid):
                continue
            PCs, idx = subsample_cal(obj["PC"], fr, s)
            run_part(pid, obj, ds, ds, 0.1, methods="core", PC=PCs,
                     extra=dict(cal_idx=obj["sp"]["cal"][idx],
                                cols=dict(exp="robust", dataset="BDG2", protocol="random", seed=s,
                                          perturb=f"calpool{int(fr * 100)}")))
    elif k == "weak":
        ds = get_ds("BDG2")
        obj = prepared("BDG2", "BDG2", j["seed"], "random", None, True, frac, False, train_frac_buildings=0.1, tag=tag)
        run_part(f"robust{tag}_BDG2_s{j['seed']}_weakmodel", obj, ds, ds, 0.1, methods="core",
                 extra=dict(cols=dict(exp="robust", dataset="BDG2", protocol="random", seed=j["seed"],
                                      perturb="weak-forecaster")))


def collect():
    """Merge parts -> results/raw_results.csv, results/stage_curves.csv, results/run_info.json"""
    import glob
    fs = sorted(f for f in glob.glob(os.path.join(PARTS, "*.csv")) if not f.endswith("_curves.csv"))
    df = pd.concat([pd.read_csv(f) for f in fs], ignore_index=True)
    df.to_csv(os.path.join(RES, "raw_results.csv"), index=False)  # local working copy (gitignored, ~75 MB)
    df.to_csv(os.path.join(RES, "raw_results.csv.gz"), index=False, compression="gzip")  # archived copy
    cv = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(os.path.join(PARTS, "*_curves.csv")))], ignore_index=True)
    cv.to_csv(os.path.join(RES, "stage_curves.csv"), index=False)
    info = {}
    for f in sorted(glob.glob(os.path.join(PARTS, "*_info.json"))):
        info[os.path.basename(f)[:-10]] = json.load(open(f))
    json.dump(info, open(os.path.join(RES, "run_info.json"), "w"), indent=1)
    return df


# ---------------------------------------------------------------- E7 sensitivity + example extraction
def sensitivity(mode="full"):
    """Evaluate HSC / HSC-CQR on the targets over the full (kappa, K) grid (reported, never used for
    selection) and extract two pre-specified example buildings for the time-series figure."""
    from src.models import calibration as cb
    quick = mode == "quick"
    tag = "_quick" if quick else ""
    frac = 0.1 if quick else 0.4
    seeds = [0] if quick else [0, 1, 2, 3, 4]
    out = []
    stages = np.arange(1, pl.NH + 1)
    for dsn in ["BDG2", "UCI"]:
        ds = get_ds(dsn)
        for s in seeds:
            obj = prepared(dsn, dsn, s, "random", None, ds["temp"] is not None, frac, True, tag=tag)
            PC, PT = obj["PC"], obj["PT"]
            for score in ["abs", "cqr"]:
                Sc = pl.scores_abs(PC) if score == "abs" else pl.scores_cqr(PC)
                St = pl.scores_abs(PT) if score == "abs" else pl.scores_cqr(PT)
                binc, _ = cb.bin_cdfs(cb.cum_counts(Sc), stages)
                cct = cb.cum_counts(St)
                for K in pl.KS:
                    nb = pl.nbrs_by_stage(PT["z"], PC["z"], K)
                    q = cb.hsc_quantiles(cct, binc, nb, 0.1, pl.KAPPAS, stages)
                    for ki, kap in enumerate(pl.KAPPAS):
                        if score == "abs":
                            lo, hi = PT["yhat"] - q[ki][:, :, None] * PT["s"][:, :, None], PT["yhat"] + q[ki][:, :, None] * PT["s"][:, :, None]
                        else:
                            lo, hi = PT["qlo"] - q[ki][:, :, None] * PT["s"][:, :, None], PT["qhi"] + q[ki][:, :, None] * PT["s"][:, :, None]
                        m, _, _ = mt.interval_metrics(PT["y"], lo, hi, 0.1)
                        cov = m["coverage"]
                        out.append(dict(dataset=dsn, seed=s, score=score, K="all" if K is None else K,
                                        kappa=kap, macd=float(np.mean(np.abs(cov - 0.9))),
                                        under=float(np.mean(cov < 0.85)), mean_cov=float(cov.mean()),
                                        rel_IS=float(np.median(m["rel_IS"])),
                                        rel_width=float(np.median(m["rel_width"]))))
            if s == 0:
                _examples(dsn, ds, obj, tag)
    pd.DataFrame(out).to_csv(os.path.join(RES, f"sensitivity{tag}.csv"), index=False)


def _examples(dsn, ds, obj, tag):
    """Pre-specified rule: the target buildings at the 10th and 50th percentile of per-building CQR
    coverage in seed 0 (a poorly covered and a typical building)."""
    PT = obj["PT"]
    out, info = pl.run_calibration(obj["PC"], PT, 0.1, methods="core")
    m, _, _ = mt.interval_metrics(PT["y"], *out["CQR"], 0.1)
    cov = m["coverage"]
    order = np.argsort(cov)
    picks = {"p10": order[int(0.1 * (len(cov) - 1))], "p50": order[int(0.5 * (len(cov) - 1))]}
    rows = []
    for lab, i in picks.items():
        for meth in ["CQR", "HSC-CQR" if "HSC-CQR" in out else "HSC", "HSC"]:
            lo, hi = out[meth]
            for h in range(pl.NH):
                for j in range(24):
                    rows.append(dict(dataset=dsn, pick=lab, building=ds["meta"].building_id.iloc[obj["tgt_idx"][i]],
                                     method=meth, stage=h + 1, hour=j, y=PT["y"][i, h, j], lo=lo[i, h, j],
                                     hi=hi[i, h, j]))
    pd.DataFrame(rows).to_csv(os.path.join(RES, f"examples_{dsn}{tag}.csv"), index=False)
