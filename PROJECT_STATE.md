# PROJECT_STATE

Last updated: 2026-11-21 (session 2)

## Decisions (final unless reviewers force a change; method re-centred on PCS-CQR in revision 1)
- Target journal: **Advances in Applied Energy** (Elsevier, gold OA). Evidence: journal_selection/*.md.
  Fallback: Energy and AI.
- Topic: reliable per-building prediction intervals for day-ahead load forecasts of newly metered
  (cold-start) buildings. Since revision 1: comparison/tuning study; recommended layer PCS-CQR (uniform pooled
  prior shrunk toward own CQR scores, pseudo-count κ by reliability-aware LOBO or fixed 168 h). The pre-registered
  HSC/HSC-CQR (stage-matched + similarity prior, IS-tuned) is a labelled comparator.
- Data: BDG2 electricity (842 buildings, 10 sites after quality filter), UCI ElectricityLoadDiagrams
  (315 clients). Raw files in data/raw (gitignored; `src/data/datasets.py::download`).
- Pre-registration: experiments/PREREGISTRATION.md.

## Code status
- src/data, src/preprocessing, src/models (forecasters, calibration), src/training/pipeline.py,
  src/experiments.py (E1-E8, resumable), src/statistics/analysis.py, src/visualization/figures.py,
  tests/test_core.py (6 passing), run_all.py (--mode quick|full).

## Experiment status
- Revision-1 full run complete 2026-11-21 03:06 UTC (61 jobs + sensitivity + examples + latency).
  Raw results archived as results/raw/raw_results_<exp>.csv.gz (split for the 100 MB limit; local working copy
  results/raw_results.csv is gitignored; analysis.read_raw() reads either).

## Manuscript status
- Revision 1 built 2026-11-21: all sections rewritten (06 results / 07 discussion new), ~8.4k words, 4 figures +
  3 tables in main text; supplement with fixed numbering (tokens supp_T_*/supp_F_* from build_supplementary.py);
  cover letter updated; REVIEW/response_01.md complete.

## Exact next step
- Review cycle 2: `python REVIEW/build_packet.py 2` -> 10 reviewer agents (same roles as cycle 1) ->
  REVIEW/review_02.md, REVIEW_HISTORY.md entry -> fixes -> rebuild.
- Rebuild chain after any change: analysis.run('full') (also manuscript tables + error analysis);
  figures.run('full'); manuscript/values.py compute; build_docx.py; build_supplementary.py; build_extras.py;
  build_cover_letter.py; claim_evidence.py.

## Automatic resume
Scheduled self-resume messages (user request): 2026-11-16 02:15, 03:45, 07:20 UTC (trigger ids in
session). On resume: read this file, check `ps aux | grep ex.execute`, restart stopped jobs
(`ex.execute('full', kinds=[...])` skips finished parts), continue with the next unfinished task.

## Planned recompute pass (after audit)
Add methods: "HSC simple"/"HSC-CQR simple" (K=all, no stage matching; recommended default) and
"CQR-MLP"/"HSC-CQR-MLP" (model-agnostic check on MLP quantiles); apply verified audit fixes; then
delete results/parts and rerun `ex.execute('full')` (models cached → calibration only), then
`ex.sensitivity('full')`, `python run_all.py --mode full --skip-experiments`.
