# REVIEW_HISTORY

Ten reviewer perspectives (R1 novelty/prior art, R2 methodology, R3 experimental design, R4 statistics,
R5 data & leakage, R6 robustness & generalisation, R7 computation, R8 literature & citations,
R9 associate editor, R10 hostile competitor) review the complete package in each of 10 cycles.
Per-cycle consolidated reviews: REVIEW/review_XX.md. Corrective actions: CHANGELOG.md.

## Pre-review self-audit (author, before cycle 1)
| Issue | Severity | Action | Status |
|---|---|---|---|
| Stuck-meter artefacts (Lamb site) inflate errors ~80x | Critical | stuck-run masking rule; training filter y/s<=20 | fixed (before full run) |
| HSC-CQR missing in robustness experiments | Major | moved out of ablation-only block | fixed |
| Same-score competitors for HSC-CQR missing (self-only, ACI on CQR) | Major | Self-CQR, ACI-CQR added | fixed (before full run) |
| HSC-CQR lacked component ablation | Major | -stage, -kNN, -shrink for HSC-CQR | fixed (before full run) |
| Descriptor described as "first h days" but uses last min(h,28) days | Minor | manuscript corrected | fixed |
| First full-run look (seed 0 BDG2): kNN localisation and stage matching show ~no benefit; ACI-CQR close to HSC-CQR | Major (claims) | do not claim benefit of these components unless supported across seeds/datasets; report honestly | pending full results |

## Cycle 1 (2026-11-20) — consolidated in REVIEW/review_01.md
Recommendations: 9 Major revision, 1 Minor revision. Top issues: fixed kappa=168 beats LOBO-tuned headline
method (A1); headline numbers from the full kNN/stage variant the paper calls unnecessary (A2); pre-registration
overstated, deviations undisclosed (A3); no week-1 gain (A4); site-clustered inference, ACI cap handicap,
'most reliable' outside main protocol, no operational payoff, data-filter/cleaning issues, length, literature.
Status: addressed in revision 1 (2026-11-21); point-by-point response in REVIEW/response_01.md. Method re-centred
on PCS-CQR with reliability-aware tuning (fixed kappa=168 reported everywhere); deviations table (Supp. Table S1);
week-wise metrics with explicit 'no week-1 repair' claim; site sign-flip tests; ACI fallback fix; LOSO 10x3,
disjoint period, new stress tests, small pools, 80/95 %; operational metrics; observed-hour scoring; ~8.4k words.
Not done: causal (training-period-only) quality filter (discussed as a limitation); full market case study.

## Cycle 2 (2026-11-21) — consolidated in REVIEW/review_02.md
Recommendations: 8 Major revision, 2 Minor revision. Top issues: the 56-day headline hides sub-window
under-coverage (PCS-CQR 11–20 % per window on BDG2, 41 % fail at least one window after week 1; ACI (MACD) better in
weeks 5–8) (A1); ACI wins at 80 % nominal and with small pools, and its LOBO objective is computed asymmetrically
and its grid is truncated (A2); claims stronger than the tables: fixed κ "without data", "equally well", tuning p = 0.164,
week-1 exceptions, operational payoff not significant (A3); target-year filter and day-ahead information set (B1).
Status: pending (corrective plan in review_02.md).
