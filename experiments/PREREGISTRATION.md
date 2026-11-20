# Pre-registered research design (written before any target-building result was inspected)

Date: 2026-11-15. Only a pipeline smoke test (reduced data) had been run when this file was written;
any change after this point is logged in CHANGELOG.md with its justification.

## Problem
Day-ahead (24 h) hourly electricity forecasts with prediction intervals are needed for a building
from the first days after it is metered (cold start). A global model trained on other buildings
gives point forecasts; the question is how to calibrate intervals so that **each** new building
receives intervals with close-to-nominal coverage, with as little width as possible, from day 1.

## Hypothesis
H0 (main): Pooled split-conformal calibration attains near-nominal *marginal* coverage on new
buildings but leaves a large dispersion of *per-building* coverage, most severely in the first
week; a hierarchical-shrinkage calibration (HSC) that starts from a similarity-localised,
onboarding-stage-matched population score distribution and shrinks toward the building's own
accumulating scores (pseudo-count κ) reduces per-building miscalibration and the interval score
without any target-building tuning.

## Research questions → experiments
| RQ | Question | Experiment | Primary metric |
|---|---|---|---|
| RQ1 | How reliable are standard interval methods per building during onboarding? | E1 main evaluation (BDG2, UCI; 5 seeds) | MACD, under-coverage rate, P10 coverage |
| RQ2 | Does HSC improve per-building reliability and interval score over strong baselines? | E2 baseline comparison + paired tests | rel. interval score (IS), MACD |
| RQ3 | Which HSC components matter? | E3 ablation (−stage matching, −kNN prior, −shrinkage, fixed κ, combinations) | IS, MACD |
| RQ4 | Is HSC robust to meter noise, missing data, abrupt load changes, small calibration pools, weaker forecasters? | E4 robustness | IS, MACD, coverage |
| RQ5 | Does it generalise to unseen sites and to another dataset/country? | E5 leave-site-out (BDG2), cross-dataset (BDG2↔UCI) | IS, MACD |
| — | Cost? | E6 efficiency: tuning time, per-target-day time, memory | seconds, MB |
| — | Sensitivity to κ, K, α | E7 | IS, MACD vs. parameter |
| — | Where does it fail? | E8 error analysis by usage, site, volatility, stage | per-building coverage |

## Pre-specified choices
* Nominal level 90 % (α = 0.1) main; α ∈ {0.05, 0.2} in E7.
* Seeds: 0,1,2,3,4 (partition, onboarding dates, model seeds). Fixed before results.
* Onboarding window: 56 daily forecasts per target building.
* Tuning objective for HSC (κ, K) and ACI (γ): mean normalised interval score on calibration
  buildings, leave-one-building-out. Grids: κ ∈ {0,24,48,96,168,336,672,1344,∞} (hours of pseudo-
  observations), K ∈ {10,25,50,100,all}, γ ∈ {5e-4,1e-3,2e-3,5e-3,1e-2}.
* Primary endpoints: per-building rel. interval score (lower = better) and |coverage − 0.9|.
* Statistics: unit = target building; Wilcoxon signed-rank (paired, two-sided) HSC vs. each baseline,
  Holm correction across baselines; effect size = matched-pairs rank-biserial r; 95 % CIs by site-
  cluster bootstrap (BDG2) / building bootstrap (UCI); seed-level mean ± s.d.
* Under-coverage threshold: coverage < 0.85 (5 pp below nominal).

## Baselines
Seasonal-naive + SCP (classical); raw-kWh pooled SCP; normalised pooled SCP; stage-matched SCP;
Mondrian-by-usage SCP; self-only conformal (fallback to pooled); ACI (Gibbs & Candès 2021);
LightGBM quantile regression; CQR (Romano et al. 2019); MLP-Gaussian (NLL); MLP quantile regression;
HSC on CQR scores (variant).

---
## Addendum A (2026-11-20, review cycle 1) — written BEFORE any of the following was implemented or run

Context: Reviewer #1 showed, and the author confirmed from results/raw_results.csv.gz, that (i) no shrinkage
variant improves reliability in the first week (BDG2 under-covered share, week 1: HSC-CQR 24.5 %, CQR 23.8 %),
(ii) the interval-score tuning objective selects larger κ than per-building reliability favours (fixed κ = 168 h
beats tuned κ on MACD), (iii) TQA-B used the maximum budget over *target* buildings to scale λ (fairness bug),
(iv) ACI set the radius to the grid cap whenever α_h ≤ 0. The original pre-registration file was committed with
the code (commit e9ca94d) and is an internal protocol, not an external registration; the manuscript will say so
and list all deviations.

### New hypotheses and fixed designs
H-A (objective mismatch). Selecting κ by leave-one-building-out *per-building coverage deviation*
(LOBO-MACD on calibration buildings) instead of the interval score yields lower target MACD than IS-tuning.
Fairness: the same objective is also applied to QShrink-CQR (λ) and ACI-CQR (γ). Variants:
"HSC-CQR simple (cov)", "QShrink-CQR (cov)", "ACI-CQR (cov)".

H-B (scale before quantile). A building's error *scale* can be estimated from far fewer own scores than its
90 % tail quantile. Stage-wise studentised conformal calibration ("SSC-CQR"): each CQR score is divided by the
building's running shrunk scale ratio r_{b,h} = σ̂_{b,h}/σ0, σ̂_{b,h} = (κ_s σ0 + Σ own |abs residual|/s)/(κ_s + n_{b,h})
using only stages < h; the radius is the (1−α) quantile of the building-weighted pooled CDF of studentised
calibration scores at the *exact* stage h, with a point mass 1/(M+1) at +∞ for the new building
(Dunn et al. pooled-CDF construction); interval [q̂lo − q r s, q̂hi + q r s]. κ_s fixed a priori at 24
(one day of hourly scores; not tuned, so that the stage-wise exchangeability argument is not affected by tuning);
σ0 = building-weighted mean abs residual of calibration buildings (leave-one-out for calibration buildings).
Prediction: lower under-covered share than CQR and HSC-CQR in week 1 (days 2–7) and overall.
Combination: "HSC-SSC-CQR" = HSC simple (κ by LOBO-MACD) applied to the studentised scores.

H-C (recency). Exponential down-weighting of own scores (factor 0.95 per day, half-life ≈ 13.5 days, fixed a
priori) reduces under-coverage after level shifts. Variant "HSC-CQR recency" (simple, κ by LOBO-MACD).

### Fixes to baselines
* TQA-B-CQR: λ computed from the calibration buildings' own budgets (each ranked among the others), never
  from target buildings.
* ACI / ACI-CQR: for α_h ≤ 0 the radius is the largest observed calibration score (finite surrogate of the
  infinite interval) instead of the 500·s grid cap; the frequency of α_h ≤ 0 events is logged.
* α ∈ {0.05, 0.2}: all CQR-based methods are now evaluated too (quantile models trained at α = 0.1; conformal
  calibration corrects the level; documented as a deviation).

### New outcome measures (operational, pre-specified)
* Upper- and lower-tail exceedance rates per building (nominal 5 % each).
* Capacity-headroom case study: an operator offers headroom below a contracted limit equal to (limit − U) and
  pays a penalty for violations (y − U)+. Relative cost per building = mean(U)/ȳ + ρ·mean((y − U)+)/ȳ for
  penalty ratios ρ ∈ {10, 20, 40} (all three reported); share of buildings with
  upper-tail exceedance > 10 % (twice nominal) = "under-protected buildings".
* Day-block standard error of each building's coverage (daily coverage values, s.d./√days) → sampling floor of MACD
  E|N(0,SE²)| = SE·√(2/π), replacing the independence-based floor.
* Statistics: additionally a site-level paired test for BDG2 (Wilcoxon on site means, n = 10 sites) and a
  sensitivity analysis excluding the largest site (Rat).

All results, favourable or not, will be reported; no variant will be dropped after seeing results.
