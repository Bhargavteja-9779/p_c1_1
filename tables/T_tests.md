**Paired Wilcoxon signed-rank tests (per building; Holm-adjusted)**

| dataset   | protocol   | proposed   | baseline        | metric   |   n_buildings |   mean_diff | CI95             |   median_diff |   share_proposed_better |   rank_biserial |   p_holm |
|:----------|:-----------|:-----------|:----------------|:---------|--------------:|------------:|:-----------------|--------------:|------------------------:|----------------:|---------:|
| BDG2      | random     | HSC-CQR    | CQR             | rel_IS   |           713 |    nan      | [nan, nan]       |      nan      |                  0.5736 |          0.4084 |   0      |
| BDG2      | random     | HSC-CQR    | CQR             | abs_dev  |           713 |     -0.0205 | [-0.024, -0.019] |       -0.0164 |                  0.8485 |          0.8758 |   0      |
| BDG2      | random     | HSC-CQR    | Self-CQR        | rel_IS   |           713 |    nan      | [nan, nan]       |      nan      |                  0.9187 |          0.9143 |   0      |
| BDG2      | random     | HSC-CQR    | Self-CQR        | abs_dev  |           713 |     -0.0035 | [-0.007, -0.001] |       -0.0022 |                  0.5638 |          0.2312 |   0      |
| BDG2      | random     | HSC-CQR    | ACI-CQR         | rel_IS   |           713 |    nan      | [nan, nan]       |      nan      |                  0.4839 |          0.1191 |   0      |
| BDG2      | random     | HSC-CQR    | ACI-CQR         | abs_dev  |           713 |     -0.0087 | [-0.011, -0.007] |       -0.0066 |                  0.7335 |          0.6495 |   0      |
| BDG2      | random     | HSC-CQR    | QR-LGBM         | rel_IS   |           713 |    nan      | [nan, nan]       |      nan      |                  0.6858 |          0.6488 |   0      |
| BDG2      | random     | HSC-CQR    | QR-LGBM         | abs_dev  |           713 |     -0.0321 | [-0.038, -0.024] |       -0.0272 |                  0.9102 |          0.9629 |   0      |
| BDG2      | random     | HSC-CQR    | MLP-QR          | rel_IS   |           713 |    nan      | [nan, nan]       |      nan      |                  0.6564 |          0.3707 |   0      |
| BDG2      | random     | HSC-CQR    | MLP-QR          | abs_dev  |           713 |     -0.021  | [-0.023, -0.020] |       -0.0169 |                  0.8373 |          0.842  |   0      |
| BDG2      | random     | HSC-CQR    | MLP-Gauss       | rel_IS   |           713 |    nan      | [nan, nan]       |      nan      |                  0.9215 |          0.9308 |   0      |
| BDG2      | random     | HSC-CQR    | MLP-Gauss       | abs_dev  |           713 |     -0.024  | [-0.033, -0.017] |       -0.0212 |                  0.7994 |          0.7824 |   0      |
| BDG2      | random     | HSC-CQR    | SCP-stage       | rel_IS   |           713 |    nan      | [nan, nan]       |      nan      |                  0.986  |          0.9988 |   0      |
| BDG2      | random     | HSC-CQR    | SCP-stage       | abs_dev  |           713 |     -0.0758 | [-0.084, -0.070] |       -0.0603 |                  0.9173 |          0.9701 |   0      |
| BDG2      | random     | HSC-CQR    | ACI             | rel_IS   |           713 |    nan      | [nan, nan]       |      nan      |                  0.979  |          0.997  |   0      |
| BDG2      | random     | HSC-CQR    | ACI             | abs_dev  |           713 |     -0.0414 | [-0.049, -0.036] |       -0.0394 |                  0.8836 |          0.9247 |   0      |
| BDG2      | random     | HSC-CQR    | Self-CP         | rel_IS   |           713 |    nan      | [nan, nan]       |      nan      |                  0.9719 |          0.9918 |   0      |
| BDG2      | random     | HSC-CQR    | Self-CP         | abs_dev  |           713 |     -0.0084 | [-0.010, -0.007] |       -0.007  |                  0.6985 |          0.5271 |   0      |
| BDG2      | random     | HSC-CQR    | Mondrian-usage  | rel_IS   |           713 |    nan      | [nan, nan]       |      nan      |                  0.9874 |          0.9989 |   0      |
| BDG2      | random     | HSC-CQR    | Mondrian-usage  | abs_dev  |           713 |     -0.0748 | [-0.086, -0.069] |       -0.0595 |                  0.9411 |          0.9793 |   0      |
| BDG2      | random     | HSC-CQR    | Naive+SCP       | rel_IS   |           713 |    nan      | [nan, nan]       |      nan      |                  0.9341 |          0.9952 |   0      |
| BDG2      | random     | HSC-CQR    | Naive+SCP       | abs_dev  |           713 |     -0.0755 | [-0.085, -0.064] |       -0.0622 |                  0.9411 |          0.9742 |   0      |
| BDG2      | random     | HSC-CQR    | HSC             | rel_IS   |           713 |    nan      | [nan, nan]       |      nan      |                  0.9593 |          0.987  |   0      |
| BDG2      | random     | HSC-CQR    | HSC             | abs_dev  |           713 |     -0.0112 | [-0.013, -0.009] |       -0.0095 |                  0.7504 |          0.649  |   0      |
| BDG2      | random     | HSC        | SCP             | rel_IS   |           713 |    nan      | [nan, nan]       |      nan      |                  0.8163 |          0.8443 |   0      |
| BDG2      | random     | HSC        | SCP             | abs_dev  |           713 |     -0.064  | [-0.074, -0.057] |       -0.0454 |                  0.8808 |          0.9204 |   0      |
| BDG2      | random     | HSC        | SCP-stage       | rel_IS   |           713 |    nan      | [nan, nan]       |      nan      |                  0.798  |          0.8249 |   0      |
| BDG2      | random     | HSC        | SCP-stage       | abs_dev  |           713 |     -0.0646 | [-0.075, -0.057] |       -0.0461 |                  0.885  |          0.9245 |   0      |
| BDG2      | random     | HSC        | Mondrian-usage  | rel_IS   |           713 |    nan      | [nan, nan]       |      nan      |                  0.8163 |          0.8524 |   0      |
| BDG2      | random     | HSC        | Mondrian-usage  | abs_dev  |           713 |     -0.0636 | [-0.076, -0.057] |       -0.0465 |                  0.892  |          0.9352 |   0      |
| BDG2      | random     | HSC        | Self-CP         | rel_IS   |           713 |    nan      | [nan, nan]       |      nan      |                  0.7069 |          0.5358 |   0      |
| BDG2      | random     | HSC        | Self-CP         | abs_dev  |           713 |      0.0028 | [0.002, 0.004]   |        0.0015 |                  0.4264 |         -0.1905 |   0      |
| BDG2      | random     | HSC        | ACI             | rel_IS   |           713 |    nan      | [nan, nan]       |      nan      |                  0.7181 |          0.666  |   0      |
| BDG2      | random     | HSC        | ACI             | abs_dev  |           713 |     -0.0302 | [-0.038, -0.025] |       -0.0297 |                  0.8149 |          0.8188 |   0      |
| BDG2      | random     | HSC        | Raw-SCP         | rel_IS   |           713 |    nan      | [nan, nan]       |      nan      |                  0.8962 |          0.9384 |   0      |
| BDG2      | random     | HSC        | Raw-SCP         | abs_dev  |           713 |     -0.0904 | [-0.112, -0.074] |       -0.063  |                  0.9411 |          0.9712 |   0      |
| BDG2      | random     | HSC        | HSC -stage      | rel_IS   |           713 |    nan      | [nan, nan]       |      nan      |                  0.561  |          0.236  |   0      |
| BDG2      | random     | HSC        | HSC -stage      | abs_dev  |           713 |      0.0005 | [0.000, 0.001]   |        0.0004 |                  0.4404 |         -0.1284 |   0.0109 |
| BDG2      | random     | HSC        | HSC -kNN        | rel_IS   |           713 |    nan      | [nan, nan]       |      nan      |                  0.6676 |          0.4198 |   0      |
| BDG2      | random     | HSC        | HSC -kNN        | abs_dev  |           713 |     -0.0007 | [-0.003, 0.001]  |       -0.0014 |                  0.547  |          0.099  |   0.0448 |
| BDG2      | random     | HSC        | HSC -shrink     | rel_IS   |           713 |    nan      | [nan, nan]       |      nan      |                  0.8303 |          0.8276 |   0      |
| BDG2      | random     | HSC        | HSC -shrink     | abs_dev  |           713 |     -0.0681 | [-0.082, -0.049] |       -0.0387 |                  0.9046 |          0.9417 |   0      |
| BDG2      | random     | HSC        | HSC fixed-kappa | rel_IS   |           713 |    nan      | [nan, nan]       |      nan      |                  0.1683 |         -0.0478 |   0      |
| BDG2      | random     | HSC        | HSC fixed-kappa | abs_dev  |           713 |     -0.0004 | [-0.000, -0.000] |        0      |                  0.2104 |          0.3646 |   0      |
| BDG2      | random     | HSC        | HSC -kNN -stage | rel_IS   |           713 |    nan      | [nan, nan]       |      nan      |                  0.6648 |          0.4312 |   0      |
| BDG2      | random     | HSC        | HSC -kNN -stage | abs_dev  |           713 |     -0.0003 | [-0.003, 0.002]  |       -0.0009 |                  0.5316 |          0.0595 |   0.1713 |
| BDG2      | random     | HSC-CQR    | HSC-CQR -stage  | rel_IS   |           713 |    nan      | [nan, nan]       |      nan      |                  0.4881 |         -0.0899 |   0      |
| BDG2      | random     | HSC-CQR    | HSC-CQR -stage  | abs_dev  |           713 |      0.0003 | [0.000, 0.000]   |        0.0004 |                  0.4208 |         -0.1354 |   0.0024 |
| BDG2      | random     | HSC-CQR    | HSC-CQR -kNN    | rel_IS   |           713 |    nan      | [nan, nan]       |      nan      |                  0.4656 |         -0.0092 |   0      |
| BDG2      | random     | HSC-CQR    | HSC-CQR -kNN    | abs_dev  |           713 |      0.0004 | [-0.000, 0.001]  |        0.0004 |                  0.3619 |         -0.1623 |   0.0008 |
| BDG2      | random     | HSC-CQR    | HSC-CQR -shrink | rel_IS   |           713 |    nan      | [nan, nan]       |      nan      |                  0.6171 |          0.4465 |   0      |
| BDG2      | random     | HSC-CQR    | HSC-CQR -shrink | abs_dev  |           713 |     -0.0191 | [-0.022, -0.016] |       -0.0154 |                  0.8822 |          0.9016 |   0      |
