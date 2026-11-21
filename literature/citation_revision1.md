# Citation revision 1 (reviewer cycle 1)

Date of checks: 2026-11-21. All fields written to `manuscript/references.py` come from the records listed below
(Crossref REST API, arXiv API, papers.nips.cc citation metadata, proceedings.mlr.press volume pages, jmlr.org BibTeX,
OpenReview API v2, Zenodo REST API, eia.gov). DBLP could not be queried (bot-check page) and IEA, MDPI and ScienceDirect
pages returned HTTP 403; nothing was taken from those sites.

## 1. Added and changed keys

### Added (15)

| Key | Entry (short) | Verified source |
|---|---|---|
| `zhang2026transfer` | Zhang, Li, Xie, Kong, Jiang. Transfer conformal predictive inference for regression. JMLR 27(90):1–68, 2026 | http://jmlr.org/papers/v27/24-1899.html (BibTeX `JMLR:v27:24-1899`); no arXiv version found |
| `zhang2024posterior` | Zhang, Candès. Posterior conformal prediction. arXiv:2409.19712 (v2, 27 May 2026) | arXiv API; no journal/proceedings version found on Crossref or OpenReview |
| `guan2023` | Guan. Localized conformal prediction. Biometrika 110(1):33–50, 2023 | https://doi.org/10.1093/biomet/asac040 (Crossref; online 2022-07-21, issue 2023) |
| `angelopoulos2023pid` | Angelopoulos, Candès, Tibshirani. Conformal PID control. NeurIPS 36, pp. 23047–74 | papers.nips.cc hash 47f2fad8c1111d07f83c91be7870f8db; Crossref also has DOI 10.52202/075280-1000 |
| `bhatnagar2023` | Bhatnagar, Wang, Xiong, Bai. SAOCP. ICML 2023, PMLR 202:2337–63 | https://proceedings.mlr.press/v202/bhatnagar23a.html |
| `barber2021limits` | Foygel Barber, Candès, Ramdas, Tibshirani. The limits of distribution-free conditional predictive inference. Inf Inference 10(2):455–82, 2021 | https://doi.org/10.1093/imaiai/iaaa017. Note the title is "The **limits** …" (plural), not "The limit …" |
| `kath2021` | Kath, Ziel. Int J Forecast 37(2):777–99, 2021 | https://doi.org/10.1016/j.ijforecast.2020.09.006 |
| `jensen2024` | Jensen, Bianchi, Anfinsen. EnCQR. IEEE TNNLS 35(7):9014–25, 2024 | https://doi.org/10.1109/TNNLS.2022.3217694 (DOI minted 2022; issue July 2024 → cite as 2024) |
| `buhlmann1967` | Bühlmann. Experience rating and credibility. ASTIN Bull 4(3):199–207, 1967 | https://doi.org/10.1017/S0515036100008989 (a second part, ASTIN Bull 5(2):157–65, 1969, DOI 10.1017/s0515036100008023, exists; not added) |
| `buhlmann2005` | Bühlmann, Gisler. A Course in Credibility Theory and its Applications. Springer (Universitext), 2005 | https://doi.org/10.1007/3-540-29273-X (Crossref book record: title, Springer, Berlin/Heidelberg, 2005; the record has no author field — authors taken from the Crossref records of two published reviews, 10.1017/s1748499500000415 and 10.1080/03461230600889660, whose titles name "H. Bühlmann & A. Gisler (Springer, 2005)") |
| `jin2022` | Jin, Acquah, Seo, Han. Energy Build 258:111846, 2022 | https://doi.org/10.1016/j.enbuild.2022.111846 (Crossref; also in `references_verified_new.json`) |
| `ansari2024` | Ansari et al. Chronos: Learning the language of time series. TMLR 2024 | OpenReview TMLR note https://openreview.net/forum?id=gerNCVqqtR ("Accepted by TMLR", 11 Nov 2024); 18 authors, listed as in that record (6 + et al.) |
| `eia2026elec` | U.S. EIA, Electricity explained: Use of electricity | https://www.eia.gov/energyexplained/electricity/use-of-electricity.php (accessed 2026-11-21). States 2025 U.S. retail electricity sales: residential 37.3 %, commercial 36.8 %, industrial 25.7 %. IEA pages were not reachable (HTTP 403), so no IEA report was added |
| `li2025ncc` | Li, Rodríguez. Neural conformal control for time series forecasting. AAAI-25, vol. 39(17), pp. 18439–47 | https://doi.org/10.1609/aaai.v39i17.34029 (archival version of arXiv:2412.18144) |
| `zhou2026der` | Zhou, Zhu. Hierarchical probabilistic conformal prediction for DER adoption. Ann Appl Stat 20(2):1626–45, 2026 | https://doi.org/10.1214/26-AOAS2199 (archival version of arXiv:2411.12193) |

### Changed (existing keys kept)

| Key | Change | Verified source |
|---|---|---|
| `lee2023hier` | arXiv preprint → **ACM J Data Sci 2026**, article 3786352 (published online 2026-03-19; Crossref gives no volume/issue yet) | https://doi.org/10.1145/3786352. The reviewer is right. GHCP (arXiv:2608.15500) also cites HCP as "Lee et al., 2026". Consider renaming the key to `lee2026hier` when the section files are next edited |
| `bashari2025` | arXiv → **NeurIPS 38 (2025)**, pp. 130461–521 | https://doi.org/10.52202/085713-3925 (Crossref) |
| `lin2022cptd` | arXiv DOI replaced by TMLR OpenReview URL | https://openreview.net/forum?id=8QoxXTDcsH ("Accepted by TMLR", Sept 2022; arXiv comment confirms TMLR Sept 2022) |
| `zhang2024bayes` | **unchanged**. No archival version: OpenReview shows a rejected ICLR 2025 submission, an RSS 2025 workshop paper and a NeurIPS 2024 BDU workshop poster (the last under a different title); PMLR v258 and Crossref show nothing. arXiv v2 dated 2025-05-22 | arXiv API, OpenReview API |
| `romano2019` | + proceedings URL (NeurIPS shows no page numbers for 2019) | papers.nips.cc …/2019/hash/5103c3584b063c431bd1268e9b5e76fb-Abstract.html |
| `gibbs2021` | + pp. 1660–72 + URL | …/2021/hash/0d441de75945e5acbc865406fc9a2559-Abstract.html |
| `tibshirani2019` | + URL (no pages listed) | …/2019/hash/8fb21ee7a2207526da55a679f0332de2-Abstract.html |
| `ding2023` | + pp. 64555–76 + URL | …/2023/hash/cb931eddd563f8d473c355518ce8601c-Abstract-Conference.html |
| `emami2023` | + pp. 19823–57 + URL | …/2023/hash/3f17bf868966df01ca125e5bbc9ee24e-Abstract-Datasets_and_Benchmarks.html |
| `lin2022tqa` | + pp. 31017–30 + URL | …/2022/hash/c8d2860e1b51a1ffadc7ed0a06f8d8f5-Abstract-Conference.html |
| `ke2017` | + URL | …/2017/hash/6449f44a102fde848669bdd9eb6b76fa-Abstract.html |
| `paszke2019` | + URL | …/2019/hash/bdbca288fee7f92f2bfa9f7012727740-Abstract.html |
| `fisch2021`, `xu2021`, `zaffran2022` | + PMLR URL (pages already correct) | proceedings.mlr.press v139/fisch21a, v139/xu21h, v162/zaffran22a |

`python3 -c "import sys; sys.path.insert(0,'manuscript'); import references"` works (79 keys, no duplicate keys).

## 2. Jeon Zenodo record (`jeon2026`, 10.5281/zenodo.24002627)

Record: software, CC-BY-4.0, published 2026-11-06, single creator Jeon, Byung-ki, one file
`coldstart-conformal-solar-v1.2.zip` (downloaded and read; 48 files). It is the only version (concept DOI 10.5281/zenodo.24002626).

**What the record description says:** eight calibration strategies, including "pooled / distance-weighted / selected donor
stations, local-only windows of 1–182 days, a donor+local mixture, delayed-feedback adaptive conformal inference, and a
full-local-year oracle". It does **not** mention a pseudo-count or any value.

**What the code says** (`src/run_cp_matrix.py`, `src/revision_r1_analysis.py::mixture_quantile`):
- Mixture M4 is a weighted split-conformal quantile over donor scores ∪ local scores. The **whole donor pool gets a fixed total
  mass m** (each of the N_p donor scores weight m/N_p), each local score weight 1, plus the test point:
  threshold (1−α)(m + n + 1). This is a fixed pseudo-count.
- **Main value m = 150** (`M_MIX_MAIN = 150.0`); **sensitivity m ∈ {50, 400}** (`M_MIX_SENS`, run for the first 3 window placements).
  The unit is individual conformity scores (15-min resolution time steps), not days.
- `revision2/results/NUMBERS_R2.md` (C3) reports that at certification the median local set is 2183–3192 scores, so
  "donor mass 150 ⇒ donor weight 4–6 % of the mixture".
- **Discrepancy inside the record:** the pre-registered design (`research/DESIGN.md`, table §4, M4) describes the mixture as
  "local weight by effective-sample-size rule", but the released code uses the fixed m = 150 (with 50/400 sensitivity).
  No effective-sample-size rule appears in the code.

So the manuscript wording "a donor–local mixture with a fixed pseudo-count" (03_related, 04_method, 05_setup) is supported
by the released code, not by the record's description text. Suggested precise phrasing: "…a donor–local mixture in which
the pooled donor scores carry a fixed total weight of 150 scores (sensitivity 50 and 400) [@jeon2026]". Do not say this
was pre-registered: the design file describes a different rule.

**Associated manuscript / preprint:** the record and README state the code accompanies "A two-network audit shows when
conformal prediction intervals for solar irradiance forecasts remain valid at newly commissioned stations" (Scientific
Reports, under review; second revision). No preprint was found: arXiv title/author searches, Crossref (which covers SSRN and
Research Square) and Zenodo search found nothing. Earlier Crossref records by Jeon B-K and Kim E-J (solar irradiance
prediction, Energy Rep 2023, J Korean Sol Energy Soc 2023) are unrelated to conformal prediction. Cite only the software record.

## 3. Claim checks and corrected wording

**Hao et al. 2026 (`hao2026`, Appl Sci 16:7984).** Only the abstract could be read (Crossref/OpenAlex; the MDPI full text
returned 403). The abstract says that "Conformal prediction maintains reasonable coverage for seen buildings but shows
reduced coverage after transferring to unseen buildings", and that reliability "should be evaluated from multiple angles,
beyond point prediction accuracy alone". It says nothing about recommending recalibration. Also, "under-cover on average"
is stronger than "reduced coverage".
- 02_intro, proposed: "…a recent cross-building study reports that split-conformal intervals that keep reasonable coverage
  for seen buildings lose coverage when transferred to unseen buildings [@hao2026], but it evaluates pooled coverage and
  does not study how a new building's own data should enter the calibration."
- 03_related, proposed: "A recent cross-building evaluation found that split-conformal coverage drops when the model is
  transferred to unseen buildings [@hao2026]."
- If the authors want to keep "recommends recalibration", they must check it against the full text first.

**Pinto et al. 2022 (`pinto2022`).** The abstract (OpenAlex) says the review classifies 77 papers and "identified four main
application areas of transfer learning: (1) building load prediction, (2) occupancy detection and activity recognition,
(3) building dynamics modeling, and (4) energy systems control". The full text was not reachable, so whether load prediction
is the *most frequent* area could not be checked.
- Proposed: "…a review of 77 studies identifies building load prediction as one of four main application areas of transfer
  learning in smart buildings [@pinto2022]…"

**GHCP (`mallick2026`, arXiv:2608.15500v1).** Checked against the full HTML text, Eq. (5). One donor group J₀ is drawn
uniformly from the eligible reference groups, removed from calibration, and its size N_{J₀} is given to the test group.
Each remaining calibration group and the test group then get total mass 1/(|S_cal|+1). The test group's mass is split:
each of its o−⌊o/2⌋ observed held-out scores gets 1/((|S_cal|+1)L_{K+1}), and the unobserved remainder
(N_{K+1}−o)/((|S_cal|+1)L_{K+1}) is a point mass at +∞. The first ⌊o/2⌋ observations fit a local predictor. So "the
weight of a single reference group" is correct for the *total* weight, but it hides the randomly donated size and the
+∞ mass.
- Proposed (03_related): "…GHCP uses a new group's first few observations together with reference groups while retaining a
  finite-sample guarantee: the new group is assigned the size of a randomly drawn donor group and receives the same total
  weight as one reference group, with the share belonging to its not-yet-observed scores placed at +∞ [@mallick2026]."
- 05_setup already describes the +∞ mass and the deviation from the random donor size correctly. Its statement "every
  calibration building receives total weight 1/(M+1)" matches Eq. (5) if M = |S_cal|.

## 4. Where to cite each new reference (one sentence each)

- `zhang2026transfer`, Related Work (conformal under shift/transfer): "Transfer conformal inference uses labelled
  source-domain data to make target-domain prediction intervals more efficient while keeping coverage [@zhang2026transfer].
  Our setting differs because the 'target' is each new building, which has very few labelled scores."
- `zhang2024posterior` and `guan2023`, Related Work (conditional/local calibration): "Localized [@guan2023] and posterior
  [@zhang2024posterior] conformal prediction reweight calibration scores towards points similar to the test point. Our
  similarity prior applies the same idea at the building level rather than the observation level."
- `barber2021limits`, Related Work or Discussion limitation 1: "Exact distribution-free conditional coverage is impossible
  in general [@barber2021limits], so per-building reliability can only be approximated or established empirically."
- `angelopoulos2023pid`, `bhatnagar2023`, `li2025ncc`, Related Work (online time-series methods, after ACI): "Later online
  methods replace ACI's single step size with PID-style quantile tracking [@angelopoulos2023pid], strongly adaptive expert
  aggregation (SAOCP) [@bhatnagar2023] or a learned neural controller [@li2025ncc]. All of these adapt *after* errors are
  observed and therefore cannot help on a building's first days."
- `kath2021`, `jensen2024`, Introduction/Related Work (conformal in energy forecasting): "Conformal intervals have been
  applied to day-ahead and intraday electricity-price forecasting [@kath2021] and, via ensemble CQR, to energy time series
  [@jensen2024]."
- `buhlmann1967`, `buhlmann2005`, Method (Eq. hsc) and Related Work: "The weight n/(n+κ) is Bühlmann's credibility factor
  [@buhlmann1967; @buhlmann2005]." Cite these primary sources next to, or instead of, `hong2023cred`.
- `jin2022`, Related Work (cold-start building forecasting): "Jin et al. combine transfer learning with an adjustment of the
  interval estimate for the target building [@jin2022], the closest building-energy precedent for correcting transferred
  intervals."
- `ansari2024`, Introduction/Related Work: "Pretrained probabilistic time-series models such as Chronos [@ansari2024]
  produce zero-shot quantile forecasts that could replace our global forecaster; their intervals need the same
  per-building calibration."
- `eia2026elec`, Introduction, first sentence: "In the United States, residential and commercial buildings account for
  about three-quarters of retail electricity sales [@eia2026elec]…". The source is U.S.-only, so the sentence must not say
  "globally".
- `zhou2026der`, Related Work (hierarchical conformal in energy): "Hierarchical conformal prediction has also been applied
  in the energy domain, for distributed-energy-resource adoption across a spatial hierarchy [@zhou2026der]."

## 5. Further Energy and Buildings / Applied Energy / Advances in Applied Energy papers (task 5)

I ran Crossref `query.bibliographic` and `query.title=conformal` searches restricted by ISSN (0378-7788, 0306-2619,
2666-7924, 2020–2026). Besides `jin2022` (added), the candidates were:
- Liang X, Liu Z, Wang J, Jin X, Du Z. Uncertainty quantification-based robust deep learning for building energy systems
  considering distribution shift problem. Appl Energy 2023;337:120889. https://doi.org/10.1016/j.apenergy.2023.120889
- Liu S, Yan J, Yan Y, Liu K, Hao R, Han S, Liu Y. Fine-grained potential load flexibility estimation based on
  meta-learning-inspired adaptation and conformal quantile regression. Appl Energy 2026;424:128502.
  https://doi.org/10.1016/j.apenergy.2026.128502
- Cui E, Shao Y, Chen Z, Lin Y, Liu Y. Building energy forecast routing for grid-responsive BEMS: Selective conformal
  screening under operational uncertainty. Energy Build 2026;371:118170. https://doi.org/10.1016/j.enbuild.2026.118170

None of these were added. Their bibliographic data is verified on Crossref, but no abstract or full text could be read
(Crossref, OpenAlex, Semantic Scholar and the Elsevier API returned no abstract; ScienceDirect returned 403). Their relevance
to *recalibrating intervals for transferred load models at new buildings* therefore rests on the titles only. Read the
abstracts before citing them; Liang et al. 2023 looks the most relevant.
