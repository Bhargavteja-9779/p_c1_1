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
             "*Rel. width (median)* are medians over buildings; mean values are in tables/*_raw.csv.\n\n")
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
    s.append("# S2. Statistical tests\n\n")
    s.append(_tab("T_tests", f"Table S{n}. All paired Wilcoxon signed-rank tests at nominal 90 % (Holm-adjusted)."))
    n += 1
    s.append("# S3. Robustness (all methods)\n\n")
    s.append(_tab("T_robustness", f"Table S{n}. Robustness conditions on BDG2 (mean over 3 seeds)."))
    n += 1
    s.append("# S4. Selected hyper-parameters (leave-one-building-out on calibration buildings)\n\n")
    info = json.load(open(os.path.join(ROOT, "results", "run_info.json")))
    rows = ["| Run | HSC (κ, K) | HSC-CQR (κ, K) | ACI γ | ACI-CQR γ |", "|:--|:--|:--|:--|:--|"]
    for k, v in sorted(info.items()):
        if "a0.1" in k or k.startswith(("lso", "xds")):
            hq = v.get("hsc_cqr", {})
            rows.append(f"| {k} | {v.get('hsc_kappa')}, {v.get('hsc_K') or 'all'} | {hq.get('kappa')}, "
                        f"{hq.get('K') or 'all'} | {v.get('aci_gamma')} | {v.get('aci_cqr_gamma')} |")
    s.append(f"**Table S{n}. Selected κ (hours), K and γ per run.**\n\n" + "\n".join(rows) + "\n\n")
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
