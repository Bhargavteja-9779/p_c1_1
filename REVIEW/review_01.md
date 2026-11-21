# Review cycle 1 — consolidated report and action plan

Date: 2026-11-21. Packet: REVIEW/packet_cycle01.md (manuscript v1). Ten reviewer agents
(REVIEW/review_workflow.js). Full reports: REVIEW/review_01_full.md (raw: review_01_raw.json).

| Reviewer | Recommendation |
|---|---|
| R1 novelty/prior art | Major revision |
| R2 methodology | Major revision |
| R3 experimental design | Major revision |
| R4 statistics | Major revision |
| R5 data & leakage | Major revision |
| R6 robustness | Major revision |
| R7 computation | Minor revision |
| R8 literature | Minor revision |
| R9 associate editor | Major revision |
| R10 hostile competitor | Major revision |

## Convergent findings (raised by >= 3 reviewers)
1. **Headline method contradicted by own evidence** (R1, R2, R4, R6, R9, R10; Critical). Fixed one-week
   pseudo-count (HSC-CQR fixed-κ, = prior-art donor-local mixture) and the simple variant beat the full
   HSC-CQR on per-building reliability; stage matching and kNN prior slightly *hurt* on BDG2 (significant);
   LOBO interval-score selection of κ picks 336 h and trades reliability for sharpness.
2. **"Most reliable" not established vs QShrink-CQR** (R1, R3, R6, R9, R10).
3. **Pre-registration overstated** (R3, R5, R10): design changes after interim target results.
4. **No first-week benefit** despite "from the first days" framing (R6, R9, R10).
5. **Robustness/generalisation tables omit fixed-κ/simple** (R6, R10); per-site LSO hidden (R6).

## Single-reviewer Critical items
* R5: calibration windows lie in the training year (not out-of-time) -> pooled baselines biased.
* R10: a trivial warm-up switch (pooled CQR in week 1, then self-only CQR) matches tuned HSC-CQR.

## Action plan (revision 1)
| # | Issue (reviewers) | Severity | Action | Type | Status |
|---|---|---|---|---|---|
| A1 | Calibration scores not out-of-time (R5.1, R3.5) | Critical | New main protocol: training year < calibration windows (test-year H1, ending before 1 July) < target windows (test-year H2). All experiments recomputed; v1 (in-period calibration, same deterministic models) kept as comparison in the deviation log | rerun | running |
| A2 | Warm-up switch baseline (R10.1) | Critical | `Switch-CQR`: pooled CQR until n* days of own scores, then self-only CQR; n* by LOBO (same IS objective) from {1..28} | rerun | running |
| A3 | Fixed-κ beats tuned; LOBO-IS objective misaligned (R1.1, R2.2, R3.2, R4.2, R9.1, R10.2) | Critical | Reliability-aware selection rule added (`HSC-CQR cov-κ`: κ by LOBO mean absolute coverage deviation); both LOBO objectives stored for every candidate. Manuscript re-centred on the simple pseudo-count mixture; LOBO-IS presented as sharpness-oriented; fixed-κ credited to prior art | rerun + text | running |
| A4 | Ablation misreported (R2.1, R4.1) | Major | Ablation paired-test table; "refinements slightly hurt on BDG2" wording; day 1-7 coverage of ablations | analysis + text | pending |
| A5 | Confound in QShrink vs HSC comparison (R10.3) | Major | `QShrink-CQR fixed-λ` (λ = 168 h) vs `HSC-CQR fixed-κ` (κ = 168 h) | rerun | running |
| A6 | ACI handicapped (R3.3, R10.5, R6.7) | Moderate | `ACI-CQR clip` (working level clipped to [0.005, 0.5]); report cap-hit rates; median/HL effect sizes for IS | rerun + analysis | running |
| A7 | Site concentration, no site-conditional baseline (R5.3) | Major | `Mondrian-site CQR` (random protocol, BDG2); per-site coverage table; with/without Wolf | rerun + analysis | running |
| A8 | Stress tests benign/target-only (R6.3, R6.6) | Major | Added early level shift (day 5), volatility ×2 at day 28, 3-day outage, noise on calibration AND target, temperature-forecast error (AR(1), s.d. 2 °C, cal+target); core stress tests on UCI as well | rerun | running |
| A9 | Observed temperature as day-ahead input (R5.5) | Moderate | covered by A8 temperature-forecast-error condition | rerun | running |
| A10 | Interpolated truths evaluated (R5.6) | Moderate | interpolated hours excluded from scores and metrics (unit test) | rerun | running |
| A11 | Cluster-aware statistics (R4.3, R10.7) | Major | site-level sign tests / site-stratified permutation test next to building-level Wilcoxon; number of clusters stated | analysis | pending |
| A12 | Effect sizes vs tests mismatch; Holm families (R4.4, R4.5, R9.7) | Moderate | median paired difference / Hodges-Lehmann with bootstrap CI as primary; caption states families; primary vs exploratory families | analysis | pending |
| A13 | Robustness text omits where competitors win (R4.6, R6.5, R3.4) | Moderate | robustness paired-test table; per-condition winners stated | analysis + text | pending |
| A14 | Per-site LSO (R6.4) | Major | per-site LSO table, Wolf/Robin discussion | analysis | pending |
| A15 | Week-1 claims (R6.2, R9.5) | Major | week-1/week-2 per-building metrics in main tables; claims narrowed to evidence | analysis + text | pending |
| A16 | Pre-registration wording (R3.1, R5.2, R10.6) | Major | deviation table (item, date, trigger, target results seen?); post-hoc items labelled exploratory; CHANGELOG corrected; attrition table for the quality filter | text | pending |
| A17 | Wolf site audit (R5.4) | Major | load–temperature lag cross-correlation per site; interpolated-weather share per site | analysis | pending |
| A18 | Cost of wrong variant; timings under concurrency (R7.1-R7.4) | Major | isolated timing pass for HSC-CQR simple (per-building single-day latency + batch throughput, median/IQR); complexity statement; claims restricted | analysis + text | pending |
| A19 | Missing literature; credibility source (R1.4, R8.1, R8.2, R9.6) | Moderate | add Zhang et al. JMLR 2026 transfer conformal; Zhang & Candès posterior CP; Guan 2023 localized CP; Angelopoulos et al. conformal PID; Bühlmann credibility; Jin et al. 2022; preprint status flagged; [29] described only as far as verifiable | text | pending |
| A20 | Applied-energy value not quantified (R9.2) | Major | downstream case study: day-ahead reserve/flexibility commitment sized from interval bounds with asymmetric shortfall penalty, per building | analysis | pending |
| A21 | Length (R9.4) | Major | cut to ~7,000 words; ≤ 8 figures, 3-4 main tables; rest to Supplementary | text | pending |
| A22 | Novelty framing (R1, R9.3) | Critical | Title/highlights/contributions re-framed: benchmark + protocol + operational rule; mechanism credited to prior art | text | pending |

Deferred / not done (with reason, to be stated in the manuscript):
* Training-year-only quality filter rerun (R5.2): would change the building population and require
  all models retrained a second time; replaced by an attrition table and explicit disclosure.
* Residential dataset (R6.6) and conformal PID/SAOCP baseline (R8.1): out of scope of this revision;
  discussed as limitations.
