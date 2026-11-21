# Discussion {#sec:discussion}

## Why pooled calibration fails per building, and what shrinkage changes

**Why pooling fails.** A global forecaster normalised by building scale yields scores that are comparable *on average* across buildings but not identically distributed. Some buildings have regular schedules and small errors. Others have irregular occupancy, plug loads or faults that a few days of data cannot reveal. A pooled radius is a compromise: it over-covers the former and under-covers the latter. In our data it left about one in five new BDG2 buildings clearly under-covered while the mean coverage looked acceptable. The error analysis shows the mechanism: under pooled CQR, per-building coverage falls with forecast difficulty, and PCS largely removes this dependence.

**Why self-only calibration is not enough.** Calibration on the building's own errors alone removes this bias but replaces it with variance. A few dozen hourly scores give a noisy 90 % quantile, which is why Self-CQR is the worst strategy in week 1.

**What shrinkage does.** Shrinkage trades bias against variance explicitly. Its pseudo-count has a direct reading: the number of hourly own scores that the population prior is worth. The selected values of 2–7 days, and the equally good fixed value of one week, mean that a building's own errors dominate after one to two weeks.

**What the other strategies show.** Adjusting the *queried level* rather than the *score distribution* is a weaker lever in this setting:

- ACI with a step size tuned for sharpness changes the level too slowly.
- ACI tuned for coverage alone reaches near-perfect per-building coverage only by inflating the intervals.
- TQA-B bounds its adjustment by design.
- GHCP-style pooling secures marginal validity across buildings by never giving the new building more weight than one reference building.

Per-building reliability during onboarding requires the building's own errors to gain weight as they accumulate, at a rate set by one parameter.

**Relation to prior findings.**

- *Per-site evaluation.* Shahid et al. [@shahid2026] found in federated risk control that average calibration can hide failing sites. We find the same at building level, and the result persists under site hold-out, where pooled CQR fails for half or more of the buildings at two sites.
- *Quantile shrinkage.* Rafe and Das [@rafe2026] reported no decisive subgroup gain from quantile shrinkage in survey data. Here the same mechanism gives a decisive gain over pooled calibration. The difference is plausibly the setting: each building contributes a growing stream of its own scores, so its "group" quickly becomes large, whereas survey subgroups are fixed and often small.
- *Donor–local mixture.* The fixed one-week pseudo-count performed as well as the tuned one. This supports the fixed donor–local mixture implemented for new solar stations [@jeon2026], for which no results have been published.

## How the layer should be tuned and designed

**Tuning.** The practically important finding is negative: the interval score — the usual tuning target and the primary endpoint of our analysis plan — is nearly flat in the pseudo-count. It cannot distinguish a layer that leaves 3 % of buildings under-covered from one that leaves 1.5 %, nor, at $\kappa=\infty$, from pooled calibration. The reason is that a proper score aggregated over buildings rewards average sharpness and average calibration, and is insensitive to how miscoverage is distributed across buildings. A rule that looks at the per-building coverage deviation of calibration buildings, with the interval score only as a guard-rail, selects pseudo-counts of 2–7 days. A fixed one-week value is equally good. With a small calibration pool, where LOBO estimates are noisy, the fixed value is preferable.

**Design.** Neither refinement of our pre-registered design helped on the CQR score:

- *Similarity-localised prior.* After scale normalisation and history-derived features, the remaining between-building differences in score distributions seem to be driven by events (occupancy changes, equipment faults, irregular schedules) rather than by load shape or usage type. The usage-based Mondrian baseline fails for the same reason.
- *Onboarding-stage matching.* Unnecessary for CQR scores, because the quantile models already widen when little history is available.

On absolute residuals, stage matching did improve the first week, so the value of this refinement depends on the score. The planned comparison of the absolute-score design with self-only calibration found a lower interval score but no gain in per-building reliability. The recommendation therefore changed during the study (Supplementary Table S1), and results for PCS-CQR should be read as exploratory evidence that the confirmatory comparisons of a future study can build on.

## Practical implications

For aggregators, utilities and demand-response platforms that onboard buildings continuously, the results support a simple operating rule:

1. Train one global quantile forecaster.
2. Calibrate it with CQR scores of previously onboarded buildings.
3. Blend each new building's own scores in with a pseudo-count of about one week of hourly scores, or one selected by the reliability-aware rule when the calibration pool is large.

This keeps the share of buildings with clearly unreliable intervals small after the first week. It avoids a failure mode that pooled calibration hides: systematically under-protected capacity reservations and baselines for the most irregular buildings, which are the ones where settlements and alarms are most error-prone. The layer adds a few hundredths of a millisecond per building-day and 16 kB per building, and it works on top of different forecasters. It is therefore compatible with portfolio-scale deployment, including with pretrained forecasting models.

Two cautions apply:

- *The first week remains unreliable.* About one in five BDG2 buildings is under-covered with every strategy of comparable width. A platform that must act in week 1 should widen its intervals or reserves explicitly for that period, accepting a higher reserve cost — as coverage-targeting ACI does automatically.
- *Volatility increases defeat any method* that learns from a few weeks of history, including this one.

## Limitations {#sec:limits}

1. **No finite-sample guarantee.** For $0<\kappa<\infty$ the layer does not inherit the guarantee of split conformal prediction, and its per-building reliability is established empirically. Distribution-free per-series validity is impossible in general [@lin2022cptd]. GHCP keeps a marginal guarantee [@mallick2026] but adapts little per building.
2. **Exploratory status.** The recommended configuration and the reliability-aware rule were defined after interim and review results had been seen (Supplementary Table S1). Their benefit was consistent across both datasets, ten held-out sites, two cross-dataset transfers, a disjoint calibration period and the stress tests, but it has not been confirmed in a separately planned study.
3. **Data selection and setting.** The quality filter uses completeness in the target year, so very poorly metered buildings are excluded from the targets. Onboarding dates were sampled within existing meter histories. Real onboarding can coincide with commissioning problems or behaviour changes, which the level-shift and volatility tests only approximate. BDG2 uses observed temperature as a stand-in for weather forecasts; the UCI and cross-dataset runs use no weather and give the same qualitative results.
4. **Scope.** BDG2 is dominated by campus buildings in North America and Europe, and UCI has no metadata. Residential portfolios, industrial sites and other climates remain untested, as does any horizon beyond 56 days after metering.
5. **Abrupt changes.** Past own scores remain in the mixture, so level shifts and volatility increases during onboarding degrade all strategies. Self-only calibration was more reliable under added meter noise and an increase in volatility. Recency weighting of own scores, or combining shrinkage with online miscoverage control, are plausible but untested remedies.
6. **Baselines and metrics.** Large pretrained probabilistic forecasters [@emami2023] were not run, and the GHCP and TQA-B baselines are adaptations of methods designed for other settings. The operational metrics are stylised: booking failures and reserve cost translate the upper bound into a capacity reservation but do not model a specific market or contract.
7. **Per-building coverage is itself an estimate.** With about {{nvalid_BDG2_median}} hourly observations per building, its sampling noise (MACD ≈ {{floor_BDG2_macd}} for independent misses, more with autocorrelation) is of the same order as the differences among the best strategies. With ten BDG2 sites, site-level tests have limited power.

# Conclusion {#sec:conclusion}

Day-ahead prediction intervals are needed from the first days after a building is metered, and they must be reliable for each building, not just on average. Across {{n_bdg2_plus_uci}} buildings and clients from two public datasets, pooled conformalised quantile regression left {{main_BDG2_CQR_under_rate}} (BDG2) and {{main_UCI_CQR_under_rate}} (UCI) of new buildings clearly under-covered although their mean coverage was close to nominal.

Shrinking the pooled score distribution toward each building's own accumulating scores reduced these shares to {{main_BDG2_PCSCQR_under_rate}} and {{main_UCI_PCSCQR_under_rate}} at an unchanged interval score. The benefit held on two forecasters, at unseen sites and in cross-country transfer. Quantile-level shrinkage tuned the same way was equivalent. Adaptive conformal inference matched the reliability only with much wider intervals.

What mattered was how the shrinkage was tuned: for per-building reliability, or simply fixed at one week of hourly scores, not for the interval score. Similarity-weighted priors and onboarding-stage matching added nothing on the CQR score. No strategy of comparable width made the first week reliable, and none coped with a sharp increase in day-to-day volatility. Future work should address these two gaps, establish finite-sample guarantees for the shrinkage estimator and test the layer on pretrained forecasters and residential portfolios.
