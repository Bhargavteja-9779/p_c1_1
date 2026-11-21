# R5 — Dataset and leakage review (cycle 2)

## Recommendation
**Major revision.**

## Summary
The feature pipeline is causal. `features.py` builds every load feature from days t−h..t−1 only, `hsc_quantiles` updates the own-score store only after computing the stage-h radius (calibration.py, `self_before` update), and all 14 tests pass (`pytest -q tests`: 14 passed). I found no duplicate meters: there is no pair with r > 0.98 among the 842 BDG2 or 315 UCI series. BDG2 temperature is in local time: the daily maximum falls at 14–16 h at all 10 sites. Observed weather is disclosed (Limitations 3), and the no-weather BDG2→BDG2 run keeps the same ordering (CQR 17.4% vs HSC-CQR recency 0.1% under-covered). Both datasets are CC-BY-4.0, cited correctly.

Two problems remain. The quality filter uses target-period data, and that removes a fifth of the eligible BDG2 buildings and four whole sites. The day-ahead information set also assumes all of day D−1 is observed, which helps the recency layer most. Smaller problems are a mismatch between the stated interpolation rule and the code, UCI daylight-saving and timestamp artefacts, and calibration scores computed in the same period the forecaster was trained on.

## Issues

**1. Major — Quality filter uses target-year data and changes which buildings and sites are studied (risk d).**
*Evidence.* `datasets.py:95-101` keeps a BDG2 building only if it passes the 5%-missing and 1 kWh/h rules in both 2016 and 2017. I re-ran the cleaning on the raw files. 1,050 of 1,578 meters pass in 2016, but only 842 pass in both years. So 208 buildings (19.8%) are removed only because of their 2017 (target-period) data. They include four complete sites that have usable 2016 data: Lamb (129 buildings; median 60% missing in 2017), Bobcat (21), Shrew (9) and Crow (5). A further 44 come from retained sites (Rat 19, Fox 7, Bull 7, …). UCI is barely affected (1 client). Section 3.1 says only "in every period used" and reports "842 buildings at 10 sites". It does not say that the 10 sites are themselves a result of target-year screening, and these are probably the meters with the hardest behaviour (outages, decommissioning). Leave-site-out claims ("unseen campuses") inherit the same selection.
*Action.* Filter training and calibration buildings on the training period only. Admit a target building if it passes in 2016 and has at least one window with ≥80% valid hours, and report how many buildings each criterion removes. Report the excluded sites in Section 3.1 and Limitations.
*Experiment.* Re-run the main BDG2 protocol (5 seeds) and leave-site-out on the relaxed set. Report the under-covered share (window and week 1) for CQR, ACI-CQR, the QShrink and HSC variants, and HSC-CQR recency.

**2. Major — The day-ahead information set assumes all of day D−1 is observed (risk e).**
*Evidence.* The forecast is "issued at the end of day t0+h−1" (Section 2.1). `lag1d`, `prev_mean/max/min` and the scale use all 24 hours of t−1 (features.py, `hist[:,0]` with k=1). In Eq. 4 the most recent own day (D−1) gets weight 1, and with ρ=0.95 the recency layer leans hardest on exactly those scores. The first-week claim (13.7% vs 23.8% under-covered, Section 4.3) depends on scores from the latest days. Real day-ahead nominations close around noon of D−1, and AMI data often arrive with a lag of a day or more. The manuscript never discusses this.
*Action.* State the information-set assumption explicitly.
*Experiment.* Run a gate-closure variant: features from days ≤D−2 plus hours 0–11 of D−1, and own scores only up to D−2 (also a one-day data-latency variant). Re-run the main comparison and the weekly analysis, and report whether the recency layer's first-week advantage survives.

**3. Moderate — Part of the pooled baselines' failure is a uniform level offset, not building heterogeneity.**
*Evidence.* Calibration windows lie in 2016, the same period as the forecaster's training rows from co-sited buildings (`experiments.py:89-92`). Targets lie in 2017. Mean pooled-CQR coverage is 0.891 (BDG2). If every building-seed row of `raw_results.csv.gz` (main, CQR, α=0.1) is shifted up by the mean bias (+0.0086), the under-covered share falls from 18.7% to 14.7%. About a fifth of the headline excess is therefore a shared offset. Any method that uses own scores, including ACI, absorbs that offset.
*Action/Experiment.* Report pooled-CQR leave-one-building-out coverage on the calibration buildings next to coverage on the targets. Add a run whose calibration windows are disjoint in time from the training rows (e.g. train January–August 2016, calibrate September–December 2016). Then split the pooled under-coverage into an offset part and a heterogeneity part.

**4. Minor — The interpolation rule in the code differs from the manuscript.**
*Evidence.* `datasets.py:68` calls `interpolate(limit=6, limit_area="inside")`. In pandas 3.0.5 this fills the first 6 hours of gaps of any length: `[1, NaN×10, 12]` becomes `[1, 2, …, 7, NaN×4, 12]`. Of the 39,043 imputed BDG2 hours, 17,418 (45%) are the leading hours of gaps longer than 6 h. Imputed hours are 0.25% of valid 2017 hours (99th percentile per building 2.3%, maximum 9.1%). They count as observed truth in own scores and in evaluation, and a straight line is easy to cover.
*Action.* Mask gaps longer than 6 h completely, flag imputed hours, and exclude them from evaluation scores. Run a one-seed sensitivity check.

**5. Minor — UCI daylight-saving artefacts and timestamp alignment.**
*Evidence.* In the raw `LD2011_2014.txt`, the readings labelled 2014-03-30 01:00–01:45 are zero for 68% of clients, and on 2014-10-26 they are roughly doubled. That block matches the documented "1–2 am", so labels mark interval starts. The code assumes they mark interval ends and shifts back 15 min (`datasets.py:127-128`), which puts every hourly value 15 min out of step. The DST hours are not masked. My cube shows hour 0 at 0.79× its week-earlier value in March and 1.2× in October. About 36% of the 2014 target windows contain one of these days, and the artefacts also enter training and calibration. The effect on coverage is at most about 0.15 points per building.
*Action.* Fix the alignment, mask the DST hours, and document both.

**6. Minor — The unit of the headline share does not match Section 3.5.**
*Evidence.* Section 3.5 says metrics are averaged over the seeds in which a building was a target. But 18.7% is the share of building-seed rows (1,265 rows). Averaging per building gives 15.4% (713 buildings).
*Action.* Use one unit throughout, and recompute the noise floor on the same unit.

**7. Minor — Data hygiene details.**
Weather gaps are interpolated without limit and extrapolated at both ends (`datasets.py:111`). Moose has a 202-h gap and 3.9% missing. The fallback `rng.choice(starts)` in `onboard_dates` (pipeline.py:133) silently admits windows with less than 80% valid hours.
*Action.* Cap weather interpolation, and log or forbid the fallback.
