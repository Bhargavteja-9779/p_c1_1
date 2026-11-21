# PROJECT_STATE

Last updated: 2026-11-21 (session 2)

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
- FINAL calibration pass complete (2026-11-16 17:19-18:00 UTC): 74 parts (main 30, LSO 5, cross-dataset 9,
  robustness 30) + sensitivity + examples, all with the audited code. Analysis/tables/figures regenerated.

## Manuscript status
- v1 built 2026-11-16 ~18:20 UTC: manuscript/Final_Manuscript.{docx,pdf,md}, supplementary, highlights,
  title page, claim-evidence map (REVIEW/claim_evidence_map.md). Novelty re-scoped (comparison study +
  design evidence; no new-mechanism claim).

## Exact next step
(Updated 2026-11-21, session 2.) Review cycle 1 reviewers launched (workflow REVIEW/review_workflow.js,
args {cycle:1, packet:REVIEW/packet_cycle01.md}).
- If `REVIEW/review_01_raw.json` does NOT exist: rerun the cycle-1 workflow (results of an interrupted run are lost
  with the container).
- If it exists but `REVIEW/review_01.md` does not: consolidate (dedupe, rank by severity, decide action per issue)
  into REVIEW/review_01.md and add a cycle-1 table to REVIEW_HISTORY.md.
- Then implement fixes (text first; experiments only if required), rebuild (`python run_all.py --mode full
  --skip-experiments`, `python manuscript/build_docx.py`, supplementary/extras), regenerate packet for cycle 2
  (`python REVIEW/build_packet.py`), commit+push, and ask the user before running cycle 2.

## Automatic resume
Scheduled self-resume messages (user request): 2026-11-16 02:15, 03:45, 07:20 UTC (trigger ids in
session). On resume: read this file, check `ps aux | grep ex.execute`, restart stopped jobs
(`ex.execute('full', kinds=[...])` skips finished parts), continue with the next unfinished task.

## Planned recompute pass (after audit)
Add methods: "HSC simple"/"HSC-CQR simple" (K=all, no stage matching; recommended default) and
"CQR-MLP"/"HSC-CQR-MLP" (model-agnostic check on MLP quantiles); apply verified audit fixes; then
delete results/parts and rerun `ex.execute('full')` (models cached → calibration only), then
`ex.sensitivity('full')`, `python run_all.py --mode full --skip-experiments`.
