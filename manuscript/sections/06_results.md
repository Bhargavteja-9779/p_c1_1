# Results {#sec:results}

## Point accuracy and the reliability problem (RQ1)

The global LightGBM forecaster reaches a median CV(RMSE) of {{point_BDG2_cvrmse_lgb}} on new BDG2 buildings over their first 56 forecast days (seasonal naive: {{point_BDG2_cvrmse_naive}}; MLP: {{point_BDG2_cvrmse_mlp}}) and {{point_UCI_cvrmse_lgb}} on UCI clients (naive {{point_UCI_cvrmse_naive}}; MLP {{point_UCI_cvrmse_mlp}}). The forecasters are therefore reasonable; the question is whether their intervals can be trusted building by building.

Tables [-@tbl:mainbdg2] and [-@tbl:mainuci] show that they cannot when calibration is pooled. Stage-matched split conformal prediction (SCP-stage) attains a mean per-building coverage of {{main_BDG2_SCPstage_mean_cov}} on BDG2, close to the 0.90 target, yet {{main_BDG2_SCPstage_under_rate}} of the new buildings have coverage below 0.85 and the 10th percentile of per-building coverage is {{main_BDG2_SCPstage_p10_cov}}. Direct quantile regression under-covers on average ({{main_BDG2_QRLGBM_mean_cov}}); conformalising it (CQR) restores the mean ({{main_BDG2_CQR_mean_cov}}) but leaves {{main_BDG2_CQR_under_rate}} of the buildings under-covered. Calibrating separately per usage type (Mondrian-usage, {{main_BDG2_Mondrianusage_under_rate}}) does not help, and the deep quantile model (MLP-QR, {{main_BDG2_MLPQR_under_rate}}) does not solve the problem either; the Gaussian MLP lowers under-coverage only by over-covering on average ({{main_BDG2_MLPGauss_mean_cov}}) with wider intervals (median relative width {{main_BDG2_MLPGauss_rel_width}} vs {{main_BDG2_CQR_rel_width}} for CQR). The same pattern appears on UCI, where SCP-stage and CQR leave {{main_UCI_SCPstage_under_rate}} and {{main_UCI_CQR_under_rate}} of the clients under-covered. Fig. [-@fig:cdf] shows the full distributions: pooled methods have long lower tails of buildings with 0.70–0.85 coverage.

<<TABLE:MS_main_BDG2|tbl:mainbdg2>>

<<TABLE:MS_main_UCI|tbl:mainuci>>

![Empirical distribution of per-building coverage over the 56-day onboarding window for the CQR-score calibration strategies and stage-matched split conformal prediction (all target buildings of all five seeds; dashed: nominal 0.90; dotted: 0.85).](figures/Fig4_coverage_cdf.png){#fig:cdf}

## Comparison of building-adaptive calibration strategies (RQ2)

All strategies in this subsection use the same LightGBM quantile models and the same CQR scores; they differ only in how a new building's own scores enter the calibration. Pseudo-count shrinkage of the score distribution (HSC-CQR) is the most reliable of the tuned strategies on both datasets: on BDG2 its MACD is {{main_BDG2_HSCCQR_macd}} and {{main_BDG2_HSCCQR_under_rate}} of the buildings are under-covered (CQR: {{main_BDG2_CQR_macd}}, {{main_BDG2_CQR_under_rate}}), and on UCI {{main_UCI_HSCCQR_macd}} and {{main_UCI_HSCCQR_under_rate}} (CQR: {{main_UCI_CQR_macd}}, {{main_UCI_CQR_under_rate}}). The 10th-percentile coverage rises from {{main_BDG2_CQR_p10_cov}} to {{main_BDG2_HSCCQR_p10_cov}} on BDG2. The median relative interval score is essentially unchanged ({{main_BDG2_HSCCQR_rel_IS}} vs {{main_BDG2_CQR_rel_IS}} on BDG2; {{main_UCI_HSCCQR_rel_IS}} vs {{main_UCI_CQR_rel_IS}} on UCI), so the gain in reliability does not come from wider intervals. For reference, perfectly calibrated intervals with independent misses would have an expected MACD of about {{floor_BDG2_macd}} (BDG2) and {{floor_UCI_macd}} (UCI) from sampling noise alone ({{nvalid_BDG2_median}} hourly observations per building); autocorrelated misses raise this floor further.

The competing mechanisms behave as their designs suggest. Quantile-level shrinkage (QShrink-CQR, the "regularised Mondrian") is the closest competitor (MACD {{main_BDG2_QShrinkCQR_macd}} on BDG2, {{main_UCI_QShrinkCQR_macd}} on UCI; under-covered {{main_BDG2_QShrinkCQR_under_rate}} and {{main_UCI_QShrinkCQR_under_rate}}). Self-only calibration (Self-CQR) is reliable later in the window but poor in the first week (coverage {{main_BDG2_SelfCQR_cov_early}} on BDG2), when a handful of own scores yields noisy quantiles. Adaptive conformal inference on the same scores (ACI-CQR; MACD {{main_BDG2_ACICQR_macd}}, under-covered {{main_BDG2_ACICQR_under_rate}}) adapts more slowly because it reacts to the building's errors only through the miscoverage indicator with a small step size. Temporal quantile adjustment (TQA-B-CQR; {{main_BDG2_TQABCQR_macd}}, {{main_BDG2_TQABCQR_under_rate}}) and the GHCP-style pooling (GHCP-CQR; {{main_BDG2_GHCPCQR_macd}}, {{main_BDG2_GHCPCQR_under_rate}}) remain close to pooled CQR: TQA-B bounds the quantile adjustment by design, and GHCP never gives the new building more weight than one reference building, which secures marginal validity across buildings but cannot correct a building whose errors are systematically larger than average.

Table [-@tbl:tests] reports the paired per-building tests of HSC-CQR against each strategy. On BDG2, HSC-CQR has a smaller absolute coverage deviation than CQR for {{test_main_BDG2_HSCCQR_vs_CQR_abs_dev_better}} of the {{test_main_BDG2_HSCCQR_vs_CQR_abs_dev_n}} buildings ($r_{rb}$ = {{test_main_BDG2_HSCCQR_vs_CQR_abs_dev_r}}, Holm-adjusted $p$ {{test_main_BDG2_HSCCQR_vs_CQR_abs_dev_p}}); against QShrink-CQR the corresponding values are {{test_main_BDG2_HSCCQR_vs_QShrinkCQR_abs_dev_better}} ($r_{rb}$ = {{test_main_BDG2_HSCCQR_vs_QShrinkCQR_abs_dev_r}}, $p$ {{test_main_BDG2_HSCCQR_vs_QShrinkCQR_abs_dev_p}}), against Self-CQR {{test_main_BDG2_HSCCQR_vs_SelfCQR_abs_dev_better}} ($r_{rb}$ = {{test_main_BDG2_HSCCQR_vs_SelfCQR_abs_dev_r}}, $p$ {{test_main_BDG2_HSCCQR_vs_SelfCQR_abs_dev_p}}) and against ACI-CQR {{test_main_BDG2_HSCCQR_vs_ACICQR_abs_dev_better}} ($r_{rb}$ = {{test_main_BDG2_HSCCQR_vs_ACICQR_abs_dev_r}}, $p$ {{test_main_BDG2_HSCCQR_vs_ACICQR_abs_dev_p}}). For the interval score the differences to CQR, QShrink-CQR and ACI-CQR are small in magnitude ($r_{rb}$ = {{test_main_BDG2_HSCCQR_vs_CQR_rel_IS_r}}, {{test_main_BDG2_HSCCQR_vs_QShrinkCQR_rel_IS_r}} and {{test_main_BDG2_HSCCQR_vs_ACICQR_rel_IS_r}}). The UCI comparisons, based on {{test_main_UCI_HSCCQR_vs_CQR_abs_dev_n}} clients, are reported in the same table. Fig. [-@fig:tradeoff] summarises the reliability–sharpness trade-off of all methods.

The calibration layer is not specific to LightGBM: applied to the quantiles of the MLP quantile model, it reduces the MACD from {{main_BDG2_CQR_MLP_macd}} (CQR on MLP quantiles) to {{main_BDG2_HSCCQR_MLP_macd}} and the under-covered share from {{main_BDG2_CQR_MLP_under_rate}} to {{main_BDG2_HSCCQR_MLP_under_rate}} on BDG2 ({{main_UCI_CQR_MLP_macd}} → {{main_UCI_HSCCQR_MLP_macd}} on UCI). On the absolute-residual score, HSC improves on pooled SCP (MACD {{main_BDG2_HSC_macd}} vs {{main_BDG2_SCPstage_macd}}) but not on self-only calibration (Self-CP: {{main_BDG2_SelfCP_macd}}); for that score the stage-agnostic simple variant is the better choice ({{main_BDG2_HSC_simple_macd}}).

<<TABLE:MS_tests|tbl:tests>>

![Reliability–sharpness trade-off: MACD (lower is better) against the median relative interval score (lower is better); mean ± s.d. over five seeds.](figures/Fig5_tradeoff.png){#fig:tradeoff}

## Onboarding dynamics

Fig. [-@fig:stage] resolves coverage and interval score by onboarding day. All methods have their largest interval scores in the first days, when the forecaster has least history. Pooled calibration keeps a fixed radius per stage bin and therefore cannot react to an individual building, whereas the shrinkage strategies move towards the building's own error level as scores accumulate. In the first week, HSC-CQR's mean coverage is {{main_BDG2_HSCCQR_cov_early}} on BDG2 and {{main_UCI_HSCCQR_cov_early}} on UCI (CQR: {{main_BDG2_CQR_cov_early}} and {{main_UCI_CQR_cov_early}}); until own scores accumulate, every strategy can only be as reliable as its population calibration.

![Coverage (a, b) and relative interval score (c, d) by days of own history; daily for the first week (shaded), weekly means afterwards; mean over buildings and seeds.](figures/Fig3_stage_curves.png){#fig:stage}

## Which design elements matter (RQ3)

Table [-@tbl:ablation] isolates the elements of the calibration layer. Removing the shrinkage towards own scores (κ = ∞) is decisive: HSC-CQR's under-covered share rises from {{main_BDG2_HSCCQR_under_rate}} to {{main_BDG2_HSCCQR_shrink_under_rate}} on BDG2 and from {{main_UCI_HSCCQR_under_rate}} to {{main_UCI_HSCCQR_shrink_under_rate}} on UCI. Removing the similarity prior (K = all) or the stage matching changes the MACD by less than its seed-to-seed standard deviation (BDG2: {{main_BDG2_HSCCQR_kNN_macd}} and {{main_BDG2_HSCCQR_stage_macd}} vs {{main_BDG2_HSCCQR_macd}}); the simple variant without both refinements reaches {{main_BDG2_HSCCQR_simple_macd}} on BDG2 and {{main_UCI_HSCCQR_simple_macd}} on UCI. The pseudo-count itself matters more than the refinements: fixing it at one week of hourly scores (κ = 168, a donor–local mixture with fixed pseudo-count) gives {{main_BDG2_HSCCQR_fixedkappa_macd}} and {{main_BDG2_HSCCQR_fixedkappa_under_rate}} under-covered buildings on BDG2 at a median interval score of {{main_BDG2_HSCCQR_fixedkappa_rel_IS}} ({{main_UCI_HSCCQR_fixedkappa_macd}} and {{main_UCI_HSCCQR_fixedkappa_rel_IS}} on UCI), whereas leave-one-building-out tuning on the interval score selected κ ∈ {{{tuned_BDG2_kappa_simple}}} h for the simple variant on BDG2 and {{{tuned_UCI_kappa_simple}}} h on UCI. The tuning objective rewards sharpness as well as coverage, so a slightly smaller pseudo-count trades a little sharpness for per-building reliability (Section [-@sec:discussion]).

<<TABLE:MS_ablation|tbl:ablation>>

![Ablation of the HSC-CQR elements: '-stage' removes onboarding-stage matching, '-kNN' the similarity prior, 'simple' both, 'fixed-κ' fixes κ = 168 h, '-shrink' removes the shrinkage towards own scores (κ = ∞); Self-CQR is κ = 0; mean ± s.d. over five seeds.](figures/Fig6_ablation.png){#fig:ablation}

## Robustness (RQ4)

Table [-@tbl:robust] and Fig. [-@fig:robust] stress the strategies on BDG2. With 15 % meter noise on the new buildings, pooled calibration from clean calibration buildings breaks down (SCP-stage: {{rob_noise15_SCPstage_under_rate}} under-covered; CQR: {{rob_noise15_CQR_under_rate}}), whereas HSC-CQR leaves {{rob_noise15_HSCCQR_under_rate}} under-covered because the building's own, noisy scores enter the mixture. Missing data (up to 40 % of hours) mainly delays adaptation (HSC-CQR {{rob_missing40_HSCCQR_under_rate}} vs CQR {{rob_missing40_CQR_under_rate}}). Abrupt level changes of ±40 % at day 28 are the hardest case for all strategies that accumulate own scores, because pre-change scores remain in the mixture: with the downward shift HSC-CQR leaves {{rob_shift-40_HSCCQR_under_rate}} under-covered (ACI-CQR {{rob_shift-40_ACICQR_under_rate}}, QShrink-CQR {{rob_shift-40_QShrinkCQR_under_rate}}, CQR {{rob_shift-40_CQR_under_rate}}), and with the upward shift {{rob_shift+40_HSCCQR_under_rate}} (ACI-CQR {{rob_shift+40_ACICQR_under_rate}}). Reducing the calibration pool to 10 % of the buildings ({{rob_calpool10_HSCCQR_under_rate}}) or using a forecaster trained on only 10 % of the training buildings ({{rob_weak-forecaster_HSCCQR_under_rate}}) has little effect on HSC-CQR.

<<TABLE:MS_robustness|tbl:robust>>

![Robustness on BDG2: MACD (a) and share of under-covered buildings (b) under meter noise, missing data, level shifts, reduced calibration pools and a weak forecaster (3 seeds).](figures/Fig7_robustness.png){#fig:robust}

## Generalisation (RQ5)

Under the leave-site-out protocol the target buildings are on campuses from which no training or calibration building comes. HSC-CQR's MACD is {{lso_BDG2_HSCCQR_macd}} (CQR {{lso_BDG2_CQR_macd}}; QShrink-CQR {{lso_BDG2_QShrinkCQR_macd}}), with {{lso_BDG2_HSCCQR_under_rate}} versus {{lso_BDG2_CQR_under_rate}} of the buildings under-covered (Table [-@tbl:gen], Fig. [-@fig:gen]). Cross-dataset transfer is harder: with models and calibration scores from BDG2 applied to Portuguese UCI clients, CQR leaves {{xds_B2U_CQR_under_rate}} under-covered and HSC-CQR {{xds_B2U_HSCCQR_under_rate}}; in the opposite direction (UCI→BDG2) the values are {{xds_U2B_CQR_under_rate}} and {{xds_U2B_HSCCQR_under_rate}}. Because the population prior comes from a different population, the gains under transfer rest on the shrinkage towards own scores.

<<TABLE:MS_generalisation|tbl:gen>>

![Generalisation: MACD (a) and median relative interval score (b) for random-building, leave-site-out and cross-dataset settings.](figures/Fig8_generalisation.png){#fig:gen}

## Sensitivity and computational cost

Fig. [-@fig:sens] shows the target-building MACD and interval score of HSC-CQR over the full grid of κ and K (for transparency only; not used for any choice). MACD is lowest for κ between one day and one to two weeks of hourly scores and deteriorates towards κ = ∞; K has little influence. Results at nominal 95 % and 80 % show the same ordering of the absolute-score strategies (supplementary Tables S3–S6).

Table [-@tbl:cost] reports costs on a 4-core CPU. Once the scores are stored, the calibration layer adds {{cost_BDG2_apply_ms}} ms per building-day and needs {{cost_BDG2_store_MB}} MB for about 170 calibration buildings; the one-off leave-one-building-out tuning takes {{cost_BDG2_tune_s}} s. Both are negligible next to training the global forecaster ({{cost_BDG2_lgb_s}} s for the three LightGBM models).

![Sensitivity of HSC-CQR to κ and K on target buildings (mean over five seeds; not used for selection).](figures/Fig9_sensitivity.png){#fig:sens}

<<TABLE:MS_cost|tbl:cost>>

## Error analysis

{{ERROR_ANALYSIS_TEXT}} Fig. [-@fig:examples] shows two pre-specified buildings: the one at the 10th percentile and the one at the median of per-building CQR coverage.

![Error analysis on BDG2: (a) per-building coverage vs. point-forecast CV(RMSE); (b) mean coverage by primary usage (usage classes with at least 30 building × seed units).](figures/Fig10_error_analysis.png){#fig:errors}

![Day-ahead 90 % intervals for two pre-specified BDG2 buildings during their first 10 forecast days (seed 0): the building at the 10th percentile (a) and at the median (b) of per-building CQR coverage. Markers show observations outside the respective interval.](figures/Fig11_examples.png){#fig:examples}
