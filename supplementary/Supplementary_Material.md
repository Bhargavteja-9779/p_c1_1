---
title: "Supplementary material: Trustworthy day-ahead load intervals for newly metered buildings via recency-weighted shrinkage conformal calibration"
---
# S1. Input features of the global forecasters

**Table S1. Input features (identical for LightGBM and MLP models).**

| Group | Features (computed only from the building's own h days of history, divided by the scale s) |
|:--|:--|
| Calendar | hour of day, day of week, weekend flag, month |
| History length | min(h, 28) |
| Lagged load | same hour 1, 2, 7 and 14 days earlier (missing if h is too short) |
| Previous day | mean, maximum and minimum of the previous day's normalised load |
| Profiles | hour-of-day mean over ≤ 28 days; same day-type (weekday/weekend) hour mean; same day-of-week hour mean (≤ 4 weeks, h ≥ 7) |
| Variability | mean absolute day-to-day change of the normalised hourly profile |
| Weather (BDG2 only) | air temperature at the target hour; daily mean; difference to the mean of the scale window and to the previous day |
| Target | y / s (point model: squared error; quantile models: pinball loss at α/2 and 1 − α/2) |


# S2. Refinements examined: onboarding-stage matching and similarity-localised population distribution

*Stage matching.* Calibration scores are grouped into onboarding-stage bins $\{1\},\{2\},\{3\},\{4..6\},\{7..13\},\{14..27\},\{28..56\}$; a forecast at stage $h$ is calibrated with the scores of the bin containing $h$.

*Similarity-localised distribution.* From its most recent $\min(h,28)$ observed days, each building is summarised by a descriptor $\mathbf z_{b,h}$: its mean daily load profile divided by its mean load (24 values), the mean absolute day-to-day change of that normalised profile, and the logarithm of the mean load, computed in the same way for calibration buildings at the same stage. The population distribution is the average of the score distributions of the $K$ calibration buildings closest to $\mathbf z_{b,h}$ (Euclidean distance after standardisation; buildings without valid scores or descriptor are skipped). $K\in\{10,25,50,100,\text{all}\}$ and $\kappa$ were selected by leave-one-building-out with the interval-score objective (variant HSC-CQR).

# S3. Implementation details of all compared methods

All conformal-type methods share the same forecaster, scores and score grid; they differ only in how the radius is obtained.


All conformal-type methods share the same forecaster, scores, grid and stage bins; they differ only in how the radius $q_{b,h}$ is obtained.

* **Naive+SCP** (classical): seasonal-naive forecast (same hour one week earlier if $h\ge7$, else the previous day) with stage-matched split conformal intervals.
* **Raw-SCP**: split conformal prediction on unnormalised absolute residuals (kWh).
* **SCP**: split conformal on normalised absolute scores pooled over all stages .
* **SCP-stage**: as SCP, with stage-bin matching (the score-weighted analogue of HSC with $\kappa=\infty$, $K=$ all, whose prior weights buildings equally).
* **Mondrian-usage** (BDG2): SCP-stage computed separately per primary-usage class (classes with at least 10 calibration buildings), a group-conditional (Mondrian) variant .
* **Self-CP**: split conformal on the building's own past scores ($\kappa=0$), falling back to SCP-stage until enough own scores exist.
* **ACI** : adaptive conformal inference on top of the SCP-stage distribution, $\alpha_{h+1}=\alpha_h+\gamma\sum_j(\alpha-\mathrm{err}_{h,j})$, with $\gamma$ chosen by leave-one-building-out on calibration buildings from $\{0,10^{-4},2\!\times\!10^{-4},5\!\times\!10^{-4},10^{-3},2\!\times\!10^{-3},5\!\times\!10^{-3},10^{-2}\}$ (the three smallest values were added after a code audit showed that the pre-registered grid's lower edge was selected in most runs; $\gamma=0$ recovers the pooled method). When $\alpha_h$ leaves $[0,1]$, the radius is set to the largest observed calibration score ($\alpha_h\le 0$; a finite surrogate of the infinite interval of the original method, used in 0.02% of BDG2 and 0.14% of UCI building-days for ACI-CQR) or to the smallest observed score ($\alpha_h\ge1$, empty-set convention). In the first version of the code the radius for $\alpha_h\le0$ was the grid maximum ($500\,s$); this was changed after internal review.
* **QR-LGBM**: direct LightGBM quantile regression .
* **CQR** : QR-LGBM conformalised with stage-matched pooled CQR scores.
* **MLP-Gauss**: a global multilayer perceptron (256-256-128, ReLU) with a Gaussian output trained by negative log-likelihood, a deep probabilistic baseline in the spirit of DeepAR's likelihood training .
* **MLP-QR**: the same network trained with the pinball loss for the two quantiles .
* **Self-CQR** and **ACI-CQR**: self-only calibration and ACI applied to the CQR scores (same quantile models as CQR).
* **TQA-B-CQR** : temporal quantile adjustment ("budgeting" variant) on the CQR scores. The building's exponentially decayed mean own score (decay 0.8 per day, normalised by the weight sum, days before the forecast only) is ranked among the calibration buildings' decayed means at the same stage; the rank $r=|\{j:\bar e_j<\bar e_b\}|/(N+1)$ is mapped to the queried level $1-a$ with $a=\alpha-\lambda g^B(r)$, $g^B(r)=C(r-(1-\alpha))$ for $r<1-\alpha$ and $r-(1-\alpha)$ otherwise, $C=\alpha^2/(1-\alpha)^2$, $\lambda\le1$ chosen per stage so that $a\ge0.01$ for every *calibration* building (each ranked among the others; the first version used the target buildings, which made a building's interval depend on other new buildings and was corrected after internal review), and the quantile is taken over the pooled scores together with a point at $+\infty$, as in the original method; the paper's TQA-E variant is an ACI-type update and is represented by ACI-CQR.
* **GHCP-CQR**: the calibration step of generalised hierarchical conformal prediction , adapted to our setting: with $M$ calibration buildings, every calibration building receives total weight $1/(M+1)$ spread over its scores (pooled over all onboarding stages, since GHCP has no notion of stages), and the new building receives the same group share, spread over its observed own scores and a point mass at $+\infty$ for its not-yet-observed scores. Deviations from the original: the surrogate group size is the median number of scores per calibration building (≈1344 in all runs) instead of a randomly drawn donor, and no observations are set aside to fit a local predictor, because our global forecaster already conditions on the building's own history (omitting this step most likely favours GHCP-CQR). GHCP's finite-sample guarantee relies on within-group exchangeability, which hourly loads violate.
* **QShrink-CQR** (regularised Mondrian ): quantile-level shrinkage $q=w\,q^{\mathrm{own}}+(1-w)\,q^{\mathrm{pool}}$ with $w=n_{b,h}/(n_{b,h}+\lambda)$, $q^{\mathrm{own}}$ the split-conformal quantile of the own scores (w = 0 while undefined) and $q^{\mathrm{pool}}$ the CQR radius; $\lambda$ is selected by leave-one-building-out from the same grid as $\kappa$, including $\lambda=0$ (own quantile whenever it exists) and $\lambda=\infty$ (pooled CQR radius).
* **HSC** and **HSC-CQR**: Eq. ([-@eq:hsc]) with all three elements (stage matching, similarity prior, shrinkage) applied to absolute and CQR scores; **HSC simple** and **HSC-CQR simple**: the same with a uniform prior ($K$ = all) and without stage matching, i.e. a single pseudo-count shrinkage towards the pooled score distribution; **HSC-CQR fixed-κ**: HSC-CQR simple with the pseudo-count fixed at one week of hourly scores ($\kappa=168$) instead of being selected — a donor–local mixture with fixed pseudo-count as in .
* **CQR (MLP)** and **HSC-CQR (MLP)**: CQR and HSC-CQR simple on the quantiles of the MLP quantile model, to check that the calibration layer is not specific to LightGBM.

The neural networks use the same features (missing values set to zero with missingness indicators, standardised), Adam (learning rate $10^{-3}$, batch 4096), at most 12 epochs, and early stopping on the validation buildings (patience 3). LightGBM uses 63 leaves, learning rate 0.05, at least 200 samples per leaf, 0.8 feature and bagging fractions, L2 regularisation 1, and early stopping (50 rounds) on the validation buildings. These are conventional settings, applied identically to point and quantile models. No method was tuned on target buildings.

 and statistical analysis


# S4. Protocol and deviations

1. The ACI step-size grid was extended to $\{0, 10^{-4}, 2\cdot10^{-4}\}$ after a code audit showed that the lower edge of the original grid was selected in most runs.
2. Mis-specified ablations of the first version were removed and replaced by the fixed-κ variant.
3. After the first internal review round, Addendum A (written and committed before the corresponding experiments) added the coverage objective for HSC, QShrink and ACI, recency weighting (ρ = 0.95), stage-wise studentisation, the operational outcomes, the noise reference, site-level tests and the rule for the recommended configuration (Addendum A.1). It also fixed the TQA-B budget scaling and the ACI convention for α_h ≤ 0 (Section S3).
4. At nominal 95 % and 80 %, all CQR-based methods use the quantile models trained for α = 0.1; the conformal step corrects the level. Uncalibrated quantile models (QR-LGBM, MLP-QR) are not reported at these levels.
5. The original protocol selected the HSC pseudo-count by the interval score; this variant is reported (HSC-CQR, HSC-CQR simple).

The complete protocol, including the addenda, is reproduced at the end of this document.

# S5. Additional results

**Table S2. All methods, BDG2, random-building protocol, nominal 90 % (mean ± s.d. over 5 seeds; widths and interval scores are medians over buildings).**

| Method               | Coverage      | Coverage (week 1)   | MACD          | Under-covered share   | P10 coverage   | Rel. width (median)   | Rel. IS (median)   |
|:---------------------|:--------------|:--------------------|:--------------|:----------------------|:---------------|:----------------------|:-------------------|
| HSC-CQR recency      | 0.896 ± 0.001 | 0.897 ± 0.003       | 0.011 ± 0.000 | 0.004 ± 0.003         | 0.878 ± 0.001  | 0.400 ± 0.018         | 0.570 ± 0.020      |
| HSC-SSC-CQR          | 0.898 ± 0.001 | 0.903 ± 0.004       | 0.014 ± 0.001 | 0.009 ± 0.009         | 0.876 ± 0.001  | 0.397 ± 0.017         | 0.571 ± 0.020      |
| SSC-CQR              | 0.899 ± 0.004 | 0.898 ± 0.007       | 0.029 ± 0.001 | 0.097 ± 0.010         | 0.852 ± 0.003  | 0.395 ± 0.015         | 0.565 ± 0.022      |
| HSC-CQR simple (cov) | 0.895 ± 0.001 | 0.897 ± 0.004       | 0.015 ± 0.001 | 0.019 ± 0.008         | 0.872 ± 0.001  | 0.393 ± 0.016         | 0.567 ± 0.022      |
| QShrink-CQR (cov)    | 0.896 ± 0.001 | 0.896 ± 0.004       | 0.015 ± 0.001 | 0.015 ± 0.008         | 0.873 ± 0.002  | 0.394 ± 0.016         | 0.567 ± 0.021      |
| ACI-CQR (cov)        | 0.900 ± 0.000 | 0.898 ± 0.003       | 0.004 ± 0.000 | 0.000 ± 0.000         | 0.894 ± 0.001  | 0.913 ± 0.161         | 1.110 ± 0.194      |
| HSC-CQR              | 0.891 ± 0.003 | 0.885 ± 0.007       | 0.018 ± 0.001 | 0.034 ± 0.008         | 0.864 ± 0.003  | 0.385 ± 0.011         | 0.564 ± 0.024      |
| HSC-CQR simple       | 0.895 ± 0.002 | 0.895 ± 0.004       | 0.017 ± 0.001 | 0.029 ± 0.007         | 0.869 ± 0.001  | 0.388 ± 0.013         | 0.563 ± 0.023      |
| HSC                  | 0.899 ± 0.003 | 0.880 ± 0.010       | 0.029 ± 0.002 | 0.092 ± 0.019         | 0.853 ± 0.005  | 0.413 ± 0.014         | 0.642 ± 0.024      |
| HSC simple           | 0.910 ± 0.001 | 0.906 ± 0.006       | 0.029 ± 0.002 | 0.055 ± 0.008         | 0.865 ± 0.002  | 0.437 ± 0.018         | 0.643 ± 0.021      |
| CQR                  | 0.891 ± 0.004 | 0.892 ± 0.006       | 0.038 ± 0.001 | 0.187 ± 0.018         | 0.831 ± 0.003  | 0.383 ± 0.014         | 0.564 ± 0.023      |
| Self-CQR             | 0.889 ± 0.002 | 0.864 ± 0.003       | 0.021 ± 0.001 | 0.061 ± 0.017         | 0.857 ± 0.003  | 0.395 ± 0.016         | 0.575 ± 0.018      |
| ACI-CQR              | 0.894 ± 0.003 | 0.892 ± 0.005       | 0.025 ± 0.003 | 0.080 ± 0.037         | 0.855 ± 0.008  | 0.385 ± 0.014         | 0.563 ± 0.025      |
| TQA-B-CQR            | 0.894 ± 0.003 | 0.894 ± 0.004       | 0.038 ± 0.001 | 0.170 ± 0.015         | 0.836 ± 0.002  | 0.384 ± 0.012         | 0.567 ± 0.023      |
| GHCP-CQR             | 0.894 ± 0.004 | 0.897 ± 0.004       | 0.038 ± 0.001 | 0.168 ± 0.010         | 0.834 ± 0.003  | 0.385 ± 0.014         | 0.565 ± 0.023      |
| QShrink-CQR          | 0.897 ± 0.002 | 0.895 ± 0.005       | 0.022 ± 0.004 | 0.041 ± 0.016         | 0.862 ± 0.003  | 0.390 ± 0.013         | 0.562 ± 0.024      |
| QR-LGBM              | 0.859 ± 0.009 | 0.865 ± 0.008       | 0.050 ± 0.006 | 0.403 ± 0.084         | 0.799 ± 0.008  | 0.357 ± 0.013         | 0.573 ± 0.025      |
| MLP-QR               | 0.885 ± 0.010 | 0.884 ± 0.016       | 0.039 ± 0.005 | 0.206 ± 0.062         | 0.826 ± 0.015  | 0.383 ± 0.024         | 0.571 ± 0.021      |
| MLP-Gauss            | 0.924 ± 0.009 | 0.934 ± 0.019       | 0.041 ± 0.002 | 0.056 ± 0.033         | 0.867 ± 0.013  | 0.451 ± 0.030         | 0.604 ± 0.036      |
| CQR (MLP)            | 0.895 ± 0.004 | 0.897 ± 0.007       | 0.037 ± 0.004 | 0.156 ± 0.019         | 0.838 ± 0.005  | 0.392 ± 0.016         | 0.568 ± 0.023      |
| HSC-CQR (MLP)        | 0.897 ± 0.003 | 0.897 ± 0.004       | 0.018 ± 0.001 | 0.025 ± 0.010         | 0.869 ± 0.002  | 0.398 ± 0.014         | 0.569 ± 0.022      |
| ACI                  | 0.914 ± 0.003 | 0.895 ± 0.011       | 0.044 ± 0.001 | 0.130 ± 0.010         | 0.846 ± 0.002  | 0.435 ± 0.020         | 0.634 ± 0.023      |
| Self-CP              | 0.904 ± 0.003 | 0.899 ± 0.004       | 0.026 ± 0.001 | 0.058 ± 0.009         | 0.862 ± 0.003  | 0.440 ± 0.018         | 0.656 ± 0.023      |
| SCP-stage            | 0.881 ± 0.009 | 0.888 ± 0.013       | 0.094 ± 0.005 | 0.290 ± 0.034         | 0.700 ± 0.020  | 0.461 ± 0.024         | 0.639 ± 0.022      |
| SCP                  | 0.881 ± 0.008 | 0.863 ± 0.012       | 0.093 ± 0.005 | 0.289 ± 0.036         | 0.701 ± 0.020  | 0.460 ± 0.024         | 0.640 ± 0.023      |
| Mondrian-usage       | 0.883 ± 0.011 | 0.887 ± 0.016       | 0.092 ± 0.004 | 0.285 ± 0.044         | 0.706 ± 0.011  | 0.435 ± 0.040         | 0.666 ± 0.031      |
| Naive+SCP            | 0.883 ± 0.011 | 0.891 ± 0.011       | 0.092 ± 0.006 | 0.304 ± 0.023         | 0.707 ± 0.032  | 0.691 ± 0.053         | 0.978 ± 0.044      |
| Raw-SCP              | 0.907 ± 0.024 | 0.895 ± 0.029       | 0.118 ± 0.014 | 0.188 ± 0.047         | 0.700 ± 0.113  | 0.769 ± 0.077         | 1.130 ± 0.034      |
| HSC -stage           | 0.898 ± 0.003 | 0.863 ± 0.010       | 0.028 ± 0.002 | 0.093 ± 0.025         | 0.853 ± 0.004  | 0.409 ± 0.014         | 0.646 ± 0.021      |
| HSC -kNN             | 0.911 ± 0.002 | 0.921 ± 0.004       | 0.029 ± 0.002 | 0.053 ± 0.009         | 0.867 ± 0.002  | 0.443 ± 0.019         | 0.642 ± 0.022      |
| HSC -shrink          | 0.841 ± 0.008 | 0.834 ± 0.016       | 0.093 ± 0.005 | 0.458 ± 0.034         | 0.689 ± 0.014  | 0.364 ± 0.009         | 0.662 ± 0.030      |
| HSC-CQR -stage       | 0.892 ± 0.002 | 0.889 ± 0.006       | 0.017 ± 0.001 | 0.032 ± 0.009         | 0.865 ± 0.002  | 0.384 ± 0.010         | 0.564 ± 0.024      |
| HSC-CQR -kNN         | 0.894 ± 0.002 | 0.895 ± 0.005       | 0.017 ± 0.001 | 0.031 ± 0.009         | 0.868 ± 0.001  | 0.389 ± 0.012         | 0.563 ± 0.024      |
| HSC-CQR -shrink      | 0.884 ± 0.004 | 0.879 ± 0.008       | 0.037 ± 0.001 | 0.217 ± 0.026         | 0.826 ± 0.002  | 0.377 ± 0.012         | 0.567 ± 0.023      |
| HSC-CQR fixed-κ      | 0.895 ± 0.002 | 0.897 ± 0.004       | 0.015 ± 0.001 | 0.019 ± 0.008         | 0.873 ± 0.001  | 0.392 ± 0.016         | 0.566 ± 0.022      |


**Table S3. All methods, UCI, random-building protocol, nominal 90 %.**

| Method               | Coverage      | Coverage (week 1)   | MACD          | Under-covered share   | P10 coverage   | Rel. width (median)   | Rel. IS (median)   |
|:---------------------|:--------------|:--------------------|:--------------|:----------------------|:---------------|:----------------------|:-------------------|
| HSC-CQR recency      | 0.901 ± 0.002 | 0.903 ± 0.002       | 0.010 ± 0.001 | 0.000 ± 0.000         | 0.886 ± 0.003  | 0.268 ± 0.011         | 0.369 ± 0.014      |
| HSC-SSC-CQR          | 0.903 ± 0.003 | 0.908 ± 0.002       | 0.013 ± 0.002 | 0.000 ± 0.000         | 0.884 ± 0.005  | 0.268 ± 0.014         | 0.368 ± 0.014      |
| SSC-CQR              | 0.914 ± 0.006 | 0.918 ± 0.008       | 0.027 ± 0.002 | 0.025 ± 0.018         | 0.877 ± 0.011  | 0.283 ± 0.019         | 0.369 ± 0.015      |
| HSC-CQR simple (cov) | 0.900 ± 0.002 | 0.904 ± 0.003       | 0.013 ± 0.002 | 0.002 ± 0.005         | 0.880 ± 0.005  | 0.268 ± 0.014         | 0.367 ± 0.015      |
| QShrink-CQR (cov)    | 0.901 ± 0.003 | 0.906 ± 0.005       | 0.013 ± 0.002 | 0.002 ± 0.005         | 0.882 ± 0.004  | 0.266 ± 0.015         | 0.368 ± 0.015      |
| ACI-CQR (cov)        | 0.901 ± 0.001 | 0.903 ± 0.004       | 0.004 ± 0.000 | 0.000 ± 0.000         | 0.895 ± 0.001  | 0.328 ± 0.026         | 0.431 ± 0.037      |
| HSC-CQR              | 0.898 ± 0.003 | 0.894 ± 0.007       | 0.014 ± 0.002 | 0.006 ± 0.009         | 0.878 ± 0.005  | 0.266 ± 0.012         | 0.368 ± 0.016      |
| HSC-CQR simple       | 0.901 ± 0.004 | 0.902 ± 0.006       | 0.014 ± 0.003 | 0.011 ± 0.015         | 0.879 ± 0.009  | 0.267 ± 0.013         | 0.366 ± 0.015      |
| HSC                  | 0.904 ± 0.003 | 0.891 ± 0.010       | 0.021 ± 0.001 | 0.042 ± 0.026         | 0.870 ± 0.003  | 0.286 ± 0.012         | 0.418 ± 0.018      |
| HSC simple           | 0.912 ± 0.004 | 0.917 ± 0.010       | 0.023 ± 0.002 | 0.019 ± 0.014         | 0.880 ± 0.004  | 0.299 ± 0.013         | 0.418 ± 0.014      |
| CQR                  | 0.899 ± 0.011 | 0.900 ± 0.010       | 0.033 ± 0.005 | 0.095 ± 0.043         | 0.856 ± 0.016  | 0.273 ± 0.019         | 0.368 ± 0.015      |
| Self-CQR             | 0.896 ± 0.002 | 0.880 ± 0.008       | 0.016 ± 0.002 | 0.013 ± 0.019         | 0.871 ± 0.002  | 0.263 ± 0.011         | 0.372 ± 0.014      |
| ACI-CQR              | 0.903 ± 0.005 | 0.902 ± 0.007       | 0.020 ± 0.006 | 0.036 ± 0.031         | 0.871 ± 0.011  | 0.271 ± 0.015         | 0.366 ± 0.015      |
| TQA-B-CQR            | 0.900 ± 0.007 | 0.902 ± 0.008       | 0.032 ± 0.006 | 0.091 ± 0.041         | 0.857 ± 0.014  | 0.272 ± 0.014         | 0.368 ± 0.013      |
| GHCP-CQR             | 0.906 ± 0.010 | 0.909 ± 0.011       | 0.034 ± 0.006 | 0.078 ± 0.036         | 0.864 ± 0.016  | 0.280 ± 0.019         | 0.369 ± 0.016      |
| QShrink-CQR          | 0.902 ± 0.005 | 0.905 ± 0.006       | 0.016 ± 0.004 | 0.017 ± 0.024         | 0.879 ± 0.011  | 0.267 ± 0.012         | 0.367 ± 0.015      |
| QR-LGBM              | 0.877 ± 0.009 | 0.879 ± 0.010       | 0.035 ± 0.006 | 0.181 ± 0.069         | 0.832 ± 0.017  | 0.257 ± 0.015         | 0.368 ± 0.014      |
| MLP-QR               | 0.889 ± 0.013 | 0.886 ± 0.018       | 0.034 ± 0.008 | 0.133 ± 0.086         | 0.849 ± 0.022  | 0.268 ± 0.012         | 0.379 ± 0.017      |
| MLP-Gauss            | 0.927 ± 0.005 | 0.927 ± 0.013       | 0.037 ± 0.002 | 0.025 ± 0.016         | 0.885 ± 0.011  | 0.299 ± 0.017         | 0.394 ± 0.017      |
| CQR (MLP)            | 0.899 ± 0.010 | 0.899 ± 0.011       | 0.033 ± 0.005 | 0.078 ± 0.038         | 0.860 ± 0.015  | 0.276 ± 0.012         | 0.377 ± 0.016      |
| HSC-CQR (MLP)        | 0.901 ± 0.006 | 0.896 ± 0.014       | 0.016 ± 0.004 | 0.021 ± 0.025         | 0.877 ± 0.010  | 0.274 ± 0.010         | 0.378 ± 0.016      |
| ACI                  | 0.920 ± 0.011 | 0.910 ± 0.018       | 0.047 ± 0.021 | 0.080 ± 0.070         | 0.848 ± 0.039  | 0.331 ± 0.032         | 0.423 ± 0.015      |
| Self-CP              | 0.908 ± 0.003 | 0.912 ± 0.003       | 0.021 ± 0.001 | 0.021 ± 0.018         | 0.878 ± 0.003  | 0.294 ± 0.012         | 0.420 ± 0.012      |
| SCP-stage            | 0.903 ± 0.015 | 0.904 ± 0.017       | 0.090 ± 0.006 | 0.202 ± 0.047         | 0.771 ± 0.025  | 0.377 ± 0.031         | 0.443 ± 0.018      |
| SCP                  | 0.904 ± 0.014 | 0.884 ± 0.018       | 0.090 ± 0.006 | 0.200 ± 0.045         | 0.771 ± 0.023  | 0.376 ± 0.031         | 0.444 ± 0.018      |
| Naive+SCP            | 0.905 ± 0.008 | 0.904 ± 0.008       | 0.075 ± 0.004 | 0.215 ± 0.036         | 0.762 ± 0.018  | 0.475 ± 0.028         | 0.583 ± 0.020      |
| Raw-SCP              | 0.908 ± 0.048 | 0.898 ± 0.050       | 0.130 ± 0.028 | 0.179 ± 0.098         | 0.681 ± 0.218  | 0.967 ± 0.321         | 1.137 ± 0.207      |
| HSC -stage           | 0.903 ± 0.004 | 0.880 ± 0.016       | 0.021 ± 0.001 | 0.044 ± 0.033         | 0.868 ± 0.004  | 0.282 ± 0.012         | 0.419 ± 0.016      |
| HSC -kNN             | 0.916 ± 0.006 | 0.926 ± 0.008       | 0.027 ± 0.005 | 0.029 ± 0.022         | 0.876 ± 0.004  | 0.308 ± 0.015         | 0.420 ± 0.014      |
| HSC -shrink          | 0.857 ± 0.007 | 0.846 ± 0.013       | 0.078 ± 0.004 | 0.314 ± 0.037         | 0.719 ± 0.011  | 0.254 ± 0.011         | 0.435 ± 0.030      |
| HSC-CQR -stage       | 0.899 ± 0.003 | 0.897 ± 0.004       | 0.014 ± 0.003 | 0.011 ± 0.015         | 0.877 ± 0.008  | 0.265 ± 0.012         | 0.366 ± 0.015      |
| HSC-CQR -kNN         | 0.901 ± 0.004 | 0.905 ± 0.006       | 0.014 ± 0.002 | 0.011 ± 0.015         | 0.880 ± 0.007  | 0.268 ± 0.012         | 0.366 ± 0.016      |
| HSC-CQR -shrink      | 0.891 ± 0.007 | 0.887 ± 0.009       | 0.031 ± 0.005 | 0.126 ± 0.040         | 0.847 ± 0.012  | 0.267 ± 0.017         | 0.369 ± 0.016      |
| HSC-CQR fixed-κ      | 0.901 ± 0.003 | 0.904 ± 0.004       | 0.013 ± 0.002 | 0.004 ± 0.006         | 0.882 ± 0.005  | 0.267 ± 0.014         | 0.366 ± 0.015      |


**Table S4. Paired per-building comparisons of HSC-CQR recency with the strongest alternatives.**

| Data   | Baseline             | Metric   |   n |   Mean diff. |   Better (%) |   r_rb | p (Holm)   | p (sites)   |
|:-------|:---------------------|:---------|----:|-------------:|-------------:|-------:|:-----------|:------------|
| BDG2   | CQR                  | CD       | 713 |      -0.0266 |           90 |   0.93 | <0.001     | 0.002       |
| BDG2   | CQR                  | CD wk 1  | 713 |      -0.0257 |           79 |   0.8  | <0.001     | 0.002       |
| BDG2   | CQR                  | IS       | 713 |       0.0195 |           46 |   0.02 | 1.000      | 0.846       |
| BDG2   | QShrink-CQR (cov)    | CD       | 713 |      -0.0037 |           77 |   0.68 | <0.001     | 0.002       |
| BDG2   | QShrink-CQR (cov)    | CD wk 1  | 713 |      -0.0078 |           62 |   0.52 | <0.001     | 0.002       |
| BDG2   | QShrink-CQR (cov)    | IS       | 713 |       0.01   |           32 |  -0.41 | <0.001     | 0.006       |
| BDG2   | ACI-CQR              | CD       | 713 |      -0.0132 |           81 |   0.8  | <0.001     | 0.002       |
| BDG2   | ACI-CQR              | CD wk 1  | 713 |      -0.0226 |           77 |   0.78 | <0.001     | 0.002       |
| BDG2   | ACI-CQR              | IS       | 713 |       0.0216 |           35 |  -0.33 | <0.001     | 0.160       |
| BDG2   | ACI-CQR (cov)        | CD       | 713 |       0.0071 |           11 |  -0.91 | <0.001     | 0.002       |
| BDG2   | ACI-CQR (cov)        | CD wk 1  | 713 |       0.0047 |           32 |  -0.38 | <0.001     | 0.002       |
| BDG2   | ACI-CQR (cov)        | IS       | 713 |      -0.8592 |           97 |   0.98 | <0.001     | 0.002       |
| BDG2   | Self-CQR             | CD       | 713 |      -0.0096 |           82 |   0.8  | <0.001     | 0.002       |
| BDG2   | Self-CQR             | CD wk 1  | 713 |      -0.0159 |           59 |   0.41 | <0.001     | 0.006       |
| BDG2   | Self-CQR             | IS       | 713 |      -0.0234 |           90 |   0.9  | <0.001     | 0.002       |
| BDG2   | HSC-CQR fixed-κ      | CD       | 713 |      -0.0035 |           77 |   0.73 | <0.001     | 0.002       |
| BDG2   | HSC-CQR fixed-κ      | CD wk 1  | 713 |      -0.0098 |           69 |   0.64 | <0.001     | 0.002       |
| BDG2   | HSC-CQR fixed-κ      | IS       | 713 |       0.0221 |           27 |  -0.54 | <0.001     | 0.002       |
| BDG2   | HSC-CQR simple (cov) | CD       | 713 |      -0.0035 |           78 |   0.74 | <0.001     | 0.002       |
| BDG2   | HSC-CQR simple (cov) | CD wk 1  | 713 |      -0.0089 |           66 |   0.62 | <0.001     | 0.002       |
| BDG2   | HSC-CQR simple (cov) | IS       | 713 |       0.0211 |           29 |  -0.51 | <0.001     | 0.002       |
| BDG2   | HSC-CQR              | CD       | 713 |      -0.0062 |           76 |   0.72 | <0.001     | 0.002       |
| BDG2   | HSC-CQR              | CD wk 1  | 713 |      -0.0156 |           72 |   0.68 | <0.001     | 0.002       |
| BDG2   | HSC-CQR              | IS       | 713 |       0.0285 |           27 |  -0.53 | <0.001     | 0.002       |
| BDG2   | HSC-SSC-CQR          | CD       | 713 |      -0.003  |           72 |   0.57 | <0.001     | 0.004       |
| BDG2   | HSC-SSC-CQR          | CD wk 1  | 713 |      -0.0041 |           55 |   0.41 | <0.001     | 0.002       |
| BDG2   | HSC-SSC-CQR          | IS       | 713 |      -1.487  |           45 |   0.01 | 1.000      | 0.014       |
| BDG2   | GHCP-CQR             | CD       | 713 |      -0.0263 |           90 |   0.93 | <0.001     | 0.002       |
| BDG2   | GHCP-CQR             | CD wk 1  | 713 |      -0.0255 |           80 |   0.81 | <0.001     | 0.002       |
| BDG2   | GHCP-CQR             | IS       | 713 |       0.0197 |           46 |   0.02 | 1.000      | 0.846       |
| BDG2   | TQA-B-CQR            | CD       | 713 |      -0.0268 |           90 |   0.93 | <0.001     | 0.002       |
| BDG2   | TQA-B-CQR            | CD wk 1  | 713 |      -0.0216 |           76 |   0.76 | <0.001     | 0.002       |
| BDG2   | TQA-B-CQR            | IS       | 713 |       0.0188 |           52 |   0.16 | <0.001     | 0.557       |
| UCI    | CQR                  | CD       | 270 |      -0.0234 |           86 |   0.9  | <0.001     | –           |
| UCI    | CQR                  | CD wk 1  | 270 |      -0.0261 |           76 |   0.77 | <0.001     | –           |
| UCI    | CQR                  | IS       | 270 |      -0.0022 |           47 |  -0.03 | 1.000      | –           |
| UCI    | QShrink-CQR (cov)    | CD       | 270 |      -0.0033 |           76 |   0.75 | <0.001     | –           |
| UCI    | QShrink-CQR (cov)    | CD wk 1  | 270 |      -0.0056 |           61 |   0.48 | <0.001     | –           |
| UCI    | QShrink-CQR (cov)    | IS       | 270 |       0.0027 |           33 |  -0.35 | <0.001     | –           |
| UCI    | ACI-CQR              | CD       | 270 |      -0.0102 |           74 |   0.7  | <0.001     | –           |
| UCI    | ACI-CQR              | CD wk 1  | 270 |      -0.0216 |           76 |   0.76 | <0.001     | –           |
| UCI    | ACI-CQR              | IS       | 270 |      -0.0032 |           35 |  -0.33 | <0.001     | –           |
| UCI    | ACI-CQR (cov)        | CD       | 270 |       0.0056 |           12 |  -0.87 | <0.001     | –           |
| UCI    | ACI-CQR (cov)        | CD wk 1  | 270 |       0.0012 |           36 |  -0.17 | 0.023      | –           |
| UCI    | ACI-CQR (cov)        | IS       | 270 |      -0.4375 |           93 |   0.94 | <0.001     | –           |
| UCI    | Self-CQR             | CD       | 270 |      -0.0066 |           77 |   0.78 | <0.001     | –           |
| UCI    | Self-CQR             | CD wk 1  | 270 |      -0.0132 |           63 |   0.48 | <0.001     | –           |
| UCI    | Self-CQR             | IS       | 270 |      -0.0096 |           90 |   0.92 | <0.001     | –           |
| UCI    | HSC-CQR fixed-κ      | CD       | 270 |      -0.0028 |           71 |   0.61 | <0.001     | –           |
| UCI    | HSC-CQR fixed-κ      | CD wk 1  | 270 |      -0.0099 |           67 |   0.59 | <0.001     | –           |
| UCI    | HSC-CQR fixed-κ      | IS       | 270 |       0.0055 |           21 |  -0.68 | <0.001     | –           |
| UCI    | HSC-CQR simple (cov) | CD       | 270 |      -0.0033 |           82 |   0.85 | <0.001     | –           |
| UCI    | HSC-CQR simple (cov) | CD wk 1  | 270 |      -0.0038 |           53 |   0.35 | <0.001     | –           |
| UCI    | HSC-CQR simple (cov) | IS       | 270 |       0.004  |           28 |  -0.51 | <0.001     | –           |
| UCI    | HSC-CQR              | CD       | 270 |      -0.0038 |           65 |   0.51 | <0.001     | –           |
| UCI    | HSC-CQR              | CD wk 1  | 270 |      -0.0126 |           67 |   0.53 | <0.001     | –           |
| UCI    | HSC-CQR              | IS       | 270 |       0.0059 |           20 |  -0.64 | <0.001     | –           |
| UCI    | HSC-SSC-CQR          | CD       | 270 |      -0.0032 |           76 |   0.68 | <0.001     | –           |
| UCI    | HSC-SSC-CQR          | CD wk 1  | 270 |      -0.0038 |           56 |   0.39 | <0.001     | –           |
| UCI    | HSC-SSC-CQR          | IS       | 270 |      -0.0483 |           36 |  -0.18 | 0.047      | –           |
| UCI    | GHCP-CQR             | CD       | 270 |      -0.0245 |           88 |   0.92 | <0.001     | –           |
| UCI    | GHCP-CQR             | CD wk 1  | 270 |      -0.0277 |           77 |   0.78 | <0.001     | –           |
| UCI    | GHCP-CQR             | IS       | 270 |      -0.0021 |           53 |   0.1  | 0.495      | –           |
| UCI    | TQA-B-CQR            | CD       | 270 |      -0.022  |           86 |   0.88 | <0.001     | –           |
| UCI    | TQA-B-CQR            | CD wk 1  | 270 |      -0.021  |           75 |   0.73 | <0.001     | –           |
| UCI    | TQA-B-CQR            | IS       | 270 |      -0.0006 |           47 |   0.03 | 1.000      | –           |


**Table S5. Site-level robustness of the paired comparisons of HSC-CQR recency on BDG2 (90 %). p (10 site means): Wilcoxon signed-rank test on the ten site means of the paired differences (smallest attainable two-sided p = 0.002); p (without largest site): building-level Wilcoxon test without site 'Rat'. CD = absolute coverage deviation over the window; CD wk 1 = the same for the first week; IS = relative interval score.**

| Baseline | Metric | Better (%) | p (buildings, Holm) | p (10 site means) | p (without largest site) |
|:--|:--|--:|--:|--:|--:|
| CQR | IS | 46 | 1.000 | 0.846 | 0.054 |
| CQR | CD | 90 | <0.001 | 0.002 | <0.001 |
| CQR | CD wk 1 | 79 | <0.001 | 0.002 | <0.001 |
| Self-CQR | IS | 90 | <0.001 | 0.002 | <0.001 |
| Self-CQR | CD | 82 | <0.001 | 0.002 | <0.001 |
| Self-CQR | CD wk 1 | 59 | <0.001 | 0.006 | <0.001 |
| ACI-CQR | IS | 35 | <0.001 | 0.160 | <0.001 |
| ACI-CQR | CD | 81 | <0.001 | 0.002 | <0.001 |
| ACI-CQR | CD wk 1 | 77 | <0.001 | 0.002 | <0.001 |
| ACI-CQR (cov) | IS | 97 | <0.001 | 0.002 | <0.001 |
| ACI-CQR (cov) | CD | 11 | <0.001 | 0.002 | <0.001 |
| ACI-CQR (cov) | CD wk 1 | 32 | <0.001 | 0.002 | <0.001 |
| TQA-B-CQR | IS | 52 | <0.001 | 0.557 | <0.001 |
| TQA-B-CQR | CD | 90 | <0.001 | 0.002 | <0.001 |
| TQA-B-CQR | CD wk 1 | 76 | <0.001 | 0.002 | <0.001 |
| GHCP-CQR | IS | 46 | 1.000 | 0.846 | 0.013 |
| GHCP-CQR | CD | 90 | <0.001 | 0.002 | <0.001 |
| GHCP-CQR | CD wk 1 | 80 | <0.001 | 0.002 | <0.001 |
| QShrink-CQR | IS | 32 | <0.001 | 0.002 | <0.001 |
| QShrink-CQR | CD | 81 | <0.001 | 0.002 | <0.001 |
| QShrink-CQR | CD wk 1 | 75 | <0.001 | 0.002 | <0.001 |
| QShrink-CQR (cov) | IS | 32 | <0.001 | 0.006 | <0.001 |
| QShrink-CQR (cov) | CD | 77 | <0.001 | 0.002 | <0.001 |
| QShrink-CQR (cov) | CD wk 1 | 62 | <0.001 | 0.002 | <0.001 |
| HSC-CQR | IS | 27 | <0.001 | 0.002 | <0.001 |
| HSC-CQR | CD | 76 | <0.001 | 0.002 | <0.001 |
| HSC-CQR | CD wk 1 | 72 | <0.001 | 0.002 | <0.001 |
| HSC-CQR simple | IS | 27 | <0.001 | 0.002 | <0.001 |
| HSC-CQR simple | CD | 73 | <0.001 | 0.002 | <0.001 |
| HSC-CQR simple | CD wk 1 | 73 | <0.001 | 0.002 | <0.001 |
| HSC-CQR fixed-κ | IS | 27 | <0.001 | 0.002 | <0.001 |
| HSC-CQR fixed-κ | CD | 77 | <0.001 | 0.002 | <0.001 |
| HSC-CQR fixed-κ | CD wk 1 | 69 | <0.001 | 0.002 | <0.001 |
| SSC-CQR | IS | 48 | 0.331 | 0.492 | 0.623 |
| SSC-CQR | CD | 84 | <0.001 | 0.002 | <0.001 |
| SSC-CQR | CD wk 1 | 77 | <0.001 | 0.002 | <0.001 |
| MLP-QR | IS | 62 | <0.001 | 0.922 | <0.001 |
| MLP-QR | CD | 89 | <0.001 | 0.002 | <0.001 |
| MLP-QR | CD wk 1 | 77 | <0.001 | 0.002 | <0.001 |
| MLP-Gauss | IS | 90 | <0.001 | 0.027 | <0.001 |
| MLP-Gauss | CD | 88 | <0.001 | 0.002 | <0.001 |
| MLP-Gauss | CD wk 1 | 81 | <0.001 | 0.002 | <0.001 |
| HSC-SSC-CQR | IS | 45 | 1.000 | 0.014 | 0.970 |
| HSC-SSC-CQR | CD | 72 | <0.001 | 0.004 | <0.001 |
| HSC-SSC-CQR | CD wk 1 | 55 | <0.001 | 0.002 | <0.001 |
| HSC-CQR simple (cov) | IS | 29 | <0.001 | 0.002 | <0.001 |
| HSC-CQR simple (cov) | CD | 78 | <0.001 | 0.002 | <0.001 |
| HSC-CQR simple (cov) | CD wk 1 | 66 | <0.001 | 0.002 | <0.001 |

**Table S6. BDG2, nominal 95 %.**

| Method               | Coverage      | Coverage (week 1)   | MACD          | Under-covered share   | P10 coverage   | Rel. width (median)   | Rel. IS (median)   |
|:---------------------|:--------------|:--------------------|:--------------|:----------------------|:---------------|:----------------------|:-------------------|
| HSC-CQR recency      | 0.948 ± 0.000 | 0.948 ± 0.002       | 0.008 ± 0.000 | 0.001 ± 0.002         | 0.934 ± 0.002  | 0.507 ± 0.029         | 0.703 ± 0.023      |
| HSC-SSC-CQR          | 0.948 ± 0.001 | 0.951 ± 0.003       | 0.010 ± 0.001 | 0.001 ± 0.002         | 0.932 ± 0.002  | 0.500 ± 0.022         | 0.702 ± 0.020      |
| SSC-CQR              | 0.951 ± 0.001 | 0.951 ± 0.005       | 0.019 ± 0.001 | 0.036 ± 0.008         | 0.920 ± 0.001  | 0.497 ± 0.014         | 0.694 ± 0.022      |
| HSC-CQR simple (cov) | 0.948 ± 0.001 | 0.947 ± 0.004       | 0.011 ± 0.001 | 0.004 ± 0.003         | 0.929 ± 0.001  | 0.492 ± 0.020         | 0.698 ± 0.023      |
| QShrink-CQR (cov)    | 0.948 ± 0.001 | 0.947 ± 0.004       | 0.011 ± 0.000 | 0.004 ± 0.003         | 0.929 ± 0.001  | 0.497 ± 0.027         | 0.699 ± 0.022      |
| ACI-CQR (cov)        | 0.950 ± 0.000 | 0.949 ± 0.003       | 0.003 ± 0.000 | 0.000 ± 0.000         | 0.945 ± 0.001  | 2.041 ± 0.414         | 2.256 ± 0.384      |
| HSC-CQR              | 0.944 ± 0.002 | 0.937 ± 0.006       | 0.015 ± 0.003 | 0.013 ± 0.010         | 0.920 ± 0.006  | 0.476 ± 0.017         | 0.690 ± 0.021      |
| HSC-CQR simple       | 0.949 ± 0.001 | 0.944 ± 0.004       | 0.015 ± 0.003 | 0.010 ± 0.007         | 0.925 ± 0.004  | 0.487 ± 0.023         | 0.687 ± 0.021      |
| HSC                  | 0.950 ± 0.003 | 0.939 ± 0.009       | 0.019 ± 0.002 | 0.034 ± 0.016         | 0.918 ± 0.007  | 0.571 ± 0.017         | 0.805 ± 0.026      |
| HSC simple           | 0.957 ± 0.002 | 0.956 ± 0.002       | 0.019 ± 0.003 | 0.017 ± 0.009         | 0.927 ± 0.002  | 0.608 ± 0.024         | 0.808 ± 0.026      |
| CQR                  | 0.943 ± 0.004 | 0.944 ± 0.005       | 0.032 ± 0.001 | 0.141 ± 0.021         | 0.887 ± 0.008  | 0.473 ± 0.021         | 0.680 ± 0.025      |
| Self-CQR             | 0.942 ± 0.001 | 0.914 ± 0.004       | 0.015 ± 0.001 | 0.021 ± 0.009         | 0.918 ± 0.002  | 0.497 ± 0.026         | 0.709 ± 0.022      |
| ACI-CQR              | 0.947 ± 0.002 | 0.945 ± 0.005       | 0.022 ± 0.001 | 0.051 ± 0.012         | 0.910 ± 0.004  | 0.479 ± 0.020         | 0.683 ± 0.024      |
| TQA-B-CQR            | 0.943 ± 0.003 | 0.945 ± 0.005       | 0.031 ± 0.000 | 0.140 ± 0.015         | 0.888 ± 0.006  | 0.474 ± 0.018         | 0.681 ± 0.024      |
| GHCP-CQR             | 0.946 ± 0.004 | 0.944 ± 0.005       | 0.031 ± 0.000 | 0.130 ± 0.019         | 0.891 ± 0.008  | 0.482 ± 0.021         | 0.680 ± 0.024      |
| QShrink-CQR          | 0.951 ± 0.001 | 0.948 ± 0.005       | 0.017 ± 0.003 | 0.011 ± 0.012         | 0.924 ± 0.005  | 0.488 ± 0.022         | 0.688 ± 0.017      |
| MLP-Gauss            | 0.950 ± 0.006 | 0.956 ± 0.013       | 0.026 ± 0.002 | 0.087 ± 0.048         | 0.904 ± 0.012  | 0.537 ± 0.036         | 0.739 ± 0.044      |
| CQR (MLP)            | 0.945 ± 0.003 | 0.948 ± 0.005       | 0.030 ± 0.002 | 0.125 ± 0.020         | 0.894 ± 0.004  | 0.482 ± 0.021         | 0.688 ± 0.024      |
| HSC-CQR (MLP)        | 0.950 ± 0.002 | 0.946 ± 0.003       | 0.014 ± 0.001 | 0.006 ± 0.004         | 0.928 ± 0.002  | 0.496 ± 0.022         | 0.692 ± 0.025      |
| ACI                  | 0.959 ± 0.004 | 0.948 ± 0.012       | 0.030 ± 0.004 | 0.074 ± 0.066         | 0.907 ± 0.015  | 0.637 ± 0.025         | 0.794 ± 0.023      |
| Self-CP              | 0.950 ± 0.002 | 0.937 ± 0.003       | 0.017 ± 0.001 | 0.028 ± 0.012         | 0.921 ± 0.003  | 0.591 ± 0.029         | 0.823 ± 0.023      |
| SCP-stage            | 0.937 ± 0.006 | 0.943 ± 0.012       | 0.059 ± 0.004 | 0.205 ± 0.027         | 0.820 ± 0.018  | 0.695 ± 0.045         | 0.810 ± 0.030      |
| SCP                  | 0.937 ± 0.006 | 0.926 ± 0.012       | 0.059 ± 0.004 | 0.204 ± 0.026         | 0.821 ± 0.019  | 0.694 ± 0.044         | 0.814 ± 0.026      |
| Mondrian-usage       | 0.938 ± 0.008 | 0.942 ± 0.011       | 0.058 ± 0.004 | 0.215 ± 0.046         | 0.825 ± 0.017  | 0.661 ± 0.064         | 0.879 ± 0.060      |
| Naive+SCP            | 0.940 ± 0.008 | 0.944 ± 0.008       | 0.058 ± 0.005 | 0.212 ± 0.031         | 0.823 ± 0.022  | 1.059 ± 0.081         | 1.222 ± 0.053      |
| Raw-SCP              | 0.953 ± 0.020 | 0.948 ± 0.024       | 0.071 ± 0.013 | 0.115 ± 0.049         | 0.863 ± 0.096  | 1.439 ± 0.240         | 1.831 ± 0.174      |
| HSC-CQR fixed-κ      | 0.948 ± 0.001 | 0.947 ± 0.004       | 0.012 ± 0.001 | 0.002 ± 0.002         | 0.930 ± 0.001  | 0.492 ± 0.022         | 0.696 ± 0.020      |


**Table S7. UCI, nominal 95 %.**

| Method               | Coverage      | Coverage (week 1)   | MACD          | Under-covered share   | P10 coverage   | Rel. width (median)   | Rel. IS (median)   |
|:---------------------|:--------------|:--------------------|:--------------|:----------------------|:---------------|:----------------------|:-------------------|
| HSC-CQR recency      | 0.952 ± 0.001 | 0.954 ± 0.001       | 0.007 ± 0.001 | 0.000 ± 0.000         | 0.941 ± 0.003  | 0.338 ± 0.015         | 0.454 ± 0.021      |
| HSC-SSC-CQR          | 0.951 ± 0.001 | 0.951 ± 0.003       | 0.008 ± 0.001 | 0.000 ± 0.000         | 0.938 ± 0.003  | 0.331 ± 0.016         | 0.447 ± 0.020      |
| SSC-CQR              | 0.964 ± 0.003 | 0.968 ± 0.004       | 0.018 ± 0.002 | 0.004 ± 0.006         | 0.945 ± 0.005  | 0.374 ± 0.024         | 0.461 ± 0.020      |
| HSC-CQR simple (cov) | 0.951 ± 0.002 | 0.951 ± 0.002       | 0.009 ± 0.001 | 0.000 ± 0.000         | 0.938 ± 0.003  | 0.330 ± 0.016         | 0.449 ± 0.020      |
| QShrink-CQR (cov)    | 0.951 ± 0.002 | 0.953 ± 0.005       | 0.009 ± 0.001 | 0.000 ± 0.000         | 0.936 ± 0.003  | 0.329 ± 0.014         | 0.450 ± 0.020      |
| ACI-CQR (cov)        | 0.950 ± 0.001 | 0.952 ± 0.003       | 0.003 ± 0.000 | 0.000 ± 0.000         | 0.946 ± 0.001  | 0.847 ± 0.385         | 0.950 ± 0.376      |
| HSC-CQR              | 0.949 ± 0.003 | 0.946 ± 0.004       | 0.010 ± 0.001 | 0.004 ± 0.009         | 0.934 ± 0.005  | 0.331 ± 0.017         | 0.446 ± 0.020      |
| HSC-CQR simple       | 0.952 ± 0.003 | 0.949 ± 0.004       | 0.010 ± 0.001 | 0.004 ± 0.009         | 0.937 ± 0.006  | 0.333 ± 0.016         | 0.445 ± 0.020      |
| HSC                  | 0.953 ± 0.004 | 0.945 ± 0.009       | 0.015 ± 0.001 | 0.023 ± 0.017         | 0.928 ± 0.008  | 0.381 ± 0.022         | 0.519 ± 0.020      |
| HSC simple           | 0.959 ± 0.002 | 0.959 ± 0.014       | 0.017 ± 0.002 | 0.011 ± 0.013         | 0.937 ± 0.004  | 0.412 ± 0.011         | 0.523 ± 0.018      |
| CQR                  | 0.950 ± 0.007 | 0.952 ± 0.006       | 0.027 ± 0.005 | 0.076 ± 0.020         | 0.913 ± 0.008  | 0.349 ± 0.026         | 0.445 ± 0.020      |
| Self-CQR             | 0.948 ± 0.002 | 0.934 ± 0.007       | 0.011 ± 0.001 | 0.000 ± 0.000         | 0.930 ± 0.003  | 0.326 ± 0.013         | 0.454 ± 0.017      |
| ACI-CQR              | 0.953 ± 0.003 | 0.953 ± 0.006       | 0.017 ± 0.005 | 0.023 ± 0.016         | 0.925 ± 0.005  | 0.344 ± 0.021         | 0.445 ± 0.020      |
| TQA-B-CQR            | 0.950 ± 0.006 | 0.953 ± 0.006       | 0.027 ± 0.005 | 0.078 ± 0.024         | 0.912 ± 0.009  | 0.347 ± 0.024         | 0.444 ± 0.021      |
| GHCP-CQR             | 0.958 ± 0.006 | 0.957 ± 0.007       | 0.028 ± 0.003 | 0.051 ± 0.009         | 0.924 ± 0.006  | 0.370 ± 0.029         | 0.454 ± 0.021      |
| QShrink-CQR          | 0.954 ± 0.003 | 0.956 ± 0.004       | 0.012 ± 0.002 | 0.002 ± 0.005         | 0.936 ± 0.008  | 0.340 ± 0.021         | 0.446 ± 0.020      |
| MLP-Gauss            | 0.954 ± 0.004 | 0.952 ± 0.011       | 0.020 ± 0.001 | 0.036 ± 0.019         | 0.924 ± 0.006  | 0.357 ± 0.020         | 0.480 ± 0.023      |
| CQR (MLP)            | 0.949 ± 0.008 | 0.951 ± 0.010       | 0.027 ± 0.005 | 0.069 ± 0.018         | 0.914 ± 0.011  | 0.352 ± 0.022         | 0.459 ± 0.021      |
| HSC-CQR (MLP)        | 0.953 ± 0.004 | 0.947 ± 0.008       | 0.011 ± 0.001 | 0.006 ± 0.009         | 0.937 ± 0.006  | 0.342 ± 0.019         | 0.459 ± 0.019      |
| ACI                  | 0.967 ± 0.007 | 0.957 ± 0.016       | 0.031 ± 0.009 | 0.032 ± 0.048         | 0.922 ± 0.023  | 0.495 ± 0.069         | 0.555 ± 0.043      |
| Self-CP              | 0.954 ± 0.002 | 0.950 ± 0.004       | 0.014 ± 0.001 | 0.004 ± 0.009         | 0.932 ± 0.002  | 0.390 ± 0.024         | 0.521 ± 0.014      |
| SCP-stage            | 0.950 ± 0.015 | 0.948 ± 0.015       | 0.059 ± 0.009 | 0.135 ± 0.033         | 0.877 ± 0.030  | 0.579 ± 0.083         | 0.615 ± 0.067      |
| SCP                  | 0.950 ± 0.015 | 0.934 ± 0.020       | 0.059 ± 0.009 | 0.131 ± 0.035         | 0.878 ± 0.030  | 0.576 ± 0.084         | 0.613 ± 0.066      |
| Naive+SCP            | 0.951 ± 0.008 | 0.948 ± 0.005       | 0.053 ± 0.003 | 0.162 ± 0.022         | 0.862 ± 0.027  | 0.711 ± 0.076         | 0.765 ± 0.057      |
| Raw-SCP              | 0.951 ± 0.036 | 0.945 ± 0.039       | 0.079 ± 0.024 | 0.114 ± 0.090         | 0.842 ± 0.203  | 1.998 ± 0.831         | 2.153 ± 0.676      |
| HSC-CQR fixed-κ      | 0.952 ± 0.002 | 0.950 ± 0.003       | 0.010 ± 0.001 | 0.000 ± 0.000         | 0.939 ± 0.003  | 0.334 ± 0.018         | 0.446 ± 0.019      |


**Table S8. BDG2, nominal 80 %.**

| Method               | Coverage      | Coverage (week 1)   | MACD          | Under-covered share   | P10 coverage   | Rel. width (median)   | Rel. IS (median)   |
|:---------------------|:--------------|:--------------------|:--------------|:----------------------|:---------------|:----------------------|:-------------------|
| HSC-CQR recency      | 0.794 ± 0.001 | 0.802 ± 0.003       | 0.017 ± 0.001 | 0.032 ± 0.007         | 0.766 ± 0.003  | 0.322 ± 0.014         | 0.465 ± 0.020      |
| HSC-SSC-CQR          | 0.800 ± 0.002 | 0.805 ± 0.003       | 0.020 ± 0.002 | 0.032 ± 0.009         | 0.769 ± 0.005  | 0.319 ± 0.012         | 0.464 ± 0.020      |
| SSC-CQR              | 0.792 ± 0.009 | 0.792 ± 0.020       | 0.055 ± 0.004 | 0.204 ± 0.037         | 0.712 ± 0.017  | 0.321 ± 0.013         | 0.463 ± 0.018      |
| HSC-CQR simple (cov) | 0.793 ± 0.002 | 0.809 ± 0.002       | 0.022 ± 0.001 | 0.064 ± 0.008         | 0.759 ± 0.004  | 0.320 ± 0.012         | 0.462 ± 0.017      |
| QShrink-CQR (cov)    | 0.790 ± 0.004 | 0.792 ± 0.007       | 0.023 ± 0.002 | 0.082 ± 0.015         | 0.755 ± 0.004  | 0.319 ± 0.013         | 0.464 ± 0.019      |
| ACI-CQR (cov)        | 0.801 ± 0.000 | 0.804 ± 0.003       | 0.006 ± 0.000 | 0.000 ± 0.000         | 0.792 ± 0.001  | 0.383 ± 0.020         | 0.517 ± 0.034      |
| HSC-CQR              | 0.795 ± 0.004 | 0.796 ± 0.008       | 0.022 ± 0.001 | 0.055 ± 0.012         | 0.761 ± 0.004  | 0.318 ± 0.011         | 0.461 ± 0.018      |
| HSC-CQR simple       | 0.796 ± 0.004 | 0.813 ± 0.005       | 0.023 ± 0.001 | 0.063 ± 0.020         | 0.759 ± 0.004  | 0.321 ± 0.013         | 0.461 ± 0.016      |
| HSC                  | 0.799 ± 0.003 | 0.776 ± 0.009       | 0.039 ± 0.002 | 0.150 ± 0.025         | 0.733 ± 0.005  | 0.277 ± 0.011         | 0.493 ± 0.025      |
| HSC simple           | 0.811 ± 0.003 | 0.804 ± 0.008       | 0.041 ± 0.002 | 0.118 ± 0.016         | 0.745 ± 0.005  | 0.287 ± 0.012         | 0.496 ± 0.021      |
| CQR                  | 0.795 ± 0.008 | 0.795 ± 0.013       | 0.048 ± 0.005 | 0.168 ± 0.028         | 0.720 ± 0.017  | 0.326 ± 0.014         | 0.463 ± 0.017      |
| Self-CQR             | 0.782 ± 0.003 | 0.758 ± 0.006       | 0.030 ± 0.002 | 0.157 ± 0.031         | 0.738 ± 0.006  | 0.319 ± 0.016         | 0.468 ± 0.019      |
| ACI-CQR              | 0.802 ± 0.002 | 0.797 ± 0.009       | 0.019 ± 0.003 | 0.013 ± 0.009         | 0.773 ± 0.004  | 0.322 ± 0.013         | 0.462 ± 0.017      |
| TQA-B-CQR            | 0.818 ± 0.001 | 0.811 ± 0.002       | 0.040 ± 0.003 | 0.052 ± 0.013         | 0.763 ± 0.002  | 0.328 ± 0.011         | 0.465 ± 0.018      |
| GHCP-CQR             | 0.798 ± 0.008 | 0.817 ± 0.006       | 0.047 ± 0.005 | 0.152 ± 0.027         | 0.725 ± 0.015  | 0.327 ± 0.014         | 0.463 ± 0.017      |
| QShrink-CQR          | 0.793 ± 0.006 | 0.795 ± 0.011       | 0.029 ± 0.005 | 0.104 ± 0.039         | 0.748 ± 0.012  | 0.320 ± 0.015         | 0.463 ± 0.019      |
| MLP-Gauss            | 0.868 ± 0.014 | 0.887 ± 0.029       | 0.077 ± 0.009 | 0.028 ± 0.018         | 0.789 ± 0.018  | 0.351 ± 0.024         | 0.479 ± 0.032      |
| CQR (MLP)            | 0.798 ± 0.004 | 0.799 ± 0.009       | 0.046 ± 0.006 | 0.170 ± 0.028         | 0.725 ± 0.014  | 0.330 ± 0.015         | 0.466 ± 0.017      |
| HSC-CQR (MLP)        | 0.798 ± 0.003 | 0.810 ± 0.016       | 0.024 ± 0.003 | 0.062 ± 0.018         | 0.761 ± 0.007  | 0.326 ± 0.011         | 0.465 ± 0.019      |
| ACI                  | 0.811 ± 0.004 | 0.791 ± 0.013       | 0.060 ± 0.015 | 0.206 ± 0.083         | 0.716 ± 0.028  | 0.279 ± 0.009         | 0.490 ± 0.024      |
| Self-CP              | 0.809 ± 0.004 | 0.816 ± 0.004       | 0.038 ± 0.002 | 0.102 ± 0.021         | 0.750 ± 0.008  | 0.293 ± 0.012         | 0.501 ± 0.020      |
| SCP-stage            | 0.775 ± 0.011 | 0.783 ± 0.014       | 0.139 ± 0.007 | 0.383 ± 0.028         | 0.529 ± 0.030  | 0.282 ± 0.012         | 0.493 ± 0.022      |
| SCP                  | 0.775 ± 0.011 | 0.752 ± 0.011       | 0.138 ± 0.007 | 0.385 ± 0.031         | 0.531 ± 0.030  | 0.281 ± 0.013         | 0.494 ± 0.021      |
| Mondrian-usage       | 0.778 ± 0.015 | 0.786 ± 0.020       | 0.136 ± 0.004 | 0.378 ± 0.041         | 0.541 ± 0.018  | 0.266 ± 0.023         | 0.507 ± 0.024      |
| Naive+SCP            | 0.778 ± 0.013 | 0.787 ± 0.013       | 0.142 ± 0.006 | 0.404 ± 0.027         | 0.534 ± 0.028  | 0.402 ± 0.027         | 0.745 ± 0.033      |
| Raw-SCP              | 0.813 ± 0.025 | 0.793 ± 0.030       | 0.181 ± 0.014 | 0.279 ± 0.041         | 0.467 ± 0.094  | 0.391 ± 0.019         | 0.692 ± 0.034      |
| HSC-CQR fixed-κ      | 0.794 ± 0.003 | 0.811 ± 0.004       | 0.021 ± 0.001 | 0.064 ± 0.009         | 0.760 ± 0.003  | 0.319 ± 0.011         | 0.462 ± 0.017      |


**Table S9. UCI, nominal 80 %.**

| Method               | Coverage      | Coverage (week 1)   | MACD          | Under-covered share   | P10 coverage   | Rel. width (median)   | Rel. IS (median)   |
|:---------------------|:--------------|:--------------------|:--------------|:----------------------|:---------------|:----------------------|:-------------------|
| HSC-CQR recency      | 0.799 ± 0.002 | 0.809 ± 0.006       | 0.014 ± 0.002 | 0.002 ± 0.005         | 0.776 ± 0.004  | 0.214 ± 0.010         | 0.302 ± 0.012      |
| HSC-SSC-CQR          | 0.807 ± 0.004 | 0.814 ± 0.010       | 0.020 ± 0.001 | 0.013 ± 0.009         | 0.777 ± 0.008  | 0.215 ± 0.011         | 0.301 ± 0.012      |
| SSC-CQR              | 0.816 ± 0.019 | 0.813 ± 0.012       | 0.063 ± 0.005 | 0.135 ± 0.067         | 0.740 ± 0.028  | 0.230 ± 0.019         | 0.306 ± 0.013      |
| HSC-CQR simple (cov) | 0.797 ± 0.003 | 0.812 ± 0.006       | 0.019 ± 0.003 | 0.019 ± 0.014         | 0.768 ± 0.004  | 0.213 ± 0.011         | 0.302 ± 0.012      |
| QShrink-CQR (cov)    | 0.795 ± 0.003 | 0.796 ± 0.009       | 0.020 ± 0.003 | 0.038 ± 0.022         | 0.766 ± 0.008  | 0.212 ± 0.011         | 0.301 ± 0.011      |
| ACI-CQR (cov)        | 0.802 ± 0.001 | 0.803 ± 0.004       | 0.006 ± 0.001 | 0.000 ± 0.000         | 0.793 ± 0.001  | 0.219 ± 0.010         | 0.306 ± 0.013      |
| HSC-CQR              | 0.797 ± 0.003 | 0.796 ± 0.008       | 0.021 ± 0.003 | 0.032 ± 0.020         | 0.766 ± 0.008  | 0.213 ± 0.010         | 0.301 ± 0.011      |
| HSC-CQR simple       | 0.799 ± 0.004 | 0.813 ± 0.009       | 0.021 ± 0.005 | 0.034 ± 0.026         | 0.768 ± 0.010  | 0.214 ± 0.011         | 0.301 ± 0.012      |
| HSC                  | 0.805 ± 0.005 | 0.791 ± 0.003       | 0.028 ± 0.001 | 0.074 ± 0.017         | 0.762 ± 0.006  | 0.198 ± 0.005         | 0.321 ± 0.013      |
| HSC simple           | 0.814 ± 0.006 | 0.815 ± 0.011       | 0.031 ± 0.004 | 0.046 ± 0.033         | 0.768 ± 0.006  | 0.205 ± 0.006         | 0.322 ± 0.012      |
| CQR                  | 0.798 ± 0.015 | 0.798 ± 0.008       | 0.047 ± 0.008 | 0.128 ± 0.093         | 0.746 ± 0.030  | 0.220 ± 0.016         | 0.304 ± 0.013      |
| Self-CQR             | 0.787 ± 0.002 | 0.763 ± 0.011       | 0.024 ± 0.002 | 0.084 ± 0.032         | 0.754 ± 0.004  | 0.210 ± 0.011         | 0.303 ± 0.012      |
| ACI-CQR              | 0.806 ± 0.005 | 0.800 ± 0.006       | 0.019 ± 0.003 | 0.013 ± 0.014         | 0.780 ± 0.006  | 0.216 ± 0.012         | 0.301 ± 0.012      |
| TQA-B-CQR            | 0.807 ± 0.005 | 0.802 ± 0.008       | 0.042 ± 0.004 | 0.109 ± 0.060         | 0.752 ± 0.017  | 0.220 ± 0.007         | 0.304 ± 0.012      |
| GHCP-CQR             | 0.805 ± 0.015 | 0.825 ± 0.015       | 0.047 ± 0.005 | 0.114 ± 0.068         | 0.754 ± 0.028  | 0.223 ± 0.016         | 0.304 ± 0.013      |
| QShrink-CQR          | 0.796 ± 0.007 | 0.800 ± 0.009       | 0.025 ± 0.008 | 0.063 ± 0.054         | 0.767 ± 0.016  | 0.213 ± 0.011         | 0.301 ± 0.011      |
| MLP-Gauss            | 0.869 ± 0.007 | 0.878 ± 0.016       | 0.073 ± 0.005 | 0.008 ± 0.014         | 0.810 ± 0.017  | 0.233 ± 0.013         | 0.317 ± 0.016      |
| CQR (MLP)            | 0.797 ± 0.013 | 0.800 ± 0.013       | 0.045 ± 0.011 | 0.139 ± 0.115         | 0.742 ± 0.022  | 0.219 ± 0.010         | 0.313 ± 0.010      |
| HSC-CQR (MLP)        | 0.799 ± 0.010 | 0.806 ± 0.020       | 0.023 ± 0.005 | 0.044 ± 0.058         | 0.765 ± 0.013  | 0.217 ± 0.007         | 0.310 ± 0.009      |
| ACI                  | 0.816 ± 0.011 | 0.810 ± 0.020       | 0.072 ± 0.028 | 0.192 ± 0.067         | 0.702 ± 0.045  | 0.215 ± 0.012         | 0.323 ± 0.014      |
| Self-CP              | 0.811 ± 0.005 | 0.824 ± 0.004       | 0.029 ± 0.002 | 0.042 ± 0.027         | 0.769 ± 0.005  | 0.205 ± 0.005         | 0.323 ± 0.011      |
| SCP-stage            | 0.805 ± 0.017 | 0.809 ± 0.019       | 0.124 ± 0.006 | 0.280 ± 0.045         | 0.614 ± 0.026  | 0.231 ± 0.013         | 0.327 ± 0.010      |
| SCP                  | 0.805 ± 0.017 | 0.780 ± 0.014       | 0.124 ± 0.006 | 0.282 ± 0.044         | 0.613 ± 0.027  | 0.231 ± 0.013         | 0.328 ± 0.009      |
| Naive+SCP            | 0.807 ± 0.015 | 0.807 ± 0.016       | 0.097 ± 0.010 | 0.263 ± 0.051         | 0.638 ± 0.046  | 0.294 ± 0.013         | 0.449 ± 0.017      |
| Raw-SCP              | 0.807 ± 0.056 | 0.791 ± 0.055       | 0.208 ± 0.024 | 0.284 ± 0.086         | 0.408 ± 0.154  | 0.406 ± 0.097         | 0.559 ± 0.028      |
| HSC-CQR fixed-κ      | 0.799 ± 0.004 | 0.813 ± 0.008       | 0.019 ± 0.003 | 0.025 ± 0.018         | 0.770 ± 0.007  | 0.214 ± 0.011         | 0.301 ± 0.012      |


**Table S10. BDG2 leave-site-out (5 site folds).**

| Method               | Coverage      | Coverage (week 1)   | MACD          | Under-covered share   | P10 coverage   | Rel. width (median)   | Rel. IS (median)   |
|:---------------------|:--------------|:--------------------|:--------------|:----------------------|:---------------|:----------------------|:-------------------|
| HSC-CQR recency      | 0.896 ± 0.003 | 0.897 ± 0.016       | 0.012 ± 0.001 | 0.004 ± 0.005         | 0.877 ± 0.003  | 0.386 ± 0.082         | 0.537 ± 0.114      |
| HSC-SSC-CQR          | 0.900 ± 0.003 | 0.905 ± 0.017       | 0.015 ± 0.001 | 0.011 ± 0.004         | 0.876 ± 0.001  | 0.389 ± 0.085         | 0.539 ± 0.118      |
| SSC-CQR              | 0.899 ± 0.020 | 0.902 ± 0.032       | 0.036 ± 0.004 | 0.138 ± 0.091         | 0.850 ± 0.022  | 0.384 ± 0.058         | 0.539 ± 0.115      |
| HSC-CQR simple (cov) | 0.896 ± 0.004 | 0.899 ± 0.021       | 0.016 ± 0.001 | 0.014 ± 0.008         | 0.872 ± 0.003  | 0.382 ± 0.080         | 0.536 ± 0.118      |
| QShrink-CQR (cov)    | 0.898 ± 0.004 | 0.901 ± 0.023       | 0.016 ± 0.001 | 0.017 ± 0.009         | 0.873 ± 0.004  | 0.384 ± 0.080         | 0.537 ± 0.117      |
| ACI-CQR (cov)        | 0.900 ± 0.001 | 0.900 ± 0.015       | 0.004 ± 0.001 | 0.000 ± 0.000         | 0.893 ± 0.001  | 1.428 ± 0.703         | 1.582 ± 0.706      |
| HSC-CQR              | 0.893 ± 0.009 | 0.888 ± 0.029       | 0.020 ± 0.004 | 0.053 ± 0.026         | 0.863 ± 0.008  | 0.374 ± 0.071         | 0.533 ± 0.116      |
| HSC-CQR simple       | 0.897 ± 0.010 | 0.896 ± 0.030       | 0.020 ± 0.004 | 0.035 ± 0.018         | 0.868 ± 0.008  | 0.380 ± 0.071         | 0.533 ± 0.116      |
| HSC                  | 0.900 ± 0.013 | 0.886 ± 0.032       | 0.030 ± 0.002 | 0.107 ± 0.062         | 0.850 ± 0.015  | 0.404 ± 0.065         | 0.610 ± 0.127      |
| HSC simple           | 0.913 ± 0.012 | 0.903 ± 0.030       | 0.034 ± 0.005 | 0.068 ± 0.034         | 0.861 ± 0.011  | 0.427 ± 0.069         | 0.612 ± 0.126      |
| CQR                  | 0.894 ± 0.027 | 0.896 ± 0.037       | 0.044 ± 0.008 | 0.218 ± 0.176         | 0.835 ± 0.029  | 0.374 ± 0.052         | 0.539 ± 0.117      |
| Self-CQR             | 0.889 ± 0.005 | 0.863 ± 0.006       | 0.022 ± 0.003 | 0.063 ± 0.037         | 0.859 ± 0.009  | 0.388 ± 0.088         | 0.545 ± 0.114      |
| ACI-CQR              | 0.897 ± 0.014 | 0.896 ± 0.035       | 0.026 ± 0.006 | 0.084 ± 0.067         | 0.858 ± 0.019  | 0.377 ± 0.065         | 0.534 ± 0.115      |
| TQA-B-CQR            | 0.897 ± 0.027 | 0.898 ± 0.034       | 0.043 ± 0.007 | 0.199 ± 0.176         | 0.836 ± 0.026  | 0.373 ± 0.053         | 0.540 ± 0.117      |
| GHCP-CQR             | 0.896 ± 0.027 | 0.897 ± 0.036       | 0.044 ± 0.007 | 0.203 ± 0.163         | 0.836 ± 0.029  | 0.376 ± 0.052         | 0.538 ± 0.117      |
| QShrink-CQR          | 0.900 ± 0.014 | 0.901 ± 0.032       | 0.026 ± 0.010 | 0.042 ± 0.052         | 0.864 ± 0.009  | 0.380 ± 0.068         | 0.536 ± 0.117      |
| QR-LGBM              | 0.867 ± 0.023 | 0.871 ± 0.035       | 0.049 ± 0.014 | 0.346 ± 0.205         | 0.807 ± 0.024  | 0.352 ± 0.054         | 0.539 ± 0.121      |
| MLP-QR               | 0.889 ± 0.029 | 0.898 ± 0.044       | 0.043 ± 0.011 | 0.250 ± 0.190         | 0.833 ± 0.031  | 0.379 ± 0.054         | 0.547 ± 0.108      |
| MLP-Gauss            | 0.931 ± 0.013 | 0.935 ± 0.016       | 0.045 ± 0.007 | 0.050 ± 0.040         | 0.878 ± 0.022  | 0.462 ± 0.088         | 0.584 ± 0.122      |
| CQR (MLP)            | 0.896 ± 0.024 | 0.898 ± 0.037       | 0.041 ± 0.007 | 0.191 ± 0.142         | 0.839 ± 0.025  | 0.385 ± 0.051         | 0.545 ± 0.106      |
| HSC-CQR (MLP)        | 0.895 ± 0.011 | 0.905 ± 0.036       | 0.020 ± 0.005 | 0.042 ± 0.024         | 0.866 ± 0.009  | 0.386 ± 0.065         | 0.542 ± 0.108      |
| ACI                  | 0.910 ± 0.032 | 0.895 ± 0.052       | 0.063 ± 0.023 | 0.193 ± 0.126         | 0.812 ± 0.063  | 0.451 ± 0.033         | 0.622 ± 0.097      |
| Self-CP              | 0.905 ± 0.003 | 0.902 ± 0.008       | 0.026 ± 0.001 | 0.063 ± 0.021         | 0.861 ± 0.007  | 0.427 ± 0.083         | 0.619 ± 0.129      |
| SCP-stage            | 0.881 ± 0.064 | 0.890 ± 0.057       | 0.100 ± 0.028 | 0.308 ± 0.178         | 0.714 ± 0.129  | 0.457 ± 0.049         | 0.641 ± 0.105      |
| SCP                  | 0.881 ± 0.063 | 0.863 ± 0.067       | 0.099 ± 0.027 | 0.305 ± 0.177         | 0.716 ± 0.130  | 0.456 ± 0.048         | 0.643 ± 0.104      |
| Mondrian-usage       | 0.872 ± 0.064 | 0.884 ± 0.057       | 0.103 ± 0.032 | 0.330 ± 0.194         | 0.703 ± 0.117  | 0.409 ± 0.028         | 0.661 ± 0.125      |
| Naive+SCP            | 0.887 ± 0.073 | 0.900 ± 0.038       | 0.099 ± 0.033 | 0.287 ± 0.232         | 0.739 ± 0.135  | 0.691 ± 0.093         | 0.957 ± 0.174      |
| Raw-SCP              | 0.891 ± 0.039 | 0.877 ± 0.045       | 0.120 ± 0.028 | 0.235 ± 0.071         | 0.676 ± 0.139  | 0.646 ± 0.255         | 1.023 ± 0.254      |
| HSC -stage           | 0.897 ± 0.013 | 0.859 ± 0.038       | 0.029 ± 0.003 | 0.121 ± 0.066         | 0.848 ± 0.017  | 0.398 ± 0.065         | 0.614 ± 0.130      |
| HSC -kNN             | 0.915 ± 0.011 | 0.923 ± 0.024       | 0.034 ± 0.005 | 0.060 ± 0.025         | 0.864 ± 0.009  | 0.433 ± 0.068         | 0.612 ± 0.121      |
| HSC -shrink          | 0.834 ± 0.077 | 0.833 ± 0.067       | 0.103 ± 0.056 | 0.457 ± 0.245         | 0.696 ± 0.106  | 0.339 ± 0.037         | 0.659 ± 0.158      |
| HSC-CQR -stage       | 0.891 ± 0.011 | 0.888 ± 0.030       | 0.022 ± 0.006 | 0.068 ± 0.043         | 0.860 ± 0.010  | 0.372 ± 0.068         | 0.534 ± 0.117      |
| HSC-CQR -kNN         | 0.897 ± 0.010 | 0.900 ± 0.030       | 0.020 ± 0.004 | 0.035 ± 0.019         | 0.869 ± 0.008  | 0.381 ± 0.071         | 0.533 ± 0.116      |
| HSC-CQR -shrink      | 0.885 ± 0.023 | 0.884 ± 0.035       | 0.042 ± 0.011 | 0.243 ± 0.187         | 0.826 ± 0.027  | 0.362 ± 0.049         | 0.539 ± 0.119      |
| HSC-CQR fixed-κ      | 0.896 ± 0.005 | 0.897 ± 0.025       | 0.016 ± 0.002 | 0.017 ± 0.010         | 0.870 ± 0.004  | 0.381 ± 0.077         | 0.535 ± 0.117      |


**Table S11. BDG2 → UCI transfer (no weather; 3 seeds).**

| Method               | Coverage      | Coverage (week 1)   | MACD          | Under-covered share   | P10 coverage   | Rel. width (median)   | Rel. IS (median)   |
|:---------------------|:--------------|:--------------------|:--------------|:----------------------|:---------------|:----------------------|:-------------------|
| HSC-CQR recency      | 0.901 ± 0.001 | 0.906 ± 0.008       | 0.009 ± 0.000 | 0.000 ± 0.000         | 0.888 ± 0.001  | 0.318 ± 0.009         | 0.441 ± 0.014      |
| HSC-SSC-CQR          | 0.901 ± 0.002 | 0.911 ± 0.009       | 0.011 ± 0.001 | 0.004 ± 0.006         | 0.885 ± 0.002  | 0.317 ± 0.009         | 0.440 ± 0.016      |
| SSC-CQR              | 0.910 ± 0.009 | 0.911 ± 0.007       | 0.025 ± 0.001 | 0.021 ± 0.036         | 0.874 ± 0.013  | 0.324 ± 0.013         | 0.442 ± 0.015      |
| HSC-CQR simple (cov) | 0.901 ± 0.002 | 0.907 ± 0.009       | 0.011 ± 0.001 | 0.004 ± 0.006         | 0.885 ± 0.001  | 0.316 ± 0.009         | 0.439 ± 0.015      |
| QShrink-CQR (cov)    | 0.900 ± 0.002 | 0.904 ± 0.009       | 0.011 ± 0.001 | 0.000 ± 0.000         | 0.883 ± 0.001  | 0.314 ± 0.009         | 0.438 ± 0.015      |
| ACI-CQR (cov)        | 0.901 ± 0.001 | 0.904 ± 0.005       | 0.004 ± 0.000 | 0.000 ± 0.000         | 0.896 ± 0.001  | 0.475 ± 0.020         | 0.577 ± 0.029      |
| HSC-CQR              | 0.899 ± 0.002 | 0.895 ± 0.006       | 0.013 ± 0.000 | 0.004 ± 0.006         | 0.880 ± 0.002  | 0.312 ± 0.002         | 0.437 ± 0.016      |
| HSC-CQR simple       | 0.902 ± 0.003 | 0.907 ± 0.011       | 0.013 ± 0.001 | 0.007 ± 0.006         | 0.886 ± 0.003  | 0.318 ± 0.006         | 0.438 ± 0.016      |
| HSC                  | 0.920 ± 0.002 | 0.885 ± 0.005       | 0.032 ± 0.005 | 0.042 ± 0.000         | 0.880 ± 0.009  | 0.361 ± 0.009         | 0.477 ± 0.018      |
| HSC simple           | 0.923 ± 0.002 | 0.901 ± 0.002       | 0.031 ± 0.003 | 0.011 ± 0.018         | 0.889 ± 0.010  | 0.372 ± 0.015         | 0.479 ± 0.017      |
| CQR                  | 0.903 ± 0.013 | 0.903 ± 0.011       | 0.028 ± 0.004 | 0.056 ± 0.043         | 0.870 ± 0.011  | 0.318 ± 0.013         | 0.442 ± 0.016      |
| Self-CQR             | 0.892 ± 0.003 | 0.866 ± 0.008       | 0.016 ± 0.001 | 0.021 ± 0.028         | 0.866 ± 0.004  | 0.316 ± 0.005         | 0.447 ± 0.016      |
| ACI-CQR              | 0.904 ± 0.005 | 0.904 ± 0.009       | 0.015 ± 0.001 | 0.011 ± 0.011         | 0.885 ± 0.004  | 0.317 ± 0.007         | 0.437 ± 0.016      |
| TQA-B-CQR            | 0.901 ± 0.013 | 0.902 ± 0.011       | 0.027 ± 0.005 | 0.063 ± 0.038         | 0.867 ± 0.011  | 0.315 ± 0.012         | 0.441 ± 0.018      |
| GHCP-CQR             | 0.905 ± 0.013 | 0.909 ± 0.014       | 0.028 ± 0.003 | 0.049 ± 0.034         | 0.873 ± 0.009  | 0.321 ± 0.013         | 0.443 ± 0.015      |
| QShrink-CQR          | 0.903 ± 0.004 | 0.907 ± 0.007       | 0.014 ± 0.001 | 0.004 ± 0.006         | 0.883 ± 0.003  | 0.316 ± 0.004         | 0.436 ± 0.017      |
| QR-LGBM              | 0.882 ± 0.006 | 0.889 ± 0.009       | 0.031 ± 0.006 | 0.158 ± 0.018         | 0.841 ± 0.003  | 0.301 ± 0.006         | 0.440 ± 0.017      |
| MLP-QR               | 0.908 ± 0.002 | 0.907 ± 0.015       | 0.024 ± 0.003 | 0.032 ± 0.021         | 0.873 ± 0.005  | 0.327 ± 0.004         | 0.435 ± 0.014      |
| MLP-Gauss            | 0.947 ± 0.014 | 0.948 ± 0.008       | 0.048 ± 0.014 | 0.004 ± 0.006         | 0.919 ± 0.014  | 0.384 ± 0.038         | 0.457 ± 0.024      |
| CQR (MLP)            | 0.902 ± 0.004 | 0.909 ± 0.007       | 0.024 ± 0.003 | 0.035 ± 0.026         | 0.867 ± 0.005  | 0.322 ± 0.004         | 0.435 ± 0.017      |
| HSC-CQR (MLP)        | 0.902 ± 0.000 | 0.903 ± 0.014       | 0.014 ± 0.002 | 0.011 ± 0.018         | 0.881 ± 0.003  | 0.325 ± 0.009         | 0.433 ± 0.016      |
| ACI                  | 0.931 ± 0.004 | 0.897 ± 0.008       | 0.049 ± 0.003 | 0.077 ± 0.016         | 0.864 ± 0.006  | 0.398 ± 0.017         | 0.481 ± 0.016      |
| Self-CP              | 0.920 ± 0.001 | 0.900 ± 0.000       | 0.026 ± 0.001 | 0.018 ± 0.016         | 0.892 ± 0.003  | 0.366 ± 0.010         | 0.490 ± 0.023      |
| SCP-stage            | 0.916 ± 0.009 | 0.891 ± 0.009       | 0.088 ± 0.008 | 0.154 ± 0.024         | 0.801 ± 0.017  | 0.466 ± 0.024         | 0.524 ± 0.014      |
| SCP                  | 0.915 ± 0.010 | 0.866 ± 0.011       | 0.087 ± 0.008 | 0.154 ± 0.024         | 0.804 ± 0.016  | 0.466 ± 0.025         | 0.527 ± 0.017      |
| Naive+SCP            | 0.941 ± 0.007 | 0.938 ± 0.012       | 0.085 ± 0.002 | 0.105 ± 0.000         | 0.848 ± 0.006  | 0.661 ± 0.041         | 0.691 ± 0.030      |
| Raw-SCP              | 0.787 ± 0.043 | 0.740 ± 0.040       | 0.195 ± 0.036 | 0.411 ± 0.079         | 0.360 ± 0.136  | 0.413 ± 0.038         | 0.758 ± 0.049      |
| HSC -stage           | 0.919 ± 0.003 | 0.874 ± 0.005       | 0.031 ± 0.005 | 0.046 ± 0.006         | 0.878 ± 0.011  | 0.362 ± 0.012         | 0.476 ± 0.019      |
| HSC -kNN             | 0.925 ± 0.002 | 0.917 ± 0.001       | 0.032 ± 0.003 | 0.007 ± 0.012         | 0.892 ± 0.009  | 0.377 ± 0.015         | 0.483 ± 0.016      |
| HSC -shrink          | 0.897 ± 0.010 | 0.850 ± 0.010       | 0.077 ± 0.008 | 0.207 ± 0.034         | 0.778 ± 0.013  | 0.397 ± 0.026         | 0.503 ± 0.008      |
| HSC-CQR -stage       | 0.899 ± 0.002 | 0.901 ± 0.011       | 0.013 ± 0.001 | 0.004 ± 0.006         | 0.881 ± 0.002  | 0.312 ± 0.001         | 0.438 ± 0.016      |
| HSC-CQR -kNN         | 0.902 ± 0.003 | 0.904 ± 0.009       | 0.013 ± 0.001 | 0.011 ± 0.011         | 0.883 ± 0.004  | 0.317 ± 0.006         | 0.437 ± 0.016      |
| HSC-CQR -shrink      | 0.894 ± 0.012 | 0.890 ± 0.014       | 0.029 ± 0.008 | 0.095 ± 0.079         | 0.855 ± 0.015  | 0.308 ± 0.008         | 0.444 ± 0.014      |
| HSC-CQR fixed-κ      | 0.901 ± 0.002 | 0.907 ± 0.010       | 0.011 ± 0.001 | 0.004 ± 0.006         | 0.885 ± 0.001  | 0.316 ± 0.008         | 0.439 ± 0.016      |


**Table S12. UCI → BDG2 transfer (no weather; 3 seeds).**

| Method               | Coverage      | Coverage (week 1)   | MACD          | Under-covered share   | P10 coverage   | Rel. width (median)   | Rel. IS (median)   |
|:---------------------|:--------------|:--------------------|:--------------|:----------------------|:---------------|:----------------------|:-------------------|
| HSC-CQR recency      | 0.895 ± 0.001 | 0.878 ± 0.006       | 0.014 ± 0.001 | 0.012 ± 0.007         | 0.874 ± 0.002  | 0.419 ± 0.021         | 0.605 ± 0.028      |
| HSC-SSC-CQR          | 0.898 ± 0.003 | 0.881 ± 0.002       | 0.018 ± 0.000 | 0.022 ± 0.005         | 0.869 ± 0.001  | 0.418 ± 0.017         | 0.611 ± 0.023      |
| SSC-CQR              | 0.884 ± 0.002 | 0.885 ± 0.007       | 0.042 ± 0.002 | 0.250 ± 0.006         | 0.819 ± 0.003  | 0.398 ± 0.024         | 0.610 ± 0.028      |
| HSC-CQR simple (cov) | 0.894 ± 0.002 | 0.873 ± 0.006       | 0.018 ± 0.001 | 0.032 ± 0.010         | 0.866 ± 0.004  | 0.412 ± 0.026         | 0.605 ± 0.027      |
| QShrink-CQR (cov)    | 0.896 ± 0.003 | 0.877 ± 0.003       | 0.018 ± 0.001 | 0.033 ± 0.012         | 0.868 ± 0.003  | 0.415 ± 0.021         | 0.607 ± 0.029      |
| ACI-CQR (cov)        | 0.899 ± 0.000 | 0.886 ± 0.002       | 0.005 ± 0.000 | 0.000 ± 0.000         | 0.892 ± 0.001  | 1.770 ± 1.270         | 1.915 ± 1.232      |
| HSC-CQR              | 0.887 ± 0.001 | 0.862 ± 0.007       | 0.023 ± 0.002 | 0.087 ± 0.040         | 0.853 ± 0.006  | 0.403 ± 0.023         | 0.605 ± 0.026      |
| HSC-CQR simple       | 0.889 ± 0.001 | 0.864 ± 0.009       | 0.022 ± 0.003 | 0.067 ± 0.036         | 0.855 ± 0.006  | 0.407 ± 0.024         | 0.603 ± 0.025      |
| HSC                  | 0.897 ± 0.006 | 0.864 ± 0.027       | 0.029 ± 0.002 | 0.111 ± 0.022         | 0.848 ± 0.005  | 0.438 ± 0.043         | 0.696 ± 0.048      |
| HSC simple           | 0.905 ± 0.001 | 0.888 ± 0.006       | 0.027 ± 0.000 | 0.072 ± 0.018         | 0.859 ± 0.004  | 0.460 ± 0.020         | 0.695 ± 0.043      |
| CQR                  | 0.861 ± 0.001 | 0.859 ± 0.001       | 0.060 ± 0.004 | 0.418 ± 0.029         | 0.782 ± 0.012  | 0.376 ± 0.024         | 0.613 ± 0.031      |
| Self-CQR             | 0.893 ± 0.003 | 0.852 ± 0.004       | 0.022 ± 0.002 | 0.069 ± 0.028         | 0.858 ± 0.005  | 0.426 ± 0.019         | 0.617 ± 0.027      |
| ACI-CQR              | 0.880 ± 0.011 | 0.861 ± 0.003       | 0.035 ± 0.017 | 0.209 ± 0.178         | 0.830 ± 0.036  | 0.399 ± 0.008         | 0.608 ± 0.025      |
| TQA-B-CQR            | 0.869 ± 0.004 | 0.866 ± 0.003       | 0.056 ± 0.003 | 0.374 ± 0.026         | 0.788 ± 0.009  | 0.376 ± 0.020         | 0.609 ± 0.025      |
| GHCP-CQR             | 0.869 ± 0.001 | 0.864 ± 0.005       | 0.056 ± 0.004 | 0.366 ± 0.019         | 0.790 ± 0.012  | 0.382 ± 0.024         | 0.611 ± 0.030      |
| QShrink-CQR          | 0.888 ± 0.003 | 0.870 ± 0.004       | 0.026 ± 0.006 | 0.112 ± 0.062         | 0.848 ± 0.013  | 0.404 ± 0.027         | 0.603 ± 0.025      |
| QR-LGBM              | 0.838 ± 0.003 | 0.832 ± 0.007       | 0.072 ± 0.004 | 0.555 ± 0.028         | 0.756 ± 0.013  | 0.357 ± 0.020         | 0.623 ± 0.035      |
| MLP-QR               | 0.855 ± 0.007 | 0.836 ± 0.021       | 0.061 ± 0.005 | 0.432 ± 0.042         | 0.776 ± 0.015  | 0.373 ± 0.010         | 0.623 ± 0.034      |
| MLP-Gauss            | 0.894 ± 0.011 | 0.892 ± 0.018       | 0.047 ± 0.003 | 0.231 ± 0.060         | 0.819 ± 0.013  | 0.436 ± 0.014         | 0.663 ± 0.047      |
| CQR (MLP)            | 0.861 ± 0.007 | 0.855 ± 0.014       | 0.058 ± 0.003 | 0.406 ± 0.029         | 0.782 ± 0.012  | 0.379 ± 0.012         | 0.623 ± 0.035      |
| HSC-CQR (MLP)        | 0.890 ± 0.001 | 0.854 ± 0.020       | 0.023 ± 0.004 | 0.065 ± 0.034         | 0.856 ± 0.005  | 0.417 ± 0.023         | 0.614 ± 0.026      |
| ACI                  | 0.896 ± 0.008 | 0.856 ± 0.015       | 0.041 ± 0.014 | 0.157 ± 0.141         | 0.835 ± 0.036  | 0.419 ± 0.012         | 0.676 ± 0.048      |
| Self-CP              | 0.905 ± 0.002 | 0.892 ± 0.001       | 0.027 ± 0.000 | 0.078 ± 0.010         | 0.861 ± 0.002  | 0.470 ± 0.020         | 0.700 ± 0.042      |
| SCP-stage            | 0.837 ± 0.006 | 0.840 ± 0.008       | 0.112 ± 0.001 | 0.420 ± 0.024         | 0.634 ± 0.018  | 0.395 ± 0.011         | 0.681 ± 0.049      |
| SCP                  | 0.837 ± 0.006 | 0.808 ± 0.006       | 0.111 ± 0.001 | 0.423 ± 0.021         | 0.635 ± 0.017  | 0.394 ± 0.012         | 0.683 ± 0.044      |
| Naive+SCP            | 0.824 ± 0.016 | 0.842 ± 0.012       | 0.123 ± 0.011 | 0.474 ± 0.043         | 0.605 ± 0.034  | 0.490 ± 0.008         | 0.958 ± 0.080      |
| Raw-SCP              | 0.963 ± 0.016 | 0.951 ± 0.023       | 0.103 ± 0.005 | 0.075 ± 0.036         | 0.898 ± 0.060  | 1.901 ± 0.389         | 2.087 ± 0.278      |
| HSC -stage           | 0.897 ± 0.004 | 0.850 ± 0.020       | 0.029 ± 0.003 | 0.108 ± 0.018         | 0.847 ± 0.006  | 0.436 ± 0.036         | 0.698 ± 0.049      |
| HSC -kNN             | 0.906 ± 0.001 | 0.897 ± 0.006       | 0.029 ± 0.002 | 0.071 ± 0.016         | 0.858 ± 0.003  | 0.459 ± 0.023         | 0.690 ± 0.048      |
| HSC -shrink          | 0.771 ± 0.025 | 0.764 ± 0.021       | 0.152 ± 0.021 | 0.657 ± 0.063         | 0.570 ± 0.025  | 0.292 ± 0.036         | 0.774 ± 0.069      |
| HSC-CQR -stage       | 0.887 ± 0.000 | 0.860 ± 0.006       | 0.023 ± 0.002 | 0.079 ± 0.024         | 0.853 ± 0.004  | 0.403 ± 0.022         | 0.604 ± 0.026      |
| HSC-CQR -kNN         | 0.890 ± 0.001 | 0.871 ± 0.002       | 0.022 ± 0.002 | 0.065 ± 0.030         | 0.856 ± 0.005  | 0.408 ± 0.024         | 0.602 ± 0.027      |
| HSC-CQR -shrink      | 0.856 ± 0.004 | 0.851 ± 0.006       | 0.062 ± 0.004 | 0.441 ± 0.059         | 0.775 ± 0.012  | 0.369 ± 0.018         | 0.614 ± 0.032      |
| HSC-CQR fixed-κ      | 0.892 ± 0.001 | 0.868 ± 0.006       | 0.019 ± 0.001 | 0.043 ± 0.014         | 0.863 ± 0.003  | 0.408 ± 0.025         | 0.603 ± 0.027      |


**Table S13. BDG2 → BDG2 without weather features (reference; 3 seeds).**

| Method               | Coverage      | Coverage (week 1)   | MACD          | Under-covered share   | P10 coverage   | Rel. width (median)   | Rel. IS (median)   |
|:---------------------|:--------------|:--------------------|:--------------|:----------------------|:---------------|:----------------------|:-------------------|
| HSC-CQR recency      | 0.896 ± 0.002 | 0.897 ± 0.004       | 0.012 ± 0.001 | 0.001 ± 0.002         | 0.878 ± 0.003  | 0.406 ± 0.021         | 0.577 ± 0.025      |
| HSC-SSC-CQR          | 0.900 ± 0.002 | 0.904 ± 0.004       | 0.015 ± 0.001 | 0.005 ± 0.006         | 0.877 ± 0.003  | 0.407 ± 0.016         | 0.577 ± 0.023      |
| SSC-CQR              | 0.901 ± 0.003 | 0.898 ± 0.005       | 0.031 ± 0.002 | 0.097 ± 0.002         | 0.851 ± 0.001  | 0.401 ± 0.014         | 0.578 ± 0.025      |
| HSC-CQR simple (cov) | 0.895 ± 0.002 | 0.897 ± 0.003       | 0.015 ± 0.000 | 0.013 ± 0.002         | 0.871 ± 0.002  | 0.403 ± 0.015         | 0.576 ± 0.023      |
| QShrink-CQR (cov)    | 0.896 ± 0.003 | 0.894 ± 0.000       | 0.015 ± 0.001 | 0.009 ± 0.006         | 0.872 ± 0.004  | 0.403 ± 0.015         | 0.577 ± 0.023      |
| ACI-CQR (cov)        | 0.900 ± 0.000 | 0.898 ± 0.002       | 0.004 ± 0.000 | 0.000 ± 0.000         | 0.894 ± 0.001  | 0.877 ± 0.082         | 1.056 ± 0.105      |
| HSC-CQR              | 0.893 ± 0.004 | 0.887 ± 0.006       | 0.017 ± 0.000 | 0.029 ± 0.006         | 0.866 ± 0.004  | 0.395 ± 0.016         | 0.575 ± 0.025      |
| HSC-CQR simple       | 0.896 ± 0.003 | 0.896 ± 0.003       | 0.017 ± 0.001 | 0.022 ± 0.010         | 0.869 ± 0.004  | 0.399 ± 0.015         | 0.574 ± 0.025      |
| HSC                  | 0.902 ± 0.002 | 0.883 ± 0.012       | 0.029 ± 0.002 | 0.078 ± 0.013         | 0.857 ± 0.001  | 0.429 ± 0.024         | 0.652 ± 0.019      |
| HSC simple           | 0.910 ± 0.002 | 0.905 ± 0.002       | 0.028 ± 0.001 | 0.049 ± 0.006         | 0.865 ± 0.002  | 0.453 ± 0.033         | 0.654 ± 0.009      |
| CQR                  | 0.894 ± 0.003 | 0.892 ± 0.004       | 0.037 ± 0.001 | 0.174 ± 0.018         | 0.835 ± 0.007  | 0.391 ± 0.012         | 0.574 ± 0.026      |
| Self-CQR             | 0.888 ± 0.003 | 0.860 ± 0.005       | 0.022 ± 0.002 | 0.074 ± 0.008         | 0.857 ± 0.001  | 0.404 ± 0.015         | 0.583 ± 0.021      |
| ACI-CQR              | 0.897 ± 0.002 | 0.892 ± 0.003       | 0.020 ± 0.001 | 0.042 ± 0.005         | 0.865 ± 0.002  | 0.397 ± 0.020         | 0.573 ± 0.025      |
| TQA-B-CQR            | 0.896 ± 0.002 | 0.896 ± 0.003       | 0.038 ± 0.002 | 0.177 ± 0.020         | 0.836 ± 0.002  | 0.394 ± 0.012         | 0.573 ± 0.022      |
| GHCP-CQR             | 0.896 ± 0.003 | 0.899 ± 0.003       | 0.037 ± 0.001 | 0.157 ± 0.006         | 0.837 ± 0.006  | 0.393 ± 0.012         | 0.574 ± 0.026      |
| QShrink-CQR          | 0.898 ± 0.004 | 0.894 ± 0.003       | 0.021 ± 0.001 | 0.036 ± 0.010         | 0.867 ± 0.004  | 0.401 ± 0.021         | 0.575 ± 0.026      |
| QR-LGBM              | 0.873 ± 0.012 | 0.879 ± 0.009       | 0.043 ± 0.005 | 0.278 ± 0.087         | 0.815 ± 0.012  | 0.373 ± 0.007         | 0.576 ± 0.025      |
| MLP-QR               | 0.900 ± 0.006 | 0.896 ± 0.011       | 0.036 ± 0.004 | 0.126 ± 0.050         | 0.845 ± 0.012  | 0.400 ± 0.006         | 0.564 ± 0.023      |
| MLP-Gauss            | 0.929 ± 0.009 | 0.934 ± 0.014       | 0.042 ± 0.003 | 0.038 ± 0.023         | 0.873 ± 0.015  | 0.463 ± 0.047         | 0.613 ± 0.044      |
| CQR (MLP)            | 0.895 ± 0.005 | 0.897 ± 0.011       | 0.035 ± 0.004 | 0.148 ± 0.050         | 0.841 ± 0.010  | 0.395 ± 0.007         | 0.562 ± 0.023      |
| HSC-CQR (MLP)        | 0.898 ± 0.002 | 0.893 ± 0.009       | 0.020 ± 0.003 | 0.041 ± 0.022         | 0.867 ± 0.004  | 0.399 ± 0.012         | 0.562 ± 0.024      |
| ACI                  | 0.915 ± 0.001 | 0.891 ± 0.009       | 0.044 ± 0.001 | 0.125 ± 0.002         | 0.847 ± 0.001  | 0.444 ± 0.028         | 0.639 ± 0.021      |
| Self-CP              | 0.905 ± 0.001 | 0.898 ± 0.002       | 0.027 ± 0.001 | 0.066 ± 0.010         | 0.861 ± 0.001  | 0.457 ± 0.031         | 0.664 ± 0.017      |
| SCP-stage            | 0.881 ± 0.006 | 0.883 ± 0.011       | 0.094 ± 0.006 | 0.289 ± 0.021         | 0.702 ± 0.024  | 0.466 ± 0.024         | 0.642 ± 0.020      |
| SCP                  | 0.882 ± 0.006 | 0.861 ± 0.006       | 0.093 ± 0.006 | 0.291 ± 0.019         | 0.704 ± 0.026  | 0.466 ± 0.025         | 0.643 ± 0.015      |
| Mondrian-usage       | 0.881 ± 0.009 | 0.880 ± 0.011       | 0.093 ± 0.005 | 0.299 ± 0.019         | 0.706 ± 0.008  | 0.430 ± 0.030         | 0.669 ± 0.031      |
| Naive+SCP            | 0.876 ± 0.006 | 0.884 ± 0.006       | 0.096 ± 0.006 | 0.314 ± 0.010         | 0.692 ± 0.031  | 0.661 ± 0.041         | 0.970 ± 0.053      |
| Raw-SCP              | 0.906 ± 0.031 | 0.892 ± 0.037       | 0.119 ± 0.019 | 0.190 ± 0.069         | 0.684 ± 0.153  | 0.744 ± 0.043         | 1.117 ± 0.016      |
| HSC -stage           | 0.900 ± 0.002 | 0.866 ± 0.012       | 0.028 ± 0.002 | 0.078 ± 0.009         | 0.855 ± 0.002  | 0.428 ± 0.025         | 0.657 ± 0.017      |
| HSC -kNN             | 0.911 ± 0.002 | 0.918 ± 0.000       | 0.029 ± 0.001 | 0.046 ± 0.008         | 0.867 ± 0.003  | 0.458 ± 0.033         | 0.655 ± 0.012      |
| HSC -shrink          | 0.847 ± 0.006 | 0.838 ± 0.017       | 0.091 ± 0.004 | 0.437 ± 0.012         | 0.693 ± 0.020  | 0.375 ± 0.013         | 0.668 ± 0.029      |
| HSC-CQR -stage       | 0.893 ± 0.003 | 0.892 ± 0.006       | 0.017 ± 0.000 | 0.028 ± 0.004         | 0.866 ± 0.003  | 0.394 ± 0.017         | 0.574 ± 0.026      |
| HSC-CQR -kNN         | 0.895 ± 0.004 | 0.893 ± 0.003       | 0.018 ± 0.003 | 0.037 ± 0.018         | 0.867 ± 0.001  | 0.398 ± 0.016         | 0.575 ± 0.025      |
| HSC-CQR -shrink      | 0.888 ± 0.005 | 0.882 ± 0.007       | 0.036 ± 0.001 | 0.182 ± 0.029         | 0.831 ± 0.003  | 0.387 ± 0.010         | 0.574 ± 0.026      |
| HSC-CQR fixed-κ      | 0.895 ± 0.003 | 0.897 ± 0.003       | 0.015 ± 0.000 | 0.016 ± 0.004         | 0.871 ± 0.003  | 0.403 ± 0.015         | 0.575 ± 0.024      |


**Table S14. Robustness conditions on BDG2, all strategies (mean over 3 seeds).**

| perturb         | method               |   mean_cov |   macd |   under_rate |   under_wk1 |   rel_IS |   rel_width |   underprot |   cost20 |
|:----------------|:---------------------|-----------:|-------:|-------------:|------------:|---------:|------------:|------------:|---------:|
| calpool10       | ACI                  |      0.901 |  0.043 |        0.17  |       0.364 |    0.624 |       0.401 |       0.061 |    1.479 |
| calpool10       | ACI-CQR              |      0.889 |  0.026 |        0.101 |       0.353 |    0.558 |       0.379 |       0.055 |    1.415 |
| calpool10       | ACI-CQR (cov)        |      0.9   |  0.004 |        0     |       0.124 |    0.752 |       0.593 |       0.003 |    1.562 |
| calpool10       | CQR                  |      0.883 |  0.039 |        0.216 |       0.362 |    0.56  |       0.375 |       0.076 |    1.418 |
| calpool10       | GHCP-CQR             |      0.911 |  0.036 |        0.087 |       0.115 |    0.557 |       0.411 |       0.047 |    1.419 |
| calpool10       | HSC                  |      0.904 |  0.028 |        0.072 |       0.237 |    0.644 |       0.428 |       0.033 |    1.475 |
| calpool10       | HSC-CQR              |      0.889 |  0.02  |        0.079 |       0.311 |    0.562 |       0.387 |       0.036 |    1.418 |
| calpool10       | HSC-CQR recency      |      0.892 |  0.015 |        0.025 |       0.186 |    0.56  |       0.394 |       0.02  |    1.426 |
| calpool10       | HSC-CQR simple       |      0.89  |  0.02  |        0.062 |       0.213 |    0.56  |       0.388 |       0.036 |    1.418 |
| calpool10       | HSC-CQR simple (cov) |      0.891 |  0.019 |        0.045 |       0.199 |    0.562 |       0.39  |       0.025 |    1.422 |
| calpool10       | HSC-SSC-CQR          |      0.897 |  0.015 |        0.013 |       0.14  |    0.568 |       0.396 |       0.013 |    2.706 |
| calpool10       | MLP-QR               |      0.885 |  0.037 |        0.196 |       0.258 |    0.563 |       0.381 |       0.094 |    1.414 |
| calpool10       | QR-LGBM              |      0.861 |  0.048 |        0.383 |       0.352 |    0.565 |       0.359 |       0.133 |    1.419 |
| calpool10       | QShrink-CQR          |      0.891 |  0.019 |        0.059 |       0.295 |    0.56  |       0.388 |       0.034 |    1.423 |
| calpool10       | QShrink-CQR (cov)    |      0.893 |  0.017 |        0.028 |       0.262 |    0.562 |       0.392 |       0.022 |    1.424 |
| calpool10       | SCP-stage            |      0.846 |  0.111 |        0.395 |       0.378 |    0.627 |       0.385 |       0.286 |    1.556 |
| calpool10       | SSC-CQR              |      0.945 |  0.046 |        0.001 |       0.113 |    0.647 |       0.531 |       0.004 |    1.46  |
| calpool10       | Self-CP              |      0.905 |  0.026 |        0.055 |       0.183 |    0.65  |       0.445 |       0.028 |    1.483 |
| calpool10       | Self-CQR             |      0.889 |  0.021 |        0.07  |       0.354 |    0.573 |       0.395 |       0.025 |    1.437 |
| calpool10       | TQA-B-CQR            |      0.882 |  0.04  |        0.237 |       0.358 |    0.561 |       0.373 |       0.086 |    1.418 |
| calpool25       | ACI                  |      0.913 |  0.046 |        0.116 |       0.266 |    0.624 |       0.433 |       0.05  |    1.484 |
| calpool25       | ACI-CQR              |      0.895 |  0.017 |        0.03  |       0.209 |    0.555 |       0.388 |       0.038 |    1.417 |
| calpool25       | ACI-CQR (cov)        |      0.9   |  0.004 |        0     |       0.082 |    0.9   |       0.759 |       0.003 |    1.711 |
| calpool25       | CQR                  |      0.891 |  0.037 |        0.175 |       0.221 |    0.557 |       0.383 |       0.069 |    1.418 |
| calpool25       | GHCP-CQR             |      0.902 |  0.037 |        0.126 |       0.19  |    0.557 |       0.394 |       0.058 |    1.418 |
| calpool25       | HSC                  |      0.903 |  0.029 |        0.078 |       0.278 |    0.637 |       0.421 |       0.03  |    1.461 |
| calpool25       | HSC-CQR              |      0.893 |  0.017 |        0.032 |       0.229 |    0.554 |       0.388 |       0.036 |    1.413 |
| calpool25       | HSC-CQR recency      |      0.896 |  0.012 |        0.005 |       0.146 |    0.565 |       0.401 |       0.017 |    1.423 |
| calpool25       | HSC-CQR simple       |      0.895 |  0.018 |        0.036 |       0.225 |    0.554 |       0.388 |       0.034 |    1.413 |
| calpool25       | HSC-CQR simple (cov) |      0.895 |  0.015 |        0.018 |       0.196 |    0.561 |       0.394 |       0.024 |    1.415 |
| calpool25       | HSC-SSC-CQR          |      0.898 |  0.015 |        0.007 |       0.136 |    0.566 |       0.398 |       0.012 |    1.63  |
| calpool25       | MLP-QR               |      0.885 |  0.037 |        0.196 |       0.258 |    0.563 |       0.381 |       0.094 |    1.414 |
| calpool25       | QR-LGBM              |      0.861 |  0.048 |        0.383 |       0.352 |    0.565 |       0.359 |       0.133 |    1.419 |
| calpool25       | QShrink-CQR          |      0.898 |  0.02  |        0.03  |       0.199 |    0.552 |       0.393 |       0.033 |    1.417 |
| calpool25       | QShrink-CQR (cov)    |      0.897 |  0.015 |        0.016 |       0.165 |    0.56  |       0.395 |       0.018 |    1.423 |
| calpool25       | SCP-stage            |      0.884 |  0.093 |        0.274 |       0.273 |    0.635 |       0.468 |       0.191 |    1.544 |
| calpool25       | SSC-CQR              |      0.914 |  0.029 |        0.041 |       0.149 |    0.565 |       0.42  |       0.029 |    1.419 |
| calpool25       | Self-CP              |      0.906 |  0.026 |        0.053 |       0.166 |    0.652 |       0.447 |       0.028 |    1.483 |
| calpool25       | Self-CQR             |      0.89  |  0.021 |        0.066 |       0.341 |    0.573 |       0.395 |       0.025 |    1.438 |
| calpool25       | TQA-B-CQR            |      0.892 |  0.038 |        0.178 |       0.213 |    0.56  |       0.385 |       0.066 |    1.419 |
| calpool50       | ACI                  |      0.914 |  0.04  |        0.094 |       0.267 |    0.624 |       0.428 |       0.036 |    1.489 |
| calpool50       | ACI-CQR              |      0.894 |  0.022 |        0.062 |       0.225 |    0.553 |       0.384 |       0.046 |    1.415 |
| calpool50       | ACI-CQR (cov)        |      0.9   |  0.004 |        0     |       0.09  |    0.867 |       0.712 |       0.001 |    1.689 |
| calpool50       | CQR                  |      0.891 |  0.037 |        0.178 |       0.231 |    0.557 |       0.382 |       0.07  |    1.418 |
| calpool50       | GHCP-CQR             |      0.896 |  0.037 |        0.148 |       0.207 |    0.557 |       0.387 |       0.067 |    1.417 |
| calpool50       | HSC                  |      0.901 |  0.027 |        0.066 |       0.289 |    0.642 |       0.417 |       0.029 |    1.461 |
| calpool50       | HSC-CQR              |      0.893 |  0.018 |        0.041 |       0.223 |    0.553 |       0.385 |       0.037 |    1.413 |
| calpool50       | HSC-CQR recency      |      0.896 |  0.012 |        0.005 |       0.138 |    0.565 |       0.401 |       0.012 |    1.425 |
| calpool50       | HSC-CQR simple       |      0.894 |  0.018 |        0.036 |       0.223 |    0.554 |       0.387 |       0.034 |    1.413 |
| calpool50       | HSC-CQR simple (cov) |      0.895 |  0.015 |        0.02  |       0.179 |    0.563 |       0.395 |       0.022 |    1.418 |
| calpool50       | HSC-SSC-CQR          |      0.898 |  0.015 |        0.009 |       0.14  |    0.566 |       0.399 |       0.013 |    1.613 |
| calpool50       | MLP-QR               |      0.885 |  0.037 |        0.196 |       0.258 |    0.563 |       0.381 |       0.094 |    1.414 |
| calpool50       | QR-LGBM              |      0.861 |  0.048 |        0.383 |       0.352 |    0.565 |       0.359 |       0.133 |    1.419 |
| calpool50       | QShrink-CQR          |      0.898 |  0.019 |        0.032 |       0.203 |    0.552 |       0.394 |       0.028 |    1.418 |
| calpool50       | QShrink-CQR (cov)    |      0.896 |  0.015 |        0.017 |       0.159 |    0.561 |       0.395 |       0.018 |    1.425 |
| calpool50       | SCP-stage            |      0.879 |  0.095 |        0.294 |       0.281 |    0.63  |       0.453 |       0.207 |    1.545 |
| calpool50       | SSC-CQR              |      0.904 |  0.029 |        0.076 |       0.192 |    0.559 |       0.403 |       0.041 |    1.416 |
| calpool50       | Self-CP              |      0.906 |  0.026 |        0.054 |       0.171 |    0.652 |       0.447 |       0.026 |    1.483 |
| calpool50       | Self-CQR             |      0.89  |  0.021 |        0.066 |       0.331 |    0.573 |       0.395 |       0.025 |    1.437 |
| calpool50       | TQA-B-CQR            |      0.893 |  0.037 |        0.165 |       0.216 |    0.559 |       0.384 |       0.065 |    1.418 |
| missing20       | ACI                  |      0.909 |  0.047 |        0.179 |       0.296 |    0.65  |       0.444 |       0.067 |    1.508 |
| missing20       | ACI-CQR              |      0.896 |  0.028 |        0.099 |       0.264 |    0.585 |       0.421 |       0.042 |    1.434 |
| missing20       | ACI-CQR (cov)        |      0.9   |  0.006 |        0     |       0.174 |    0.789 |       0.611 |       0.001 |    1.723 |
| missing20       | CQR                  |      0.895 |  0.038 |        0.175 |       0.269 |    0.585 |       0.416 |       0.058 |    1.436 |
| missing20       | GHCP-CQR             |      0.897 |  0.037 |        0.157 |       0.25  |    0.583 |       0.419 |       0.05  |    1.436 |
| missing20       | HSC                  |      0.901 |  0.029 |        0.086 |       0.319 |    0.663 |       0.437 |       0.033 |    1.475 |
| missing20       | HSC-CQR              |      0.895 |  0.019 |        0.04  |       0.274 |    0.585 |       0.416 |       0.028 |    1.431 |
| missing20       | HSC-CQR recency      |      0.899 |  0.012 |        0.007 |       0.175 |    0.589 |       0.431 |       0.012 |    1.442 |
| missing20       | HSC-CQR simple       |      0.898 |  0.018 |        0.033 |       0.246 |    0.585 |       0.42  |       0.025 |    1.431 |
| missing20       | HSC-CQR simple (cov) |      0.898 |  0.016 |        0.018 |       0.227 |    0.586 |       0.425 |       0.021 |    1.432 |
| missing20       | HSC-SSC-CQR          |      0.902 |  0.016 |        0.008 |       0.167 |    0.586 |       0.431 |       0.012 |    1.476 |
| missing20       | MLP-QR               |      0.865 |  0.047 |        0.335 |       0.318 |    0.632 |       0.422 |       0.136 |    1.469 |
| missing20       | QR-LGBM              |      0.87  |  0.044 |        0.302 |       0.381 |    0.589 |       0.395 |       0.097 |    1.436 |
| missing20       | QShrink-CQR          |      0.9   |  0.022 |        0.034 |       0.24  |    0.585 |       0.423 |       0.024 |    1.435 |
| missing20       | QShrink-CQR (cov)    |      0.899 |  0.016 |        0.017 |       0.204 |    0.587 |       0.426 |       0.018 |    1.441 |
| missing20       | SCP-stage            |      0.866 |  0.101 |        0.339 |       0.312 |    0.653 |       0.447 |       0.235 |    1.568 |
| missing20       | SSC-CQR              |      0.906 |  0.031 |        0.075 |       0.228 |    0.586 |       0.433 |       0.041 |    1.434 |
| missing20       | Self-CP              |      0.913 |  0.028 |        0.04  |       0.09  |    0.675 |       0.492 |       0.018 |    1.5   |
| missing20       | Self-CQR             |      0.892 |  0.022 |        0.059 |       0.358 |    0.599 |       0.426 |       0.022 |    1.457 |
| missing20       | TQA-B-CQR            |      0.895 |  0.036 |        0.163 |       0.273 |    0.585 |       0.415 |       0.057 |    1.435 |
| missing40       | ACI                  |      0.902 |  0.053 |        0.24  |       0.302 |    0.671 |       0.457 |       0.099 |    1.525 |
| missing40       | ACI-CQR              |      0.898 |  0.033 |        0.12  |       0.295 |    0.613 |       0.449 |       0.045 |    1.456 |
| missing40       | ACI-CQR (cov)        |      0.903 |  0.011 |        0     |       0.242 |    0.692 |       0.533 |       0.004 |    1.652 |
| missing40       | CQR                  |      0.897 |  0.04  |        0.169 |       0.299 |    0.614 |       0.449 |       0.063 |    1.457 |
| missing40       | GHCP-CQR             |      0.9   |  0.04  |        0.15  |       0.269 |    0.613 |       0.453 |       0.061 |    1.457 |
| missing40       | HSC                  |      0.902 |  0.032 |        0.107 |       0.321 |    0.681 |       0.464 |       0.047 |    1.492 |
| missing40       | HSC-CQR              |      0.899 |  0.023 |        0.054 |       0.325 |    0.611 |       0.45  |       0.029 |    1.453 |
| missing40       | HSC-CQR recency      |      0.903 |  0.016 |        0.009 |       0.217 |    0.612 |       0.465 |       0.016 |    1.462 |
| missing40       | HSC-CQR simple       |      0.901 |  0.023 |        0.047 |       0.279 |    0.612 |       0.454 |       0.028 |    1.453 |
| missing40       | HSC-CQR simple (cov) |      0.902 |  0.02  |        0.024 |       0.256 |    0.611 |       0.456 |       0.021 |    1.453 |
| missing40       | HSC-SSC-CQR          |      0.907 |  0.019 |        0.012 |       0.196 |    0.615 |       0.464 |       0.016 |    1.457 |
| missing40       | MLP-QR               |      0.847 |  0.063 |        0.47  |       0.381 |    0.699 |       0.446 |       0.242 |    1.524 |
| missing40       | QR-LGBM              |      0.874 |  0.044 |        0.287 |       0.403 |    0.616 |       0.428 |       0.099 |    1.457 |
| missing40       | QShrink-CQR          |      0.903 |  0.027 |        0.061 |       0.274 |    0.611 |       0.452 |       0.03  |    1.456 |
| missing40       | QShrink-CQR (cov)    |      0.903 |  0.02  |        0.022 |       0.249 |    0.611 |       0.46  |       0.016 |    1.461 |
| missing40       | SCP-stage            |      0.855 |  0.107 |        0.37  |       0.31  |    0.67  |       0.447 |       0.26  |    1.594 |
| missing40       | SSC-CQR              |      0.91  |  0.034 |        0.079 |       0.254 |    0.617 |       0.464 |       0.042 |    1.456 |
| missing40       | Self-CP              |      0.92  |  0.033 |        0.037 |       0.07  |    0.705 |       0.531 |       0.021 |    1.522 |
| missing40       | Self-CQR             |      0.896 |  0.023 |        0.055 |       0.398 |    0.627 |       0.465 |       0.022 |    1.48  |
| missing40       | TQA-B-CQR            |      0.896 |  0.038 |        0.166 |       0.303 |    0.615 |       0.447 |       0.062 |    1.455 |
| noise15         | ACI                  |      0.858 |  0.042 |        0.281 |       0.841 |    0.94  |       0.622 |       0.054 |    1.657 |
| noise15         | ACI-CQR              |      0.87  |  0.03  |        0.104 |       0.391 |    0.921 |       0.661 |       0.049 |    1.594 |
| noise15         | ACI-CQR (cov)        |      0.897 |  0.003 |        0     |       0.063 |    1.199 |       0.992 |       0     |    1.876 |
| noise15         | CQR                  |      0.859 |  0.041 |        0.307 |       0.401 |    0.925 |       0.641 |       0.113 |    1.597 |
| noise15         | GHCP-CQR             |      0.861 |  0.039 |        0.271 |       0.378 |    0.924 |       0.643 |       0.104 |    1.597 |
| noise15         | HSC                  |      0.88  |  0.025 |        0.103 |       0.823 |    0.934 |       0.673 |       0.014 |    1.609 |
| noise15         | HSC-CQR              |      0.882 |  0.018 |        0.017 |       0.391 |    0.917 |       0.681 |       0.013 |    1.588 |
| noise15         | HSC-CQR recency      |      0.896 |  0.007 |        0.001 |       0.091 |    0.913 |       0.708 |       0     |    1.591 |
| noise15         | HSC-CQR simple       |      0.883 |  0.017 |        0.014 |       0.335 |    0.916 |       0.684 |       0.013 |    1.588 |
| noise15         | HSC-CQR simple (cov) |      0.891 |  0.011 |        0.004 |       0.228 |    0.913 |       0.697 |       0.003 |    1.588 |
| noise15         | HSC-SSC-CQR          |      0.899 |  0.008 |        0     |       0.087 |    0.914 |       0.711 |       0.001 |    1.604 |
| noise15         | MLP-QR               |      0.861 |  0.039 |        0.264 |       0.406 |    0.95  |       0.683 |       0.121 |    1.61  |
| noise15         | QR-LGBM              |      0.846 |  0.054 |        0.519 |       0.519 |    0.935 |       0.619 |       0.188 |    1.603 |
| noise15         | QShrink-CQR          |      0.881 |  0.02  |        0.026 |       0.336 |    0.918 |       0.677 |       0.013 |    1.59  |
| noise15         | QShrink-CQR (cov)    |      0.894 |  0.01  |        0.005 |       0.181 |    0.913 |       0.703 |       0.003 |    1.591 |
| noise15         | SCP-stage            |      0.696 |  0.204 |        1     |       0.864 |    1.093 |       0.447 |       0.906 |    1.784 |
| noise15         | SSC-CQR              |      0.882 |  0.021 |        0.058 |       0.286 |    0.917 |       0.678 |       0.03  |    1.59  |
| noise15         | Self-CP              |      0.907 |  0.019 |        0.02  |       0.096 |    0.938 |       0.732 |       0.003 |    1.616 |
| noise15         | Self-CQR             |      0.902 |  0.01  |        0.001 |       0.087 |    0.918 |       0.725 |       0.001 |    1.598 |
| noise15         | TQA-B-CQR            |      0.856 |  0.044 |        0.357 |       0.44  |    0.929 |       0.634 |       0.129 |    1.598 |
| noise5          | ACI                  |      0.904 |  0.038 |        0.142 |       0.307 |    0.66  |       0.446 |       0.046 |    1.513 |
| noise5          | ACI-CQR              |      0.886 |  0.02  |        0.083 |       0.225 |    0.611 |       0.438 |       0.049 |    1.443 |
| noise5          | ACI-CQR (cov)        |      0.899 |  0.003 |        0     |       0.07  |    0.95  |       0.799 |       0.001 |    1.796 |
| noise5          | CQR                  |      0.879 |  0.029 |        0.169 |       0.233 |    0.612 |       0.43  |       0.072 |    1.444 |
| noise5          | GHCP-CQR             |      0.882 |  0.028 |        0.154 |       0.215 |    0.611 |       0.433 |       0.067 |    1.444 |
| noise5          | HSC                  |      0.895 |  0.024 |        0.083 |       0.335 |    0.67  |       0.448 |       0.028 |    1.48  |
| noise5          | HSC-CQR              |      0.889 |  0.015 |        0.028 |       0.208 |    0.611 |       0.443 |       0.026 |    1.44  |
| noise5          | HSC-CQR recency      |      0.896 |  0.009 |        0.001 |       0.094 |    0.612 |       0.457 |       0.004 |    1.447 |
| noise5          | HSC-CQR simple       |      0.891 |  0.013 |        0.025 |       0.192 |    0.61  |       0.446 |       0.025 |    1.44  |
| noise5          | HSC-CQR simple (cov) |      0.894 |  0.012 |        0.009 |       0.157 |    0.612 |       0.45  |       0.018 |    1.441 |
| noise5          | HSC-SSC-CQR          |      0.897 |  0.011 |        0.003 |       0.091 |    0.613 |       0.454 |       0.005 |    1.483 |
| noise5          | MLP-QR               |      0.876 |  0.031 |        0.192 |       0.256 |    0.623 |       0.435 |       0.108 |    1.443 |
| noise5          | QR-LGBM              |      0.856 |  0.045 |        0.383 |       0.336 |    0.615 |       0.408 |       0.132 |    1.448 |
| noise5          | QShrink-CQR          |      0.89  |  0.015 |        0.026 |       0.195 |    0.611 |       0.443 |       0.028 |    1.442 |
| noise5          | QShrink-CQR (cov)    |      0.894 |  0.012 |        0.011 |       0.141 |    0.612 |       0.45  |       0.012 |    1.447 |
| noise5          | SCP-stage            |      0.862 |  0.098 |        0.344 |       0.321 |    0.657 |       0.448 |       0.249 |    1.56  |
| noise5          | SSC-CQR              |      0.893 |  0.021 |        0.078 |       0.191 |    0.61  |       0.447 |       0.045 |    1.442 |
| noise5          | Self-CP              |      0.907 |  0.024 |        0.04  |       0.109 |    0.683 |       0.488 |       0.013 |    1.498 |
| noise5          | Self-CQR             |      0.894 |  0.016 |        0.018 |       0.199 |    0.624 |       0.456 |       0.008 |    1.458 |
| noise5          | TQA-B-CQR            |      0.877 |  0.029 |        0.19  |       0.231 |    0.61  |       0.428 |       0.075 |    1.444 |
| shift+40        | ACI                  |      0.897 |  0.035 |        0.15  |       0.275 |    0.728 |       0.461 |       0.133 |    1.574 |
| shift+40        | ACI-CQR              |      0.879 |  0.027 |        0.163 |       0.242 |    0.664 |       0.412 |       0.232 |    1.508 |
| shift+40        | ACI-CQR (cov)        |      0.9   |  0.004 |        0     |       0.1   |    2.122 |       1.901 |       0.007 |    2.321 |
| shift+40        | CQR                  |      0.869 |  0.041 |        0.303 |       0.242 |    0.666 |       0.397 |       0.331 |    1.514 |
| shift+40        | GHCP-CQR             |      0.872 |  0.039 |        0.283 |       0.223 |    0.666 |       0.4   |       0.321 |    1.514 |
| shift+40        | HSC                  |      0.883 |  0.025 |        0.105 |       0.306 |    0.741 |       0.447 |       0.183 |    1.546 |
| shift+40        | HSC-CQR              |      0.882 |  0.021 |        0.065 |       0.26  |    0.665 |       0.417 |       0.191 |    1.501 |
| shift+40        | HSC-CQR recency      |      0.891 |  0.012 |        0.008 |       0.133 |    0.676 |       0.446 |       0.067 |    1.505 |
| shift+40        | HSC-CQR simple       |      0.884 |  0.02  |        0.053 |       0.224 |    0.665 |       0.418 |       0.166 |    1.501 |
| shift+40        | HSC-CQR simple (cov) |      0.886 |  0.017 |        0.028 |       0.198 |    0.67  |       0.427 |       0.141 |    1.501 |
| shift+40        | HSC-SSC-CQR          |      0.891 |  0.014 |        0.012 |       0.138 |    0.672 |       0.439 |       0.097 |    1.664 |
| shift+40        | MLP-QR               |      0.867 |  0.043 |        0.314 |       0.258 |    0.668 |       0.389 |       0.337 |    1.509 |
| shift+40        | QR-LGBM              |      0.845 |  0.058 |        0.502 |       0.352 |    0.677 |       0.376 |       0.509 |    1.525 |
| shift+40        | QShrink-CQR          |      0.884 |  0.022 |        0.074 |       0.217 |    0.665 |       0.419 |       0.183 |    1.504 |
| shift+40        | QShrink-CQR (cov)    |      0.888 |  0.017 |        0.02  |       0.181 |    0.671 |       0.43  |       0.129 |    1.506 |
| shift+40        | SCP-stage            |      0.849 |  0.092 |        0.383 |       0.292 |    0.727 |       0.436 |       0.398 |    1.642 |
| shift+40        | SSC-CQR              |      0.881 |  0.03  |        0.182 |       0.215 |    0.669 |       0.413 |       0.25  |    1.507 |
| shift+40        | Self-CP              |      0.891 |  0.024 |        0.082 |       0.173 |    0.756 |       0.48  |       0.162 |    1.563 |
| shift+40        | Self-CQR             |      0.883 |  0.022 |        0.079 |       0.336 |    0.68  |       0.441 |       0.15  |    1.518 |
| shift+40        | TQA-B-CQR            |      0.873 |  0.04  |        0.295 |       0.22  |    0.673 |       0.401 |       0.311 |    1.514 |
| shift-40        | ACI                  |      0.882 |  0.029 |        0.179 |       0.275 |    0.854 |       0.505 |       0.011 |    1.565 |
| shift-40        | ACI-CQR              |      0.882 |  0.024 |        0.109 |       0.242 |    0.748 |       0.488 |       0.005 |    1.505 |
| shift-40        | ACI-CQR (cov)        |      0.901 |  0.005 |        0     |       0.1   |    2.222 |       1.985 |       0     |    2.355 |
| shift-40        | CQR                  |      0.869 |  0.039 |        0.286 |       0.242 |    0.75  |       0.482 |       0.009 |    1.502 |
| shift-40        | GHCP-CQR             |      0.872 |  0.037 |        0.262 |       0.223 |    0.749 |       0.486 |       0.009 |    1.502 |
| shift-40        | HSC                  |      0.866 |  0.036 |        0.242 |       0.306 |    0.875 |       0.49  |       0.008 |    1.517 |
| shift-40        | HSC-CQR              |      0.884 |  0.019 |        0.042 |       0.26  |    0.749 |       0.494 |       0.004 |    1.504 |
| shift-40        | HSC-CQR recency      |      0.896 |  0.011 |        0.012 |       0.133 |    0.755 |       0.513 |       0     |    1.523 |
| shift-40        | HSC-CQR simple       |      0.887 |  0.017 |        0.036 |       0.224 |    0.751 |       0.499 |       0.004 |    1.504 |
| shift-40        | HSC-CQR simple (cov) |      0.889 |  0.016 |        0.03  |       0.198 |    0.751 |       0.505 |       0.003 |    1.509 |
| shift-40        | HSC-SSC-CQR          |      0.896 |  0.013 |        0.014 |       0.138 |    0.756 |       0.513 |       0.001 |    1.768 |
| shift-40        | MLP-QR               |      0.881 |  0.035 |        0.195 |       0.258 |    0.723 |       0.47  |       0.017 |    1.48  |
| shift-40        | QR-LGBM              |      0.841 |  0.06  |        0.542 |       0.352 |    0.762 |       0.46  |       0.016 |    1.499 |
| shift-40        | QShrink-CQR          |      0.886 |  0.019 |        0.059 |       0.217 |    0.751 |       0.498 |       0.004 |    1.508 |
| shift-40        | QShrink-CQR (cov)    |      0.89  |  0.016 |        0.024 |       0.181 |    0.751 |       0.503 |       0.001 |    1.519 |
| shift-40        | SCP-stage            |      0.809 |  0.106 |        0.534 |       0.292 |    0.883 |       0.465 |       0.154 |    1.57  |
| shift-40        | SSC-CQR              |      0.884 |  0.029 |        0.148 |       0.215 |    0.753 |       0.498 |       0.007 |    1.505 |
| shift-40        | Self-CP              |      0.877 |  0.032 |        0.19  |       0.173 |    0.88  |       0.531 |       0.003 |    1.552 |
| shift-40        | Self-CQR             |      0.887 |  0.023 |        0.086 |       0.336 |    0.762 |       0.511 |       0.003 |    1.539 |
| shift-40        | TQA-B-CQR            |      0.882 |  0.035 |        0.22  |       0.22  |    0.76  |       0.489 |       0.007 |    1.509 |
| weak-forecaster | ACI                  |      0.912 |  0.048 |        0.158 |       0.262 |    0.652 |       0.462 |       0.074 |    1.512 |
| weak-forecaster | ACI-CQR              |      0.899 |  0.026 |        0.071 |       0.241 |    0.59  |       0.425 |       0.055 |    1.456 |
| weak-forecaster | ACI-CQR (cov)        |      0.901 |  0.005 |        0     |       0.083 |    0.997 |       0.802 |       0.003 |    1.88  |
| weak-forecaster | CQR                  |      0.89  |  0.052 |        0.25  |       0.254 |    0.592 |       0.42  |       0.125 |    1.466 |
| weak-forecaster | GHCP-CQR             |      0.893 |  0.052 |        0.231 |       0.242 |    0.592 |       0.423 |       0.119 |    1.466 |
| weak-forecaster | HSC                  |      0.9   |  0.028 |        0.083 |       0.285 |    0.664 |       0.442 |       0.049 |    1.484 |
| weak-forecaster | HSC-CQR              |      0.894 |  0.021 |        0.054 |       0.257 |    0.593 |       0.423 |       0.051 |    1.453 |
| weak-forecaster | HSC-CQR recency      |      0.899 |  0.013 |        0.007 |       0.136 |    0.591 |       0.434 |       0.016 |    1.462 |
| weak-forecaster | HSC-CQR simple       |      0.898 |  0.021 |        0.043 |       0.215 |    0.593 |       0.425 |       0.042 |    1.453 |
| weak-forecaster | HSC-CQR simple (cov) |      0.898 |  0.018 |        0.028 |       0.166 |    0.593 |       0.428 |       0.033 |    1.458 |
| weak-forecaster | HSC-SSC-CQR          |      0.902 |  0.018 |        0.018 |       0.099 |    0.597 |       0.436 |       0.016 |    2.468 |
| weak-forecaster | QR-LGBM              |      0.849 |  0.067 |        0.482 |       0.433 |    0.599 |       0.382 |       0.219 |    1.47  |
| weak-forecaster | QShrink-CQR          |      0.901 |  0.022 |        0.037 |       0.188 |    0.591 |       0.428 |       0.034 |    1.46  |
| weak-forecaster | QShrink-CQR (cov)    |      0.899 |  0.018 |        0.028 |       0.155 |    0.593 |       0.432 |       0.026 |    1.465 |
| weak-forecaster | SCP-stage            |      0.882 |  0.092 |        0.286 |       0.27  |    0.655 |       0.482 |       0.223 |    1.573 |
| weak-forecaster | SSC-CQR              |      0.9   |  0.041 |        0.161 |       0.208 |    0.595 |       0.433 |       0.086 |    1.46  |
| weak-forecaster | Self-CP              |      0.904 |  0.027 |        0.055 |       0.175 |    0.683 |       0.469 |       0.045 |    1.506 |
| weak-forecaster | Self-CQR             |      0.893 |  0.022 |        0.076 |       0.304 |    0.602 |       0.429 |       0.037 |    1.474 |
| weak-forecaster | TQA-B-CQR            |      0.894 |  0.049 |        0.224 |       0.235 |    0.589 |       0.425 |       0.112 |    1.462 |


**Table S15. Parameters selected by leave-one-building-out on calibration buildings, per run.**

| Run | κ recency (cov) | κ simple (cov) | κ simple (IS) | λ QShrink (cov) | γ ACI-CQR | γ ACI-CQR (cov) |
|:--|--:|--:|--:|--:|--:|--:|
| lso_BDG2_f0 | 48.0 | 96.0 | 336.0 | 96.0 | 0.001 | 0.01 |
| lso_BDG2_f1 | 48.0 | 168.0 | 672.0 | 96.0 | 0.001 | 0.01 |
| lso_BDG2_f2 | 48.0 | 96.0 | 336.0 | 48.0 | 0.0005 | 0.01 |
| lso_BDG2_f3 | 48.0 | 168.0 | 336.0 | 168.0 | 0.0005 | 0.01 |
| lso_BDG2_f4 | 48.0 | 96.0 | 336.0 | 96.0 | 0.001 | 0.01 |
| main_BDG2_s0_a0.1 | 48.0 | 96.0 | 336.0 | 96.0 | 0.001 | 0.01 |
| main_BDG2_s1_a0.1 | 48.0 | 168.0 | 336.0 | 168.0 | 0.0005 | 0.01 |
| main_BDG2_s2_a0.1 | 48.0 | 168.0 | 336.0 | 168.0 | 0.0005 | 0.01 |
| main_BDG2_s3_a0.1 | 48.0 | 168.0 | 336.0 | 168.0 | 0.0005 | 0.01 |
| main_BDG2_s4_a0.1 | 48.0 | 168.0 | 336.0 | 96.0 | 0.001 | 0.01 |
| main_UCI_s0_a0.1 | 48.0 | 96.0 | 336.0 | 48.0 | 0.002 | 0.01 |
| main_UCI_s1_a0.1 | 48.0 | 96.0 | 168.0 | 96.0 | 0.0005 | 0.01 |
| main_UCI_s2_a0.1 | 24.0 | 96.0 | 336.0 | 96.0 | 0.0005 | 0.01 |
| main_UCI_s3_a0.1 | 24.0 | 48.0 | 168.0 | 96.0 | 0.0002 | 0.01 |
| main_UCI_s4_a0.1 | 24.0 | 96.0 | 672.0 | 96.0 | 0.001 | 0.01 |
| xds_BDG2toBDG2_s0 | 48.0 | 96.0 | 336.0 | 96.0 | 0.001 | 0.01 |
| xds_BDG2toBDG2_s1 | 48.0 | 168.0 | 336.0 | 168.0 | 0.001 | 0.01 |
| xds_BDG2toBDG2_s2 | 96.0 | 168.0 | 336.0 | 168.0 | 0.001 | 0.01 |
| xds_BDG2toUCI_s0 | 48.0 | 96.0 | 336.0 | 96.0 | 0.001 | 0.01 |
| xds_BDG2toUCI_s1 | 48.0 | 168.0 | 336.0 | 168.0 | 0.001 | 0.01 |
| xds_BDG2toUCI_s2 | 96.0 | 168.0 | 336.0 | 168.0 | 0.001 | 0.01 |
| xds_UCItoBDG2_s0 | 48.0 | 96.0 | 336.0 | 48.0 | 0.002 | 0.01 |
| xds_UCItoBDG2_s1 | 48.0 | 96.0 | 168.0 | 96.0 | 0.0005 | 0.01 |
| xds_UCItoBDG2_s2 | 24.0 | 96.0 | 336.0 | 96.0 | 0.0005 | 0.01 |

# S6. Additional figures

![**Fig. S1.** Robustness on BDG2 (MACD and under-covered share).](figures/Fig7_robustness.png){width=16cm}

![**Fig. S2.** Generalisation (MACD and median relative interval score).](figures/Fig8_generalisation.png){width=16cm}

![**Fig. S3.** Sensitivity of the stage-matched, similarity-localised variant to κ and K.](figures/Fig9_sensitivity.png){width=16cm}

![**Fig. S4.** Mean coverage and median relative interval score by days of own history.](figures/Fig3_stage_curves.png){width=16cm}

# S7. Analysis protocol (as committed, including addenda)

## Pre-registered research design (written before any target-building result was inspected)

Date: 2026-11-15. Only a pipeline smoke test (reduced data) had been run when this file was written;
any change after this point is logged in CHANGELOG.md with its justification.

## Problem
Day-ahead (24 h) hourly electricity forecasts with prediction intervals are needed for a building
from the first days after it is metered (cold start). A global model trained on other buildings
gives point forecasts; the question is how to calibrate intervals so that **each** new building
receives intervals with close-to-nominal coverage, with as little width as possible, from day 1.

## Hypothesis
H0 (main): Pooled split-conformal calibration attains near-nominal *marginal* coverage on new
buildings but leaves a large dispersion of *per-building* coverage, most severely in the first
week; a hierarchical-shrinkage calibration (HSC) that starts from a similarity-localised,
onboarding-stage-matched population score distribution and shrinks toward the building's own
accumulating scores (pseudo-count κ) reduces per-building miscalibration and the interval score
without any target-building tuning.

## Research questions → experiments
| RQ | Question | Experiment | Primary metric |
|---|---|---|---|
| RQ1 | How reliable are standard interval methods per building during onboarding? | E1 main evaluation (BDG2, UCI; 5 seeds) | MACD, under-coverage rate, P10 coverage |
| RQ2 | Does HSC improve per-building reliability and interval score over strong baselines? | E2 baseline comparison + paired tests | rel. interval score (IS), MACD |
| RQ3 | Which HSC components matter? | E3 ablation (−stage matching, −kNN prior, −shrinkage, fixed κ, combinations) | IS, MACD |
| RQ4 | Is HSC robust to meter noise, missing data, abrupt load changes, small calibration pools, weaker forecasters? | E4 robustness | IS, MACD, coverage |
| RQ5 | Does it generalise to unseen sites and to another dataset/country? | E5 leave-site-out (BDG2), cross-dataset (BDG2↔UCI) | IS, MACD |
| — | Cost? | E6 efficiency: tuning time, per-target-day time, memory | seconds, MB |
| — | Sensitivity to κ, K, α | E7 | IS, MACD vs. parameter |
| — | Where does it fail? | E8 error analysis by usage, site, volatility, stage | per-building coverage |

## Pre-specified choices
* Nominal level 90 % (α = 0.1) main; α ∈ {0.05, 0.2} in E7.
* Seeds: 0,1,2,3,4 (partition, onboarding dates, model seeds). Fixed before results.
* Onboarding window: 56 daily forecasts per target building.
* Tuning objective for HSC (κ, K) and ACI (γ): mean normalised interval score on calibration
  buildings, leave-one-building-out. Grids: κ ∈ {0,24,48,96,168,336,672,1344,∞} (hours of pseudo-
  observations), K ∈ {10,25,50,100,all}, γ ∈ {5e-4,1e-3,2e-3,5e-3,1e-2}.
* Primary endpoints: per-building rel. interval score (lower = better) and |coverage − 0.9|.
* Statistics: unit = target building; Wilcoxon signed-rank (paired, two-sided) HSC vs. each baseline,
  Holm correction across baselines; effect size = matched-pairs rank-biserial r; 95 % CIs by site-
  cluster bootstrap (BDG2) / building bootstrap (UCI); seed-level mean ± s.d.
* Under-coverage threshold: coverage < 0.85 (5 pp below nominal).

## Baselines
Seasonal-naive + SCP (classical); raw-kWh pooled SCP; normalised pooled SCP; stage-matched SCP;
Mondrian-by-usage SCP; self-only conformal (fallback to pooled); ACI (Gibbs & Candès 2021);
LightGBM quantile regression; CQR (Romano et al. 2019); MLP-Gaussian (NLL); MLP quantile regression;
HSC on CQR scores (variant).

---
## Addendum A (2026-11-20, review cycle 1) — written BEFORE any of the following was implemented or run

Context: Reviewer #1 showed, and the author confirmed from results/raw_results.csv.gz, that (i) no shrinkage
variant improves reliability in the first week (BDG2 under-covered share, week 1: HSC-CQR 24.5 %, CQR 23.8 %),
(ii) the interval-score tuning objective selects larger κ than per-building reliability favours (fixed κ = 168 h
beats tuned κ on MACD), (iii) TQA-B used the maximum budget over *target* buildings to scale λ (fairness bug),
(iv) ACI set the radius to the grid cap whenever α_h ≤ 0. The original pre-registration file was committed with
the code (commit e9ca94d) and is an internal protocol, not an external registration; the manuscript will say so
and list all deviations.

### New hypotheses and fixed designs
H-A (objective mismatch). Selecting κ by leave-one-building-out *per-building coverage deviation*
(LOBO-MACD on calibration buildings) instead of the interval score yields lower target MACD than IS-tuning.
Fairness: the same objective is also applied to QShrink-CQR (λ) and ACI-CQR (γ). Variants:
"HSC-CQR simple (cov)", "QShrink-CQR (cov)", "ACI-CQR (cov)".

H-B (scale before quantile). A building's error *scale* can be estimated from far fewer own scores than its
90 % tail quantile. Stage-wise studentised conformal calibration ("SSC-CQR"): each CQR score is divided by the
building's running shrunk scale ratio r_{b,h} = σ̂_{b,h}/σ0, σ̂_{b,h} = (κ_s σ0 + Σ own |abs residual|/s)/(κ_s + n_{b,h})
using only stages < h; the radius is the (1−α) quantile of the building-weighted pooled CDF of studentised
calibration scores at the *exact* stage h, with a point mass 1/(M+1) at +∞ for the new building
(Dunn et al. pooled-CDF construction); interval [q̂lo − q r s, q̂hi + q r s]. κ_s fixed a priori at 24
(one day of hourly scores; not tuned, so that the stage-wise exchangeability argument is not affected by tuning);
σ0 = building-weighted mean abs residual of calibration buildings (leave-one-out for calibration buildings).
Prediction: lower under-covered share than CQR and HSC-CQR in week 1 (days 2–7) and overall.
Combination: "HSC-SSC-CQR" = HSC simple (κ by LOBO-MACD) applied to the studentised scores.

H-C (recency). Exponential down-weighting of own scores (factor 0.95 per day, half-life ≈ 13.5 days, fixed a
priori) reduces under-coverage after level shifts. Variant "HSC-CQR recency" (simple, κ by LOBO-MACD).

### Fixes to baselines
* TQA-B-CQR: λ computed from the calibration buildings' own budgets (each ranked among the others), never
  from target buildings.
* ACI / ACI-CQR: for α_h ≤ 0 the radius is the largest observed calibration score (finite surrogate of the
  infinite interval) instead of the 500·s grid cap; the frequency of α_h ≤ 0 events is logged.
* α ∈ {0.05, 0.2}: all CQR-based methods are now evaluated too (quantile models trained at α = 0.1; conformal
  calibration corrects the level; documented as a deviation).

### New outcome measures (operational, pre-specified)
* Upper- and lower-tail exceedance rates per building (nominal 5 % each).
* Capacity-headroom case study: an operator offers headroom below a contracted limit equal to (limit − U) and
  pays a penalty for violations (y − U)+. Relative cost per building = mean(U)/ȳ + ρ·mean((y − U)+)/ȳ for
  penalty ratios ρ ∈ {10, 20, 40} (all three reported); share of buildings with
  upper-tail exceedance > 10 % (twice nominal) = "under-protected buildings".
* Day-block standard error of each building's coverage (daily coverage values, s.d./√days) → sampling floor of MACD
  E|N(0,SE²)| = SE·√(2/π), replacing the independence-based floor.
* Statistics: additionally a site-level paired test for BDG2 (Wilcoxon on site means, n = 10 sites) and a
  sensitivity analysis excluding the largest site (Rat).

All results, favourable or not, will be reported; no variant will be dropped after seeing results.

### Addendum A.1 (2026-11-20 21:47 UTC; only the BDG2 seed-0 pipeline check had been inspected)
Decision rule for the configuration recommended in the manuscript, fixed before the full rerun:
among all CQR-score calibration strategies, the recommended one is the strategy with the lowest
under-covered share (averaged over the BDG2 and UCI main experiments, 5 seeds each) among those whose median
relative interval score is at most 2 % above that of pooled CQR on both datasets (a sharpness constraint:
reliability may not be bought with wider intervals). Strategies violating the constraint (e.g. aggressive
online level control) are reported on the reliability–sharpness frontier but not recommended. The paired
tests are reported for every Addendum-A variant regardless of which one is recommended.

