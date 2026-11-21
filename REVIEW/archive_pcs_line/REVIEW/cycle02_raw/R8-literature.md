# R8 Literature and citations, cycle 2

## Recommendation
Minor revision. One Major claim-versus-table problem in the abstract, highlights and conclusion needs fixing first.

## Summary
The bibliographic side of cycle-1 B7 is now resolved. I checked these against the Crossref API: buhlmann1967 (ASTIN Bull 4:199-207), jin2022 (Energy Build 258:111846), ristovska2026 (Energy AI 25:100815), hao2026 (Appl Sci 16:7984), shi2026 (EPSR 261:113412), suresh2025 (KBS 328:114222), hong2023 (NAAJ 27:675-88), bersson2024, gibbs2025 and li2021 (AAE 3:100054). Authors, year, venue and pages are all correct. arXiv, DataCite and Zenodo are blocked from this session. I therefore confirmed the preprints by web search: mallick2026 (arXiv 2608.15500), shahid2026 (2606.20115) and rafe2026 (2605.05562). Their content matches how they are used. Shahid shrinks per-site thresholds with a single n0, and Rafe and Das's regularised Mondrian uses w_g = n_g/(n_g+λ) and gives "no decisive fairness gain". I could not open jeon2026 (Zenodo) or wang2024acmcp (arXiv); the repository's DataCite record lists jeon2026 as Software. Preprints and software are now labelled. All headline numbers in the abstract and conclusion match T_main (18.2/9.1 %, 1.4/0.4 %, 19.4 %, width ratios 0.949/0.391 = 2.43 and 0.330/0.266 = 1.24). The abstract is 230 words. The remaining problems are listed below.

## Issues

**1. Major — The week-1 claim "no strategy of comparable width repairs it" is contradicted by the paper's own Table 1.**
Evidence: in Table 1 / T_main_BDG2, MLP-Gauss has a week-1 under-covered share of 9.9 ± 2.3 % with median relative width 0.455. That is only 1.16× PCS-CQR's 0.391, against 19.4 % for PCS-CQR. Coverage-only ACI reaches 8.9 % at 2.43× the width. On UCI, MLP-Gauss reaches 9.1 % (width 0.298, 1.12×) and absolute-score Self-CP 7.6 % (width 0.297), against 10.3 % for PCS-CQR. Coverage-only ACI on UCI reaches 4.6 % at only 1.24× width. That is hard to call "much wider" (Conclusion) or not "comparable". The response to A4 also says "Only coverage-only ACI reaches 8.9 %", which is false given MLP-Gauss's 9.9 %. Section 6.3 says "about one in five BDG2 buildings is under-covered with every strategy of comparable width". Yet QShrink-CQR (MACD) is at 17.7 %, PCS-CQR (MLP) at 16.1 % and MLP-Gauss at 9.9 %.
Action: define "comparable width" numerically (for example within 10 % of PCS-CQR's median width). Then restate the abstract, the 5th highlight, Sec. 1, 5.5, 6.3 and 7 against that definition. Acknowledge that a wider parametric model (MLP-Gauss, over-covering at 0.927) and UCI coverage-only ACI (1.24×) cut week-1 failures roughly in half. Replace "much wider" for UCI.

**2. Moderate — "Pre-registered" is still used throughout, against the response to A3.**
Evidence: the response says "'Pre-registered' was replaced by 'internal analysis plan…'". The built manuscript still says "pre-registered" at Contribution 3, Sec. 3.4 (twice), Sec. 4.3 (four times), the Table 1 caption, Sec. 5.3, 5.4 (twice) and 6.2 ("our pre-registered design"). Sec. 4.4 correctly says the plan was not externally registered. For readers, "pre-registered" implies an external registry.
Action: replace every occurrence with "planned" or "analysis-plan", and rename the "preregistered-abs" family label.

**3. Moderate — The motivating citation [12] is paraphrased beyond what the source shows; cycle-1 item R8-2 is not resolved.**
Evidence: the cycle-1 R8 review asked the authors to "quote supporting passage of [14]" (now [12], Hao et al.). citation_audit_r1.md confirms only the metadata. The Crossref abstract says: HEEW dataset, 55 buildings, one-hour-ahead forecasts, "Conformal prediction maintains reasonable coverage for seen buildings but shows reduced coverage after transferring to unseen buildings." It does not say "split-conformal" or "recommended recalibration". The manuscript makes both statements twice (Sec. 1 and Sec. 2.1). Ristovska [10] "reaches warm-start accuracy after a few weeks" also has no supporting passage on record.
Action: quote the supporting passages in citation_audit. Reword [12] to "reported reduced conformal coverage on unseen buildings (one-hour-ahead, 55 buildings)" unless the full text confirms the extra claims.

**4. Moderate — A directly relevant competitor to the ACI baseline is missing: ACI with multiple step sizes or online step-size selection.**
Evidence: Sec. 5.2 states that coverage-only ACI "always selected the largest step size in the grid (γ = 0.01)". The optimum is therefore at the grid boundary, and the reported 2.4× width penalty depends on that truncated grid. Zaffran et al. [35] (AgACI) is cited but not run. Dynamically-tuned ACI (DtACI; Gibbs and Candès, JMLR 2024, "Conformal inference for online prediction with arbitrary distribution shifts") and conformal PID control (Angelopoulos, Candès and Tibshirani, NeurIPS 2023) are neither cited nor run. Both remove exactly this tuning problem. Per-series conformal for panels of time series is also omitted: Stankevičiūtė, Alaa and van der Schaar, CF-RNN, NeurIPS 2021.
Action: cite these works. Extend the γ grid beyond 0.01, or run AgACI/DtACI, which is cheap given the existing ACI code. At minimum, qualify the ACI width penalty as conditional on the grid.

**5. Minor — An unreviewed code record is used as corroborating evidence.**
Evidence: Sec. 6.1 says the fixed-κ result "supports the fixed donor–local mixture implemented for new solar stations [22], for which no results have been published". A software deposit with no reported results makes no claim that can be supported. Sec. 2.2 already says it "cannot be compared".
Action: delete the bullet or move it to Sec. 2.2 as a design note.

**6. Minor — A cycle-1 suggestion was dropped silently.**
Evidence: the cycle-1 R8 item 3(d), Löfström et al., PMLR 329 (2026), on power-grid demand uncertainty, is neither cited nor mentioned in response_01.md. Bersson and Hoff [47] still gets one clause in the list, with no reason for not using it as a baseline (cycle-1 R8 item 4).
Action: cite Löfström or explain why it is omitted, and add one sentence on why empirical-Bayes small-area CP [47] is not applicable.

**7. Minor — The "similarity priors add nothing" highlight understates a small harm.**
Evidence: +kNN raises the BDG2 under-covered share from 1.4 % to 1.8 % and week 1 from 19.4 % to 20.3 %. +kNN+stage raises week 1 to 21.7 %. The response to A2 itself says "+kNN slightly harms".
Action: write "add nothing or slightly harm" in the highlight, abstract and conclusion, matching Sec. 5.4.

**8. Minor — The reference for contribution 1 is narrow.**
Evidence: Contribution 1 credits per-unit evaluation to [17,20] only. Rafe and Das [21] is credited in the response but not in the text of Contribution 1.
Action: add [21] there.
