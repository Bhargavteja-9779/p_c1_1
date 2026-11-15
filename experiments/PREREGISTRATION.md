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
