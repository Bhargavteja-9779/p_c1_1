# R2 — Methodology review, cycle 2

## Recommendation
**Major revision.**

## Summary
The revision fixes most cycle-1 methodology items, and I checked them in code. The κ=0 fallback is in `calibration.py:220-221`. ACI uses the split-conformal level with a finite fallback (`:248-252`), and γ=0 gives exactly CQR. TQA-B no longer uses target information (`:357-358`). Own scores are strictly past scores (`:204-223`). The Eq. (1) scale is causal (`features.py:58-63`). Eq. (3), QShrink and GHCP are implemented as Supplementary S2.1 states.

My own analysis of the released per-building results raises a new problem with the headline metric. The 56-day-window under-covered share flatters PCS in a way the per-week tables show but the text never reconciles. I also found an asymmetry in how the "same" tuning rule is applied to ACI, and several claims that are stronger than the tables support.

## Issues

**1. Critical — The 56-day-window metric hides sub-window miscalibration that is specific to PCS.**
*Evidence.* T_weeks_BDG2 gives the PCS-CQR under-covered share as 19.4% (week 1), 19.8% (week 2), 15.3% (weeks 3–4) and 11.0% (weeks 5–8). Over the full window it is only 1.4%. For CQR the full window and weeks 5–8 agree (18.2% vs 20.7%), so a shorter window by itself adds little noise.

From `results/raw/raw_results_main.csv.gz` (BDG2, α=0.1, building×seed), I computed the correlation between coverage in weeks 1–4 and weeks 5–8:

| Method | BDG2 | UCI |
|---|---|---|
| CQR | +0.58 | +0.76 |
| ACI-CQR (MACD) | −0.00 | +0.25 |
| PCS-CQR | −0.30 | −0.18 |
| PCS-CQR κ=168 | −0.30 | −0.20 |

Of the 139 PCS units under-covered in weeks 5–8, 69% were over-covered (>0.90) in weeks 1–4. Under PCS, early over-coverage and late under-coverage therefore cancel inside the evaluation window. That window is also the window over which PCS pools its own scores and over which the LOBO coverage-deviation objective is computed (`pipeline.py` `tune_hsc`; `calibration.py:261-268`).

In weeks 5–8, ACI-CQR (MACD) is more reliable than PCS-CQR at equal width:

| | ACI-CQR (MACD) | PCS-CQR |
|---|---|---|
| BDG2 weeks 5–8 under-covered | 7.1% | 11.0% |
| UCI weeks 5–8 under-covered | 3.2% | 4.4% |
| Median relative width (BDG2) | 0.387 | 0.391 |

This contradicts three statements in the paper:
- "keeps the share … small after the first week" (Section 6.3);
- the contrast that ACI is more reliable "only with much wider intervals" (abstract, conclusion);
- the implication of Section 5.5 that PCS's gain over time is unique.

*Action.*
- Make a sub-window metric (per week, or a rolling 14-day window) co-primary.
- Restate the headline as "over the 56-day window".
- Report the correlation between early and late coverage.
- Discuss the mechanism: own scores are non-stationary in h, and the quantile of cumulative own scores lags.
- Revise the abstract, Section 6.3 and the conclusion.

*Experiment.* No new runs are needed. Recompute Tables 1–3 and the paired tests for weeks 5–8 and for rolling 14-day windows, and select κ by LOBO on the sub-window coverage deviation.

**2. Moderate — The "same" reliability-aware rule is applied asymmetrically to ACI.**
*Evidence.* `tune_aci` calls `normalized_IS(q, …, np.zeros_like(cal_scores), …)` (`pipeline.py`, in `tune_aci`), which leaves out the base width qhi−qlo. PCS and QShrink pass `bwq_cal`. The objective shifts by a constant, so the IS-tuned choice is unaffected. The relative 2% band (`_select`, `IS_TOL`), however, is about twice as tight for ACI, because its objective is about 0.37 instead of about 0.73.

I recomputed the selection after adding the base width, estimated as the λ=∞ QShrink objective minus the γ=0 ACI objective, which use the same radius. The selected γ changes in 31 of 177 runs, including 3 of the 5 UCI main seeds (s2: γ 0.001→0.002, LOBO under-covered share 1.6%→0%; s4: 0.002→0.005). This mainly handicaps ACI-CQR (MACD).

*Action.* Pass `bwq_cal` in `tune_aci` and rerun ACI-CQR (MACD).

*Experiment.* Rerun the calibration stage only (forecasters are cached).

**3. Moderate — "2.4× wider" for coverage-only ACI is an artefact of the grid edge and the fallback.**
*Evidence.*
- Coverage-only ACI always selects γ=0.01, the top of the grid (Section 5.2).
- With daily batches the effective step is 24γ, so α changes by up to 0.24 per day.
- When α_h ≤ 1/(N+1), the radius becomes the largest calibration score (`calibration.py:251-252`), which inflates the median width.
- LOBO objectives in run_info (BDG2 s0, α=0.05) are non-monotone: γ=0.001 has under-covered share 0 at an objective of 0.385, while γ=0.002 has 0.598.

The paper therefore never shows ACI at a reliability matched to PCS.

*Action.* Report target-building curves of MACD, under-covered share and width against γ for ACI, analogous to Fig. 3. Compare at matched width or matched reliability rather than at a degenerate grid edge.

*Experiment.* No new training. Evaluate every γ in the grid on targets.

**4. Moderate — The sampling floor assumes independent misses.**
*Evidence.* The text uses three binomial floors: "fewer than 0.00% below 0.85", "1.7% of 168-hour windows" and MACD 0.0066 (Sections 4.4, 5.1 and 5.5). These are correct for independent hours (I verified 0.0065 and 1.67%). Hourly misses cluster within days, however, so these floors understate noise for the week-1 claims ("the first-week failures are real"). "0.00%" is also a formatting artefact.

*Action.* Estimate the floor with a day-block bootstrap or permutation of each building's own miss indicators, apply it to every window length, and print "<0.01%".

**5. Minor — The κ=∞ limit and the matching unit test are misdescribed.**
*Evidence.*
- PCS-CQR at κ=∞ uses a building-weighted prior pooled over all stages (`hsc_quantiles` with `stage_matched=False`). CQR is score-weighted and stage-matched (`pooled_quantile`, `:106-120`).
- Section 5.4 nevertheless says "κ=∞ returns pooled CQR". The tables differ: 18.5% vs 18.2% (BDG2) and 9.3% vs 9.1% (UCI).
- The Fig. 3 caption says "∞ = pooled calibration".
- `tests/test_core.py:92-102` checks equality only for synthetic, balanced, NaN-free data with `stage_matched=True`, not for the PCS configuration. Supplementary S2.3 overstates what the test shows.

*Action.* Correct the text. State that PCS against CQR also changes the weighting and drops stage matching, and that the clean shrinkage control is "PCS-CQR -shrink".

**6. Minor — Some claims are stronger than the tables support.**
*Evidence.*
- Abstract and Section 6.1, "fixed one-week pseudo-count did equally well": on UCI, κ=168 has a worse interval score (+0.0031, p<0.001, Table 2), an under-covered share of 0.8% vs 0.4%, and a week-1 share of 12.0% vs 10.3%.
- Contribution 3, the rule works "for PCS and quantile shrinkage alike, without loss of sharpness": QShrink-CQR (MACD) has a worse interval score than PCS on BDG2 (p=0.041).
- The 2% tolerance is justified by seed-to-seed interval-score variability. That variability compares different target sets. The LOBO objective is also an hour-pooled mean in units of s (`calibration.py:271-278`), whereas the reported interval score is a building median divided by mean load. In practice the rule reduces to minimising MACD, since every κ≥48 lies within 2% (T_tuning_curves).
- "1344 observed hours" (Section 5.1, limitation 7) is the maximum per building, not the observed number (n_b≈1300 in Section 4.4).

*Action.* Qualify each statement, justify the tolerance with a paired, building-level quantity, and harmonise n_b.
