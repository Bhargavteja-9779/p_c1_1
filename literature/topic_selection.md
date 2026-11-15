# Topic discovery, stress test and selection (Phases 1–2, Global Update 2)

Constraints: target = Advances in Applied Energy; 4 CPU cores, no GPU; user asked to avoid "hi-fi"
(heavy/over-ambitious) topics and hype-driven topics.

## 15 candidate directions (screened)
| # | Direction | Verdict | Main reason |
|---|---|---|---|
| 1 | Transformer/LSTM hybrid for building load forecasting | reject | generic architecture; marginal-accuracy paper |
| 2 | Leakage audit of random-split battery SOH evaluation | reject | already established (cell-wise GroupKFold papers 2025–2026) |
| 3 | Leakage in CWRU bearing benchmarks | reject | already published (MSSP benchmark papers); off-scope |
| 4 | Conformal intervals for battery SOH across datasets | reject | close 2026 preprints (conformalized transfer learning for SOH); data heavy |
| 5 | Mamba/ACI probabilistic STLF | reject | done (KBS 2025, Mamba-ACI); architecture-driven |
| 6 | Physics-informed solar nowcasting from sky images | reject | GPU-heavy ("hi-fi"); SkyGPT already in AAE |
| 7 | Probabilistic wind/PV aggregation | reject | AAE already has close paper; data licensing |
| 8 | Concrete strength / tabular ML | reject | overused, weak novelty, off-scope |
| 9 | Interpretable ML for building energy (SHAP) | reject | reviewed in AAE 2023; limited scientific contribution |
| 10 | Active learning for HVAC modelling | reject | needs plant data not public |
| 11 | Zero-shot load forecasting with pretrained foundation models | reject | GPU-heavy; BuildingsBench exists |
| 12 | Robustness of load forecasts to meter faults | reserve | relevant but weaker hypothesis; folded into robustness experiments |
| 13 | EV-charging load uncertainty | reject | public data limited; MDPI-saturated |
| 14 | City-scale demand forecasting under extremes | reject | AAE 2021 paper; few public series |
| **15** | **Reliable (per-building calibrated) prediction intervals for day-ahead load forecasts of newly metered (cold-start) buildings** | **select** | real operational gap; public large data (BDG2 1,578 meters/19 sites; UCI 370 clients); CPU-feasible; objectively testable (coverage is checkable) |

## Stress test of #15 (skeptical-editor questions)
- *Already solved?* Split/pooled conformal gives marginal coverage across pooled hours, but not per-building
  reliability during the onboarding period; search found no study evaluating per-building coverage of
  intervals for newly metered buildings (closest: BuildingsBench zero-shot probabilistic STLF — no
  calibration analysis per building; cross-building conformal studies report reduced coverage on unseen
  buildings without a remedy; MC-dropout transfer study, 2026).
- *Just combining techniques?* Risk acknowledged. Contribution is a calibration layer whose components
  each have a hypothesis and an ablation: (i) scale-normalised, onboarding-stage-matched scores,
  (ii) partial pooling between population and building-specific score distributions with a
  pseudo-count κ (Dirichlet-process posterior-mean CDF), (iii) similarity-localised population prior,
  (iv) κ and neighbourhood size chosen by leave-building-out on source buildings only.
  Statistical precursors (hierarchical conformal: Dunn et al. 2023 JASA; Lee et al. 2023; clustered
  conformal: Ding et al. 2023; few-shot conformal: Fisch et al. 2021; Bayesian-bootstrap conformal 2025)
  are cited and positioned; none addresses sequential onboarding of new time series.
- *Simpler method enough?* Tested explicitly: pooled conformal, self-only conformal, ACI, Mondrian,
  quantile regression, CQR, Gaussian/quantile MLPs, seasonal-naive empirical intervals.
- *Data leakage risk?* Building-disjoint model-training / calibration / target sets; target period
  (2017 for BDG2, 2014 for UCI) strictly after model-training & calibration period.
- *Dataset too small?* >1,000 buildings, 2 datasets, leave-site-out and cross-dataset tests.
- *Could gains vanish under proper statistics?* Paired per-building Wilcoxon tests with Holm correction,
  site-cluster bootstrap CIs, 5 predefined partition seeds.
