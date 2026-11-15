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
