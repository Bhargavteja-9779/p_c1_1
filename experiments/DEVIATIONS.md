# Deviations from the analysis plan (Supplementary Table S1)

The analysis plan (experiments/PREREGISTRATION.md, committed 2026-11-15 12:59 UTC in e9ca94d) is an internal,
version-controlled file, not an external registration. Every change after it is listed below. "Target results
seen" says whether results on target buildings (from any run) were available when the change was decided.

| # | Date (UTC) | Change | Reason | Target results seen? |
|---|---|---|---|---|
| 1 | 2026-11-15 | Stuck-meter rule widened to any run of ≥ 24 identical readings; training rows with normalised target > 20 excluded from model fitting | Smoke test (reduced data) showed errors ~80× too large from flat-lined meters at one site | Yes (smoke test, 15 % of training rows) |
| 2 | 2026-11-15 | Self-CQR and ACI-CQR added; HSC-CQR component ablations added | Quick-mode check: self-only calibration a strong competitor; fair test of HSC-CQR needs same-score competitors | Yes (quick mode) |
| 3 | 2026-11-15 | Evaluation on the common set of hours with observed truth and finite intervals | Bug: hours without any possible forecast were counted as misses | No (bug found in code; all results recomputed) |
| 4 | 2026-11-16 | GHCP-CQR, TQA-B-CQR, QShrink-CQR added | Prior-art audit identified these as the closest published mechanisms | Yes (interim full-run results) |
| 5 | 2026-11-16 | "Simple" variants (uniform prior, no stage matching), fixed-κ = 168 h variant, MLP-CQR check added | Interim ablation showed no benefit of the similarity prior or stage matching | Yes |
| 6 | 2026-11-16 | ACI γ grid extended by {0, 1e-4, 2e-4} | Lower grid edge selected in 7 of 10 runs | Yes (selected γ only) |
| 7 | 2026-11-16 | Code-audit fixes (NaN-safe neighbour search, empty-bin prior, grid range, ACI empty-set convention, TQA-B λ-scaling, QShrink grid) | Independent code audit | Yes (all results recomputed) |
| 8 | 2026-11-20 | Recommended layer changed from HSC-CQR (similarity prior + stage matching, κ by LOBO interval score) to PCS-CQR (uniform prior, no stage matching, κ by the reliability-aware LOBO rule) | Review cycle 1: the refinements added nothing and the pre-registered interval-score objective is nearly flat in κ and selected a less reliable κ than a fixed one-week value | Yes (complete v1 results) |
| 9 | 2026-11-20 | Reliability-aware LOBO rule (minimum coverage deviation among parameter values within 2 % of the best LOBO interval score) applied to PCS, QShrink and ACI; unconstrained coverage-only ACI added as reference | Same as 8; applied to all tuned competitors for fairness | Yes |
| 10 | 2026-11-20 | ACI: split-conformal level ⌈(1−α_h)(N+1)⌉/N and finite fallback (largest calibration score) instead of a 500·s radius when α_h ≤ 1/(N+1) | Review: the cap dominated the tuning objective and handicapped ACI | Yes |
| 11 | 2026-11-20 | TQA-B budget scaling from the largest attainable rank instead of the maximum over target buildings; κ = 0 with pooled fallback in the grid | Review: target information used in TQA-B; κ = 0 previously unselectable | Yes |
| 12 | 2026-11-20 | Only actually observed hours are scored (interpolated/masked hours used as inputs only); UCI daylight-saving artefacts masked; weather interpolation limited to 6 h | Review (data and leakage) | Yes |
| 13 | 2026-11-20 | Leave-site-out with 5 site groups and one seed replaced by leave-one-site-out (10 sites × 3 seeds) | Review: site-dependent results, single training run per fold | Yes |
| 14 | 2026-11-20 | Added: disjoint calibration period; history-only noise, contiguous outages, early level shift, volatility increase; small calibration pools (5–40 buildings, 5 draws); CQR-score strategies at 80 % and 95 % | Review (robustness, experimental design) | Yes |
| 15 | 2026-11-20 | Inference: site-level sign-flip randomisation tests (BDG2) instead of building-level Wilcoxon as primary; tests of the under-covered share and booking failures; per-week metrics; operational metrics | Review (statistics): building-level tests ignore clustering in 10 sites | Yes |
| 16 | 2026-11-20 | Headline metric: share of under-covered buildings (an RQ1 metric in the plan) reported first; the planned primary endpoints (interval score and |coverage − 0.9|) are tested and reported for every comparison | The paper's question is per-building reliability; the interval score barely separates strategies | Yes |

Consequences: results for PCS-CQR, the reliability-aware rule and the protocols added in revision are exploratory.
The planned primary comparison (HSC, absolute score, against the planned baselines) is reported in full in the
supplementary tests table (family "preregistered-abs"); its hypothesis was not confirmed (HSC does not improve on
self-only calibration).
