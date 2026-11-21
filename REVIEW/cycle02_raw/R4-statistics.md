# R4 — Statistical review (cycle 2)

**Recommendation: Major revision**

## Summary
I recomputed the key numbers from `results/raw_results.csv.gz` and they reproduce exactly: under-covered shares of 18.7 % and 0.4 % (BDG2), first-week shares of 23.8 % and 13.7 %, a CD improvement for 90 % of buildings with rank-biserial r = 0.93, a site-mean p of 0.00195, and 713 unique BDG2 buildings across 1265 building×seed units. Against pooled CQR the reliability gain holds up. The site-cluster bootstrap CI of the window under-share difference is [−24.1, −10.0] pp, and only 1 unit is lost while 232 are gained. The remaining problems lie elsewhere: the inference does not cover the claims actually made, the sharpness claim depends only on medians, and the "sampling-noise" reference is not a valid floor.

## Issues

**1. Major — The headline outcome (under-covered share) and the method rankings have no inferential uncertainty, and the pre-registered CIs are not reported.**
Evidence: `paired_tests` (src/statistics/analysis.py:180–215) tests only CD, CD wk1 and IS. The share, which carries the abstract, highlights and Table 2 ("lowest in every condition"), gets only the seed s.d. PREREGISTRATION.md:41–42 promises 95 % site-cluster bootstrap CIs. They are computed (`ci95_mean_diff`) but appear in no table, and Supplementary S4 does not list this as a deviation. My recomputation: on UCI, HSC recency (0.0 %) vs QShrink-CQR (cov) (0.2 %) and vs HSC simple (cov) (0.2 %) each rest on **one** discordant unit out of 475 (bootstrap CI [−0.56, 0.00] pp). The Table 2 margins of 0.1–0.4 pp (BDG2→UCI, 15 % noise, calibration pool 10 %: 2.5 vs 2.8) come from 3 seeds.
Action: report paired share differences with site-cluster CIs (building-level for UCI) and McNemar-type tests for the headline comparisons. Rephrase "lowest" as "tied" wherever the CI includes 0. Add the CI columns to Table S4.

**2. Major — "Unchanged interval score" rests on medians and hides tail blow-ups of the proposed layer itself.**
Evidence: the text says IS is "statistically indistinguishable (Holm p = 1.000)". The raw p is 0.63, which is absence of evidence, not equivalence. The building-level median log-ratio is +0.17 % [0.01, 0.28] %, so median equivalence holds. Mean behaviour is different. The mean relative IS on BDG2 is 0.752 vs 0.726 for CQR (+3.7 %), and seed 4 alone is +11.3 % (0.856 vs 0.769). The worst-decile cost (ρ = 20) is +4.8 % on average and +17.5 % in seed 4 (`seed_level_metrics.csv`, `cost20_worst10`). Single cases: Rat_office_Colby (seed 1) widens ×23 (rel. width 0.30→6.85) while its coverage *falls* from 0.929 to 0.884. Robin_office_Wai (seed 4) goes from 2.64 to 28.8. This is the same "tail failure the medians hide" for which Section 4.4 rejects HSC-SSC-CQR.
Action: report mean IS, mean cost and worst-decile cost for every method in Tables 1 and 3. Diagnose the blow-ups (likely extreme own scores that dominate under recency weighting) and test a cap or winsorisation. Replace "indistinguishable" with a TOST equivalence test against the pre-registered 2 % margin.

**3. Major — The noise reference is method-dependent and biased, so it is not a floor.**
Evidence: `under_floor` uses each method's *own* day-block SE (analysis.py:55–60). As a result the paper cites 1.6 % (CQR) and 1.2 % (recency) as "the" floor (Sections 4.1 and 4.2), and weekly floors of 17.6 % and 18.7 %. The proposed method falls *below* its own reference over the window (0.4 % < 1.2 %) and in week 1 (13.7 % < 18.7 %), and ACI (cov) reaches 0.0 %. I compared the within-building variance of weekly coverage (weeks 2–8) with the variance implied by the day-block SE. The mean ratio is 1.37 for CQR on BDG2 (1.36 on UCI), which points to dependence across days that day blocks ignore (risk f only partly fixed). The ratio is 0.57–0.67 for ACI (cov), where feedback makes coverage anti-correlated. The weekly floor scales by √(56/7) instead of each building's valid days.
Action: build one method-independent reference by simulating an oracle-calibrated building with a multi-day (e.g. 7-day) moving-block bootstrap. Report the excess over that reference with CIs. Drop "the level expected from sampling noise" unless this reference supports it.

**4. Moderate — "The first week remains the hardest period" is a resolution artefact, and the week-1 sharpness cost is not reported.**
Evidence: `weekly_coverage.csv` and my recomputation for HSC recency on BDG2 give a weekly MACD of 0.035 in week 1 and 0.046–0.050 in weeks 2–8. The weekly under-share is 13.7 % in week 1 vs 18.7–20.8 % later. CQR is flat (23.8–25.1 %). The window-vs-week-1 contrast (0.4 % vs 13.7 %) therefore compares 1344-h and 168-h noise scales. Section 5.2 claims the shares reach "noise level from the second week on", but this is untested: BDG2 weeks 5–6 are 20.1–20.8 % vs 18.7 %, and UCI week 8 is 16.6 % vs 12.9 %. Week-1 IS is higher than CQR's (median paired log-ratio +1.0 % BDG2 and +1.3 % UCI, Wilcoxon p < 10⁻⁸), and the paper does not mention this.
Action: correct Limitation 2 and Section 5.2. Report week-1 IS. Show weekly excess over the reference with CIs.

**5. Moderate — The eligibility condition of the recommendation rule is judged on a point estimate.**
Evidence: the seed-level median-IS ratio of HSC recency to CQR on BDG2 is −0.3, +0.1, **+4.5**, −0.4 and +1.0 %. The mean is 0.98 %, but the t-interval upper bound is about 3.6 %, above the 2 % margin. The runner-up HSC-SSC-CQR (0.9 ± 0.9 %) is not separated from the winner (0.4 ± 0.3 %).
Action: report the bootstrap frequency with which the rule selects each strategy, and state that HSC recency, HSC-SSC-CQR and QShrink-CQR (cov) are statistically close.

**6. Minor — The Holm families are software artefacts.**
Evidence: each `paired_tests` call forms its own family per metric, giving 264 families of size 2–20 and 3141 tests. The deduplication only removes repeats inside a single list. FAMILY_CQR mixes absolute-score baselines into the HSC-CQR family. The site-level and Rat-excluded p-values are not adjusted. This is immaterial for the main CD results (p < 10⁻²⁵) but matters for borderline ones: UCI ACI-CQR (cov) CD wk1 p = 0.023, UCI HSC-SSC IS p = 0.047, and leave-site-out QShrink-CQR (cov) wk1 site-level p = 0.064.
Action: declare one confirmatory family (recency vs CQR, QShrink-CQR (cov), ACI-CQR, Self-CQR × 3 metrics × 2 datasets) and label the rest exploratory.

**7. Minor — Replication units are blurred.**
Evidence: the seed s.d. is presented as uncertainty, but seeds share buildings (406 of 713 BDG2 buildings appear in two or more seeds). The Section 4.7 Mann–Whitney tests use building×seed units, so the comparison group contains duplicates. The test also reports p = 0.005 for an effect in the unexpected direction (failures *less* volatile: 0.012 vs 0.113).
Action: label the seed s.d. as split variability, not a CI. Run the error-analysis tests on unique buildings and mark them exploratory.
