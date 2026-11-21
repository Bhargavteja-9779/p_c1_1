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
    resp = os.path.join(ROOT, "REVIEW", f"response_{cycle - 1:02d}.md")
    if os.path.exists(resp):
        parts.append(f"\n\n## 3b. Authors' response to review cycle {cycle - 1}\n\n" + open(resp).read())
    dev = os.path.join(ROOT, "experiments", "DEVIATIONS.md")
    if os.path.exists(dev):
        parts.append("\n\n## 3c. Deviations from the analysis plan\n\n" + open(dev).read())
    hist = os.path.join(ROOT, "REVIEW_HISTORY.md")
    parts.append("\n\n## 4. Review history (issues already raised and how they were resolved)\n\n" + open(hist).read())
    out = os.path.join(ROOT, "REVIEW", f"packet_cycle{cycle:02d}.md")
    open(out, "w").write("".join(parts))
    print(out, os.path.getsize(out) // 1000, "kB")
    return out


CODE_MAP = """
- src/data/datasets.py — download, cleaning (stuck-meter runs >=24 h, interpolation <=6 h for inputs only,
  obs mask of actually observed hours, UCI DST masking, filters, exclusion flow -> data/processed/*_exclusion.json).
- src/preprocessing/features.py — build(): history-masked, scale-normalised features (Eq. 1 scale);
  descriptor(): load-shape descriptor for the optional kNN prior.
- src/models/forecasters.py — LightGBM point/quantile, MLP Gaussian/quantile (early stopping on validation buildings).
- src/models/calibration.py — grid CDFs; pooled_quantile; neighbours; prior_cdf (incl. grouped LOBO);
  hsc_quantiles (Eq. pcs; kappa=0 fallback); aci_quantiles (conformal level, finite fallback); coverage_objective;
  normalized_IS; ghcp_quantiles; qshrink_quantiles; tqab_quantiles.
- src/training/pipeline.py — split() (random / loso / lso), train_models, onboard_dates, window_predictions
  (scores only observed hours), _select (IS / MACD / MACDc rules), tune_hsc / tune_aci / tune_qshrink,
  run_calibration (all interval methods, timings), common_mask/evaluate.
- src/experiments.py — experiment plan, prepared() caches (incl. disjoint calibration period), perturbations,
  small pools, sensitivity, examples.
- src/evaluation/metrics.py — per-building coverage (overall, per week), width, interval score, exceedance,
  reserve cost.
- src/statistics/analysis.py — seed-level tables, paired comparisons (site sign-flip randomisation tests,
  cluster bootstrap, Holm, Wilcoxon secondary), week/site/pool/tuning/cost tables.
- src/statistics/manuscript_tables.py, error_analysis.py, latency.py; manuscript/values.py (every number in the
  text); manuscript/build_docx.py; tests/test_core.py (15 tests); experiments/PREREGISTRATION.md,
  experiments/DEVIATIONS.md; CHANGELOG.md.
- results/raw_results.csv.gz (per building x seed x method), results/statistics.csv, results/run_info.json
  (tuned parameters + tuning tables + timings), results/seed_level_metrics.csv, results/stage_curves.csv.
"""

if __name__ == "__main__":
    build(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
