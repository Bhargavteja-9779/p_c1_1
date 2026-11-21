# R6: Robustness and generalisation review (cycle 2)

## Recommendation
**Major revision.**

## Summary
The window-level results hold up well. On unseen sites (every fold ≤1.2% under-covered), BDG2→UCI transfer, i.i.d. noise, MCAR gaps, small pools and a weak forecaster, the layer has the lowest share of buildings under-covered over the full window, and its interval score is close to CQR's. Three robustness claims go further than the files support, though. (i) At weekly resolution the reliability gain is modest, and deep weekly misses exceed the paper's own noise expectation. (ii) At nominal 80% the pre-registered rule would select ACI-CQR, not the layer. (iii) Table 2 reports only two-sided window coverage. That hides one-sided under-protection after an upward level shift and the first-week metric, where other methods win.

## Issues

**1. Major. Window coverage hides weekly under-coverage (risk a, present).**
*Evidence:* results/weekly_coverage.csv (BDG2, mean of 5 seeds). In weeks 2–8, 18.7–20.8% of buildings are under-covered with the layer, against 23.8–25.1% with CQR. The window-level contrast is 0.4% vs 18.7%. From raw_results.csv.gz (random protocol, α=0.1): 43.4% of BDG2 building×seed units have at least one week below 0.80 (CQR 51.3%), and 15.3% have a week below 0.75 (CQR 31.4%). Using each building's own day-block SE with the paper's weekly scaling (analysis.py:60) and assuming independent weeks, perfect calibration would give 29.5% and 6.7%. For UCI the observed values are 21.9% and 4.0%, against expected 12.3% and 1.4%. So "stays close to the level expected… from the second week on" (§4.3) holds only at the 0.85 threshold. Weekly misses deeper than that occur about 1.5–2.8× more often than noise would produce. Weekly mean coverage of the layer is also below 0.90 in all 8 BDG2 weeks (0.894–0.897).
*Action:* Report weekly and worst-week metrics in the main text, next to the 56-day figures: share of buildings with any week below 0.85/0.80/0.75, and mean number of under-covered weeks. Soften the Highlights and Abstract wording to match ("0.4%" is a window-level figure).
*Experiment:* none new; the analysis can be computed from the existing raw results.

**2. Major. The selection rule flips at nominal 80%, and "same ordering" understates this.**
*Evidence:* T_alpha0.2_*_raw.csv. Under-covered share: ACI-CQR (IS-tuned) 1.3% on BDG2 and 1.3% on UCI (mean 1.3), with rel. IS 0.462/0.301 against CQR's 0.463/0.304, so it is eligible. The layer has 3.2% and 0.2% (mean 1.7). Applied at α=0.2, the pre-registered rule (§3.6) therefore selects ACI-CQR. On UCI, ACI-CQR (cov) reaches 0.0% at +0.7% IS. §4.5 calls this "one exception" (BDG2 only). The Abstract says online level control matched reliability "only in a narrow parameter band", which this result contradicts.
*Action:* State in the text that the recommendation depends on the nominal level. Apply the rule at 80% and 95% and report the result. Qualify the ACI sentences in the Abstract and Conclusion.
*Experiment:* add the full-grid frontier (Fig. 5) at α=0.05 and α=0.2.

**3. Major. Table 2 reports only two-sided window coverage, so one-sided failures and first-week failures are missing.**
*Evidence:* T_robustness.md.
- (a) Shift +40%: the layer's under-protected share is 6.7%. That is 5× its clean value (1.3%) and about equal to clean pooled CQR (6.8%), although its window under-coverage is only 0.8%. Post-shift coverage is 0.912: two-sided coverage is inflated by lower-tail slack while the upper tail fails. The §4.6 claim that the layer "removed systematically under-protected buildings" does not hold under this stress.
- (b) First-week shares under stress: 21.7% (missing 40%), 18.6% (pool 10%) and 25.2% (UCI→BDG2). These are worse than the clean 13.7%. GHCP-CQR at pool 10% reaches 11.5% in week 1 at a lower IS (0.557 vs 0.560). Self-CP reaches 7.0–9.0% under missing data, at about +15% IS.
- (c) calpool50 is pre-specified (§3.2) but missing from Table 2. ACI-CQR (cov), HSC-SSC-CQR and GHCP are also left out.
*Action:* Add columns to Table 2 for week-1 under-coverage, under-protection and post-shift (weeks 5–8) coverage. Add the omitted conditions and methods. Revise "lowest in every condition" to name the metrics where the layer is beaten.

**4. Moderate. Stress-test differences are a handful of buildings, with no uncertainty reported.**
*Evidence:* BDG2 has about 253 target buildings per seed, and stress tests use 3 seeds. So 0.1% is about 1 unit out of ~759, and "0.8 vs 2.0%" (shift +40, layer vs QShrink (cov)) is about 6 vs 15 units. Table 2 gives no s.d., CI or paired test. Leave-site-out is a single run per fold, and the Rat fold alone has 25.0% week-1 under-coverage.
*Action:* Add seed s.d. or bootstrap CIs and paired Wilcoxon tests (layer vs QShrink (cov)) for every Table 2 row. Report per-fold leave-site-out results in the Supplement.

**5. Moderate. The noise floor is method-dependent and has not been validated (risk f, partly present).**
*Evidence:* metrics.py:60–67 builds the SE from the method's own realised daily coverage and assumes days are independent. The weekly floor rescales the window SE by √8 (analysis.py:60), which assumes the error process is stationary within the window, but the paper itself shows week 1 differs. The week-1 "floor" (~18.4%) is higher than the layer's observed 13.7%, and ACI-CQR (cov) runs at 9–13% in every week, below its floor. This shows the reference is not a floor.
*Action/Experiment:* Calibrate the reference empirically. Two options: an oracle that gives each building its own in-window 90% score quantile, or a moving-block bootstrap with week blocks. Then recompute the "within sampling noise" claims.

**6. Moderate. The stress scenarios are mild and stylised.**
*Evidence:* §3.2. Noise is i.i.d. Gaussian, missing data is MCAR at hourly level, and the level shift is a single step at a fixed day 28 for every building. BDG2→UCI does not discriminate between methods: CQR is only at 5.6%, and QShrink (cov) also reaches 0.0%.
*Action/Experiment:* Add three stress tests: (1) block outages of 1–3 days; (2) heavy-tailed or spike noise and slow drift; (3) shifts at a random day in 3–14 or shortly before day 1 (commissioning), plus a gradual ramp. Re-run with κ re-selected by LOBO. Report window, weekly and one-sided metrics.

**7. Minor. The robustness wording overstates the first-week claim.**
*Evidence:* The Conclusion says QShrink "does not repair the first week". QShrink (cov) cuts week-1 under-coverage from 23.8% to 17.2% (BDG2) and from 16.0% to 9.5% (UCI), so it is a partial repair. Highlight 4 ("unlike online level control") leaves out that ACI-CQR (cov) achieves 9.1%/5.3% in week 1, though at about double the IS.
*Action:* Rephrase as a comparison under the sharpness constraint.
