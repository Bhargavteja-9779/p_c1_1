"""Publication figures, generated only from machine-written result files (results/*.csv).

Colour = method identity, fixed across all figures (validated categorical palette, adjacent-pair CVD
dE >= 9.1); other methods are grey. Lines also differ by marker/linestyle (secondary encoding).
Sizes follow Elsevier column widths (90 mm single, 190 mm double); vector PDF + 600-dpi PNG.
"""
from __future__ import annotations

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RES = os.path.join(ROOT, "results")
FIG = os.path.join(ROOT, "figures")
MM = 1 / 25.4
COL = {"HSC-CQR": "#2a78d6", "CQR": "#eb6834", "HSC": "#1baf7a", "SCP-stage": "#eda100", "ACI": "#e87ba4",
       "QR-LGBM": "#008300", "MLP-QR": "#6250d6", "Self-CP": "#e34948"}
MARK = {"HSC-CQR": "o", "CQR": "s", "HSC": "^", "SCP-stage": "v", "ACI": "D", "QR-LGBM": "P", "MLP-QR": "X",
        "Self-CP": "*"}
GREY = "#8a8984"
INK, INK2 = "#0b0b0b", "#52514e"
KEY = ["HSC-CQR", "CQR", "HSC", "SCP-stage", "ACI", "QR-LGBM", "MLP-QR", "Self-CP"]

plt.rcParams.update({"font.size": 7.5, "axes.titlesize": 8, "axes.labelsize": 7.5, "legend.fontsize": 6.5,
                     "xtick.labelsize": 6.5, "ytick.labelsize": 6.5, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.edgecolor": INK2, "axes.labelcolor": INK,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.grid": True, "grid.color": "#e6e5e1",
                     "grid.linewidth": 0.5, "lines.linewidth": 1.4, "font.family": "DejaVu Sans",
                     "savefig.bbox": "tight", "pdf.fonttype": 42})


def _save(fig, name):
    os.makedirs(FIG, exist_ok=True)
    fig.savefig(os.path.join(FIG, name + ".pdf"))
    fig.savefig(os.path.join(FIG, name + ".png"), dpi=600)
    plt.close(fig)


def _c(m):
    return COL.get(m, GREY)


def fig_schematic():
    fig, ax = plt.subplots(figsize=(190 * MM, 62 * MM))
    ax.set_axis_off()
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 34)
    boxes = [
        (1, 20, 20, 11, "Source buildings\n(training set)\nglobal LightGBM / QR\non normalised load y/s"),
        (1, 3, 20, 13, "Calibration buildings\nsimulated onboarding,\nscores e = |y-ŷ|/s (or CQR)\nper stage h = 1..56"),
        (27, 3, 21, 13, "Population prior F_prior\nstage-bin matched;\nK nearest buildings by\nearly-load descriptor z"),
        (27, 20, 21, 11, "New building b\nmetered from day 0;\nfeatures & z from its\nfirst h days only"),
        (54, 11, 22, 13, "Hierarchical shrinkage\nF = (κ F_prior + Σ 1{e_i ≤ ·})\n      / (κ + n_b + 1)\nq = F⁻¹(1-α)"),
        (81, 11, 18, 13, "Day-ahead interval\n[lo - q s, hi + q s]\nfor the 24 h of day h+1;\nscores of day h+1\nfed back"),
    ]
    for x, y, w, h, t in boxes:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.2", fc="#f0f5fc",
                                    ec="#2a78d6", lw=0.8))
        ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=6.6, color=INK)
    arr = dict(arrowstyle="-|>", color=INK2, lw=0.8)
    ax.annotate("", xy=(27, 9.5), xytext=(21.5, 9.5), arrowprops=arr)
    ax.annotate("", xy=(27, 25.5), xytext=(21.5, 25.5), arrowprops=arr)
    ax.annotate("", xy=(54, 15), xytext=(48.5, 9.5), arrowprops=arr)
    ax.annotate("", xy=(54, 20), xytext=(48.5, 25.5), arrowprops=arr)
    ax.annotate("", xy=(81, 17.5), xytext=(76.5, 17.5), arrowprops=arr)
    ax.annotate("", xy=(65, 24.6), xytext=(90, 24.6), arrowprops=dict(arrowstyle="-|>", color="#eb6834", lw=0.8,
                                                                        connectionstyle="arc3,rad=0.35"))
    ax.text(77.5, 31.5, "own scores accumulate (n_b = 24·(h-1))", ha="center", fontsize=6.2, color=INK2)
    ax.text(38, 1.0, "κ, K chosen by leave-one-building-out on calibration buildings only", ha="center",
            fontsize=6.2, color=INK2)
    _save(fig, "Fig1_method")


def fig_data(meta_bdg2, meta_uci, load_b, load_u):
    fig, axs = plt.subplots(1, 2, figsize=(190 * MM, 55 * MM))
    vc = meta_bdg2.usage.value_counts()
    vc = pd.concat([vc.iloc[:7], pd.Series({"Other (9 types)": vc.iloc[7:].sum()})])
    axs[0].barh(vc.index[::-1], vc.values[::-1], color="#2a78d6", height=0.6)
    for i, v in enumerate(vc.values[::-1]):
        axs[0].text(v + 3, i, str(v), va="center", fontsize=6, color=INK2)
    axs[0].set_xlabel("BDG2 buildings (after quality filter)")
    axs[0].set_title("a  Primary space usage (BDG2, n = %d, %d sites)" % (len(meta_bdg2), meta_bdg2.site_id.nunique()),
                     loc="left")
    mb = np.nanmean(load_b, axis=(1, 2))
    mu = np.nanmean(load_u, axis=(1, 2))
    bins = np.logspace(0, 4, 40)
    axs[1].hist(mb, bins=bins, color="#2a78d6", alpha=0.85, label=f"BDG2 (n = {len(mb)})")
    axs[1].hist(mu, bins=bins, color="#eb6834", alpha=0.75, label=f"UCI (n = {len(mu)})")
    axs[1].set_xscale("log")
    axs[1].set_xlabel("Mean hourly load (kWh)")
    axs[1].set_ylabel("Buildings / clients")
    axs[1].legend(frameon=False)
    axs[1].set_title("b  Size distribution", loc="left")
    _save(fig, "Fig2_data")


def fig_stage_curves(cv, tag):
    fig, axs = plt.subplots(2, 2, figsize=(190 * MM, 100 * MM), sharex=True)
    for j, ds in enumerate(["BDG2", "UCI"]):
        d = cv[cv.part.str.startswith(f"main{tag}_{ds}_s") & cv.part.str.endswith("a0.1")]
        g = d.groupby(["method", "stage"])[["coverage", "rel_IS"]].mean().reset_index()
        for m in KEY:
            gm = g[g.method == m]
            if not len(gm):
                continue
            axs[0, j].plot(gm.stage, gm.coverage, color=_c(m), marker=MARK[m], markersize=2.5, markevery=7,
                           label=m, lw=1.6 if m.startswith("HSC") else 1.0)
            axs[1, j].plot(gm.stage, gm.rel_IS, color=_c(m), marker=MARK[m], markersize=2.5, markevery=7,
                           lw=1.6 if m.startswith("HSC") else 1.0)
        axs[0, j].axhline(0.9, color=INK, lw=0.8, ls="--")
        axs[0, j].set_title(f"{'ab'[j]}  {ds}: mean per-building coverage by onboarding day", loc="left")
        axs[1, j].set_title(f"{'cd'[j]}  {ds}: mean relative interval score", loc="left")
        axs[1, j].set_xlabel("Days of history h (forecast for day h+1)")
        axs[1, j].set_yscale("log")
    axs[0, 0].set_ylabel("Coverage (nominal 0.90)")
    axs[1, 0].set_ylabel("Rel. interval score (log)")
    axs[0, 1].legend(ncol=2, frameon=False, loc="lower right")
    _save(fig, "Fig3_stage_curves")


def fig_cov_dist(df):
    fig, axs = plt.subplots(1, 2, figsize=(190 * MM, 60 * MM), sharey=True)
    for j, ds in enumerate(["BDG2", "UCI"]):
        d = df[(df.exp == "main") & (df.dataset == ds) & (df.alpha == 0.1)]
        for m in KEY:
            c = np.sort(d[d.method == m].coverage.values)
            if not len(c):
                continue
            axs[j].plot(c, np.arange(1, len(c) + 1) / len(c), color=_c(m), lw=1.6 if m.startswith("HSC") else 1.0,
                        label=m, ls="-" if m.startswith("HSC") else (0, (3, 1)))
        axs[j].axvline(0.9, color=INK, lw=0.8, ls="--")
        axs[j].axvline(0.85, color=INK2, lw=0.6, ls=":")
        axs[j].set_xlim(0.55, 1.0)
        axs[j].set_xlabel("Per-building coverage over the 56-day onboarding window")
        axs[j].set_title(f"{'ab'[j]}  {ds}: empirical CDF across buildings × seeds", loc="left")
    axs[0].set_ylabel("Share of buildings ≤ x")
    axs[1].legend(frameon=False, loc="upper left", ncol=1)
    _save(fig, "Fig4_coverage_cdf")


def fig_tradeoff(s):
    fig, axs = plt.subplots(1, 2, figsize=(190 * MM, 70 * MM))
    for j, ds in enumerate(["BDG2", "UCI"]):
        d = s[(s.exp == "main") & (s.dataset == ds) & (s.alpha == 0.1) & (s.perturb == "none")]
        g = d.groupby("method")[["macd", "rel_IS"]].agg(["mean", "std"])
        for m in g.index:
            if m.startswith("HSC ") or m == "Raw-SCP":
                continue
            x, y = g.loc[m, ("rel_IS", "mean")], g.loc[m, ("macd", "mean")]
            axs[j].errorbar(x, y, xerr=g.loc[m, ("rel_IS", "std")], yerr=g.loc[m, ("macd", "std")], fmt=MARK.get(m, "o"),
                            color=_c(m), ms=5 if m in COL else 3.5, elinewidth=0.6, capsize=1.5)
            axs[j].annotate(m, (x, y), xytext=(4, 3), textcoords="offset points", fontsize=6, color=INK)
        axs[j].set_xlabel("Median relative interval score (lower = sharper & valid)")
        axs[j].set_title(f"{'ab'[j]}  {ds}", loc="left")
    axs[0].set_ylabel("MACD = mean |coverage_b − 0.90| (lower = more reliable)")
    _save(fig, "Fig5_tradeoff")


def fig_ablation(s):
    meths = ["HSC", "HSC -stage", "HSC -kNN", "HSC -shrink", "HSC fixed-kappa", "HSC -kNN -stage", "Self-CP",
             "SCP-stage"]
    fig, axs = plt.subplots(1, 2, figsize=(190 * MM, 58 * MM))
    w = 0.38
    for j, metric, lab in [(0, "macd", "MACD"), (1, "rel_IS", "Median rel. interval score")]:
        for k, ds in enumerate(["BDG2", "UCI"]):
            d = s[(s.exp == "main") & (s.dataset == ds) & (s.alpha == 0.1) & (s.perturb == "none")]
            g = d.groupby("method")[metric].agg(["mean", "std"]).reindex(meths)
            x = np.arange(len(meths)) + (k - 0.5) * w
            axs[j].bar(x, g["mean"], w * 0.92, yerr=g["std"], color=["#2a78d6", "#eb6834"][k], label=ds,
                       error_kw=dict(lw=0.6, capsize=1.5))
        axs[j].set_xticks(np.arange(len(meths)))
        axs[j].set_xticklabels(meths, rotation=35, ha="right")
        axs[j].set_ylabel(lab)
        axs[j].set_title(f"{'ab'[j]}  {lab}", loc="left")
    axs[0].legend(frameon=False)
    _save(fig, "Fig6_ablation")


def fig_robust(s):
    rb = s[s.exp == "robust"]
    if not len(rb):
        return
    perts = ["noise5", "noise15", "missing20", "missing40", "shift+40", "shift-40", "calpool10", "calpool25",
             "calpool50", "weak-forecaster"]
    perts = [p for p in perts if p in set(rb.perturb)]
    meths = ["HSC-CQR", "CQR", "QR-LGBM", "MLP-QR", "HSC", "SCP-stage", "ACI"]
    fig, axs = plt.subplots(2, 1, figsize=(190 * MM, 95 * MM), sharex=True)
    w = 0.8 / len(meths)
    for j, metric, lab in [(0, "macd", "MACD"), (1, "under_rate", "Share of buildings under-covered (<0.85)")]:
        for k, m in enumerate(meths):
            g = rb[rb.method == m].groupby("perturb")[metric].mean().reindex(perts)
            axs[j].bar(np.arange(len(perts)) + (k - len(meths) / 2 + 0.5) * w, g.values, w * 0.9, color=_c(m),
                       label=m)
        axs[j].set_ylabel(lab)
    axs[1].set_xticks(np.arange(len(perts)))
    axs[1].set_xticklabels(perts, rotation=20)
    axs[0].legend(ncol=7, frameon=False, loc="upper left", bbox_to_anchor=(0, 1.18))
    axs[0].set_title("a  Per-building miscalibration under stress (BDG2, 3 seeds)", loc="left", pad=14)
    axs[1].set_title("b  Under-coverage", loc="left")
    _save(fig, "Fig7_robustness")


def fig_generalisation(s):
    combos = [("main", "BDG2", "random", "BDG2 random"), ("lso", "BDG2", "leave-site-out", "BDG2 leave-site-out"),
              ("xds", "BDG2", "BDG2->BDG2 (no weather)", "BDG2→BDG2 no-wx"),
              ("xds", "BDG2", "UCI->BDG2 (no weather)", "UCI→BDG2 no-wx"), ("main", "UCI", "random", "UCI random"),
              ("xds", "UCI", "BDG2->UCI (no weather)", "BDG2→UCI no-wx")]
    meths = ["HSC-CQR", "CQR", "QR-LGBM", "MLP-QR", "HSC", "SCP-stage"]
    fig, axs = plt.subplots(1, 2, figsize=(190 * MM, 62 * MM))
    w = 0.8 / len(meths)
    labs = []
    for ci, (e, ds, p, lab) in enumerate(combos):
        d = s[(s.exp == e) & (s.dataset == ds) & (s.protocol == p) & (s.alpha == 0.1) & (s.perturb == "none")]
        if not len(d):
            continue
        labs.append((ci, lab))
        for k, m in enumerate(meths):
            v = d[d.method == m]
            for j, metric in enumerate(["macd", "rel_IS"]):
                axs[j].bar(ci + (k - len(meths) / 2 + 0.5) * w, v[metric].mean(), w * 0.9, color=_c(m),
                           label=m if ci == 0 else None)
    for j, lab in enumerate(["MACD", "Median rel. interval score"]):
        axs[j].set_xticks([c for c, _ in labs])
        axs[j].set_xticklabels([l for _, l in labs], rotation=30, ha="right")
        axs[j].set_ylabel(lab)
        axs[j].set_title(f"{'ab'[j]}  {lab}", loc="left")
    axs[0].legend(frameon=False, ncol=2)
    _save(fig, "Fig8_generalisation")


def fig_sensitivity(tag):
    p = os.path.join(RES, f"sensitivity{tag}.csv")
    if not os.path.exists(p):
        return
    d = pd.read_csv(p)
    d = d[np.isfinite(d.kappa) | (d.kappa == np.inf)]
    fig, axs = plt.subplots(2, 2, figsize=(190 * MM, 95 * MM))
    for j, ds in enumerate(["BDG2", "UCI"]):
        g = d[(d.dataset == ds) & (d.score == "cqr")].groupby(["K", "kappa"])[["macd", "rel_IS"]].mean().reset_index()
        g = g[g.kappa > 0]
        for i, metric in enumerate(["macd", "rel_IS"]):
            for kk, K in enumerate(["10", "25", "50", "100", "all"]):
                gk = g[g.K.astype(str) == K]
                xs = np.where(np.isinf(gk.kappa), 3000, gk.kappa)
                axs[i, j].plot(xs, gk[metric], marker="o", ms=2.5, lw=1.0,
                               color=["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"][kk], label=f"K={K}")
            axs[i, j].set_xscale("log")
            axs[i, j].set_xticks([24, 96, 336, 1344, 3000])
            axs[i, j].set_xticklabels(["24", "96", "336", "1344", "∞"])
            axs[i, j].set_title(f"{'abcd'[2 * i + j]}  {ds}: HSC-CQR {'MACD' if metric == 'macd' else 'median rel. IS'}",
                                loc="left")
        axs[1, j].set_xlabel("Prior pseudo-count κ (hours of scores)")
    axs[0, 0].legend(frameon=False, ncol=3)
    _save(fig, "Fig9_sensitivity")


def fig_errors(df):
    d = df[(df.exp == "main") & (df.alpha == 0.1) & (df.dataset == "BDG2")]
    fig, axs = plt.subplots(1, 2, figsize=(190 * MM, 62 * MM))
    for m in ["CQR", "HSC-CQR"]:
        dm = d[d.method == m]
        axs[0].scatter(dm.cvrmse_lgb, dm.coverage, s=3, alpha=0.45, color=_c(m), label=m, linewidths=0)
    axs[0].set_xscale("log")
    axs[0].axhline(0.9, color=INK, lw=0.8, ls="--")
    axs[0].set_xlabel("Point-forecast CV(RMSE) of the building (log)")
    axs[0].set_ylabel("Per-building coverage")
    axs[0].legend(frameon=False, markerscale=3)
    axs[0].set_title("a  Coverage vs. forecast difficulty (BDG2)", loc="left")
    dm = d[d.method == "HSC-CQR"]
    u = dm.groupby("usage").coverage.agg(["mean", "size"]).query("size >= 30").sort_values("mean")
    dc = d[d.method == "CQR"].groupby("usage").coverage.mean().reindex(u.index)
    y = np.arange(len(u))
    axs[1].scatter(dc.values, y, color=_c("CQR"), marker="s", s=14, label="CQR", zorder=3)
    axs[1].scatter(u["mean"].values, y, color=_c("HSC-CQR"), marker="o", s=14, label="HSC-CQR", zorder=3)
    for yi, a, b in zip(y, dc.values, u["mean"].values):
        axs[1].plot([a, b], [yi, yi], color=GREY, lw=0.6, zorder=1)
    axs[1].set_yticks(y)
    axs[1].set_yticklabels([f"{i} (n={n})" for i, n in zip(u.index, u["size"])])
    axs[1].axvline(0.9, color=INK, lw=0.8, ls="--")
    axs[1].set_xlabel("Mean per-building coverage")
    axs[1].legend(frameon=False)
    axs[1].set_title("b  By primary usage (BDG2, building×seed units)", loc="left")
    _save(fig, "Fig10_error_analysis")


def fig_examples(tag):
    p = os.path.join(RES, f"examples_BDG2{tag}.csv")
    if not os.path.exists(p):
        return
    d = pd.read_csv(p)
    fig, axs = plt.subplots(2, 1, figsize=(190 * MM, 85 * MM))
    for i, pick in enumerate(["p10", "p50"]):
        e = d[(d.pick == pick) & (d.stage <= 10)]
        b = e.building.iloc[0]
        for m, c in [("CQR", _c("CQR")), ("HSC-CQR", _c("HSC-CQR"))]:
            em = e[e.method == m].sort_values(["stage", "hour"])
            t = (em.stage.values - 1) * 24 + em.hour.values + 24
            axs[i].fill_between(t, em.lo, em.hi, color=c, alpha=0.22 if m == "CQR" else 0.18, lw=0, label=f"{m} 90 % PI")
        em = e[e.method == "CQR"].sort_values(["stage", "hour"])
        t = (em.stage.values - 1) * 24 + em.hour.values + 24
        axs[i].plot(t, em.y, color=INK, lw=0.7, label="observed")
        axs[i].set_title(f"{'ab'[i]}  {b} ({'10th' if pick == 'p10' else '50th'} percentile of CQR coverage, seed 0)",
                         loc="left")
        axs[i].set_ylabel("kWh")
    axs[1].set_xlabel("Hours since metering started (first 10 forecast days)")
    axs[0].legend(ncol=3, frameon=False, loc="upper right")
    _save(fig, "Fig11_examples")


def run(mode="full"):
    import sys
    sys.path.insert(0, ROOT)
    from src.statistics.analysis import load, seed_level
    from src.experiments import get_ds
    tag = "_quick" if mode == "quick" else ""
    df = load()
    df = df[df.part.str.contains("_quick") == (mode == "quick")]
    s = seed_level(df)
    cv = pd.read_csv(os.path.join(RES, "stage_curves.csv"))
    fig_schematic()
    b, u = get_ds("BDG2"), get_ds("UCI")
    fig_data(b["meta"], u["meta"], b["load"], u["load"])
    fig_stage_curves(cv, tag)
    fig_cov_dist(df)
    fig_tradeoff(s)
    fig_ablation(s)
    fig_robust(s)
    fig_generalisation(s)
    fig_sensitivity(tag)
    fig_errors(df)
    fig_examples(tag)
