"""Assemble the submission package in Target_Journal_Submission/ from generated files.

Upload set (Advances in Applied Energy, Editorial Manager): manuscript (DOCX + PDF), title page, highlights,
cover letter, supplementary material, and a code-and-data archive. Run after
`python run_all.py --mode full --skip-experiments` and the manuscript builders."""
import os
import re
import shutil
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "Target_Journal_Submission")
M = os.path.join(ROOT, "manuscript")
WITH_CODE = False  # code available on request (data availability statement)

UPLOAD = [(os.path.join(M, "Final_Manuscript.docx"), "01_Manuscript.docx"),
          (os.path.join(M, "Final_Manuscript.pdf"), "01_Manuscript.pdf"),
          (os.path.join(M, "title_page.docx"), "02_Title_page.docx"),
          (os.path.join(M, "highlights.docx"), "03_Highlights.docx"),
          (os.path.join(M, "cover_letter.docx"), "04_Cover_letter.docx"),
          (os.path.join(ROOT, "supplementary", "Supplementary_Material.docx"), "05_Supplementary_Material.docx")]

# code archive: everything needed to reproduce the study, nothing about how the manuscript was prepared
CODE_DIRS = ["src", "tests", "config", "experiments", "figures", "tables"]
CODE_FILES = ["run_all.py", "requirements.txt", "environment.yml", "README.md",
              "scripts/calibration_pass.sh", "scripts/timing_benchmark.py",
              "manuscript/build_docx.py", "manuscript/build_supplementary.py", "manuscript/build_extras.py",
              "manuscript/values.py", "manuscript/references.py", "manuscript/citation_order.json",
              "manuscript/reference_style.docx", "manuscript/print.css", "manuscript/supp_methods.md",
              "results/raw_results.csv.xz", "results/seed_level_metrics.csv", "results/stage_curves.csv",
              "results/statistics.csv", "results/statistics.json", "results/metrics.json", "results/run_info.json",
              "results/recommended.json", "results/selection.json", "results/extended_analysis.json",
              "results/frontier.csv", "results/sensitivity.csv", "results/weekly_coverage.csv",
              "results/timing.json", "results/error_analysis.json", "results/manuscript_values.json",
              "results/examples_BDG2.csv", "results/examples_UCI.csv"]
CODE_GLOBS_DIRS = ["manuscript/sections"]
SKIP = re.compile(r"(__pycache__|\.pyc$|\.ipynb_checkpoints)")
# wording that refers to how the work was produced rather than to the study itself
TRACE = re.compile(r"(?i)\b(review(er)?s?\b(?! of)|review cycle|claude|anthropic|chatgpt|llm agent|session \d|"
                   r"first submission|resubmission)")


def _members():
    for d in CODE_DIRS + CODE_GLOBS_DIRS:
        for r, _, fs in os.walk(os.path.join(ROOT, d)):
            for f in fs:
                p = os.path.join(r, f)
                if not SKIP.search(p):
                    yield p
    for f in CODE_FILES:
        p = os.path.join(ROOT, f)
        if os.path.exists(p):
            yield p
        else:
            print("missing:", f)


def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    for src, name in UPLOAD:
        shutil.copy2(src, os.path.join(OUT, name))
    if not WITH_CODE:  # code is available on request: no code archive in the upload set
        print(f"packaged {len(UPLOAD)} upload files into {OUT}")
        return
    zpath = os.path.join(OUT, "06_Code_and_data.zip")
    hits = []
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for p in _members():
            arc = os.path.join("code_and_data", os.path.relpath(p, ROOT))
            if p.endswith((".py", ".md", ".sh", ".yaml", ".yml", ".txt", ".json")) and os.path.getsize(p) < 5e6:
                t = open(p, errors="ignore").read()
                for m in TRACE.finditer(t):
                    line = t[:m.start()].count("\n") + 1
                    hits.append(f"{os.path.relpath(p, ROOT)}:{line}: {m.group(0)}")
            z.write(p, arc)
    n = len(zipfile.ZipFile(zpath).namelist())
    print(f"packaged {len(UPLOAD)} upload files + code archive ({n} files, "
          f"{os.path.getsize(zpath) / 1e6:.1f} MB) into {OUT}")
    print("trace scan hits:", len(hits))
    for h in hits:
        print("  ", h)


if __name__ == "__main__":
    main()
