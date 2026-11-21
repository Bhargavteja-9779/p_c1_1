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

## Cycle 1 (Reviewer 1, general; REVIEW/review_01.md) — resolved in manuscript v2
| Issue | Resolution |
|---|---|
| No week-1 gain | Pre-registered recency weighting + coverage objective (Addendum A); week-1 under-covered share now reported (BDG2 23.8 % → 13.7 %, UCI 16.0 % → 5.9 %); weekly figure with noise reference |
| Fixed κ beat tuned κ (objective mismatch) | Coverage objective for HSC, QShrink and ACI alike; frontier over all parameter grids |
| Pre-registration overstated | Reworded as internal protocol + committed addendum; deviations in Supplementary S4 |
| Missing baselines (scale-normalised, recency) | SSC-CQR, HSC-SSC-CQR (with Proposition 1, HCP-based), recency variant |
| No applied significance | Capacity-headroom cost (ρ = 10/20/40) and under-protected share; result: average cost unchanged, risk redistributed (reported as such) |
| Noise floor / clustering | Day-block SE per building; under-share noise reference; site-level tests (Table S5) |
| ACI grid cap; TQA-B target batch | Fixed (finite surrogate; λ from calibration buildings; unit test) |
| Selective stress reporting | Table 2 reports all key strategies per condition; exceptions stated (α = 0.2 ACI, HSC-SSC in two conditions) |
| Length/structure vs journal | v2 restructured to AAE pattern (literature/aae_fulltext_benchmark.md) |

## Cycle 2 (10 reviewers; REVIEW/review_02.md) — fixes in progress
All 10: Major revision; R9 (AE): not desk-rejected. Core result vs pooled CQR reproduced by all.
| Issue | Planned resolution | Status |
|---|---|---|
| Window headline hides weekly under-coverage (~1 in 5 buildings per week) | weekly/worst-week metrics in main text; 0.4 % labelled window metric | open |
| ACI tuned asymmetrically (grid edge γ=0.01; excluded post hoc) | constrained LOBO (min MACD s.t. IS ≤ 1.02×pooled) for every family; rule A.1 re-applied | open |
| Noise reference method-dependent, not a floor | one method-independent 7-day block-bootstrap oracle reference | open |
| D−1 information set; target-year filter; interpolation/DST | delayed-own-score variant; SSC-line data rules ported; full rerun | open |
| Mean IS / tail blow-ups hidden | mean+median IS, tails, TOST; safeguard variant | open |
| Week-1 gain from κ not recency; distribution-vs-quantile claim | matched-κ attribution; QShrink/Self recency variants; family-level framing | open |
| Selection on target data | nested selection, bootstrap selection frequencies | open |
| Novelty (Shahid n0 selection), missing refs, Prop. 1 premises, ESS ×24 | reframe; corollary; corrected bound | open |
