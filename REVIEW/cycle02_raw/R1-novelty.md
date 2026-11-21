# R1 — Novelty and prior-art review (cycle 2)

**Recommendation: Major revision**

## Summary
Contribution 1, the per-building onboarding evaluation, looks new. I found no prior study that reports the distribution of per-building coverage by onboarding week for day-ahead building loads. The nearest is Hao, Yang & Ji, Appl Sci 2026;16:7984, which reports pooled coverage on unseen buildings (about 87%). The calibration layer itself (Eq. 4) adds little: it combines existing pieces, namely a credibility/pseudo-count mixture of a unit's empirical CDF with a pooled CDF, exponential recency weights (nexCP) and a tuned pseudo-count. Each piece, and the narrative "average calibration hides failing units", already exists. Proposition 1 is a direct corollary of Lee–Barber–Willett, and the implementation does not meet its premises. Several close works are missing, and two characterisations of prior art overstate the gap.

## Issues

**1. Major — The methodological novelty is overstated relative to close prior art.**
*Evidence:*
- Shahid, "When Average Calibration Fails: Site-Conditional Federated Conformal Risk Control", arXiv:2606.20115 (2026). It shrinks each site's empirical risk curve towards the pooled curve with a single pseudo-count n0. It shows that pooled calibration violates the target at 40% of sites while local calibration inflates sets 83×. It evaluates per site and reports a sensitivity analysis of n0 against per-site violations and set size (n0 = 19).
- Rafe & Das, arXiv:2605.05562 (2026): regularised Mondrian.
- Hong, N Am Actuar J 2023;27:675–88: credibility form.
- Zhang, Lu & Yang, arXiv:2410.02561: Bayesian prior in online CP.
- Fang & Lee, "Optimal Spatio-Temporal Decoupling for Bayesian Conformal Prediction", arXiv:2605.00432 (2026): a cold-start prior whose weight decays as 1/√(1+t).
- Barber et al., Ann Stat 2023: recency weights.

Gap 3 says transition parameters "have so far been fixed by hand or tuned for sharpness". That is doubtful given Shahid's coverage-oriented choice of n0.

*Action:* Present the layer as an adaptation and combination ("we adapt…"). Add a short delta table against [34–38] and Fang & Lee. Rewrite Gap 3. Put the onboarding evaluation and the frontier first as the main contribution.

**2. Major — Directly relevant prior work is omitted.**
*Evidence:* Fisch, Schuster, Jaakkola & Barzilay, "Few-shot conformal prediction with auxiliary tasks", ICML 2021, PMLR 139:3329–39, addresses a new unit with few labels by borrowing calibration from exchangeable auxiliary units. It is in `manuscript/references.py:19` and `literature/literature_matrix.md` (#26), but the manuscript does not cite it. Also missing:
- Zhang & Candès, "Posterior conformal prediction", arXiv:2409.19712: unit-type clustering of scores.
- Bhattacharyya, Ding & Barber, "Conformal prediction with macro-coverage guarantees", arXiv:2606.28598 (2026). Its unweighted average of group coverages matches the building-weighted F^pop.
- Bhattacharyya & Barber, "Group-weighted conformal prediction", arXiv:2401.17452.
- Global-CP pooled residuals across series, in "Conformal prediction algorithms for time series forecasting: methods and benchmarking", arXiv:2601.18509.
- Zaregarizi & Yavari, arXiv:2605.29733 (2026): cross-building transfer with calibrated intervals.

*Action:* Cite these in §1.2 and say how the layer differs from each, especially from Fisch et al.

**3. Major — Proposition 1 is not new, and the experiments do not satisfy its premises.**
*Evidence:*
- The proof is a single invocation of Theorem 1 of [32], applied per stage. It should be labelled a corollary.
- Premise "σ0 fixed": the code estimates σ0 from the calibration buildings and treats them asymmetrically. Calibration buildings use a leave-one-out `s0_loo`, while targets use `s0_all` (`src/training/pipeline.py:404–410`). The score is therefore not the same function of each building's data.
- Premise of exchangeability: calibration buildings come from the training period and targets from a later period, by design (period-disjoint protocol).
- Empirical check (`results/stage_curves.csv`, main, α = 0.1, 5 seeds): SSC-CQR's stage-wise mean coverage on BDG2 is below 0.90 at 71% of stages (minimum 0.883; stage 1 gives 0.887). Yet §4.4 says "despite its stage-wise guarantee".

*Action:* Rename it as a corollary credited to [32]. Estimate σ0 from training or validation buildings. Report SSC's stage-wise mean coverage against 1−α. State explicitly that the period shift voids the guarantee here.

**4. Moderate — The GHCP comparison and the "no valid adaptive method" framing.**
*Evidence:*
- GHCP [33] is built for a new group with initial observations and has finite-sample validity. The text says that the Prop. 1 property holds for "no shrinkage estimator with 0<κ<∞" and that no mechanism "was designed for a population of new units". Both statements read as broader than warranted.
- The GHCP-CQR baseline drops GHCP's local-predictor step, its adaptation mechanism, and fixes the surrogate size at about 1344 (`src/models/calibration.py:260–282`; Supplement S3). The own scores therefore get at most 1/(M+1) of the weight, which makes the baseline essentially pooled CQR. The two have similar CD in Table S5.
- The Supplement says that omitting the local-predictor step "most likely favours GHCP-CQR". This is unsupported.

*Action:* Implement a building-specific local step, such as an own-residual offset or scale from the first days, or delete the "favours" claim and label the baseline as HCP-style. Narrow the framing in §1.3 and §2.4.

**5. Moderate — An attribution that cannot be verified.**
*Evidence:* [37] (Jeon, Zenodo 10.5281/zenodo.24002627) is a software deposit. Only its DataCite metadata was checked (`literature/references_verified_new.json`, item 15). I could not find any paper that describes its method. Even so, the manuscript says it uses a "donor–local mixture with a fixed pseudo-count", and the fixed-κ baseline is labelled "as in [37]".

*Action:* Verify the method from the code and quote it, or remove the attribution and label HSC-CQR fixed-κ as an internal ablation.

**6. Minor — Inconsistent attribution of the stage-wise rule.**
*Evidence:* The `ssc_quantiles` docstring credits Dunn et al.'s "pooling CDFs" (`calibration.py:372–376`). The manuscript credits LBW's HCP and says Dunn et al. give only an asymptotic guarantee.

*Action:* Make the two consistent.

**7. Minor — The Dirichlet-process reading is stated too loosely.**
*Evidence:* The DP posterior-mean interpretation [36,41] holds only for ρ = 1 and without the +∞ atom. With recency weights the mixture is not a DP posterior.

*Action:* State the conditions under which the interpretation holds.

*Searches:* WebSearch, Nov 2026. arxiv.org and zenodo.org could not be fetched directly, so arXiv content is based on abstracts and search snippets. I could not find the full text of Shi et al. [21].
