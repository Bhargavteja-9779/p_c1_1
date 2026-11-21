# R9 — Associate Editor, Advances in Applied Energy (cycle 2)

**Desk decision: NOT desk-rejected; send to external review.** The paper is within scope (applied probabilistic load forecasting for DR and flexibility onboarding). Its format matches the AAE benchmark (literature/aae_fulltext_benchmark.md:98–123): abstract of 237 words, 6 keywords, five highlights of 68–80 characters, 8 figures and 3 tables in the main text, about 10.7k words in a 24-page PDF, CRediT, generative-AI and data statements, and a reproducible code path.

**Recommendation: Major revision.**

## Summary
The study is clearly framed and its claims are machine-traceable. The novelty against [34,35,37] is incremental: it adds recency weighting and a κ tuned for coverage on top of known credibility shrinkage. For AAE, the value rests on the evaluation framing and the operational evidence, so the headline claims must match the tables exactly. Four places do not. The abstract and highlights sell a window-level metric that hides weekly unreliability. "Unchanged interval score" holds only for medians. The noise-reference wording is inaccurate. One methods sentence contradicts the protocol history. The submission is also not administratively ready.

## Issues

**1. Critical — The headline "18.7% → 0.4%" hides weekly unreliability (risk a).**
*Evidence:* results/weekly_coverage.csv, BDG2. In weeks 2–8, HSC-CQR recency leaves 18.7, 18.8, 19.0, 20.1, 20.8, 19.5 and 19.6% of buildings under-covered. For CQR the figures are 23.8–25.1%. On UCI the layer is at 14.5% in week 4 and 16.6% in week 8, above the 12.9% noise line (Fig_weekly.png). About one building in five has an unreliable week under the proposed layer, against about one in four under pooled CQR. A reader of the abstract and highlights would infer about one in 250.
*Action:* In the abstract and highlights, state that "0.4%" is a 56-day-window metric. Report the weekly excess over the noise reference (about 0–2 points for the layer versus about 6 for CQR) as the like-for-like weekly result. Soften "calibrates intervals building by building".

**2. Major — "Unchanged interval score" holds for medians only.**
*Evidence:* results/manuscript_values.json gives a mean relative IS on BDG2 of 0.752 for the layer and 0.726 for CQR, i.e. +3.6%. That exceeds the 2% eligibility margin of rule A.1 if it were applied to means. Table 3 shows a cost change at ρ=10 of +1.8 ± 1.5%. The highlight says "at unchanged interval score", and the abstract says "within +0.9%".
*Action:* Report mean and median IS side by side in Table 1. Replace "unchanged" with the actual numbers. Show the tail with the existing cost20_worst10 metric for all methods, not only for HSC-SSC.

**3. Major — The noise reference is method-dependent and is misdescribed.**
*Evidence:* src/statistics/analysis.py:56–60 computes the reference from each method's own day-block SE. The result is 1.6% for CQR, 1.2% for the layer and 1.4% for ACI-CQR (manuscript_values.json). The text gives both 1.6% (§4.1) and 1.2% (§4.2). The layer's 0.4% is three times below its own reference, yet the abstract calls it "the level expected from sampling noise". In week 1 the layer's 13.7% is below the weekly reference of 18.7%, which contradicts Limitation 2 ("first week remains the hardest… 13.7% still under-covered"). The weekly SE is the window SE scaled by √8 (line 60), which assumes independent days (risk f). A share below the noise level points to coverage being steered by feedback from realised misses, as ACI does, rather than to calibration.
*Action:* Use one method-independent reference, for example the SE of CQR or a binomial-with-day-clustering simulation at nominal coverage. Allow for between-day autocorrelation (block bootstrap over weeks). Reword the abstract, §4.3 and Limitation 2 so they are consistent. Discuss the feedback-control interpretation.

**4. Major — Day-ahead information set and target-year filter (risks e, d).**
*Evidence (e):* §2.1 and features.py:77 use `lag1d` as the full day D−1, and the own scores of day D−1 enter the calibration for day D. Day-ahead gate closure is typically around noon on D−1, so hours 12–23 would not yet be observed.
*Evidence (d):* datasets.py:96–99 requires at most 5% missing data and a mean of at least 1 kWh/h in 2017, the target year. This drops buildings with poor data in their onboarding period, which is the commissioning-type behaviour §5.3 calls hard.
*Action and experiment:* Rerun the main BDG2 and UCI protocols (3 seeds) with the information cut-off at 12:00 on D−1, for features and own scores alike. Rerun the filter using only training-period data, with the 2017 missing-data rule applied only to window eligibility. Report how many buildings are added and how they perform.

**5. Major — Protocol-history statement is inaccurate.**
*Evidence:* §2.4 says ρ=0.95 "was fixed before any result was seen". Addendum A (Supplementary S7) was written after the v1 full results had been inspected, including the week-1 failure. §3.6 is accurate; §2.4 is not. The ACI-CQR (cov) selection of γ=0.01 is a grid-edge choice (risk b). The frontier shows γ=0.002 at 0.1% under-covered with no loss of sharpness, so the sharpness-constrained ACI is not the comparator that rule A.1 evaluated.
*Action:* Correct §2.4. Add an ACI-CQR variant whose γ is chosen on calibration buildings by coverage subject to the same 2% IS constraint, and include it in the rule table (results/recommended.json).

**6. Moderate — Novelty positioning relies on very recent grey literature.**
*Evidence:* The closest prior art is [33–35] (2026 arXiv preprints) and [37] (a Zenodo software record). [37] already implements a donor–local mixture for new units.
*Action:* State the delta over [37] in one sentence in the abstract or contributions (recency weighting plus κ selected for coverage, and the evaluation framework). Cite peer-reviewed versions where they exist.

**7. Minor — Figures, tables and notation.**
(i) The Table 3 caption cites "Eq. 9"; the cost equation is (7). (ii) ρ denotes both the decay factor and the penalty ratio (ρ_p in the text, ρ in Table 3). (iii) The two x-axis labels in Fig_frontier.png run into each other ("(%)Change"). Pooled CQR in panel c sits at about 23.3% while the text gives 23.8%; explain or reconcile. (iv) Fig. 1 writes ρ^{d_i−1} and "day h+1", whereas Eq. (4) uses ρ^{h−1−h'} and the stage-h forecast is for day t0+h. (v) Figure files are numbered differently from the manuscript (Fig4_coverage_cdf.png is Fig. 3, Fig10 is Fig. 7); rename them for the production upload. (vi) The highlight "1,157 buildings" counts UCI electricity clients as buildings; say "buildings and clients".

**8. Minor — Administrative readiness.**
Author names, affiliations, CRediT, acknowledgements and the repository URL are placeholders. The generative-AI statement carries an authors' to-do note. A public DOI-backed code and data archive (Zenodo) is expected at submission, not "upon acceptance".
