# PROJECT_STATE — read this first when resuming (any new session / account)

Last updated: 2026-11-20 22:30 UTC (session 2). Branch: `claude/funny-euler-sjuow2` (all work is pushed here).

## How to resume in a NEW container (nothing outside git survives)
1. `pip install -r requirements.txt` (CPU torch: `pip install torch --index-url https://download.pytorch.org/whl/cpu`), `pytest -q tests` (14 tests must pass).
2. Retrain all model caches (deterministic; reproduces committed results exactly, verified 2026-11-20):
   `setsid nohup python3 -u -c "import sys;sys.path.insert(0,'.');from src import experiments as ex;ex.train_only('full')" > results/experiment_logs/train_only.log 2>&1 &`
   (~2–3 h on 4 cores; data download is automatic). **Run NOTHING else CPU-heavy while it trains** (OpenMP oversubscription slows it ~4x).
3. Calibration pass (after "=== all trainings cached ===" appears in the log): `bash scripts/calibration_pass.sh`
   (4 single-threaded workers; finished parts in results/parts are skipped). Then
   `python3 -c "import sys;sys.path.insert(0,'.');from src import experiments as ex;ex.sensitivity('full');ex.frontier('full')"`
   and `python run_all.py --mode full --skip-experiments` (statistics, tables, figures).
4. Continue at "Exact next steps" below.

## Decisions (final unless reviewers force a change)
- Target journal: **Advances in Applied Energy** (Elsevier). Only well-fitting journal with publisher-reported
  submission→acceptance ≤ 72 days (66 d current panel; older 86 d; unverified at article level). User constraints:
  ≤ 72 days to acceptance, high-IF Q1, no MDPI; avoid DESK REJECTION (novelty + fit are the main goal).
- Topic: per-building reliable day-ahead prediction intervals for newly metered buildings (onboarding into DR /
  flexibility / M&V platforms). Data: BDG2 (842 bldgs, 10 sites) + UCI (315 clients).
- Evidence on accepted AAE papers: literature/aae_fulltext_benchmark.md (structure: numbered gaps+contributions in
  Introduction, ~7–10.5k words, 1–3 main tables, 8–12 figures, "Practical implications" + "Limitations" subsections,
  decision/cost framing; comparison papers accepted when tied to a concrete decision).

## Review cycle 1 (done) → revision in progress
- REVIEW/review_01.md: Reviewer 1 (Major/near-reject) + author response table. Confirmed problems: no week-1 gain;
  IS-tuned κ worse than fixed κ; TQA-B used target batch (fixed); ACI grid cap (fixed); MACD floor understated.
- Pre-registered revision: experiments/PREREGISTRATION.md Addendum A + A.1 (written before results):
  new variants SSC-CQR, HSC-SSC-CQR, HSC-CQR recency, coverage-objective tuning for HSC/QShrink/ACI,
  operational outcomes (capacity headroom cost ρ∈{10,20,40}, under-protected share), day-block noise floor,
  site-level tests, weekly per-building coverage (days-to-reliable), reliability–sharpness frontier (ex.frontier).
  Recommendation rule (A.1): lowest under-covered share s.t. median rel. IS ≤ 1.02 × CQR on both datasets.
- Seed-0 pipeline check (not a result): ACI-CQR(cov) forces per-building coverage but doubles IS → frontier framing;
  HSC-CQR recency and HSC-SSC-CQR promising; SSC-CQR alone weak.
- SSC theory: construction = HCP of Lee, Barber & Willett (arXiv 2306.06342, Eq. 6, Theorem 1, finite-sample ≥1−α);
  Dunn et al. pooling-CDFs is only asymptotic. Draft text: manuscript/drafts/method_new_cycle1.md.

## Experiment status (2026-11-21 13:40 UTC)
- COMPLETE: all 74 calibration parts with the revised code, sensitivity, frontier, clean timing
  (scripts/timing_benchmark.py -> results/timing.json), statistics, tables, figures. Committed.
- Rule A.1 selected **HSC-CQR recency** (results/recommended.json).
- Manuscript v2 (AAE structure; ~7.7k words, 3 tables, 8 figures, 52 refs, abstract 237 words) built:
  manuscript/Final_Manuscript.{md,docx,pdf}; supplementary/Supplementary_Material.{md,docx} (Tables S1–S15).

## Exact next steps (updated)
- Review round 2 (novelty/prior art + desk-reject screen) next; then rounds 3–10 per list below.
- Rebuild after any change: `python run_all.py --mode full --skip-experiments && python manuscript/build_docx.py &&
  python manuscript/build_supplementary.py` (and `python manuscript/build_extras.py` for highlights/title page).

## Exact next steps (original list)
0. New container: install; extract the newest results/parts_snapshot tarball into results/; `ex.train_only('full')`
   ALONE; then `bash scripts/calibration_pass.sh` (+ optionally a 5th worker for kind=='xds').
1. Finish calibration pass → `ex.sensitivity('full'); ex.frontier('full')` → `python run_all.py --mode full --skip-experiments`
   (writes results/recommended.json by rule A.1, weekly_coverage.csv, MS2_* tables, Fig_frontier, Fig_weekly).
2. Apply A.1 rule; update manuscript_tables.py/figures.py/values.py for new methods, frontier figure, operational
   table, days-to-reliable figure; add new refs (Lee et al. already [24]).
3. Rewrite manuscript to AAE pattern (benchmark checklist), ~9k words, main tables ≤3, rest to supplementary;
   graphical abstract; highlights; cover letter. Integrate drafts/method_new_cycle1.md.
4. Review rounds 2–10 (one independent reviewer agent per round; each must first give a desk-reject verdict):
   R2 novelty/prior art, R3 statistics/fairness/leakage, R4 ML method + code-vs-paper, R5 data/generalisation/
   deployment, R6 computation, R7 writing + guideline compliance, R8 competing researcher, R9 associate editor
   desk screen, R10 final adversarial. Save REVIEW/review_XX.md with author response; fix; rerun if needed.
5. Final audits (consistency, reproducibility), DOCX/PDF, cover letter, /Target_Journal_Submission package
   (scripts/package_submission.py), REVIEW/final_audit.md, rejection-risk report, final decision.
