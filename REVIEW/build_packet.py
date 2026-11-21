"""Assemble the review packet for one review cycle: built manuscript + generated tables + code map +
review history, so that reviewer agents can work from one file (and verify details in the repository)."""
import glob
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def build(cycle):
    parts = [f"# Review packet — cycle {cycle}\n",
             "Repository root: /home/user/p_c1_1 (read-only for reviewers).\n"]
    ms = os.path.join(ROOT, "manuscript", "Final_Manuscript.md")
    parts.append("\n## 1. Manuscript (as built; all numbers filled from results files)\n\n" + open(ms).read())
    parts.append("\n\n## 2. Supplementary tables (machine-generated)\n")
    for f in sorted(glob.glob(os.path.join(ROOT, "tables", "T_*.md"))):
        if f.endswith(("T_tests.md",)):
            continue
        parts.append(f"\n### {os.path.basename(f)}\n\n" + open(f).read())
    parts.append("\n\n## 3. Code map (verify claims here)\n\n" + CODE_MAP)
    hist = os.path.join(ROOT, "REVIEW_HISTORY.md")
    parts.append("\n\n## 4. Review history (issues already raised and how they were resolved)\n\n" + open(hist).read())
    out = os.path.join(ROOT, "REVIEW", f"packet_cycle{cycle:02d}.md")
    open(out, "w").write("".join(parts))
    print(out, os.path.getsize(out) // 1000, "kB")
    return out


CODE_MAP = """
- src/data/datasets.py — download, cleaning (stuck-meter runs >=24 h, interpolation <=6 h, filters), cubes.
- src/preprocessing/features.py — build(): history-masked, scale-normalised features (Eq. 1 scale);
  descriptor(): load-shape descriptor for the kNN prior.
- src/models/forecasters.py — LightGBM point/quantile, MLP Gaussian/quantile (early stopping on validation buildings).
- src/models/calibration.py — grid CDFs; pooled_quantile; neighbours (NaN-safe); prior_cdf; hsc_quantiles
  (Eq. hsc); aci_quantiles; normalized_IS (tuning objective); ghcp_quantiles; qshrink_quantiles; tqab_quantiles.
- src/training/pipeline.py — split() (building/period-disjoint), sample_training, train_models, onboard_dates,
  window_predictions, tune_hsc / tune_aci / tune_qshrink (LOBO on calibration buildings), run_calibration
  (all interval methods), common_mask/evaluate.
- src/experiments.py — experiment plan (E1-E8), prepared() caches, robustness perturbations, sensitivity.
- src/evaluation/metrics.py — per-building coverage, width, Winkler interval score, MACD.
- src/statistics/analysis.py — seed-level tables, paired Wilcoxon + Holm + rank-biserial + cluster bootstrap.
- src/statistics/manuscript_tables.py, error_analysis.py; manuscript/values.py (every number in the text);
  manuscript/build_docx.py; tests/test_core.py (11 tests); experiments/PREREGISTRATION.md; CHANGELOG.md.
- results/raw_results.csv (per building × seed × method), results/statistics.csv, results/run_info.json
  (tuned parameters + tuning tables), results/seed_level_metrics.csv, results/stage_curves.csv.
"""

if __name__ == "__main__":
    build(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
