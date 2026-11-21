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
(Updated 2026-11-21, session 2.) Review cycle 1 DONE: raw `REVIEW/review_01_raw.json`, consolidated
`REVIEW/review_01.md` (20 themes, decisions, tiers A/B/C, execution plan). NOW: implement the cycle-1 execution plan
in order (step 1 code changes → step 2 full rerun → step 3 re-analysis → step 4 manuscript). Track sub-step progress
in the checklist below; tick items as they are committed.

### Cycle-1 fix checklist
- [ ] 1a cleaning fix (only gaps <=6 h interpolated, imputed-hour flag excluded from metrics) + unit test
- [ ] 1b target selection without target-year filter; per-site attrition table
- [ ] 1c UCI DST masking; duplicate-meter check
- [ ] 1d ACI/ACI-CQR clipped level; cap-hit counts
- [ ] 1e Self-CQR-fallback baseline (72/168/336 h by LOBO); Mondrian-CQR
- [ ] 1f reliability-aware LOBO objective; primary = HSC-CQR simple; fixed-κ reported; cold-start variant
- [ ] 1g TQA-B λ from calibration only, LOBO decay; GHCP weight tuned; QShrink fixed λ=168 + matched grid
- [ ] 1h weak forecaster (no lag/profile); new stress scenarios (block outage, early shift, history-only noise)
- [ ] 1i isolated timing benchmark
- [ ] 2  full rerun (sequential; data auto-download; retrain)
- [ ] 3  re-analysis (per-window, site-cluster tests, per-site, HL, CIs, deviations table, DR case study)
- [ ] 4  manuscript rewrite + rebuild + packet cycle 2; ask user before cycle 2

## Automatic resume
Scheduled self-resume messages (user request): 2026-11-16 02:15, 03:45, 07:20 UTC (trigger ids in
session). On resume: read this file, check `ps aux | grep ex.execute`, restart stopped jobs
(`ex.execute('full', kinds=[...])` skips finished parts), continue with the next unfinished task.

## Planned recompute pass (after audit)
Add methods: "HSC simple"/"HSC-CQR simple" (K=all, no stage matching; recommended default) and
"CQR-MLP"/"HSC-CQR-MLP" (model-agnostic check on MLP quantiles); apply verified audit fixes; then
delete results/parts and rerun `ex.execute('full')` (models cached → calibration only), then
`ex.sensitivity('full')`, `python run_all.py --mode full --skip-experiments`.
