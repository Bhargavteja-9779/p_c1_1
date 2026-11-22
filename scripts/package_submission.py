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
          (os.path.join(ROOT, "supplementary", "Supplementary_Material.docx"), "05_Supplementary_Material.docx"),
          (os.path.join(M, "graphical_abstract", "Graphical_abstract.png"), "06_Graphical_abstract.png"),
          (os.path.join(M, "graphical_abstract", "Graphical_abstract.pdf"), "06_Graphical_abstract.pdf")]
TITLE = ("Two-timescale conformal calibration for week-by-week reliable day-ahead load intervals of newly "
         "enrolled buildings")
AUTHOR = "P N Bhargav Teja"
# figure files in order of appearance in the manuscript (separate high-resolution files for production)
FIGS = ["Fig1_method", "Fig2_data", "Fig4_coverage_cdf", "Fig_ttsc_weekly", "Fig_frontier", "Fig6_ablation",
        "Fig10_error_analysis", "Fig11_examples"]

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


def _declaration(path):
    import docx
    d = docx.Document()
    d.add_heading("Declaration of interests", level=1)
    d.add_paragraph("Manuscript title: " + TITLE)
    d.add_paragraph("\u2612 The authors declare that they have no known competing financial interests or personal "
                    "relationships that could have appeared to influence the work reported in this paper.")
    d.add_paragraph("\u2610 The authors declare the following financial interests/personal relationships which may be "
                    "considered as potential competing interests: none.")
    d.add_paragraph("Funding: this research did not receive any specific grant from funding agencies in the public, "
                    "commercial, or not-for-profit sectors.")
    d.save(path)


def _clean_metadata():
    """Neutral document properties: author name and title only (no generator strings, no empty comment parts)."""
    import docx
    from pypdf import PdfReader, PdfWriter
    for f in sorted(os.listdir(OUT)):
        p = os.path.join(OUT, f)
        if f.endswith(".docx"):
            d = docx.Document(p)
            cp = d.core_properties
            cp.author, cp.last_modified_by, cp.comments, cp.keywords, cp.subject = AUTHOR, AUTHOR, "", "", ""
            cp.title = {"02": "Title page", "03": "Highlights", "04": "Cover letter",
                        "05": "Supplementary material", "07": "Declaration of interests"}.get(f[:2], TITLE)
            d.save(p)
        elif f.endswith(".pdf") and f.startswith("01"):
            r = PdfReader(p)
            w = PdfWriter(clone_from=r)
            w.metadata = {"/Title": TITLE, "/Author": AUTHOR}
            w.write(p)


def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    for src, name in UPLOAD:
        shutil.copy2(src, os.path.join(OUT, name))
    _declaration(os.path.join(OUT, "07_Declaration_of_interest.docx"))
    fd = os.path.join(OUT, "08_Figures")
    os.makedirs(fd)
    for i, f in enumerate(FIGS, 1):
        for ext in (".pdf", ".png"):
            shutil.copy2(os.path.join(ROOT, "figures", f + ext), os.path.join(fd, f"Fig{i}{ext}"))
    _clean_metadata()
    shutil.copy2(os.path.join(M, "upload_guide.txt"), os.path.join(OUT, "00_Upload_guide.txt"))
    if not WITH_CODE:  # code is available on request: no code archive in the upload set
        print(f"packaged {len(UPLOAD)} upload files + declaration + figures into {OUT}")
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
