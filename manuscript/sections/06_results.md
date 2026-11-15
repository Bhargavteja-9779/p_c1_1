# Results {#sec:results}

## Point accuracy and the reliability problem (RQ1)

The global LightGBM forecaster reaches a median CV(RMSE) of {{point_BDG2_cvrmse_lgb}} on new BDG2 buildings over their first 56 forecast days, against {{point_BDG2_cvrmse_naive}} for the seasonal-naive forecast; the MLP is comparable ({{point_BDG2_cvrmse_mlp}}). On UCI the values are {{point_UCI_cvrmse_lgb}}, {{point_UCI_cvrmse_naive}} and {{point_UCI_cvrmse_mlp}}. The forecasters are therefore reasonable, and the question is whether their intervals can be trusted building by building.

Tables [-@tbl:mainbdg2] and [-@tbl:mainuci] show that they cannot when calibration is pooled. Split conformal prediction with stage matching (SCP-stage) attains a mean per-building coverage of {{main_BDG2_SCPstage_mean_cov}} on BDG2, close to the 0.90 target. Yet {{main_BDG2_SCPstage_under_rate}} of the new buildings have coverage below 0.85, and the 10th percentile of per-building coverage is {{main_BDG2_SCPstage_p10_cov}}. Quantile regression (QR-LGBM) under-covers on average ({{main_BDG2_QRLGBM_mean_cov}}). Conformalising it (CQR) restores the mean ({{main_BDG2_CQR_mean_cov}}) but still leaves {{main_BDG2_CQR_under_rate}} of buildings under-covered. Group-wise calibration by usage type (Mondrian-usage, {{main_BDG2_Mondrianusage_under_rate}}) does not help. The deep quantile model (MLP-QR, {{main_BDG2_MLPQR_under_rate}}) and the Gaussian MLP do not solve the problem either: the Gaussian MLP reduces under-coverage only by producing wider intervals (median relative width {{main_BDG2_MLPGauss_rel_width}} versus {{main_BDG2_CQR_rel_width}} for CQR) and over-covers on average ({{main_BDG2_MLPGauss_mean_cov}}). The same pattern appears on UCI, where SCP-stage and CQR leave {{main_UCI_SCPstage_under_rate}} and {{main_UCI_CQR_under_rate}} of clients under-covered. Fig. [-@fig:cdf] shows the full distributions: pooled methods have long lower tails of buildings with 0.70–0.85 coverage.

<<TABLE:MS_main_BDG2|tbl:mainbdg2>>

<<TABLE:MS_main_UCI|tbl:mainuci>>

![Empirical distribution of per-building coverage over the 56-day onboarding window (all target buildings of all five seeds; dashed: nominal 0.90; dotted: 0.85).](figures/Fig4_coverage_cdf.png){#fig:cdf}

## Per-building reliability of HSC (RQ2)

HSC applied to CQR scores (HSC-CQR) gives the most reliable intervals on both datasets. On BDG2 its MACD is {{main_BDG2_HSCCQR_macd}} (CQR: {{main_BDG2_CQR_macd}}), the under-covered share falls to {{main_BDG2_HSCCQR_under_rate}} (CQR: {{main_BDG2_CQR_under_rate}}), and the 10th-percentile coverage rises to {{main_BDG2_HSCCQR_p10_cov}} (CQR: {{main_BDG2_CQR_p10_cov}}). The median relative interval score is essentially unchanged ({{main_BDG2_HSCCQR_rel_IS}} vs {{main_BDG2_CQR_rel_IS}}). On UCI the MACD is {{main_UCI_HSCCQR_macd}} versus {{main_UCI_CQR_macd}}, with {{main_UCI_HSCCQR_under_rate}} versus {{main_UCI_CQR_under_rate}} of clients under-covered. For reference, perfectly calibrated intervals with independent misses would have an expected MACD of about {{floor_BDG2_macd}} (BDG2) and {{floor_UCI_macd}} (UCI) from sampling noise alone ({{nvalid_BDG2_median}} hourly observations per building), and autocorrelated misses would raise this floor further.

The two building-adaptive competitors that use the same CQR scores are informative. Self-only calibration (Self-CQR, $\kappa=0$) reaches a MACD of {{main_BDG2_SelfCQR_macd}} on BDG2 and {{main_UCI_SelfCQR_macd}} on UCI. Its first-week coverage is low ({{main_BDG2_SelfCQR_cov_early}} on BDG2), because a handful of own scores yields noisy quantiles. ACI on CQR scores attains {{main_BDG2_ACICQR_macd}} and {{main_UCI_ACICQR_macd}}. HSC-CQR is better than both, which is the expected behaviour of partial pooling. With few own scores, the population prior stabilises the quantile; as scores accumulate, the building's own distribution takes over.

Table [-@tbl:tests] reports paired per-building tests. On BDG2, HSC-CQR has a smaller absolute coverage deviation than CQR for {{test_main_BDG2_HSCCQR_vs_CQR_abs_dev_better}} of the {{test_main_BDG2_HSCCQR_vs_CQR_abs_dev_n}} buildings ($r_{rb}$ = {{test_main_BDG2_HSCCQR_vs_CQR_abs_dev_r}}, Holm-adjusted $p$ {{test_main_BDG2_HSCCQR_vs_CQR_abs_dev_p}}). Against ACI-CQR the corresponding values are {{test_main_BDG2_HSCCQR_vs_ACICQR_abs_dev_better}} ($r_{rb}$ = {{test_main_BDG2_HSCCQR_vs_ACICQR_abs_dev_r}}, $p$ {{test_main_BDG2_HSCCQR_vs_ACICQR_abs_dev_p}}), and against Self-CQR {{test_main_BDG2_HSCCQR_vs_SelfCQR_abs_dev_better}} ($r_{rb}$ = {{test_main_BDG2_HSCCQR_vs_SelfCQR_abs_dev_r}}, $p$ {{test_main_BDG2_HSCCQR_vs_SelfCQR_abs_dev_p}}). For the interval score, differences to CQR and ACI-CQR are small in magnitude ($r_{rb}$ = {{test_main_BDG2_HSCCQR_vs_CQR_rel_IS_r}} and {{test_main_BDG2_HSCCQR_vs_ACICQR_rel_IS_r}}, $p$ {{test_main_BDG2_HSCCQR_vs_CQR_rel_IS_p}} and {{test_main_BDG2_HSCCQR_vs_ACICQR_rel_IS_p}}). The reliability gain is therefore not bought with wider or less informative intervals. The UCI comparisons are reported in the same table. Fig. [-@fig:tradeoff] summarises the trade-off between sharpness (interval score) and reliability (MACD).

On the absolute-residual score, HSC improves on pooled SCP (MACD {{main_BDG2_HSC_macd}} vs {{main_BDG2_SCPstage_macd}} on BDG2, {{main_UCI_HSC_macd}} vs {{main_UCI_SCPstage_macd}} on UCI). It is, however, not better than self-only calibration on this score in terms of MACD (Self-CP: {{main_BDG2_SelfCP_macd}} on BDG2, {{main_UCI_SelfCP_macd}} on UCI), although its interval score is lower ({{main_BDG2_HSC_rel_IS}} vs {{main_BDG2_SelfCP_rel_IS}}); for the absolute score, adapting to the building's own errors matters more than how the prior is formed.

<<TABLE:MS_tests|tbl:tests>>

![Reliability–sharpness trade-off: MACD (lower is better) against the median relative interval score (lower is better); mean ± s.d. over five seeds.](figures/Fig5_tradeoff.png){#fig:tradeoff}

## Onboarding dynamics

Fig. [-@fig:stage] resolves coverage and interval score by onboarding day. All methods have their largest interval scores in the first days, when the forecaster has least history. Coverage curves show where the methods differ. Pooled methods sit persistently above or below the target for the whole window, because their radius does not change once the stage bin is fixed. Self-only calibration starts noisily. HSC-CQR stays close to 0.90 from the second week onwards. In the first week, HSC-CQR's mean coverage is {{main_BDG2_HSCCQR_cov_early}} on BDG2 and {{main_UCI_HSCCQR_cov_early}} on UCI, compared with {{main_BDG2_CQR_cov_early}} and {{main_UCI_CQR_cov_early}} for CQR. HSC can only be as reliable as its prior until own scores accumulate.

![Coverage (a, b) and relative interval score (c, d) by days of own history; daily for the first week (shaded), weekly means afterwards; mean over buildings and seeds.](figures/Fig3_stage_curves.png){#fig:stage}

## Ablation (RQ3)

Table [-@tbl:ablation] isolates the three elements of HSC. Removing the shrinkage toward own scores (κ = ∞) is decisive. HSC-CQR's under-covered share rises from {{main_BDG2_HSCCQR_under_rate}} to {{main_BDG2_HSCCQR_shrink_under_rate}} on BDG2 and from {{main_UCI_HSCCQR_under_rate}} to {{main_UCI_HSCCQR_shrink_under_rate}} on UCI. In contrast, removing similarity localisation (K = all) or stage matching changes the results by less than the seed-to-seed standard deviation on both datasets (BDG2 MACD {{main_BDG2_HSCCQR_kNN_macd}} and {{main_BDG2_HSCCQR_stage_macd}} vs {{main_BDG2_HSCCQR_macd}}). The same holds for the absolute-residual variant. We therefore report the simplest variant, a uniform population prior with shrinkage, as the recommended default (Section [-@sec:discussion]). Fixing κ at one week (168 h) instead of selecting it gives similar results, which indicates that the shrinkage does not hinge on fine-tuning.

<<TABLE:MS_ablation|tbl:ablation>>

![Ablation of HSC components (absolute-residual score); mean ± s.d. over five seeds.](figures/Fig6_ablation.png){#fig:ablation}

## Robustness (RQ4)

Table [-@tbl:robust] and Fig. [-@fig:robust] stress the methods on BDG2. With 15 % meter noise on the new buildings, pooled calibration from clean calibration buildings breaks down: SCP-stage leaves {{rob_noise15_SCPstage_under_rate}} and CQR {{rob_noise15_CQR_under_rate}} of buildings under-covered, while HSC-CQR leaves {{rob_noise15_HSCCQR_under_rate}}, because the building's own (noisy) scores enter the mixture. Missing data (up to 40 % of hours) mainly reduces the number of own scores and therefore slows adaptation. Here HSC-CQR leaves {{rob_missing40_HSCCQR_under_rate}} under-covered versus {{rob_missing40_CQR_under_rate}} for CQR. Abrupt level changes of ±40 % at day 28 are the hardest case for any method that accumulates own scores, because pre-change scores remain in the mixture. With the downward shift, HSC-CQR's under-covered share is {{rob_shift-40_HSCCQR_under_rate}} (ACI-CQR: {{rob_shift-40_ACICQR_under_rate}}; CQR: {{rob_shift-40_CQR_under_rate}}). With the upward shift it is {{rob_shift+40_HSCCQR_under_rate}} (ACI-CQR: {{rob_shift+40_ACICQR_under_rate}}). Reducing the calibration pool to 10 % of the buildings has little effect ({{rob_calpool10_HSCCQR_under_rate}}), and so does a forecaster trained on only 10 % of the training buildings ({{rob_weak-forecaster_HSCCQR_under_rate}}).

<<TABLE:MS_robustness|tbl:robust>>

![Robustness on BDG2: MACD (a) and share of under-covered buildings (b) under meter noise, missing data, level shifts, reduced calibration pools and a weak forecaster (3 seeds). *No MLP baseline for the weak-forecaster condition.](figures/Fig7_robustness.png){#fig:robust}

## Generalisation (RQ5)

Under the leave-site-out protocol the targets are at campuses that none of the training or calibration buildings come from. HSC-CQR's MACD is {{lso_BDG2_HSCCQR_macd}} (CQR {{lso_BDG2_CQR_macd}}), with {{lso_BDG2_HSCCQR_under_rate}} versus {{lso_BDG2_CQR_under_rate}} of buildings under-covered (Table [-@tbl:gen], Fig. [-@fig:gen]). Cross-dataset transfer is harder. With models and calibration scores from BDG2 applied to Portuguese UCI clients, CQR leaves {{xds_B2U_CQR_under_rate}} under-covered; HSC-CQR reduces this to {{xds_B2U_HSCCQR_under_rate}}. In the opposite direction (UCI→BDG2) the corresponding values are {{xds_U2B_CQR_under_rate}} and {{xds_U2B_HSCCQR_under_rate}}. Because the prior comes from a different population, the gains under transfer come mostly from the shrinkage toward own scores.

<<TABLE:MS_generalisation|tbl:gen>>

![Generalisation: MACD (a) and median relative interval score (b) for random-building, leave-site-out and cross-dataset settings.](figures/Fig8_generalisation.png){#fig:gen}

## Sensitivity and computational cost

Fig. [-@fig:sens] shows the target-building MACD and interval score of HSC-CQR for the full grid of κ and K. These values are reported for transparency and were not used for selection. MACD is flat for κ between roughly one and fourteen days (24–336 h) and deteriorates toward κ = ∞. K has almost no influence. The leave-one-building-out selections were κ ∈ {{{tuned_BDG2_kappa}}} h on BDG2 and {{{tuned_UCI_kappa}}} h on UCI. Results at nominal 95 % and 80 % levels are given in the supplementary tables and show the same ordering.

Table [-@tbl:cost] reports costs on a 4-core CPU. HSC adds {{cost_BDG2_apply_ms}} ms per building-day and a store of {{cost_BDG2_store_MB}} MB for about 170 calibration buildings. The one-off leave-one-building-out tuning takes {{cost_BDG2_tune_s}} s. Both are negligible next to training the global forecaster ({{cost_BDG2_lgb_s}} s for the three LightGBM models).

![Sensitivity of HSC-CQR to κ and K on target buildings (mean over five seeds; not used for selection).](figures/Fig9_sensitivity.png){#fig:sens}

<<TABLE:MS_cost|tbl:cost>>

## Error analysis

Fig. [-@fig:errors]a relates per-building coverage to forecast difficulty. Under CQR, buildings with high CV(RMSE) are systematically under-covered and easy buildings are over-covered. HSC-CQR removes most of this dependence. {{ERROR_ANALYSIS_TEXT}} Fig. [-@fig:examples] shows two pre-specified buildings: one at the 10th percentile of CQR coverage and one at the median.

![Error analysis on BDG2: (a) per-building coverage vs. point-forecast CV(RMSE); (b) mean coverage by primary usage (usage classes with at least 30 building × seed units).](figures/Fig10_error_analysis.png){#fig:errors}

![Day-ahead 90 % intervals for two pre-specified BDG2 buildings during their first 10 forecast days (seed 0): the building at the 10th percentile (a) and at the median (b) of per-building CQR coverage. Markers show observations outside the respective interval.](figures/Fig11_examples.png){#fig:examples}
