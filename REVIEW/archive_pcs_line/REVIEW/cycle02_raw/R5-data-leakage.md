# R5 Dataset & leakage, cycle 2: Major revision

## Recommendation
**Major revision.**

## Summary
Several cycle-1 items are resolved:
- Hours are scored only when observed (`pipeline.py:190-191`).
- UCI daylight-saving hours are masked (`datasets.py:166-171`).
- Weather interpolation is capped at 6 h.
- Site weather is in local time. I re-checked this: the diurnal peak falls at 14–16 h at all 10 sites.
- LOSO now uses 10 sites × 3 seeds, and LOBO can be grouped by site.
- Data checksums are recorded, and there are no onboarding fallbacks (`run_info.json`: 177 × `[]`).
- The causality tests were extended, and all 15 tests pass.

Two problems remain. First, the headline reliability claim is not supported by the paper's own per-week table. Second, the target-year quality filter was kept for a reason that no longer holds, and it biases the target population toward regular buildings.

## Issues

**1. Critical: the "1.4 %" headline is a 56-day aggregate that hides 11–20 % sub-window under-coverage.**
*Evidence.* T_weeks_BDG2 gives PCS-CQR under-covered shares of 19.4 % (week 1), 19.8 % (week 2), 15.3 % (weeks 3–4) and 11.0 % (weeks 5–8), against 1.4 % over the full window. UCI shows 10.3 / 12.2 / 8.6 / 4.4 % against 0.4 %.

From `raw_results_main.csv.gz` I computed:
- 10.0 % of BDG2 PCS-CQR building×seed units are below 0.85 in weeks 5–8 (672 h) yet count as reliable over 56 days.
- Per building, corr(cov_w1, cov_w58) is −0.22 for PCS-CQR, against +0.44 for CQR. Early misses are offset by later over-coverage, which is consistent with old own scores staying in the mixture.
- Coverage-only ACI reaches 0.0 % in weeks 5–8, so the 11 % is not an unavoidable floor.

Several statements are therefore contradicted:
- Highlight 3: "restores reliability".
- Abstract: only week 1 is singled out as not repaired, but week 2 is no better.
- §6.3: "keeps the share … small after the first week".
- §6.1: "largely removes".

*Action.* Report window-length-matched shares as co-primary, for example rolling 7- and 28-day windows. Restate the abstract, highlights, §6.3 and the conclusion, naming week 2 and weeks 5–8.

*Experiment.* Under-covered share over rolling 28-day windows for all CQR-score strategies, using the stored intervals. No retraining is needed.

**2. Major: the target-year quality filter (cycle-1 #1) is not resolved, and the stated reason is wrong.**
*Evidence.* The response says "a forecast cannot be evaluated where truth is missing". The revised pipeline already handles this: it scores only observed hours and requires windows with at least 80 % valid hours. I re-ran `_clean_hourly` and the filter rules (`datasets.py:79-90`):
- 1,050 buildings pass the rule in 2016. Of these, 208 (20 %) are removed only by the 2017 rule.
- 164 of the 208 have at least one 57-day window in 2017 with at least 80 % valid hours, so they could be evaluated.
- Four whole sites are dropped only for this reason: Lamb 129, Bobcat 21, Crow 5, Shrew 9.
- Their 2016 day-to-day variability (median |Δdaily|/mean) is 0.212, against 0.085 for retained buildings.

The excluded group is 2.5× more volatile, and volatility is the condition under which every method fails (Table 3). §4.1/§6.4 call them "very poorly metered", which is not accurate. `*_exclusion.json` gives no per-period or per-site breakdown.

*Action.* Apply the filter to the training/calibration period only. Report the exclusion flow by period and site, and compare characteristics of included and excluded buildings.

*Experiment.* Main and LOSO protocols with the causal filter. This adds about 164 targets and 4 sites.

**3. Major: the day-ahead information set assumes all of day t−1 is known.**
*Evidence.* `features.py:77-99` uses lag1d, prev_* and daily_var over hours 0–23 of t−1. The PCS, ACI and TQA-B updates also use day-(t−1) scores for day t (`calibration.py:223, 254-256, 334`). The paper motivates the work with flexibility bidding (abstract, §1). Day-ahead gate closure is typically around noon on D−1, so hours 12–23 of D−1, and their scores, are not yet available. Faster own-score adaptation is the mechanism credited for PCS's gains.

*Action.* Define the issuance time explicitly, or limit the claims.

*Experiment.* Rerun the main protocol, at least for BDG2, with features and own scores restricted to data before 12:00 on D−1, or simply lagged one extra day.

**4. Moderate: the sampling floor assumes independent misses.**
*Evidence.* `values.py:180-189` simulates the floor as Binomial(n, 0.9), giving 0.00 % for 56 days and 1.7 % for 168 h. Load misses cluster within days. With day-level clustering, the week-1 floor (Binomial(7, 0.9)) is about 15 %, which is comparable to PCS's 19.4 %. The claims "first-week failures are real" (§5.5) and "not sampling artefacts" (§5.1) rest on this independence assumption. Issue 1 also depends on it: either the sub-window failures are real, or the floor is mis-stated.

*Action/Experiment.* Compute the floor with a block bootstrap, using the empirical within-building autocorrelation of misses under the best-calibrated method, for each window length.

**5. Moderate: upstream cleaning and non-causal input processing remain.**
*Evidence.* The truth comes from BDG2's *cleaned* meters (`datasets.py:32`), which the dataset authors processed using whole-series information. The response's statement that "evaluation truth is no longer cleaned" is therefore only partly true. In addition:
- Stuck-run masking needs up to 24 h of future readings (`datasets.py:66-72`).
- Linear interpolation fills a gap from both sides (`:75`). A gap at the end of day t−1 is filled using target-day readings, and gaps on onboarding day t0 use data from before metering started. About 0.27 % of BDG2 hours are interpolated (share_finite − share_obs).
- The tests run on the cleaned data cube, so they cannot detect this.

*Action.* State that upstream cleaning was used. Apply cleaning causally to history inputs, or forward-fill only. Add a test that perturbs raw readings at t and beyond and checks that features at t do not change.

*Experiment.* A raw-meter sensitivity run on one seed.

**6. Minor: reporting and disclosure.**
- The 80 %-window rule was added after the analysis plan (5d857b6, 7 minutes after e9ca94d). It is missing from Table S1, which claims to list every change.
- The 80 %-window rule counts interpolated hours as valid (`pipeline.py:134`). So does the 5 % rule: `obs` is passed to `_filter_flow` but never used.
- §5.1 says "fewer than 0.00% of buildings", a formatting artefact.
- "1344 observed hours per building" is the median; the minimum is 946.
- Table 3 lists LOSO "Runs" as 3, while the protocol has 30 forecasters.

*Action.* Correct each item.
