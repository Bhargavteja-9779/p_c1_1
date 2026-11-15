# Journal comparison (≈90 journals screened)

## A. Measured by us from PubMed article-level "received"/"accepted" dates (2025-01 → 2026-10)
Script: `journal_selection/pubmed_acceptance_times.py`; raw: `journal_selection/pubmed_acceptance_times.tsv`.
These are article-level medians (individual articles with both dates), i.e. directly verified.

| Journal | Publisher | n articles | Median days (IQR) | Within 100 d? |
|---|---|---|---|---|
| Comput Struct Biotechnol J | Elsevier | 398 | 89 (62–117) | yes (median) |
| Int J Med Inform | Elsevier | 400 | 90.5 (59–149) | yes (median) |
| J Am Med Inform Assoc | OUP | 367 | 127 (96–166) | no |
| Physiol Meas | IOP | 270 | 127 (101–168) | no |
| Brief Bioinform | OUP | 398 | 129 (93–172) | no |
| Comput Biol Med | Elsevier | 388 | 130 (79–205) | no |
| J Neural Eng | IOP | 392 | 140.5 | no |
| J Biomed Inform | Elsevier | 329 | 145 | no |
| Neuroimage | Elsevier | 398 | 146.5 | no |
| Comput Med Imaging Graph | Elsevier | 352 | 149.5 | no |
| Bioinformatics | OUP | 338 | 152 (112–203) | no |
| NAR Genom Bioinform | OUP | 342 | 155.5 | no |
| Brief Funct Genomics | OUP | 51 | 155 | no |
| Patterns | Cell Press | 137 | 166 | no |
| Database (Oxford) | OUP | 158 | 167.5 | no |
| Med Biol Eng Comput | Springer | 400 | 178.5 | no |
| Gigascience | OUP | 274 | 179 | no |
| Comput Methods Programs Biomed | Elsevier | 400 | 183 | no |
| NPJ Digit Med | Springer Nature | 400 | 191 | no |
| Neural Netw | Elsevier | 400 | 220 | no |
| Med Image Anal | Elsevier | 399 | 231 | no |
| Artif Intell Med | Elsevier | 346 | 277.5 | no |
| IEEE JBHI / TNNLS / TBME / TMI / TPAMI | IEEE | — | dates not deposited | UNVERIFIED |

Conclusion: no Oxford/Cambridge/IEEE ML or informatics journal had verifiable acceptance ≤100 days.

## B. Publisher-reported (Elsevier Journal Insights "Submission to acceptance"), energy/engineering/AI
| Journal | Days | JIF (as displayed) | Fit for applied-ML energy topic |
|---|---|---|---|
| Results in Engineering | 74–76 | ~7 (unverified) | broad; weaker prestige |
| Energy Conversion & Management: X | 78 | 7.6 | moderate |
| **Advances in Applied Energy** | **86** | **13.8 (2024) / 18.3 (2025, aggregator)** | **strong** |
| Developments in the Built Environment | 89 | — | moderate |
| Energy and AI | 95 | 9.6 | strong (fallback) |
| Energy and Built Environment | 106 | — | >100 |
| Building and Environment | 110 | — | >100 |
| Energy and Buildings | 111 | 7.1 | >100 |
| Energy Reports | 113 | — | >100 |
| Applied Energy | 127–130 | 11.0 | >100 |
| Expert Systems with Applications | 147 | — | >100 |
| Energy | 149 | 9.4 | >100 |
| Knowledge-Based Systems | 155 | — | >100 |
| Sustainable Cities and Society | 139 | — | >100 |
| Engineering Applications of AI | 210 | — | >100 |
| Artificial Intelligence in Medicine | 265 | — | >100 |
| Pattern Recognition | 250 | — | >100 |
Fast (<72 d) Q1 journals found (J. Energy Chemistry 37 d, Separation & Purification Tech. 56 d, Nano Energy 66 d, etc.) were rejected for **scope mismatch** (chemistry/materials).

## Decision
Advances in Applied Energy: highest JIF among journals with publisher-reported acceptance ≤100 days **and** genuine scope fit.
