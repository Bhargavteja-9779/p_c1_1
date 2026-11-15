"""Reproduce every experiment, statistic, figure and table of the study.

    python run_all.py --mode quick   # pipeline check: 1 seed, 10 % training rows (~20-30 min on 4 CPU cores)
    python run_all.py --mode full    # complete study (several hours on 4 CPU cores)

Outputs: results/ (raw_results.csv, stage_curves.csv, run_info.json, statistics.json, metrics.json,
experiment_logs/), figures/, tables/. Re-running resumes: finished experiment parts are skipped.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src import experiments as ex  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["quick", "full"], default="quick")
    ap.add_argument("--skip-experiments", action="store_true", help="only rebuild statistics/figures/tables")
    a = ap.parse_args()
    if not a.skip_experiments:
        ex.execute(a.mode)
        ex.sensitivity(a.mode)
    ex.collect()
    from src.statistics import analysis
    analysis.run(a.mode)
    from src.visualization import figures
    figures.run(a.mode)


if __name__ == "__main__":
    main()
