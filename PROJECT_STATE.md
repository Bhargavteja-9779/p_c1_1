# PROJECT_STATE

Last updated: 2026-11-15 ~13:15 UTC (session 1)

## Decisions (final unless reviewers force a change)
- Target journal: **Advances in Applied Energy** (Elsevier, gold OA). Evidence: journal_selection/*.md.
  Fallback: Energy and AI.
- Topic: reliable per-building prediction intervals for day-ahead load forecasts of newly metered
  (cold-start) buildings. Method: Hierarchical Shrinkage Conformal (HSC) calibration layer
  (stage-matched + similarity-localised population prior, shrunk toward the building's own scores
  with pseudo-count κ; κ,K by leave-one-building-out on calibration buildings).
- Data: BDG2 electricity (842 buildings, 12 sites after quality filter), UCI ElectricityLoadDiagrams
  (315 clients). Raw files in data/raw (gitignored; `src/data/datasets.py::download`).
- Pre-registration: experiments/PREREGISTRATION.md.

## Code status
- src/data, src/preprocessing, src/models (forecasters, calibration), src/training/pipeline.py,
  src/experiments.py (E1-E8, resumable), src/statistics/analysis.py, src/visualization/figures.py,
  tests/test_core.py (6 passing), run_all.py (--mode quick|full).

## Experiment status
- Smoke test exposed stuck-meter data artefact -> fixed (CHANGELOG).
- Quick mode run: in progress (verification only).
- Full mode: NOT STARTED.

## Exact next step
1. Finish quick run; check all job kinds; run analysis/figures in quick mode.
2. Launch `python run_all.py --mode full` in background (~3-4 h on 4 cores).
3. Meanwhile: literature matrix + verified references (literature/verify_refs.py), manuscript draft.
