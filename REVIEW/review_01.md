# Reviewer #1 report: "Reliable day-ahead prediction intervals for newly metered buildings: a building-level comparison of conformal calibration strategies"

## Summary of the submission
The authors train one global, scale-normalised LightGBM forecaster with history-length masking. They then compare about 20 interval-calibration strategies for "newly metered" buildings over a simulated 56-day onboarding window, on BDG2 (842 buildings, 10 sites) and UCI (315 clients), with 5 seeds. They also run leave-site-out, cross-dataset and stress tests. The main finding is that a Dirichlet-process/credibility mixture of a pooled score distribution with the building's own accumulating CQR scores (HSC-CQR) cuts the share of under-covered buildings from 18.7% to 3.4% (BDG2) and from 9.5% to 0.6% (UCI) at an unchanged median interval score. The kNN prior and stage-matching components add nothing. The authors say themselves that the mechanism is not new, so the contribution is a benchmark plus design evidence.

## Recommendation
**Major revision**, close to reject for this venue. The engineering is careful and transparent. However, the headline claims do not match the authors' own result files in three places: the first-week claim, which method is "most reliable", and what was pre-registered. The applied-energy significance is also not shown.

## Issues

**1. MAJOR: No improvement in the first week, which is the setting the paper is built around.**
Evidence: the title, abstract ("from the first days after a building is metered"), Section 3.1 ("from the first days") and Section 6.3 ("keeps the share … small throughout onboarding") all stress early reliability. I recomputed the first week from `results/raw_results.csv.gz` (column `coverage_early`, main, α=0.1, mean over seeds). Share of buildings under-covered in week 1:
- BDG2: HSC-CQR 24.5% vs CQR 23.8%.
- UCI: HSC-CQR 17.5% vs CQR 16.0%.

So HSC-CQR is slightly *worse* than pooled CQR in week 1. For weeks 2–8 the shares are 4.9% vs 18.5% (BDG2) and 1.3% vs 10.3% (UCI). Table 2 agrees: mean week-1 coverage is 0.885 for HSC-CQR vs 0.892 for CQR, and in Fig. 5a HSC-CQR's day-1 coverage (~0.868) is below CQR's. All of the reported gain comes from week 2 onward.
Fix (no new experiment needed): report reliability by stage (week 1 / 2 / 3–8), including MACD and under-covered share, in the main tables. Rewrite the title, abstract, highlights and Section 6.3 so they do not imply reliability "from the first days". If early reliability is the aim, the method needs to be redesigned. Since the -shrink variant shows the building-weighted kNN prior is worse than plain CQR (21.7% vs 18.7%), the cold-start prior is the place to work.

**2. MAJOR: The "most reliable strategy" is a fixed-pseudo-count prior-art variant, not the tuned layer.**
Evidence:
- Table 5 / `T_ablation_BDG2`: HSC-CQR fixed-κ (κ=168, which the authors equate with the donor–local mixture of [29]) has MACD 0.015 and 1.9% under-covered, vs 0.018 and 3.4% for the tuned HSC-CQR.
- In Table 4 the paired test favours fixed-κ: r_rb = −0.45, p<0.001, and HSC-CQR is better for only 31% of buildings.
- In week 1 fixed-κ is also best (19.8% vs 24.5%, my computation).
- The selection objective is mis-aligned. In Fig. 9c the interval score varies only from 0.562 to 0.573 across the whole κ grid, while MACD varies 2.5-fold. LOBO-on-IS therefore picks κ=336 in 9/10 main runs (`results/run_info.json`), which is far from the MACD optimum of 96–168.

The abstract's sentence "pseudo-count selected by leave-one-building-out … most reliable", and contribution 3, therefore misstate the evidence. The best reliability came from a fixed κ that the authors attribute to prior work.
Fix: either select κ with a reliability-aware objective chosen on calibration buildings (e.g. IS subject to a constraint on the LOBO under-covered share) and report it as the primary variant, or state plainly that a fixed one-week pseudo-count as in [29] is at least as good and that LOBO tuning adds nothing. This needs a re-run of the calibration pass only, not retraining.

**3. MAJOR: The pre-registration claim is overstated and the deviations are buried.**
Evidence: `experiments/PREREGISTRATION.md` was committed in the same commit as the implementation (e9ca94d). It is not an external registration. Its baseline list does not include GHCP-CQR, QShrink-CQR, TQA-B-CQR, the simple variants, fixed-κ or the MLP variants. These were added on 2026-11-16, after the "first full-run look (seed 0 BDG2)" recorded in REVIEW_HISTORY. The ACI γ grid was also changed after the results were seen (CHANGELOG item 7). The pre-registered α∈{0.05, 0.2} analysis (E7) was not run for any CQR-based method; `raw_results` contains HSC-CQR only at α=0.1. The pre-registered hypothesis (kNN plus stage matching improves IS) was not supported. The abstract nevertheless calls the protocol "pre-registered".
Fix: add a deviations table to the main text listing each post-hoc addition, the change to the γ grid and the claims that were not supported. Replace "pre-registered" with "a protocol fixed in an internal, version-controlled design file". Run E7 (α=0.05, 0.2) for all CQR-score methods: a calibration-only re-run. Note that on the absolute score, Self-CP already beats or matches HSC at 95% (MACD 0.017 vs 0.019) and at 80% (0.038 vs 0.039).

**4. MAJOR: A natural, principled baseline is missing: building-specific normalisation of the scores.**
Evidence: the paper's own explanation (Section 6.1) is that some buildings have systematically larger errors. The textbook remedy is locally weighted (normalised) conformal prediction. Each score is divided by a running estimate of the building's own error scale (e.g. the mean absolute CQR residual over the last 7 days, with a population fallback), and the quantile is then pooled. This keeps pooled calibration but adapts per building. Weighted/recency conformal prediction ([42], NexCP), which is cited, is also not run, even though Limitation 6 names recency weighting as a remedy.
Fix (new experiment, calibration-only): add (a) normalised-score pooled CQR with a building running scale and (b) NexCP-style recency-weighted calibration on own plus pooled scores. Evaluate both under the main protocol and the level-shift stress tests.

**5. MAJOR: Significance for an applied-energy journal is not demonstrated.**
Evidence: all outcomes are statistical (MACD, under-coverage, interval score). No downstream task is evaluated: demand-response baseline settlement errors, flexibility-bid penalties, M&V uncertainty or false-alarm rates. These are invoked in the abstract and in Section 6.3 but never quantified. The gain in median interval score is nil (0.564 vs 0.564), and the MACD gain (0.038 → 0.018) has no operational interpretation.
Fix (new experiment): at least one decision-level case study. For example, a DR baseline with an asymmetric penalty for under-delivery, or a day-ahead bid with an imbalance cost. Report the cost per building and its tail across buildings for CQR, QShrink, fixed-κ and HSC-CQR.

**6. MODERATE: The noise floor and statistical inference are not quantified.**
Evidence: the stated MACD floor of 0.0066 assumes independent hourly misses. The authors admit misses are autocorrelated but give no number, so it is unclear whether 0.015 vs 0.018 vs 0.022 differ beyond noise. Under-coverage below 0.85 is a hard threshold on noisy estimates. The Wilcoxon tests treat 713 buildings as independent although Rat alone contributes 218 of them (31%) and Moose only 5. With 10 clusters, the site-cluster bootstrap is unreliable, and the confidence intervals sometimes conflict with the tests: QShrink IS CI [−0.0098, −0.0000] alongside p=0.688.
Fix (calibration-only): estimate the floor with an oracle (each building calibrated on its own scores from a disjoint later window) or with a day-block bootstrap of hourly coverage. Use a mixed model or a site-stratified permutation test. Report results with Rat excluded.

**7. MODERATE: Stress-test reporting is selective.**
Evidence: Section 5.5 highlights HSC-CQR's 1.7% under 15% noise but does not mention that Self-CQR does better (0.010 / 0.1%; Self-CP 0.019 / 2.0%). With a 10% calibration pool, QShrink (5.9%) and HSC-CQR simple (6.2%) beat HSC-CQR (7.9%). Under leave-site-out, HSC-CQR (5.3%) is worse than QShrink (4.2%) and the simple variant (3.5%), with fold standard deviations up to ±17.6. The SCP-stage figure quoted in the text (100% under-covered) is not in Table 6.
Fix: no new experiment. Report the winner per condition neutrally, and add SCP-stage and fixed-κ to Table 6.

**8. MODERATE: The ACI baselines are degenerate.**
Evidence: when α_h≤0 the radius jumps to the grid cap of 500·s (`src/models/calibration.py:231`). On UCI, ACI-CQR produces relative widths up to 335× mean load and relative IS up to 336, so its mean paired IS difference is −1.91 (Table 4). Medians hide this. The daily batched update γ·Σ_24 is also non-standard.
Fix: report how often infinite or capped intervals occur. Use the aggregated/expert ACI [21] or a clipped α_h. Calibration-only re-run.

**9. MODERATE: TQA-B uses target-batch information.**
Evidence: `calibration.py:325-326` sets λ from `g.max()` over *all target buildings* at each stage. This is transductive: each building's interval depends on the other new buildings.
Fix: compute λ from calibration buildings only and re-run.

**10. MODERATE: The forecaster baselines are dated.**
Evidence: the "DeepAR-spirit" MLP is not DeepAR, and no pretrained model (e.g. BuildingsBench [13]) is run, even though the paper argues that the layer is compatible with pretrained forecasters. Weather is observed, not forecast (Limitation 3), which flatters point accuracy.
Fix (new experiment): apply CQR and HSC-CQR to at least one pretrained zero-shot probabilistic model on BDG2, on CPU-feasible subsets if necessary. Add a run with perturbed or forecast-like temperatures.

**11. MINOR: Inconsistencies.**
- The abstract's figure of 0.437 ms is the timing of the absolute-score HSC with kNN (`pipeline.py:317-321`), not of the recommended "one-parameter layer".
- Headline numbers use the full HSC-CQR, while the text recommends the simple variant.
- Stage bin {28..56} in the text vs "28+" in the code.
- Fig. 9 omits κ=0 although it is on the grid.
- Table 2 (22 rows) and Table 7 (45 rows) are too long for a ~12-page article; move them to the SI.
- Several key references, including the closest prior art [25–27, 29, 49], are 2026 preprints or a Zenodo software record [29]. I verified [25]. The others should be checked, and [29] should be cited together with any accompanying paper.

**12. MINOR: Compliance.**
The highlights (≤85 characters) and the abstract (215 words) comply. The AI-use declaration says the AI "executed the experiments". The editor should confirm that this is acceptable under Elsevier policy. The repository URL is still a placeholder, and the CRediT section is unfinished.

---
## Author response and actions (cycle 1)

| # | Verified? | Action | Status |
|---|---|---|---|
| 1 First-week claim | **Confirmed** (BDG2 week-1 under-covered: HSC-CQR 24.5 %, CQR 23.8 %) | Pre-registered H-B (stage-wise studentised conformal, SSC-CQR; HSC on studentised scores) and H-C (recency weighting) targeting the first weeks; stage-resolved reporting; claims rewritten | code done; full rerun pending |
| 2 Fixed-κ beats tuned κ | **Confirmed** (objective mismatch) | Pre-registered H-A: LOBO per-building-coverage objective, applied alike to HSC, QShrink and ACI; reliability–sharpness frontier over all parameter grids (`ex.frontier`) | code done; rerun pending |
| 3 Pre-registration wording | Confirmed (internal protocol, committed with code) | Wording: "internal analysis protocol fixed before the full experiments"; deviations table in Supplementary; α-sweep now includes all CQR methods | pending manuscript |
| 4 Missing baselines (locally weighted / recency) | Accepted | SSC-CQR (running own-scale normalisation, Dunn-style pooled-CDF), HSC-CQR recency (NexCP-type decay) | code done |
| 5 Applied significance | Accepted | Operational outcomes pre-specified: tail exceedances, under-protected buildings, capacity-headroom cost at three penalty ratios | code done (metrics) |
| 6 Noise floor / clustering | Confirmed (day-block floor ≈ 0.016 on seed 0, not 0.0066) | Day-block SE per building; site-level paired test; Rat-excluded sensitivity | code (metric) done; analysis pending |
| 7 Selective stress reporting | Confirmed | Text to report all winners per condition (incl. Self-CQR under 15 % noise) | pending manuscript |
| 8 ACI grid cap | Confirmed (`calibration.py` lev ≥ 1 → 500·s) | Finite surrogate (largest observed calibration score); frequency logged (seed 0: 0.44 % abs, 0.04 % CQR of building-days) | done |
| 9 TQA-B target-batch λ | **Confirmed bug** | λ from calibration buildings; unit test that a target's interval is invariant to other targets | done |
| 10 Pretrained model / observed weather | Partly | No-weather BDG2 runs exist (Table 7); pretrained models remain a stated limitation (CPU budget) | limitation |
| 11 Inconsistencies | Accepted | timing for the recommended layer; κ = 0 in sensitivity; long tables to Supplementary | pending manuscript |
| 12 Compliance | Accepted | AI statement rephrased to Elsevier wording; placeholders flagged for authors | pending manuscript |

Reproducibility check (cycle 1): models retrained from scratch in a fresh container reproduce the committed
per-building coverages of seed 0 exactly (max |Δ| = 1e-16 for CQR, HSC-CQR, HSC-CQR simple, QShrink-CQR,
Self-CQR, GHCP-CQR).

Pipeline check on seed 0 (BDG2; not a reported result) revealed a further issue that changes the framing:
ACI-CQR tuned on per-building coverage reaches MACD 0.004 / 0 % under-covered but doubles the interval score
(1.06 vs 0.55) — per-building coverage alone can be enforced by aggressive online level control. The study
must therefore evaluate the reliability–sharpness trade-off (frontier), not MACD alone.
