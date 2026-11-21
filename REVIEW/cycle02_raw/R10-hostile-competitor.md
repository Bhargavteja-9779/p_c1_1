# R10: Hostile competitor review (cycle 2)

## Recommendation
**Major revision**

## Summary
I re-derived the component attributions from `results/frontier.csv`, `results/weekly_coverage.csv`, `results/raw_results.csv.gz`, `results/run_info.json` and `results/recommended.json`. The headline (18.7% to 0.4%) comes from score-level shrinkage with a coverage-tuned small pseudo-count. Several simpler configurations already in the frontier reach the same result. The first-week gain is credited to recency, but it comes from the small κ. The "proposed" method was picked by a rule that ranks on the target-set evaluation metric, by margins inside the paper's own noise reference. The method also has a tail failure of the kind the authors use to dismiss HSC-SSC-CQR.

## Issues

**1. Critical: the first-week gain comes from κ, not recency.**
Evidence: §4.4 credits recency with the week-1 change 19.4% to 13.7% (BDG2) and 8.2% to 5.9% (UCI). That comparison sets ρ=0.95 at the selected κ=48 h against ρ=1 at κ=96–168 h (`run_info.json`, `hsc_cqr_simple_cov` vs `hsc_cqr_recency`). At equal κ, `frontier.csv` (5-seed means) gives the following week-1 shares:
- BDG2, κ=48: 14.2% with ρ=1 vs 13.7% with ρ=0.95.
- UCI, κ=24: 6.1% vs 6.1%.

Week-1 own-score weights are all at least 0.74, so recency barely acts there. Its effect is on the window (2.3% vs 0.4% at κ=48 h), and it lets leave-one-building-out (LOBO) choose a small κ.
Action: correct §4.4, §5.1, the Highlights and the Conclusion. Report all components at matched κ.
Experiment: a ρ=1 variant with κ selected by a first-week-weighted or stage-dependent objective.

**2. Critical: the recommendation rule ranks candidates on the target metric.**
Evidence: Addendum A.1 (`experiments/PREREGISTRATION.md:103-110`) picks the method with the lowest *target* under-covered share among 13 eligible candidates. The rule was fixed after the BDG2 seed-0 pipeline check had been inspected. Margins in `recommended.json`:
- HSC-CQR recency: 0.20%
- HSC-SSC-CQR: 0.47%
- QShrink-CQR (cov): 0.86%
- HSC-CQR simple (cov): 1.05%

On BDG2 the gap is about 1 vs 4 building-units per seed (≈253 targets). The noise reference is 1.2%, so these values are not distinguishable. Picking the minimum of correlated candidates builds in winner's-curse optimism.
Action: present the method as one member of the shrinkage family and give the family-level result.
Experiment: nested selection. Choose the configuration on calibration-building LOBO, or on one dataset or held-out seeds, and confirm it on the other.

**3. Major: a quantile-level mixture works as well as a score-distribution mixture.**
Evidence: §5.1 says mixing distributions rather than quantiles is the key ingredient. At κ=λ=48 on BDG2 the two give nearly the same results:
- HSC, ρ=1: 2.3% over the window, 14.2% in week 1.
- QShrink: 2.0% over the window, 15.9% in week 1.

Against QShrink-CQR (cov), the layer improves the coverage deviation (CD) by only 0.0037. Its interval score (IS) is worse for 68% of buildings (`tables/MS2_tests.md`, r=−0.41, p<0.001). Against fixed-κ and simple (cov), IS is worse for 71–79% of buildings. The layer moves along a shared frontier; it does not dominate.
Action: drop the "distribution vs quantile" claim and the "at unchanged interval score" wording, except relative to pooled CQR.
Experiment: run recency-weighted QShrink and recency-weighted self-only calibration (κ=0) with pooled fallback.

**4. Major: ACI is tuned asymmetrically and the Highlight overclaims.**
Evidence: the coverage objective is degenerate for ACI. It selects the grid ceiling γ=0.01 in all 10 seed×dataset runs (`run_info.json`, `aci_cqr_gamma_cov`). The sharpness constraint is applied only afterwards, on target data, and this rules ACI out. If ACI were selected under the same constraint on calibration buildings, γ=0.002 would win. At γ=0.002, ACI gives 0.08% (BDG2) and 0.0% (UCI) over the window at unchanged IS, which is *better* than the layer. The Highlight "reduces first-week unreliability, unlike online level control" is contradicted by ACI-CQR (cov) at 9.1% and 5.3% in week 1.
Separately, `tune_aci` passes `base_w=0` (`src/training/pipeline.py:228`) while QShrink and HSC pass the band width. The selection is unaffected, but the logged objectives are not comparable (0.22 vs 0.60 at pooled).
Action: for every family, select by constrained LOBO (minimum MACD subject to IS ≤ 1.02 × pooled, on calibration buildings). Rewrite the Highlight.

**5. Major: the method has an unreported tail failure of its own.**
Evidence: in the BDG2 main runs, the layer gives 4 building×seed units with width more than 5× pooled CQR. The worst is Rat_office_Colby, seed 1: width 0.30 to 6.85 (23×), while coverage *falls* from 0.929 to 0.884. HSC simple (cov) has no such unit (maximum 4.5×). The +0.8% mean-cost increase at ρ_p=20 is entirely due to the top 5 units; without them it is −0.25%. The maximum building cost is 27.8 vs 15.8 for CQR. §4.4 calls exactly this pattern a disqualifying "tail failure" for HSC-SSC-CQR.
Action: report the tail (maximum and 99th percentile of width and cost ratios) for all methods. Diagnose the cause (scale collapse or own-score explosion) and add a safeguard.

**6. Major: the noise reference cannot separate the competitors.**
Evidence: the layer sits *below* its own noise reference, both over the window (0.4% vs 1.2%) and in week 1 (13.7% vs a weekly reference of ≈18.7%, §4.3). The 7-day day-block SE is unstable, and adaptive methods shrink the spread of per-building coverage, so Φ(−0.05/SE) is not a floor. From week 2 on, every shrinkage method is indistinguishable (18.3–18.7% weekly, `weekly_coverage.csv`).
Action: build the reference by parametric bootstrap from each method's own daily misses. Report intervals for the differences in under-covered share between the shrinkage variants.

**7. Moderate: the operational benefit is marginal and not unique to the method.**
Evidence: Table 3 shows an average cost of +1.8 ± 1.5% at ρ_p=10. The share of under-protected buildings is 1.3%, vs 1.5% for QShrink (cov) at lower cost. That share is a threshold count, not a monetised outcome.
Action: model a building-level contractual penalty (for example a threshold or convex penalty on exceedance frequency) under which "removing under-protected buildings" has a value. Otherwise, present the outcome as descriptive.

**8. Moderate: the information set favours recency.**
Evidence: Eq. (4) gives full weight to the scores of day D−1 (weight one at h′=h−1). Day-ahead offers usually close around midday on D−1, so the most recent day's hours are not all observed. Recency depends most on this last day.
Experiment: rerun with D−1 scores (and the scale) truncated at a realistic gate closure.

**9. Minor: the fixed ρ is not on the frontier's best point.**
Evidence: ρ=0.8 at κ=24 gives 0.08% over the window and 13.0% in week 1 (BDG2), and 6.1% in week 1 (UCI), better than the chosen configuration. State that the configuration was not tuned.
