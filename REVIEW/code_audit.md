# Code audit (agent workflow "code-audit", 2026-11-16)

Five dimension reviewers were launched (calibration mathematics, faithfulness of the prior-art baselines,
data/leakage, metrics/statistics, orchestration/reproducibility) with adversarial verification of
Critical/Major findings. **Execution note:** the usage limit stopped 3 of 5 reviewers and the verifier of the
single Major finding; the Major finding was reproduced by the author (unit test
tests/test_core.py::test_neighbours_nan_safe_and_self_excluded fails on the old code path) before fixing.
Raw outputs: REVIEW/code_audit_raw.json. The uncovered dimensions (leakage, statistics, orchestration) are
covered by reviewers R3, R4 and R5 of the review cycles.

| # | Finding | Severity | Verified | Fix | Status |
|---|---|---|---|---|---|
| A1 | NaN calibration descriptor → kNN neighbours arbitrary; in LOBO the pseudo-target selects itself (own scores leak into its prior). Affects leave-site-out folds (lso0, lso2) | Major | yes (author, unit test) | NaN-safe standardisation, invalid buildings never neighbours, explicit self removal | fixed, recomputed |
| A2 | Calibration building with an empty stage bin enters prior as all-zero CDF (+inf mass); inflated radii for some targets/LOBO candidates | Moderate | yes (unit test) | prior averaged over buildings with scores in the bin | fixed, recomputed |
| A3 | 'HSC fixed-kappa' identical to tuned HSC in 6/10 runs; only for abs score; K not re-tuned | Moderate | yes (part files) | removed; new 'HSC-CQR fixed-κ' (simple variant, κ=168 h) | fixed |
| A4 | 'HSC -kNN -stage' not re-tuned, duplicates 'HSC simple' | Moderate | yes (code) | removed (HSC simple kept) | fixed |
| A5 | Grid cap 60 = infinity sentinel; Self-*/QShrink fallback triggered by large but defined own quantiles | Minor/Moderate | yes (unit test) | grid to 500·s (4000 pts); definedness from counts | fixed |
| A6 | SCP-stage ≠ HSC(κ=∞, K=all) (score- vs building-weighted) | Minor | yes | manuscript wording corrected | fixed |
| A7 | Tuning objective described as Eq. (is) | Minor | yes | wording corrected (per-hour IS / s, pooled) | fixed |
| A8 | QShrink λ grid lacked limits; tuning pooled radius ≠ applied | Minor/Moderate | yes | same grid as κ incl. 0/∞; LOBO score-weighted pooled radius | fixed |
| A9 | ACI with α_h>1 → inverted interval (latent) | Minor | yes (unit test) | empty-set convention (smallest observed score) | fixed |
| A10 | ACI-CQR γ at grid lower edge in 7/10 runs (possible under-tuning of a competitor) | Minor | yes (info files) | grid extended {0,1e-4,2e-4,...} (logged pre-registration deviation) | fixed |
| A11 | TQA-B clip instead of λ-scaling; +inf point omitted | Minor | yes | implemented as in the original | fixed |
| A12 | GHCP deviations undocumented; K symbol clash | Minor | yes | documented in 05_setup (M symbol) | fixed |
| A13 | Tuning tables discarded (boundary hits undetectable) | Minor | yes | stored in run_info | fixed |

Verified correct by the auditors (summary): HSC mixture equals Eq. (hsc) to grid rounding (brute force,
0 mismatches); own scores only from earlier stages for all methods; +1 point mass and finite-sample levels;
stage bins; CQR band construction; ACI update/batching; normalised IS objective; float32/int16 exactness;
GHCP/QShrink/TQA-B implementations match their specifications to ≤2.4e-7 (brute force).
