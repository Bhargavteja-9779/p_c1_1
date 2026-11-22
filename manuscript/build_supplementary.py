"""Supplementary material (DOCX + MD) assembled from machine-generated tables and result files.
Numbering is fixed because the manuscript cites it: Table S1 features; S2/S3 full main results; S4 paired tests of
the recommended method; S5 site-level tests; S6-S9 nominal 95 % / 80 %; S10-S13 generalisation; S14 robustness;
S15 selected parameters; S16-S21 extended analyses; S22 stage-wise coverage. Sections: S1 features, S2 refinements, S3 baseline details, S4 deviations + protocol."""
import json
import os
import re
import subprocess
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
T = os.path.join(ROOT, "tables")
sys.path.insert(0, HERE)


def _tab(name, caption):
    p = os.path.join(T, name + ".md")
    if not os.path.exists(p):
        raise FileNotFoundError(p)
    body = open(p).read()
    if body.startswith("**"):
        body = body.split("\n", 2)[2]
    return f"**{caption}**\n\n{body}\n\n"


def _site_table():
    st = pd.read_csv(os.path.join(ROOT, "results", "statistics.csv"))
    rec = json.load(open(os.path.join(ROOT, "results", "recommended.json")))["recommended"]
    t = st[(st.proposed == rec) & (st.dataset == "BDG2") & (st.protocol == "random") & (st.perturb == "none") &
           (st.alpha == 0.1)]
    rows = ["| Baseline | Metric | Better (%) | p (buildings, Holm) | p (10 site means) | p (without largest site) |",
            "|:--|:--|--:|--:|--:|--:|"]
    lab = {"abs_dev": "CD", "abs_dev_early": "CD wk 1", "rel_IS": "IS"}
    f = lambda p: "<0.001" if p < 0.001 else f"{p:.3f}"  # noqa: E731
    for _, r in t.iterrows():
        rows.append(f"| {r.baseline} | {lab[r.metric]} | {100 * r.share_proposed_better:.0f} | {f(r.p_holm)} | "
                    f"{f(r.p_site)} | {f(r.p_excl_largest_site)} |")
    big = t.excluded_site.iloc[0] if len(t) else ""
    return (f"**Table S5. Site-level robustness of the paired comparisons of {rec} on BDG2 (90 %). p (10 site means): "
            f"Wilcoxon signed-rank test on the ten site means of the paired differences (smallest attainable two-sided "
            f"p = 0.002); p (without largest site): building-level Wilcoxon test without site '{big}'. CD = absolute "
            f"coverage deviation over the window; CD wk 1 = the same for the first week; IS = relative interval "
            f"score.**\n\n" + "\n".join(rows) + "\n\n")



def build():
    import values as V
    vals = json.load(open(os.path.join(ROOT, "results", "manuscript_values.json")))
    rec = vals.get("PRIMARY", "HSC-CQR recency")
    s = ["---\ntitle: \"Supplementary material: Two-timescale conformal calibration for week-by-week re"
         "liable day-ahead load intervals of newly enrolled buildings\"\n---\n"]
    s.append("# S1. Input features of the global forecasters\n\n")
    s.append(_tab("MS_features", "Table S1. Input features (identical for LightGBM and MLP models)."))
    s.append("# S2. Refinements examined: onboarding-stage matching and similarity-localised population distribution\n\n"
             "*Stage matching.* Calibration scores are grouped into onboarding-stage bins $\\{1\\},\\{2\\},\\{3\\},"
             "\\{4..6\\},\\{7..13\\},\\{14..27\\},\\{28..56\\}$; a forecast at stage $h$ is calibrated with the scores of "
             "the bin containing $h$.\n\n*Similarity-localised distribution.* From its most recent $\\min(h,28)$ observed "
             "days, each building is summarised by a descriptor $\\mathbf z_{b,h}$: its mean daily load profile divided "
             "by its mean load (24 values), the mean absolute day-to-day change of that normalised profile, and the "
             "logarithm of the mean load, computed in the same way for calibration buildings at the same stage. The "
             "population distribution is the average of the score distributions of the $K$ calibration buildings "
             "closest to $\\mathbf z_{b,h}$ (Euclidean distance after standardisation; buildings without valid scores "
             "or descriptor are skipped). $K\\in\\{10,25,50,100,\\text{all}\\}$ and $\\kappa$ were selected by "
             "leave-one-building-out with the interval-score objective (variant HSC-CQR).\n\n")
    s.append("# S3. Implementation details of all compared methods\n\nAll conformal-type methods share the same "
             "forecaster, scores and score grid; they differ only in how the radius is obtained.\n\n")
    txt = open(os.path.join(HERE, "supp_methods.md")).read()
    txt = re.sub(r"\{\{(.*?)\}\}", lambda m: str(vals[m.group(1).strip()]), txt)
    txt = re.sub(r"\[@[^\]]*\]", "", txt)  # citations are listed in the main article
    s.append(txt + "\n\n")
    s.append("# S4. Protocol and deviations\n\n"
             "1. The ACI step-size grid was extended to $\\{0, 10^{-4}, 2\\cdot10^{-4}\\}$ after a code audit showed that "
             "the lower edge of the original grid was selected in most runs.\n"
             "2. Mis-specified ablations of the first version were removed and replaced by the fixed-κ variant.\n"
             "3. After a pilot evaluation, Addendum A (written and committed before the corresponding "
             "experiments) added the coverage objective for HSC, QShrink and ACI, recency weighting (ρ = 0.95), "
             "stage-wise studentisation, the operational outcomes, the noise reference, site-level tests and the rule "
             "for the recommended configuration (Addendum A.1). It also fixed the TQA-B budget scaling and the ACI "
             "convention for α_h ≤ 0 (Section S3).\n"
             "4. At nominal 95 % and 80 %, all CQR-based methods use the quantile models trained for α = 0.1; the "
             "conformal step corrects the level. Uncalibrated quantile models (QR-LGBM, MLP-QR) are not reported at "
             "these levels.\n"
             "5. The original protocol selected the HSC pseudo-count by the interval score; this variant is reported "
             "(HSC-CQR, HSC-CQR simple).\n"
             "6. Before the final runs, the analysis was revised without reference to target results: (a) building "
             "eligibility is decided on the training period only, no target hours are interpolated, daylight-saving "
             "hours are masked, and targets without an onboarding window with at least 80 % valid hours are dropped and "
             "counted; (b) the running scale σ0 is estimated on training buildings; (c) every parametrised strategy is "
             "tuned by the same constrained leave-one-building-out rule (minimum MACD subject to an interval score at "
             "most 2 % above pooled CQR), with grids extended to κ, λ ∈ {6, 12} h and γ ≤ 0.05 and grid-edge selections "
             "reported; (d) QShrink-CQR recency, Self-CQR recency, a one-day-delayed and a capped variant, the layer on "
             "MLP quantiles and five further stress conditions were added; (e) the method-specific noise reference was "
             "replaced by a method-independent oracle reference (7-day moving-block bootstrap); (f) one confirmatory "
             "family was declared and the recommended configuration is selected by a nested rule (BDG2 selection, "
             "confirmation on UCI, unseen sites and both transfer directions). All models were retrained and all "
             "results recomputed.\n\nThe complete protocol, including the addenda, is reproduced at the end of "
             "this document.\n\n")
    s.append("# S5. Additional results\n\n")
    s.append(_tab("T_main_BDG2", "Table S2. All methods, BDG2, random-building protocol, nominal 90 % (mean ± s.d. over "
                                 "5 seeds; widths and interval scores are medians over buildings)."))
    s.append(_tab("T_main_UCI", "Table S3. All methods, UCI, random-building protocol, nominal 90 %."))
    s.append(_tab("MS2_tests", f"Table S4. Exploratory paired per-building comparisons of {rec} with the strongest alternatives (Wilcoxon on absolute coverage deviation and interval score)."))
    s.append(_site_table())
    n = 6
    for name, cap in [("T_alpha0.05_BDG2", "BDG2, nominal 95 %"), ("T_alpha0.05_UCI", "UCI, nominal 95 %"),
                      ("T_alpha0.2_BDG2", "BDG2, nominal 80 %"), ("T_alpha0.2_UCI", "UCI, nominal 80 %"),
                      ("T_gen_leave-site-out", "BDG2 leave-site-out (5 site folds)"),
                      ("T_gen_BDG2toUCI_nw", "BDG2 → UCI transfer (no weather; 3 seeds)"),
                      ("T_gen_UCItoBDG2_nw", "UCI → BDG2 transfer (no weather; 3 seeds)"),
                      ("T_gen_BDG2toBDG2_nw", "BDG2 → BDG2 without weather features (reference; 3 seeds)")]:
        s.append(_tab(name, f"Table S{n}. {cap}."))
        n += 1
    s.append(_tab("T_robustness", f"Table S{n}. Robustness conditions on BDG2, all strategies (mean over 3 seeds)."))
    n += 1
    info = json.load(open(os.path.join(ROOT, "results", "run_info.json")))
    rows = ["| Run | κ recency (cov) | κ simple (cov) | κ simple (IS) | λ QShrink (cov) | γ ACI-CQR | γ ACI-CQR (cov) |",
            "|:--|--:|--:|--:|--:|--:|--:|"]
    g = lambda d, k: (d.get(k) or {}).get("kappa") if isinstance(d.get(k), dict) else d.get(k)  # noqa: E731
    for k, v in sorted(info.items()):
        if "a0.1" in k or k.startswith(("lso", "xds")):
            rows.append(f"| {k} | {g(v, 'hsc_cqr_recency')} | {g(v, 'hsc_cqr_simple_cov')} | {g(v, 'hsc_cqr_simple')} | "
                        f"{v.get('qshrink_lambda_cov')} | {v.get('aci_cqr_gamma')} | {v.get('aci_cqr_gamma_cov')} |")
    s.append(f"**Table S{n}. Parameters selected by leave-one-building-out on calibration buildings, per run.**\n\n"
             + "\n".join(rows) + "\n\n")
    # extended analyses (per-building unit): S16 confirmatory family, S17 weekly, S18 tails, S19 matched kappa,
    # S20 stress tests (all strategies), S21 threshold sensitivity, S22 SSC stage-wise coverage
    n += 1
    for name, cap in [("T2_confirmatory", "Single-timescale analysis: confirmatory family of the recommended single-timescale configuration (HSC-CQR recency) versus pooled CQR, QShrink-CQR (cov), "
                       "ACI-CQR (cov) and Self-CQR (paired share differences with 95 % site-cluster (BDG2) or building (UCI) "
                       "bootstrap CI, McNemar tests, TOST equivalence of the interval score within 2 %; Holm over the family)"),
                      ("T2_weekly", "Window, first-week and weekly under-coverage with the oracle reference and excess over it"),
                      ("T2_tails", "Sharpness tails: median and mean relative interval score, width ratio to pooled CQR, "
                       "capacity-headroom cost"),
                      ("T2_matched_kappa", "Under-covered share over the window and in the first week at matched pseudo-count "
                       "for own-score decay factors 0.8–1.0"),
                      ("T2_robustness", "Stress tests on BDG2, all strategies (3 seeds; unit = building; McNemar against the "
                       "recommended configuration)"),
                      ("T2_threshold", "Share of buildings more than 2, 3, 5 and 10 points below the 90 % target")]:
        if os.path.exists(os.path.join(ROOT, "tables", name + ".md")):
            s.append(_tab(name, f"Table S{n}. {cap}."))
            n += 1
    sc = os.path.join(ROOT, "results", "stage_curves.csv")
    if os.path.exists(sc):
        c = pd.read_csv(sc)
        rows = ["| Data | Method | Mean stage-wise coverage | Stages below 0.90 (%) | Lowest stage-wise coverage |",
                "|:--|:--|--:|--:|--:|"]
        for d in ["BDG2", "UCI"]:
            x = c[c.part.str.match(rf"main_{d}_s\d_a0\.1$")]
            for m in ["SSC-CQR", "HSC-SSC-CQR", rec, "CQR"]:
                y = x[x.method == m].groupby("stage").coverage.mean()
                if len(y):
                    rows.append(f"| {d} | {m} | {y.mean():.3f} | {100 * (y < 0.9).mean():.0f} | {y.min():.3f} |")
        s.append(f"**Table S{n}. Stage-wise coverage (coverage over all target buildings at each onboarding day, mean "
                 "over five seeds; nominal 0.90). The stage-wise guarantee of SSC-CQR assumes exchangeable calibration "
                 "and target periods, which does not hold in this protocol.**\n\n" + "\n".join(rows) + "\n\n")
    n += 1
    for name, cap in [("TT_tests", "TTSC: paired per-building comparisons (difference TTSC minus baseline in shares; 95 % "
                       "site-cluster (BDG2) or building (UCI) bootstrap CI; Wilcoxon signed-rank; Holm over the declared "
                       "family; 'seeds 2–4' = held-out runs)"),
                      ("TT_main", "TTSC and comparators, main protocol (90 %), all metrics, all and held-out seeds"),
                      ("TT_other", "TTSC and comparators under all other protocols, stress tests and nominal levels"),
                      ("TT_params", "Pseudo-count κ and feedback gain γ selected by leave-one-building-out, per run"),
                      ("MS3_main", "Single-timescale strategies: per-building reliability and sharpness (90 %)"),
                      ("MS3_robust", "Single-timescale strategies: stress tests on BDG2"),
                      ("MS2_operational", "Single-timescale strategies: capacity-headroom cost"),
                      ("TT_window", "TTSC: sensitivity to the feedback window W (γ re-selected for each W; mean over five "
                       "seeds, building × seed units) and share of building-days at the radius cap")]:
        f = os.path.join(ROOT, "tables", name + ".md")
        if os.path.exists(f):
            s.append(_tab(name, f"Table S{n}. {cap}."))
            n += 1
    figs = [("Fig7_robustness", "Robustness on BDG2 (MACD and under-covered share)."),
            ("Fig8_generalisation", "Generalisation (MACD and median relative interval score)."),
            ("Fig9_sensitivity", "Sensitivity of the stage-matched, similarity-localised variant to κ and K."),
            ("Fig3_stage_curves", "Mean coverage and median relative interval score by days of own history.")]
    s.append("# S6. Additional figures\n\n")
    for i, (f, cap) in enumerate(figs, 1):
        s.append(f"![**Fig. S{i}.** {cap}](figures/{f}.png){{width=16cm}}\n\n")
    s.append("# S7. Analysis protocol (as committed, including addenda)\n\n" +
             open(os.path.join(ROOT, "experiments", "PREREGISTRATION.md")).read().replace("# ", "## ", 1) + "\n")
    md = os.path.join(ROOT, "supplementary", "Supplementary_Material.md")
    os.makedirs(os.path.dirname(md), exist_ok=True)
    open(md, "w").write("".join(s))
    out = md.replace(".md", ".docx")
    subprocess.run(["pandoc", md, "-o", out, "--resource-path", ROOT, "--reference-doc",
                    os.path.join(HERE, "reference_style.docx")], check=True)
    print("built", out)


if __name__ == "__main__":
    build()
