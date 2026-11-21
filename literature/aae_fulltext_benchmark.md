# Full-text benchmark: accepted research articles in *Advances in Applied Energy* (AAE, ISSN 2666-7924)

Compiled 2026-11-20. Scope: AAE research articles close to probabilistic / day-ahead load forecasting, uncertainty quantification, building-energy ML, data-scarce / transfer / active learning, and benchmark-type studies.

## 0. Sources, access and how far the evidence goes

* **ScienceDirect** returned HTTP 403. The Elsevier TDM API link that Crossref advertises returns metadata only when no API key is sent. **OpenAlex** was over its daily free budget (HTTP 429/"Insufficient budget") all session. **Unpaywall** rejected placeholder e-mails. **DiVA (Uppsala)** reset the connection through the proxy, so the Lindberg et al. full text could not be fetched.
* Full texts I did get (all files are in `/tmp/claude-0/aae_bench/pdf/`, with extracted text in `/tmp/claude-0/aae_bench/txt/`):

| File | Paper | Source | Version |
|---|---|---|---|
| zech2024.pdf | Zech, Tetens, Ranalli 2024, 10.1016/j.adapen.2024.100191 | elib.dlr.de/208726 | **Published VoR** (AAE layout) |
| wang2025.pdf | X. Wang, Liu, Kang, Xiao, Yan 2025, 10.1016/j.adapen.2025.100246 | ira.lib.polyu.edu.hk/10397/117509 | **VoR** |
| han2024.pdf | Han, Li, Wang 2024, 10.1016/j.adapen.2024.100186 | ira.lib.polyu.edu.hk/10397/111756 | **VoR** |
| li2024.pdf | A. Li, Xiao et al. 2024, 10.1016/j.adapen.2024.100189 | ira.lib.polyu.edu.hk/10397/112192 | **VoR** |
| siels2026.pdf | Murthy et al. 2026, 10.1016/j.adapen.2026.100309 | osti.gov (DOE PAGES) | **VoR** |
| gilleran2021.pdf | Gilleran et al. 2021, 10.1016/j.adapen.2021.100062 | osti.gov/servlets/purl/1821903 | **VoR** |
| wang2021_am.pdf | Z. Wang, Hong, Li, Piette 2021, 10.1016/j.adapen.2021.100025 | escholarship.org qt0c11p173 (LBNL) | Accepted manuscript (39 pp., LBNL cover page) |
| tgdlf2_arxiv.pdf | Gao, Hu, Zhang, Chen: arXiv 2210.02448 = AAE 10.1016/j.adapen.2023.100142 | arXiv | **Preprint**. The AAE abstract figures (about 16 % better than TgDLF, 50 % weather noise) match the preprint. The AAE title was changed to "An adaptive deep-learning load forecasting framework by integrating transformer and domain knowledge" |
| skygpt_arxiv.pdf | Nie et al.: arXiv 2306.11682 = AAE 10.1016/j.adapen.2024.100172 | arXiv | **Preprint** (title and format differ from the AAE version) |

* Every DOI above has the prefix 10.1016/j.adapen. AAE publication was checked against Crossref and the AAE masthead on the VoR PDFs. The two preprints' structural figures (headings, length) may differ from the published versions. I use them only for content and validation design.
* **Highlights and graphical abstracts are not in the Elsevier VoR PDFs**, so they could not be checked from full text. Treat them as unknown, not absent.
* Statistics such as word counts are approximate. They come from `pdftotext`, include figure and table text, and run from the start of the body to "References".

---

## 1. Per-paper table (full texts)

### 1a. Core relevant papers

| | **Zech 2024** (100191) | **X. Wang 2025** (100246) | **Han 2024** (100186) | **A. Li 2024** (100189) | **Z. Wang 2021** (100025) | **Gao 2023 / TgDLF2.0** (100142) [preprint] | **Nie 2024 / SkyGPT** (100172) [preprint] |
|---|---|---|---|---|---|---|---|
| Title | "Toward global rooftop PV detection with Deep Active Learning" | "Prediction-based control of energy storage systems using dynamic accuracy weighting" | "A probabilistic model for real-time quantification of building energy flexibility" | "Active learning concerning sampling cost for enhancing AI-enabled building energy system modeling" | "Predicting city-scale daily electricity consumption using data-driven models" | AAE: "An adaptive deep-learning load forecasting framework by integrating transformer and domain knowledge" | AAE: "SkyGPT: Probabilistic ultra-short-term solar forecasting using synthetic sky images from physics-constrained VideoGPT" |
| Title style | Goal + method, no colon | Task + method ("using …") | "A [model] for [task]" | Method + purpose | Task + "using data-driven models" | Descriptive framework title (preprint used model acronym) | Acronym + colon + descriptive |
| Review timeline (VoR) | Rec. 5 Aug 2024 → acc. 25 Sep 2024 | Rec. 22 Sep 2025 → acc. 28 Sep 2025 | Rec. 17 Jun → acc. 15 Aug 2024 | Rec. 27 May → acc. 2 Sep 2024 | n/a (AM) | n/a | n/a |
| Abstract words / numbers | ~200 / **1 number** (3 % of data) | ~245 / **7** (6.5 %, 10 capacities, 18 tariffs, 93.9–97.2 % vs 86.4–95.4 %) | ~190 / **5** (150 buildings, 3605 s → 6.7 s, 537×, 8×) | ~250 / **0 numbers** | ~300 / **~20** (CVRMSE per city, 30–50 %, 5 %/°C, −10 %) | ~200 / 2 (16 %, 50 % noise) | ~255 / 7 (CRPS 2.81, −13 %/−23 %, Winkler 26.70) |
| Abstract shape | context → gap → "we compare" → 1 result → implication | context → problem (accuracy metrics not monotone with control) → method → quantified result → scalability → tool → implication | context → need → method → validation set → quantified speed and accuracy | context → problem → method → cost metric → "comprehensive comparison of five AL methods" on real data → qualitative result → implication | need → 3 model families → 7 models, 3 cities → numbers → applications (heat wave, COVID) | problem → method → CV result → robustness → TL | gap → method → benchmark → numbers → practical recommendation (10 scenarios) |
| Keywords | 5 | 5 | 5 | 6 | 5 | 6 | 4 |
| Numbered headings | Yes (1–6 + Appendices A, B) | Yes (1–5 + Appendices A–H) | Yes (1–6) | Yes (1–4 + Appendix) | Yes (1–6) | Yes | Yes |
| Main sections | 1 Introduction (1.1 Background, 1.2 Related works, **1.3 Research contributions**); 2 Deep active learning; 3 Experimental design (datasets, training, verification, simulation, computational implementation); 4 Results; 5 Discussion; 6 Conclusion | 1 Introduction; 2 Methodology; 3 Results (multiple buildings / capacities / tariffs); 4 Discussions (**4.1 Application perspectives**, **4.2 Limitations and future works**); 5 Conclusions | 1 Intro; 2 Proposed probabilistic model; 3 Validation test arrangement; 4 Performance evaluation; 5 Discussion (5.1, **5.2 Real-world implementation**, **5.3 Limitations … future research**); 6 Conclusion | 1 Intro (1.1–**1.3 Research gaps and contributions**); 2 Methodology (incl. 2.4 Data experiments); 3 Results and discussions (3.3 Discussions); 4 Conclusion | 1 Introduction (Background, **Objectives**); 2 Methodology; 3 Results; 4 Applications; 5 Discussion (**5.1 Implications**, **5.2 Limitations**); 6 Conclusions | Intro; 2 Methodology; 3 Experiments (data, forecasting, additional analysis, transfer learning); Conclusions; Appendices | Intro; related work; method; experiments; **6 limitations / future work**; conclusion |
| Length (body words, approx.) | ~10,400 | ~10,500 (incl. long appendices) | ~7,000 | ~8,000 | ~10,600 (AM, double-spaced) | ~6,400 | ~13,500 |
| Figures / tables | 11 / 3 | 5 + 7 appendix / 1 + 3 appendix | 8 / 2 | 10 / 3 | ~19 / few | ~10 / ~3 | 13 / ~1 |
| References | 86 | 79 | 56 | 58 | 61 | 48 | 58 |
| Nomenclature | No | **Abbreviation table** (end) | No | No | No | No | No |
| Contribution list in intro | 4 research questions (numbered) | 3 numbered gaps + 3 numbered contributions | 3 bullet "original contributions" ("first attempt") | Prose (gaps "First… Secondly… Thirdly") | "twofold" contributions (2 bullets) | "four-fold" numbered | bulleted contributions |
| Practical-implications section | In Discussion (annotation effort; operational software next) | **4.1 Application perspectives** + web tool (App. G) | **5.2 Real-world implementation** (steps for aggregators, challenges) | Discussion gives implementation guidance (compute time per round) | **5.1 Implications** (7 numbered findings for utilities and planners) | Brief | Recommends 10 scenarios as cost/accuracy trade-off |
| Limitations section | In Discussion (single architecture, caveats) | **Yes (4.2)** | **Yes (5.3)** | Brief, in discussion | **Yes (5.2)** | No | Yes |
| Data/code statement | Data public (except one set); code "on GitHub once accepted"; CRediT; competing interests | "Data will be made available on request"; CRediT; GenAI declaration | "Data will be made available on request" | "The authors do not have permission to share data" | **All data and code on GitHub** (stated as a contribution) | – (preprint) | GitHub link (preprint) |
| Validation | **6 aerial-image datasets** from several regions; **3 seeds** with min–max bands; baselines random sampling and full-data training; second architecture (SegFormer) in appendix; no significance tests | **6 buildings** with ice storage; **180 prediction models** (6 algorithms × 30 hyperparameter sets); **10 capacities × 18 TOU tariffs**; baselines MAPE, CV-MAE, CV-RMSE; no significance tests | **150 simulated commercial buildings** (prototype ±20 %); 1 typical summer day; compared with deterministic, numerical-probabilistic and archetype models; accuracy and run time | **1 real high-rise building** (cooling towers); 5 AL methods vs base models; RMSE on unseen conditions; compute time | **3 metro areas**; 7 models; train/test split; CVRMSE; complexity and interpretability comparison | **12 Beijing districts**; cross-validation across districts; noise robustness (weather noise up to 50 %); transfer-learning experiments | **1 PV system** (30 kW); baselines SUNSET and smart persistence; CRPS, Winkler; number of scenarios vs cost |
| Statistical tests | None | None | None | None | None | None | None |
| Novelty type | **Empirical comparison** of existing acquisition functions + application scenarios (fine-tuning, joint learning) | New metric (method) + multi-case evidence + tool | New analytical model (speed-up) | New sampling strategy + new cost metric + **comprehensive comparison** | **Empirical comparison** of standard models + applications; open data/code | New model/framework (TL + transformer + domain knowledge) | New generative model |
| Tone | "we compare", "We believe…"; moderate claims | Impersonal ("this study"), "evidently enhances", "novel attempt" | "this paper", "To our best knowledge, … first attempt", "dramatically reduces" | Impersonal, "novel", "comprehensive and in-depth" | Heavy "we", plain, hedged ("might not necessarily outperform") | "we", "proves its robustness" | "we", "extensive experiments" |

### 1b. Peripheral full texts (structure only)

| Paper | Notes |
|---|---|
| Murthy et al. 2026, SIELS (10.1016/j.adapen.2026.100309) | **Data/empirical-model paper**: industrial hourly load shapes built by clustering California meter data and sampling from it. Headings: 1 Intro; 2 Data; 3 Simulation; 4 Results (4.2 Use case: value of flexibility); **5 Limitations** (separate section); 6 Conclusion; 7 Simulation outputs. ~10.6k words, 10 figures, 49 references, abstract ~230 words with almost no numbers, 5 keywords, data availability statement. Rec. 21 Jul → acc. 26 Sep 2026. |
| Gilleran et al. 2021 (10.1016/j.adapen.2021.100062) | Simulation/scenario study. Unnumbered headings (Introduction … Discussion, Conclusions; older AAE layout). ~6.6k words, 9 figures, 76 references, abstract ~165 words with 2–3 numbers, 6 keywords, "Data availability" (profiles freely downloadable). Rec. 11 Aug → acc. 13 Aug 2021, probably a transfer from another journal. |

### 1c. Relevant AAE papers I could NOT get in full (abstract or metadata only; not used for structural statistics)

* Lindberg et al. 2023, 10.1016/j.adapen.2022.100120, "Day-ahead probabilistic forecasting at a co-located wind and solar power park in Sweden: Trading and forecast verification". The DiVA copy exists (diva2:1770882) but was unreachable here. The abstract evaluates CRPS, interval and quantile scores of existing probabilistic methods on one park. It is closer to an **analysis/verification study** than a new-model paper.
* Guo, Huang, Wang 2024, 10.1016/j.adapen.2024.100165 (attentive QR-TCN probabilistic load forecasting). No open copy found.
* Peterssen et al. 2024, 10.1016/j.adapen.2024.100181, "Impact of forecasting on energy system optimization". Abstract: compares an LP (perfect foresight) with a priority-list heuristic; 28 % and 22 % cost gaps.
* **Lademann et al. 2026, 10.1016/j.adapen.2026.100300, "Real-world benchmarking of control strategies in an industrial energy system"**. Only the title, the Crossref record and the supplementary dataset (TU Darmstadt tudatalib: RL vs MPC vs market-based control, simulation plus real-world experiments) were accessible. The paper itself was not.
* Gan et al. 2026 (100293, multi-model short-term load prediction for a microgrid), Fan et al. 2026 (100280, decision-focused learning), Xiong et al. 2025 (100250, multimodal probabilistic solar). No open copy found.

---

## 2. Targeted searches

**Conformal prediction / prediction intervals / interval calibration in AAE.** I searched AAE titles (Crossref, all 308 + 103 items up to 2026-11) and ran Crossref bibliographic queries for "conformal prediction", "prediction interval", "quantile regression" and "uncertainty quantification", plus web searches. **No AAE article with conformal prediction or interval calibration as its subject was found.** The closest interval-related AAE work:

* Probabilistic forecasting with interval/probabilistic scores: SkyGPT (CRPS, Winkler; 100172), Lindberg 2023 (interval score, CRPS; 100120), Guo 2024 (quantile regression; 100165), Xiong 2025 (100250).
* Uncertainty propagation: Han 2024 (sampling-based probability–capacity curves; 100186), Hu 2023 robust MPC (100124).
* X. Wang 2025 names "novel application-oriented prediction accuracy metrics … based on the confidence interval of prediction uncertainty" as **future work** (Section 4.2). This is a direct opening for interval-based work in the same building-ML community.

*Caveat:* Crossref does not search abstracts or full texts, and OpenAlex full-text search was unavailable. A paper that uses conformal methods without saying so in its title could have been missed.

**Cold-start / newly metered building forecasting.** **No AAE article on cold-start building load forecasting was found.** The data-scarcity neighbours are Gao 2023 (transfer learning "for realistic scenarios with scarce samples" across Beijing districts), A. Li 2024 (active learning for limited operating ranges), Zech 2024 (label-efficient deep active learning), Pinto 2022 (TL for smart buildings, review, 100084) and Liu 2023 (TL for batteries, review).

**Pure empirical-comparison / benchmark papers accepted in AAE.** Yes, they exist:

1. **Z. Wang et al. 2021, 10.1016/j.adapen.2021.100025** (full text read). It proposes no new model. It compares 7 standard models (change-point, HDD/CDD, Prophet, LightGBM, RF, SVM, NN) on 3 cities. The stated contributions are the comparison itself, open data and code, and applications (heat waves, COVID). It has about 123 citations (per the earlier metadata file).
2. **Zech et al. 2024, 10.1016/j.adapen.2024.100191** (full text read). It compares 3 existing deep-active-learning acquisition functions against random sampling on 6 regional datasets, 3 seeds, and 2 training variants. The contribution is framed as 4 research questions, and no new algorithm is proposed. Accepted 7 weeks after submission.
3. **A. Li et al. 2024, 10.1016/j.adapen.2024.100189** (full text read). A hybrid: the first stated gap is "a lack of comprehensive and in-depth comparison of various active learning methods". It adds a proposed sampling strategy and a new evaluation (cost) metric.
4. **Lademann et al. 2026, 10.1016/j.adapen.2026.100300** (title and supplement only). A benchmarking paper of RL vs MPC vs market-based control on a real industrial system.
5. Supporting abstract-level examples: Lindberg 2023 (forecast verification and value), Peterssen 2024 (comparison of operation strategies), and Murthy 2026 SIELS (dataset/empirical-model contribution).

---

## 3. Synthesis

**Typical structure.** All VoR papers from 2024 on use numbered IMRaD-like sections with energy-engineering naming: 1 Introduction (often with subsections Background / Related work / **Research gaps and contributions**); 2 Methodology (or "Proposed …"); 3 "Validation test arrangement" / "Experimental design" / "Data"; 4 Results; 5 Discussion; 6 Conclusion(s). The Discussion usually holds subsections for **application or real-world implementation** and **limitations and future work** (Han 5.2/5.3; X. Wang 4.1/4.2; Z. Wang 5.1/5.2; SIELS 5). After the conclusion come the Elsevier back-matter blocks: CRediT statement, Declaration of competing interest, (GenAI declaration from 2025), Acknowledgements, **Data availability**. Appendices are common and can be long (X. Wang 2025 has A–H, including model lists, case-building data, tariffs, and the web tool).

**Length.** VoR bodies run about 7,000–10,500 words, 8–12 main figures, 1–3 main tables, and 56–86 references (median about 60). This is 9–20 journal pages.

**Abstract style.** A single unstructured paragraph of about 190–250 words, in the order context → specific problem/gap → what this study does → data and validation scale → results → implication. Most give **concrete numbers** (percent improvements, speed-ups, scale of validation such as "150 buildings", "6 energy storage systems", "10 capacities and 18 tariffs"). Two accepted papers (Zech, A. Li) give one number or none, so numbers are the norm but not mandatory. Keywords: 5–6.

**Contribution framing.** Almost every paper states an explicit gap and contribution list in the introduction: numbered gaps followed by numbered contributions (X. Wang 2025), 3 bullets including "first attempt" (Han), numbered research questions (Zech), or a "twofold/four-fold" list. Contributions are framed around an **energy-application payoff** rather than ML novelty: lower operating cost, real-time market participation, less labelling effort for PV registries, planning under heat waves. Comparison studies justify themselves by naming a decision the comparison informs: which acquisition function to use, which accuracy metric to pick a model by, whether ML beats linear models.

**Validation depth.** Moderate. Typical evidence is **one real system or a handful of cases, made broad through scenario or sensitivity sweeps** (6 buildings × 10 capacities × 18 tariffs; 150 synthetic buildings; 6 datasets × 3 seeds; 3 cities; 12 districts). Baselines are established methods or metrics. **None of the seven core papers uses formal significance testing.** Repeated seeds appear in only one (Zech, 3 seeds, min–max bands). Robustness or generalisation checks distinguish the stronger papers: noise injection (TgDLF2.0), a second architecture (Zech App. B), cross-region datasets (Zech), and capacity/tariff sweeps (X. Wang).

**What distinguishes them.** (i) A clearly operational energy question. (ii) Quantified practical benefit (cost, time, labelling effort). (iii) Scale or diversity of test cases that makes the conclusion transferable. (iv) An explicit implementation pathway (web tool, steps for aggregators, open code). (v) Candid limitations.

**Tone.** Mixed: impersonal "this study/this paper" (PolyU and Tsinghua papers) or first-person "we" (DLR, LBNL, Stanford). Claims language is fairly assertive ("dramatically reduces", "evidently enhances", "first attempt", "comprehensive and in-depth"), but limitations are stated openly.

**Open science.** Mixed and not enforced. Statements range from "data will be made available on request" and "no permission to share data" to full GitHub release. Open data and code were presented as a contribution in the comparison paper (Z. Wang 2021) and promised in Zech 2024.

---

## 4. Checklist for a manuscript to read like an accepted AAE research article

1. **Title**: descriptive, application-anchored, 10–16 words; method + target ("… for prediction intervals of newly metered buildings"). An acronym is optional. A colon subtitle is acceptable (e.g. "…: A case study of …").
2. **Abstract**: one paragraph, about 200–250 words, in the order context → specific gap → what the study does → data scale (number of buildings, sites, horizons) → **2–6 concrete numbers** (coverage, width, cost or skill gains vs baselines) → practical implication. No citations.
3. **Keywords**: 5–6.
4. **Highlights and graphical abstract**: required by Elsevier submission systems as a rule, but I could not verify them from the PDFs. Prepare 3–5 highlights and a graphical abstract anyway.
5. **Numbered sections**, e.g. 1 Introduction (1.1 Background, 1.2 Related work, **1.3 Research gaps and contributions**); 2 Methodology; 3 Data and experimental design (or "Validation test arrangement"); 4 Results; 5 Discussion (5.1 **Practical implications / implementation**, 5.2 **Limitations and future work**); 6 Conclusions.
6. **Gaps and contributions**: end the introduction with 2–4 numbered gaps and 3–4 numbered contributions, or numbered research questions (Zech style, which suits comparison studies). Close with a roadmap paragraph ("The rest of this paper is organized as follows…").
7. **Nomenclature**: optional. Only 1 of 7 papers had an abbreviation table. Add one if the paper uses many symbols (coverage α, nonconformity scores, calibration-window notation).
8. **Length**: about 7,000–10,500 words of body; 8–12 main figures; 1–4 main tables; 50–85 references. Push secondary material (model lists, hyperparameters, per-building results) to appendices, as X. Wang 2025 did with A–H.
9. **Validation**: several real buildings or datasets plus scenario sweeps. Use established baselines, report seeds and spread where training is stochastic, and add at least one robustness or generalisation axis (other climate or region, other base model, other horizon). Significance tests are not the journal norm, so including them (e.g. paired tests or bootstrap CIs across buildings) would be above the benchmark.
10. **Practical implications section**: spell out who uses the result (utilities, aggregators, building operators) and how, step by step, with implementation costs (compute time, data needed). A tool or code release is a plus.
11. **Limitations section**: explicit and specific (data coverage, number of sites, assumptions), paired with future work.
12. **Back matter**: CRediT statement, Declaration of competing interest, GenAI-use declaration (seen in 2025), Acknowledgements and funding, **Data availability** (public data and code preferred; open release can itself be a stated contribution).
13. **Tone**: either "we" or impersonal is fine. Use quantified claims, and use "first" or "novel" sparingly and only with "to our best knowledge".

---

## 5. Is a "comparison study + design evidence" paper at the accepted-paper level?

**Yes, within the range of accepted AAE research articles, provided it is framed around an operational decision and validated broadly.** Evidence:

* **Z. Wang et al. 2021 (100025)** is a pure comparison of seven off-the-shelf models on three cities, with no new model. Its contributions are the comparison, open data and code, and applied findings for planners (heat-wave and COVID impacts, a seven-point "Implications" list). It is among the journal's most-cited research papers.
* **Zech et al. 2024 (100191)** compares existing deep-active-learning acquisition functions on six datasets with three seeds. The contribution is framed as four research questions and practical guidance ("Entropy … most favorable"), with no new algorithm. Accepted about 7 weeks after submission with one revision.
* **A. Li et al. 2024 (100189)** puts "lack of comprehensive and in-depth comparison" first among its gaps, then adds a modest methodological element (a sampling strategy and a cost metric).
* **X. Wang 2025 (100246)** is mostly design evidence on how to *select* among 180 existing models for a downstream task. Its novelty is an evaluation metric, not a predictor, validated across buildings, capacities and tariffs.
* **Lademann et al. 2026 (100300)** has "benchmarking" in the title (full text not seen).

**Conditions the accepted comparison papers meet, which a conformal-calibration comparison should also meet:**

1. Name a concrete decision the comparison settles (which calibration strategy to deploy for a newly metered building, with how much data, at what coverage cost), and give design rules.
2. Provide breadth: several buildings and categories, scenario sweeps (calibration-window length, coverage level, horizon), and a robustness axis such as base model or climate.
3. Quantify practical value: coverage error, interval width, and ideally a downstream cost or risk proxy.
4. Release code and data where possible, which reinforces the "benchmark" value (Z. Wang 2021).
5. Include explicit Practical-implications and Limitations subsections.

**Risks:**

* Most AAE forecasting papers in this area (TgDLF/Adaptive-TgDLF, SkyGPT, QR-TCN, Han 2024) propose a new model or framework. A pure comparison is the minority pattern, so it must be compensated by breadth and clearly actionable design evidence.
* AAE has published **no conformal-prediction or cold-start building paper** that I could find. That is novelty in favour of the submission, but the introduction must establish relevance for an energy-application audience rather than an ML one.
* Reviewers may ask why an existing method is not extended. A small methodological element (a selection rule, a calibration-data heuristic, a metric linking interval quality to an operational cost, as X. Wang 2025 and A. Li 2024 did) would move the paper from "comparison" to "comparison + design method", which is the safer level for this journal.

---

### Source URLs used
* https://elib.dlr.de/208726/2/1-s2.0-S2666792424000295-main.pdf
* https://ira.lib.polyu.edu.hk/bitstream/10397/117509/1/1-s2.0-S266679242500040X-main.pdf
* https://ira.lib.polyu.edu.hk/bitstream/10397/111756/1/1-s2.0-S2666792424000246-main.pdf
* https://ira.lib.polyu.edu.hk/bitstream/10397/112192/1/1-s2.0-S2666792424000271-main.pdf
* https://escholarship.org/content/qt0c11p173/qt0c11p173.pdf
* https://www.osti.gov/servlets/purl/1821903 ; OSTI record for 10.1016/j.adapen.2026.100309 (found through the OSTI API, journal filter)
* https://arxiv.org/pdf/2210.02448v1 ; https://arxiv.org/pdf/2306.11682v1
* https://tudatalib.ulb.tu-darmstadt.de/items/7ea83a91-14f2-4510-8143-b689f8dffe28/full (Lademann supplementary data)
* https://uu.diva-portal.org/smash/get/diva2:1770882/FULLTEXT01.pdf (Lindberg; could not be reached)
* Crossref API (journal 2666-7924) and Semantic Scholar API for metadata
