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
- **v4 STATUS (2026-11-22 12:00 UTC):** TTSC full rerun with cost columns running (results/ttsc; old copy in
  results/ttsc_prev, delete after rerun, do not commit). Manuscript v4 text DONE (title, highlights, abstract in
  values._abstract, intro gaps/contributions + positioning table (manuscript/tables_static), method §TTSC + Fig1,
  setup, results (MS5_main, MS5_robust, Fig_ttsc_weekly), discussion/conclusion, data statement 'code on request',
  cover letter, SI S23-S29). NEXT: when `=== ttsc all done ===` in results/experiment_logs/ttsc.log:
  `python src/statistics/ttsc_analysis.py` -> `python -c "...manuscript_tables.ms_ttsc()"` -> figures.fig_ttsc_weekly()
  (call figures._set_primary() first) -> check every claim in 06_results/07_discussion against tables (esp.
  'lowest in X of Y', 'every comparison significant', shift+40 sentence, 2-3 % IS) -> build_docx, build_supplementary,
  build_extras, build_cover_letter -> package (no code zip) -> trace scan -> commit/push -> report.
- **LATEST (2026-11-22 ~03:00 UTC, dazzling-ramanujan session, stopped for account change). USER REQUEST (v4):**
  make the paper much stronger/novel, compare with related + same-journal (AAE) papers, reframe around a real-world
  problem (onboarding buildings into weekly-settled flexibility/DR contracts), authors P N Bhargav Teja (1st) +
  [Second Author] placeholder, no funding, no competing interests, **code "available on request"** (drop the code zip
  from the upload set; data availability statement accordingly). Work fully automatically.
  **New method TTSC (two-timescale shrinkage conformal)** = recency shrinkage prior (kappa as HSC-CQR recency) + per-
  building ACI-type level feedback over a 7-day window (`cb.hsc_aci_quantiles`, window=7) + cap at pooled 99 % score
  quantile; gamma by constrained LOBO with WEEKLY-MACD objective (IS <= 1.02 x pooled). Code: src/experiments_ttsc.py
  (results/ttsc/<part>.csv, ~12 s/part, needs model caches in results/cache -> if missing, retrain first via
  ex.train_only('full') ~70 min), analysis src/statistics/ttsc_analysis.py (tables/TT_*.md, results/ttsc_summary.json).
  Pilot (seeds 0-1 BDG2, seed 0 UCI; method designed on these -> report seeds 2-4 as held-out): weeks 2-8 under-
  coverage 19-19 % -> 13-16 % (BDG2; oracle 17.3 %), any-week<0.80 43 % -> 18-34 %, UCI 12.8 -> 10.4 %, mean IS ~=,
  median IS +0-2.4 %; week-1 sometimes slightly worse. gamma often at grid edge (grid extended to 0.01).
  NEXT: (1) finish run: `OMP_NUM_THREADS=1 python -u src/experiments_ttsc.py main lso xds robust weak` (skips done
  parts) as harness background task; (2) `python src/statistics/ttsc_analysis.py`; (3) integrate: positioning table
  manuscript/tables_static/positioning.md (verify claims for zhang2024bayes, fang2026, shi2026, jeon2026 abstracts
  first), new title/abstract/highlights/intro gaps+contributions/method section for TTSC (+ algorithm box)/results
  (TT tables, weekly contract case: breach = week with upper exceedance > 10 %)/discussion/limitations; TTSC becomes the
  proposed method, HSC-CQR recency its slow component; (4) data/code statement "available on request"; remove
  06_Code_and_data.zip from scripts/package_submission.py UPLOAD; (5) rebuild all docs, trace scan, package, push,
  report to user honestly (no paper is "unrejectable").
- **2026-11-22 01:45 UTC: CHAIN DONE (23:00 UTC, no failures).** Complete calibration parts (258 files) saved as
  results/parts_snapshot/parts_c2_full.tgz.part* (restore: `cat ...part* | tar xzf - -C results`). Sensitivity + frontier
  done. DONE 02:00 UTC: timing benchmark (results/timing.json), run_all --skip-experiments (rule A.1 -> HSC-CQR recency).
  DONE 02:15 UTC: manuscript v3 (results/discussion/abstract/highlights/contribution 4/setup rewritten; new title
  'Reliable day-ahead load intervals for newly metered buildings: shrinkage conformal calibration evaluated building by
  building'; tables MS3_main, MS3_robust; SI Tables S16-S22; cover letter rewritten). DONE 02:20 UTC: submission package
  Target_Journal_Submission/ (6 upload files + 06_Code_and_data.zip; trace scan clean except the AI-use declaration);
  SUBMISSION_CHECKLIST.md lists the author placeholders. NEXT: user fills placeholders; optional review cycle 3 only if
  the user asks (CLAUDE.md: ask before the next cycle).
- **LATEST (2026-11-21 20:55 UTC, dazzling-ramanujan session): most advanced branch is now
  `claude/dazzling-ramanujan-j9ysli`** (fast-forwarded from sharp-cori). Deps installed, 17 tests pass, parts snapshot
  17:56 restored (222 parts), `scripts/run_c2_stage.sh` restarted 20:52 UTC as harness-tracked background task.
  DONE for package: src/statistics/cycle2.py renamed -> extended_analysis.py (output results/extended_analysis.json).
- **LATEST (2026-11-21 ~20:40 UTC, sharp-cori session, stopped for account change): most advanced branch is
  `claude/sharp-cori-11buu9`.** Training was stopped by the user at ~16/22 jobs (caches not in git -> retrain).
  In the NEW container: `pip install -r requirements.txt`; restore parts snapshot (step 1b below); then run
  `bash scripts/run_c2_stage.sh` AS A HARNESS-TRACKED BACKGROUND TASK (Bash run_in_background, timeout 2 h; rerun it if
  killed: it resumes training per job, skips finished calibration parts) and STAY ACTIVE in the turn (wait loops of
  <=10 min) -- the container is suspended when idle and detached jobs die. Then steps 4-5 below (timing, run_all,
  manuscript step 4), then the FINAL SUBMISSION PACKAGE the user asked for (see USER note below): clean upload set
  (manuscript docx/pdf, title page, highlights, cover letter (update text to new title/method), supplementary, code
  zip WITHOUT REVIEW/, state files or review notes; rename src/statistics/cycle2.py -> extended_analysis.py incl. imports
  and results/cycle2.json), scan for AI/process traces (only the AI-use declaration may mention AI), then tell the
  user in chat: journal, final title, honest acceptance rationale and risks.
- 2026-11-21 18:15 UTC (sharp-cori session): jolly-meitner tree merged into branch `claude/sharp-cori-11buu9`;
  WORK CONTINUES THERE. New container: deps installed, 17 tests pass, parts snapshot 17:56 restored (222 parts),
  stale old-code caches deleted, `train_only('full')` (log train_c2.log) and `scripts/chain_c2.sh` started 18:05 UTC.
  20:05 UTC: container was suspended while idle (processes killed at 18:29; files kept). Detached setsid jobs do NOT
  survive idle periods -> run `bash scripts/run_c2_stage.sh` as a harness-tracked background task (resumable).
  USER (18:20 UTC): finish everything -> final submission-ready package; authors: P N Bhargav Teja (1st, corresponding,
  all CRediT roles incl. Software) + [Second Author] placeholder (Supervision); no funding; no competing interests;
  accurate AI-use statement only (no other AI/process traces in submitted files: strip 'review cycle'/R# comments in
  code copy); give journal + title + acceptance rationale in chat. Front/back matter + title page + cover letter updated.
- **HANDOVER 2026-11-21 16:45 UTC (account change).** Cycle-2 code fixes 1a-1f DONE and committed; manuscript
  method/intro/refs partly revised (see 'Cycle-2 manuscript progress'). The full rerun was RUNNING in the old container
  (training 15/~22 done). Model caches/results parts are NOT in git, so in a NEW container do exactly:
  1. `pip install -r requirements.txt` (data downloads automatically; UCI needs archive.ics.uci.edu allowed — env "p_c1_1").
  1b. Calibration parts finished in the old container up to 17:56 UTC are saved: restore with
     `mkdir -p results && cat results/parts_snapshot/parts_c2_1756.tgz.part* | tar xzf - -C results` (the
     calibration pass then skips them; only the remaining robust parts are recomputed). Training (step 2) is still
     needed for sensitivity/frontier/timing.
  2. `setsid nohup python3 -u -c "import sys;sys.path.insert(0,'.');import warnings;warnings.filterwarnings('ignore');from src import experiments as ex;ex.train_only('full')" > results/experiment_logs/train_c2.log 2>&1 &`  (~1.5 h)
  3. `setsid nohup bash scripts/chain_c2.sh > /dev/null 2>&1 &`  (waits for training, then calibration pass ~2 h,
     then sensitivity+frontier ~1 h; progress in results/experiment_logs/chain_c2.log; ends with "CHAIN DONE").
     NEVER run other CPU-heavy work while it runs.
  4. After CHAIN DONE: `OMP_NUM_THREADS=1 python scripts/timing_benchmark.py` (alone), then
     `python run_all.py --mode full --skip-experiments` (writes tables incl. T2_*, results/selection.json, cycle2.json).
  5. Then manuscript step 4: rewrite 06_results, 07_discussion, conclusion, intro contribution 4, abstract
     (values._abstract), highlights (build_extras.py) from the new tables; Supplementary S5 (SSC stage-wise coverage);
     rebuild DOCX/PDF/SI; REVIEW_HISTORY cycle-2 statuses; packet cycle 3 (REVIEW/build_packet.py); commit+push;
     then ASK THE USER before review cycle 3.
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
- [x] 1b sigma0 from training buildings (Prop. 1 premise); docstring/prereg attribution aligned
- [x] 1c constrained LOBO for all families + extended grids (gamma<=0.05, kappa 6/12) + edge reporting
- [x] 1d new variants (GHCP: label as HCP-style in text, no code change; + 4 new stress tests outage/spikes/random-day shift/ramp; frontier at alpha 0.05/0.1/0.2): QShrink-CQR recency, Self-CQR recency (fallback), delayed own scores, radius safeguard, recommended layer on MLP, GHCP local step
- [x] 1e analysis (src/statistics/cycle2.py + oracle_reference in metrics.py; tested on old results): block-bootstrap reference, weekly/worst-week, share CIs + McNemar, one confirmatory family, per-building unit, tails/TOST, nested selection
- [x] 1f timing (script rewritten; RUN ALONE after calibration pass: OMP_NUM_THREADS=1 python scripts/timing_benchmark.py): whole online step, reps, threads; regenerate cost tables
- [ ] 2  full rerun: TRAINING STARTED 15:48 UTC; unattended chain scripts/chain_c2.sh (training->calibration->sensitivity+frontier; log results/experiment_logs/chain_c2.log; rerun it after a restart once training is redone) (log results/experiment_logs/train_c2.log; caches results/cache not in git;
       if container restarted: rerun train_only, it resumes per job). After '=== all trainings cached ===': `bash scripts/calibration_pass.sh`
       (no calibration while training!), then sensitivity+frontier, then run_all --skip-experiments. Full rerun (retrain -> calibration -> sensitivity -> frontier alpha 0.05/0.1/0.2 -> run_all)
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

### Cycle-2 manuscript progress (step 4, results-independent parts)
- DONE: 04_method (credibility attribution Bühlmann/Efron, Shahid LOO credit, [37] as software record, DP reading
  only rho=1, kappa->inf limit qualified, ESS bound 24/(1-rho), rho history corrected, constrained objective + grid,
  sigma0 from validation, Corollary 1 credited to LBW + premise violated, Bersson & Hoff, algorithm box, D-1 info set).
- DONE: 02_intro related work + gaps 2-3 + contributions 1-3 reframed (evaluation/frontier first; layer = adaptation).
  Contribution 4 (operational) + results/discussion/abstract/highlights: after results.
- DONE refs: 14 added (literature/citation_audit_c2.md).
- DONE: GHCP HCP-style label (supp_methods.md), Table 3 Eq. 7, rho_p in table.
- TODO later: Supplementary S5 = SSC-CQR stage-wise coverage (cited in 04_method);
  figure file renaming; "buildings and clients" in highlights; REPRODUCIBILITY_STATUS update; per-part commit hash.
