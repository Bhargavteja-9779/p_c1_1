# R4 Statistics — cycle 2

## Recommendation
Major revision. No new experiments are needed, only re-analysis of the stored results and corrected claims.

## Summary
The headline numbers reproduce from results/raw/raw_results_main.csv.gz. I recomputed: CQR 18.18 %, PCS-CQR 1.42 % (BDG2); 9.05 % and 0.42 % (UCI); PCS week 1 19.45 %; paired under-covered difference −15.82 pp; 87.4 % of 713 buildings better on CD; site sign-flip raw p = 2/1024, which Holm with 9 comparisons turns into 0.0176; booking failure raw p = 0.0078 (8/10 sites), which becomes 0.070 after Holm; independent-miss floors 0.0065 and 1.67 %.

Several cycle-1 issues are resolved: site clustering, the untested under-covered share, family definitions and disclosure of deviations. Cycle-1 issue #2 (the mean interval-score estimand is driven by outliers) is not resolved. Several claims in the abstract, highlights and contributions also conflict with the paper's own statistics.csv.

## Issues

**1. Major — Sharpness claims are reported selectively; fixed κ=168 is significantly sharper than the headline tuned PCS-CQR.**
Evidence: in the design family (statistics.csv), the IS difference "PCS-CQR − κ=168" is:
- UCI: +0.0031, p_holm < 0.001, median +0.00047, rank-biserial −0.84 (only 12.6 % of clients favour tuned PCS);
- UCI→BDG2: +0.0166, p_holm = 0.021;
- BDG2: raw p = 0.014, p_holm = 0.068.

The interval-score-tuned PCS and HSC-CQR also have significantly lower IS than PCS-CQR (BDG2 p_holm = 0.014 and 0.031; UCI 0.045 and 0.040). Yet:
- Contribution 3 (Final_Manuscript.md:38) says the reliability-aware rule works "without loss of sharpness";
- the abstract says κ=168 "did equally well";
- Section 5.3 cites only the under-covered test (p = 1.000).

So cycle-1 A1 is only partly resolved. The data favour the untuned κ=168: equal reliability, sharper intervals, no tuning.
Action: report CD, under-covered and IS tests together wherever a variant is called equal. Either make κ=168 the headline configuration or justify keeping the tuned one. Rephrase "without loss of sharpness" to state the small but significant IS cost (≈1.4 % against IS-tuned on BDG2).
Experiment: none.

**2. Major — The claim "no strategy of comparable width repairs week 1" (highlights, abstract, introduction, 5.5, 6.3) is contradicted, and week-wise metrics are never tested.**
Evidence: on BDG2, MLP-Gauss intervals are 1.16× as wide as PCS-CQR's (median relative width 0.455 vs 0.391), and its week-1 under-covered share is 9.9 % against 19.4 %. My site sign-flip test of the building-level week-1 indicator gives PCS-CQR +10.0 pp worse than MLP-Gauss, with 9 of 10 sites in that direction (raw p = 0.0078).

On UCI, coverage-only ACI is only 1.24× as wide (0.330 vs 0.266; IS +17 %), with 0 % under-covered overall and 4.6 % in week 1 against 10.3 %. The conclusion's phrase "much wider intervals" overstates this.

"Comparable width" is never defined. METRICS in analysis.py:199 has no week-wise metric, so no week-1 claim has been tested.
Action: define a width tolerance in advance, add week-1 CD and under-covered tests to the families, and restate the claim, for example as "no CQR-score calibration strategy within X % of CQR width". Mention MLP-Gauss explicitly and give the 2.4× / 1.24× contrast by dataset.
Experiment: re-analysis only.

**3. Major (cycle-1 #2 not resolved) — The mean-IS estimand rests on a handful of buildings, and its sign disagrees with the median.**
Evidence (BDG2):
- *PCS vs QShrink-CQR (MACD).* Mean difference −0.0085 (p = 0.041), reported in 5.2 as a PCS advantage. The median difference is −0.00016. Four buildings (three at Robin) contribute −2.1, −1.4, −1.1 and −0.6; without the 5 most extreme of 713 the mean is −0.0011.
- *ACI-CQR (MACD).* Mean −0.0029 (favours PCS), but the median is +0.0007 with a CI that excludes 0, and rank-biserial is −0.21 (favours ACI).
- *Self-CQR.* One building contributes −12.9.

A sum-based site sign-flip statistic inherits these outliers.
Action: make the median or Hodges–Lehmann difference (or log-IS) the primary IS estimand, with a matching test. Report how many buildings have IS > 5 × median. Drop the "slightly lower interval score" claim unless it survives this.
Experiment: none.

**4. Moderate — Equivalence and "nothing added" claims rest on non-significant tests, and some are contradicted.**
Evidence: the paper writes "statistically indistinguishable", "practically equivalent", "changes nothing" and "added nothing" without any equivalence margin. With 10 sites, one dissenting site already raises raw p to ≥ 0.0039, and Holm floors are 0.018–0.023.

The similarity prior in fact *improves* IS significantly: PCS − (+kNN) is +0.00088 on BDG2 (p_holm = 0.023) and +0.00015 on UCI (p < 0.001), and PCS − (+kNN+stage) on UCI is +0.0028 (p = 0.040). The abstract, highlights and 5.4 mention only its non-significant cost in reliability (+kNN under-covered difference p_holm = 0.75).
Action: run TOST with stated margins (for example 1 pp under-covered, 0.002 CD, 1 % IS) using the existing cluster bootstrap. Reword to "tiny, practically irrelevant IS gain; no reliability gain".
Experiment: re-analysis only.

**5. Moderate — The sampling floor assumes independent hourly misses.**
Evidence: Section 5.5 uses 1.7 % (Binomial(168, 0.9)) to call the week-1 failures "real". Hourly misses are strongly autocorrelated within days, so the effective sample size of a 168-h window may be closer to days than to hours, and the floor could approach the observed 19 %.

Section 5.1 prints "fewer than 0.00% of buildings" (values.py:187: a Monte Carlo count of zero formatted as 0.00 %). Section 4.4 says n_b ≈ 1300 where 5.1 says 1344.
Action: estimate the floors with a block or Markov bootstrap fitted to the observed miss autocorrelation, using stored hourly exceedances of a well-calibrated reference (for example weeks 5–8 under PCS). Print "<0.001 %" and harmonise n_b.
Experiment: re-analysis of the stored predictions.

**6. Minor — Multiplicity and reporting gaps.**
Evidence:
- statistics.csv holds 1660 tests. Reserve cost is tested (analysis.py:17, 199) but is not declared among the tested metrics in Section 4.4.
- No paired tests exist for the small-pool experiment (run() never calls paired_tests on pools). The text still states that "the fixed value is the safer choice" from 1.7 % vs 2.7 % at n_cal = 5 (s.d. 0.006 and 0.009).
- Table 3's caption and the text cite the 5- and 40-building pools, but the table shows only 10 and 20.
- "κ=∞ returns pooled CQR (18.5 %)" while CQR is 18.2 %: −shrink is the unstaged pool.

Action: declare all tested metrics and state the total number of tests. Add pool tests (runs as clusters). Complete Table 3. Fix the κ=∞ wording.
Experiment: none.
