# R9 — Associate Editor, Advances in Applied Energy (cycle 2)

## Recommendation
**Major revision.** The revision deals with most cycle-1 items: the method is now centred on PCS, the deviations table is honest, week 1 is reported, inference is site-clustered and ACI is fixed. What remains is an editorial problem. Once the revised results are read plainly, the paper's energy-application payoff and its "tuning" contribution are both weaker than the abstract, highlights and cover letter suggest. This is the main desk-rejection risk for AAE.

## Summary
The paper compares conformal calibration strategies for per-building day-ahead load intervals during onboarding (BDG2, 842 buildings; UCI, 315 clients). Pooled CQR leaves 18.2%/9.1% of buildings under-covered. Pseudo-count shrinkage (PCS) brings this down to 1.4%/0.4% at an unchanged interval score. Quantile shrinkage and a fixed κ=168 do the same, and no method repairs week 1. The evaluation is extensive and fully regenerated from result files. I checked the numbers in the abstract and conclusion against Tables 1–3 and they agree. The problems are in interpretation and framing.

## Issues

**1. Major — The operational payoff is null on cost and not significant on failures.**
Evidence: Table 1 gives the same reserve cost for CQR and PCS-CQR (2.1 ± 0.1 % of mean load). Booking failures fall from 7.3% to 2.1%, but p = 0.070 after Holm (Table 2 text). The AAE benchmark (literature/aae_benchmark.md, conclusions 1 and 6) expects "quantified gains with an operational interpretation". The only energy metric added in answer to B4 shows no cost benefit. Meanwhile §6.3 and the cover letter call the layer the avoidance of "systematically under-protected capacity reservations".
Action: State the null reserve-cost result in the abstract or discussion. Explain it: pinball cost is an average over buildings, so it cannot reward the redistribution. Then either add a cost function that penalises per-building failures (for example a contractual performance-factor penalty per failing building) or soften the operational claims.

**2. Major — "Fixed one-week κ, chosen without any data" is post hoc.**
Evidence: §5.3 says "A fixed one-week pseudo-count, chosen without any data". Supplementary Table S1 #5 records that κ=168 was added on 2026-11-16 after interim target results had been seen ("Target results seen: Yes"). κ=168 is also exactly the target-set MACD minimum in Fig. 3 (Fig9_sensitivity.png). The abstract, highlight 4, contribution 3 and the conclusion all rest on this value.
Action: Remove "chosen without any data". Label κ=168 as selected after interim results. Report how sensitive the conclusion is to neighbouring fixed values (96, 336), which are 1.6% and 2.9% in Fig. 3b.

**3. Major — The reliability-aware rule never beats the constant, yet it is recommended.**
Evidence: in T_pools (S18), fixed κ=168 is better than tuned PCS-CQR at every pool size: 1.7/1.9/1.8/1.9% vs 2.7/3.0/2.6/2.4% at n=5/10/20/40. In S17, calpool10 gives 2.2% vs 4.7%. In the main protocol they tie (1.5 vs 1.4%, p = 1.000). Even so, §6.3 step 3 recommends the tuned rule "when the calibration pool is large", and contribution 3 presents the rule as a finding. No experiment shows a regime where tuning helps.
Action: Recommend the fixed value. Recast the rule as a diagnostic showing that interval-score tuning is flat, or show a regime where it wins. Revise contribution 3 and highlight 4 to match.

**4. Moderate — Novelty versus the AAE standard.**
Evidence: §2.2 and §3.4 concede that the mechanism [20–22,50] and per-unit metrics [17,20] are not new. Quantile shrinkage is equivalent (Table 2, p = 0.60). Issue 3 removes the tuning novelty. The remaining contribution is a careful benchmark plus negative findings, which is legitimate but unusual for AAE.
Action: Make the cover letter and introduction explicit that this is an evidence and benchmark paper. Lead with the practitioner decision rule and the null results on week 1 and on volatility.

**5. Moderate — The coverage-only ACI reference sits at the edge of the grid.**
Evidence: §5.2 says "always selected the largest step size in the grid (γ = 0.01)". The abstract's "2.4 × as wide" therefore depends on the grid. Cycle-1 B2 was answered by stating the issue, not by resolving it.
Action: Extend γ (for example to 0.02, 0.05 and 0.1) for this reference, or describe the width ratio as grid-conditional wherever it appears.

**6. Moderate — No main figure shows the paper's central quantity.**
Evidence: Fig. 4 (Fig3_stage_curves.png) plots *mean* coverage. In it the PCS and CQR curves are almost indistinguishable after week 1, which visually contradicts the message. The per-building coverage CDF (Fig4_coverage_cdf) was moved to the supplement.
Action: Replace panels a and b with the weekly under-covered share or P10 coverage, or move the coverage-CDF figure back into the main text in place of Fig. 3 (Fig9_sensitivity.png), whose panel b duplicates Table 1. Also label the κ ticks 48, 168 and 672 in Fig. 3 and show κ=0 there.

**7. Minor — Mismatches between tables and text.**
Evidence:
- §5.1 says "fewer than 0.00% of buildings" (values.py line 187 uses .2f formatting).
- Table 2's under-covered difference (−15.8 pp BDG2; −9.1 UCI) does not equal the Table 1 difference (16.8; 8.7). The two tables use different units (seed-averaged buildings vs seed means), and this is not explained.
- §5.3 cites "PCS-CQR (IS-tuned)" at 2.9%, a row that is in no main table.
- The abstract's "did equally well" ignores the worse UCI interval score of κ=168 (+0.0031, p < 0.001).
- Fig. 1 states n_b = 24h, while Eq. (3) gives n ≤ 24(h−1).
- §5.6 says shrinkage is "most reliable under level shifts" and also that Self-CQR is "as reliable or more after an early level shift".
- The calpool10/25/50 rows in S17 are not described anywhere.

Action: Correct each item. Write "< 0.01%". Define the unit for Table 2.

**8. Minor — Cover letter overclaims.**
Evidence: the letter says the layer "turns the forecasts of … pretrained models into intervals". §6.4(6) says that pretrained forecasters were not run.
Action: Remove the claim or mark it as untested.

**9. Minor — Submission completeness and AI declaration.**
Evidence: author names, affiliations, CRediT ("To be completed"), the repository URL and suggested reviewers are still placeholders. §4 says the AI assistant "executed the experiments and ran independent code and manuscript audits". Calling AI audits "independent" is misleading.
Action: Fill in all placeholders and deposit the code with a DOI (Zenodo) before submission. Say "automated" rather than "independent". Add an explicit statement of which human checks verified the AI-executed analyses.
