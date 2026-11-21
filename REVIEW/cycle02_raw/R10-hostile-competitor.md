# R10 — Hostile competing researcher, cycle 2

## Recommendation
Major revision.

## Summary
The revision does fix the cycle-1 items A2–A4 and B5–B7. The PCS layer is now the headline, deviations are disclosed and week 1 is reported honestly. But the reported tables still support a more modest paper than the text describes. (i) At 80 % nominal, a simple existing method (ACI-CQR) beats PCS significantly, and the manuscript leaves this out. (ii) The "same reliability-aware rule" is coded differently for ACI. (iii) An existing method, quantile shrinkage (QShrink, Rafe & Das), is at least as good as PCS in nearly every condition. (iv) The tuning contribution and the operational payoff are not supported by the paper's own tests.

## Issues

**1. Critical — The ACI-vs-PCS ranking reverses at 80 % nominal and the paper hides it.**
Evidence: in T_alpha0.2_BDG2, ACI-CQR (MACD) leaves 0.9 % of buildings under-covered versus 6.3 % for PCS-CQR, at the same IS (0.460 vs 0.460) and width (0.321 vs 0.318). Even IS-tuned ACI-CQR reaches 1.4 %. In results/statistics.csv (BDG2, α=0.2, PCS-CQR vs ACI-CQR (MACD)), PCS is worse on CD (+0.0041, p_holm=0.023) and on the under-covered share (+5.5 pp, p_holm=0.031). On UCI at 80 %, ACI (MACD) leaves 1.1 % versus 3.2 %, and coverage-only ACI reaches 0 % with intervals only 3 % wider (0.220 vs 0.213). Section 5.6 reports only "6.3 % vs 16.6 % for CQR". The abstract, contribution 3 and the conclusion ("ACI matched the reliability only with much wider intervals") are therefore true only at 90/95 %.
Action: report the 80 % reversal in the abstract, Sections 5.2/5.6 and the conclusion, and qualify every "ACI needs wider intervals" claim. Discuss why it happens (e.g. at α=0.2 the ACI feedback signal is twice as dense).
Experiment: none; the results already exist.

**2. Major — The reliability-aware rule is not the same rule for ACI.**
Evidence: src/training/pipeline.py:255 passes `np.zeros_like(cal_scores)` as the base width to `normalized_IS` for ACI. PCS and QShrink pass `cal_base_w` (lines 237 and 273). The 2 % tolerance is therefore applied to a radius-only IS of about 0.21 for ACI but to the full IS of about 0.58 for PCS (run_info main_BDG2_s0: ACI γ=0 obj 0.218 vs PCS κ=∞ obj 0.584). That makes the rule about 2.7 times stricter for ACI. I added the base-width offset and re-ran the selection. The selected γ changes in 10 of 30 main runs (UCI α=0.1: seed 2 0.001→0.002, seed 3 0.0002→0.0005, seed 4 0.002→0.005; also several α=0.05/0.2 runs). The intermediate γ=0.002, with LOBO under-coverage of 0 % and IS +6 %, is never evaluated on targets. The "2.4× wider" figure compares PCS only with the grid edge γ=0.01.
Action: fix the objective, rerun ACI-CQR (MACD), and report the full γ frontier (target MACD and IS for every γ). Show a sensitivity analysis of the 2 % tolerance, which was chosen after target results had been seen.
Experiment: recalibration only; no retraining needed.

**3. Major — An existing method (QShrink) is at least as good as the recommended PCS.**
Evidence: in Table 3, QShrink-CQR (MACD) has an under-covered share at or below PCS-CQR in 15 of 17 conditions (lower in 13). Examples: LOSO 2.0 vs 2.4; UCI→BDG2 3.4 vs 4.2; site-balanced LOSO 1.3 vs 1.7 %. On BDG2 it also has fewer booking failures (1.4 vs 2.1 %) and a better week 1 (17.7 vs 19.4 %). Its fixed version QShrink λ=168 reaches 1.2 % versus 1.5 % for PCS κ=168. PCS's only edge is −0.0085 IS on BDG2 (p=0.041), which is not seen on UCI. Yet Fig. 1, the method section, Section 6.3 step 3 and the keyword framing all promote PCS.
Action: present "credibility shrinkage (PCS or QShrink)" as the finding, credit [21], and give the practical rule in its quantile form as well, or justify why PCS is preferred.

**4. Major — The tuning contribution is overstated; κ=168 was not "chosen without any data".**
Evidence: Section 5.3 says the fixed value was "chosen without any data". DEVIATIONS #5 says the κ=168 variant was added after interim target results had been seen ("Yes"), and Fig. 3 puts the target-MACD minimum at κ=168. The reliability-aware rule versus IS tuning: 1.4 vs 2.9 %, with p=0.164 on the under-covered share. In practice the rule picks {96, 168} where IS tuning picks 336, a one-step move on the grid (T_tuning). It brings no gain over the fixed value (p=1.000), and on UCI the fixed κ has a worse IS (p<0.001) and twice the under-covered share (0.8 vs 0.4 %). That contradicts the abstract's "did equally well".
Action: delete "chosen without any data", soften highlight 4, abstract sentence 7 and contribution 3, and state that IS-tuned PCS already removes most of the gap (18.2→2.9 %).

**5. Major — The operational metrics show no significant payoff.**
Evidence: booking failures PCS vs CQR: p_holm=0.070 (BDG2) and 0.060 (UCI). PCS vs Self-CQR: p=0.91 and 1.0, i.e. self-only calibration is operationally equal. Reserve cost is identical for all sharp methods (2.1 %; p=1.0 vs CQR). Like the IS, it is a proper pinball score and is flat by construction. Section 6.3 ("avoids … systematically under-protected capacity reservations") claims more than the data show. Booking-failure tests are missing from Table 2.
Action: add booking-failure columns to Table 2, rephrase Section 6.3 to match the tests, or add a contract model with asymmetric per-building penalties that actually discriminates between methods.

**6. Moderate — The week-1 claim "no strategy of comparable width" is untested against simple fixes.**
Evidence: MLP-Gauss halves week-1 under-coverage (9.9 vs 19.4 %) with intervals 16 % wider (0.455 vs 0.391; Table 1). No week-1 radius inflation (e.g. a LOBO-tuned multiplier for h≤7) was tried, although Section 6.3 recommends exactly that.
Experiment: PCS with a LOBO-tuned week-1 inflation factor, reporting week-1 under-coverage, IS and reserve cost.

**7. Minor — Text defects.**
Section 5.1 says "fewer than 0.00% of buildings" (a formatting bug: give the actual binomial value). Section 5.1 uses 1344 hours while Section 4.4 says "≈1300". Section 5.7 reports 6/713 under-covered (0.8 %), which differs from the 1.4 % in Table 1 because coverage is seed-averaged; say so.
