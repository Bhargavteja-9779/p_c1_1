# Review cycle 1 — consolidated (2026-11-20)

Ten independent reviewer agents read packet_cycle01.md plus the repository (raw reviews: REVIEW/cycle01_raw/).

| Reviewer | Recommendation |
|---|---|
| R1 novelty / prior art | Major revision |
| R2 methodology | Major revision |
| R3 experimental design | Major revision |
| R4 statistics | Major revision |
| R5 data & leakage | Major revision |
| R6 robustness & generalisation | Major revision |
| R7 computation | Minor revision |
| R8 literature & citations | Major revision |
| R9 associate editor | Major revision |
| R10 hostile competitor | Major revision |

Overall: **Major revision** (9/10). Reported numbers reproduce (R4 recomputed them independently; R2 confirmed code matches the equations). The criticism is of framing, method choice, inference and missing analyses, not of data integrity.

## Consensus issues (ordered by priority; reviewers raising each in brackets)

### A. Critical
**A1. Fixed κ=168 (prior-art donor–local mixture) beats the LOBO-tuned headline method everywhere** [R1, R2, R3, R4, R6, R9, R10].
BDG2 main: MACD 0.015 / 1.9 % vs 0.018 / 3.4 % (r_rb=−0.45, worse at 10/10 sites); robustness (cal10 2.2 vs 7.9 %, shift+40 2.8 vs 6.5 %, …) and generalisation (LSO 1.7 vs 5.3 %, UCI→BDG2 4.3 vs 8.7 %). LOBO-IS objective is flat (0.15 % between κ=168 and 336; κ=∞ only 0.8 % worse while under-coverage is ~6×), picks 336 almost always, K selection is noise. Sec 2.3 claims LOBO selection as the difference from [29].
→ Fix: drop LOBO-IS selection as a contribution; add a **reliability-aware LOBO objective** (calibration-building MACD / under-covered share; IS subject to coverage) evaluated in all protocols; report objective flatness; report fixed-κ next to every headline number; recommend whichever is supported (with κ justified without target results). Grouped (leave-site-out) LOBO as a variant [R5]. Cap/fallback for small pools (cal10 seed 2 picked κ=1344 → 19 % under-covered) [R6].

**A2. Headline numbers from the variant the paper calls unnecessary** [R2, R3, R7, R9, R10, R1].
Abstract/Table 4/Fig 1/cost refer to full HSC-CQR (kNN + stage); recommended layer is "simple". kNN prior is harmful in week 1 and at unseen sites (Wolf 30.6 % vs 0 % for fixed-κ/QShrink) [R2, R6].
→ Fix: make the simple (uniform prior, no stage) layer — or fixed/reliability-tuned κ version — the method; report its tests; move kNN/stage to ablation and say they can **harm**; rename the layer (drop "hierarchical"; e.g. "pseudo-count score shrinkage") [R1, R9]; redraw Fig 1.

**A3. Pre-registration overstated / undisclosed deviations** [R3, R4, R5, R8, R9, R10, R1].
H0 (abs-score HSC with kNN+stage, lower IS) not confirmed; HSC-CQR was a variant; GHCP/TQA-B/QShrink/simple/fixed-κ/MLP-CQR added after interim looks; ACI grid widened; quality rules not in the plan; internal file only. Sec 4.4 sentence "All settings were fixed…" is false.
→ Fix: replace "pre-registered" by "analysis plan fixed before the full runs"; deviations table (item, plan, change, date, reason, target results seen?); report the planned primary comparison (HSC vs baselines incl. Self-CP where it loses); label exploratory analyses.

**A4. No gain in the first week, which the title/abstract emphasise** [R6, R9, R10, R2].
Week-1 share <0.85: HSC-CQR 24.5 % vs CQR 23.8 % (BDG2); entire 18.7→3.4 % gain is in days 8–56.
→ Fix: per-week reliability table (weeks 1, 2, 3–4, 5–8; under-covered share, P10, MACD) for all CQR-score strategies; reframe claims ("after about one week"); state that no strategy fixes week-1 under-coverage.

### B. Major
**B1. Statistics** [R4, R3, R6]: Wilcoxon ignores site clustering (exact site-level sign-flip: Self-CQR p=0.033, simple p=0.40) → add site-level randomisation tests (Holm); median/Hodges–Lehmann paired differences with CIs on the same estimand; test the headline under-covered share (paired cluster bootstrap); report tests + s.d. for LSO, cross-dataset and robustness; fix text contradicting stored tests (abs "simple better", ablation "less than seed s.d."); define Holm families; error analysis at building level.
**B2. ACI handicapped by 500·s cap with IS tuning** [R3, R4, R10]: finite data-based fallback (max calibration score) or clip α_h; ACI also tuned on reliability; remove "ACI adapts slowly" unless supported.
**B3. "Most reliable" not supported outside main protocol; mechanism vs tuning confounded** [R1, R3, R5, R6, R9, R10]: LSO HSC-CQR ≈ Self-CQR (p=0.96), QShrink and simple better; noise15 Self-CQR better; QShrink wins several stress rows. Compare QShrink and HSC at matched pseudo-counts. Present shrinkage strategies as a near-equivalent family; name best per condition; LSO co-primary with per-site/fold table.
**B4. Energy-application payoff missing (desk-rejection risk)** [R9]: operational case study from stored intervals (e.g. flexibility commitment / DR baseline with under-delivery penalty) per method.
**B5. Data handling** [R5]: quality filter uses 2017 (target) data; evaluation truth pre-cleaned/interpolated; weather observed, naive timestamp join (timezone unused), unbounded interpolation; exclusion-flow table; 10 sites (README/PROJECT_STATE say 12); pin data version; UCI DST hours.
**B6. Length** [R9]: 29 pages, ~12.7k words, 11 figures, 8 tables → ~8k words, 6–7 display items; move Tables 6–8 (full), Figs 2, 10, 11 to supplement.
**B7. Literature** [R8, R1]: label preprints/software; describe [29] and state what this study confirms/adds; re-verify [12], [14], [35] (drop if unconfirmable); fix missing citation_audit.md reference; add Jin et al. 2022 (Energy Build 258:111846), BuildingsBench same-dataset note, Wang & Hyndman AcMCP, Bühlmann 1967; engage prior findings in Sec 6; reword contribution 1 (per-unit evaluation exists: TQA, Shahid, Rafe & Das).
**B8. Robustness design** [R6]: stress tests mild/favour self-calibration; post-change coverage (days 29–56) separately; contiguous outages; α=0.05/0.2 for CQR-score family [R3, R6]; long-run drift beyond 56 days or restrict claims.

### C. Moderate / minor
- Methodology wording [R2]: DP reading → "DP-motivated heuristic with conformal-style correction"; own scores not stage-matched; κ-limit discontinuity; stage-matching claim score-specific; descriptor dominated by load shape; TQA-B λ uses target buildings (fix to calibration ranks); κ=0 grid point degenerate; γ=0 ≠ SCP-stage exactly.
- Cost [R7, R9, R3]: time the recommended layer; describe as amortised batch cost or measure single-building latency; medians (UCI s1 OpenMP stall); per-building memory state (~448 KB as implemented; minimal 16 KB); cost for all strategies; grid vs exact quantile check.
- Leakage tests narrower than claimed [R5]: add h∈{7,14,28,56}, descriptor, calibration causality tests or soften.
- Calibration period overlaps training period [R3]: discuss/quantify.
- AI-use declaration: describe research use in Methods; remove placeholders [R9].
- Fig 11 uninformative [R9]; IS cannot discriminate → report width and P90 width ratio [R10]; 80 %-window fallback units [R5]; PyTorch citation, DeepAR attribution, arXiv versions [R8].

## Corrective plan (cycle 1 → v2)
1. **Calibration-only recompute (cached models; needs data re-download + model cache rebuild if absent)**: reliability-aware and grouped LOBO; fixed-κ in all protocols; QShrink at matched λ; ACI with finite fallback and reliability tuning; TQA-B λ from calibration buildings; κ=0 fallback; CQR family at α=0.05/0.2; per-week metrics; timing of all strategies.
2. **Analysis**: site-level randomisation tests, HL differences, under-covered-share tests, robustness/generalisation tests with s.d., per-site/fold tables, week-wise table, operational cost case study.
3. **Data**: exclusion-flow table; causal-filter sensitivity run; timezone check; UCI DST masking (requires rerun → schedule with 1).
4. **Manuscript**: re-centre on the simple pseudo-count layer with fixed/reliability-selected κ; rename; deviations table; reframe week-1 and "most reliable"; length cut to ~8k words; literature fixes; declarations.
