# Target-journal benchmark: *Advances in Applied Energy* (Global Update 3)

Source: Crossref listing of all 308 journal items (literature/aae_all_works_crossref.json); 25 most relevant
items (by topic and citations) with abstracts from OpenAlex (literature/aae_25_papers_openalex.json).
**Limitation:** full texts were not accessible from this environment (ScienceDirect blocks automated
access), so fields 9–17 below are assessed from abstracts and marked "n/s" (not stated) when the abstract
does not say. No claim about these papers beyond their abstracts is made in the manuscript.

| # | Paper (year; citations) | Type | Problem / gap | Novelty type | Data | Validation & baselines (from abstract) | Stats / robustness / generalisation | Why it fits AAE |
|---|---|---|---|---|---|---|---|---|
| 1 | Li et al. 2021, energy flexibility of residential buildings (449) | review | fragmented flexibility metrics | synthesis | literature | — | — | grid–building interface |
| 2 | Chen et al. 2023, interpretable ML for building energy mgmt (378) | review | black-box ML trust | synthesis/taxonomy | literature | — | — | ML for buildings |
| 3 | Pinto et al. 2022, transfer learning for smart buildings (318) | review | TL scattered; 77 papers | synthesis | literature | — | — | ML for buildings; identifies load prediction as main TL use |
| 4 | Paletta et al. 2023, solar forecasting with computer vision (178) | review | sky-image forecasting | synthesis | literature | — | — | renewable forecasting |
| 5 | Liu et al. 2022, TL for battery state estimation (174) | review | battery management | synthesis | literature | — | — | storage |
| 6 | Gilleran et al. 2021, EV charging impact on retail buildings (168) | research | EV charging peak impact | scenario analysis | simulated store, climates | scenario comparison | multi-climate sensitivity | electrification |
| 7 | Chen & Zhang 2021, TgDLF (126) | research | accurate & robust STLF | theory-guided DL | district loads | vs LSTM; cross-validation; 23 % better | noise robustness (40 % weather noise) | load forecasting with domain knowledge |
| 8 | Wang et al. 2021, city-scale daily electricity (123) | research | extreme-weather demand | model comparison (7 models) | 3 US metros | CV(RMSE) comparison | heat-wave/COVID scenarios | utility planning |
| 9 | Jiang et al. 2025, physics-informed ML for BPS (90) | review | PIML in building simulation | synthesis/guideline | literature | — | — | ML + physics |
| 10 | Zhao et al. 2021, NY 100 % renewable under uncertainty (85) | research | robust transition planning | data-driven MARO (Dirichlet-process mixture uncertainty sets) | NY state | vs deterministic | uncertainty sets | system planning under uncertainty |
| 11 | Gao et al. 2023, Adaptive-TgDLF (82) | research | scarce samples, shifting distributions | transformer + transfer + online learning | districts | vs TgDLF; cross-validation; 16 % better | 50 % weather noise; transfer across locations | cold-start/adaptive forecasting |
| 12 | Liang et al. 2024, PCNN MPC tropical net-zero office (67) | research (case study) | flexibility quantification in tropics | physically consistent NN MPC | 1 building (Singapore) | case study | n/s | flexibility |
| 13 | Nie et al. 2024, SkyGPT (66) | research | probabilistic 15-min PV forecasting | generative video prediction | 1 PV system (30 kW) | vs CNN, smart persistence; CRPS −13 %/−23 % | reliability & sharpness | probabilistic forecasting |
| 14 | Lindberg et al. 2023, co-located wind–PV probabilistic (60) | research | probabilistic forecasting of co-located parks | analysis of aggregation | 1 park, 3 years | CRPS, interval score, quantile score | seasonal breakdown; trading value | probabilistic forecasting value |
| 15 | Hu et al. 2023, multi-zone robust MPC (56) | research | control under weather-forecast error | data-driven robust MPC | simulation | vs benchmarks | uncertainty sets | control under uncertainty |
| 16 | Guo et al. 2024, attentive QR-TCN (50) | research | multi-energy probabilistic forecasting | attention + QR-TCN | ASU campus | "superior performance" vs benchmarks | n/s | probabilistic load forecasting |
| 17 | Qiu et al. 2022, retail pricing chance-constrained (47) | research | retailer bidding | bi-level + CNN-LSTM forecast | market data | n/s | chance constraints | markets |
| 18 | Li et al. 2024, active learning for HVAC modelling (26) | research | generalisation with limited operating data | Mahalanobis-based sampling | cooling-tower data | 5 AL methods compared | sampling-cost metric | data-efficient building models |
| 19 | Peterssen et al. 2024, impact of forecasting on ESOM (25) | research | perfect-foresight bias | LP vs priority list | German system model | two strategies | cost bounds | forecast value |
| 20 | Han et al. 2024, probabilistic real-time flexibility (25) | research | fast probabilistic flexibility | analytical solution + sampling | 150 Hong Kong buildings | vs numerical (537× faster), archetype | uncertainty analysis | flexibility under uncertainty |
| 21 | Zech et al. 2024, global rooftop PV detection with deep AL (25) | research | label efficiency across regions | deep active learning comparison | multi-region datasets | AL algorithm comparison | cross-region | data efficiency/generalisation |
| 22 | Jiang et al. 2025, PIML modular NN for DRL control (25) | research | physics consistency | modular PINN + DRL | case building | 31.4 % HVAC savings | physical-consistency metric | ML control |
| 23 | Dougherty et al. 2023, TOM.D (23) | research | microclimate in UBEM | remote-sensing data fusion | urban | n/s | n/s | urban energy modelling |
| 24 | Luo et al. 2024, land-use electricity prediction (20) | research | multi-scale consumption | interpretable ML | 297 cities, 2,505 counties | R² 0.91 | multi-scale | planning |
| 25 | Waterworth et al. 2021, smart building metadata NLP (35) | research | sensor tagging | TL with LMs | BMS metadata | vs prior approaches | n/s | digitalisation |

(First authors from OpenAlex metadata.)

## Benchmark conclusions (expectations of the journal)
1. **Novelty level:** methodological or system-level innovation with a clear *energy-application*
   payoff (flexibility, planning, forecasting value). Pure ML novelty without energy relevance is not the
   pattern; ML papers frame their contribution around an operational energy problem.
2. **Methodological sophistication:** moderate-to-high (theory-guided DL, generative models, robust
   optimisation, analytical uncertainty models). Closed-form/analytical contributions are valued when
   they bring speed or reliability (e.g. #20: 537× speed-up).
3. **Experimental depth:** typically one site/system or one dataset, case-study style; benchmark against
   a few baselines; robustness tests to noise are present in the strongest forecasting papers (#7, #11).
4. **Statistics:** formal significance testing is rare in the abstracts; cross-validation is common.
5. **Generalisation:** transfer across locations (#11) and multi-region evaluation (#21) distinguish
   stronger papers.
6. **What differentiates the strongest papers:** a clear practical problem, a principled method,
   quantified gains with an operational interpretation, and robustness/generalisation evidence.

## Implications for this manuscript
- Frame HSC around an operational problem (onboarding buildings into DR/flexibility/M&V platforms)
  and quantify the operational meaning (share of buildings with unreliable intervals).
- Exceed the typical experimental depth: two datasets, more than 1,100 buildings, 5 seeds, leave-site-out,
  cross-country, stress tests, paired statistics. This is a realistic way to be *stronger* than typical
  journal papers, not a claim of superiority over them.
- Keep the method closed-form and cheap (an advantage the journal values: #20).
- Direct quantitative comparison with these papers is impossible: different problems and datasets.
