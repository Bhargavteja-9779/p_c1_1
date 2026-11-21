# Claim–evidence map (auto-generated; qualitative claims require manual evidence column)

### 01_front.md
> {{ABSTRACT}}

- `ABSTRACT` = Demand response, flexibility bidding and measurement-and-verification need day-ahead prediction intervals for individual ← generated text (manuscript/values.py) from results/*.json/csv

### 02_intro.md
> 1. **Problem and evaluation protocol.** We formalise *per-building interval reliability during onboarding* — coverage of each new building over its first weeks, the dispersion of coverage across buildings, the share of clearly under-covered buildings and the evolution with the number of days since metering started — and evaluate it under a pre-registered, strictly building- and period-disjoint protocol on two public datasets with {{n_bdg2}} buildings and {{n_uci}} clients, including leave-site-out and cross-country transfer and stress tests. 2. **A head-to-head comparison of calibration strate

- `n_bdg2` = 842 ← data/processed after quality filter (src/data/datasets.py)
- `n_uci` = 315 ← data/processed after quality filter (src/data/datasets.py)

### 03_related.md
> These works assess reliability with *pooled* metrics over a site, a system or a test period, typically for systems with long histories; how reliability is distributed across many individual buildings, and how it evolves during the first weeks of data, has not been their object.

- **qualitative claim — evidence to be mapped manually**

### 03_related.md
> For time series, exchangeability fails: adaptive conformal inference (ACI) [@gibbs2021] and its aggregated variants [@zaffran2022] adjust the miscoverage level online, and ensemble or weighted methods bound the coverage gap under weak dependence or distribution drift [@xu2021; @barber2023; @tibshirani2019].

- **qualitative claim — evidence to be mapped manually**

### 03_related.md
> Mondrian conformal prediction [@vovk2005] requires enough calibration data in every group; conditional calibration over a function class gives guarantees for pre-specified groups [@gibbs2025cond]; clustered conformal prediction pools groups with similar score distributions [@ding2023]; few-shot conformal prediction meta-learns from auxiliary tasks [@fisch2021]; and personalised or federated methods weight other agents' scores [@vejling2026].

- **qualitative claim — evidence to be mapped manually**

### 03_related.md
> For hierarchical data, Dunn et al. [@dunn2023] and Lee et al. [@lee2023hier] obtain marginal coverage for a new group, and generalised hierarchical conformal prediction (GHCP) uses a new group's first few observations together with reference groups while retaining a finite-sample guarantee, by giving the new group the weight of a single reference group [@mallick2026].

- **qualitative claim — evidence to be mapped manually**

### 03_related.md
> What has been missing is evidence on *which* of these strategies makes day-ahead **load** intervals reliable for each newly metered building — a setting with a large, heterogeneous population of units, a forecaster whose accuracy itself improves with the history length, and a need for calibration from the first day.

- **qualitative claim — evidence to be mapped manually**

### 04_method.md
> For a miscoverage level $\alpha$ (main analysis: $\alpha=0.1$), the goal is an interval $C_{b,h,j}=[L_{b,h,j},U_{b,h,j}]$ such that, **for every individual building**, the share of hours with $y_{b,t,j}\in C_{b,h,j}$ is close to $1-\alpha$ from the first days after metering starts, while the intervals remain as narrow as possible.

- **qualitative claim — evidence to be mapped manually**

### 04_method.md
> Three disjoint sets of buildings are available (Section [-@sec:setup]): *training* buildings for the global forecaster, *calibration* buildings whose (simulated) onboarding windows provide nonconformity scores, and *target* buildings, which are metered in a later period and on which all methods are evaluated.

- **qualitative claim — evidence to be mapped manually**

### 04_method.md
> Division by $s_{b,h}$ is what makes scores from buildings of different size comparable and therefore poolable.

- **qualitative claim — evidence to be mapped manually**

### 04_method.md
> Split conformal prediction [@vovk2005; @lei2018] would set $q$ to the $\lceil(1-\alpha)(N+1)\rceil$-th smallest of $N$ pooled calibration scores.

- **qualitative claim — evidence to be mapped manually**

### 04_method.md
> Buildings without any valid score in $\mathcal B$ are left out of the average, and buildings whose descriptor is undefined (no valid data in the descriptor window) are never selected as neighbours.

- **qualitative claim — evidence to be mapped manually**

### 04_method.md
> Target buildings are never used for any choice.

- **qualitative claim — evidence to be mapped manually**

### 04_method.md
> ([-@eq:hsc]) then reduce to a vectorised search; the grid quantile is rounded upwards (conservatively) for all methods alike, and a quantile above the grid range is capped at $500\,s_{b,h}$ (a conservative stand-in for an unbounded radius).

- **qualitative claim — evidence to be mapped manually**

### 05_setup.md
> **UCI.** The ElectricityLoadDiagrams20112014 dataset [@trindade2015] contains 15-min consumption of {{n_uci_raw}} Portuguese electricity clients (2011–2014).

- `n_uci_raw` = 370 ← manuscript/values.py

### 05_setup.md
> **Quality rules** (applied identically to all methods and fixed before the main experiments): runs of at least 24 identical consecutive readings (meter outage or stuck meter) are treated as missing; gaps of at most 6 h are linearly interpolated; a building is retained if at most 5 % of its hours are missing in every period used and its mean load is at least 1 kWh/h.

- **qualitative claim — evidence to be mapped manually**

### 05_setup.md
> This leaves **{{n_bdg2}} BDG2 buildings at {{n_sites}} sites** and **{{n_uci}} UCI clients** (Fig. [-@fig:data]).

- `n_bdg2` = 842 ← data/processed after quality filter (src/data/datasets.py)
- `n_sites` = 10 ← data/processed after quality filter (src/data/datasets.py)
- `n_uci` = 315 ← data/processed after quality filter (src/data/datasets.py)

### 05_setup.md
> Target buildings, their period and their data are therefore never seen by the forecaster, the calibration scores, or any hyper-parameter selection.

- **qualitative claim — evidence to be mapped manually**

### 05_setup.md
> *Leave-site-out (BDG2).* The {{n_sites}} sites are grouped into five folds of similar size.

- `n_sites` = 10 ← data/processed after quality filter (src/data/datasets.py)

### 05_setup.md
> * **Naive+SCP** (classical): seasonal-naive forecast (same hour one week earlier if $h\ge7$, else the previous day) with stage-matched split conformal intervals. * **Raw-SCP**: split conformal prediction on unnormalised absolute residuals (kWh). * **SCP**: split conformal on normalised absolute scores pooled over all stages [@lei2018]. * **SCP-stage**: as SCP, with stage-bin matching (the score-weighted analogue of HSC with $\kappa=\infty$, $K=$ all, whose prior weights buildings equally). * **Mondrian-usage** (BDG2): SCP-stage computed separately per primary-usage class (classes with at least

- **qualitative claim — evidence to be mapped manually**

### 05_setup.md
> When $\alpha_h$ leaves $[0,1]$, the radius is set to the largest grid value ($\alpha_h\le 0$) or to the smallest observed score ($\alpha_h\ge1$, empty-set convention). * **QR-LGBM**: direct LightGBM quantile regression [@ke2017; @koenker1978]. * **CQR** [@romano2019]: QR-LGBM conformalised with stage-matched pooled CQR scores. * **MLP-Gauss**: a global multilayer perceptron (256-256-128, ReLU) with a Gaussian output trained by negative log-likelihood, a deep probabilistic baseline in the spirit of DeepAR's likelihood training [@salinas2020]. * **MLP-QR**: the same network trained with the pinb

- **qualitative claim — evidence to be mapped manually**

### 05_setup.md
> Effect sizes are matched-pairs rank-biserial correlations [@kerby2014], positive when HSC is better. 95 % confidence intervals of the mean paired difference come from a cluster bootstrap over sites for BDG2 (buildings at a site share weather and operation) and over buildings for UCI (2000 resamples).

- **qualitative claim — evidence to be mapped manually**

### 06_results.md
> The global LightGBM forecaster reaches a median CV(RMSE) of {{point_BDG2_cvrmse_lgb}} on new BDG2 buildings over their first 56 forecast days (seasonal naive: {{point_BDG2_cvrmse_naive}}; MLP: {{point_BDG2_cvrmse_mlp}}) and {{point_UCI_cvrmse_lgb}} on UCI clients (naive {{point_UCI_cvrmse_naive}}; MLP {{point_UCI_cvrmse_mlp}}).

- `point_BDG2_cvrmse_lgb` = 0.136 ← results/run_info.json
- `point_BDG2_cvrmse_naive` = 0.197 ← results/run_info.json
- `point_BDG2_cvrmse_mlp` = 0.137 ← results/run_info.json
- `point_UCI_cvrmse_lgb` = 0.089 ← results/run_info.json
- `point_UCI_cvrmse_naive` = 0.120 ← results/run_info.json
- `point_UCI_cvrmse_mlp` = 0.087 ← results/run_info.json

### 06_results.md
> Stage-matched split conformal prediction (SCP-stage) attains a mean per-building coverage of {{main_BDG2_SCPstage_mean_cov}} on BDG2, close to the 0.90 target, yet {{main_BDG2_SCPstage_under_rate}} of the new buildings have coverage below 0.85 and the 10th percentile of per-building coverage is {{main_BDG2_SCPstage_p10_cov}}.

- `main_BDG2_SCPstage_mean_cov` = 0.881 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_SCPstage_under_rate` = 29.0% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_SCPstage_p10_cov` = 0.700 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 06_results.md
> Direct quantile regression under-covers on average ({{main_BDG2_QRLGBM_mean_cov}}); conformalising it (CQR) restores the mean ({{main_BDG2_CQR_mean_cov}}) but leaves {{main_BDG2_CQR_under_rate}} of the buildings under-covered.

- `main_BDG2_QRLGBM_mean_cov` = 0.859 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_CQR_mean_cov` = 0.891 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_CQR_under_rate` = 18.7% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 06_results.md
> Calibrating separately per usage type (Mondrian-usage, {{main_BDG2_Mondrianusage_under_rate}}) does not help, and the deep quantile model (MLP-QR, {{main_BDG2_MLPQR_under_rate}}) does not solve the problem either; the Gaussian MLP lowers under-coverage only by over-covering on average ({{main_BDG2_MLPGauss_mean_cov}}) with wider intervals (median relative width {{main_BDG2_MLPGauss_rel_width}} vs {{main_BDG2_CQR_rel_width}} for CQR).

- `main_BDG2_Mondrianusage_under_rate` = 28.5% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_MLPQR_under_rate` = 20.6% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_MLPGauss_mean_cov` = 0.924 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_MLPGauss_rel_width` = 0.451 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_CQR_rel_width` = 0.383 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 06_results.md
> The same pattern appears on UCI, where SCP-stage and CQR leave {{main_UCI_SCPstage_under_rate}} and {{main_UCI_CQR_under_rate}} of the clients under-covered.

- `main_UCI_SCPstage_under_rate` = 20.2% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_UCI_CQR_under_rate` = 9.5% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 06_results.md
> Pseudo-count shrinkage of the score distribution (HSC-CQR) is the most reliable of the tuned strategies on both datasets: on BDG2 its MACD is {{main_BDG2_HSCCQR_macd}} and {{main_BDG2_HSCCQR_under_rate}} of the buildings are under-covered (CQR: {{main_BDG2_CQR_macd}}, {{main_BDG2_CQR_under_rate}}), and on UCI {{main_UCI_HSCCQR_macd}} and {{main_UCI_HSCCQR_under_rate}} (CQR: {{main_UCI_CQR_macd}}, {{main_UCI_CQR_under_rate}}).

- `main_BDG2_HSCCQR_macd` = 0.018 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_HSCCQR_under_rate` = 3.4% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_CQR_macd` = 0.038 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_CQR_under_rate` = 18.7% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_UCI_HSCCQR_macd` = 0.014 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_UCI_HSCCQR_under_rate` = 0.6% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_UCI_CQR_macd` = 0.033 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_UCI_CQR_under_rate` = 9.5% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 06_results.md
> The 10th-percentile coverage rises from {{main_BDG2_CQR_p10_cov}} to {{main_BDG2_HSCCQR_p10_cov}} on BDG2.

- `main_BDG2_CQR_p10_cov` = 0.831 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_HSCCQR_p10_cov` = 0.864 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 06_results.md
> The median relative interval score is essentially unchanged ({{main_BDG2_HSCCQR_rel_IS}} vs {{main_BDG2_CQR_rel_IS}} on BDG2; {{main_UCI_HSCCQR_rel_IS}} vs {{main_UCI_CQR_rel_IS}} on UCI), so the gain in reliability does not come from wider intervals.

- `main_BDG2_HSCCQR_rel_IS` = 0.564 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_CQR_rel_IS` = 0.564 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_UCI_HSCCQR_rel_IS` = 0.368 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_UCI_CQR_rel_IS` = 0.368 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 06_results.md
> For reference, perfectly calibrated intervals with independent misses would have an expected MACD of about {{floor_BDG2_macd}} (BDG2) and {{floor_UCI_macd}} (UCI) from sampling noise alone ({{nvalid_BDG2_median}} hourly observations per building); autocorrelated misses raise this floor further.

- `floor_BDG2_macd` = 0.0066 ← Monte Carlo from per-building n_valid (manuscript/values.py)
- `floor_UCI_macd` = 0.0065 ← Monte Carlo from per-building n_valid (manuscript/values.py)
- `nvalid_BDG2_median` = 1344 ← Monte Carlo from per-building n_valid (manuscript/values.py)

### 06_results.md
> Quantile-level shrinkage (QShrink-CQR, the "regularised Mondrian") is the closest competitor (MACD {{main_BDG2_QShrinkCQR_macd}} on BDG2, {{main_UCI_QShrinkCQR_macd}} on UCI; under-covered {{main_BDG2_QShrinkCQR_under_rate}} and {{main_UCI_QShrinkCQR_under_rate}}).

- `main_BDG2_QShrinkCQR_macd` = 0.022 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_UCI_QShrinkCQR_macd` = 0.016 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_QShrinkCQR_under_rate` = 4.1% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_UCI_QShrinkCQR_under_rate` = 1.7% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 06_results.md
> Self-only calibration (Self-CQR) is reliable later in the window but poor in the first week (coverage {{main_BDG2_SelfCQR_cov_early}} on BDG2), when a handful of own scores yields noisy quantiles.

- `main_BDG2_SelfCQR_cov_early` = 0.864 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 06_results.md
> Adaptive conformal inference on the same scores (ACI-CQR; MACD {{main_BDG2_ACICQR_macd}}, under-covered {{main_BDG2_ACICQR_under_rate}}) adapts more slowly because it reacts to the building's errors only through the miscoverage indicator with a small step size.

- `main_BDG2_ACICQR_macd` = 0.027 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_ACICQR_under_rate` = 10.5% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 06_results.md
> Temporal quantile adjustment (TQA-B-CQR; {{main_BDG2_TQABCQR_macd}}, {{main_BDG2_TQABCQR_under_rate}}) and the GHCP-style pooling (GHCP-CQR; {{main_BDG2_GHCPCQR_macd}}, {{main_BDG2_GHCPCQR_under_rate}}) remain close to pooled CQR: TQA-B bounds the quantile adjustment by design, and GHCP never gives the new building more weight than one reference building, which secures marginal validity across buildings but cannot correct a building whose errors are systematically larger than average.

- `main_BDG2_TQABCQR_macd` = 0.038 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_TQABCQR_under_rate` = 17.0% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_GHCPCQR_macd` = 0.038 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_GHCPCQR_under_rate` = 16.8% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 06_results.md
> On BDG2, HSC-CQR has a smaller absolute coverage deviation than CQR for {{test_main_BDG2_HSCCQR_vs_CQR_abs_dev_better}} of the {{test_main_BDG2_HSCCQR_vs_CQR_abs_dev_n}} buildings ($r_{rb}$ = {{test_main_BDG2_HSCCQR_vs_CQR_abs_dev_r}}, Holm-adjusted $p$ {{test_main_BDG2_HSCCQR_vs_CQR_abs_dev_p}}); against QShrink-CQR the corresponding values are {{test_main_BDG2_HSCCQR_vs_QShrinkCQR_abs_dev_better}} ($r_{rb}$ = {{test_main_BDG2_HSCCQR_vs_QShrinkCQR_abs_dev_r}}, $p$ {{test_main_BDG2_HSCCQR_vs_QShrinkCQR_abs_dev_p}}), against Self-CQR {{test_main_BDG2_HSCCQR_vs_SelfCQR_abs_dev_better}} ($r_{rb}$

- `test_main_BDG2_HSCCQR_vs_CQR_abs_dev_better` = 84% ← results/statistics.csv (src/statistics/analysis.py::paired_tests)
- `test_main_BDG2_HSCCQR_vs_CQR_abs_dev_n` = 713 ← results/statistics.csv (src/statistics/analysis.py::paired_tests)
- `test_main_BDG2_HSCCQR_vs_CQR_abs_dev_r` = 0.86 ← results/statistics.csv (src/statistics/analysis.py::paired_tests)
- `test_main_BDG2_HSCCQR_vs_CQR_abs_dev_p` = < 0.001 ← results/statistics.csv (src/statistics/analysis.py::paired_tests)
- `test_main_BDG2_HSCCQR_vs_QShrinkCQR_abs_dev_better` = 63% ← results/statistics.csv (src/statistics/analysis.py::paired_tests)
- `test_main_BDG2_HSCCQR_vs_QShrinkCQR_abs_dev_r` = 0.40 ← results/statistics.csv (src/statistics/analysis.py::paired_tests)
- `test_main_BDG2_HSCCQR_vs_QShrinkCQR_abs_dev_p` = < 0.001 ← results/statistics.csv (src/statistics/analysis.py::paired_tests)
- `test_main_BDG2_HSCCQR_vs_SelfCQR_abs_dev_better` = 56% ← results/statistics.csv (src/statistics/analysis.py::paired_tests)
- `test_main_BDG2_HSCCQR_vs_SelfCQR_abs_dev_r` = 0.22 ← results/statistics.csv (src/statistics/analysis.py::paired_tests)
- `test_main_BDG2_HSCCQR_vs_SelfCQR_abs_dev_p` = < 0.001 ← results/statistics.csv (src/statistics/analysis.py::paired_tests)
- `test_main_BDG2_HSCCQR_vs_ACICQR_abs_dev_better` = 74% ← results/statistics.csv (src/statistics/analysis.py::paired_tests)
- `test_main_BDG2_HSCCQR_vs_ACICQR_abs_dev_r` = 0.66 ← results/statistics.csv (src/statistics/analysis.py::paired_tests)
- `test_main_BDG2_HSCCQR_vs_ACICQR_abs_dev_p` = < 0.001 ← results/statistics.csv (src/statistics/analysis.py::paired_tests)

### 06_results.md
> The reliability gain does not cost sharpness: HSC-CQR's per-building interval score is lower than CQR's for {{test_main_BDG2_HSCCQR_vs_CQR_rel_IS_better}} of the buildings ($r_{rb}$ = {{test_main_BDG2_HSCCQR_vs_CQR_rel_IS_r}}, $p$ {{test_main_BDG2_HSCCQR_vs_CQR_rel_IS_p}}) and statistically indistinguishable from QShrink-CQR's ($p$ {{test_main_BDG2_HSCCQR_vs_QShrinkCQR_rel_IS_p}}).

- `test_main_BDG2_HSCCQR_vs_CQR_rel_IS_better` = 58% ← results/statistics.csv (src/statistics/analysis.py::paired_tests)
- `test_main_BDG2_HSCCQR_vs_CQR_rel_IS_r` = 0.41 ← results/statistics.csv (src/statistics/analysis.py::paired_tests)
- `test_main_BDG2_HSCCQR_vs_CQR_rel_IS_p` = < 0.001 ← results/statistics.csv (src/statistics/analysis.py::paired_tests)
- `test_main_BDG2_HSCCQR_vs_QShrinkCQR_rel_IS_p` = = 0.688 ← results/statistics.csv (src/statistics/analysis.py::paired_tests)

### 06_results.md
> The UCI comparisons, based on {{test_main_UCI_HSCCQR_vs_CQR_abs_dev_n}} clients, are reported in the same table.

- `test_main_UCI_HSCCQR_vs_CQR_abs_dev_n` = 270 ← results/statistics.csv (src/statistics/analysis.py::paired_tests)

### 06_results.md
> Fig. [-@fig:tradeoff] summarises reliability and sharpness of all methods.

- **qualitative claim — evidence to be mapped manually**

### 06_results.md
> The calibration layer is not specific to LightGBM: applied to the quantiles of the MLP quantile model, it reduces the MACD from {{main_BDG2_CQR_MLP_macd}} (CQR on MLP quantiles) to {{main_BDG2_HSCCQR_MLP_macd}} and the under-covered share from {{main_BDG2_CQR_MLP_under_rate}} to {{main_BDG2_HSCCQR_MLP_under_rate}} on BDG2 ({{main_UCI_CQR_MLP_macd}} → {{main_UCI_HSCCQR_MLP_macd}} on UCI).

- `main_BDG2_CQR_MLP_macd` = 0.037 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_HSCCQR_MLP_macd` = 0.018 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_CQR_MLP_under_rate` = 15.6% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_HSCCQR_MLP_under_rate` = 2.5% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_UCI_CQR_MLP_macd` = 0.033 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_UCI_HSCCQR_MLP_macd` = 0.016 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 06_results.md
> On the absolute-residual score, HSC improves on pooled SCP (MACD {{main_BDG2_HSC_macd}} vs {{main_BDG2_SCPstage_macd}}) but not on self-only calibration (Self-CP: {{main_BDG2_SelfCP_macd}}); for that score the stage-agnostic simple variant is the better choice ({{main_BDG2_HSC_simple_macd}}).

- `main_BDG2_HSC_macd` = 0.029 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_SCPstage_macd` = 0.094 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_SelfCP_macd` = 0.026 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_HSC_simple_macd` = 0.029 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 06_results.md
> All methods have their largest interval scores in the first days, when the forecaster has least history.

- **qualitative claim — evidence to be mapped manually**

### 06_results.md
> In the first week, HSC-CQR's mean coverage is {{main_BDG2_HSCCQR_cov_early}} on BDG2 and {{main_UCI_HSCCQR_cov_early}} on UCI (CQR: {{main_BDG2_CQR_cov_early}} and {{main_UCI_CQR_cov_early}}); until own scores accumulate, every strategy can only be as reliable as its population calibration.

- `main_BDG2_HSCCQR_cov_early` = 0.885 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_UCI_HSCCQR_cov_early` = 0.894 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_CQR_cov_early` = 0.892 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_UCI_CQR_cov_early` = 0.900 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 06_results.md
> Removing the shrinkage towards own scores (κ = ∞) is decisive: HSC-CQR's under-covered share rises from {{main_BDG2_HSCCQR_under_rate}} to {{main_BDG2_HSCCQR_shrink_under_rate}} on BDG2 and from {{main_UCI_HSCCQR_under_rate}} to {{main_UCI_HSCCQR_shrink_under_rate}} on UCI.

- `main_BDG2_HSCCQR_under_rate` = 3.4% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_HSCCQR_shrink_under_rate` = 21.7% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_UCI_HSCCQR_under_rate` = 0.6% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_UCI_HSCCQR_shrink_under_rate` = 12.6% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 06_results.md
> Removing the similarity prior (K = all) or the stage matching changes the MACD by less than its seed-to-seed standard deviation (BDG2: {{main_BDG2_HSCCQR_kNN_macd}} and {{main_BDG2_HSCCQR_stage_macd}} vs {{main_BDG2_HSCCQR_macd}}); the simple variant without both refinements reaches {{main_BDG2_HSCCQR_simple_macd}} on BDG2 and {{main_UCI_HSCCQR_simple_macd}} on UCI.

- `main_BDG2_HSCCQR_kNN_macd` = 0.017 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_HSCCQR_stage_macd` = 0.017 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_HSCCQR_macd` = 0.018 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_HSCCQR_simple_macd` = 0.017 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_UCI_HSCCQR_simple_macd` = 0.014 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 06_results.md
> Fixing it at one week of hourly scores (κ = 168 h, a donor–local mixture with fixed pseudo-count) gives a MACD of {{main_BDG2_HSCCQR_fixedkappa_macd}} and {{main_BDG2_HSCCQR_fixedkappa_under_rate}} under-covered buildings on BDG2 at a median interval score of {{main_BDG2_HSCCQR_fixedkappa_rel_IS}}, i.e. more reliable but marginally less sharp than the tuned HSC-CQR (paired tests: $r_{rb}$ = {{test_main_BDG2_HSCCQR_vs_HSCCQR_fixedkappa_abs_dev_r}} for the coverage deviation and {{test_main_BDG2_HSCCQR_vs_HSCCQR_fixedkappa_rel_IS_r}} for the interval score, positive values favouring the tuned va

- `main_BDG2_HSCCQR_fixedkappa_macd` = 0.015 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_HSCCQR_fixedkappa_under_rate` = 1.9% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_HSCCQR_fixedkappa_rel_IS` = 0.566 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `test_main_BDG2_HSCCQR_vs_HSCCQR_fixedkappa_abs_dev_r` = -0.45 ← results/statistics.csv (src/statistics/analysis.py::paired_tests)
- `test_main_BDG2_HSCCQR_vs_HSCCQR_fixedkappa_rel_IS_r` = 0.34 ← results/statistics.csv (src/statistics/analysis.py::paired_tests)
- `main_UCI_HSCCQR_fixedkappa_macd` = 0.013 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_UCI_HSCCQR_macd` = 0.014 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `test_main_UCI_HSCCQR_vs_HSCCQR_fixedkappa_abs_dev_p` = = 0.058 ← results/statistics.csv (src/statistics/analysis.py::paired_tests)

### 06_results.md
> Leave-one-building-out tuning on the interval score selected κ values of {{tuned_BDG2_kappa_simple}} h for the simple variant on BDG2 and {{tuned_UCI_kappa_simple}} h on UCI (across seeds); the tuning objective rewards sharpness as well as coverage (see the sensitivity analysis below).

- `tuned_BDG2_kappa_simple` = 336 ← results/run_info.json
- `tuned_UCI_kappa_simple` = 168, 336, 672 ← results/run_info.json

### 06_results.md
> Table [-@tbl:robust] and Fig. [-@fig:robust] stress the strategies on BDG2.

- **qualitative claim — evidence to be mapped manually**

### 06_results.md
> With 15 % meter noise on the new buildings, pooled calibration from clean calibration buildings breaks down (SCP-stage: {{rob_noise15_SCPstage_under_rate}} under-covered; CQR: {{rob_noise15_CQR_under_rate}}), whereas HSC-CQR leaves {{rob_noise15_HSCCQR_under_rate}} under-covered because the building's own, noisy scores enter the mixture.

- `rob_noise15_SCPstage_under_rate` = 100.0% ← results/seed_level_metrics.csv, exp=robust
- `rob_noise15_CQR_under_rate` = 30.7% ← results/seed_level_metrics.csv, exp=robust
- `rob_noise15_HSCCQR_under_rate` = 1.7% ← results/seed_level_metrics.csv, exp=robust

### 06_results.md
> Missing data (up to 40 % of hours) mainly delays adaptation (HSC-CQR {{rob_missing40_HSCCQR_under_rate}} vs CQR {{rob_missing40_CQR_under_rate}}).

- `rob_missing40_HSCCQR_under_rate` = 5.4% ← results/seed_level_metrics.csv, exp=robust
- `rob_missing40_CQR_under_rate` = 16.9% ← results/seed_level_metrics.csv, exp=robust

### 06_results.md
> Abrupt level changes of ±40 % at day 28 degrade every strategy, because pre-change scores remain in the calibration, but the shrinkage strategies least: with the downward shift HSC-CQR leaves {{rob_shift-40_HSCCQR_under_rate}} of the buildings under-covered (QShrink-CQR {{rob_shift-40_QShrinkCQR_under_rate}}, ACI-CQR {{rob_shift-40_ACICQR_under_rate}}, CQR {{rob_shift-40_CQR_under_rate}}) and with the upward shift {{rob_shift+40_HSCCQR_under_rate}} (ACI-CQR {{rob_shift+40_ACICQR_under_rate}}, CQR {{rob_shift+40_CQR_under_rate}}).

- `rob_shift-40_HSCCQR_under_rate` = 4.2% ← results/seed_level_metrics.csv, exp=robust
- `rob_shift-40_QShrinkCQR_under_rate` = 5.9% ← results/seed_level_metrics.csv, exp=robust
- `rob_shift-40_ACICQR_under_rate` = 10.9% ← results/seed_level_metrics.csv, exp=robust
- `rob_shift-40_CQR_under_rate` = 28.6% ← results/seed_level_metrics.csv, exp=robust
- `rob_shift+40_HSCCQR_under_rate` = 6.5% ← results/seed_level_metrics.csv, exp=robust
- `rob_shift+40_ACICQR_under_rate` = 16.3% ← results/seed_level_metrics.csv, exp=robust
- `rob_shift+40_CQR_under_rate` = 30.3% ← results/seed_level_metrics.csv, exp=robust

### 06_results.md
> A very small calibration pool (10 % of the calibration buildings, 16 buildings) raises HSC-CQR's under-covered share to {{rob_calpool10_HSCCQR_under_rate}} (CQR {{rob_calpool10_CQR_under_rate}}), whereas pools of 25 % and 50 % have little effect ({{rob_calpool25_HSCCQR_under_rate}} and {{rob_calpool50_HSCCQR_under_rate}}); a forecaster trained on only 10 % of the training buildings increases it to {{rob_weak-forecaster_HSCCQR_under_rate}} (CQR {{rob_weak-forecaster_CQR_under_rate}}).

- `rob_calpool10_HSCCQR_under_rate` = 7.9% ← results/seed_level_metrics.csv, exp=robust
- `rob_calpool10_CQR_under_rate` = 21.6% ← results/seed_level_metrics.csv, exp=robust
- `rob_calpool25_HSCCQR_under_rate` = 3.2% ← results/seed_level_metrics.csv, exp=robust
- `rob_calpool50_HSCCQR_under_rate` = 4.1% ← results/seed_level_metrics.csv, exp=robust
- `rob_weak-forecaster_HSCCQR_under_rate` = 5.4% ← results/seed_level_metrics.csv, exp=robust
- `rob_weak-forecaster_CQR_under_rate` = 25.0% ← results/seed_level_metrics.csv, exp=robust

### 06_results.md
> HSC-CQR's MACD is {{lso_BDG2_HSCCQR_macd}} (CQR {{lso_BDG2_CQR_macd}}; QShrink-CQR {{lso_BDG2_QShrinkCQR_macd}}), with {{lso_BDG2_HSCCQR_under_rate}} versus {{lso_BDG2_CQR_under_rate}} of the buildings under-covered (QShrink-CQR {{lso_BDG2_QShrinkCQR_under_rate}}; HSC-CQR simple {{lso_BDG2_HSCCQR_simple_under_rate}}) (Table [-@tbl:gen], Fig. [-@fig:gen]).

- `lso_BDG2_HSCCQR_macd` = 0.020 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `lso_BDG2_CQR_macd` = 0.044 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `lso_BDG2_QShrinkCQR_macd` = 0.026 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `lso_BDG2_HSCCQR_under_rate` = 5.3% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `lso_BDG2_CQR_under_rate` = 21.8% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `lso_BDG2_QShrinkCQR_under_rate` = 4.2% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `lso_BDG2_HSCCQR_simple_under_rate` = 3.5% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 06_results.md
> With models and calibration scores from BDG2 applied to Portuguese UCI clients, CQR leaves {{xds_B2U_CQR_under_rate}} under-covered and HSC-CQR {{xds_B2U_HSCCQR_under_rate}}.

- `xds_B2U_CQR_under_rate` = 5.6% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `xds_B2U_HSCCQR_under_rate` = 0.4% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 06_results.md
> The opposite direction is much harder: a model and calibration population from UCI clients, without weather information, leave {{xds_U2B_CQR_under_rate}} of BDG2 buildings under-covered with CQR; HSC-CQR reduces this to {{xds_U2B_HSCCQR_under_rate}}, but self-only calibration does as well ({{xds_U2B_SelfCQR_under_rate}}), because a prior from a different population adds nothing — the gain under such transfer rests entirely on the building's own scores.

- `xds_U2B_CQR_under_rate` = 41.8% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `xds_U2B_HSCCQR_under_rate` = 8.7% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `xds_U2B_SelfCQR_under_rate` = 6.9% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 06_results.md
> MACD is lowest for κ of about four days to one week of hourly scores (96–168 h; BDG2 {{sens_BDG2_macd_min}}, UCI {{sens_UCI_macd_min}}), increases moderately up to two weeks and sharply towards κ = ∞ ({{sens_BDG2_macd_inf}} on BDG2), whereas the interval score is lowest for two to four weeks (336–672 h); K has little influence.

- `sens_BDG2_macd_min` = 0.015 ← results/sensitivity.csv
- `sens_UCI_macd_min` = 0.012 ← results/sensitivity.csv
- `sens_BDG2_macd_inf` = 0.037 ← results/sensitivity.csv

### 06_results.md
> Once the scores are stored, the calibration layer adds {{cost_BDG2_apply_ms}} ms per building-day and needs {{cost_BDG2_store_MB}} MB for about 170 calibration buildings; the one-off leave-one-building-out tuning takes {{cost_BDG2_tune_s}} s.

- `cost_BDG2_apply_ms` = 0.437 ← results/run_info.json
- `cost_BDG2_store_MB` = 19.8 ← results/run_info.json
- `cost_BDG2_tune_s` = 36.7 ← results/run_info.json

### 06_results.md
> Both are negligible next to training the global forecaster ({{cost_BDG2_lgb_s}} s for the three LightGBM models).

- `cost_BDG2_lgb_s` = 106 ← results/run_info.json

### 06_results.md
> {{ERROR_ANALYSIS_TEXT}} Fig. [-@fig:examples] shows two pre-specified buildings: the one at the 10th percentile and the one at the median of per-building CQR coverage.

- `ERROR_ANALYSIS_TEXT` = On BDG2 the Spearman correlation between per-building coverage and CV(RMSE) is -0.65 for CQR and -0.36 for HSC-CQR (-0.9 ← generated text (manuscript/values.py) from results/*.json/csv

### 07_discussion.md
> ## Why pooled calibration fails per building, and why shrinkage helps

- **qualitative claim — evidence to be mapped manually**

### 07_discussion.md
> A global forecaster normalised by building scale yields scores that are comparable *on average* across buildings, but not identically distributed: some buildings have regular schedules and small errors, others irregular occupancy, plug loads or weather sensitivity that the first days of data cannot reveal.

- **qualitative claim — evidence to be mapped manually**

### 07_discussion.md
> Calibration on the building's own errors alone removes this bias but replaces it with variance — with a few dozen hourly scores, the empirical 90 % quantile is a noisy estimate, which is visible in Self-CQR's first-week coverage.

- **qualitative claim — evidence to be mapped manually**

### 07_discussion.md
> The leave-one-building-out selections ({{tuned_BDG2_kappa_simple}} h on BDG2 and {{tuned_UCI_kappa_simple}} h on UCI for the simple variant) mean that a building's own errors dominate after about one to two weeks of data.

- `tuned_BDG2_kappa_simple` = 336 ← results/run_info.json
- `tuned_UCI_kappa_simple` = 168, 336, 672 ← results/run_info.json

### 07_discussion.md
> Mixing *distributions* (HSC) and shrinking *quantiles* (QShrink) behave similarly when κ and λ are tuned in the same way, with an advantage for the distribution mixture in our data; both clearly outperform strategies that adapt the queried level instead of the score distribution (ACI, TQA-B).

- **qualitative claim — evidence to be mapped manually**

### 07_discussion.md
> The GHCP-style pooling secures marginal validity across buildings by never giving the new building more weight than one reference building — a sound choice for exchangeable groups, but one that cannot correct a building whose errors are systematically larger than average.

- **qualitative claim — evidence to be mapped manually**

### 07_discussion.md
> Similarity localisation of the prior (nearest calibration buildings by load-shape descriptor) produced no measurable gain.

- **qualitative claim — evidence to be mapped manually**

### 07_discussion.md
> Stage matching was unnecessary because the forecaster is told how much history it has (history-length feature and masked lags), so its errors at different stages are already on a comparable scale after normalisation.

- **qualitative claim — evidence to be mapped manually**

### 07_discussion.md
> Operators who weight under-coverage more heavily than sharpness — for example, when intervals protect demand-response baselines — can therefore choose a pseudo-count of about one week rather than the interval-score optimum; the sensitivity analysis (Fig. [-@fig:sens]) shows that any value between about one day and two weeks performs far better than pooled calibration.

- **qualitative claim — evidence to be mapped manually**

### 07_discussion.md
> This keeps the share of buildings with clearly unreliable intervals small throughout onboarding and avoids a failure mode that pooled calibration hides — systematically under-protected baselines for the most irregular buildings, which are the ones for which settlements and alarms are most error-prone.

- **qualitative claim — evidence to be mapped manually**

### 07_discussion.md
> In the UCI→BDG2 transfer the shrinkage still removed most of the under-coverage, but it was no better than self-only calibration (Table [-@tbl:gen]). 3. **Observed weather.** BDG2 experiments use observed temperature as a stand-in for day-ahead weather forecasts, which favours point accuracy for all methods equally; the UCI and cross-dataset experiments use no weather and show the same qualitative findings. 4. **Simulated onboarding.** Onboarding dates were sampled within existing meter histories.

- **qualitative claim — evidence to be mapped manually**

### 07_discussion.md
> Real onboarding can coincide with commissioning problems or behaviour changes after enrolment, which our level-shift stress tests only approximate. 5. **Data coverage.** BDG2 consists mostly of campus buildings in North America and Europe and UCI has no metadata; residential portfolios, industrial sites and other climates remain to be tested. 6. **Abrupt changes and small pools.** Because past own scores remain in the mixture, level shifts during onboarding increase under-coverage for all strategies, although least for the shrinkage strategies (Table [-@tbl:robust]); the remaining failures of 

- **qualitative claim — evidence to be mapped manually**

### 07_discussion.md
> Recency weighting of own scores or a combination with online miscoverage control are untested remedies. 7. **Baselines.** Large pretrained probabilistic forecasters [@emami2023] were not run because of the CPU-only budget, and the GHCP and TQA baselines are adaptations of methods designed for other settings (documented in Section [-@sec:setup]). 8. **Per-building coverage is itself an estimate.** With about {{nvalid_BDG2_median}} hourly observations per building, per-building coverage carries sampling noise (MACD floor ≈ {{floor_BDG2_macd}} for independent misses, higher with autocorrelation),

- `nvalid_BDG2_median` = 1344 ← Monte Carlo from per-building n_valid (manuscript/values.py)
- `floor_BDG2_macd` = 0.0066 ← Monte Carlo from per-building n_valid (manuscript/values.py)

### 07_discussion.md
> Day-ahead prediction intervals are needed from the first days after a building is metered, and they must be reliable for each building, not just on average.

- **qualitative claim — evidence to be mapped manually**

### 07_discussion.md
> Across {{n_bdg2_plus_uci}} buildings and clients from two public datasets, pooled conformal and quantile-regression intervals left many new buildings substantially under-covered although their average coverage was close to nominal.

- `n_bdg2_plus_uci` = 1,157 ← data/processed after quality filter (src/data/datasets.py)

### 07_discussion.md
> Among the building-adaptive calibration strategies compared under one protocol — self-only calibration, adaptive conformal inference, temporal quantile adjustment, GHCP-style hierarchical pooling, quantile shrinkage and pseudo-count shrinkage of the score distribution — the latter was the most reliable: applied to conformalised quantile regression, it reduced the share of under-covered new buildings from {{main_BDG2_CQR_under_rate}} to {{main_BDG2_HSCCQR_under_rate}} on BDG2 and from {{main_UCI_CQR_under_rate}} to {{main_UCI_HSCCQR_under_rate}} on UCI with an essentially unchanged interval sco

- `main_BDG2_CQR_under_rate` = 18.7% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_HSCCQR_under_rate` = 3.4% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_UCI_CQR_under_rate` = 9.5% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_UCI_HSCCQR_under_rate` = 0.6% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
