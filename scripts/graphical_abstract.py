"""Graphical abstract (Elsevier: >= 1328 x 531 px, readable at 13 x 5 cm). Values from tables/MS5_main.csv."""
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
t = pd.read_csv(os.path.join(ROOT, "tables", "MS5_main.csv"))
col = [c for c in t.columns if c.startswith("Weeks 2")][0]
def v(data, strat):
    r = t[(t["Data"] == data) & (t["Strategy"] == strat)]
    return float(r[col].iloc[0])
vals = {d: [v(d, "Pooled CQR"), v(d, "Oracle reference"), v(d, "TTSC (proposed)")] for d in ["BDG2", "UCI"]}

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})
fig = plt.figure(figsize=(13.28, 5.31))
C = ["#9aa5b1", "#d9a441", "#1f6fb2"]

def box(ax, x, y, w, h, txt, fc, fs=11, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.02", fc=fc, ec="#333", lw=1.2))
    ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=fs, weight="bold" if bold else "normal", wrap=True)

ax = fig.add_axes([0.0, 0.0, 0.64, 1.0]); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
ax.text(0.02, 0.93, "Newly enrolled building: load intervals must hold per building, per settlement week",
        fontsize=13.5, weight="bold", va="center")
box(ax, 0.02, 0.50, 0.25, 0.30, "Previously onboarded\nbuildings\n(calibration scores)", "#eef2f6")
box(ax, 0.02, 0.10, 0.25, 0.30, "New building\nfirst days of own\nforecast errors", "#eef2f6")
box(ax, 0.36, 0.50, 0.30, 0.30, "Slow timescale\nshrinkage prior:\npopulation  →  recency-\nweighted own scores", "#dbe9f6")
box(ax, 0.36, 0.10, 0.30, 0.30, "Fast timescale\n7-day feedback on the\nmiscoverage level\n(= settlement week)", "#dbe9f6")
box(ax, 0.75, 0.28, 0.23, 0.34, "TTSC\nday-ahead 90 %\nintervals,\nfrom day 1", "#1f6fb2", fs=12.5, bold=True)
ax.texts[-1].set_color("white")
kw = dict(arrowstyle="-|>", lw=1.6, color="#333", mutation_scale=16)
for (a, b) in [((0.27, 0.65), (0.36, 0.65)), ((0.27, 0.25), (0.36, 0.25)), ((0.27, 0.22), (0.36, 0.60)),
               ((0.66, 0.65), (0.75, 0.50)), ((0.66, 0.25), (0.75, 0.40))]:
    ax.annotate("", xy=b, xytext=a, arrowprops=kw)
ax.text(0.515, 0.03, "Parameters tuned by leave-one-building-out for weekly reliability",
        ha="center", fontsize=10.5, style="italic")

bx = fig.add_axes([0.70, 0.17, 0.28, 0.66])
import numpy as np
x = np.arange(2); w = 0.26
labels = ["Pooled CQR", "Oracle reference", "TTSC"]
for i in range(3):
    ys = [vals["BDG2"][i], vals["UCI"][i]]
    bars = bx.bar(x + (i - 1) * w, ys, w, color=C[i], label=labels[i], ec="#333", lw=0.6)
    for b_, y in zip(bars, ys):
        bx.text(b_.get_x() + b_.get_width() / 2, y + 0.5, f"{y:.1f}", ha="center", fontsize=9.5)
bx.set_xticks(x, ["1,042 buildings\n(BDG2)", "316 clients\n(UCI)"])
bx.set_ylabel("Buildings under-covered\nin a typical week (%)")
bx.set_ylim(0, max(max(v_) for v_ in vals.values()) * 1.25)
bx.spines[["top", "right"]].set_visible(False)
bx.legend(frameon=False, fontsize=9.5, loc="upper right")
bx.set_title("Weekly under-coverage (weeks 2–8)", fontsize=12, weight="bold")
out = os.path.join(ROOT, "manuscript", "graphical_abstract", "Graphical_abstract")
fig.savefig(out + ".png", dpi=300); fig.savefig(out + ".pdf")
print("saved", out, vals)
