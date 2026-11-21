# R6 — Robustness and generalisation reviewer (cycle 2)

## Recommendation
Major revision.

## Summary
The revision resolves most of my cycle-1 points. Fixed κ=168 is now reported everywhere, LOSO is run as 10 sites × 3 seeds with a per-site table, the CQR family is run at 80/95 %, post-change weeks (w58) are reported, and the new stress tests are real. Against pooled CQR, TQA-B and GHCP, the core result holds in every condition. But the new tables show where the recommended layer is matched or beaten, and the text does not report it. (i) Within any sub-window of the onboarding period, PCS-CQR leaves 11–20 % of BDG2 buildings under-covered. (ii) ACI tuned by the same reliability rule beats PCS in weeks 5–8 and at the 80 % level, at the same width. (iii) The headline metric does not see over-coverage. (iv) The level-shift "robustness" comes mostly from the weeks before the shift.

## Issues

**1. Critical — The 1.4 % headline depends on 56-day aggregation; PCS is beaten late in the window.**
Evidence: T_weeks_BDG2, PCS-CQR under-covered share: week 1 19.4 %, week 2 19.8 %, weeks 3–4 15.3 %, weeks 5–8 11.0 %, against 1.4 % over the whole window. In weeks 5–8, ACI-CQR (MACD) reaches 7.1 % (UCI 3.2 % vs PCS 4.4 %) at the same width (T_main: rel. width 0.387 vs 0.391). Section 5.5 (packet l.275) says the PCS gain "grows with time" but does not mention that ACI (MACD) is better then. Abstract, highlights ("restores reliability") and conclusion report only the 56-day figure. In weeks 5–8 PCS has the most own data, and its old scores are never discarded, so the ranking could flip beyond day 56. Cycle 1 asked for a long-run test, and it was not run.
Action: Report rolling 4-week (or weekly) under-coverage next to the 56-day figure in the abstract and Table 1. Qualify "restores reliability".
Experiment: Follow BDG2/UCI targets for 180+ days. Compare PCS, PCS with forgetting (sliding or decayed own scores) and ACI-CQR (MACD), with monthly under-covered share.

**2. Major — At 80 % nominal, ACI beats PCS and QShrink is not equivalent.**
Evidence: T_alpha0.2_BDG2, under-covered share: PCS-CQR 6.3 %, ACI-CQR 1.4 %, ACI-CQR (MACD) 0.9 %, TQA-B 5.3 %, QShrink (MACD) 8.8 %, all at rel. IS 0.460–0.462. On UCI: PCS 3.2 %, ACI (MACD) 1.1 %, ACI 1.9 %. Section 5.6 (l.291) reports only PCS vs CQR (6.3 vs 16.6). This contradicts "practically equivalent" (QShrink) and "the only ones both reliable and as sharp as pooled CQR" (§5.2) outside 90 %.
Action: Report all strategies at 80/95 % in the text, with paired tests, and restrict the equivalence and superiority claims to 90 %.
Experiment: None beyond tests on existing results. Ideally add α=0.3 to check the trend.

**3. Major — Table 3 compares reliability-tuned PCS with an IS-tuned ACI column.**
Evidence: COND_METHODS (src/statistics/manuscript_tables.py:20) lists "ACI-CQR", which is the IS-tuned version, although the response (B2) claims tuning parity. T_robustness, ACI-CQR (MACD): noise15 5.5 %, shift−40 3.6 %, weak forecaster 7.2 %, disjoint period 4.9 %. Post-change, ACI (MACD) beats PCS: shift−40 w58 2.8 % vs 5.7 %, outage7d 9.1 % vs 10.8 %.
Action: Add ACI-CQR (MACD) and a w58 column to Table 3, and revise "shrinkage strategies are the most reliable" accordingly.

**4. Major — The under-covered share does not see over-coverage, so Table 3 misranks one condition.**
Evidence: noise15-history: PCS-CQR mean coverage 0.944 and MACD 0.046, vs Self-CQR 0.909 and 0.020. Relative widths are 0.572 vs 0.507. Table 3 nevertheless shows PCS best (0.3 % vs 1.6 %). The same blind spot lets T_pools list GHCP-CQR at n_cal=5 as most reliable (0.1 %), although its rel. IS is 411 (unbounded intervals).
Action: Add MACD and an over-covered share (cov > 1−α+0.05) to Table 3, and state that Self-CQR is best calibrated under history-only noise.

**5. Major — Level-shift robustness comes from the pre-shift weeks, and booking failures rise sharply.**
Evidence: For shift+40 at day 28, w58 under-coverage is 5.4 % (PCS), 4.7 % (Self-CQR) and 5.3 % (ACI-MACD), so there is no PCS advantage after the shift. Booking failures are 15.7 % for PCS vs 2.1 % unperturbed (Self 16.5 %, QShrink 14.0 %). Yet the text says shrinkage strategies are "the most reliable under … level shifts in either direction".
Action: Report post-change metrics and booking failures in Table 3, and correct the claim.
Experiment: PCS with recency weighting or change detection under the shift and volatility scenarios (the remedy proposed in Limitation 5).

**6. Moderate — Small-pool evidence is selectively reported.**
Evidence: Section 5.6 cites n_cal=5 numbers (2.7 %, 1.7 %, 16.6 %), but Table 3 has only the 10- and 20-building rows. The separate calpool10 run (10 % of the pool, T_robustness) gives tuned PCS-CQR 4.7 ± 4.2 %. In seed 2 it reaches 9.5 %, equal to Self-CQR, while κ=168 reaches 3.6 % (seed_level_metrics.csv). With 5 buildings, IS-tuned ACI-CQR is already at 3.2 % with equal IS (0.559 vs 0.556).
Action: Show both small-pool designs and the per-seed worst case, and make κ=168 the stated default below roughly 20 calibration buildings.

**7. Moderate — The week-1 claim has unacknowledged exceptions.**
Evidence: GHCP-CQR at n_cal=10 has 2.5 % week-1 under-coverage at rel. IS 0.596, only 7 % above PCS (T_pools, though it over-covers at 0.935). MLP-Gauss reaches 9.9 % in week 1 with intervals 16 % wider (T_main_BDG2).
Action: Define "comparable width" numerically and discuss these cases. They also point to a remedy: a first-week inflation toward a GHCP-like or prior upper quantile.

**8. Moderate — Cycle-1 robustness items still open.**
Evidence: Stress tests and the disjoint-period run are BDG2-only. Only target windows are perturbed (calibration buildings are clean). The "weak forecaster" is still LightGBM on 10 % of the training buildings (src/experiments.py:381–386). Contribution 3 still claims the layer works "on top of any interval forecaster", but it was never applied to the seasonal-naive or a pretrained forecaster.
Action: Narrow the claim.
Experiment: Run the stress subset (noise, outage, shift) on UCI. Apply PCS-CQR to Naive+SCP or a no-lag model, and to perturbed calibration pools.

**9. Minor — LOSO wording and weighting.**
Evidence: Section 5.6 says pooled CQR fails for "half or more" of the buildings at two sites, but Rat is at 49.7 % (T_loso_sites). The pooled 2.4 % is dominated by Rat (248/842 buildings, 29 %); the site-balanced figure is 1.7 %. QShrink (MACD) is at or below PCS at 9 of 10 sites.
Action: Correct the wording, report the site-balanced figure, and note QShrink's per-site edge.
