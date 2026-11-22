| Study | Units and data | Prior from other units | Unit's own scores | Online feedback | Reliability assessed per unit | New units (cold start) |
|:--|:--|:--|:--|:--|:--|:--|
| ACI, DtACI, conformal PID [@gibbs2021; @gibbs2024dtaci; @angelopoulos2023pid] | single series | – | ✓ | ✓ (long-run) | per series | – |
| Bayesian online conformal [@zhang2024bayes] | single series | prior (not learned from other units) | ✓ | ✓ | per series | – |
| TQA [@lin2022tqa] | panels of series | pooled scores | ✓ | – | per series (longitudinal) | – |
| Hierarchical CP [@dunn2023; @lee2023hier], GHCP [@mallick2026] | groups | ✓ | first observations (GHCP) | – | marginal over groups | ✓ |
| Few-shot CP [@fisch2021] | tasks | ✓ (auxiliary tasks) | few labels | – | per task (marginal) | ✓ |
| Credibility shrinkage [@shahid2026; @rafe2026] | sites, subgroups | ✓ | ✓ | – | per site / subgroup | – |
| Decaying cold-start prior [@fang2026] | spatio-temporal | ✓ | ✓ | – | n/s | ✓ |
| Donor–local mixture [@jeon2026] | solar stations | ✓ | ✓ | – | n/s | ✓ |
| Online conformal for load [@shi2026; @suresh2025] | loads | – | ✓ | ✓ | n/s | – |
| Cross-building conformal [@hao2026], BuildingsBench [@emami2023] | buildings | pooled / pretrained | – | – | pooled | ✓ |
| **This study (TTSC)** | **1,358 buildings and clients** | **✓ (learned, LOBO-tuned)** | **✓ (recency-weighted)** | **✓ (7-day window = settlement period)** | **per building, per week, vs oracle reference** | **✓ (from day 1)** |
