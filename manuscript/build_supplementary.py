"""Supplementary material (DOCX + MD) assembled from machine-generated tables."""
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
T = os.path.join(ROOT, "tables")


def _tab(name, caption):
    p = os.path.join(T, name + ".md")
    if not os.path.exists(p):
        return ""
    body = open(p).read()
    if body.startswith("**"):
        body = body.split("\n", 2)[2]
    return f"**{caption}**\n\n{body}\n\n"


def build():
    s = ["---\ntitle: \"Supplementary material: Reliable day-ahead prediction intervals for newly metered buildings\"\n---\n"]
    s.append("# S1. Deviations from the analysis plan\n\n" +
             open(os.path.join(ROOT, "experiments", "DEVIATIONS.md")).read().split("\n", 1)[1] + "\n\n")
    s.append("# S2. Methods and implementation details\n\n" +
             open(os.path.join(HERE, "supp_methods.md")).read() + "\n\n")
    s.append(_tab("MS_features", "Table S2. Forecaster features."))
    n = 3
    s.append("# S3. Full results (all methods; mean ± s.d. over seeds)\n\nRel. IS and Rel. width are medians over "
             "buildings; means are in tables/*_raw.csv.\n\n")
    for name, cap in [("MS_main_full_BDG2", "BDG2, random-building protocol, nominal 90 %, all methods"),
                      ("MS_main_full_UCI", "UCI, random-building protocol, nominal 90 %, all methods"),
                      ("MS_weeks", "Per-building reliability by onboarding week"),
                      ("MS_ablation", "Design elements and ablations"),
                      ("MS_alpha0.05_BDG2", "BDG2, nominal 95 %"), ("MS_alpha0.05_UCI", "UCI, nominal 95 %"),
                      ("MS_alpha0.2_BDG2", "BDG2, nominal 80 %"), ("MS_alpha0.2_UCI", "UCI, nominal 80 %"),
                      ("T_gen_leave-site-out", "BDG2 leave-one-site-out (10 sites × 3 training seeds)"),
                      ("T_loso_sites", "Leave-one-site-out: under-covered share per held-out site"),
                      ("T_loso_site_balanced", "Leave-one-site-out: site-balanced means"),
                      ("T_gen_BDG2toUCI_nw", "BDG2 → UCI transfer (no weather; 3 seeds)"),
                      ("T_gen_UCItoBDG2_nw", "UCI → BDG2 transfer (no weather; 3 seeds)"),
                      ("T_gen_BDG2toBDG2_nw", "BDG2 → BDG2 without weather features (reference; 3 seeds)"),
                      ("T_robustness", "Stress tests on BDG2 (mean over 3 seeds)"),
                      ("T_pools", "Small calibration pools (BDG2)"),
                      ("T_tuning", "Selected tuning parameters per run"),
                      ("T_cost_strategies", "Wall-clock time per calibration strategy")]:
        t = _tab(name, f"Table S{n}. {cap}.")
        if t:
            s.append(t)
            n += 1
    s.append("# S4. Statistical tests\n\n")
    s.append(_tab("T_tests", f"Table S{n}. All paired comparisons at nominal 90 % without perturbation (family "
                  "'preregistered-abs' = the planned primary comparison). p_holm: site-cluster (BDG2) or building "
                  "(UCI) sign-flip randomisation test, Holm-adjusted within family and metric; p_wilcoxon_holm: "
                  "building-level Wilcoxon signed-rank test (ignores clustering)."))
    n += 1
    s.append("# S5. Analysis plan (as committed on 2026-11-15)\n\n" +
             open(os.path.join(ROOT, "experiments", "PREREGISTRATION.md")).read().replace("# Pre-registered",
                                                                                          "Pre-registered") + "\n")
    md = os.path.join(ROOT, "supplementary", "Supplementary_Material.md")
    os.makedirs(os.path.dirname(md), exist_ok=True)
    open(md, "w").write("".join(s))
    out = md.replace(".md", ".docx")
    subprocess.run(["pandoc", md, "-o", out, "--reference-doc", os.path.join(HERE, "reference_style.docx")], check=True)
    print("built", out)


if __name__ == "__main__":
    build()
