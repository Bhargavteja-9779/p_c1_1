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
- [x] 1a cleaning fix (only gaps <=6 h interpolated, imputed-hour flag excluded from metrics) + unit test
- [x] 1b target selection without target-year filter; per-site attrition table
- [x] 1c UCI DST masking (duplicate-meter check moved to step 3 analysis)
- [x] 1d ACI/ACI-CQR clipped level; cap-hit counts
- [x] 1e Self-CQR-fallback baseline (72/168/336 h by LOBO); Mondrian-CQR
- [x] 1f reliability-aware LOBO objective; primary = HSC-CQR simple; fixed-κ reported; cold-start variant
- [x] 1g TQA-B λ from calibration only, LOBO decay; GHCP weight tuned; QShrink fixed λ=168 + matched grid
- [x] 1h weak forecaster (no lag/profile); new stress scenarios (block outage, early shift, history-only noise)
- [x] 1i isolated timing benchmark script (scripts/benchmark_timing.py; RUN ALONE after training, before/after calibration pass)
- [ ] 2  full rerun: (a) `ex.train_only('full')` STARTED 2026-11-21 08:19 UTC (log results/experiment_logs/train_r1.log;
       models cached in results/cache, NOT in git -> lost if container restarts: just restart it, it resumes per job);
       (b) then calibration pass `bash scripts/calibration_pass.sh` (4 single-threaded workers) or `ex.execute('full')`;
       (c) `ex.sensitivity('full')`; (d) `python run_all.py --mode full --skip-experiments`.
       Network: environment "p_c1_1" (allows archive.ics.uci.edu for UCI; setup script installs requirements).
       Tuning rule FROZEN (2026-11-21 08:50): sharpest setting with <=5% under-covered LOBO pseudo-targets (cb.pick);
       ACI gamma grid up to 0.05. main_BDG2_s0 parts already computed with the final code (kept).
       Decisions taken: cold-start variant skipped (week-1 reported honestly); CQR-family alpha-sensitivity NOT run
       (claims limited to 90 %); all LOBO-tuned competitors use the MACD objective (IS tie-break); pre-registered
       HSC/HSC-CQR keep the IS objective.
- [ ] 3  re-analysis: CODE DONE in analysis.py (window_table, site_table, downstream_table, site sign-flip, median CIs, families); still to do: run it, duplicate-meter check, deviations table (manuscript), update manuscript_tables.py/values.py/figures.py for new method names
- [ ] 4  manuscript rewrite + rebuild + packet cycle 2; ask user before cycle 2
       DONE so far: 02_intro contributions 1-2, 03_related, 04_method (SSC naming), 05_setup (rules, methods, stats,
       sec:prereg + tables/MS_deviations.md, tables/MS_budget.md), references (+8, literature/citation_audit_r1.md),
       values.py tokens (windows, downstream, timing, psite), manuscript_tables.py rewritten (display names DISPLAY,
       new MS_windows/MS_sites/MS_downstream/MS_cost from T_timing, SI_abs_*).
       TODO after results: figures.py (method names -> SSC display, Fig1 redraw as one-parameter layer, Fig4 add
       fixed-κ, file numbering), 06_results + 07_discussion + conclusion + abstract (_abstract in values.py) +
       highlights (build_extras.py), contribution 3 in intro, length cut to ~6000 words (abs-score tables to SI),
       build_supplementary.py for new tables, REVIEW_HISTORY cycle-1 table.

## Automatic resume
Scheduled self-resume messages (user request): 2026-11-16 02:15, 03:45, 07:20 UTC (trigger ids in
session). On resume: read this file, check `ps aux | grep ex.execute`, restart stopped jobs
(`ex.execute('full', kinds=[...])` skips finished parts), continue with the next unfinished task.

## Planned recompute pass (after audit)
Add methods: "HSC simple"/"HSC-CQR simple" (K=all, no stage matching; recommended default) and
"CQR-MLP"/"HSC-CQR-MLP" (model-agnostic check on MLP quantiles); apply verified audit fixes; then
delete results/parts and rerun `ex.execute('full')` (models cached → calibration only), then
`ex.sensitivity('full')`, `python run_all.py --mode full --skip-experiments`.
