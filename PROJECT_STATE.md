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

## RESUME HERE (2026-11-21, great-ride session; supersedes "Exact next steps" below)
- 2026-11-21 (jolly-meitner session): great-ride tree adopted onto branch `claude/jolly-meitner-850g1y` (merge);
  work continues THERE. Third parallel line (SSC-CQR) archived: REVIEW/archive_ssc_line/README.md — its data fixes
  (no target-year filter, no imputation, DST mask; commit d763a3a) directly address cycle-2 R5 and can be ported.
- Branch `claude/great-ride-5vxp0a` now carries the funny-euler-sjuow2 line (tree adopted by merge commit dbaa850).
  Parallel PCS-CQR line and its 10-reviewer critique: REVIEW/archive_pcs_line/ (code in history at 90c477e).
- Review cycle 2 on this line: 10 reviewer agents run on REVIEW/packet_cycle02.md; raw reviews in REVIEW/cycle02_raw/
  (all 10 done, all Major revision; R5 adds: target-year filter removes 208/1050 incl. 4 sites; uniform calibration-year offset explains part of CQR failure (18.7->14.7 %); 6-h gap fill + imputed hours scored; UCI DST unmasked, 15-min shift; headline counts building-seed rows (15.4 % seed-averaged). Prompt pattern if rerun needed:
  read scratch common instructions = role + "known risk areas a-f" listed in REVIEW/archive_pcs_line/review_02.md).
- DONE (jolly-meitner session): REVIEW/review_02.md consolidated (20 themes, tiers, execution plan) + REVIEW_HISTORY entry.
- NEXT: execute review_02.md execution plan step 1 (code), then step 2 full rerun (retrain on relaxed set), 3, 4.
  Track sub-steps in the 'Cycle-2 fix checklist' below (add ticks as committed). Previous NEXT text kept for context: User approved the FULL plan:
  re-analysis + calibration-only recompute (symmetric ACI tuning/extended gamma grid, tolerance sensitivity,
  autocorrelation-aware floor, one-day-delayed own-score update) + causal quality-filter retraining run; reframe claims
  to supported time scales (56-day window vs weekly).
- Consensus issues so far: 56-day headline hides ~19-21 % weekly under-coverage (A); ACI coverage objective picks grid
  edge gamma=0.01 in all runs, ACI not tuned under same sharpness constraint, decides rule A.1 (A); recency gain is from
  kappa not rho (week-1 14.2 vs 13.7 % at equal kappa); rule ranks on target metric with tiny margins; noise reference
  method-dependent; mean IS +3.7 % (tail blow-ups, Rat_office_Colby 23x width); at 80 % nominal rule would pick ACI-CQR;
  Proposition 1 = corollary of Lee-Barber-Willett and its premises violated (sigma0 asymmetric, pipeline.py:404-410);
  recency ESS bound off by factor 24; Shahid 2026 already tunes n0 by leave-one-site-out (novelty claim); missing refs
  (Bersson & Hoff, Fisch, Vejling, Batra, conformal PID, DtACI, SAOCP); D-1 information set; target-year filter.
- Local note: stale PCS-line intermediates were moved to the session scratchpad (not needed); model caches for this
  line must be retrained before any recompute (see "How to resume" step 2).

## Cycle-2 fix checklist (review_02.md execution plan)
- [x] 1a data (BDG2 1,042 bldgs / 14 sites; UCI 316; tests/test_data_rules.py): port SSC-line rules (train-period eligibility, no interpolation, DST mask, no onboarding fallback), UCI timestamp, weather cap
- [ ] 1b sigma0 from training buildings (Prop. 1 premise); docstring/prereg attribution aligned
- [ ] 1c constrained LOBO for all families + extended grids (gamma<=0.05, kappa 6/12) + edge reporting
- [ ] 1d new variants: QShrink-CQR recency, Self-CQR recency (fallback), delayed own scores, radius safeguard, recommended layer on MLP, GHCP local step
- [ ] 1e analysis: block-bootstrap reference, weekly/worst-week, share CIs + McNemar, one confirmatory family, per-building unit, tails/TOST, nested selection
- [ ] 1f timing: whole online step, reps, threads; regenerate cost tables
- [ ] 2  full rerun (retrain -> calibration -> sensitivity -> frontier alpha 0.05/0.1/0.2 -> run_all)
- [ ] 3  re-analysis outputs checked
- [ ] 4  manuscript rewrite + rebuild + packet cycle 3 -> ASK USER before cycle 3

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
