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
    s.append("# S1. Full results (all methods; mean ± s.d. over seeds)\n\nIn these tables, *Rel. IS (median)* and "
             "*Rel. width (median)* are medians over buildings; mean values are in tables/*_raw.csv. Method names are the code "
             "names: HSC-CQR simple = SSC-CQR (primary); HSC-CQR fixed-κ = SSC-CQR (κ=168); HSC-CQR = SSC-CQR +stage+kNN; "
             "HSC = SSC +stage+kNN on the absolute score (pre-registered); HSC simple = SSC (abs).\n\n")
    n = 1
    for name, cap in [("T_main_BDG2", "BDG2, random-building protocol, nominal 90 %"),
                      ("T_main_UCI", "UCI, random-building protocol, nominal 90 %"),
                      ("T_alpha0.05_BDG2", "BDG2, nominal 95 % (methods based on α-specific quantile models omitted)"),
                      ("T_alpha0.05_UCI", "UCI, nominal 95 %"),
                      ("T_alpha0.2_BDG2", "BDG2, nominal 80 %"),
                      ("T_alpha0.2_UCI", "UCI, nominal 80 %"),
                      ("T_gen_leave-site-out", "BDG2 leave-site-out (5 site folds)"),
                      ("T_gen_BDG2toUCI_nw", "BDG2 → UCI transfer (no weather; 3 seeds)"),
                      ("T_gen_UCItoBDG2_nw", "UCI → BDG2 transfer (no weather; 3 seeds)"),
                      ("T_gen_BDG2toBDG2_nw", "BDG2 → BDG2 without weather features (reference; 3 seeds)")]:
        t = _tab(name, f"Table S{n}. {cap}.")
        if t:
            s.append(t)
            n += 1
    for name, cap in [("SI_abs_BDG2", "Absolute-score methods, BDG2"), ("SI_abs_UCI", "Absolute-score methods, UCI"),
                      ("T_windows_BDG2", "Per-window reliability, BDG2 (all window metrics incl. P10)"),
                      ("T_windows_UCI", "Per-window reliability, UCI"),
                      ("T_sites_BDG2", "Per-site MACD and under-covered share, BDG2"),
                      ("T_downstream_BDG2", "Downstream reservation case study, BDG2 (all penalty ratios)"),
                      ("T_downstream_UCI", "Downstream reservation case study, UCI")]:
        p = os.path.join(T, name + ".md")
        if os.path.exists(p):
            body = open(p).read()
            if body.startswith("**"):
                body = body.split("\n", 2)[2]
            s.append(f"**Table S{n}. {cap}.**\n\n{body}\n\n")
            n += 1
    s.append("# S2. Statistical tests\n\n")
    s.append(_tab("T_tests", f"Table S{n}. All paired tests at nominal 90 % (site sign-flip and building-level Wilcoxon; Holm within family × metric)."))
    n += 1
    s.append("# S3. Robustness (all methods)\n\n")
    s.append(_tab("T_robustness", f"Table S{n}. Robustness conditions on BDG2 (mean and s.d. over 3 seeds)."))
    n += 1
    s.append("# S4. Selected hyper-parameters (leave-one-building-out on calibration buildings)\n\n")
    info = json.load(open(os.path.join(ROOT, "results", "run_info.json")))
    rows = ["| Run | SSC-CQR κ | SSC-CQR (IS-tuned) κ | +stage+kNN (κ, K) | QShrink λ | Self-CQR-fb m | ACI-CQR γ | "
            "TQA-B β | GHCP n | inverted h |", "|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|"]
    for k, v in sorted(info.items()):
        if "a0.1" in k or k.startswith(("lso", "xds")):
            hq = v.get("hsc_cqr", {})
            rows.append(f"| {k} | {v.get('hsc_cqr_simple', {}).get('kappa')} | "
                        f"{v.get('hsc_cqr_simple_IS', {}).get('kappa')} | {hq.get('kappa')}, {hq.get('K') or 'all'} | "
                        f"{v.get('qshrink_lambda')} | {v.get('selffb_min_hours')} | {v.get('aci_cqr_gamma')} | "
                        f"{v.get('tqab_beta')} | {v.get('ghcp_n_sur')} | {v.get('inverted_hours', 0)} |")
    s.append(f"**Table S{n}. Parameters selected by leave-one-building-out per run (hours for κ, λ, m, n).**\n\n"
             + "\n".join(rows) + "\n\n")
    n += 1
    s.append("# S5. Pre-registration\n\n" + open(os.path.join(ROOT, "experiments", "PREREGISTRATION.md")).read()
             .replace("# Pre-registered", "Pre-registered") + "\n")
    md = os.path.join(ROOT, "supplementary", "Supplementary_Material.md")
    os.makedirs(os.path.dirname(md), exist_ok=True)
    open(md, "w").write("".join(s))
    out = md.replace(".md", ".docx")
    subprocess.run(["pandoc", md, "-o", out, "--reference-doc", os.path.join(HERE, "reference_style.docx")], check=True)
    print("built", out)


if __name__ == "__main__":
    build()
