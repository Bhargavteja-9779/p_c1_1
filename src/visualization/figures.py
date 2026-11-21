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

from src.statistics.names import disp  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RES = os.path.join(ROOT, "results")
FIG = os.path.join(ROOT, "figures")
MM = 1 / 25.4
PRIMARY = "HSC-CQR cov-κ"
COL = {PRIMARY: "#2a78d6", "CQR": "#eb6834", "ACI-CQR clip": "#1baf7a", "Self-CQR": "#eda100", "Switch-CQR": "#e87ba4",
       "QShrink-CQR": "#008300", "HSC-CQR fixed-κ": "#6250d6", "SCP-stage": "#e34948"}
MARK = {PRIMARY: "o", "CQR": "s", "ACI-CQR clip": "^", "Self-CQR": "v", "Switch-CQR": "D", "QShrink-CQR": "P",
        "HSC-CQR fixed-κ": "X", "SCP-stage": "*"}
BOLD = (PRIMARY, "HSC-CQR fixed-κ")
GREY = "#8a8984"
INK, INK2 = "#0b0b0b", "#52514e"
KEY = [PRIMARY, "HSC-CQR fixed-κ", "Self-CQR", "Switch-CQR", "QShrink-CQR", "ACI-CQR clip", "CQR", "SCP-stage"]

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
    fig, ax = plt.subplots(figsize=(190 * MM, 80 * MM))
    ax.set_axis_off()
    ax.set_xlim(0, 100)
    ax.set_ylim(-9, 40)
    fs = 6.2
    boxes = [
        (0.5, 23, 21, 13, "Training buildings\n(training year)\nglobal LightGBM quantile\nmodels on normalised load"),
        (0.5, 3, 21, 15, "Calibration buildings\n(test year, Jan–Jun)\nsimulated onboarding;\nCQR scores $e$ pooled\ninto $F^{pool}$"),
        (26, 23, 22, 13, "New building $b$\n(test year, Jul–Dec)\nfeatures from its own\n$h$ days only"),
        (26, 3, 22, 15, "Pseudo-count $\\kappa$\nleave-one-building-out\non calibration buildings\n(coverage deviation)"),
        (52, 11, 26, 17, "Pseudo-count mixture (PCM)\n$\\tilde{F}(e)\\propto\\kappa F^{pool}(e)+\\#\\{i\\leq n_b: e_i\\leq e\\}$\n(normalised by $\\kappa+n_b+1$)\n$q=\\tilde{F}^{-1}(1-\\alpha)$"),
        (81, 11, 18.5, 17, "Day-ahead interval\n$[\\hat{y}^{lo}-qs,\\ \\hat{y}^{hi}+qs]$\nfor the 24 h of\nday $h+1$"),
    ]
    for x, y, w, h, t in boxes:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3,rounding_size=1.0", fc="#f0f5fc",
                                    ec="#2a78d6", lw=0.8))
        ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs, color=INK, linespacing=1.6)
    arr = dict(arrowstyle="-|>", color=INK2, lw=0.8)
    ax.annotate("", xy=(25.6, 29.5), xytext=(21.9, 29.5), arrowprops=arr)
    ax.annotate("", xy=(25.6, 10.5), xytext=(21.9, 10.5), arrowprops=arr)
    ax.annotate("", xy=(51.6, 16), xytext=(48.4, 10.5), arrowprops=arr)
    ax.annotate("", xy=(51.6, 23), xytext=(48.4, 29.5), arrowprops=arr)
    ax.annotate("", xy=(80.6, 19.5), xytext=(78.4, 19.5), arrowprops=arr)
    ax.annotate("", xy=(66, 28.6), xytext=(90, 28.6), arrowprops=dict(arrowstyle="-|>", color="#eb6834", lw=0.9,
                                                                        connectionstyle="arc3,rad=0.45"))
    ax.text(78, 37.2, "realised scores of day $h+1$ are added to $b$'s own scores ($n_b=24(h-1)$)", ha="center",
            fontsize=fs, color=INK2)
    # timeline of the out-of-time protocol
    y0 = -5
    for x0, x1, lab, c in [(2, 34, "training year: forecaster", "#8a8984"),
                           (36, 66, "test year H1: calibration windows", "#2a78d6"),
                           (68, 98, "test year H2: target windows", "#eb6834")]:
        ax.plot([x0, x1], [y0, y0], color=c, lw=3, solid_capstyle="butt")
        ax.text((x0 + x1) / 2, y0 - 3.2, lab, ha="center", fontsize=fs, color=INK2)
    ax.text(0, y0 + 2.2, "time", fontsize=fs, color=INK2)
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


def _blocks(g):
    """Daily values for days 1-7, then 7-day block means (plotted at block mid-day)."""
    st = g.stage.values
    blk = np.where(st <= 7, st, 7 + 7 * ((st - 8) // 7) + 4)
    return g.assign(x=blk).groupby("x").mean(numeric_only=True).reset_index()


def fig_stage_curves(cv, tag):
    meths = KEY
    fig, axs = plt.subplots(2, 2, figsize=(190 * MM, 110 * MM), sharex=True)
    fig.subplots_adjust(hspace=0.32, wspace=0.22)
    for j, ds in enumerate(["BDG2", "UCI"]):
        d = cv[cv.part.str.startswith(f"main{tag}_{ds}_s") & cv.part.str.endswith("a0.1")]
        col_is = "rel_IS_median" if "rel_IS_median" in d.columns else "rel_IS"
        g = d.groupby(["method", "stage"])[["coverage", col_is]].mean().reset_index().rename(columns={col_is: "rel_IS"})
        for m in meths:
            gm = g[g.method == m]
            if not len(gm):
                continue
            gb = _blocks(gm)
            kw = dict(color=_c(m), marker=MARK.get(m, "o"), markersize=3, lw=1.8 if m in BOLD else 0.9,
                      ls="-" if m in BOLD else (0, (3, 1)))
            axs[0, j].plot(gb.x, gb.coverage, label=disp(m), **kw)
            axs[1, j].plot(gb.x, gb.rel_IS, **kw)
        axs[0, j].axhline(0.9, color=INK, lw=0.8, ls="--")
        axs[0, j].set_title(f"{'ab'[j]}  {ds}: mean coverage", loc="left")
        axs[1, j].set_title(f"{'cd'[j]}  {ds}: median relative interval score", loc="left")
        axs[1, j].set_xlabel("Days of own history h (daily to h = 7, then weekly means)")
        axs[0, j].axvspan(0.5, 7.5, color="#f0efec", zorder=0)
        axs[1, j].axvspan(0.5, 7.5, color="#f0efec", zorder=0)
    axs[0, 0].set_ylabel("Coverage (nominal 0.90)")
    axs[1, 0].set_ylabel("Median relative interval score")
    h, l = axs[0, 0].get_legend_handles_labels()
    fig.legend(h, l, ncol=4, frameon=False, loc="lower center", bbox_to_anchor=(0.5, -0.05))
    fig.subplots_adjust(bottom=0.14)
    _save(fig, "Fig3_stage_curves")


def fig_cov_dist(df):
    fig, axs = plt.subplots(1, 2, figsize=(190 * MM, 60 * MM), sharey=True)
    for j, ds in enumerate(["BDG2", "UCI"]):
        d = df[(df.exp == "main") & (df.dataset == ds) & (df.alpha == 0.1)]
        for m in KEY:
            c = np.sort(d[d.method == m].coverage.values)
            if not len(c):
                continue
            axs[j].plot(c, np.arange(1, len(c) + 1) / len(c), color=_c(m), lw=1.6 if m in BOLD else 1.0,
                        label=disp(m), ls="-" if m in BOLD else (0, (3, 1)))
        axs[j].axvline(0.9, color=INK, lw=0.8, ls="--")
        axs[j].axvline(0.85, color=INK2, lw=0.6, ls=":")
        axs[j].set_xlim(0.55, 1.0)
        axs[j].set_xlabel("Per-building coverage over the 56-day onboarding window")
        axs[j].set_title(f"{'ab'[j]}  {ds}: empirical CDF across buildings × seeds", loc="left")
    axs[0].set_ylabel("Share of buildings ≤ x")
    axs[1].legend(frameon=False, loc="upper left", ncol=1)
    _save(fig, "Fig4_coverage_cdf")


def fig_tradeoff(s):
    """Dot plot (no label overlap): methods sorted by BDG2 MACD; MACD and median relative IS; both datasets."""
    meths = [PRIMARY, "HSC-CQR fixed-κ", "HSC-CQR simple", "HSC-CQR", "HSC-CQR (MLP)", "QShrink-CQR",
             "QShrink-CQR fixed-λ", "Self-CQR", "Switch-CQR", "ACI-CQR clip", "ACI-CQR", "Mondrian-site CQR", "Self-CP",
             "HSC", "TQA-B-CQR", "GHCP-CQR", "CQR", "CQR (MLP)", "MLP-QR", "MLP-Gauss", "QR-LGBM", "ACI", "SCP-stage",
             "Mondrian-usage", "Naive+SCP"]
    d = s[(s.exp == "main") & (s.alpha == 0.1) & (s.perturb == "none")]
    g = d.groupby(["dataset", "method"])[["macd", "rel_IS"]].agg(["mean", "std"])
    meths = [m for m in meths if ("BDG2", m) in g.index]
    meths = sorted(meths, key=lambda m: g.loc[("BDG2", m), ("macd", "mean")])
    fig, axs = plt.subplots(1, 2, figsize=(190 * MM, 95 * MM), sharey=True)
    y = np.arange(len(meths))[::-1]
    for j, (metric, lab) in enumerate([("macd", "MACD (lower = more reliable per building)"),
                                       ("rel_IS", "Median relative interval score (lower = better)")]):
        for k, (ds, col, mk) in enumerate([("BDG2", "#2a78d6", "o"), ("UCI", "#eb6834", "s")]):
            mu = [g.loc[(ds, m), (metric, "mean")] if (ds, m) in g.index else np.nan for m in meths]
            sd = [g.loc[(ds, m), (metric, "std")] if (ds, m) in g.index else np.nan for m in meths]
            axs[j].errorbar(mu, y + (0.15 if k == 0 else -0.15), xerr=sd, fmt=mk, color=col, ms=3.5, elinewidth=0.6,
                            capsize=1.2, label=ds)
        axs[j].set_xlabel(lab)
        axs[j].set_title(f"{'ab'[j]}", loc="left")
        axs[j].grid(axis="y", color="#f0efec")
    axs[0].set_yticks(y)
    axs[0].set_yticklabels([disp(m) for m in meths])
    for t in axs[0].get_yticklabels():
        if t.get_text() == disp(PRIMARY):
            t.set_fontweight("bold")
    axs[0].legend(frameon=False, loc="upper right")
    _save(fig, "Fig5_tradeoff")


def fig_ablation(s):
    meths = [PRIMARY, "HSC-CQR fixed-κ", "HSC-CQR simple", "HSC-CQR -kNN", "HSC-CQR -stage", "HSC-CQR",
             "HSC-CQR -shrink", "Self-CQR", "Switch-CQR", "CQR"]
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
        axs[j].set_xticklabels([disp(m) for m in meths], rotation=35, ha="right")
        axs[j].set_ylabel(lab)
        axs[j].set_title(f"{'ab'[j]}  {lab}", loc="left")
    axs[0].legend(frameon=False)
    _save(fig, "Fig6_ablation")


def fig_robust(s):
    rb = s[s.exp == "robust"]
    if not len(rb):
        return
    perts = ["noise15", "noise15 (cal+target)", "missing40", "outage 3d@d10", "shift+40@d5", "shift+40", "shift-40",
             "vol x2@d28", "temp-forecast error 2°C", "calpool10", "weak-forecaster"]
    nice = {"noise15": "noise\n15%", "noise15 (cal+target)": "noise 15%\ncal+tgt", "missing40": "missing\n40%",
            "outage 3d@d10": "outage\n3 d", "shift+40@d5": "level +40%\nday 5", "shift+40": "level +40%\nday 28",
            "shift-40": "level −40%\nday 28", "vol x2@d28": "volatility\n×2", "temp-forecast error 2°C": "temp. fc\nerror",
            "calpool10": "10% cal.\npool", "weak-forecaster": "weak\nforecaster"}
    meths = KEY[:-1]
    fig, axs = plt.subplots(2, 1, figsize=(190 * MM, 100 * MM))
    fig.subplots_adjust(hspace=0.55)
    w = 0.8 / len(meths)
    for j, ds in enumerate(["BDG2", "UCI"]):
        pp = [p for p in perts if p in set(rb[rb.dataset == ds].perturb)]
        for k, m in enumerate(meths):
            g = rb[(rb.method == m) & (rb.dataset == ds)].groupby("perturb")["macd"].mean().reindex(pp)
            axs[j].bar(np.arange(len(pp)) + (k - len(meths) / 2 + 0.5) * w, g.values, w * 0.9, color=_c(m),
                       label=disp(m) if j == 0 else None)
        axs[j].set_xticks(np.arange(len(pp)))
        axs[j].set_xticklabels([nice.get(p, p) for p in pp])
        axs[j].set_ylabel("MACD")
        axs[j].set_title(f"{'ab'[j]}  {ds}: per-building miscalibration under stress (3 seeds)", loc="left")
    axs[0].legend(ncol=4, frameon=False, loc="upper left", bbox_to_anchor=(0, 1.42), fontsize=5.8)
    _save(fig, "Fig7_robustness")


def fig_generalisation(s):
    combos = [("main", "BDG2", "random", "BDG2 random"), ("lso", "BDG2", "leave-site-out", "BDG2 leave-site-out"),
              ("xds", "BDG2", "BDG2->BDG2 (no weather)", "BDG2→BDG2 no-wx"),
              ("xds", "BDG2", "UCI->BDG2 (no weather)", "UCI→BDG2 no-wx"), ("main", "UCI", "random", "UCI random"),
              ("xds", "UCI", "BDG2->UCI (no weather)", "BDG2→UCI no-wx")]
    meths = KEY
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
                           label=disp(m) if ci == 0 else None)
    for j, lab in enumerate(["MACD", "Median rel. interval score"]):
        axs[j].set_xticks([c for c, _ in labs])
        axs[j].set_xticklabels([l for _, l in labs], rotation=30, ha="right")
        axs[j].set_ylabel(lab)
        axs[j].set_title(f"{'ab'[j]}  {lab}", loc="left")
    axs[0].legend(frameon=False, ncol=2, fontsize=5.8)
    _save(fig, "Fig8_generalisation")


def fig_sensitivity(tag):
    """Target-building MACD and median IS of the uniform-prior mixture (PCM-CQR) over the κ grid, with the
    distribution of κ selected on calibration buildings by LOBO-CD and LOBO-IS (never used for selection)."""
    p = os.path.join(RES, f"sensitivity{tag}.csv")
    if not os.path.exists(p):
        return
    import json
    d = pd.read_csv(p)
    info = json.load(open(os.path.join(RES, "run_info.json")))
    fig, axs = plt.subplots(2, 2, figsize=(190 * MM, 95 * MM))
    fig.subplots_adjust(hspace=0.5, wspace=0.25)
    for j, ds in enumerate(["BDG2", "UCI"]):
        g = d[(d.dataset == ds) & (d.score == "cqr") & (d.K.astype(str) == "uniform")]
        g = g.groupby(["seed", "kappa"])[["macd", "rel_IS"]].mean().reset_index()
        g = g[g.kappa > 0]
        picks = {lab: [info[k][key]["kappa"] for k in info if k.startswith(f"main{tag}_{ds}_s") and k.endswith("a0.1")
                       and key in info[k]] for lab, key in [("LOBO-CD", "hsc_cqr_covk"), ("LOBO-IS", "hsc_cqr_simple")]}
        for i, metric in enumerate(["macd", "rel_IS"]):
            for sd, gs in g.groupby("seed"):
                xs = np.where(np.isinf(gs.kappa), 3000, gs.kappa)
                axs[i, j].plot(xs, gs[metric], color="#c3c2bd", lw=0.7)
            m = g.groupby("kappa")[metric].mean()
            xs = np.where(np.isinf(m.index), 3000, m.index)
            axs[i, j].plot(xs, m.values, color=INK, marker="o", ms=2.5, lw=1.2, label="mean over seeds")
            for lab, col, off in [("LOBO-CD", "#2a78d6", 0.0), ("LOBO-IS", "#eb6834", 0.08)]:
                for kk in picks[lab]:
                    x = 3000 if np.isinf(kk) else kk
                    axs[i, j].axvline(x * (1 + off), color=col, lw=0.8, alpha=0.6,
                                      label=f"κ chosen by {lab}" if kk == picks[lab][0] else None)
            axs[i, j].set_xscale("log")
            axs[i, j].minorticks_off()
            axs[i, j].set_xticks([24, 96, 336, 1344, 3000])
            axs[i, j].set_xticklabels(["24", "96", "336", "1344", "∞"])
            axs[i, j].set_title(f"{'abcd'[2 * i + j]}  {ds}: {'MACD' if metric == 'macd' else 'median rel. IS'} "
                                "on target buildings", loc="left")
        axs[1, j].set_xlabel("Pseudo-count κ (hours of pooled scores)")
    axs[0, 0].legend(frameon=False, fontsize=5.8)
    _save(fig, "Fig9_sensitivity")


def fig_errors(df):
    d = df[(df.exp == "main") & (df.alpha == 0.1) & (df.dataset == "BDG2")]
    fig, axs = plt.subplots(1, 2, figsize=(190 * MM, 62 * MM))
    for m in ["CQR", PRIMARY]:
        dm = d[d.method == m]
        axs[0].scatter(dm.cvrmse_lgb, dm.coverage, s=3, alpha=0.45, color=_c(m), label=disp(m), linewidths=0)
    axs[0].set_xscale("log")
    axs[0].axhline(0.9, color=INK, lw=0.8, ls="--")
    axs[0].set_xlabel("Point-forecast CV(RMSE) of the building (log)")
    axs[0].set_ylabel("Per-building coverage")
    axs[0].legend(frameon=False, markerscale=3)
    axs[0].set_title("a  Coverage vs. forecast difficulty (BDG2)", loc="left")
    dm = d[d.method == PRIMARY]
    u = dm.groupby("usage").coverage.agg(["mean", "size"]).query("size >= 30").sort_values("mean")
    dc = d[d.method == "CQR"].groupby("usage").coverage.mean().reindex(u.index)
    y = np.arange(len(u))
    axs[1].scatter(dc.values, y, color=_c("CQR"), marker="s", s=14, label="CQR", zorder=3)
    axs[1].scatter(u["mean"].values, y, color=_c(PRIMARY), marker="o", s=14, label=disp(PRIMARY), zorder=3)
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
    fig, axs = plt.subplots(2, 1, figsize=(190 * MM, 95 * MM))
    fig.subplots_adjust(hspace=0.4)
    for i, pick in enumerate(["p10", "p50"]):
        e = d[(d.pick == pick) & (d.stage <= 10)]
        b = e.building.iloc[0]
        em0 = e[e.method == "CQR"].sort_values(["stage", "hour"])
        t = (em0.stage.values) * 24 + em0.hour.values
        axs[i].plot(t, em0.y, color=INK, lw=0.8, label="observed", zorder=3)
        for m, ls in [("CQR", (0, (3, 1.5))), (PRIMARY, "-")]:
            em = e[e.method == m].sort_values(["stage", "hour"])
            axs[i].plot(t, em.lo, color=_c(m), lw=0.9, ls=ls, label=f"{disp(m)} 90 % bounds")
            axs[i].plot(t, em.hi, color=_c(m), lw=0.9, ls=ls)
            miss = (em.y.values < em.lo.values) | (em.y.values > em.hi.values)
            axs[i].scatter(t[miss], em.y.values[miss], s=9, marker="x" if m == "CQR" else "o", color=_c(m),
                           zorder=4, linewidths=0.8, facecolors="none" if m == PRIMARY else None,
                           label=f"missed by {disp(m)}")
        axs[i].set_title(f"{'ab'[i]}  {b}: {'10th' if pick == 'p10' else '50th'} percentile of CQR coverage "
                         f"(seed 0, first 10 forecast days)", loc="left")
        axs[i].set_ylabel("kWh")
    axs[1].set_xlabel("Hours since metering started")
    axs[0].legend(ncol=5, frameon=False, loc="upper left", bbox_to_anchor=(0, 1.32))
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
