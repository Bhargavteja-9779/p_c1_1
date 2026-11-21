| # | Deviation from the pre-registration | When | Target results seen? | Reason |
|:--|:--|:--|:--|:--|
| 1 | Stuck-meter rule (≥ 24 identical readings → missing); training filter y/s ≤ 20 | before full run | smoke test only (one seed, 15 % of rows) | flat-lined meters inflated errors ~80× |
| 2 | Common evaluation mask (hours with no issuable forecast excluded for all methods) | during first full run | no (bug found before use) | NaN interval scores |
| 3 | Same-score competitors (Self-CQR, ACI-CQR) and CQR-score ablations added | before full run | quick-mode check | fair test of the CQR variant |
| 4 | Primary method moved from SSC +stage+kNN (absolute score) to its CQR-score version | first submission | yes (seed-0 BDG2 look) | absolute-score variant lost on interval score to CQR |
| 5 | Prior-art baselines added (GHCP-CQR, QShrink-CQR, TQA-B-CQR), simple and fixed-κ variants, MLP check; ACI grid extended below 5e-4; mis-specified ablations replaced | first submission, after prior-art and code audits | yes (seed-0 BDG2 look) | closest prior art; grid edge hit in 7/10 runs |
| 6 | Target-year quality filter removed; no imputation; UCI DST hours masked | revision 1 | yes | look-ahead selection and imputation leakage found in review |
| 7 | Primary method = one-parameter layer (SSC-CQR) with κ by LOBO on MACD; all tuned competitors use the same objective; ACI level clipping; Self-CQR-fb, Mondrian-CQR, fixed-λ QShrink added; TQA-B and GHCP parameters tuned | revision 1 | yes | review: interval-score tuning traded reliability for sharpness; fair budgets |
| 8 | Cluster-aware primary inference (site sign-flip test), confirmatory family declared, per-window and per-site reporting | revision 1 | yes | review |
| 9 | Stress tests extended (weak-feature forecaster, outage block, early shift, input-only noise and spikes); former "weak forecaster" renamed "reduced training pool" | revision 1 | yes | review |
| 10 | α-sensitivity restricted to absolute-score methods (CQR family not retrained at α = 0.05, 0.2); claims limited to 90 % | revision 1 | – | compute |
