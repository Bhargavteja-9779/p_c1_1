| Method | Tuned parameter | Grid (values) | Objective (LOBO on calibration buildings) |
|:--|:--|:--|:--|
| SSC-CQR (primary), SSC (abs), SSC-CQR (MLP) | pseudo-count κ (h) | 0, 24, 48, 96, 168, 336, 672, 1344, ∞ (9) | sharpest with ≤ 5 % under-covered |
| SSC-CQR (IS-tuned) | κ | same (9) | interval score |
| SSC-CQR (κ=168), QShrink-CQR (λ=168) | – | fixed | – |
| SSC(-CQR) +stage+kNN and ablations | κ, K | 9 × {10, 25, 50, 100, all} (45) | interval score (pre-registered) |
| QShrink-CQR | λ (h) | as κ (9) | sharpest with ≤ 5 % under-covered |
| Self-CQR-fb | minimum own history (h) | 72, 168, 336 (3) | sharpest with ≤ 5 % under-covered |
| ACI, ACI-CQR | step size γ | 0, 1e-4, 2e-4, 5e-4, 1e-3, 2e-3, 5e-3, 1e-2, 2e-2, 5e-2 (10) | sharpest with ≤ 5 % under-covered |
| TQA-B-CQR | decay β | 0.5, 0.8, 0.95 (3) | sharpest with ≤ 5 % under-covered |
| GHCP-CQR | surrogate group size (h) | 24, 168, 672 (3) | sharpest with ≤ 5 % under-covered |
| SCP, SCP-stage, CQR, Mondrian, Self-CP, Self-CQR | – | – | – |
