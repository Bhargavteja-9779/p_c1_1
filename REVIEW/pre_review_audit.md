# Pre-review audit (agent workflow "pre-review-audit", 2026-11-15/16)

Agents: 4 prior-art searchers (statistics/ML conformal; energy UQ; multi-series time-series conformal;
patents/grey literature), per-item existence verifiers, novelty synthesis, 4 code auditors with
adversarial verifiers, 1 journal-requirements agent. **Execution note:** the usage limit stopped the
workflow; 3 of 34 agents completed (stat-conformal and energy-UQ searchers, journal agent). Existence of
every work below was then verified by the author via arXiv/Crossref/DataCite APIs
(literature/verify_refs_new.py, references_verified_new.json). The code audit was re-run separately
(workflow "code-audit"; see REVIEW/code_audit.md).

## Prior-art findings that change the paper (Reviewer-1 perspective: novelty)
| Work (verified) | Closeness | Consequence |
|---|---|---|
| Jeon 2026, Zenodo 10.5281/zenodo.24002627 — cold-start conformal for solar irradiance at unseen stations; donor+local mixture (algebraically = our pseudo-count mixture with fixed κ), pooled/distance-weighted donors, delayed-feedback ACI, 41 stations | **High** | mechanism and cold-start framing not new; cite and position: different domain (building load), large heterogeneous population, LOBO-tuned κ, per-building distribution |
| Shahid 2026, arXiv:2606.20115 — risk-curve shrinkage w=n/(n+n0) per site, LOSO choice of n0, per-site evaluation | High | shrinkage form not new; static sites, risk control |
| Rafe & Das 2026, arXiv:2605.05562 — regularised Mondrian (quantile shrinkage n/(n+λ)) | High | implemented as baseline **QShrink-CQR** |
| Mallick et al. 2026, arXiv:2608.15500 — GHCP: new group with few observations, finite-sample guarantee | High | implemented as baseline **GHCP-CQR** (adapted, documented) |
| Lin, Trivedi & Sun 2022 NeurIPS (TQA) / TMLR (CPTD) — per-series (longitudinal) coverage, tail coverage, impossibility of distribution-free longitudinal validity | High | implemented **TQA-B-CQR**; TQA-E ≈ ACI-CQR; cite impossibility result |
| Zhang, Lu & Yang 2024, arXiv:2410.02561 — DP-posterior-type prior regularisation of the empirical score belief (online CP) | Medium | cite for the functional form |
| Hao, Yang & Ji 2026, Appl Sci 16:7984 — split-conformal under-covers unseen buildings on average | Medium | cite as domain evidence of the problem |
| Bersson & Hoff 2024 JSSAM; Bashari et al. 2025; Batra et al. 2023; Vejling et al. 2026; Hong 2023 (credibility); Ristovska et al. 2026 (Energy and AI, cold-start buildings) | Medium/Low | cite in related work |

## Decision
The topic is **not abandoned** (no prior study evaluates or improves per-building interval reliability during
onboarding of newly metered buildings for load forecasting), but the contribution is **re-scoped**:
no claim of a new conformal mechanism; claims are (1) problem/protocol, (2) head-to-head comparison incl. the
closest published mechanisms under one protocol, (3) design evidence (LOBO-tuned shrinkage is the active
ingredient; similarity prior and stage matching unnecessary), (4) operational guidance. Introduction, related
work, title and abstract revised accordingly; three prior-art baselines added (calibration-only).

## Journal requirements agent
Raw output in pre_review_audit_raw.json → "journal"; consolidated in journal_selection/journal_verification.md.
