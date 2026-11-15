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
- Session limit hit ~14:35 UTC; resumed 21:07 UTC. Full run resumed as two parallel processes
  (A: main/lso/robust/weak, B: xds); finished parts are skipped. Parts done at resume: main BDG2 s0-4,
  main UCI s0-1 (all alphas). Log: results/experiment_logs/run.log, full_stdout_{A,B}.log.
- Sensitivity (E7) + examples still to run after jobs: `python3 -c "...ex.sensitivity('full')"`.
- Background workflow "pre-review-audit" (prior-art sweep with verification, adversarially verified code
  audit, journal requirements) running; results to be consolidated in REVIEW/pre_review_audit.md.

## Manuscript status
- sections 01 front (tokens), 02 intro, 03 related, 04 method, 05 setup, 09 backmatter drafted.
- Results/discussion/conclusion to be written from full results (tokens via manuscript/values.py).

## Exact next step
1. Wait for full run; then `python run_all.py --mode full --skip-experiments`.
2. Write 06_results, 07_discussion, 08_conclusion; build DOCX (manuscript/build_docx.py).
3. Start review cycle 1 (10 reviewer agents) -> REVIEW/review_01.md.
