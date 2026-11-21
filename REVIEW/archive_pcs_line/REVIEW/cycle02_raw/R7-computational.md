# R7 – Computational efficiency reviewer, cycle 2

## Recommendation
**Minor revision.** This is the computational perspective only.

## Summary
The revision fixes the main cycle-1 cost problems. The recommended layer (PCS-CQR) is now timed. Every CQR-score strategy has a tuning and application time (T_cost_strategies). Single-building latency is measured separately (latency.json: median 0.023 ms, IQR 0.023–0.024, 2000 reps, one core). Medians replace means, and the batch time is labelled "amortised". I checked that the benchmark function `daily_update` (src/statistics/latency.py:21-26) gives the same radii as the evaluated code `hsc_quantiles(..., stage_matched=False)`. It matches to float32 precision on 5 synthetic targets × 55 days (scratch check). So the 0.023 ms figure does measure the recommended layer. The cost statements in the abstract and conclusion ("well under a millisecond", "a few hundredths of a millisecond") agree with MS_cost and latency.json. The negligible cost justifies the reliability gain. Five smaller problems remain: two unresolved cycle-1 items and three descriptions that do not match the code.

## Issues

**1. Moderate – "LightGBM inference" still times only the point model, and end-to-end daily latency is still missing (cycle-1 item not resolved).**
*Evidence:* pipeline.py:174-177 starts the timer before `models["lgb"].predict` and stops it immediately after. The two quantile models that actually produce the CQR bounds (lines 178-179) and feature construction are outside the timer. MS_cost reports this number as "LightGBM inference (ms / building-day)": 0.79 for BDG2. The per-seed values (T_efficiency) range from 0.15 to 1.39 ms, a 9× spread. Tree counts explain only part of it: seed 0 has 898 point-model trees and 0.79 ms, seed 2 has 660 trees and 0.15 ms. A single `time.time()` call was made while four workers ran on four cores.
*Action:* Time feature construction plus the two quantile predictions plus the PCS update for one building-day, single-threaded and repeated. Report the median and IQR, and rename the column. State that the forecaster, not the calibration layer, dominates the daily cost (about 0.8 ms vs 0.023 ms).
*Experiment:* Micro-benchmark on cached models (minutes).

**2. Moderate – The per-building state is described as "16 kB as implemented", but the evaluated code uses 28× more.**
*Evidence:* Section 5.7: "The per-building state is 16 kB as implemented." The pipeline keeps a target's own counts as `(nt, 56, 4000)` int16 (calibration.py:48), which is 448 kB per building. The 16 kB comes from the separate benchmark (int32 vector, latency.py:35). T_efficiency's `pcs_store_MB = 0.016` measures something else: the *shared* prior as float32 (pipeline.py:439). latency.json, however, gives `prior_kB = 32` (float64). One 16 kB figure therefore stands for two different objects, and two different sizes are given for the prior.
*Action:* Write "16 kB in a streaming deployment (one running int32 count vector; at most 1344 raw scores, about 5 kB, also suffice); the research harness stores per-stage counts". Relabel the T_efficiency column as "shared prior" and give one prior size.
*Experiment:* None.

**3. Minor – The effect of the 4000-point grid is asserted, not checked (cycle-1 item not resolved).**
*Evidence:* Section 3 now states "relative spacing about 0.5 %, rounded upwards", but no grid-vs-exact comparison was run. My check with `make_grid` gives a relative step of 0.48 % for scores ≥ 0.05·s, 0.68 % at 0.01·s and 4.8 % at 0.001·s. The CQR radius can be near zero, where the relative error is largest. On synthetic N(0, 0.1) scores, the grid's 90 % split-conformal radius was +0.37 % above the exact one. Probably negligible against MACD differences (0.015 vs 0.039), but not shown on real scores.
*Action:* For one seed per dataset, report the coverage and width difference between grid and exact sorted-score quantiles for CQR and PCS-CQR. Alternatively, run with 16 000 points and show the table does not change.
*Experiment:* Calibration-only rerun of one seed (seconds to minutes).

**4. Minor – Training times are still affected by uncontrolled contention, and the model count is mislabelled.**
*Evidence:* LightGBM training takes 70–289 s for nearly identical training sets (1.318–1.323 M rows). The times do not follow model size. Seed 4 has the most trees (1918 + 1273 + 609) but took 107 s. Seed 1 has fewer trees (1249 + 1010 + 531) but took 289 s. Section 5.7 says "Training the three LightGBM *quantile* models takes 107 s". In fact pipeline.py:114-116 trains one point model and two quantile models. CQR needs only the two quantile models.
*Action:* Correct the wording. Report training time per model, or give the range in the text, and say the times were not controlled for contention. Deployment needs only the two quantile models.
*Experiment:* None, or retrain one seed on an idle machine (optional).

**5. Minor – Cost wording and scaling.**
*Evidence:*
(a) "Batch-updating 10 000 buildings takes 0.3 s" describes a sequential Python loop of single updates (latency.py:47-48), not a vectorised batch.
(b) "Selecting κ by LOBO takes 1.1 s, against 29.1 s for the pre-registered design" compares tuning alone (PCS) with tuning plus application (HSC-CQR). The like-for-like figures are 1.33 s vs 29.1 s.
(c) Section 6.3 claims compatibility with portfolio-scale deployment "including with pretrained forecasting models". LOBO tuning was tested only with the pools of this study. Its memory grows as M × 56 × 4000 int16 (tune_hsc → `cum_counts`), about 4.5 GB at M = 10⁴ calibration buildings. Pretrained models were not run.
(d) Section 5.1 prints "fewer than 0.00% of buildings would fall below 0.85". This is a rounding artefact from values.py.
*Action:*
(a) Write "updating 10 000 buildings sequentially on one core".
(b) Compare like for like.
(c) Give the O(|κ|·NH·M·G) time and memory of LOBO tuning, and either soften the deployment sentence or show a resampled scaling run (M = 10³ and 10⁴).
(d) Print "< 0.01 %" or give the exact probability.
*Experiment:* Optional synthetic scaling run of `tune_hsc`.

## Checks of claims against tables (computational and headline numbers)
These all match:
- Abstract and conclusion percentages: 18.2/9.1 → 1.4/0.4 (Table 1 and T_main_UCI).
- Width ratios: BDG2 0.949/0.391 = 2.43, UCI 0.330/0.266 = 1.24.
- Week-1 share: 19.4 %.
- PCS width +2 %: 0.391/0.382.
- Abstract length: 230 words, within the 250-word limit.

One wording problem: the introduction and conclusion say ACI needs "much wider" intervals. On UCI it needs only 1.24× the width, with interval score 0.430 vs 0.367. Use "wider (2.4× BDG2, 1.2× UCI)".
