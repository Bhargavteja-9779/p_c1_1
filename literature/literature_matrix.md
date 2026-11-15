# Literature matrix, gap analysis and novelty map (Phases 3–4)

All bibliographic data verified by `literature/verify_refs.py` (Crossref / arXiv / DataCite / NeurIPS
proceedings pages). Content columns are based on the abstracts and, where noted, full texts that
were accessible from this environment; "n/c" = not checked (not claimed in the manuscript).

## A. Matrix

| # | Paper (year, venue) | Problem | Data (size) | Method | Uncertainty | Per-unit calibration analysed? | Cold start / new unit? | Statistical testing | Code |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Miller et al. 2020, Sci. Data | BDG2 dataset | 3,053 meters, 1,636 buildings, 19 sites, 2016–17 | dataset paper | — | — | — | — | yes (GitHub) |
| 2 | Miller et al. 2020, STBE (GEPIII) | Kaggle competition overview | BDG2 subset | GBM ensembles (winners) | point only | no | no (buildings seen in training) | no | partial |
| 3 | Emami et al. 2023, NeurIPS D&B (BuildingsBench) | zero-shot / transfer STLF | 900K simulated + 7 real datasets incl. BDG2 | pretrained transformers | Gaussian / categorical predictive distributions, RPS | no per-building coverage | yes (zero-shot unseen buildings) | n/c | yes |
| 4 | Ribeiro et al. 2018, Energy & Buildings | cross-building transfer | school buildings | Hephaestus transfer + seasonal/trend adj. | no | no | partial (target with little data) | n/c | n/c |
| 5 | Fan et al. 2020, Applied Energy | transfer learning for STLF | 400 buildings (BDG1) | pretrained NN fine-tuning | no | no | yes (limited target data) | descriptive statistics | n/c |
| 6 | Pinto et al. 2022, Adv. Appl. Energy | review of 77 transfer-learning studies | — | review | — | identifies UQ as gap area (review) | — | — | — |
| 7 | Chen & Zhang 2021, Adv. Appl. Energy (TgDLF) | district load forecasting | Chinese districts | theory-guided ensemble LSTM | no | no | no | cross-validation | n/c |
| 8 | Gao et al. 2023, Adv. Appl. Energy | adaptive load forecasting | districts | transformer + transfer + online learning | no | no | transfer to new locations | cross-validation | n/c |
| 9 | Guo et al. 2024, Adv. Appl. Energy | multi-energy probabilistic forecasting | ASU campus | attentive QR-TCN | quantiles (PICP, PINAW, pinball) | no | no | n/c | n/c |
| 10 | Wang et al. 2021, Adv. Appl. Energy | city-scale daily demand | 3 US metros | 7 models incl. LightGBM | no | — | no | no | n/c |
| 11 | Nie et al. 2024, Adv. Appl. Energy (SkyGPT) | 15-min PV probabilistic forecast | 1 PV system | generative video + U-Net | CRPS, reliability | n/a (single site) | no | n/c | yes |
| 12 | Lindberg et al. 2023, Adv. Appl. Energy | co-located wind+PV day-ahead | 1 park, 3 years | NWP post-processing | CRPS, IS, quantile score | n/a | no | n/c | n/c |
| 13 | Hong & Fan 2016, IJF | probabilistic load forecasting review | — | review | — | — | — | — | — |
| 14 | Hong et al. 2016, IJF (GEFCom2014) | probabilistic competition | — | many | pinball | aggregate | no | — | — |
| 15 | Wang et al. 2019, Applied Energy | individual (household) PLF | smart meters | pinball-loss LSTM | quantiles | n/c | no | n/c | n/c |
| 16 | Salinas et al. 2020, IJF (DeepAR) | global probabilistic forecasting | many series | autoregressive RNN, likelihood | parametric | no | handles short series | — | yes (GluonTS) |
| 17 | Suresh et al. 2025, Knowl.-Based Syst. | very-short-term load UQ | n/c | LSTM/Mamba + ACI | conformal (ACI) | n/c | no | n/c | n/c |
| 18 | Lei et al. 2018, JASA | split conformal regression | — | theory | marginal coverage | — | — | — | — |
| 19 | Romano et al. 2019, NeurIPS (CQR) | adaptive conformal intervals | UCI regression | CQR | marginal | — | — | — | yes |
| 20 | Gibbs & Candès 2021, NeurIPS (ACI) | conformal under shift | stocks, elections | online α update | long-run coverage | — | — | — | yes |
| 21 | Tibshirani et al. 2019, NeurIPS | covariate shift | — | weighted conformal | marginal under shift | — | — | — | — |
| 22 | Barber et al. 2023, Ann. Stat. | non-exchangeable data | — | weighted (nexCP) | coverage-gap bounds | — | — | — | — |
| 23 | Dunn, Wasserman & Ramdas 2023, JASA | two-layer hierarchical data, new group | simulations, real | pooling / subsampling CP | marginal for new group | — | **new group w/o own data** | — | — |
| 24 | Lee, Barber & Willett 2023 (arXiv) | hierarchical exchangeability | — | HCP | marginal | — | repeated measurements | — | — |
| 25 | Ding et al. 2023, NeurIPS | class-conditional coverage, few samples per class | ImageNet etc. | clustered conformal (pool similar classes) | class-conditional (approx.) | **yes (per class)** | rare classes | — | yes |
| 26 | Fisch et al. 2021, ICML | few-shot conformal | images, text, chemistry | meta-learned quantile predictor | task-marginal | per task | **new task with few labels** | — | yes |
| 27 | Gibbs, Cherian & Candès 2025, JRSSB | conditional guarantees | — | conditional calibration over function class | group-conditional | yes | — | — | yes |
| 28 | Gibson et al. 2025 (arXiv) | Bayesian bootstrap CP | — | Dirichlet weights on scores | Bayesian/conformal | — | — | — | n/c |

## B. Gaps (what exists → what it fails to address → why it matters)
1. **Energy forecasting**: probabilistic building/district forecasting is evaluated with *pooled*
   reliability metrics (PICP, CRPS, pinball) on buildings with long histories (#7–#12, #15, #17).
   Zero-shot/transfer work (#3–#6) targets point accuracy or pooled probabilistic scores.
   → No study reports how coverage is distributed **across individual new buildings** or how it
   evolves **day by day after metering starts**. Matters because interval consumers (demand-response
   baselines, flexibility bids, M&V, anomaly alarms) act per building; a 90 % marginal guarantee can
   hide many buildings with 70 % coverage.
2. **Conformal methodology**: hierarchical/clustered/few-shot conformal (#23–#28) pool calibration
   information across groups, but (i) assume i.i.d. groups/tasks with a fixed small calibration set,
   (ii) do not address *sequential* accumulation of a new unit's own scores together with a forecast
   quality that changes with history length, and (iii) are not evaluated on energy time series.
3. **Evaluation**: no benchmark protocol for onboarding (building-disjoint, period-disjoint,
   stage-resolved); statistical testing across buildings is rare in the domain literature.

## C. Novelty map
| Existing work | Contribution | Proposed work — genuinely different element |
|---|---|---|
| Split / CQR / ACI (#18–#20) | marginal or long-run coverage for one series / pooled data | per-building reliability during onboarding; HSC combines population and own scores with an explicit pseudo-count |
| Dunn et al. (#23) | prediction for a new group *without* its data | new building's own scores arrive daily; shrinkage weight moves from prior to own data as n_b grows |
| Ding et al. (#25) | clusters classes by *score distributions* | a new building has (almost) no scores → neighbours found from *load-shape descriptors* of the first days; stage-matched prior |
| Fisch et al. (#26) | meta-learned quantile predictor over auxiliary tasks | no meta-training of a network; closed-form mixture CDF; tuning of 2 scalars by leave-one-building-out |
| BuildingsBench (#3) | zero-shot forecasting accuracy, pooled probabilistic scores | calibration layer usable on top of any forecaster; stage-resolved per-building evaluation |
| ACI-based load UQ (#17) | online adaptation for a long series | ACI is a baseline here; HSC is compared and both are tested under level shifts |

Claim used in the manuscript (worded conservatively): *"To our knowledge, no prior study has
evaluated or targeted per-building coverage of day-ahead prediction intervals during the first weeks
after a building is metered."* (Searches documented in literature/topic_selection.md; not "first ever".)
