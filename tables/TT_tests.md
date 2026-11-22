**Paired per-building comparisons of TTSC (difference TTSC minus baseline; 95 % site-cluster (BDG2) or building (UCI) bootstrap CI; Wilcoxon signed-rank; Holm over the declared family)**

| dataset          | baseline                    | metric     | diff    | lo      | hi      | p       | better   | worse   | tost_3pct   | p_holm   |
|:-----------------|:----------------------------|:-----------|:--------|:--------|:--------|:--------|:---------|:--------|:------------|:---------|
| BDG2             | HSC-CQR recency (capped)    | wk_late    | -0.0631 | -0.0705 | -0.0588 | 1.2e-59 | 54       | 9       | nan         | 1.9e-58  |
| BDG2             | HSC-CQR recency (capped)    | any80      | -0.2393 | -0.2666 | -0.2079 | 3.9e-51 | 38       | 2       | nan         | 5e-50    |
| BDG2             | HSC-CQR recency (capped)    | breach_wk  | -0.0151 | -0.0219 | -0.0084 | 6.2e-09 | 29       | 16      | nan         | 3.7e-08  |
| BDG2             | HSC-CQR recency (capped)    | under      | -0.0012 | -0.0041 | +0.0000 | 0.94    | 0        | 0       | nan         | –        |
| BDG2             | HSC-CQR recency (capped)    | wk1        | -0.0345 | -0.0452 | -0.0216 | 0.0062  | 8        | 3       | nan         | –        |
| BDG2             | HSC-CQR recency (capped)    | log_rel_IS | +0.0254 | +0.0190 | +0.0289 | 6.9e-95 | 14       | 86      | True        | –        |
| BDG2             | QShrink-CQR (cov)           | wk_late    | -0.0733 | -0.0835 | -0.0674 | 2e-62   | 57       | 10      | nan         | 3.5e-61  |
| BDG2             | QShrink-CQR (cov)           | any80      | -0.2964 | -0.3256 | -0.2621 | 2.6e-62 | 45       | 2       | nan         | 4.4e-61  |
| BDG2             | QShrink-CQR (cov)           | breach_wk  | -0.0146 | -0.0229 | -0.0073 | 1.2e-07 | 31       | 18      | nan         | 5.9e-07  |
| BDG2             | QShrink-CQR (cov)           | under      | -0.0108 | -0.0209 | -0.0029 | 0.31    | 2        | 0       | nan         | –        |
| BDG2             | QShrink-CQR (cov)           | wk1        | -0.0304 | -0.0485 | -0.0067 | 0.012   | 10       | 5       | nan         | –        |
| BDG2             | QShrink-CQR (cov)           | log_rel_IS | +0.0212 | +0.0139 | +0.0252 | 5.1e-75 | 17       | 83      | True        | –        |
| BDG2             | ACI-CQR (cov)               | wk_late    | -0.0640 | -0.0752 | -0.0522 | 3.8e-48 | 52       | 12      | nan         | 4.5e-47  |
| BDG2             | ACI-CQR (cov)               | any80      | -0.2852 | -0.3260 | -0.2356 | 2.7e-58 | 43       | 2       | nan         | 3.7e-57  |
| BDG2             | ACI-CQR (cov)               | breach_wk  | -0.0196 | -0.0289 | -0.0104 | 1.4e-11 | 34       | 17      | nan         | 1.1e-10  |
| BDG2             | ACI-CQR (cov)               | under      | -0.0225 | -0.0385 | -0.0111 | 0.039   | 4        | 0       | nan         | –        |
| BDG2             | ACI-CQR (cov)               | wk1        | -0.0794 | -0.1151 | -0.0431 | 1.4e-08 | 17       | 5       | nan         | –        |
| BDG2             | ACI-CQR (cov)               | log_rel_IS | +0.0216 | +0.0137 | +0.0265 | 6.1e-76 | 17       | 83      | True        | –        |
| BDG2             | CQR                         | wk_late    | -0.1011 | -0.1345 | -0.0632 | 7.2e-42 | 54       | 19      | nan         | 8e-41    |
| BDG2             | CQR                         | any80      | -0.3121 | -0.3841 | -0.2287 | 1.3e-59 | 46       | 4       | nan         | 1.9e-58  |
| BDG2             | CQR                         | breach_wk  | -0.0338 | -0.0530 | -0.0123 | 1.4e-13 | 39       | 21      | nan         | 1.2e-12  |
| BDG2             | CQR                         | under      | -0.1519 | -0.2144 | -0.0878 | 3.2e-23 | 21       | 0       | nan         | –        |
| BDG2             | CQR                         | wk1        | -0.0886 | -0.1279 | -0.0478 | 2.9e-10 | 19       | 5       | nan         | –        |
| BDG2             | CQR                         | log_rel_IS | +0.0186 | +0.0114 | +0.0241 | 2.8e-39 | 27       | 73      | True        | –        |
| BDG2             | ACI (weekly-tuned)          | wk_late    | -0.0226 | -0.0325 | -0.0163 | 5.7e-14 | 35       | 16      | nan         | 5.7e-13  |
| BDG2             | ACI (weekly-tuned)          | any80      | -0.0816 | -0.1064 | -0.0685 | 8.4e-11 | 18       | 4       | nan         | 5.9e-10  |
| BDG2             | ACI (weekly-tuned)          | breach_wk  | -0.0041 | -0.0101 | +0.0028 | 0.084   | 20       | 16      | nan         | 0.34     |
| BDG2             | ACI (weekly-tuned)          | under      | -0.0008 | -0.0019 | +0.0000 | 0.89    | 0        | 0       | nan         | –        |
| BDG2             | ACI (weekly-tuned)          | wk1        | -0.0312 | -0.0480 | -0.0120 | 0.021   | 10       | 6       | nan         | –        |
| BDG2             | ACI (weekly-tuned)          | log_rel_IS | +0.0110 | +0.0082 | +0.0139 | 1e-30   | 32       | 68      | True        | –        |
| BDG2             | Windowed ACI (weekly-tuned) | wk_late    | -0.0075 | -0.0231 | +0.0079 | 0.57    | 27       | 27      | nan         | 0.81     |
| BDG2             | Windowed ACI (weekly-tuned) | any80      | -0.0110 | -0.0432 | +0.0217 | 0.41    | 10       | 8       | nan         | 0.81     |
| BDG2             | Windowed ACI (weekly-tuned) | breach_wk  | -0.0066 | -0.0151 | +0.0042 | 0.094   | 22       | 18      | nan         | 0.34     |
| BDG2             | Windowed ACI (weekly-tuned) | under      | -0.0174 | -0.0307 | -0.0086 | 0.081   | 3        | 0       | nan         | –        |
| BDG2             | Windowed ACI (weekly-tuned) | wk1        | -0.0295 | -0.0458 | -0.0131 | 0.033   | 10       | 6       | nan         | –        |
| BDG2             | Windowed ACI (weekly-tuned) | log_rel_IS | -0.0024 | -0.0045 | +0.0007 | 0.38    | 46       | 54      | True        | –        |
| BDG2 (seeds 2–4) | HSC-CQR recency (capped)    | wk_late    | -0.0630 | -0.0709 | -0.0586 | 3.3e-40 | 47       | 7       | nan         | 5.6e-39  |
| BDG2 (seeds 2–4) | HSC-CQR recency (capped)    | any80      | -0.2404 | -0.2720 | -0.2114 | 3.1e-30 | 32       | 2       | nan         | 4e-29    |
| BDG2 (seeds 2–4) | HSC-CQR recency (capped)    | breach_wk  | -0.0174 | -0.0252 | -0.0101 | 1.1e-07 | 26       | 12      | nan         | 9.6e-07  |
| BDG2 (seeds 2–4) | HSC-CQR recency (capped)    | under      | -0.0015 | -0.0053 | +0.0000 | 0.94    | 0        | 0       | nan         | –        |
| BDG2 (seeds 2–4) | HSC-CQR recency (capped)    | wk1        | -0.0550 | -0.0664 | -0.0391 | 0.00089 | 9        | 2       | nan         | –        |
| BDG2 (seeds 2–4) | HSC-CQR recency (capped)    | log_rel_IS | +0.0254 | +0.0177 | +0.0298 | 3.8e-69 | 14       | 86      | False       | –        |
| BDG2 (seeds 2–4) | QShrink-CQR (cov)           | wk_late    | -0.0756 | -0.0875 | -0.0696 | 8.9e-42 | 52       | 9       | nan         | 1.6e-40  |
| BDG2 (seeds 2–4) | QShrink-CQR (cov)           | any80      | -0.2926 | -0.3287 | -0.2568 | 2.3e-38 | 38       | 2       | nan         | 3.6e-37  |
| BDG2 (seeds 2–4) | QShrink-CQR (cov)           | breach_wk  | -0.0177 | -0.0271 | -0.0100 | 2.4e-07 | 28       | 14      | nan         | 1.7e-06  |
| BDG2 (seeds 2–4) | QShrink-CQR (cov)           | under      | -0.0136 | -0.0241 | -0.0031 | 0.36    | 2        | 0       | nan         | –        |
| BDG2 (seeds 2–4) | QShrink-CQR (cov)           | wk1        | -0.0430 | -0.0636 | -0.0180 | 0.0054  | 9        | 3       | nan         | –        |
| BDG2 (seeds 2–4) | QShrink-CQR (cov)           | log_rel_IS | +0.0201 | +0.0116 | +0.0244 | 1.9e-51 | 18       | 82      | True        | –        |
| BDG2 (seeds 2–4) | ACI-CQR (cov)               | wk_late    | -0.0540 | -0.0658 | -0.0458 | 4.9e-26 | 44       | 12      | nan         | 5.4e-25  |
| BDG2 (seeds 2–4) | ACI-CQR (cov)               | any80      | -0.2547 | -0.2961 | -0.1998 | 8.5e-32 | 34       | 3       | nan         | 1.2e-30  |
| BDG2 (seeds 2–4) | ACI-CQR (cov)               | breach_wk  | -0.0185 | -0.0273 | -0.0100 | 1.6e-07 | 28       | 14      | nan         | 1.3e-06  |
| BDG2 (seeds 2–4) | ACI-CQR (cov)               | under      | -0.0166 | -0.0342 | -0.0040 | 0.22    | 3        | 0       | nan         | –        |
| BDG2 (seeds 2–4) | ACI-CQR (cov)               | wk1        | -0.0927 | -0.1272 | -0.0491 | 1.5e-07 | 15       | 3       | nan         | –        |
| BDG2 (seeds 2–4) | ACI-CQR (cov)               | log_rel_IS | +0.0182 | +0.0088 | +0.0242 | 1.4e-50 | 20       | 80      | True        | –        |
| BDG2 (seeds 2–4) | CQR                         | wk_late    | -0.0968 | -0.1236 | -0.0639 | 9.6e-28 | 50       | 17      | nan         | 1.2e-26  |
| BDG2 (seeds 2–4) | CQR                         | any80      | -0.2824 | -0.3581 | -0.1863 | 2.1e-34 | 38       | 4       | nan         | 3.2e-33  |
| BDG2 (seeds 2–4) | CQR                         | breach_wk  | -0.0348 | -0.0532 | -0.0144 | 5.4e-11 | 36       | 19      | nan         | 5.4e-10  |
| BDG2 (seeds 2–4) | CQR                         | under      | -0.1500 | -0.2196 | -0.0838 | 1.1e-14 | 18       | 0       | nan         | –        |
| BDG2 (seeds 2–4) | CQR                         | wk1        | -0.1078 | -0.1496 | -0.0574 | 3.5e-09 | 17       | 3       | nan         | –        |
| BDG2 (seeds 2–4) | CQR                         | log_rel_IS | +0.0168 | +0.0076 | +0.0245 | 5.2e-23 | 30       | 70      | True        | –        |
| BDG2 (seeds 2–4) | ACI (weekly-tuned)          | wk_late    | -0.0185 | -0.0301 | -0.0105 | 2.5e-07 | 29       | 15      | nan         | 1.7e-06  |
| BDG2 (seeds 2–4) | ACI (weekly-tuned)          | any80      | -0.0707 | -0.0958 | -0.0555 | 2.7e-05 | 14       | 4       | nan         | 0.00014  |
| BDG2 (seeds 2–4) | ACI (weekly-tuned)          | breach_wk  | -0.0017 | -0.0086 | +0.0064 | 0.5     | 16       | 14      | nan         | 1        |
| BDG2 (seeds 2–4) | ACI (weekly-tuned)          | under      | +0.0000 | +0.0000 | +0.0000 | 1       | 0        | 0       | nan         | –        |
| BDG2 (seeds 2–4) | ACI (weekly-tuned)          | wk1        | -0.0415 | -0.0622 | -0.0188 | 0.0097  | 9        | 3       | nan         | –        |
| BDG2 (seeds 2–4) | ACI (weekly-tuned)          | log_rel_IS | +0.0105 | +0.0072 | +0.0127 | 2.3e-18 | 35       | 65      | True        | –        |
| BDG2 (seeds 2–4) | Windowed ACI (weekly-tuned) | wk_late    | +0.0008 | -0.0159 | +0.0141 | 0.18    | 21       | 26      | nan         | 0.73     |
| BDG2 (seeds 2–4) | Windowed ACI (weekly-tuned) | any80      | +0.0156 | -0.0147 | +0.0464 | 0.48    | 7        | 9       | nan         | 1        |
| BDG2 (seeds 2–4) | Windowed ACI (weekly-tuned) | breach_wk  | -0.0043 | -0.0124 | +0.0063 | 0.35    | 17       | 15      | nan         | 1        |
| BDG2 (seeds 2–4) | Windowed ACI (weekly-tuned) | under      | -0.0166 | -0.0300 | -0.0064 | 0.25    | 2        | 0       | nan         | –        |
| BDG2 (seeds 2–4) | Windowed ACI (weekly-tuned) | wk1        | -0.0292 | -0.0483 | -0.0151 | 0.077   | 7        | 3       | nan         | –        |
| BDG2 (seeds 2–4) | Windowed ACI (weekly-tuned) | log_rel_IS | -0.0121 | -0.0159 | -0.0075 | 2.6e-08 | 58       | 42      | True        | –        |
| UCI              | HSC-CQR recency (capped)    | wk_late    | -0.0667 | -0.0787 | -0.0554 | 1.1e-23 | 57       | 6       | nan         | 1.8e-22  |
| UCI              | HSC-CQR recency (capped)    | any80      | -0.1741 | -0.2114 | -0.1373 | 2.3e-13 | 29       | 0       | nan         | 3e-12    |
| UCI              | HSC-CQR recency (capped)    | breach_wk  | -0.0140 | -0.0212 | -0.0072 | 0.0014  | 25       | 13      | nan         | 0.011    |
| UCI              | HSC-CQR recency (capped)    | under      | +0.0000 | +0.0000 | +0.0000 | 1       | 0        | 0       | nan         | –        |
| UCI              | HSC-CQR recency (capped)    | wk1        | -0.0012 | -0.0222 | +0.0207 | 0.82    | 4        | 3       | nan         | –        |
| UCI              | HSC-CQR recency (capped)    | log_rel_IS | +0.0280 | +0.0245 | +0.0323 | 7e-41   | 7        | 93      | False       | –        |
| UCI              | QShrink-CQR (cov)           | wk_late    | -0.0792 | -0.0940 | -0.0655 | 7e-24   | 58       | 7       | nan         | 1.3e-22  |
| UCI              | QShrink-CQR (cov)           | any80      | -0.1926 | -0.2364 | -0.1481 | 2.5e-13 | 32       | 2       | nan         | 3e-12    |
| UCI              | QShrink-CQR (cov)           | breach_wk  | -0.0143 | -0.0226 | -0.0060 | 0.00093 | 29       | 14      | nan         | 0.0084   |
| UCI              | QShrink-CQR (cov)           | under      | +0.0000 | -0.0037 | +0.0037 | 1       | 0        | 0       | nan         | –        |
| UCI              | QShrink-CQR (cov)           | wk1        | +0.0022 | -0.0231 | +0.0281 | 0.76    | 6        | 4       | nan         | –        |
| UCI              | QShrink-CQR (cov)           | log_rel_IS | +0.0273 | +0.0233 | +0.0322 | 1.7e-33 | 12       | 88      | False       | –        |
| UCI              | ACI-CQR (cov)               | wk_late    | -0.0554 | -0.0685 | -0.0423 | 9.1e-16 | 48       | 10      | nan         | 1.3e-14  |
| UCI              | ACI-CQR (cov)               | any80      | -0.1673 | -0.2093 | -0.1225 | 2.7e-10 | 27       | 2       | nan         | 3e-09    |
| UCI              | ACI-CQR (cov)               | breach_wk  | -0.0162 | -0.0248 | -0.0078 | 0.0024  | 27       | 15      | nan         | 0.014    |
| UCI              | ACI-CQR (cov)               | under      | -0.0157 | -0.0302 | -0.0040 | 0.35    | 3        | 0       | nan         | –        |
| UCI              | ACI-CQR (cov)               | wk1        | -0.0701 | -0.1117 | -0.0299 | 0.0062  | 15       | 5       | nan         | –        |
| UCI              | ACI-CQR (cov)               | log_rel_IS | +0.0252 | +0.0196 | +0.0312 | 4.5e-26 | 14       | 86      | False       | –        |
| UCI              | CQR                         | wk_late    | -0.1163 | -0.1406 | -0.0942 | 9e-21   | 53       | 9       | nan         | 1.4e-19  |
| UCI              | CQR                         | any80      | -0.2682 | -0.3164 | -0.2188 | 3.4e-18 | 38       | 1       | nan         | 5.1e-17  |
| UCI              | CQR                         | breach_wk  | -0.0304 | -0.0450 | -0.0172 | 0.00079 | 31       | 18      | nan         | 0.0079   |
| UCI              | CQR                         | under      | -0.1216 | -0.1586 | -0.0864 | 9.7e-06 | 16       | 0       | nan         | –        |
| UCI              | CQR                         | wk1        | -0.0775 | -0.1216 | -0.0370 | 0.0028  | 16       | 5       | nan         | –        |
| UCI              | CQR                         | log_rel_IS | +0.0253 | +0.0207 | +0.0306 | 1.2e-24 | 19       | 81      | False       | –        |
| UCI              | ACI (weekly-tuned)          | wk_late    | -0.0139 | -0.0230 | -0.0050 | 0.0019  | 28       | 14      | nan         | 0.013    |
| UCI              | ACI (weekly-tuned)          | any80      | -0.0327 | -0.0525 | -0.0160 | 0.087   | 6        | 1       | nan         | 0.35     |
| UCI              | ACI (weekly-tuned)          | breach_wk  | -0.0075 | -0.0140 | -0.0012 | 0.039   | 21       | 13      | nan         | 0.19     |
| UCI              | ACI (weekly-tuned)          | under      | +0.0000 | +0.0000 | +0.0000 | 1       | 0        | 0       | nan         | –        |
| UCI              | ACI (weekly-tuned)          | wk1        | +0.0111 | -0.0157 | +0.0395 | 0.81    | 4        | 5       | nan         | –        |
| UCI              | ACI (weekly-tuned)          | log_rel_IS | +0.0064 | +0.0029 | +0.0102 | 0.00039 | 40       | 60      | True        | –        |
| UCI              | Windowed ACI (weekly-tuned) | wk_late    | -0.0097 | -0.0206 | +0.0005 | 0.37    | 21       | 18      | nan         | 0.93     |
| UCI              | Windowed ACI (weekly-tuned) | any80      | -0.0250 | -0.0516 | +0.0003 | 0.31    | 6        | 3       | nan         | 0.93     |
| UCI              | Windowed ACI (weekly-tuned) | breach_wk  | -0.0050 | -0.0131 | +0.0024 | 0.84    | 18       | 19      | nan         | 0.93     |
| UCI              | Windowed ACI (weekly-tuned) | under      | -0.0222 | -0.0407 | -0.0074 | 0.41    | 3        | 0       | nan         | –        |
| UCI              | Windowed ACI (weekly-tuned) | wk1        | +0.0065 | -0.0216 | +0.0377 | 0.99    | 6        | 6       | nan         | –        |
| UCI              | Windowed ACI (weekly-tuned) | log_rel_IS | +0.0037 | -0.0004 | +0.0077 | 1e-06   | 37       | 63      | True        | –        |
| UCI (seeds 2–4)  | HSC-CQR recency (capped)    | wk_late    | -0.0676 | -0.0814 | -0.0547 | 7e-17   | 49       | 5       | nan         | 1.1e-15  |
| UCI (seeds 2–4)  | HSC-CQR recency (capped)    | any80      | -0.1815 | -0.2274 | -0.1340 | 1.5e-08 | 25       | 0       | nan         | 1.8e-07  |
| UCI (seeds 2–4)  | HSC-CQR recency (capped)    | breach_wk  | -0.0173 | -0.0268 | -0.0078 | 0.0042  | 24       | 11      | nan         | 0.025    |
| UCI (seeds 2–4)  | HSC-CQR recency (capped)    | under      | +0.0000 | +0.0000 | +0.0000 | 1       | 0        | 0       | nan         | –        |
| UCI (seeds 2–4)  | HSC-CQR recency (capped)    | wk1        | -0.0023 | -0.0280 | +0.0234 | 0.9     | 3        | 3       | nan         | –        |
| UCI (seeds 2–4)  | HSC-CQR recency (capped)    | log_rel_IS | +0.0210 | +0.0180 | +0.0241 | 9.5e-31 | 9        | 91      | True        | –        |
| UCI (seeds 2–4)  | QShrink-CQR (cov)           | wk_late    | -0.0803 | -0.0970 | -0.0634 | 5.7e-17 | 52       | 6       | nan         | 9.7e-16  |
| UCI (seeds 2–4)  | QShrink-CQR (cov)           | any80      | -0.2165 | -0.2718 | -0.1604 | 1.5e-09 | 29       | 2       | nan         | 1.9e-08  |
| UCI (seeds 2–4)  | QShrink-CQR (cov)           | breach_wk  | -0.0199 | -0.0308 | -0.0091 | 0.0031  | 28       | 14      | nan         | 0.022    |
| UCI (seeds 2–4)  | QShrink-CQR (cov)           | under      | +0.0000 | -0.0140 | +0.0140 | 1       | 0        | 0       | nan         | –        |
| UCI (seeds 2–4)  | QShrink-CQR (cov)           | wk1        | -0.0140 | -0.0444 | +0.0164 | 0.7     | 5        | 3       | nan         | –        |
| UCI (seeds 2–4)  | QShrink-CQR (cov)           | log_rel_IS | +0.0196 | +0.0160 | +0.0233 | 3.5e-24 | 15       | 85      | True        | –        |
| UCI (seeds 2–4)  | ACI-CQR (cov)               | wk_late    | -0.0579 | -0.0745 | -0.0413 | 9.4e-11 | 43       | 10      | nan         | 1.3e-09  |
| UCI (seeds 2–4)  | ACI-CQR (cov)               | any80      | -0.1565 | -0.2056 | -0.1098 | 2e-06   | 21       | 1       | nan         | 2.2e-05  |
| UCI (seeds 2–4)  | ACI-CQR (cov)               | breach_wk  | -0.0207 | -0.0305 | -0.0109 | 0.00077 | 27       | 12      | nan         | 0.0069   |
| UCI (seeds 2–4)  | ACI-CQR (cov)               | under      | -0.0109 | -0.0273 | +0.0047 | 0.51    | 3        | 0       | nan         | –        |
| UCI (seeds 2–4)  | ACI-CQR (cov)               | wk1        | -0.0740 | -0.1207 | -0.0296 | 0.025   | 12       | 3       | nan         | –        |
| UCI (seeds 2–4)  | ACI-CQR (cov)               | log_rel_IS | +0.0140 | +0.0078 | +0.0197 | 4.2e-15 | 18       | 82      | True        | –        |
| UCI (seeds 2–4)  | CQR                         | wk_late    | -0.1346 | -0.1597 | -0.1098 | 5.5e-18 | 52       | 7       | nan         | 1e-16    |
| UCI (seeds 2–4)  | CQR                         | any80      | -0.2936 | -0.3497 | -0.2367 | 8.8e-14 | 35       | 0       | nan         | 1.3e-12  |
| UCI (seeds 2–4)  | CQR                         | breach_wk  | -0.0362 | -0.0518 | -0.0213 | 0.00036 | 30       | 14      | nan         | 0.0036   |
| UCI (seeds 2–4)  | CQR                         | under      | -0.1340 | -0.1776 | -0.0927 | 9.3e-05 | 15       | 0       | nan         | –        |
| UCI (seeds 2–4)  | CQR                         | wk1        | -0.0833 | -0.1324 | -0.0389 | 0.01    | 14       | 3       | nan         | –        |
| UCI (seeds 2–4)  | CQR                         | log_rel_IS | +0.0151 | +0.0106 | +0.0199 | 6.2e-12 | 26       | 74      | True        | –        |
| UCI (seeds 2–4)  | ACI (weekly-tuned)          | wk_late    | -0.0181 | -0.0284 | -0.0083 | 0.0015  | 25       | 10      | nan         | 0.012    |
| UCI (seeds 2–4)  | ACI (weekly-tuned)          | any80      | -0.0460 | -0.0748 | -0.0179 | 0.12    | 6        | 0       | nan         | 0.37     |
| UCI (seeds 2–4)  | ACI (weekly-tuned)          | breach_wk  | -0.0106 | -0.0192 | -0.0017 | 0.069   | 21       | 13      | nan         | 0.28     |
| UCI (seeds 2–4)  | ACI (weekly-tuned)          | under      | +0.0000 | +0.0000 | +0.0000 | 1       | 0        | 0       | nan         | –        |
| UCI (seeds 2–4)  | ACI (weekly-tuned)          | wk1        | -0.0109 | -0.0491 | +0.0234 | 0.71    | 6        | 4       | nan         | –        |
| UCI (seeds 2–4)  | ACI (weekly-tuned)          | log_rel_IS | +0.0029 | -0.0001 | +0.0058 | 0.0016  | 38       | 62      | True        | –        |
| UCI (seeds 2–4)  | Windowed ACI (weekly-tuned) | wk_late    | -0.0174 | -0.0296 | -0.0053 | 0.052   | 21       | 12      | nan         | 0.26     |
| UCI (seeds 2–4)  | Windowed ACI (weekly-tuned) | any80      | -0.0257 | -0.0538 | +0.0047 | 0.37    | 5        | 2       | nan         | 0.54     |
| UCI (seeds 2–4)  | Windowed ACI (weekly-tuned) | breach_wk  | -0.0104 | -0.0206 | -0.0009 | 0.27    | 18       | 14      | nan         | 0.54     |
| UCI (seeds 2–4)  | Windowed ACI (weekly-tuned) | under      | -0.0210 | -0.0397 | -0.0047 | 0.51    | 2        | 0       | nan         | –        |
| UCI (seeds 2–4)  | Windowed ACI (weekly-tuned) | wk1        | -0.0062 | -0.0429 | +0.0280 | 0.81    | 5        | 4       | nan         | –        |
| UCI (seeds 2–4)  | Windowed ACI (weekly-tuned) | log_rel_IS | +0.0032 | +0.0000 | +0.0061 | 0.00015 | 37       | 63      | True        | –        |
