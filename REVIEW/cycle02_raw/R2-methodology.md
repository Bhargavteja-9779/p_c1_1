# R2 – Methodology review (cycle 2)

**Recommendation: Major revision**

## Summary
I checked Eqs. (1)–(7) and Proposition 1 against `calibration.py`, `pipeline.py` and `features.py`. Eqs. (1)–(3), (6) and (7), the LOBO coverage objective and its tie-break match the code. The recency-weighted mixture (Eq. 4) is implemented correctly, but the text describes its behaviour wrongly. Proposition 1 is not satisfied by the implementation or by the protocol. Two parts of the competitor tuning and the sampling-noise reference are not neutral between methods.

## Issues

**1. Major: the bound on the effective sample size and the minimum population weight are wrong by a factor of 24.**
Evidence: §2.4 (04_method.md:53) states n^ρ ≤ 1/(1−ρ) and a minimum population weight of κ/(κ+1/(1−ρ)+1). Each day adds up to 24 hourly counts (`calibration.py:210`), so n^ρ ≤ 24/(1−ρ) = 480. With the selected κ = 48 h (run_info.json), the population weight is ≈ 48/(48+451+1) = 9.6 % at h = 56, not the 70 % (48/69) implied by the text. The Dirichlet-process posterior-mean reading also holds only for ρ = 1 and without the "+1" term.
Action: correct the bound and the interpretation, and plot the population weight against h for the selected κ.

**2. Major: the conditions of Proposition 1 are violated by the code and by the protocol.**
Evidence:
- (i) σ0 is neither fixed nor symmetric across buildings. Calibration buildings use a leave-one-out σ0, while targets use σ0 from all M buildings (`pipeline.py:405–410`). The studentised scores are therefore not "the same measurable function" for every building, which breaks the first step of the proof.
- (ii) Calibration trajectories come from the training period and targets from the following year, so exchangeability fails by design. Empirically, SSC-CQR stage-wise coverage on BDG2 is below 0.90 at 71 % of stages (minimum 0.883; stage_curves.csv, main, α = 0.1).
- (iii) The source of the rule is described inconsistently. `calibration.py:373` and PREREGISTRATION H-B call it the Dunn et al. "pooling CDFs" construction. The manuscript says that rule is different and only asymptotically valid, and attributes the rule to HCP [32].

Action: compute σ0 on training or validation buildings that are disjoint from the calibration set. State that the proposition does not apply to the evaluated protocol, and remove "guarantees coverage … from the first day on" as a property of the deployed method. Report SSC-CQR coverage by stage, and align the code, pre-registration and text on one source.

**3. Major: competitors are tuned asymmetrically, and some choices sit at the edge of the grid.**
Evidence:
- ACI-CQR (cov) selects γ = 0.01, the upper end of the grid, in all 77 runs (run_info.json).
- The sharpness constraint of rule A.1 is applied to one tuned configuration per family, after tuning. ACI is therefore excluded as a whole, although Fig. 5 shows that γ = 0.002 reaches 0.1 % under-coverage over the window without loss of sharpness.
- TQA-B (β = 0.8) and GHCP (surrogate group size = median count) are not tuned. This contradicts "each tuned in the same way" (§1.3, contribution 3) and "every tuned parameter is selected by leave-one-building-out" (§3.3).
- The proposed method itself picks κ = 24, the smallest usable grid value (κ = 0 gives a radius of 500·s), in 10/15 UCI main runs and in every α = 0.05 run.

Action: tune every family by LOBO as "minimise MACD subject to LOBO IS ≤ 1.02 × pooled", then re-apply rule A.1. Add κ ∈ {6, 12}. Either tune TQA-B's β or state plainly that it is fixed.

**4. Moderate: the sampling-noise reference depends on the method and is reported inconsistently.**
Evidence:
- `analysis.py:57–60` uses each method's own day-block SE. That SE includes the method's day-to-day miscalibration, and it is reduced for methods that feed back on their own misses.
- As a result the floor is 1.56 % for CQR and 1.23 % for HSC-CQR recency (seed_level_metrics.csv). The abstract and §4.1 quote 1.6 %/0.4 %, while §4.2 quotes 1.2 %/0.3 %.
- Day blocks are treated as independent across days (risk f). The weekly reference SE·√8 assumes i.i.d. days.
- The layer's 0.4 % lies *below* its own reference, so calling it "the level expected from sampling noise" is a description, not a test.

Action: use one reference that does not depend on the method, e.g. a block bootstrap of miss indicators re-centred to 0.9 that preserves the autocorrelation between days. Report a confidence interval, and use the same numbers throughout.

**5. Moderate: the κ→∞ limit is not the pooled CQR baseline.**
Evidence: for the recency variant, κ = ∞ gives a building-weighted, stage-agnostic F^pop with a finite-sample level based on the score count (`calibration.py:202–205`, `pipeline.py:401`). The CQR baseline is score-weighted and stage-matched (`pipeline.py:315`). The gain over CQR therefore mixes the effect of shrinkage with changes in weighting and stage matching.
Action: qualify the "κ→∞ gives pooled split conformal" statement, and report κ = ∞ of the same variant in Table 1 and Fig. 6.

**6. Moderate: the day-ahead information set is optimistic, and target-period data are used for inclusion.**
Evidence:
- Features use all 24 hours of day D−1 (`features.py:59,77`), with the forecast issued at the end of D−1 (§2.1). Day-ahead and DR nominations typically close around midday on D−1, and the Limitations section does not mention this (it covers only observed weather).
- The quality filter requires ≤ 5 % missing hours in 2017 (BDG2) and 2014 (UCI), the target periods (`datasets.py:96–99, 144–147`). Target windows are also chosen using the validity of the future window (`pipeline.py:129–133`). This contradicts §3.2 ("never seen…") and removes difficult buildings.

Experiment: rerun the main protocol with the D−1 hours after the gate masked, and with the filter computed on the training period only.

**7. Minor: notation and consistency.**
- The Table 3 caption cites "Eq. 9", but the cost is Eq. (7).
- ρ is used both for the decay factor and for the penalty ratio.
- The TQA-B docstring says a is clipped at 0.01 (`calibration.py:302`), but the code does not clip.
- §2.2 says "daily statistics … over at most 28 days", but prev_mean/max/min use only D−1 (`features.py:81–86`).
- The ACI quantile omits the (N+1) correction that CQR uses (`calibration.py:231`), so γ = 0 does not exactly reproduce CQR.
