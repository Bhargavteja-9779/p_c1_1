# Results {#sec:results}

## The reliability problem

The global LightGBM forecaster reaches a mean CV(RMSE) of {{point_BDG2_cvrmse_lgb}} on new BDG2 buildings over their first 56 forecast days (seasonal naive: {{point_BDG2_cvrmse_naive}}) and {{point_UCI_cvrmse_lgb}} on UCI clients (naive: {{point_UCI_cvrmse_naive}}). The point forecasts are therefore reasonable. The question is whether their intervals hold building by building.

With pooled calibration they do not (Table [-@tbl:mainbdg2]; UCI in Supplementary Table {{supp_T_main_full_UCI}}). Conformalised quantile regression (CQR) brings the mean per-building coverage on BDG2 to {{main_BDG2_CQR_mean_cov}}. Yet {{main_BDG2_CQR_under_rate}} of the new buildings are covered less than 85 % of the time, and the 10th percentile of per-building coverage is {{main_BDG2_CQR_p10_cov}}. Direct quantile regression is worse ({{main_BDG2_QRLGBM_under_rate}} under-covered), and so is pooled split conformal prediction on absolute residuals ({{main_BDG2_SCPstage_under_rate}}). The Gaussian MLP lowers the under-covered share to {{main_BDG2_MLPGauss_under_rate}} only by over-covering on average ({{main_BDG2_MLPGauss_mean_cov}}) with wider intervals. On UCI, CQR leaves {{main_UCI_CQR_under_rate}} of the clients under-covered.

These are not sampling artefacts. With {{nvalid_BDG2_median}} observed hours per building and independent misses, a perfectly calibrated interval would have an expected $|\mathrm{cov}_b-0.9|$ of {{floor_BDG2_macd}}, and fewer than {{floor_BDG2_under}} of buildings would fall below 0.85. The observed under-coverage is therefore a systematic, building-specific error.

For a capacity reservation sized by the upper bound, CQR produces a booking failure — the upper bound exceeded in more than 10 % of hours, twice the nominal 5 % — for {{main_BDG2_CQR_book_fail}} of the BDG2 buildings.

<<TABLE:MS_main_BDG2|tbl:mainbdg2>>

## Comparison of calibration strategies

All strategies in Table [-@tbl:mainbdg2] above CQR use the same quantile models and the same CQR scores. They differ only in how a new building's own scores enter the calibration.

**Pseudo-count shrinkage.** PCS-CQR reduces the under-covered share from {{main_BDG2_CQR_under_rate}} to {{main_BDG2_PCSCQR_under_rate}} on BDG2 and from {{main_UCI_CQR_under_rate}} to {{main_UCI_PCSCQR_under_rate}} on UCI. The 10th-percentile coverage rises from {{main_BDG2_CQR_p10_cov}} to {{main_BDG2_PCSCQR_p10_cov}}, and booking failures fall from {{main_BDG2_CQR_book_fail}} to {{main_BDG2_PCSCQR_book_fail}}. The median relative interval score is unchanged ({{main_BDG2_PCSCQR_rel_IS}} vs {{main_BDG2_CQR_rel_IS}}). The intervals are {{ratio_BDG2_pcs_vs_cqr_width}} wider in median on BDG2 and {{ratio_UCI_pcs_vs_cqr_width}} on UCI: PCS redistributes width from regular to volatile buildings rather than widening all of them.

The paired tests (Table [-@tbl:tests]) confirm these gains on BDG2. PCS-CQR has a smaller coverage deviation than CQR for {{test_main_BDG2_PCSCQR_vs_CQR_abs_dev_better}} of {{test_main_BDG2_PCSCQR_vs_CQR_abs_dev_n}} buildings (site-level randomisation test, Holm-adjusted {{test_main_BDG2_PCSCQR_vs_CQR_abs_dev_p}}). The under-covered share falls by {{test_main_BDG2_PCSCQR_vs_CQR_under_diff}} percentage points ({{test_main_BDG2_PCSCQR_vs_CQR_under_ci}}; {{test_main_BDG2_PCSCQR_vs_CQR_under_p}}). The interval-score difference is negligible ({{test_main_BDG2_PCSCQR_vs_CQR_rel_IS_diff}}; {{test_main_BDG2_PCSCQR_vs_CQR_rel_IS_p}}). The booking-failure reduction is large but, with ten sites, not significant after Holm adjustment ({{test_main_BDG2_PCSCQR_vs_CQR_book_fail_p}}).

**Other strategies.**

- *Self-only calibration* (Self-CQR) leaves {{main_BDG2_SelfCQR_under_rate}} of BDG2 buildings under-covered and has a higher interval score ({{test_main_BDG2_PCSCQR_vs_SelfCQR_rel_IS_p}} in favour of PCS-CQR). Its quantiles from a few own scores are noisy, and in the first week it is the worst CQR-score strategy (Section [-@sec:dynamics]).
- *ACI* with its step size tuned for the interval score (ACI-CQR) or by the reliability-aware rule (ACI-CQR (MACD)) leaves {{main_BDG2_ACICQR_under_rate}} and {{main_BDG2_ACICQR_MACD_under_rate}} of buildings under-covered. Tuned for coverage alone, ACI is the most reliable strategy in the study (MACD {{main_BDG2_ACICQR_coverage_only_macd}}, no under-covered building). The price is intervals {{ratio_BDG2_acicov_vs_pcs_width}} times as wide as PCS-CQR's on BDG2 ({{ratio_UCI_acicov_vs_pcs_width}} on UCI) and a reserve cost of {{main_BDG2_ACICQR_coverage_only_reserve_cost}} instead of {{main_BDG2_PCSCQR_reserve_cost}} of mean load. It always selected the largest step size in the grid ($\gamma$ = {{tuned_BDG2_aci_cov}}).
- *TQA-B* and *GHCP* stay close to pooled CQR ({{main_BDG2_TQABCQR_under_rate}} and {{main_BDG2_GHCPCQR_under_rate}}). TQA-B bounds the quantile adjustment by design, and GHCP never gives the new building more weight than one calibration building. That weighting protects marginal validity across buildings but cannot correct a building whose errors are systematically larger than average.

**Quantile-level shrinkage.** Tuned by the same reliability-aware rule, QShrink-CQR (MACD) is statistically indistinguishable from PCS-CQR in coverage deviation ({{test_main_BDG2_PCSCQR_vs_QShrinkCQR_MACD_abs_dev_p}}) and under-covered share ({{test_main_BDG2_PCSCQR_vs_QShrinkCQR_MACD_under_p}}). PCS-CQR has a slightly lower interval score on BDG2 ({{test_main_BDG2_PCSCQR_vs_QShrinkCQR_MACD_rel_IS_diff}}; {{test_main_BDG2_PCSCQR_vs_QShrinkCQR_MACD_rel_IS_p}}), but not on UCI. Shrinking the score distribution and shrinking the quantile are therefore practically equivalent here.

**Other forecasters and the absolute score.** The layer is not specific to LightGBM. On the MLP quantile model it reduces the under-covered share from {{main_BDG2_CQR_MLP_under_rate}} (CQR) to {{main_BDG2_PCSCQR_MLP_under_rate}} on BDG2 and from {{main_UCI_CQR_MLP_under_rate}} to {{main_UCI_PCSCQR_MLP_under_rate}} on UCI. On absolute residuals, PCS reduces the under-covered share from {{main_BDG2_SCPstage_under_rate}} (SCP-stage) to {{main_BDG2_PCS_under_rate}}, but there it does no better than self-only calibration (Self-CP: {{main_BDG2_SelfCP_under_rate}}; Supplementary Table {{supp_T_main_full_BDG2}}).

Figure [-@fig:tradeoff] places all methods on the reliability–sharpness–cost plane. The CQR-score shrinkage strategies are the only ones that are both reliable and as sharp as pooled CQR.

<<TABLE:MS_tests|tbl:tests>>

![Reliability (a, MACD), sharpness (b, median relative interval score) and reserve cost (c, pinball loss of the upper bound in % of mean load) of all interval methods on BDG2 and UCI (random-building protocol, nominal 90 %; mean ± s.d. over five seeds; sorted by BDG2 MACD; PCS-CQR variants in bold).](figures/Fig5_tradeoff.png){#fig:tradeoff}

## Tuning the pseudo-count {#sec:tuning}

The interval score cannot select $\kappa$. Across finite $\kappa>0$ its leave-one-building-out (LOBO) value on calibration buildings varies by only {{tune_BDG2_is_range_pct}} % (BDG2; UCI {{tune_UCI_is_range_pct}} %), and dropping the building's own scores altogether ($\kappa=\infty$) raises it by only {{tune_BDG2_inf_vs_best}} % (median over runs; Supplementary Table {{supp_T_tuning_curves}}). Coverage deviation, in contrast, varies strongly with $\kappa$.

On target buildings the picture is the same (Fig. [-@fig:sens]). The median relative interval score stays within {{sens_BDG2_is_range}} on BDG2 for every finite $\kappa$, while MACD ranges over {{sens_BDG2_macd_range}} with its minimum at $\kappa$ = {{sens_BDG2_kappa_best}}, and reaches {{sens_BDG2_macd_inf}} at $\kappa=\infty$. Too small a pseudo-count (24–48 h) also under-covers, because the quantile of a few own scores is noisy.

The pre-registered interval-score rule mostly selected $\kappa$ = 336 and left {{main_BDG2_PCSCQR_IStuned_under_rate}} of BDG2 buildings under-covered (PCS-CQR (IS-tuned)). The reliability-aware rule selected $\kappa\in\{${{tuned_BDG2_pcs}}$\}$ on BDG2 and $\{${{tuned_UCI_pcs}}$\}$ on UCI and halved that share ({{main_BDG2_PCSCQR_under_rate}}). The coverage-deviation difference is significant on BDG2 ({{test_main_BDG2_PCSCQR_vs_PCSCQR_IStuned_abs_dev_p}}), but the difference in the under-covered share is not ({{test_main_BDG2_PCSCQR_vs_PCSCQR_IStuned_under_p}}).

A fixed one-week pseudo-count, chosen without any data, performs as well as the tuned one: PCS-CQR κ=168 leaves {{main_BDG2_PCSCQR_kappa168_under_rate}} of BDG2 and {{main_UCI_PCSCQR_kappa168_under_rate}} of UCI buildings under-covered (paired test vs PCS-CQR: {{test_main_BDG2_PCSCQR_vs_PCSCQR_kappa168_abs_dev_p}}). Selecting $\kappa$ by leave-*site*-out instead of leave-building-out changes nothing ({{main_BDG2_PCSCQR_sitegrouped_under_rate}}). The same holds for quantile shrinkage (QShrink-CQR λ=168: {{main_BDG2_QShrinkCQR_lambda168_under_rate}}), whose interval-score-tuned version selected large $\lambda$ and is less reliable ({{main_BDG2_QShrinkCQR_under_rate}}).

![Sensitivity of PCS-CQR to the pseudo-count κ on target buildings, with uniform (solid) and onboarding-stage-matched (dashed) prior (random-building protocol, nominal 90 %, mean over five seeds; ∞ = pooled calibration).](figures/Fig9_sensitivity.png){#fig:sens}

## Which design elements matter

The refinements of the pre-registered design add nothing on the CQR score (Supplementary Table {{supp_T_ablation}}):

- *Onboarding-stage matching of the prior* leaves MACD and the under-covered share unchanged (PCS-CQR +stage: {{main_BDG2_PCSCQR_stage_under_rate}}; dashed lines in Fig. [-@fig:sens]).
- *A similarity-localised prior* slightly increases under-coverage (PCS-CQR +kNN: {{main_BDG2_PCSCQR_kNN_under_rate}}; +kNN+stage: {{main_BDG2_PCSCQR_kNNstage_under_rate}}).
- *The pre-registered HSC-CQR*, which combines both refinements with interval-score tuning, is less reliable than PCS-CQR ({{main_BDG2_HSCCQR_under_rate}}; coverage deviation {{test_main_BDG2_PCSCQR_vs_HSCCQR_abs_dev_p}}). It also has the worst first week of all shrinkage variants ({{main_BDG2_HSCCQR_under_w1}} under-covered).
- *Removing the shrinkage* (κ=∞) returns pooled CQR ({{main_BDG2_PCSCQR_shrink_under_rate}}).

The one element that matters is therefore shrinkage toward the building's own scores, tuned for reliability or fixed at about one week.

The planned primary comparison concerned the absolute score (Supplementary Table {{supp_T_tests}}, family "preregistered-abs"). Its hypothesis is only partly supported:

- HSC has a lower interval score than every planned baseline, including self-only calibration (BDG2 {{test_main_BDG2_HSC_vs_SelfCP_rel_IS_p}}; UCI {{test_main_UCI_HSC_vs_SelfCP_rel_IS_p}}).
- It does not reduce per-building miscalibration relative to Self-CP (BDG2 {{test_main_BDG2_HSC_vs_SelfCP_abs_dev_p}}; UCI {{test_main_UCI_HSC_vs_SelfCP_abs_dev_p}}).
- For the absolute score, stage matching does help in the first week. Without the similarity prior, stage-matched HSC leaves {{main_BDG2_HSC_kNN_under_w1}} of BDG2 buildings under-covered in week 1, compared with {{main_BDG2_PCS_under_w1}} for PCS. Absolute residuals of a forecaster with a few days of history are much larger than later ones, whereas the CQR quantile models already widen with little history.

## Onboarding dynamics {#sec:dynamics}

Figure [-@fig:stage] follows coverage and interval score by days since metering, and Supplementary Table {{supp_T_weeks}} gives the under-covered share per week.

The first week is hard for every strategy. On BDG2, {{main_BDG2_CQR_under_w1}} of buildings are under-covered within week 1 with CQR and {{main_BDG2_PCSCQR_under_w1}} with PCS-CQR. Self-CQR is worst at {{main_BDG2_SelfCQR_under_w1}}. With independent misses, sampling noise alone would put only {{floor_w1_under}} of 168-hour windows below 0.85. The first-week failures are real, and no strategy of comparable width repairs them. Coverage-only ACI reduces them to {{main_BDG2_ACICQR_coverage_only_under_w1}}, but with intervals {{ratio_BDG2_acicov_vs_pcs_width}} times as wide.

The gain of PCS-CQR over CQR grows with time since metering. In weeks 5–8 the under-covered share is {{main_BDG2_PCSCQR_under_w58}} versus {{main_BDG2_CQR_under_w58}} on BDG2, and {{main_UCI_PCSCQR_under_w58}} versus {{main_UCI_CQR_under_w58}} on UCI. Pooled strategies do not improve over the window because their radius does not learn from the building.

In the first days, the interval score falls steeply for all strategies as the forecaster's features fill (Fig. [-@fig:stage]c, d). Self-CQR's interval score stays higher throughout.

![Mean per-building coverage (a, b) and median relative interval score (c, d) by days of own history h (daily for h ≤ 7, then weekly means; shaded: first week) for the CQR-score calibration strategies (random-building protocol, nominal 90 %, five seeds).](figures/Fig3_stage_curves.png){#fig:stage}

## Generalisation, other nominal levels and stress {#sec:robust}

Table [-@tbl:conditions] reports the under-covered share of every CQR-score strategy across protocols and stress tests. MACD, interval scores and paired tests for every condition are given in Supplementary Tables {{supp_T_lso}}–{{supp_T_pools}} and {{supp_T_tests}}.

**Unseen sites, countries and calibration periods.**

- *Leave-one-site-out.* With every BDG2 site held out in turn, PCS-CQR leaves {{lso_BDG2_PCSCQR_under_rate}} of buildings under-covered, against {{lso_BDG2_CQR_under_rate}} for CQR ({{test_lso_BDG2_PCSCQR_vs_CQR_under_p}}) and {{lso_BDG2_SelfCQR_under_rate}} for Self-CQR ({{test_lso_BDG2_PCSCQR_vs_SelfCQR_under_p}}). It stays below 5 % at every one of the ten sites, including the two where pooled CQR fails for half or more of the buildings (Supplementary Table {{supp_T_lso_sites}}).
- *Cross-dataset.* When forecaster and calibration scores come from Portuguese clients and the targets are North American and European campus buildings (UCI → BDG2), pooled CQR fails for {{xds_U2B_CQR_under_rate}} of buildings. PCS-CQR fails for {{xds_U2B_PCSCQR_under_rate}} ({{test_xds_U2B_BDG2_PCSCQR_vs_CQR_under_p}}), because the building's own scores take over from the mismatched prior.
- *Disjoint calibration period.* Calibrating on a period disjoint from the forecaster's training period leaves the picture unchanged (PCS-CQR {{rob_disjointmcalmperiod_PCSCQR_under_rate}}, CQR {{rob_disjointmcalmperiod_CQR_under_rate}}).

**Other nominal levels.** At 95 %, PCS-CQR leaves {{main_BDG2_a5_PCSCQR_under_rate}} of BDG2 buildings below 90 % coverage, against {{main_BDG2_a5_CQR_under_rate}} for CQR. At 80 % the shares below 75 % are {{main_BDG2_a20_PCSCQR_under_rate}} and {{main_BDG2_a20_CQR_under_rate}} (Supplementary Tables {{supp_T_a5_BDG2}}–{{supp_T_a20_UCI}}).

**Stress tests.**

- *Shrinkage strategies are the most reliable* under missing data, contiguous outages, level shifts in either direction and a weak forecaster. Here PCS-CQR, its fixed-κ version and QShrink-CQR (MACD) stay at or below about 4 % under-covered, while pooled strategies reach 17–30 %.
- *Self-CQR is as reliable or more* when meter noise is added to history and truth ({{rob_noise15_SelfCQR_under_rate}} vs {{rob_noise15_PCSCQR_under_rate}}, {{test_rob_noise15_BDG2_PCSCQR_vs_SelfCQR_under_p}}) and after an early level shift. In both cases the pooled prior no longer describes the building.
- *Day-to-day volatility* defeats every strategy: random daily load factors with 25 % standard deviation from day 28 leave {{rob_volatility25_PCSCQR_under_rate}} of buildings under-covered with PCS-CQR and {{rob_volatility25_SelfCQR_under_rate}} with Self-CQR ({{test_rob_volatility25_BDG2_PCSCQR_vs_SelfCQR_under_p}}). Four weeks of own scores cannot anticipate an unpredictable change of this size, and a larger pseudo-count slows the adaptation further.
- *Small calibration pools.* With only 5 calibration buildings the tuned layer leaves {{pools_n5_PCSCQR_under_rate}} under-covered and the fixed one-week pseudo-count {{pools_n5_PCSCQR_kappa168_under_rate}}, compared with {{pools_n5_CQR_under_rate}} for CQR. LOBO tuning on very few buildings is noisy, so the fixed value is the safer choice for small pools. GHCP-CQR with 5 calibration buildings frequently returns unbounded intervals (Supplementary Table {{supp_T_pools}}).

<<TABLE:MS_conditions|tbl:conditions>>

## Remaining failures and cost {#sec:errors}

{{ERROR_ANALYSIS_TEXT}}

The layer is cheap (Supplementary Table {{supp_T_cost}}):

- The daily update of one building — adding 24 scores and recomputing one quantile — takes {{lat_single_ms}} ms on one CPU core.
- Batch-updating 10 000 buildings takes {{lat_batch10k_s}} s.
- The per-building state is {{lat_state_kB}} kB as implemented.
- Selecting $\kappa$ by LOBO takes {{cost_BDG2_pcs_tune_s}} s on BDG2, against {{cost_BDG2_hsc_tune_s}} s for the pre-registered similarity-localised design.
- Training the three LightGBM quantile models takes {{cost_BDG2_lgb_s}} s.
