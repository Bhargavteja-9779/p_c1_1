# R3 Experimental design review, cycle 2

## Recommendation
**Major revision.**

## Summary
The protocol keeps buildings and periods disjoint, and the LOBO tuning uses calibration buildings only (verified in `tune_hsc`, `tune_aci` and `tune_qshrink`, pipeline.py:195-249). Rule A.1 was committed before the full rerun (bf1f46f, 21:45 on 11-20; results in 8a6fd75 on 11-21), and `recommended.json` applies it exactly as written. The weakness is in what feeds the rule. The tuning protocol is "the same objective for every method", but in practice that objective puts ACI outside the rule's constraint and leaves the proposed layer inside it. Recency weighting is given only to the proposed layer. Several claims in the highlights and conclusion do not match the executed experiments.

## Issues

**1. Critical: the ACI tuning asymmetry decides the A.1 outcome.**
*Evidence.* In `tune_aci` the coverage objective is unconstrained MACD (pipeline.py:219-232). It selects γ = 0.01, the upper edge of the grid, in all 30 α = 0.1 runs (`run_info.json`, `aci_cqr_gamma_cov`). That variant is then excluded by the 2 % IS constraint (ratio 1.97 on BDG2). The target frontier (`frontier.csv`) shows ACI at γ = 0.002 with 0.1 % (BDG2) and 0.0 % (UCI) of buildings under-covered, and median rel. IS of 0.564 and 0.367, no worse than CQR. Its A.1 score would be about 0.05 %, below HSC-CQR recency at 0.20 %. HSC's MACD objective happens to land inside the constraint; ACI's runs to the grid edge.
*Action / experiment.* Run calibration-only reruns that apply the A.1 sharpness constraint inside LOBO for every method: minimise LOBO-MACD subject to LOBO-IS ≤ 1.02 × pooled LOBO-IS. Then re-apply A.1 and report the selected γ. The text says ACI's median IS "nearly doubles"; report ACI's week-1 IS alongside it. I computed +8.5 % on BDG2 (0.612 vs 0.564) and +2.2 % on UCI.

**2. Major: claims are stronger than the experiments.**
- Highlight 4 ("unlike online level control"): ACI-CQR (cov) has lower week-1 under-coverage than the layer, 9.1 % vs 13.7 % (BDG2) and 5.3 % vs 5.9 % (UCI) (Table 1).
- Conclusion, "quantile shrinkage … only at well-chosen parameters and do not repair the first week": QShrink-CQR (cov) was selected by LOBO, not on targets, and it lowers week-1 under-coverage from 23.8 % to 17.2 % (BDG2) and from 16.0 % to 9.5 % (UCI).
- Conclusion, "held … for a neural quantile model": HSC-CQR (MLP) is the IS-tuned variant without recency (pipeline.py:429-433). It gives 2.5 % / 2.1 % under-coverage and 20.3 % week-1 coverage failure vs 22.0 % for CQR (MLP). The recommended layer was never run on the MLP.
- §5.1, "mixing distributions rather than quantiles": the data say the opposite. Without recency, QShrink (cov) beats HSC simple (cov): 1.5 % vs 1.9 % over the window and 17.2 % vs 19.4 % in week 1 on BDG2.
*Action.* Correct these four statements, or run the recommended layer on the MLP quantiles (calibration-only).

**3. Major: recency is confounded with the shrinkage form.**
*Evidence.* Only HSC receives the ρ = 0.95 decay. The whole advantage over QShrink-CQR (cov) is in the recency step (HSC simple (cov) does not beat QShrink (cov); see issue 2). On BDG2 the paired comparison is 1 vs 15 discordant under-covered units (exact binomial p < 0.001).
*Experiment.* Add QShrink-CQR recency (decayed own counts and own quantile, λ by the same constrained LOBO) and Self-CQR recency. Both are calibration-only.

**4. Major: the window-level headline hides weekly under-coverage (risk a, present).**
*Evidence.* In `weekly_coverage.csv`, HSC-CQR recency leaves 18.7–20.8 % of buildings under-covered in weeks 2–8 on BDG2, rising over time, and 10.9–16.6 % on UCI. That is about one building in five every week. QShrink (cov) is indistinguishable in weeks 2–8 (18.3–21.7 %). ACI-CQR (cov) reaches 9.7–12.9 %, well below the stated "noise reference" of 18.7 %. So that reference is not a floor, and "within sampling noise" does not show that no miscalibration remains. The reference also treats days as independent (day-block SE), which ignores multi-day weather and occupancy spells (risk f).
*Action.* Report the weekly and 4-week rolling under-covered shares with a week-block reference, and describe the 0.4 % as a 56-day aggregate in the abstract and highlights.

**5. Moderate: the recommended configuration is selected and evaluated on the same target data.**
*Evidence.* A.1 picks the best of 15 candidates on the main target results, and those same numbers are the headline. The margin over HSC-SSC-CQR rests on a handful of units: 5 vs 12 of 1,265 BDG2 units, 3 vs 10 discordant (p = 0.09). I find the winner stable under building resampling (bootstrap, 98 %). A.1 was written after the v1 target results were known, and it already names the expected exclusion ("e.g. aggressive online level control").
*Action.* Label Table 1 as the selection set. Re-apply A.1 as a confirmatory test on the leave-site-out and cross-dataset runs, and report the selection uncertainty.

**6. Moderate: the day-ahead information set assumes all of day D-1 is observed (risk e, present).**
*Evidence.* Own scores from all 24 hours of D-1 enter at weight 1 (calibration.py:207-210), and the features use lag-1 days. Day-ahead offers close around midday on D-1. Recency weighting depends most on exactly these latest scores.
*Experiment.* Rerun with own scores through D-2 plus D-1 up to 12:00, and with features masked the same way.

**7. Moderate: target-year data are used in the quality filter (risk d, present).**
*Evidence.* datasets.py:12-13, 93-101 and 141-149 keep a building only if ≤ 5 % of its hours are missing, and its mean load is ≥ 1 kWh/h, in every period, including the target year. This removes the buildings with outages or commissioning problems during onboarding, which is the realistic cold-start case (Limitation 3).
*Experiment.* A sensitivity run that filters on training-period data only.

**8. Minor: reproducibility and reporting.**
*Evidence.* Logs for the 74-part revised run are missing; `experiment_logs/archive` covers only 2026-11-15. `REPRODUCIBILITY_STATUS.md` is dated 11-16 and still says "in progress". `run_info.json` has no code commit hash, and the tree was adopted from a parallel branch (dbaa850). The 50 % calibration-pool stress test was run and is described in §3.2, but it is missing from Table 2 (in the run: recency 0.5 %, ACI (cov) 0.0 %).
*Action.* Commit the run logs and a commit hash for each part, update the status file, and complete Table 2.
