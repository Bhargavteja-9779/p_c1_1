| Method | Tuned parameter | Grid (values) | Objective (LOBO on calibration buildings) |
|:--|:--|:--|:--|
| SSC-CQR (primary), SSC (abs), SSC-CQR (MLP) | pseudo-count κ (h) | 0, 24, 48, 96, 168, 336, 672, 1344, ∞ (9) | MACD, IS tie-break |
| SSC-CQR (IS-tuned) | κ | same (9) | interval score |
| SSC-CQR (κ=168), QShrink-CQR (λ=168) | – | fixed | – |
| SSC(-CQR) +stage+kNN and ablations | κ, K | 9 × {10, 25, 50, 100, all} (45) | interval score (pre-registered) |
| QShrink-CQR | λ (h) | as κ (9) | MACD, IS tie-break |
| Self-CQR-fb | minimum own history (h) | 72, 168, 336 (3) | MACD, IS tie-break |
| ACI, ACI-CQR | step size γ | 0, 1e-4, 2e-4, 5e-4, 1e-3, 2e-3, 5e-3, 1e-2, 2e-2, 5e-2 (10) | MACD, IS tie-break |
| TQA-B-CQR | decay β | 0.5, 0.8, 0.95 (3) | MACD, IS tie-break |
| GHCP-CQR | surrogate group size (h) | 24, 168, 672 (3) | MACD, IS tie-break |
| SCP, SCP-stage, CQR, Mondrian, Self-CP, Self-CQR | – | – | – |
