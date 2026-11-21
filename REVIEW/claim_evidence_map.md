# Claim–evidence map (auto-generated; qualitative claims require manual evidence column)

### 01_front.md
> - Interval reliability is assessed per building during its first weeks of metering - Pooled conformal calibration leaves many newly metered buildings under-covered - Shrinking pooled scores toward each building's own errors restores reliability - Interval-score tuning is flat; tune for reliability or fix one week of scores - No method of comparable width fixes week 1; similarity priors add nothing

- **qualitative claim — evidence to be mapped manually**

### 01_front.md
> {{ABSTRACT}}

- `ABSTRACT` = Demand response, flexibility bidding and measurement-and-verification need day-ahead prediction intervals for individual ← generated text (manuscript/values.py) from results/*.json/csv

### 02_intro.md
> If the upper bound is too low for a particular building, a capacity reservation sized by it fails repeatedly, whatever the average over the portfolio.

- **qualitative claim — evidence to be mapped manually**

### 02_intro.md
> 1. **Per-building reliability over time since metering.** We apply per-unit coverage evaluation [@lin2022tqa; @shahid2026] to building onboarding — the distribution of coverage across new buildings, the share of clearly under-covered buildings, its evolution week by week since metering started and its operational meaning for capacity reservations — on {{n_bdg2_plus_uci}} buildings and clients from two countries, with every site held out in turn, cross-country transfer and stress tests. 2. **A head-to-head comparison of calibration strategies** under one forecaster, score and protocol: pooled C

- `n_bdg2_plus_uci` = 1,157 ← data/processed after quality filter (src/data/datasets.py)

### 02_intro.md
> We also report what does not work: no strategy of comparable width repairs under-coverage in the first week after metering starts, and none copes with a sharp increase in day-to-day volatility.

- **qualitative claim — evidence to be mapped manually**

### 03_related.md
> Group-level validity is addressed by Mondrian calibration [@vovk2005], conditional calibration over function classes [@gibbs2025cond], clustered calibration [@ding2023], few-shot and personalised calibration [@fisch2021; @vejling2026], hierarchical conformal prediction for new groups [@dunn2023; @lee2023hier] and its generalisation (GHCP), which uses a new group's first observations with a finite-sample guarantee [@mallick2026], and empirical-Bayes small-area conformal prediction [@bersson2024].

- **qualitative claim — evidence to be mapped manually**

### 03_related.md
> Two prior findings bear on the present question: per-site evaluation shows that average calibration can hide failing sites [@shahid2026], and quantile shrinkage gave no decisive subgroup gain in survey data [@rafe2026].

- **qualitative claim — evidence to be mapped manually**

### 03_related.md
> What is missing is evidence on *which* calibration strategy makes day-ahead **load** intervals reliable for each newly metered building — a large, heterogeneous population of units, a forecaster whose accuracy improves with history length, and a need for intervals from the first day — and on how such a strategy should be tuned.

- **qualitative claim — evidence to be mapped manually**

### 04_method.md
> Three disjoint sets of buildings are used (Section [-@sec:setup]): *training* buildings for the global forecaster, *calibration* buildings whose simulated onboarding windows provide nonconformity scores, and *target* buildings, metered in a later period, on which all methods are evaluated.

- **qualitative claim — evidence to be mapped manually**

### 04_method.md
> The normalisation makes scores of buildings of different size comparable, and therefore poolable.

- **qualitative claim — evidence to be mapped manually**

### 04_method.md
> Pooled split conformal prediction [@vovk2005; @lei2018] sets $q$ to the $\lceil(1-\alpha)(N+1)\rceil$-th smallest of the $N$ pooled calibration scores.

- **qualitative claim — evidence to be mapped manually**

### 04_method.md
> Because this objective is almost flat in $\kappa$ (Section [-@sec:results]) and does not target per-building reliability, PCS uses a **reliability-aware rule**: among the values of $\kappa$ whose LOBO interval score is within 2 % of the minimum, choose the one with the smallest LOBO coverage deviation (ties broken by the interval score).

- **qualitative claim — evidence to be mapped manually**

### 04_method.md
> **Computation and state.** Score distributions are stored as cumulative counts on a fixed grid of 4000 asinh-spaced points between $-10$ and $500$ (in units of $s$; relative spacing about 0.5 %), and the grid quantile is rounded upwards for all methods alike.

- **qualitative claim — evidence to be mapped manually**

### 05_setup.md
> We use the cleaned electricity meters, site air temperature (whose timestamps are in local time: the mean diurnal temperature peaks at 14–16 h at every site) and the primary-space-usage attribute. **UCI.** ElectricityLoadDiagrams20112014 [@trindade2015] contains 15-min consumption of {{n_uci_raw}} Portuguese electricity clients; we aggregate to hourly energy, use 2012–2014 and mask the documented daylight-saving artefacts (zero hour in March, double hour in October).

- `n_uci_raw` = 370 ← manuscript/values.py

### 05_setup.md
> **Quality rules** (identical for all methods): runs of at least 24 identical readings (outage or stuck meter) are treated as missing; gaps of at most 6 h are interpolated for use as forecast *inputs* only — interpolated and masked hours never enter a nonconformity score or an evaluation; a building is retained if at most 5 % of its hours are missing in every period used and its mean load is at least 1 kWh/h.

- **qualitative claim — evidence to be mapped manually**

### 05_setup.md
> Of {{flow_bdg2_raw}} BDG2 electricity meters at {{flow_bdg2_sites_raw}} sites, {{n_bdg2}} buildings at {{n_sites}} sites remain (the missing-data rule removes {{flow_bdg2_removed_missing}}, the load floor {{flow_bdg2_removed_floor}}); of {{n_uci_raw}} UCI clients, {{n_uci}} remain.

- `flow_bdg2_raw` = 1,578 ← manuscript/values.py
- `flow_bdg2_sites_raw` = 19 ← manuscript/values.py
- `n_bdg2` = 842 ← data/processed after quality filter (src/data/datasets.py)
- `n_sites` = 10 ← data/processed after quality filter (src/data/datasets.py)
- `flow_bdg2_removed_missing` = 732 ← manuscript/values.py
- `flow_bdg2_removed_floor` = 4 ← manuscript/values.py
- `n_uci_raw` = 370 ← manuscript/values.py
- `n_uci` = 315 ← data/processed after quality filter (src/data/datasets.py)

### 05_setup.md
> Target buildings never influence the forecaster, the calibration scores or any tuning.

- **qualitative claim — evidence to be mapped manually**

### 05_setup.md
> *Leave-one-site-out (BDG2).* Each of the {{n_sites}} sites is held out in turn as the target set; the remaining buildings are split 70/30 into training and calibration sets, with three training seeds per site (30 trained forecasters). *Cross-dataset.* Forecaster and calibration scores from one dataset are applied to the targets of the other (BDG2→UCI, UCI→BDG2) without weather features; a BDG2→BDG2 run without weather is the reference (three seeds each). *Disjoint calibration period.* To check that calibration scores from the training period do not favour building-specific methods, the forecas

- `n_sites` = 10 ← data/processed after quality filter (src/data/datasets.py)

### 05_setup.md
> When $\alpha_h$ falls to $1/(N+1)$ or below, the radius is the largest observed calibration score. **TQA-B-CQR** [@lin2022tqa]: temporal quantile adjustment ("budgeting" variant), ranking the building's exponentially decayed mean own score among the calibration buildings at the same stage. **GHCP-CQR**: the calibration step of generalised hierarchical conformal prediction [@mallick2026], giving every calibration building and the new building one group share. **QShrink-CQR**: quantile-level shrinkage ("regularised Mondrian" [@rafe2026]), $q=w\,q^{\mathrm{own}}+(1-w)\,q^{\mathrm{pool}}$ with $w=

- **qualitative claim — evidence to be mapped manually**

### 05_setup.md
> Hyper-parameters of the forecasters are conventional and identical for all methods (Supplementary Section S2); no method is tuned on target buildings.

- **qualitative claim — evidence to be mapped manually**

### 05_setup.md
> Even a perfectly calibrated building has sampling noise: with $n_b\approx1300$ hours and independent misses, its expected $|\mathrm{cov}_b-0.9|$ is {{floor_BDG2_macd}}, and positive autocorrelation of misses makes it larger.

- `floor_BDG2_macd` = 0.0066 ← Monte Carlo from per-building n_valid (manuscript/values.py)

### 05_setup.md
> For each comparison we report the building-weighted mean paired difference with a 95 % percentile bootstrap interval (2000 resamples), the median difference with its bootstrap interval, the share of buildings that are better and the matched-pairs rank-biserial correlation.

- **qualitative claim — evidence to be mapped manually**

### 05_setup.md
> Because BDG2 buildings are clustered in {{n_sites}} sites of very unequal size, BDG2 resamples whole sites, and the primary *p*-value is an exact sign-flip randomisation test in which whole sites change sign (1024 patterns, so $p\ge0.002$).

- `n_sites` = 10 ← data/processed after quality filter (src/data/datasets.py)

### 05_setup.md
> Metrics tested are $|\mathrm{cov}_b-(1-\alpha)|$ (CD), the under-covered indicator, $\mathrm{IS}_b$ and the booking-failure indicator.

- **qualitative claim — evidence to be mapped manually**

### 05_setup.md
> Results for PCS-CQR are therefore exploratory, and the planned primary comparison (HSC against the absolute-score baselines) is reported in full in Supplementary Table {{supp_T_tests}}.

- `supp_T_tests` = S23 ← manuscript/values.py

### 06_results.md
> The global LightGBM forecaster reaches a mean CV(RMSE) of {{point_BDG2_cvrmse_lgb}} on new BDG2 buildings over their first 56 forecast days (seasonal naive: {{point_BDG2_cvrmse_naive}}) and {{point_UCI_cvrmse_lgb}} on UCI clients (naive: {{point_UCI_cvrmse_naive}}).

- `point_BDG2_cvrmse_lgb` = 0.135 ← results/run_info.json
- `point_BDG2_cvrmse_naive` = 0.197 ← results/run_info.json
- `point_UCI_cvrmse_lgb` = 0.089 ← results/run_info.json
- `point_UCI_cvrmse_naive` = 0.120 ← results/run_info.json

### 06_results.md
> With pooled calibration they do not (Table [-@tbl:mainbdg2]; UCI in Supplementary Table {{supp_T_main_full_UCI}}).

- `supp_T_main_full_UCI` = S4 ← manuscript/values.py

### 06_results.md
> Conformalised quantile regression (CQR) brings the mean per-building coverage on BDG2 to {{main_BDG2_CQR_mean_cov}}.

- `main_BDG2_CQR_mean_cov` = 0.891 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 06_results.md
> Yet {{main_BDG2_CQR_under_rate}} of the new buildings are covered less than 85 % of the time, and the 10th percentile of per-building coverage is {{main_BDG2_CQR_p10_cov}}.

- `main_BDG2_CQR_under_rate` = 18.2% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_CQR_p10_cov` = 0.829 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 06_results.md
> Direct quantile regression is worse ({{main_BDG2_QRLGBM_under_rate}} under-covered), and so is pooled split conformal prediction on absolute residuals ({{main_BDG2_SCPstage_under_rate}}).

- `main_BDG2_QRLGBM_under_rate` = 41.6% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_SCPstage_under_rate` = 29.3% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 06_results.md
> The Gaussian MLP lowers the under-covered share to {{main_BDG2_MLPGauss_under_rate}} only by over-covering on average ({{main_BDG2_MLPGauss_mean_cov}}) with wider intervals.

- `main_BDG2_MLPGauss_under_rate` = 4.7% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_MLPGauss_mean_cov` = 0.927 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 06_results.md
> On UCI, CQR leaves {{main_UCI_CQR_under_rate}} of the clients under-covered.

- `main_UCI_CQR_under_rate` = 9.1% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 06_results.md
> With {{nvalid_BDG2_median}} observed hours per building and independent misses, a perfectly calibrated interval would have an expected $|\mathrm{cov}_b-0.9|$ of {{floor_BDG2_macd}}, and fewer than {{floor_BDG2_under}} of buildings would fall below 0.85.

- `nvalid_BDG2_median` = 1344 ← Monte Carlo from per-building n_valid (manuscript/values.py)
- `floor_BDG2_macd` = 0.0066 ← Monte Carlo from per-building n_valid (manuscript/values.py)
- `floor_BDG2_under` = 0.00% ← Monte Carlo from per-building n_valid (manuscript/values.py)

### 06_results.md
> For a capacity reservation sized by the upper bound, CQR produces a booking failure — the upper bound exceeded in more than 10 % of hours, twice the nominal 5 % — for {{main_BDG2_CQR_book_fail}} of the BDG2 buildings.

- `main_BDG2_CQR_book_fail` = 7.3% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 06_results.md
> **Pseudo-count shrinkage.** PCS-CQR reduces the under-covered share from {{main_BDG2_CQR_under_rate}} to {{main_BDG2_PCSCQR_under_rate}} on BDG2 and from {{main_UCI_CQR_under_rate}} to {{main_UCI_PCSCQR_under_rate}} on UCI.

- `main_BDG2_CQR_under_rate` = 18.2% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_PCSCQR_under_rate` = 1.4% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_UCI_CQR_under_rate` = 9.1% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_UCI_PCSCQR_under_rate` = 0.4% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 06_results.md
> The 10th-percentile coverage rises from {{main_BDG2_CQR_p10_cov}} to {{main_BDG2_PCSCQR_p10_cov}}, and booking failures fall from {{main_BDG2_CQR_book_fail}} to {{main_BDG2_PCSCQR_book_fail}}.

- `main_BDG2_CQR_p10_cov` = 0.829 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_PCSCQR_p10_cov` = 0.871 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_CQR_book_fail` = 7.3% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_PCSCQR_book_fail` = 2.1% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 06_results.md
> The median relative interval score is unchanged ({{main_BDG2_PCSCQR_rel_IS}} vs {{main_BDG2_CQR_rel_IS}}).

- `main_BDG2_PCSCQR_rel_IS` = 0.562 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_CQR_rel_IS` = 0.560 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 06_results.md
> The intervals are {{ratio_BDG2_pcs_vs_cqr_width}} wider in median on BDG2 and {{ratio_UCI_pcs_vs_cqr_width}} on UCI: PCS redistributes width from regular to volatile buildings rather than widening all of them.

- `ratio_BDG2_pcs_vs_cqr_width` = +2% ← manuscript/values.py
- `ratio_UCI_pcs_vs_cqr_width` = -3% ← manuscript/values.py

### 06_results.md
> PCS-CQR has a smaller coverage deviation than CQR for {{test_main_BDG2_PCSCQR_vs_CQR_abs_dev_better}} of {{test_main_BDG2_PCSCQR_vs_CQR_abs_dev_n}} buildings (site-level randomisation test, Holm-adjusted {{test_main_BDG2_PCSCQR_vs_CQR_abs_dev_p}}).

- `test_main_BDG2_PCSCQR_vs_CQR_abs_dev_better` = 87% ← results/statistics.csv (src/statistics/analysis.py::paired_tests)
- `test_main_BDG2_PCSCQR_vs_CQR_abs_dev_n` = 713 ← results/statistics.csv (src/statistics/analysis.py::paired_tests)
- `test_main_BDG2_PCSCQR_vs_CQR_abs_dev_p` = p = 0.018 ← results/statistics.csv (src/statistics/analysis.py::paired_tests)

### 06_results.md
> The under-covered share falls by {{test_main_BDG2_PCSCQR_vs_CQR_under_diff}} percentage points ({{test_main_BDG2_PCSCQR_vs_CQR_under_ci}}; {{test_main_BDG2_PCSCQR_vs_CQR_under_p}}).

- `test_main_BDG2_PCSCQR_vs_CQR_under_diff` = -15.8 ← results/statistics.csv (src/statistics/analysis.py::paired_tests)
- `test_main_BDG2_PCSCQR_vs_CQR_under_ci` = [-23.5, -7.5] ← results/statistics.csv (src/statistics/analysis.py::paired_tests)
- `test_main_BDG2_PCSCQR_vs_CQR_under_p` = p = 0.031 ← results/statistics.csv (src/statistics/analysis.py::paired_tests)

### 06_results.md
> The interval-score difference is negligible ({{test_main_BDG2_PCSCQR_vs_CQR_rel_IS_diff}}; {{test_main_BDG2_PCSCQR_vs_CQR_rel_IS_p}}).

- `test_main_BDG2_PCSCQR_vs_CQR_rel_IS_diff` = -0.0016 ← results/statistics.csv (src/statistics/analysis.py::paired_tests)
- `test_main_BDG2_PCSCQR_vs_CQR_rel_IS_p` = p = 1.000 ← results/statistics.csv (src/statistics/analysis.py::paired_tests)

### 06_results.md
> The booking-failure reduction is large but, with ten sites, not significant after Holm adjustment ({{test_main_BDG2_PCSCQR_vs_CQR_book_fail_p}}).

- `test_main_BDG2_PCSCQR_vs_CQR_book_fail_p` = p = 0.070 ← results/statistics.csv (src/statistics/analysis.py::paired_tests)

### 06_results.md
> - *Self-only calibration* (Self-CQR) leaves {{main_BDG2_SelfCQR_under_rate}} of BDG2 buildings under-covered and has a higher interval score ({{test_main_BDG2_PCSCQR_vs_SelfCQR_rel_IS_p}} in favour of PCS-CQR).

- `main_BDG2_SelfCQR_under_rate` = 7.6% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `test_main_BDG2_PCSCQR_vs_SelfCQR_rel_IS_p` = p = 0.018 ← results/statistics.csv (src/statistics/analysis.py::paired_tests)

### 06_results.md
> Its quantiles from a few own scores are noisy, and in the first week it is the worst CQR-score strategy (Section [-@sec:dynamics]). - *ACI* with its step size tuned for the interval score (ACI-CQR) or by the reliability-aware rule (ACI-CQR (MACD)) leaves {{main_BDG2_ACICQR_under_rate}} and {{main_BDG2_ACICQR_MACD_under_rate}} of buildings under-covered.

- `main_BDG2_ACICQR_under_rate` = 8.7% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_ACICQR_MACD_under_rate` = 4.2% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 06_results.md
> Tuned for coverage alone, ACI is the most reliable strategy in the study (MACD {{main_BDG2_ACICQR_coverage_only_macd}}, no under-covered building).

- `main_BDG2_ACICQR_coverage_only_macd` = 0.004 ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 06_results.md
> The price is intervals {{ratio_BDG2_acicov_vs_pcs_width}} times as wide as PCS-CQR's on BDG2 ({{ratio_UCI_acicov_vs_pcs_width}} on UCI) and a reserve cost of {{main_BDG2_ACICQR_coverage_only_reserve_cost}} instead of {{main_BDG2_PCSCQR_reserve_cost}} of mean load.

- `ratio_BDG2_acicov_vs_pcs_width` = 2.4 ← manuscript/values.py
- `ratio_UCI_acicov_vs_pcs_width` = 1.2 ← manuscript/values.py
- `main_BDG2_ACICQR_coverage_only_reserve_cost` = 4.4% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_PCSCQR_reserve_cost` = 2.1% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 06_results.md
> It always selected the largest step size in the grid ($\gamma$ = {{tuned_BDG2_aci_cov}}). - *TQA-B* and *GHCP* stay close to pooled CQR ({{main_BDG2_TQABCQR_under_rate}} and {{main_BDG2_GHCPCQR_under_rate}}).

- `tuned_BDG2_aci_cov` = 0.01 ← results/run_info.json
- `main_BDG2_TQABCQR_under_rate` = 17.3% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_GHCPCQR_under_rate` = 17.2% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 06_results.md
> TQA-B bounds the quantile adjustment by design, and GHCP never gives the new building more weight than one calibration building.

- **qualitative claim — evidence to be mapped manually**

### 06_results.md
> **Quantile-level shrinkage.** Tuned by the same reliability-aware rule, QShrink-CQR (MACD) is statistically indistinguishable from PCS-CQR in coverage deviation ({{test_main_BDG2_PCSCQR_vs_QShrinkCQR_MACD_abs_dev_p}}) and under-covered share ({{test_main_BDG2_PCSCQR_vs_QShrinkCQR_MACD_under_p}}).

- `test_main_BDG2_PCSCQR_vs_QShrinkCQR_MACD_abs_dev_p` = p = 0.600 ← results/statistics.csv (src/statistics/analysis.py::paired_tests)
- `test_main_BDG2_PCSCQR_vs_QShrinkCQR_MACD_under_p` = p = 0.875 ← results/statistics.csv (src/statistics/analysis.py::paired_tests)

### 06_results.md
> PCS-CQR has a slightly lower interval score on BDG2 ({{test_main_BDG2_PCSCQR_vs_QShrinkCQR_MACD_rel_IS_diff}}; {{test_main_BDG2_PCSCQR_vs_QShrinkCQR_MACD_rel_IS_p}}), but not on UCI.

- `test_main_BDG2_PCSCQR_vs_QShrinkCQR_MACD_rel_IS_diff` = -0.0085 ← results/statistics.csv (src/statistics/analysis.py::paired_tests)
- `test_main_BDG2_PCSCQR_vs_QShrinkCQR_MACD_rel_IS_p` = p = 0.041 ← results/statistics.csv (src/statistics/analysis.py::paired_tests)

### 06_results.md
> On the MLP quantile model it reduces the under-covered share from {{main_BDG2_CQR_MLP_under_rate}} (CQR) to {{main_BDG2_PCSCQR_MLP_under_rate}} on BDG2 and from {{main_UCI_CQR_MLP_under_rate}} to {{main_UCI_PCSCQR_MLP_under_rate}} on UCI.

- `main_BDG2_CQR_MLP_under_rate` = 15.7% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_PCSCQR_MLP_under_rate` = 1.8% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_UCI_CQR_MLP_under_rate` = 8.2% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_UCI_PCSCQR_MLP_under_rate` = 0.8% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 06_results.md
> On absolute residuals, PCS reduces the under-covered share from {{main_BDG2_SCPstage_under_rate}} (SCP-stage) to {{main_BDG2_PCS_under_rate}}, but there it does no better than self-only calibration (Self-CP: {{main_BDG2_SelfCP_under_rate}}; Supplementary Table {{supp_T_main_full_BDG2}}).

- `main_BDG2_SCPstage_under_rate` = 29.3% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_PCS_under_rate` = 6.0% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_SelfCP_under_rate` = 6.1% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `supp_T_main_full_BDG2` = S3 ← manuscript/values.py

### 06_results.md
> Figure [-@fig:tradeoff] places all methods on the reliability–sharpness–cost plane.

- **qualitative claim — evidence to be mapped manually**

### 06_results.md
> Across finite $\kappa>0$ its leave-one-building-out (LOBO) value on calibration buildings varies by only {{tune_BDG2_is_range_pct}} % (BDG2; UCI {{tune_UCI_is_range_pct}} %), and dropping the building's own scores altogether ($\kappa=\infty$) raises it by only {{tune_BDG2_inf_vs_best}} % (median over runs; Supplementary Table {{supp_T_tuning_curves}}).

- `tune_BDG2_is_range_pct` = 1.2 ← manuscript/values.py
- `tune_UCI_is_range_pct` = 1.1 ← manuscript/values.py
- `tune_BDG2_inf_vs_best` = 0.9 ← manuscript/values.py
- `supp_T_tuning_curves` = S20 ← manuscript/values.py

### 06_results.md
> The median relative interval score stays within {{sens_BDG2_is_range}} on BDG2 for every finite $\kappa$, while MACD ranges over {{sens_BDG2_macd_range}} with its minimum at $\kappa$ = {{sens_BDG2_kappa_best}}, and reaches {{sens_BDG2_macd_inf}} at $\kappa=\infty$.

- `sens_BDG2_is_range` = 0.561–0.569 ← results/sensitivity.csv
- `sens_BDG2_macd_range` = 0.015–0.027 ← results/sensitivity.csv
- `sens_BDG2_kappa_best` = 168 ← results/sensitivity.csv
- `sens_BDG2_macd_inf` = 0.039 ← results/sensitivity.csv

### 06_results.md
> The pre-registered interval-score rule mostly selected $\kappa$ = 336 and left {{main_BDG2_PCSCQR_IStuned_under_rate}} of BDG2 buildings under-covered (PCS-CQR (IS-tuned)).

- `main_BDG2_PCSCQR_IStuned_under_rate` = 2.9% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 06_results.md
> The reliability-aware rule selected $\kappa\in\{${{tuned_BDG2_pcs}}$\}$ on BDG2 and $\{${{tuned_UCI_pcs}}$\}$ on UCI and halved that share ({{main_BDG2_PCSCQR_under_rate}}).

- `tuned_BDG2_pcs` = 96, 168 ← results/run_info.json
- `tuned_UCI_pcs` = 48, 96, 168 ← results/run_info.json
- `main_BDG2_PCSCQR_under_rate` = 1.4% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 06_results.md
> The coverage-deviation difference is significant on BDG2 ({{test_main_BDG2_PCSCQR_vs_PCSCQR_IStuned_abs_dev_p}}), but the difference in the under-covered share is not ({{test_main_BDG2_PCSCQR_vs_PCSCQR_IStuned_under_p}}).

- `test_main_BDG2_PCSCQR_vs_PCSCQR_IStuned_abs_dev_p` = p = 0.014 ← results/statistics.csv (src/statistics/analysis.py::paired_tests)
- `test_main_BDG2_PCSCQR_vs_PCSCQR_IStuned_under_p` = p = 0.164 ← results/statistics.csv (src/statistics/analysis.py::paired_tests)

### 06_results.md
> A fixed one-week pseudo-count, chosen without any data, performs as well as the tuned one: PCS-CQR κ=168 leaves {{main_BDG2_PCSCQR_kappa168_under_rate}} of BDG2 and {{main_UCI_PCSCQR_kappa168_under_rate}} of UCI buildings under-covered (paired test vs PCS-CQR: {{test_main_BDG2_PCSCQR_vs_PCSCQR_kappa168_abs_dev_p}}).

- `main_BDG2_PCSCQR_kappa168_under_rate` = 1.5% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_UCI_PCSCQR_kappa168_under_rate` = 0.8% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `test_main_BDG2_PCSCQR_vs_PCSCQR_kappa168_abs_dev_p` = p = 1.000 ← results/statistics.csv (src/statistics/analysis.py::paired_tests)

### 06_results.md
> Selecting $\kappa$ by leave-*site*-out instead of leave-building-out changes nothing ({{main_BDG2_PCSCQR_sitegrouped_under_rate}}).

- `main_BDG2_PCSCQR_sitegrouped_under_rate` = 1.5% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 06_results.md
> The same holds for quantile shrinkage (QShrink-CQR λ=168: {{main_BDG2_QShrinkCQR_lambda168_under_rate}}), whose interval-score-tuned version selected large $\lambda$ and is less reliable ({{main_BDG2_QShrinkCQR_under_rate}}).

- `main_BDG2_QShrinkCQR_lambda168_under_rate` = 1.2% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_QShrinkCQR_under_rate` = 4.3% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 06_results.md
> The refinements of the pre-registered design add nothing on the CQR score (Supplementary Table {{supp_T_ablation}}):

- `supp_T_ablation` = S6 ← manuscript/values.py

### 06_results.md
> - *Onboarding-stage matching of the prior* leaves MACD and the under-covered share unchanged (PCS-CQR +stage: {{main_BDG2_PCSCQR_stage_under_rate}}; dashed lines in Fig. [-@fig:sens]). - *A similarity-localised prior* slightly increases under-coverage (PCS-CQR +kNN: {{main_BDG2_PCSCQR_kNN_under_rate}}; +kNN+stage: {{main_BDG2_PCSCQR_kNNstage_under_rate}}). - *The pre-registered HSC-CQR*, which combines both refinements with interval-score tuning, is less reliable than PCS-CQR ({{main_BDG2_HSCCQR_under_rate}}; coverage deviation {{test_main_BDG2_PCSCQR_vs_HSCCQR_abs_dev_p}}).

- `main_BDG2_PCSCQR_stage_under_rate` = 1.4% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_PCSCQR_kNN_under_rate` = 1.8% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_PCSCQR_kNNstage_under_rate` = 1.8% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_HSCCQR_under_rate` = 3.4% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `test_main_BDG2_PCSCQR_vs_HSCCQR_abs_dev_p` = p = 0.018 ← results/statistics.csv (src/statistics/analysis.py::paired_tests)

### 06_results.md
> It also has the worst first week of all shrinkage variants ({{main_BDG2_HSCCQR_under_w1}} under-covered). - *Removing the shrinkage* (κ=∞) returns pooled CQR ({{main_BDG2_PCSCQR_shrink_under_rate}}).

- `main_BDG2_HSCCQR_under_w1` = 25.2% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_PCSCQR_shrink_under_rate` = 18.5% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 06_results.md
> The planned primary comparison concerned the absolute score (Supplementary Table {{supp_T_tests}}, family "preregistered-abs").

- `supp_T_tests` = S23 ← manuscript/values.py

### 06_results.md
> - HSC has a lower interval score than every planned baseline, including self-only calibration (BDG2 {{test_main_BDG2_HSC_vs_SelfCP_rel_IS_p}}; UCI {{test_main_UCI_HSC_vs_SelfCP_rel_IS_p}}). - It does not reduce per-building miscalibration relative to Self-CP (BDG2 {{test_main_BDG2_HSC_vs_SelfCP_abs_dev_p}}; UCI {{test_main_UCI_HSC_vs_SelfCP_abs_dev_p}}). - For the absolute score, stage matching does help in the first week.

- `test_main_BDG2_HSC_vs_SelfCP_rel_IS_p` = p = 0.018 ← results/statistics.csv (src/statistics/analysis.py::paired_tests)
- `test_main_UCI_HSC_vs_SelfCP_rel_IS_p` = p < 0.001 ← results/statistics.csv (src/statistics/analysis.py::paired_tests)
- `test_main_BDG2_HSC_vs_SelfCP_abs_dev_p` = p = 0.059 ← results/statistics.csv (src/statistics/analysis.py::paired_tests)
- `test_main_UCI_HSC_vs_SelfCP_abs_dev_p` = p = 1.000 ← results/statistics.csv (src/statistics/analysis.py::paired_tests)

### 06_results.md
> Without the similarity prior, stage-matched HSC leaves {{main_BDG2_HSC_kNN_under_w1}} of BDG2 buildings under-covered in week 1, compared with {{main_BDG2_PCS_under_w1}} for PCS.

- `main_BDG2_HSC_kNN_under_w1` = 14.3% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_PCS_under_w1` = 18.7% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 06_results.md
> Figure [-@fig:stage] follows coverage and interval score by days since metering, and Supplementary Table {{supp_T_weeks}} gives the under-covered share per week.

- `supp_T_weeks` = S5 ← manuscript/values.py

### 06_results.md
> The first week is hard for every strategy.

- **qualitative claim — evidence to be mapped manually**

### 06_results.md
> On BDG2, {{main_BDG2_CQR_under_w1}} of buildings are under-covered within week 1 with CQR and {{main_BDG2_PCSCQR_under_w1}} with PCS-CQR.

- `main_BDG2_CQR_under_w1` = 24.2% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_PCSCQR_under_w1` = 19.4% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 06_results.md
> Self-CQR is worst at {{main_BDG2_SelfCQR_under_w1}}.

- `main_BDG2_SelfCQR_under_w1` = 33.8% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 06_results.md
> With independent misses, sampling noise alone would put only {{floor_w1_under}} of 168-hour windows below 0.85.

- `floor_w1_under` = 1.7% ← Monte Carlo from per-building n_valid (manuscript/values.py)

### 06_results.md
> The first-week failures are real, and no strategy of comparable width repairs them.

- **qualitative claim — evidence to be mapped manually**

### 06_results.md
> Coverage-only ACI reduces them to {{main_BDG2_ACICQR_coverage_only_under_w1}}, but with intervals {{ratio_BDG2_acicov_vs_pcs_width}} times as wide.

- `main_BDG2_ACICQR_coverage_only_under_w1` = 8.9% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `ratio_BDG2_acicov_vs_pcs_width` = 2.4 ← manuscript/values.py

### 06_results.md
> In weeks 5–8 the under-covered share is {{main_BDG2_PCSCQR_under_w58}} versus {{main_BDG2_CQR_under_w58}} on BDG2, and {{main_UCI_PCSCQR_under_w58}} versus {{main_UCI_CQR_under_w58}} on UCI.

- `main_BDG2_PCSCQR_under_w58` = 11.0% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_CQR_under_w58` = 20.7% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_UCI_PCSCQR_under_w58` = 4.4% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_UCI_CQR_under_w58` = 11.4% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 06_results.md
> In the first days, the interval score falls steeply for all strategies as the forecaster's features fill (Fig. [-@fig:stage]c, d).

- **qualitative claim — evidence to be mapped manually**

### 06_results.md
> ## Generalisation, other nominal levels and stress {#sec:robust}

- **qualitative claim — evidence to be mapped manually**

### 06_results.md
> MACD, interval scores and paired tests for every condition are given in Supplementary Tables {{supp_T_lso}}–{{supp_T_pools}} and {{supp_T_tests}}.

- `supp_T_lso` = S11 ← manuscript/values.py
- `supp_T_pools` = S18 ← manuscript/values.py
- `supp_T_tests` = S23 ← manuscript/values.py

### 06_results.md
> - *Leave-one-site-out.* With every BDG2 site held out in turn, PCS-CQR leaves {{lso_BDG2_PCSCQR_under_rate}} of buildings under-covered, against {{lso_BDG2_CQR_under_rate}} for CQR ({{test_lso_BDG2_PCSCQR_vs_CQR_under_p}}) and {{lso_BDG2_SelfCQR_under_rate}} for Self-CQR ({{test_lso_BDG2_PCSCQR_vs_SelfCQR_under_p}}).

- `lso_BDG2_PCSCQR_under_rate` = 2.4% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `lso_BDG2_CQR_under_rate` = 24.8% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `test_lso_BDG2_PCSCQR_vs_CQR_under_p` = p = 0.043 ← results/statistics.csv (src/statistics/analysis.py::paired_tests)
- `lso_BDG2_SelfCQR_under_rate` = 7.1% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `test_lso_BDG2_PCSCQR_vs_SelfCQR_under_p` = p = 0.023 ← results/statistics.csv (src/statistics/analysis.py::paired_tests)

### 06_results.md
> It stays below 5 % at every one of the ten sites, including the two where pooled CQR fails for half or more of the buildings (Supplementary Table {{supp_T_lso_sites}}). - *Cross-dataset.* When forecaster and calibration scores come from Portuguese clients and the targets are North American and European campus buildings (UCI → BDG2), pooled CQR fails for {{xds_U2B_CQR_under_rate}} of buildings.

- `supp_T_lso_sites` = S12 ← manuscript/values.py
- `xds_U2B_CQR_under_rate` = 41.9% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 06_results.md
> PCS-CQR fails for {{xds_U2B_PCSCQR_under_rate}} ({{test_xds_U2B_BDG2_PCSCQR_vs_CQR_under_p}}), because the building's own scores take over from the mismatched prior. - *Disjoint calibration period.* Calibrating on a period disjoint from the forecaster's training period leaves the picture unchanged (PCS-CQR {{rob_disjointmcalmperiod_PCSCQR_under_rate}}, CQR {{rob_disjointmcalmperiod_CQR_under_rate}}).

- `xds_U2B_PCSCQR_under_rate` = 4.2% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `test_xds_U2B_BDG2_PCSCQR_vs_CQR_under_p` = p = 0.043 ← results/statistics.csv (src/statistics/analysis.py::paired_tests)
- `rob_disjointmcalmperiod_PCSCQR_under_rate` = 1.8% ← results/seed_level_metrics.csv, exp=robust
- `rob_disjointmcalmperiod_CQR_under_rate` = 18.4% ← results/seed_level_metrics.csv, exp=robust

### 06_results.md
> **Other nominal levels.** At 95 %, PCS-CQR leaves {{main_BDG2_a5_PCSCQR_under_rate}} of BDG2 buildings below 90 % coverage, against {{main_BDG2_a5_CQR_under_rate}} for CQR.

- `main_BDG2_a5_PCSCQR_under_rate` = 0.3% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_a5_CQR_under_rate` = 14.7% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 06_results.md
> At 80 % the shares below 75 % are {{main_BDG2_a20_PCSCQR_under_rate}} and {{main_BDG2_a20_CQR_under_rate}} (Supplementary Tables {{supp_T_a5_BDG2}}–{{supp_T_a20_UCI}}).

- `main_BDG2_a20_PCSCQR_under_rate` = 6.3% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_BDG2_a20_CQR_under_rate` = 16.6% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `supp_T_a5_BDG2` = S7 ← manuscript/values.py
- `supp_T_a20_UCI` = S10 ← manuscript/values.py

### 06_results.md
> Here PCS-CQR, its fixed-κ version and QShrink-CQR (MACD) stay at or below about 4 % under-covered, while pooled strategies reach 17–30 %. - *Self-CQR is as reliable or more* when meter noise is added to history and truth ({{rob_noise15_SelfCQR_under_rate}} vs {{rob_noise15_PCSCQR_under_rate}}, {{test_rob_noise15_BDG2_PCSCQR_vs_SelfCQR_under_p}}) and after an early level shift.

- `rob_noise15_SelfCQR_under_rate` = 0.1% ← results/seed_level_metrics.csv, exp=robust
- `rob_noise15_PCSCQR_under_rate` = 0.4% ← results/seed_level_metrics.csv, exp=robust
- `test_rob_noise15_BDG2_PCSCQR_vs_SelfCQR_under_p` = p = 1.000 ← results/statistics.csv (src/statistics/analysis.py::paired_tests)

### 06_results.md
> In both cases the pooled prior no longer describes the building. - *Day-to-day volatility* defeats every strategy: random daily load factors with 25 % standard deviation from day 28 leave {{rob_volatility25_PCSCQR_under_rate}} of buildings under-covered with PCS-CQR and {{rob_volatility25_SelfCQR_under_rate}} with Self-CQR ({{test_rob_volatility25_BDG2_PCSCQR_vs_SelfCQR_under_p}}).

- `rob_volatility25_PCSCQR_under_rate` = 84.8% ← results/seed_level_metrics.csv, exp=robust
- `rob_volatility25_SelfCQR_under_rate` = 75.8% ← results/seed_level_metrics.csv, exp=robust
- `test_rob_volatility25_BDG2_PCSCQR_vs_SelfCQR_under_p` = p = 0.020 ← results/statistics.csv (src/statistics/analysis.py::paired_tests)

### 06_results.md
> Four weeks of own scores cannot anticipate an unpredictable change of this size, and a larger pseudo-count slows the adaptation further. - *Small calibration pools.* With only 5 calibration buildings the tuned layer leaves {{pools_n5_PCSCQR_under_rate}} under-covered and the fixed one-week pseudo-count {{pools_n5_PCSCQR_kappa168_under_rate}}, compared with {{pools_n5_CQR_under_rate}} for CQR.

- `pools_n5_PCSCQR_under_rate` = 2.7% ← manuscript/values.py
- `pools_n5_PCSCQR_kappa168_under_rate` = 1.7% ← manuscript/values.py
- `pools_n5_CQR_under_rate` = 16.6% ← manuscript/values.py

### 06_results.md
> GHCP-CQR with 5 calibration buildings frequently returns unbounded intervals (Supplementary Table {{supp_T_pools}}).

- `supp_T_pools` = S18 ← manuscript/values.py

### 06_results.md
> {{ERROR_ANALYSIS_TEXT}}

- `ERROR_ANALYSIS_TEXT` = On BDG2 the Spearman correlation between per-building coverage and CV(RMSE) is -0.67 for CQR and -0.20 for PCS-CQR, i.e. ← generated text (manuscript/values.py) from results/*.json/csv

### 06_results.md
> The layer is cheap (Supplementary Table {{supp_T_cost}}):

- `supp_T_cost` = S21 ← manuscript/values.py

### 06_results.md
> - The daily update of one building — adding 24 scores and recomputing one quantile — takes {{lat_single_ms}} ms on one CPU core. - Batch-updating 10 000 buildings takes {{lat_batch10k_s}} s. - The per-building state is {{lat_state_kB}} kB as implemented. - Selecting $\kappa$ by LOBO takes {{cost_BDG2_pcs_tune_s}} s on BDG2, against {{cost_BDG2_hsc_tune_s}} s for the pre-registered similarity-localised design. - Training the three LightGBM quantile models takes {{cost_BDG2_lgb_s}} s.

- `lat_single_ms` = 0.023 ← manuscript/values.py
- `lat_batch10k_s` = 0.3 ← manuscript/values.py
- `lat_state_kB` = 16 ← manuscript/values.py
- `cost_BDG2_pcs_tune_s` = 1.1 ← results/run_info.json
- `cost_BDG2_hsc_tune_s` = 29.1 ← results/run_info.json
- `cost_BDG2_lgb_s` = 107 ← results/run_info.json

### 07_discussion.md
> ## Why pooled calibration fails per building, and what shrinkage changes

- **qualitative claim — evidence to be mapped manually**

### 07_discussion.md
> **Why pooling fails.** A global forecaster normalised by building scale yields scores that are comparable *on average* across buildings but not identically distributed.

- **qualitative claim — evidence to be mapped manually**

### 07_discussion.md
> - ACI with a step size tuned for sharpness changes the level too slowly. - ACI tuned for coverage alone reaches near-perfect per-building coverage only by inflating the intervals. - TQA-B bounds its adjustment by design. - GHCP-style pooling secures marginal validity across buildings by never giving the new building more weight than one reference building.

- **qualitative claim — evidence to be mapped manually**

### 07_discussion.md
> We find the same at building level, and the result persists under site hold-out, where pooled CQR fails for half or more of the buildings at two sites. - *Quantile shrinkage.* Rafe and Das [@rafe2026] reported no decisive subgroup gain from quantile shrinkage in survey data.

- **qualitative claim — evidence to be mapped manually**

### 07_discussion.md
> Here the same mechanism gives a decisive gain over pooled calibration.

- **qualitative claim — evidence to be mapped manually**

### 07_discussion.md
> The usage-based Mondrian baseline fails for the same reason. - *Onboarding-stage matching.* Unnecessary for CQR scores, because the quantile models already widen when little history is available.

- **qualitative claim — evidence to be mapped manually**

### 07_discussion.md
> On absolute residuals, stage matching did improve the first week, so the value of this refinement depends on the score.

- **qualitative claim — evidence to be mapped manually**

### 07_discussion.md
> This keeps the share of buildings with clearly unreliable intervals small after the first week.

- **qualitative claim — evidence to be mapped manually**

### 07_discussion.md
> It avoids a failure mode that pooled calibration hides: systematically under-protected capacity reservations and baselines for the most irregular buildings, which are the ones where settlements and alarms are most error-prone.

- **qualitative claim — evidence to be mapped manually**

### 07_discussion.md
> - *The first week remains unreliable.* About one in five BDG2 buildings is under-covered with every strategy of comparable width.

- **qualitative claim — evidence to be mapped manually**

### 07_discussion.md
> Self-only calibration was more reliable under added meter noise and an increase in volatility.

- **qualitative claim — evidence to be mapped manually**

### 07_discussion.md
> The operational metrics are stylised: booking failures and reserve cost translate the upper bound into a capacity reservation but do not model a specific market or contract. 7. **Per-building coverage is itself an estimate.** With about {{nvalid_BDG2_median}} hourly observations per building, its sampling noise (MACD ≈ {{floor_BDG2_macd}} for independent misses, more with autocorrelation) is of the same order as the differences among the best strategies.

- `nvalid_BDG2_median` = 1344 ← Monte Carlo from per-building n_valid (manuscript/values.py)
- `floor_BDG2_macd` = 0.0066 ← Monte Carlo from per-building n_valid (manuscript/values.py)

### 07_discussion.md
> Day-ahead prediction intervals are needed from the first days after a building is metered, and they must be reliable for each building, not just on average.

- **qualitative claim — evidence to be mapped manually**

### 07_discussion.md
> Across {{n_bdg2_plus_uci}} buildings and clients from two public datasets, pooled conformalised quantile regression left {{main_BDG2_CQR_under_rate}} (BDG2) and {{main_UCI_CQR_under_rate}} (UCI) of new buildings clearly under-covered although their mean coverage was close to nominal.

- `n_bdg2_plus_uci` = 1,157 ← data/processed after quality filter (src/data/datasets.py)
- `main_BDG2_CQR_under_rate` = 18.2% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_UCI_CQR_under_rate` = 9.1% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 07_discussion.md
> Shrinking the pooled score distribution toward each building's own accumulating scores reduced these shares to {{main_BDG2_PCSCQR_under_rate}} and {{main_UCI_PCSCQR_under_rate}} at an unchanged interval score.

- `main_BDG2_PCSCQR_under_rate` = 1.4% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)
- `main_UCI_PCSCQR_under_rate` = 0.4% ← results/seed_level_metrics.csv (seed-level aggregates of results/raw_results.csv)

### 07_discussion.md
> No strategy of comparable width made the first week reliable, and none coped with a sharp increase in day-to-day volatility.

- **qualitative claim — evidence to be mapped manually**
