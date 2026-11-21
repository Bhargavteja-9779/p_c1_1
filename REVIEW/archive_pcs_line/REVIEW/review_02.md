# Review cycle 2 — consolidated (2026-11-21)

Ten independent reviewer agents read packet_cycle02.md and the repository; raw reviews are in REVIEW/cycle02_raw/.

| Reviewer | Recommendation |
|---|---|
| R1 novelty / prior art | Major revision |
| R2 methodology | Major revision |
| R3 experimental design | Major revision |
| R4 statistics | Major revision (re-analysis only) |
| R5 data & leakage | Major revision |
| R6 robustness & generalisation | Major revision |
| R7 computation | Minor revision |
| R8 literature & citations | Minor revision |
| R9 associate editor | Major revision |
| R10 hostile competitor | Major revision |

Overall: **Major revision** (8 major, 2 minor). The cycle-1 framing issues are accepted as resolved. The new
criticism concerns three things: the time scale of the headline metric, claims that go beyond the tables, and an
asymmetry in the competitor tuning.

## A. Critical

**A1. The 56-day headline hides sub-window miscalibration** [R1, R2, R3, R5, R6, R9].
Verified by the authors from the results files:

| BDG2, PCS-CQR | Week 1 | Week 2 | Weeks 3–4 | Weeks 5–8 | Any window after week 1 | 56 days |
|---|---|---|---|---|---|---|
| Under-covered share | 19.4 % | 19.8 % | 15.3 % | 11.0 % | 41 % | 1.4 % |

The corresponding CQR shares are 24.2, 25.8, 25.5 and 20.7 % (48.6 % in any window after week 1).
- In weeks 5–8, ACI-CQR (MACD) is more reliable at equal width (7.1 %) [R2, R6].
- Under PCS, sub-window coverage does not persist per building: weeks 3–4 vs 5–8 correlate at −0.10 to −0.30, against +0.47 to +0.58 under CQR [R1, R2]. Remaining shortfalls are therefore largely transient, but the independent-miss sampling floor (1.7 % per week) cannot show this, because hourly misses are autocorrelated [R1, R4, R5].

The claims "restores reliability", "small after the first week" and "makes intervals reliable for each building" overstate the evidence.

→ Fix:
- Make the time scale explicit in every claim.
- Report sub-window under-coverage for all strategies, including the "any window" share, in the main text.
- Estimate an autocorrelation-aware sampling floor for windows (block bootstrap of each building's own miss sequence re-centred to nominal), which requires storing hourly miss sequences or the needed summaries.
- Report the persistence of sub-window failures (systematic vs transient).
- Reword the highlights, abstract, discussion and conclusion accordingly.

**A2. ACI is more reliable in some conditions, and the comparison is not symmetric** [R2, R3, R6, R10, R1].
- At 80 % nominal, ACI-CQR (MACD) leaves 0.9 % of BDG2 buildings under-covered vs 6.3 % for PCS-CQR (Holm p = 0.031) [R6, R10]. This contradicts "ACI needs much wider intervals".
- Small pools: with 5–10 calibration buildings, reliability-tuned ACI under-covers 0.6–0.7 % vs 2.7–3.0 % at equal width [R3].
- `tune_aci` leaves the base width out of the LOBO interval score (pipeline.py ~l.255), so the 2 % band is about 2–3× tighter for ACI; the selected γ changes in 10 of 30 (R10) or 31 of 177 (R2) runs [R2, R10].
- Coverage-only ACI sits at the γ-grid edge (0.01), so its width ratio is a grid artefact [R2, R3, R6, R8, R9].
- Table 3 shows the IS-tuned ACI column, not ACI (MACD) [R3, R6].

→ Fix:
- Compute the ACI LOBO interval score on the same total width as PCS/QShrink.
- Extend the γ grid until the coverage-only selection is interior.
- Report ACI (MACD) in Table 3, the α table and the pools table.
- Compare strategies at matched width and at matched reliability.
- State plainly where ACI wins.

**A3. Claims stronger than the tables** [R2, R3, R4, R8, R9, R10].
- *"Fixed κ=168 chosen without any data"* is false: it was added after target results were seen (Supplementary Table S1 #5), and 168 is also the target-set MACD minimum.
- *"Equally well"* fails on UCI (0.8 vs 0.4 %).
- *Tuning rule vs IS tuning:* the difference in under-covered share is p = 0.164, so "what mattered was tuning" overstates. The 2 % tolerance has no sensitivity analysis. The 1.2 % flatness is a median that hides 6.7 % in one seed [R1].
- *Week-1 "no strategy of comparable width"* is contradicted by MLP-Gauss (9.9 % at about 1.16× width) and by UCI coverage-only ACI (1.24×) [R4, R6, R8, R10].
- *Equivalence statements* ("indistinguishable", "added nothing") rest on non-significant tests without margins. The similarity prior significantly improves the interval score [R4].
- *Operational payoff:* booking failures are not significant (p = 0.070 BDG2, 0.060 UCI), reserve cost is flat, and booking failures are missing from Table 2 [R9, R10].
- *Over-coverage* is invisible in the under-covered share (history-only noise: PCS 0.944) [R6].

→ Fix: rewrite each claim to match the stored tests, add equivalence margins (TOST) or drop the equivalence language, and add booking failures and over-coverage to the main tables.

## B. Major

**B1. Data and information set** [R5].
- The target-year quality filter is unresolved: 208 buildings are removed only by the 2017 rule, 164 of them evaluable, including 4 whole sites, and 2.5× more volatile. The authors' reason for keeping the filter ("cannot evaluate where truth is missing") does not hold for them. → Sensitivity run with a causal (training-period) filter that keeps these buildings.
- Day-ahead information set: features and own scores assume all of day D−1 is observed, whereas day-ahead gate closure is around noon on D−1. → Sensitivity run with a one-day-delayed own-score update at least, or state the assumption and its direction.
- Upstream BDG2 cleaning and non-causal stuck-meter masking and interpolation: state these, and their effect on scores.

**B2. QShrink matches or beats PCS** in 15 of 17 conditions [R1, R6, R10]; QShrink matches or beats PCS at 9 of 10 LOSO sites. → Present the two as one family and recommend either; do not imply PCS is preferred.

**B3. Statistics** [R4]:
- the mean interval-score estimand is driven by outliers (the sign differs from the median) → report median or trimmed IS differences as primary for IS;
- the fixed κ=168 is significantly sharper than tuned PCS;
- add tests for week-wise metrics, pools and reserve cost (declared families).

**B4. Robustness claims** [R6]:
- level-shift robustness comes from the pre-shift weeks (no post-shift advantage; booking failures 15.7 %) → report post-change windows;
- the calpool10 run (tuned PCS 9.5 % in one seed) is not mentioned;
- GHCP with unbounded intervals is listed as "reliable" → flag infinite or over-wide intervals in Table 3;
- the weak forecaster is not weak; stress tests run on BDG2 only; calibration buildings are never perturbed.

## C. Moderate / minor
- Novelty: Dunn et al. shrinkage for new groups not credited; missing references SGCP, Zaregarizi & Yavari, Fong & Holmes, meta-XB, Löfström 2026; ACI variants (AgACI, DtACI, conformal PID) [R1, R8].
- "Pre-registered" still used about 12 times [R8]. The Hao [12] paraphrase goes beyond its abstract [R8]. Zenodo record [22] is cited as corroboration [R8]. Rafe & Das are missing from contribution 1 [R8].
- Computation [R7]:
  - the state is 448 kB as implemented, not 16 kB;
  - LightGBM inference times only the point model;
  - no end-to-end latency;
  - no check of grid vs exact quantile;
  - "three quantile models" is wrong (1 point + 2 quantile);
  - the "batch" update is a sequential loop;
  - the tuning cost comparison is not like for like.
- Text defects [many]:
  - "fewer than 0.00%";
  - the hour count is given as 1344 (median) and ≈1300;
  - "6 of 713" is not labelled as seed-averaged;
  - LOSO is shown as "Runs 3" (it is 30);
  - n_cal=5 numbers are cited but missing from Table 3;
  - two different "10 calibration buildings" experiments;
  - Rat 49.7 % is described as "half or more";
  - κ=∞ is described as pooled CQR (the finite-sample correction differs);
  - the 80 %-window rule is missing from Table S1;
  - the cover letter claims pretrained-model compatibility.
- Placeholders (authors, CRediT, repository URL) remain; the AI-run audits are called "independent" [R9].

## Corrective plan (cycle 2 → v3)
1. **Re-analysis of stored results** (no new runs):
   - sub-window tables with the "any window" share;
   - persistence correlations;
   - matched-width and matched-reliability comparisons;
   - ACI (MACD) everywhere;
   - median IS tests;
   - TOST equivalence or removal of equivalence claims;
   - booking failures in Table 2;
   - an over-coverage column;
   - tests for week-wise metrics and pools;
   - post-change windows for shift tests;
   - flags for infinite intervals.
2. **Calibration-only recompute** (cached models):
   - ACI LOBO objective on total width;
   - extended γ grid;
   - 2 % tolerance sensitivity (1, 2, 5 %);
   - store hourly miss sequences (or block-bootstrap floors) for an autocorrelation-aware floor;
   - one-day-delayed own-score update as an information-set sensitivity.
3. **Data sensitivity** (retraining needed): a causal quality filter that keeps the buildings removed only by the target-year rule (BDG2, 3 seeds).
4. **Manuscript**:
   - reframe the headline to the time scales actually supported (56-day window vs weekly windows);
   - present PCS and QShrink as one family;
   - state where ACI wins;
   - fix every claim listed in A3 and C;
   - correct the computation numbers;
   - remove "pre-registered" outside the deviations context.
