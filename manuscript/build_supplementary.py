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


# Ordered supplementary tables: (key, file, caption). Table S1 is the deviations table (Section S1), S2 the features.
SUPP_TABLES = [
    ("main_full_BDG2", "MS_main_full_BDG2", "BDG2, random-building protocol, nominal 90 %, all methods"),
    ("main_full_UCI", "MS_main_full_UCI", "UCI, random-building protocol, nominal 90 %, all methods"),
    ("weeks", "MS_weeks", "Per-building reliability by onboarding week (CQR-score strategies)"),
    ("ablation", "MS_ablation", "Design elements, tuning rules and ablations"),
    ("a5_BDG2", "MS_alpha0.05_BDG2", "BDG2, nominal 95 %"), ("a5_UCI", "MS_alpha0.05_UCI", "UCI, nominal 95 %"),
    ("a20_BDG2", "MS_alpha0.2_BDG2", "BDG2, nominal 80 %"), ("a20_UCI", "MS_alpha0.2_UCI", "UCI, nominal 80 %"),
    ("lso", "T_gen_leave-site-out", "BDG2 leave-one-site-out (10 sites × 3 training seeds)"),
    ("lso_sites", "T_loso_sites", "Leave-one-site-out: under-covered share per held-out site"),
    ("lso_balanced", "T_loso_site_balanced", "Leave-one-site-out: site-balanced means"),
    ("b2u", "T_gen_BDG2toUCI_nw", "BDG2 → UCI transfer (no weather; 3 seeds)"),
    ("u2b", "T_gen_UCItoBDG2_nw", "UCI → BDG2 transfer (no weather; 3 seeds)"),
    ("b2b", "T_gen_BDG2toBDG2_nw", "BDG2 → BDG2 without weather features (reference; 3 seeds)"),
    ("robust", "T_robustness", "Stress tests, disjoint calibration period and weak forecaster on BDG2 (mean over 3 seeds)"),
    ("pools", "T_pools", "Small calibration pools (BDG2)"),
    ("tuning", "T_tuning", "Selected tuning parameters per run"),
    ("tuning_curves", "T_tuning_curves", "LOBO objectives of PCS-CQR on calibration buildings for every κ"),
    ("cost", "MS_cost", "Computational cost"),
    ("cost_strategies", "T_cost_strategies", "Wall-clock time per calibration strategy"),
    ("tests", "T_tests", "All paired comparisons (family 'preregistered-abs' = the planned primary comparison). "
     "p_holm: site-cluster (BDG2) or building (UCI) sign-flip randomisation test, Holm-adjusted within family, "
     "protocol, condition, nominal level and metric; p_wilcoxon_holm: building-level Wilcoxon signed-rank test "
     "(ignores clustering)"),
]
SUPP_FIGURES = [
    ("data", "Fig2_data", "Data overview: building counts, load scale and missing data."),
    ("cdf", "Fig4_coverage_cdf", "Empirical distribution of per-building coverage over the 56-day onboarding window "
     "(all target buildings of all seeds; dashed: nominal 0.90; dotted: 0.85)."),
    ("ablation", "Fig6_ablation", "Design elements and tuning rules of the pseudo-count layer."),
    ("robust", "Fig7_robustness", "Under-covered share under stress tests (BDG2, 3 seeds)."),
    ("gen", "Fig8_generalisation", "Leave-one-site-out and cross-dataset transfer."),
    ("errors", "Fig10_error_analysis", "Per-building coverage against forecast difficulty and usage class."),
    ("examples", "Fig11_examples", "Example onboarding trajectories of intervals for individual buildings."),
]


def numbers():
    """Supplementary table/figure numbers as manuscript tokens (supp_T_<key>, supp_F_<key>)."""
    out = {f"supp_T_{k}": f"S{i + 3}" for i, (k, _, _) in enumerate(SUPP_TABLES)}
    out.update({f"supp_F_{k}": f"S{i + 1}" for i, (k, _, _) in enumerate(SUPP_FIGURES)})
    return out


def build():
    s = ["---\ntitle: \"Supplementary material: Reliable day-ahead prediction intervals for newly metered buildings\"\n---\n"]
    s.append("# S1. Deviations from the analysis plan\n\n**Table S1.** " +
             open(os.path.join(ROOT, "experiments", "DEVIATIONS.md")).read().split("\n", 1)[1] + "\n\n")
    s.append("# S2. Methods and implementation details\n\n" +
             open(os.path.join(HERE, "supp_methods.md")).read() + "\n\n")
    s.append(_tab("MS_features", "Table S2. Forecaster features."))
    s.append("# S3. Full results, protocols, stress tests and tests\n\nMean ± s.d. over seeds; Rel. IS and Rel. width "
             "are medians over buildings (means are in tables/*_raw.csv).\n\n")
    for i, (k, name, cap) in enumerate(SUPP_TABLES):
        t = _tab(name, f"Table S{i + 3}. {cap}.")
        assert t, f"missing supplementary table {name}"
        s.append(t)
    s.append("# S4. Supplementary figures\n\n")
    for i, (k, name, cap) in enumerate(SUPP_FIGURES):
        f = os.path.join(ROOT, "figures", name + ".png")
        assert os.path.exists(f), f
        s.append(f"![**Fig. S{i + 1}.** {cap}]({f})\n\n")
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
