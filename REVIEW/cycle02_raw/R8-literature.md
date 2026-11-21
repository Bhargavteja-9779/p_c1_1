# R8 — Literature and citation review (cycle 2)

## Recommendation
**Major revision.** I found no fabricated or wrongly attributed bibliographic records. But the novelty framing conflicts with one cited preprint, a directly competing per-unit method is left out (it is even in the authors' own reference database), and the closest prior art for the fixed-κ baseline is still a software record.

## Summary
I checked 21 references (all 2025–2026 items plus the central methodological ones). Twelve DOIs went through the Crossref API: Hao 2026, Ristovska 2026, Shi 2026, Suresh 2025, Gibbs 2025 JRSSB, Hong 2023 NAAJ, Dunn 2023 JASA, Barber 2023 AoS, Almeida 2015, Guo 2024, Li 2021, Kerby 2014. Shahid, Mallick, Rafe & Das and Lee/Barber/Willett were checked by web search, and Jeon by the repository's DataCite record (`literature/references_verified_new.json`). Authors, years, venues, volumes and pages match in every case. arXiv/DataCite could not be reached directly (the proxy blocked them). Content checks: Hao [15] does support its sentence; its abstract says conformal coverage "shows reduced coverage after transferring to unseen buildings". Mallick [33] does support "uses a new group's first observations". Rafe & Das [35] does use w_g = n_g/(n_g+50), a "regularised Mondrian", which supports the QShrink label.

## Issues

**1. Critical — The novelty claim on pseudo-count selection is contradicted by cited prior art [34].**
Evidence: Gap 3 (§1.3) says the transition parameters "have so far been fixed by hand or tuned for sharpness". Contribution 2 (Final_Manuscript.md:53) and §2.4 (l.114) present leave-one-building-out selection of κ "on the per-building coverage" as the paper's own. Shahid 2026 (arXiv:2606.20115; abstract and Algorithm 1) shrinks each site's risk curve towards the pooled curve with a prior strength n0. It **selects n0 = 19 by leave-one-site-out sensitivity analysis on the number of per-site violations** (2.7 of 20 at 2.0× stretch). That is the same selection principle. §1.2 cites [34] only as "credibility-type shrinkage … for federated sites", and §4.4 claims "the selection objective" as a key element.
Action: Rewrite Gap 3 and Contribution 2. The new elements are recency weighting, the onboarding (stage-resolved) setting and the energy evaluation. Say plainly that unit-level leave-one-out selection of the pseudo-count follows [34].
Experiment: none.

**2. Major — A direct competitor with per-unit guarantees is omitted: Bersson & Hoff 2024.**
Evidence: `bersson2024` (J Surv Stat Methodol 12:1464–88) is verified in references.py but never cited (it is missing from citation_order.json). Their FAB conformal method borrows strength across areas through an empirical-Bayes model, yet keeps **area-conditional** finite-sample coverage. This undercuts two statements: Limitation 1 (l.~309), that "combining shrinkage with a formal per-building safeguard is an open problem", and the use of [30] to say per-building validity is impossible. The impossibility result concerns longitudinal coverage under arbitrary dependence; it does not cover within-unit exchangeability.
Action: Cite and discuss [Bersson & Hoff 2024] and Hoff 2023 (Bernoulli, "Bayes-optimal prediction with frequentist coverage control"). Qualify the impossibility statements.
Experiment: preferably add a FAB-style per-building interval (shrinkage affects width only, building-level split conformal) as a baseline. At minimum, explain why it does not apply to the first week, when n_b is too small.

**3. Major — Other verified, relevant works are left out, and important online competitors are missing.**
Evidence: references.py has verified but uncited entries that bear directly on the gaps:
- Fisch 2021 (few-shot conformal for a *new task*). The authors' own literature_matrix.md:36,61 positions against it.
- Vejling 2026 (personalised per-agent validity).
- Bashari 2025 (borrowing from auxiliary data with guarantees).
- Batra 2023 (longitudinal conformal).

Also absent: strongly adaptive online methods beyond ACI/AgACI, namely Conformal PID (Angelopoulos, Candès & Tibshirani, NeurIPS 2023), SAOCP (Bhatnagar et al., ICML 2023) and DtACI (Gibbs & Candès, JMLR 2024). Energy-specific conformal work is missing too (Kath & Ziel 2021, IJF, day-ahead power markets), as is federated conformal prediction (Lu et al., ICML 2023). Gap 2's claim that "none was designed for a population of new units" is not supportable given Fisch 2021, HCP/GHCP [32,33] and [34].
Action: Add these and temper Gap 2.
Experiment: optional. Running DtACI or conformal PID would strengthen the "online level control fails in week 1" claim (Highlight 4), which currently rests on a single ACI variant.

**4. Moderate — The closest prior art for the fixed-κ baseline [37] is still only a software record.**
Evidence: Cycle 1 (review_01.md:67) asked that the Zenodo record be cited "together with any accompanying paper". It is unchanged: ref. 37 is "analysis code … [software]". The method claims attached to it ("with a fixed pseudo-count", l.110; "donor–local mixture as in [37]", l.165) cannot be checked by readers. A web search found no accompanying paper.
Action: Cite a paper describing the method, or recast as "cf. the implementation in [37]". Do not imply that κ = 168 h reproduces [37].
Experiment: none.

**5. Moderate — The classical credibility form is attributed to the wrong source.**
Evidence: "the classical credibility (empirical-Bayes) form [38]" (l.110) and "the credibility form itself is classical [38]" (§1.2) cite Hong 2023 (NAAJ). That paper links conformal prediction to credibility; it is not the classical source.
Action: Cite Bühlmann (1967, ASTIN Bull 4:199–207) and/or Bühlmann & Gisler (2005), and keep [38] for the conformal link.

**6. Minor — Some sentences stretch what their sources support.**
(a) [36] Zhang et al. is a Bayesian-prior regularisation of online quantile tracking for a single sequence, not shrinkage of a unit towards a pooled calibration (§1.2).
(b) [12] Gao 2023 (an adaptive transformer) does not address buildings with little history ([9–13]).
(c) Proposition 1 depends on "Theorem 1 of [32]", an arXiv preprint now at v4. Give the version, because theorem numbering can change.

**7. Minor — Formatting and currency.**
(a) Seven positioning references ([22,32–37]) are non-peer-reviewed preprints or software, and [34] is a workshop submission (MICCAI DeCaF 2026). Mark them as such in the text where novelty depends on them.
(b) [30] (TMLR) should carry the OpenReview URL, not the arXiv DOI.
(c) [23] is missing pages 1–6.
(d) Check whether ASHRAE Guideline 14-2014 [2] has been superseded by the 2023 edition.
(e) The references.py docstring cites `literature/citation_audit.md`, which does not exist in literature/.
(f) Twelve entries in references.py are verified but uncited. Prune them or cite them (see Issues 2–3).
