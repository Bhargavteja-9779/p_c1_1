"""Assemble /Target_Journal_Submission (Phase 40 manifest) from generated files. Run after
`python run_all.py --mode full --skip-experiments` and the manuscript builders."""
import glob
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "Target_Journal_Submission")


def cp(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.isdir(src):
        shutil.copytree(src, dst, dirs_exist_ok=True)
    elif os.path.exists(src):
        shutil.copy2(src, dst)
    else:
        print("missing:", src)


def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    j = os.path.join(ROOT, "journal_selection")
    cp(os.path.join(j, "selected_journal.md"), os.path.join(OUT, "journal_selection", "selected_journal.md"))
    cp(os.path.join(j, "journal_comparison.md"), os.path.join(OUT, "journal_selection", "journal_comparison.md"))
    cp(os.path.join(j, "journal_verification.md"), os.path.join(OUT, "journal_selection", "journal_verification.md"))
    m = os.path.join(ROOT, "manuscript")
    for f in ["Final_Manuscript.docx", "Final_Manuscript.pdf", "cover_letter.docx", "highlights.docx",
              "title_page.docx"]:
        cp(os.path.join(m, f), os.path.join(OUT, "manuscript", f))
    code = os.path.join(OUT, "code")
    for d in ["src", "experiments", "tests", "scripts", "config", "manuscript"]:
        cp(os.path.join(ROOT, d), os.path.join(code, d))
    for f in ["run_all.py", "requirements.txt", "environment.yml", "README.md"]:
        cp(os.path.join(ROOT, f), os.path.join(code, f))
    r = os.path.join(ROOT, "results")
    cp(os.path.join(r, "raw_results.csv"), os.path.join(OUT, "results", "raw_results.csv"))
    cp(os.path.join(r, "metrics.json"), os.path.join(OUT, "results", "metrics.json"))
    cp(os.path.join(r, "statistics.json"), os.path.join(OUT, "results", "statistics.json"))
    for f in ["statistics.csv", "seed_level_metrics.csv", "stage_curves.csv", "run_info.json", "error_analysis.json",
              "sensitivity.csv", "manuscript_values.json"]:
        cp(os.path.join(r, f), os.path.join(OUT, "results", f))
    cp(os.path.join(r, "experiment_logs", "archive"), os.path.join(OUT, "results", "experiment_logs"))
    cp(os.path.join(ROOT, "figures"), os.path.join(OUT, "figures"))
    cp(os.path.join(ROOT, "tables"), os.path.join(OUT, "tables"))
    cp(os.path.join(ROOT, "supplementary"), os.path.join(OUT, "supplementary"))
    for f in sorted(glob.glob(os.path.join(ROOT, "REVIEW", "review_*.md"))) + \
            [os.path.join(ROOT, "REVIEW", "final_audit.md"), os.path.join(ROOT, "REVIEW", "code_audit.md"),
             os.path.join(ROOT, "REVIEW", "pre_review_audit.md"), os.path.join(ROOT, "REVIEW_HISTORY.md"),
             os.path.join(ROOT, "REVIEW", "rejection_risk_report.md"),
             os.path.join(ROOT, "REVIEW", "comparison_with_journal_papers.md"),
             os.path.join(ROOT, "REVIEW", "claim_evidence_map.md")]:
        cp(f, os.path.join(OUT, "REVIEW", os.path.basename(f)))
    for f in ["PROJECT_STATE.md", "EXPERIMENT_LOG.md", "CHANGELOG.md", "REPRODUCIBILITY_STATUS.md"]:
        cp(os.path.join(ROOT, f), os.path.join(OUT, f))
    n = sum(len(fs) for _, _, fs in os.walk(OUT))
    print("packaged", n, "files into", OUT)


if __name__ == "__main__":
    main()
