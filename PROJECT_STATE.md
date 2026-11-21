# PROJECT_STATE

Last updated: 2026-11-20 (session 2)

## Decisions (final unless reviewers force a change; method re-centred on PCS-CQR in revision 1)
- Target journal: **Advances in Applied Energy** (Elsevier, gold OA). Evidence: journal_selection/*.md.
  Fallback: Energy and AI.
- Topic: reliable per-building prediction intervals for day-ahead load forecasts of newly metered
  (cold-start) buildings. Method: Hierarchical Shrinkage Conformal (HSC) calibration layer
  (stage-matched + similarity-localised population prior, shrunk toward the building's own scores
  with pseudo-count κ; κ,K by leave-one-building-out on calibration buildings).
- Data: BDG2 electricity (842 buildings, 10 sites after quality filter), UCI ElectricityLoadDiagrams
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
Revision 1 (after review cycle 1) IN PROGRESS (session 2, 2026-11-20/21):
- DONE: v2 code (PCS-CQR = recommended layer; reliability-aware LOBO 'MACDc'; ACI finite fallback; TQA-B fix;
  observed-hour scoring; UCI DST; LOSO 10x3; disjoint cal period; new stress tests; small pools; CQR family at
  80/95 %; site sign-flip tests; week + booking metrics), tests (15 pass), manuscript sections 01-05 + 09 rewritten,
  experiments/DEVIATIONS.md, supp_methods.md, references verified (literature/citation_audit_r1.md).
- RUNNING: scripts/v2_chain.sh (detached; log results/experiment_logs/v2_chain.log): waits for training
  (train_v2b.out), then scripts/calibration_pass.sh (4 workers), sensitivity + collect, latency benchmark.
  If the container restarted: data re-downloads automatically; rerun `python3 -c "from src import experiments as ex;
  ex.train_only('full')"` (cached models skipped), then `bash scripts/calibration_pass.sh`, then sensitivity/collect.
- NEXT: python3 -c "from src.statistics import analysis as a; a.run('full')"; figures; values.py; write
  06_results.md + 07_discussion.md (claims must match results; abstract/highlights/intro claims written from
  seed 0 are PROVISIONAL: verify ACI-width, QShrink(MACD) similarity, week-1, HSC vs Self-CP claims),
  build_docx, supplementary, REVIEW/response_01.md, packet cycle 2, review cycle 2.

## Automatic resume
Scheduled self-resume messages (user request): 2026-11-16 02:15, 03:45, 07:20 UTC (trigger ids in
session). On resume: read this file, check `ps aux | grep ex.execute`, restart stopped jobs
(`ex.execute('full', kinds=[...])` skips finished parts), continue with the next unfinished task.

## Planned recompute pass (after audit)
Add methods: "HSC simple"/"HSC-CQR simple" (K=all, no stage matching; recommended default) and
"CQR-MLP"/"HSC-CQR-MLP" (model-agnostic check on MLP quantiles); apply verified audit fixes; then
delete results/parts and rerun `ex.execute('full')` (models cached → calibration only), then
`ex.sensitivity('full')`, `python run_all.py --mode full --skip-experiments`.
