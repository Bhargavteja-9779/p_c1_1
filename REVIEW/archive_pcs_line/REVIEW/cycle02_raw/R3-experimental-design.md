# R3 Experimental design, cycle 2: Major revision

## Recommendation
Major revision.

## Summary
The revision resolves most cycle-1 design issues. A2 is resolved: the headline method is now the one-parameter PCS. A3 is mostly resolved: there is a deviations table and an exploratory label. A4 is resolved: the week-1 failure is stated openly. The disjoint calibration period and the 10×3 LOSO design were executed, and κ is still tuned only on calibration buildings (run_info/T_tuning). Two problems remain. (i) The fairness fix for ACI (B2) appears in Table 1 but is dropped from every generalisation and small-pool table. In the small-pool runs that were dropped, reliability-tuned ACI matches or beats PCS at equal width. This contradicts the abstract and the conclusion. (ii) The 56-day headline metric hides the large shares of buildings that are under-covered within each sub-window. That contradicts the "restores reliability" highlight and Sec. 6.3.

## Issues

**1. Critical: Reliability-tuned ACI is computed everywhere but left out of Table 3 and T_pools, and where it was dropped it is as good as PCS.**
Evidence: `ACI-CQR (MACD)` is present in all raw files (main/lso/xds/robust/pools). Table 3 (`COND_METHODS`, src/statistics/manuscript_tables.py:20) and T_pools (`keep`, src/statistics/analysis.py:340) show only the IS-tuned `ACI-CQR`, although T_pools does include "PCS-CQR (IS-tuned)". I recomputed from raw_results_pools.csv.gz:
- n_cal=5: ACI-CQR (MACD) under-covers 0.6% (MACD 0.013, median rel-IS 0.562, width 0.400). PCS-CQR under-covers 2.7% (0.016, 0.555, 0.389) and κ=168 under-covers 1.7%.
- n_cal=10: ACI (MACD) 0.7% (MACD 0.014, width 0.390) vs PCS 3.0% (width 0.387).

The γ selected there is 0.002 (run_info `pools_*`: `aci_cqr_gamma_macdc`=0.002). In the main protocol the rule picked 0 or 0.001 (T_tuning). These results contradict three statements:
- Abstract and Conclusion: ACI "matched the reliability only with much wider intervals".
- Sec. 5.6: the fixed κ "is the safer choice for small pools".
- Response B2/B3, which claims that all tuned competitors are treated alike.

Action: Add ACI-CQR (MACD) to Table 3, T_pools and the paired tests. Revise the abstract, Sec. 5.2/5.6/6.1 and the conclusion. Give ACI a fixed-parameter variant, as PCS and QShrink have (e.g. γ=0.002).
Experiment: Re-run calibration only (cached forecasts) for ACI-CQR with fixed γ ∈ {0.002, 0.003} in main BDG2/UCI (5 seeds), LOSO and pools, with paired tests against PCS-CQR.

**2. Major: The 56-day per-building metric hides failures within sub-windows, so "restores reliability" overstates the result.**
Evidence: T_weeks_BDG2 shows PCS-CQR under-covering 19.8% of buildings in week 2, 15.3% in weeks 3–4 and 11.0% in weeks 5–8, against 1.4% over the whole window. From the raw files, 41.2% of BDG2 buildings (×seed) are under-covered in at least one post-week-1 sub-window, against 48.6% for CQR. On UCI the figures are 23.6% and 30.3%. In weeks 5–8, ACI-CQR (MACD) does better than PCS: 7.1% vs 11.0% on BDG2 and 3.2% vs 4.4% on UCI. The paper never mentions this. Highlight 3 and Final_Manuscript.md:375 ("keeps the share … small after the first week") conflict with these numbers. The only sampling floor given (1.7%) is for 168 h windows and assumes independent misses, so there is no reference for the 336/672 h sub-windows.
Action: Report a sampling floor for every window length that accounts for autocorrelation. Report the post-week-1 "any-window" share. Revise the highlight, Sec. 5.5, Sec. 6.3 and the conclusion.
Experiment: An oracle check with no retraining. For each target building, use the quantile of its own realised window scores, or a day-block bootstrap of its misses, to give the under-coverage share expected from noise alone.

**3. Major: Some selection choices are described as data-free although they were made after target results were seen.**
Evidence: Final_Manuscript.md:243 says κ=168 was "chosen without any data". DEVIATIONS #5 says the κ=168 variant was added after interim target results, and cycle-1 R3 noted that 168 matched the target optimum. The 2% tolerance (`IS_TOL = 0.02`, src/training/pipeline.py:207) was also set after the target results (deviation #9). The paper justifies it only by assertion and never tests its sensitivity. That tolerance decides which ACI γ is admissible (see Issue 1).
Action: Correct the wording. Report how the selected κ/λ/γ and the target results change with tolerance.
Experiment: Re-select from the stored LOBO tables (run_info `tune_*`) with IS_TOL ∈ {0.5, 1, 2, 5}% and recompute target metrics for PCS, QShrink and ACI.

**4. Moderate: ACI γ grid: "2.4× as wide" is a grid-boundary result, and the grid is coarse where reliability changes.**
Evidence: `aci_gamma_cov` = 0.01 (the upper edge) in every run (T_tuning). The grid steps from 0.002 to 0.005 to 0.01 (pipeline.py:30), and γ=0.002 already gives PCS-level reliability at equal width (Issue 1). The 2.4× figure in the abstract describes a single γ chosen at the edge of the grid, not "coverage-targeting ACI" in general.
Action: Use a finer γ grid, and show the target-side γ curve (MACD and width vs γ), as Fig. 3 does for κ.
Experiment: A calibration-only rerun over γ ∈ {0.001, 0.0015, 0.002, 0.003, 0.004, 0.005, 0.01, 0.02} in main BDG2/UCI.

**5. Minor: Inconsistencies between tables and text.**
- Table 3 reports "Runs = 3" for LOSO, but that protocol has 30 runs over 10 folds.
- Sec. 5.6 quotes n_cal=5 results that Table 3 does not contain.
- Two different "10 calibration buildings" experiments disagree: robust `calpool10` gives PCS-CQR 4.7% and CQR 22.9%, while pools n_cal=10 gives 3.0% and 19.3%. One should be dropped or the difference explained.
- "Fewer than 0.00% of buildings" (Final_Manuscript.md:158) is a formatting error.
- The abstract says κ=168 "did equally well". On UCI it under-covers 0.8% vs 0.4%, and its interval score is significantly worse (+0.0031, p<0.001, Table 2).
- "6 of 713" (seed-averaged) and "1.4%" (building×seed) use different units next to each other.

Action: Fix all of these. No experiment is needed.
