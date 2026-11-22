---
title: "Supplementary material: Two-timescale conformal calibration for week-by-week reliable day-ahead load intervals of newly enrolled buildings"
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
* **ACI** : adaptive conformal inference on top of the SCP-stage distribution, $\alpha_{h+1}=\alpha_h+\gamma\sum_j(\alpha-\mathrm{err}_{h,j})$, with $\gamma$ chosen by leave-one-building-out on calibration buildings from $\{0,10^{-4},2\!\times\!10^{-4},5\!\times\!10^{-4},10^{-3},2\!\times\!10^{-3},5\!\times\!10^{-3},10^{-2}\}$ (the three smallest values were added after a code audit showed that the pre-registered grid's lower edge was selected in most runs; $\gamma=0$ recovers the pooled method). When $\alpha_h$ leaves $[0,1]$, the radius is set to the largest observed calibration score ($\alpha_h\le 0$; a finite surrogate of the infinite interval of the original method, used in 0.04% of BDG2 and 0.06% of UCI building-days for ACI-CQR) or to the smallest observed score ($\alpha_h\ge1$, empty-set convention). In the first version of the code the radius for $\alpha_h\le0$ was the grid maximum ($500\,s$); this was changed before the final runs.
* **QR-LGBM**: direct LightGBM quantile regression .
* **CQR** : QR-LGBM conformalised with stage-matched pooled CQR scores.
* **MLP-Gauss**: a global multilayer perceptron (256-256-128, ReLU) with a Gaussian output trained by negative log-likelihood, a deep probabilistic baseline in the spirit of DeepAR's likelihood training .
* **MLP-QR**: the same network trained with the pinball loss for the two quantiles .
* **Self-CQR** and **ACI-CQR**: self-only calibration and ACI applied to the CQR scores (same quantile models as CQR).
* **TQA-B-CQR** : temporal quantile adjustment ("budgeting" variant) on the CQR scores. The building's exponentially decayed mean own score (decay 0.8 per day, normalised by the weight sum, days before the forecast only) is ranked among the calibration buildings' decayed means at the same stage; the rank $r=|\{j:\bar e_j<\bar e_b\}|/(N+1)$ is mapped to the queried level $1-a$ with $a=\alpha-\lambda g^B(r)$, $g^B(r)=C(r-(1-\alpha))$ for $r<1-\alpha$ and $r-(1-\alpha)$ otherwise, $C=\alpha^2/(1-\alpha)^2$, $\lambda\le1$ chosen per stage so that $a\ge0.01$ for every *calibration* building (each ranked among the others; the first version used the target buildings, which made a building's interval depend on other new buildings and was corrected before the final runs), and the quantile is taken over the pooled scores together with a point at $+\infty$, as in the original method; the paper's TQA-E variant is an ACI-type update and is represented by ACI-CQR.
* **GHCP-CQR** (an HCP-style baseline, not a full GHCP implementation): the calibration step of generalised hierarchical conformal prediction , adapted to our setting: with $M$ calibration buildings, every calibration building receives total weight $1/(M+1)$ spread over its scores (pooled over all onboarding stages, since GHCP has no notion of stages), and the new building receives the same group share, spread over its observed own scores and a point mass at $+\infty$ for its not-yet-observed scores. Deviations from the original: the surrogate group size is the median number of scores per calibration building (≈1344 in all runs) instead of a randomly drawn donor, and no observations are set aside to fit a local predictor, because our global forecaster already conditions on the building's own history. Without that step, and with a surrogate group size of about 1344 scores, the building's own scores receive at most a weight of about 1/(M+1), so this baseline behaves almost like pooled CQR; it should not be read as a test of GHCP's adaptation mechanism. GHCP's finite-sample guarantee relies on within-group exchangeability, which hourly loads violate.
* **QShrink-CQR** (regularised Mondrian ): quantile-level shrinkage $q=w\,q^{\mathrm{own}}+(1-w)\,q^{\mathrm{pool}}$ with $w=n_{b,h}/(n_{b,h}+\lambda)$, $q^{\mathrm{own}}$ the split-conformal quantile of the own scores (w = 0 while undefined) and $q^{\mathrm{pool}}$ the CQR radius; $\lambda$ is selected by leave-one-building-out from the same grid as $\kappa$, including $\lambda=0$ (own quantile whenever it exists) and $\lambda=\infty$ (pooled CQR radius).
* **HSC** and **HSC-CQR**: Eq. ([-@eq:hsc]) with all three elements (stage matching, similarity prior, shrinkage) applied to absolute and CQR scores; **HSC simple** and **HSC-CQR simple**: the same with a uniform prior ($K$ = all) and without stage matching, i.e. a single pseudo-count shrinkage towards the pooled score distribution; **HSC-CQR fixed-κ**: HSC-CQR simple with the pseudo-count fixed at one week of hourly scores ($\kappa=168$) instead of being selected — a donor–local mixture with fixed pseudo-count as in .
* **CQR (MLP)** and **HSC-CQR (MLP)**: CQR and HSC-CQR simple on the quantiles of the MLP quantile model, to check that the calibration layer is not specific to LightGBM.

The neural networks use the same features (missing values set to zero with missingness indicators, standardised), Adam (learning rate $10^{-3}$, batch 4096), at most 12 epochs, and early stopping on the validation buildings (patience 3). LightGBM uses 63 leaves, learning rate 0.05, at least 200 samples per leaf, 0.8 feature and bagging fractions, L2 regularisation 1, and early stopping (50 rounds) on the validation buildings. These are conventional settings, applied identically to point and quantile models. No method was tuned on target buildings.

 and statistical analysis


# S4. Protocol and deviations

1. The ACI step-size grid was extended to $\{0, 10^{-4}, 2\cdot10^{-4}\}$ after a code audit showed that the lower edge of the original grid was selected in most runs.
2. Mis-specified ablations of the first version were removed and replaced by the fixed-κ variant.
3. After a pilot evaluation, Addendum A (written and committed before the corresponding experiments) added the coverage objective for HSC, QShrink and ACI, recency weighting (ρ = 0.95), stage-wise studentisation, the operational outcomes, the noise reference, site-level tests and the rule for the recommended configuration (Addendum A.1). It also fixed the TQA-B budget scaling and the ACI convention for α_h ≤ 0 (Section S3).
4. At nominal 95 % and 80 %, all CQR-based methods use the quantile models trained for α = 0.1; the conformal step corrects the level. Uncalibrated quantile models (QR-LGBM, MLP-QR) are not reported at these levels.
5. The original protocol selected the HSC pseudo-count by the interval score; this variant is reported (HSC-CQR, HSC-CQR simple).
6. Before the final runs, the analysis was revised without reference to target results: (a) building eligibility is decided on the training period only, no target hours are interpolated, daylight-saving hours are masked, and targets without an onboarding window with at least 80 % valid hours are dropped and counted; (b) the running scale σ0 is estimated on training buildings; (c) every parametrised strategy is tuned by the same constrained leave-one-building-out rule (minimum MACD subject to an interval score at most 2 % above pooled CQR), with grids extended to κ, λ ∈ {6, 12} h and γ ≤ 0.05 and grid-edge selections reported; (d) QShrink-CQR recency, Self-CQR recency, a one-day-delayed and a capped variant, the layer on MLP quantiles and five further stress conditions were added; (e) the method-specific noise reference was replaced by a method-independent oracle reference (7-day moving-block bootstrap); (f) one confirmatory family was declared and the recommended configuration is selected by a nested rule (BDG2 selection, confirmation on UCI, unseen sites and both transfer directions). All models were retrained and all results recomputed.

The complete protocol, including the addenda, is reproduced at the end of this document.

# S5. Additional results

**Table S2. All methods, BDG2, random-building protocol, nominal 90 % (mean ± s.d. over 5 seeds; widths and interval scores are medians over buildings).**

| Method               | Coverage      | Coverage (week 1)   | MACD          | Under-covered share   | P10 coverage   | Rel. width (median)   | Rel. IS (median)   |
|:---------------------|:--------------|:--------------------|:--------------|:----------------------|:---------------|:----------------------|:-------------------|
| HSC-CQR recency      | 0.897 ± 0.003 | 0.881 ± 0.009       | 0.012 ± 0.001 | 0.001 ± 0.003         | 0.877 ± 0.004  | 0.402 ± 0.018         | 0.556 ± 0.028      |
| HSC-SSC-CQR          | 0.899 ± 0.003 | 0.887 ± 0.008       | 0.014 ± 0.000 | 0.007 ± 0.004         | 0.875 ± 0.002  | 0.402 ± 0.018         | 0.559 ± 0.028      |
| SSC-CQR              | 0.900 ± 0.005 | 0.887 ± 0.009       | 0.030 ± 0.001 | 0.100 ± 0.027         | 0.851 ± 0.005  | 0.397 ± 0.014         | 0.558 ± 0.026      |
| HSC-CQR simple (cov) | 0.896 ± 0.003 | 0.882 ± 0.009       | 0.015 ± 0.001 | 0.011 ± 0.010         | 0.872 ± 0.002  | 0.399 ± 0.018         | 0.557 ± 0.028      |
| QShrink-CQR (cov)    | 0.897 ± 0.003 | 0.884 ± 0.010       | 0.016 ± 0.003 | 0.014 ± 0.011         | 0.871 ± 0.006  | 0.399 ± 0.016         | 0.556 ± 0.028      |
| ACI-CQR (cov)        | 0.897 ± 0.002 | 0.882 ± 0.009       | 0.018 ± 0.003 | 0.028 ± 0.020         | 0.868 ± 0.006  | 0.397 ± 0.024         | 0.555 ± 0.029      |
| HSC-CQR              | 0.893 ± 0.004 | 0.872 ± 0.007       | 0.017 ± 0.001 | 0.027 ± 0.015         | 0.866 ± 0.003  | 0.391 ± 0.020         | 0.557 ± 0.029      |
| HSC-CQR simple       | 0.896 ± 0.003 | 0.881 ± 0.009       | 0.017 ± 0.000 | 0.019 ± 0.005         | 0.870 ± 0.003  | 0.396 ± 0.019         | 0.555 ± 0.029      |
| HSC                  | 0.902 ± 0.006 | 0.866 ± 0.013       | 0.029 ± 0.003 | 0.077 ± 0.041         | 0.856 ± 0.009  | 0.423 ± 0.009         | 0.650 ± 0.029      |
| HSC simple           | 0.915 ± 0.003 | 0.894 ± 0.010       | 0.032 ± 0.002 | 0.036 ± 0.011         | 0.868 ± 0.005  | 0.452 ± 0.009         | 0.652 ± 0.023      |
| CQR                  | 0.895 ± 0.007 | 0.883 ± 0.009       | 0.037 ± 0.002 | 0.159 ± 0.039         | 0.835 ± 0.008  | 0.390 ± 0.013         | 0.557 ± 0.027      |
| Self-CQR             | 0.890 ± 0.003 | 0.847 ± 0.009       | 0.020 ± 0.001 | 0.059 ± 0.011         | 0.858 ± 0.003  | 0.402 ± 0.016         | 0.569 ± 0.033      |
| ACI-CQR              | 0.896 ± 0.004 | 0.882 ± 0.009       | 0.022 ± 0.004 | 0.054 ± 0.030         | 0.860 ± 0.006  | 0.395 ± 0.021         | 0.555 ± 0.028      |
| TQA-B-CQR            | 0.898 ± 0.006 | 0.883 ± 0.009       | 0.037 ± 0.002 | 0.153 ± 0.040         | 0.840 ± 0.007  | 0.390 ± 0.014         | 0.558 ± 0.026      |
| GHCP-CQR             | 0.897 ± 0.007 | 0.883 ± 0.010       | 0.037 ± 0.002 | 0.150 ± 0.031         | 0.837 ± 0.008  | 0.392 ± 0.013         | 0.556 ± 0.027      |
| QShrink-CQR          | 0.898 ± 0.008 | 0.885 ± 0.009       | 0.025 ± 0.008 | 0.066 ± 0.082         | 0.859 ± 0.019  | 0.393 ± 0.016         | 0.554 ± 0.029      |
| QR-LGBM              | 0.866 ± 0.006 | 0.855 ± 0.009       | 0.045 ± 0.004 | 0.338 ± 0.054         | 0.809 ± 0.008  | 0.367 ± 0.014         | 0.564 ± 0.028      |
| MLP-QR               | 0.888 ± 0.012 | 0.884 ± 0.019       | 0.037 ± 0.003 | 0.186 ± 0.079         | 0.834 ± 0.009  | 0.394 ± 0.026         | 0.563 ± 0.028      |
| MLP-Gauss            | 0.938 ± 0.007 | 0.926 ± 0.012       | 0.050 ± 0.005 | 0.033 ± 0.017         | 0.878 ± 0.009  | 0.513 ± 0.045         | 0.643 ± 0.033      |
| CQR (MLP)            | 0.897 ± 0.006 | 0.885 ± 0.008       | 0.035 ± 0.002 | 0.128 ± 0.031         | 0.843 ± 0.010  | 0.401 ± 0.018         | 0.561 ± 0.029      |
| HSC-CQR (MLP)        | 0.896 ± 0.006 | 0.891 ± 0.012       | 0.018 ± 0.002 | 0.031 ± 0.015         | 0.867 ± 0.007  | 0.401 ± 0.019         | 0.563 ± 0.027      |
| ACI                  | 0.921 ± 0.005 | 0.891 ± 0.013       | 0.049 ± 0.005 | 0.109 ± 0.037         | 0.847 ± 0.013  | 0.476 ± 0.020         | 0.654 ± 0.025      |
| Self-CP              | 0.906 ± 0.002 | 0.884 ± 0.008       | 0.025 ± 0.001 | 0.046 ± 0.005         | 0.865 ± 0.003  | 0.451 ± 0.013         | 0.667 ± 0.023      |
| SCP-stage            | 0.898 ± 0.014 | 0.886 ± 0.015       | 0.089 ± 0.008 | 0.248 ± 0.047         | 0.738 ± 0.036  | 0.526 ± 0.035         | 0.672 ± 0.021      |
| SCP                  | 0.898 ± 0.014 | 0.866 ± 0.015       | 0.088 ± 0.008 | 0.247 ± 0.045         | 0.741 ± 0.033  | 0.525 ± 0.035         | 0.673 ± 0.021      |
| Mondrian-usage       | 0.893 ± 0.013 | 0.880 ± 0.011       | 0.088 ± 0.007 | 0.260 ± 0.055         | 0.739 ± 0.026  | 0.481 ± 0.033         | 0.688 ± 0.022      |
| Naive+SCP            | 0.903 ± 0.012 | 0.889 ± 0.010       | 0.085 ± 0.005 | 0.238 ± 0.036         | 0.752 ± 0.028  | 0.786 ± 0.052         | 0.987 ± 0.036      |
| Raw-SCP              | 0.892 ± 0.012 | 0.857 ± 0.018       | 0.124 ± 0.008 | 0.231 ± 0.029         | 0.657 ± 0.043  | 0.715 ± 0.049         | 1.052 ± 0.032      |
| HSC -stage           | 0.901 ± 0.005 | 0.855 ± 0.015       | 0.028 ± 0.004 | 0.073 ± 0.042         | 0.856 ± 0.009  | 0.423 ± 0.010         | 0.655 ± 0.023      |
| HSC -kNN             | 0.917 ± 0.003 | 0.908 ± 0.009       | 0.032 ± 0.002 | 0.034 ± 0.013         | 0.870 ± 0.006  | 0.459 ± 0.009         | 0.657 ± 0.023      |
| HSC -shrink          | 0.856 ± 0.012 | 0.829 ± 0.011       | 0.082 ± 0.009 | 0.387 ± 0.051         | 0.716 ± 0.017  | 0.392 ± 0.027         | 0.681 ± 0.020      |
| HSC-CQR -stage       | 0.893 ± 0.003 | 0.875 ± 0.008       | 0.017 ± 0.001 | 0.022 ± 0.013         | 0.867 ± 0.003  | 0.393 ± 0.021         | 0.557 ± 0.029      |
| HSC-CQR -kNN         | 0.896 ± 0.004 | 0.884 ± 0.009       | 0.017 ± 0.001 | 0.019 ± 0.008         | 0.870 ± 0.004  | 0.397 ± 0.019         | 0.555 ± 0.029      |
| HSC-CQR -shrink      | 0.886 ± 0.006 | 0.867 ± 0.007       | 0.035 ± 0.002 | 0.193 ± 0.035         | 0.831 ± 0.007  | 0.383 ± 0.015         | 0.560 ± 0.026      |
| HSC-CQR fixed-κ      | 0.896 ± 0.003 | 0.882 ± 0.009       | 0.015 ± 0.001 | 0.010 ± 0.010         | 0.872 ± 0.002  | 0.398 ± 0.020         | 0.556 ± 0.028      |


**Table S3. All methods, UCI, random-building protocol, nominal 90 %.**

| Method               | Coverage      | Coverage (week 1)   | MACD          | Under-covered share   | P10 coverage   | Rel. width (median)   | Rel. IS (median)   |
|:---------------------|:--------------|:--------------------|:--------------|:----------------------|:---------------|:----------------------|:-------------------|
| HSC-CQR recency      | 0.901 ± 0.002 | 0.901 ± 0.004       | 0.009 ± 0.001 | 0.000 ± 0.000         | 0.886 ± 0.004  | 0.267 ± 0.009         | 0.365 ± 0.007      |
| HSC-SSC-CQR          | 0.903 ± 0.004 | 0.906 ± 0.005       | 0.012 ± 0.002 | 0.002 ± 0.005         | 0.884 ± 0.006  | 0.268 ± 0.010         | 0.365 ± 0.007      |
| SSC-CQR              | 0.915 ± 0.006 | 0.917 ± 0.010       | 0.026 ± 0.002 | 0.019 ± 0.022         | 0.880 ± 0.011  | 0.282 ± 0.017         | 0.367 ± 0.011      |
| HSC-CQR simple (cov) | 0.901 ± 0.003 | 0.902 ± 0.005       | 0.012 ± 0.002 | 0.008 ± 0.009         | 0.882 ± 0.005  | 0.266 ± 0.011         | 0.364 ± 0.007      |
| QShrink-CQR (cov)    | 0.901 ± 0.004 | 0.905 ± 0.007       | 0.012 ± 0.002 | 0.002 ± 0.005         | 0.881 ± 0.006  | 0.265 ± 0.010         | 0.364 ± 0.007      |
| ACI-CQR (cov)        | 0.903 ± 0.004 | 0.904 ± 0.008       | 0.014 ± 0.006 | 0.019 ± 0.028         | 0.881 ± 0.010  | 0.272 ± 0.008         | 0.365 ± 0.006      |
| HSC-CQR              | 0.897 ± 0.004 | 0.893 ± 0.005       | 0.014 ± 0.003 | 0.023 ± 0.034         | 0.875 ± 0.010  | 0.265 ± 0.011         | 0.364 ± 0.007      |
| HSC-CQR simple       | 0.901 ± 0.005 | 0.900 ± 0.006       | 0.014 ± 0.003 | 0.017 ± 0.026         | 0.879 ± 0.011  | 0.269 ± 0.013         | 0.364 ± 0.007      |
| HSC                  | 0.906 ± 0.006 | 0.893 ± 0.017       | 0.021 ± 0.001 | 0.036 ± 0.029         | 0.873 ± 0.007  | 0.282 ± 0.012         | 0.408 ± 0.016      |
| HSC simple           | 0.915 ± 0.006 | 0.910 ± 0.014       | 0.026 ± 0.005 | 0.027 ± 0.022         | 0.880 ± 0.010  | 0.299 ± 0.012         | 0.413 ± 0.017      |
| CQR                  | 0.901 ± 0.011 | 0.904 ± 0.010       | 0.031 ± 0.003 | 0.114 ± 0.032         | 0.850 ± 0.014  | 0.271 ± 0.017         | 0.365 ± 0.009      |
| Self-CQR             | 0.896 ± 0.003 | 0.879 ± 0.005       | 0.016 ± 0.002 | 0.013 ± 0.017         | 0.872 ± 0.005  | 0.262 ± 0.005         | 0.368 ± 0.006      |
| ACI-CQR              | 0.902 ± 0.005 | 0.903 ± 0.009       | 0.019 ± 0.003 | 0.046 ± 0.022         | 0.870 ± 0.008  | 0.271 ± 0.012         | 0.364 ± 0.008      |
| TQA-B-CQR            | 0.902 ± 0.007 | 0.905 ± 0.008       | 0.031 ± 0.002 | 0.103 ± 0.019         | 0.852 ± 0.012  | 0.273 ± 0.008         | 0.363 ± 0.010      |
| GHCP-CQR             | 0.908 ± 0.009 | 0.910 ± 0.006       | 0.033 ± 0.002 | 0.088 ± 0.032         | 0.858 ± 0.016  | 0.278 ± 0.017         | 0.364 ± 0.010      |
| QShrink-CQR          | 0.903 ± 0.006 | 0.906 ± 0.010       | 0.016 ± 0.003 | 0.021 ± 0.027         | 0.877 ± 0.012  | 0.268 ± 0.014         | 0.364 ± 0.007      |
| QR-LGBM              | 0.874 ± 0.007 | 0.876 ± 0.006       | 0.036 ± 0.006 | 0.204 ± 0.056         | 0.823 ± 0.010  | 0.251 ± 0.011         | 0.363 ± 0.007      |
| MLP-QR               | 0.886 ± 0.010 | 0.902 ± 0.022       | 0.030 ± 0.004 | 0.141 ± 0.078         | 0.842 ± 0.016  | 0.262 ± 0.014         | 0.368 ± 0.017      |
| MLP-Gauss            | 0.914 ± 0.008 | 0.921 ± 0.015       | 0.031 ± 0.004 | 0.065 ± 0.023         | 0.875 ± 0.011  | 0.309 ± 0.033         | 0.405 ± 0.031      |
| CQR (MLP)            | 0.902 ± 0.010 | 0.904 ± 0.008       | 0.030 ± 0.002 | 0.095 ± 0.042         | 0.856 ± 0.013  | 0.275 ± 0.018         | 0.369 ± 0.016      |
| HSC-CQR (MLP)        | 0.899 ± 0.006 | 0.913 ± 0.010       | 0.015 ± 0.004 | 0.019 ± 0.017         | 0.877 ± 0.010  | 0.269 ± 0.018         | 0.369 ± 0.019      |
| ACI                  | 0.922 ± 0.013 | 0.907 ± 0.012       | 0.050 ± 0.014 | 0.101 ± 0.058         | 0.843 ± 0.031  | 0.331 ± 0.036         | 0.417 ± 0.021      |
| Self-CP              | 0.910 ± 0.004 | 0.912 ± 0.003       | 0.022 ± 0.002 | 0.015 ± 0.016         | 0.880 ± 0.004  | 0.291 ± 0.009         | 0.415 ± 0.016      |
| SCP-stage            | 0.903 ± 0.024 | 0.902 ± 0.016       | 0.090 ± 0.010 | 0.217 ± 0.058         | 0.748 ± 0.059  | 0.372 ± 0.042         | 0.437 ± 0.028      |
| SCP                  | 0.903 ± 0.024 | 0.883 ± 0.024       | 0.090 ± 0.010 | 0.213 ± 0.055         | 0.749 ± 0.059  | 0.371 ± 0.043         | 0.436 ± 0.027      |
| Naive+SCP            | 0.905 ± 0.012 | 0.901 ± 0.008       | 0.076 ± 0.006 | 0.217 ± 0.032         | 0.766 ± 0.026  | 0.479 ± 0.038         | 0.578 ± 0.023      |
| Raw-SCP              | 0.907 ± 0.029 | 0.894 ± 0.035       | 0.127 ± 0.017 | 0.181 ± 0.077         | 0.689 ± 0.156  | 0.842 ± 0.163         | 0.961 ± 0.121      |
| HSC -stage           | 0.906 ± 0.006 | 0.882 ± 0.022       | 0.021 ± 0.002 | 0.038 ± 0.028         | 0.873 ± 0.008  | 0.281 ± 0.013         | 0.411 ± 0.017      |
| HSC -kNN             | 0.916 ± 0.006 | 0.924 ± 0.007       | 0.026 ± 0.005 | 0.025 ± 0.023         | 0.881 ± 0.010  | 0.303 ± 0.014         | 0.411 ± 0.015      |
| HSC -shrink          | 0.859 ± 0.013 | 0.849 ± 0.010       | 0.076 ± 0.009 | 0.326 ± 0.027         | 0.720 ± 0.028  | 0.260 ± 0.012         | 0.429 ± 0.020      |
| HSC-CQR -stage       | 0.898 ± 0.004 | 0.894 ± 0.005       | 0.014 ± 0.003 | 0.019 ± 0.031         | 0.876 ± 0.011  | 0.265 ± 0.012         | 0.364 ± 0.006      |
| HSC-CQR -kNN         | 0.901 ± 0.006 | 0.905 ± 0.009       | 0.014 ± 0.003 | 0.021 ± 0.036         | 0.879 ± 0.012  | 0.269 ± 0.014         | 0.364 ± 0.007      |
| HSC-CQR -shrink      | 0.892 ± 0.007 | 0.892 ± 0.006       | 0.029 ± 0.003 | 0.122 ± 0.035         | 0.847 ± 0.012  | 0.265 ± 0.014         | 0.365 ± 0.008      |
| HSC-CQR fixed-κ      | 0.901 ± 0.004 | 0.902 ± 0.005       | 0.012 ± 0.002 | 0.008 ± 0.009         | 0.883 ± 0.006  | 0.268 ± 0.012         | 0.364 ± 0.007      |


**Table S4. Exploratory paired per-building comparisons of HSC-CQR recency with the strongest alternatives (Wilcoxon on absolute coverage deviation and interval score).**

| Data   | Baseline             | Metric   | n   | Mean diff.   | Better (%)   | r_rb   | p (Holm)   | p (sites)   |
|:-------|:---------------------|:---------|:----|:-------------|:-------------|:-------|:-----------|:------------|
| BDG2   | CQR                  | CD       | 837 | -0.0238      | 87           | +0.92  | <0.001     | <0.001      |
| BDG2   | CQR                  | CD wk 1  | 837 | -0.0199      | 75           | +0.78  | <0.001     | 0.013       |
| BDG2   | CQR                  | IS       | 837 | +0.0115      | 49           | +0.09  | 0.086      | 0.296       |
| BDG2   | QShrink-CQR (cov)    | CD       | 837 | -0.0039      | 75           | +0.70  | <0.001     | <0.001      |
| BDG2   | QShrink-CQR (cov)    | CD wk 1  | 837 | -0.0041      | 53           | +0.36  | <0.001     | 0.025       |
| BDG2   | QShrink-CQR (cov)    | IS       | 837 | -0.0051      | 46           | -0.01  | 0.864      | 0.042       |
| BDG2   | ACI-CQR              | CD       | 837 | -0.0097      | 78           | +0.74  | <0.001     | <0.001      |
| BDG2   | ACI-CQR              | CD wk 1  | 837 | -0.0165      | 73           | +0.73  | <0.001     | 0.013       |
| BDG2   | ACI-CQR              | IS       | 837 | +0.0038      | 37           | -0.28  | <0.001     | 0.030       |
| BDG2   | ACI-CQR (cov)        | CD       | 837 | -0.0055      | 68           | +0.54  | <0.001     | <0.001      |
| BDG2   | ACI-CQR (cov)        | CD wk 1  | 837 | -0.0149      | 71           | +0.71  | <0.001     | 0.013       |
| BDG2   | ACI-CQR (cov)        | IS       | 837 | -0.0051      | 38           | -0.28  | <0.001     | 0.626       |
| BDG2   | Self-CQR             | CD       | 837 | -0.0085      | 76           | +0.68  | <0.001     | <0.001      |
| BDG2   | Self-CQR             | CD wk 1  | 837 | -0.0136      | 57           | +0.33  | <0.001     | <0.001      |
| BDG2   | Self-CQR             | IS       | 837 | -0.0483      | 91           | +0.93  | <0.001     | <0.001      |
| BDG2   | HSC-CQR fixed-κ      | CD       | 837 | -0.0026      | 72           | +0.56  | <0.001     | <0.001      |
| BDG2   | HSC-CQR fixed-κ      | CD wk 1  | 837 | -0.0057      | 53           | +0.54  | <0.001     | 0.017       |
| BDG2   | HSC-CQR fixed-κ      | IS       | 837 | +0.0143      | 35           | -0.34  | <0.001     | <0.001      |
| BDG2   | HSC-CQR simple (cov) | CD       | 837 | -0.0027      | 72           | +0.59  | <0.001     | <0.001      |
| BDG2   | HSC-CQR simple (cov) | CD wk 1  | 837 | -0.0040      | 51           | +0.48  | <0.001     | 0.017       |
| BDG2   | HSC-CQR simple (cov) | IS       | 837 | +0.0116      | 37           | -0.24  | <0.001     | <0.001      |
| BDG2   | HSC-CQR              | CD       | 837 | -0.0047      | 73           | +0.62  | <0.001     | <0.001      |
| BDG2   | HSC-CQR              | CD wk 1  | 837 | -0.0112      | 66           | +0.55  | <0.001     | <0.001      |
| BDG2   | HSC-CQR              | IS       | 837 | +0.0184      | 32           | -0.44  | <0.001     | <0.001      |
| BDG2   | HSC-SSC-CQR          | CD       | 837 | -0.0023      | 65           | +0.41  | <0.001     | 0.035       |
| BDG2   | HSC-SSC-CQR          | CD wk 1  | 837 | -0.0018      | 46           | +0.23  | <0.001     | 0.035       |
| BDG2   | HSC-SSC-CQR          | IS       | 837 | -0.1357      | 54           | +0.25  | <0.001     | 0.009       |
| BDG2   | GHCP-CQR             | CD       | 837 | -0.0237      | 88           | +0.91  | <0.001     | <0.001      |
| BDG2   | GHCP-CQR             | CD wk 1  | 837 | -0.0202      | 76           | +0.78  | <0.001     | 0.013       |
| BDG2   | GHCP-CQR             | IS       | 837 | +0.0116      | 49           | +0.09  | 0.086      | 0.268       |
| BDG2   | TQA-B-CQR            | CD       | 837 | -0.0239      | 86           | +0.91  | <0.001     | <0.001      |
| BDG2   | TQA-B-CQR            | CD wk 1  | 837 | -0.0162      | 73           | +0.72  | <0.001     | 0.013       |
| BDG2   | TQA-B-CQR            | IS       | 837 | +0.0104      | 53           | +0.18  | <0.001     | 0.194       |
| UCI    | CQR                  | CD       | 270 | -0.0225      | 89           | +0.92  | <0.001     | –           |
| UCI    | CQR                  | CD wk 1  | 270 | -0.0228      | 76           | +0.75  | <0.001     | –           |
| UCI    | CQR                  | IS       | 270 | -0.0007      | 46           | -0.03  | 0.651      | –           |
| UCI    | QShrink-CQR (cov)    | CD       | 270 | -0.0032      | 77           | +0.71  | <0.001     | –           |
| UCI    | QShrink-CQR (cov)    | CD wk 1  | 270 | -0.0037      | 56           | +0.36  | <0.001     | –           |
| UCI    | QShrink-CQR (cov)    | IS       | 270 | +0.0015      | 30           | -0.39  | <0.001     | –           |
| UCI    | ACI-CQR              | CD       | 270 | -0.0097      | 78           | +0.75  | <0.001     | –           |
| UCI    | ACI-CQR              | CD wk 1  | 270 | -0.0202      | 76           | +0.72  | <0.001     | –           |
| UCI    | ACI-CQR              | IS       | 270 | +0.0031      | 32           | -0.39  | <0.001     | –           |
| UCI    | ACI-CQR (cov)        | CD       | 270 | -0.0041      | 63           | +0.42  | <0.001     | –           |
| UCI    | ACI-CQR (cov)        | CD wk 1  | 270 | -0.0155      | 71           | +0.65  | <0.001     | –           |
| UCI    | ACI-CQR (cov)        | IS       | 270 | -0.0014      | 44           | -0.17  | 0.074      | –           |
| UCI    | Self-CQR             | CD       | 270 | -0.0065      | 78           | +0.77  | <0.001     | –           |
| UCI    | Self-CQR             | CD wk 1  | 270 | -0.0110      | 59           | +0.42  | <0.001     | –           |
| UCI    | Self-CQR             | IS       | 270 | -0.0104      | 90           | +0.92  | <0.001     | –           |
| UCI    | HSC-CQR fixed-κ      | CD       | 270 | -0.0028      | 73           | +0.62  | <0.001     | –           |
| UCI    | HSC-CQR fixed-κ      | CD wk 1  | 270 | -0.0093      | 66           | +0.53  | <0.001     | –           |
| UCI    | HSC-CQR fixed-κ      | IS       | 270 | +0.0046      | 17           | -0.71  | <0.001     | –           |
| UCI    | HSC-CQR simple (cov) | CD       | 270 | -0.0031      | 76           | +0.75  | <0.001     | –           |
| UCI    | HSC-CQR simple (cov) | CD wk 1  | 270 | -0.0059      | 62           | +0.44  | <0.001     | –           |
| UCI    | HSC-CQR simple (cov) | IS       | 270 | +0.0020      | 22           | -0.62  | <0.001     | –           |
| UCI    | HSC-CQR              | CD       | 270 | -0.0049      | 72           | +0.58  | <0.001     | –           |
| UCI    | HSC-CQR              | CD wk 1  | 270 | -0.0142      | 69           | +0.59  | <0.001     | –           |
| UCI    | HSC-CQR              | IS       | 270 | +0.0051      | 22           | -0.63  | <0.001     | –           |
| UCI    | HSC-SSC-CQR          | CD       | 270 | -0.0030      | 71           | +0.65  | <0.001     | –           |
| UCI    | HSC-SSC-CQR          | CD wk 1  | 270 | -0.0037      | 51           | +0.29  | <0.001     | –           |
| UCI    | HSC-SSC-CQR          | IS       | 270 | -0.0309      | 31           | -0.27  | <0.001     | –           |
| UCI    | GHCP-CQR             | CD       | 270 | -0.0240      | 90           | +0.94  | <0.001     | –           |
| UCI    | GHCP-CQR             | CD wk 1  | 270 | -0.0238      | 80           | +0.77  | <0.001     | –           |
| UCI    | GHCP-CQR             | IS       | 270 | -0.0007      | 51           | +0.11  | 0.338      | –           |
| UCI    | TQA-B-CQR            | CD       | 270 | -0.0215      | 89           | +0.91  | <0.001     | –           |
| UCI    | TQA-B-CQR            | CD wk 1  | 270 | -0.0193      | 74           | +0.71  | <0.001     | –           |
| UCI    | TQA-B-CQR            | IS       | 270 | -0.0005      | 49           | +0.11  | 0.338      | –           |


**Table S5. Site-level robustness of the paired comparisons of HSC-CQR recency on BDG2 (90 %). p (10 site means): Wilcoxon signed-rank test on the ten site means of the paired differences (smallest attainable two-sided p = 0.002); p (without largest site): building-level Wilcoxon test without site 'Rat'. CD = absolute coverage deviation over the window; CD wk 1 = the same for the first week; IS = relative interval score.**

| Baseline | Metric | Better (%) | p (buildings, Holm) | p (10 site means) | p (without largest site) |
|:--|:--|--:|--:|--:|--:|
| CQR | IS | 49 | 0.086 | 0.296 | <0.001 |
| CQR | CD | 87 | <0.001 | <0.001 | <0.001 |
| CQR | CD wk 1 | 75 | <0.001 | 0.013 | <0.001 |
| Self-CQR | IS | 91 | <0.001 | <0.001 | <0.001 |
| Self-CQR | CD | 76 | <0.001 | <0.001 | <0.001 |
| Self-CQR | CD wk 1 | 57 | <0.001 | <0.001 | <0.001 |
| ACI-CQR | IS | 37 | <0.001 | 0.030 | <0.001 |
| ACI-CQR | CD | 78 | <0.001 | <0.001 | <0.001 |
| ACI-CQR | CD wk 1 | 73 | <0.001 | 0.013 | <0.001 |
| ACI-CQR (cov) | IS | 38 | <0.001 | 0.626 | <0.001 |
| ACI-CQR (cov) | CD | 68 | <0.001 | <0.001 | <0.001 |
| ACI-CQR (cov) | CD wk 1 | 71 | <0.001 | 0.013 | <0.001 |
| TQA-B-CQR | IS | 53 | <0.001 | 0.194 | <0.001 |
| TQA-B-CQR | CD | 86 | <0.001 | <0.001 | <0.001 |
| TQA-B-CQR | CD wk 1 | 73 | <0.001 | 0.013 | <0.001 |
| GHCP-CQR | IS | 49 | 0.086 | 0.268 | <0.001 |
| GHCP-CQR | CD | 88 | <0.001 | <0.001 | <0.001 |
| GHCP-CQR | CD wk 1 | 76 | <0.001 | 0.013 | <0.001 |
| QShrink-CQR | IS | 39 | <0.001 | 0.002 | 0.002 |
| QShrink-CQR | CD | 82 | <0.001 | <0.001 | <0.001 |
| QShrink-CQR | CD wk 1 | 73 | <0.001 | 0.013 | <0.001 |
| QShrink-CQR (cov) | IS | 46 | 0.864 | 0.042 | 0.070 |
| QShrink-CQR (cov) | CD | 75 | <0.001 | <0.001 | <0.001 |
| QShrink-CQR (cov) | CD wk 1 | 53 | <0.001 | 0.025 | <0.001 |
| HSC-CQR | IS | 32 | <0.001 | <0.001 | <0.001 |
| HSC-CQR | CD | 73 | <0.001 | <0.001 | <0.001 |
| HSC-CQR | CD wk 1 | 66 | <0.001 | <0.001 | <0.001 |
| HSC-CQR simple | IS | 31 | <0.001 | <0.001 | <0.001 |
| HSC-CQR simple | CD | 73 | <0.001 | <0.001 | <0.001 |
| HSC-CQR simple | CD wk 1 | 67 | <0.001 | 0.013 | <0.001 |
| HSC-CQR fixed-κ | IS | 35 | <0.001 | <0.001 | <0.001 |
| HSC-CQR fixed-κ | CD | 72 | <0.001 | <0.001 | <0.001 |
| HSC-CQR fixed-κ | CD wk 1 | 53 | <0.001 | 0.017 | <0.001 |
| SSC-CQR | IS | 51 | 0.350 | 0.808 | <0.001 |
| SSC-CQR | CD | 87 | <0.001 | <0.001 | <0.001 |
| SSC-CQR | CD wk 1 | 74 | <0.001 | 0.013 | <0.001 |
| MLP-QR | IS | 63 | <0.001 | 0.119 | <0.001 |
| MLP-QR | CD | 87 | <0.001 | <0.001 | <0.001 |
| MLP-QR | CD wk 1 | 70 | <0.001 | 0.009 | <0.001 |
| MLP-Gauss | IS | 97 | <0.001 | 0.009 | <0.001 |
| MLP-Gauss | CD | 89 | <0.001 | <0.001 | <0.001 |
| MLP-Gauss | CD wk 1 | 79 | <0.001 | <0.001 | <0.001 |
| HSC-SSC-CQR | IS | 54 | <0.001 | 0.009 | <0.001 |
| HSC-SSC-CQR | CD | 65 | <0.001 | 0.035 | <0.001 |
| HSC-SSC-CQR | CD wk 1 | 46 | <0.001 | 0.035 | <0.001 |
| HSC-CQR simple (cov) | IS | 37 | <0.001 | <0.001 | <0.001 |
| HSC-CQR simple (cov) | CD | 72 | <0.001 | <0.001 | <0.001 |
| HSC-CQR simple (cov) | CD wk 1 | 51 | <0.001 | 0.017 | <0.001 |

**Table S6. BDG2, nominal 95 %.**

| Method               | Coverage      | Coverage (week 1)   | MACD          | Under-covered share   | P10 coverage   | Rel. width (median)   | Rel. IS (median)   |
|:---------------------|:--------------|:--------------------|:--------------|:----------------------|:---------------|:----------------------|:-------------------|
| HSC-CQR recency      | 0.950 ± 0.002 | 0.931 ± 0.009       | 0.010 ± 0.003 | 0.001 ± 0.002         | 0.933 ± 0.006  | 0.503 ± 0.020         | 0.688 ± 0.024      |
| HSC-SSC-CQR          | 0.948 ± 0.001 | 0.934 ± 0.009       | 0.010 ± 0.000 | 0.001 ± 0.001         | 0.931 ± 0.001  | 0.500 ± 0.022         | 0.688 ± 0.029      |
| SSC-CQR              | 0.951 ± 0.002 | 0.938 ± 0.008       | 0.019 ± 0.000 | 0.034 ± 0.010         | 0.918 ± 0.004  | 0.497 ± 0.019         | 0.688 ± 0.027      |
| HSC-CQR simple (cov) | 0.949 ± 0.001 | 0.932 ± 0.009       | 0.011 ± 0.001 | 0.002 ± 0.003         | 0.931 ± 0.002  | 0.497 ± 0.017         | 0.686 ± 0.028      |
| QShrink-CQR (cov)    | 0.950 ± 0.003 | 0.932 ± 0.012       | 0.014 ± 0.005 | 0.009 ± 0.016         | 0.928 ± 0.008  | 0.497 ± 0.018         | 0.686 ± 0.025      |
| ACI-CQR (cov)        | 0.951 ± 0.002 | 0.933 ± 0.009       | 0.019 ± 0.003 | 0.030 ± 0.026         | 0.920 ± 0.006  | 0.490 ± 0.022         | 0.686 ± 0.027      |
| HSC-CQR              | 0.946 ± 0.003 | 0.922 ± 0.007       | 0.015 ± 0.002 | 0.007 ± 0.005         | 0.922 ± 0.006  | 0.479 ± 0.018         | 0.686 ± 0.029      |
| HSC-CQR simple       | 0.951 ± 0.002 | 0.930 ± 0.009       | 0.015 ± 0.002 | 0.007 ± 0.006         | 0.928 ± 0.005  | 0.490 ± 0.020         | 0.684 ± 0.030      |
| HSC                  | 0.952 ± 0.003 | 0.921 ± 0.010       | 0.021 ± 0.001 | 0.029 ± 0.012         | 0.918 ± 0.004  | 0.588 ± 0.016         | 0.823 ± 0.028      |
| HSC simple           | 0.961 ± 0.002 | 0.938 ± 0.010       | 0.022 ± 0.002 | 0.013 ± 0.010         | 0.928 ± 0.006  | 0.644 ± 0.017         | 0.843 ± 0.020      |
| CQR                  | 0.947 ± 0.004 | 0.932 ± 0.009       | 0.030 ± 0.002 | 0.127 ± 0.025         | 0.893 ± 0.008  | 0.488 ± 0.020         | 0.683 ± 0.026      |
| Self-CQR             | 0.942 ± 0.001 | 0.898 ± 0.010       | 0.015 ± 0.001 | 0.018 ± 0.007         | 0.919 ± 0.002  | 0.502 ± 0.020         | 0.701 ± 0.030      |
| ACI-CQR              | 0.950 ± 0.002 | 0.933 ± 0.009       | 0.021 ± 0.001 | 0.050 ± 0.012         | 0.915 ± 0.003  | 0.489 ± 0.022         | 0.684 ± 0.026      |
| TQA-B-CQR            | 0.947 ± 0.004 | 0.933 ± 0.009       | 0.030 ± 0.002 | 0.125 ± 0.029         | 0.894 ± 0.008  | 0.487 ± 0.019         | 0.683 ± 0.026      |
| GHCP-CQR             | 0.949 ± 0.004 | 0.930 ± 0.009       | 0.030 ± 0.002 | 0.112 ± 0.023         | 0.896 ± 0.007  | 0.496 ± 0.020         | 0.680 ± 0.028      |
| QShrink-CQR          | 0.951 ± 0.006 | 0.934 ± 0.009       | 0.021 ± 0.008 | 0.041 ± 0.064         | 0.918 ± 0.019  | 0.492 ± 0.016         | 0.685 ± 0.025      |
| MLP-Gauss            | 0.960 ± 0.005 | 0.944 ± 0.010       | 0.028 ± 0.002 | 0.058 ± 0.021         | 0.915 ± 0.008  | 0.612 ± 0.053         | 0.782 ± 0.040      |
| CQR (MLP)            | 0.948 ± 0.005 | 0.934 ± 0.007       | 0.029 ± 0.002 | 0.097 ± 0.022         | 0.901 ± 0.008  | 0.500 ± 0.021         | 0.683 ± 0.024      |
| HSC-CQR (MLP)        | 0.951 ± 0.003 | 0.934 ± 0.006       | 0.015 ± 0.002 | 0.010 ± 0.007         | 0.925 ± 0.005  | 0.500 ± 0.019         | 0.685 ± 0.025      |
| ACI                  | 0.964 ± 0.004 | 0.936 ± 0.011       | 0.033 ± 0.003 | 0.071 ± 0.044         | 0.909 ± 0.014  | 0.729 ± 0.038         | 0.861 ± 0.025      |
| Self-CP              | 0.951 ± 0.001 | 0.919 ± 0.009       | 0.017 ± 0.001 | 0.022 ± 0.009         | 0.922 ± 0.002  | 0.615 ± 0.026         | 0.859 ± 0.030      |
| SCP-stage            | 0.948 ± 0.009 | 0.933 ± 0.011       | 0.055 ± 0.006 | 0.160 ± 0.031         | 0.850 ± 0.026  | 0.813 ± 0.062         | 0.906 ± 0.046      |
| SCP                  | 0.948 ± 0.009 | 0.920 ± 0.012       | 0.054 ± 0.006 | 0.162 ± 0.034         | 0.852 ± 0.025  | 0.810 ± 0.061         | 0.914 ± 0.041      |
| Mondrian-usage       | 0.945 ± 0.009 | 0.929 ± 0.007       | 0.055 ± 0.005 | 0.175 ± 0.037         | 0.847 ± 0.028  | 0.728 ± 0.043         | 0.899 ± 0.027      |
| Naive+SCP            | 0.953 ± 0.007 | 0.936 ± 0.009       | 0.053 ± 0.005 | 0.164 ± 0.033         | 0.857 ± 0.017  | 1.248 ± 0.078         | 1.332 ± 0.063      |
| Raw-SCP              | 0.944 ± 0.010 | 0.915 ± 0.016       | 0.074 ± 0.006 | 0.149 ± 0.029         | 0.823 ± 0.042  | 1.275 ± 0.125         | 1.658 ± 0.085      |
| HSC-CQR fixed-κ      | 0.950 ± 0.001 | 0.932 ± 0.009       | 0.011 ± 0.000 | 0.001 ± 0.002         | 0.932 ± 0.001  | 0.494 ± 0.019         | 0.684 ± 0.029      |


**Table S7. UCI, nominal 95 %.**

| Method               | Coverage      | Coverage (week 1)   | MACD          | Under-covered share   | P10 coverage   | Rel. width (median)   | Rel. IS (median)   |
|:---------------------|:--------------|:--------------------|:--------------|:----------------------|:---------------|:----------------------|:-------------------|
| HSC-CQR recency      | 0.952 ± 0.001 | 0.953 ± 0.003       | 0.007 ± 0.000 | 0.000 ± 0.000         | 0.941 ± 0.002  | 0.335 ± 0.011         | 0.443 ± 0.010      |
| HSC-SSC-CQR          | 0.952 ± 0.003 | 0.952 ± 0.002       | 0.008 ± 0.001 | 0.000 ± 0.000         | 0.939 ± 0.004  | 0.329 ± 0.014         | 0.440 ± 0.009      |
| SSC-CQR              | 0.966 ± 0.004 | 0.967 ± 0.003       | 0.020 ± 0.002 | 0.002 ± 0.005         | 0.947 ± 0.008  | 0.378 ± 0.022         | 0.457 ± 0.010      |
| HSC-CQR simple (cov) | 0.952 ± 0.002 | 0.952 ± 0.003       | 0.009 ± 0.000 | 0.000 ± 0.000         | 0.937 ± 0.004  | 0.328 ± 0.011         | 0.441 ± 0.010      |
| QShrink-CQR (cov)    | 0.952 ± 0.002 | 0.953 ± 0.003       | 0.009 ± 0.000 | 0.000 ± 0.000         | 0.938 ± 0.004  | 0.327 ± 0.012         | 0.442 ± 0.010      |
| ACI-CQR (cov)        | 0.954 ± 0.004 | 0.953 ± 0.004       | 0.015 ± 0.007 | 0.021 ± 0.032         | 0.930 ± 0.014  | 0.344 ± 0.016         | 0.440 ± 0.011      |
| HSC-CQR              | 0.949 ± 0.003 | 0.945 ± 0.004       | 0.010 ± 0.002 | 0.008 ± 0.014         | 0.933 ± 0.007  | 0.324 ± 0.012         | 0.438 ± 0.011      |
| HSC-CQR simple       | 0.953 ± 0.003 | 0.950 ± 0.005       | 0.011 ± 0.002 | 0.008 ± 0.014         | 0.936 ± 0.007  | 0.332 ± 0.016         | 0.439 ± 0.011      |
| HSC                  | 0.954 ± 0.005 | 0.939 ± 0.013       | 0.015 ± 0.001 | 0.019 ± 0.026         | 0.931 ± 0.009  | 0.378 ± 0.019         | 0.514 ± 0.015      |
| HSC simple           | 0.962 ± 0.004 | 0.958 ± 0.012       | 0.018 ± 0.003 | 0.008 ± 0.012         | 0.939 ± 0.005  | 0.405 ± 0.013         | 0.515 ± 0.016      |
| CQR                  | 0.952 ± 0.008 | 0.953 ± 0.005       | 0.027 ± 0.003 | 0.082 ± 0.030         | 0.906 ± 0.017  | 0.348 ± 0.027         | 0.439 ± 0.012      |
| Self-CQR             | 0.948 ± 0.002 | 0.932 ± 0.005       | 0.011 ± 0.001 | 0.002 ± 0.005         | 0.930 ± 0.004  | 0.324 ± 0.010         | 0.446 ± 0.009      |
| ACI-CQR              | 0.954 ± 0.005 | 0.953 ± 0.005       | 0.017 ± 0.005 | 0.032 ± 0.027         | 0.925 ± 0.011  | 0.345 ± 0.018         | 0.439 ± 0.011      |
| TQA-B-CQR            | 0.952 ± 0.006 | 0.953 ± 0.005       | 0.026 ± 0.003 | 0.084 ± 0.028         | 0.904 ± 0.017  | 0.346 ± 0.023         | 0.438 ± 0.012      |
| GHCP-CQR             | 0.960 ± 0.008 | 0.959 ± 0.006       | 0.028 ± 0.003 | 0.067 ± 0.035         | 0.916 ± 0.015  | 0.371 ± 0.032         | 0.448 ± 0.015      |
| QShrink-CQR          | 0.954 ± 0.004 | 0.956 ± 0.004       | 0.012 ± 0.002 | 0.006 ± 0.009         | 0.935 ± 0.008  | 0.335 ± 0.015         | 0.440 ± 0.012      |
| MLP-Gauss            | 0.946 ± 0.005 | 0.948 ± 0.010       | 0.020 ± 0.002 | 0.063 ± 0.027         | 0.915 ± 0.011  | 0.369 ± 0.039         | 0.488 ± 0.029      |
| CQR (MLP)            | 0.952 ± 0.007 | 0.954 ± 0.006       | 0.026 ± 0.003 | 0.076 ± 0.034         | 0.907 ± 0.015  | 0.350 ± 0.025         | 0.447 ± 0.022      |
| HSC-CQR (MLP)        | 0.952 ± 0.003 | 0.954 ± 0.007       | 0.012 ± 0.002 | 0.006 ± 0.009         | 0.933 ± 0.007  | 0.335 ± 0.019         | 0.444 ± 0.022      |
| ACI                  | 0.968 ± 0.009 | 0.957 ± 0.014       | 0.029 ± 0.008 | 0.029 ± 0.039         | 0.929 ± 0.018  | 0.482 ± 0.098         | 0.552 ± 0.068      |
| Self-CP              | 0.955 ± 0.003 | 0.948 ± 0.003       | 0.014 ± 0.001 | 0.002 ± 0.005         | 0.933 ± 0.004  | 0.384 ± 0.014         | 0.515 ± 0.018      |
| SCP-stage            | 0.949 ± 0.021 | 0.947 ± 0.019       | 0.059 ± 0.012 | 0.131 ± 0.056         | 0.857 ± 0.058  | 0.574 ± 0.129         | 0.609 ± 0.112      |
| SCP                  | 0.950 ± 0.021 | 0.934 ± 0.026       | 0.059 ± 0.012 | 0.133 ± 0.056         | 0.859 ± 0.058  | 0.571 ± 0.129         | 0.609 ± 0.110      |
| Naive+SCP            | 0.951 ± 0.011 | 0.946 ± 0.007       | 0.052 ± 0.005 | 0.145 ± 0.044         | 0.861 ± 0.036  | 0.717 ± 0.098         | 0.768 ± 0.076      |
| Raw-SCP              | 0.953 ± 0.021 | 0.947 ± 0.026       | 0.076 ± 0.013 | 0.101 ± 0.046         | 0.874 ± 0.104  | 1.718 ± 0.509         | 1.815 ± 0.460      |
| HSC-CQR fixed-κ      | 0.953 ± 0.003 | 0.951 ± 0.003       | 0.009 ± 0.000 | 0.000 ± 0.000         | 0.938 ± 0.005  | 0.331 ± 0.013         | 0.439 ± 0.009      |


**Table S8. BDG2, nominal 80 %.**

| Method               | Coverage      | Coverage (week 1)   | MACD          | Under-covered share   | P10 coverage   | Rel. width (median)   | Rel. IS (median)   |
|:---------------------|:--------------|:--------------------|:--------------|:----------------------|:---------------|:----------------------|:-------------------|
| HSC-CQR recency      | 0.795 ± 0.004 | 0.785 ± 0.006       | 0.017 ± 0.001 | 0.033 ± 0.009         | 0.769 ± 0.004  | 0.327 ± 0.018         | 0.456 ± 0.026      |
| HSC-SSC-CQR          | 0.804 ± 0.006 | 0.790 ± 0.007       | 0.021 ± 0.001 | 0.029 ± 0.022         | 0.771 ± 0.006  | 0.327 ± 0.020         | 0.455 ± 0.026      |
| SSC-CQR              | 0.796 ± 0.013 | 0.785 ± 0.007       | 0.057 ± 0.006 | 0.196 ± 0.056         | 0.712 ± 0.026  | 0.332 ± 0.011         | 0.455 ± 0.026      |
| HSC-CQR simple (cov) | 0.793 ± 0.005 | 0.790 ± 0.007       | 0.021 ± 0.001 | 0.066 ± 0.014         | 0.761 ± 0.005  | 0.326 ± 0.018         | 0.456 ± 0.027      |
| QShrink-CQR (cov)    | 0.790 ± 0.006 | 0.776 ± 0.007       | 0.023 ± 0.002 | 0.082 ± 0.025         | 0.757 ± 0.008  | 0.325 ± 0.019         | 0.456 ± 0.026      |
| ACI-CQR (cov)        | 0.802 ± 0.002 | 0.785 ± 0.005       | 0.015 ± 0.005 | 0.005 ± 0.006         | 0.779 ± 0.007  | 0.332 ± 0.024         | 0.461 ± 0.030      |
| HSC-CQR              | 0.796 ± 0.006 | 0.780 ± 0.004       | 0.023 ± 0.002 | 0.066 ± 0.030         | 0.758 ± 0.007  | 0.325 ± 0.018         | 0.455 ± 0.026      |
| HSC-CQR simple       | 0.796 ± 0.005 | 0.794 ± 0.006       | 0.024 ± 0.002 | 0.074 ± 0.014         | 0.758 ± 0.004  | 0.328 ± 0.017         | 0.456 ± 0.026      |
| HSC                  | 0.803 ± 0.005 | 0.772 ± 0.007       | 0.036 ± 0.001 | 0.116 ± 0.027         | 0.747 ± 0.007  | 0.286 ± 0.011         | 0.490 ± 0.019      |
| HSC simple           | 0.816 ± 0.004 | 0.800 ± 0.013       | 0.040 ± 0.003 | 0.085 ± 0.029         | 0.755 ± 0.007  | 0.296 ± 0.012         | 0.491 ± 0.018      |
| CQR                  | 0.791 ± 0.009 | 0.779 ± 0.005       | 0.050 ± 0.003 | 0.190 ± 0.034         | 0.709 ± 0.012  | 0.332 ± 0.010         | 0.455 ± 0.025      |
| Self-CQR             | 0.783 ± 0.005 | 0.742 ± 0.009       | 0.029 ± 0.002 | 0.145 ± 0.035         | 0.741 ± 0.007  | 0.325 ± 0.019         | 0.460 ± 0.025      |
| ACI-CQR              | 0.801 ± 0.003 | 0.782 ± 0.005       | 0.022 ± 0.004 | 0.029 ± 0.013         | 0.767 ± 0.006  | 0.332 ± 0.017         | 0.455 ± 0.025      |
| TQA-B-CQR            | 0.820 ± 0.007 | 0.794 ± 0.005       | 0.043 ± 0.001 | 0.064 ± 0.029         | 0.760 ± 0.009  | 0.332 ± 0.013         | 0.458 ± 0.024      |
| GHCP-CQR             | 0.793 ± 0.009 | 0.798 ± 0.006       | 0.049 ± 0.002 | 0.183 ± 0.028         | 0.714 ± 0.011  | 0.333 ± 0.011         | 0.455 ± 0.026      |
| QShrink-CQR          | 0.791 ± 0.009 | 0.780 ± 0.005       | 0.035 ± 0.010 | 0.134 ± 0.046         | 0.735 ± 0.024  | 0.327 ± 0.015         | 0.454 ± 0.026      |
| MLP-Gauss            | 0.891 ± 0.012 | 0.888 ± 0.015       | 0.097 ± 0.011 | 0.019 ± 0.016         | 0.804 ± 0.012  | 0.400 ± 0.035         | 0.509 ± 0.031      |
| CQR (MLP)            | 0.793 ± 0.005 | 0.784 ± 0.007       | 0.052 ± 0.008 | 0.195 ± 0.030         | 0.704 ± 0.023  | 0.337 ± 0.016         | 0.460 ± 0.026      |
| HSC-CQR (MLP)        | 0.795 ± 0.008 | 0.808 ± 0.022       | 0.028 ± 0.001 | 0.100 ± 0.043         | 0.751 ± 0.013  | 0.328 ± 0.020         | 0.460 ± 0.024      |
| ACI                  | 0.822 ± 0.007 | 0.794 ± 0.014       | 0.067 ± 0.011 | 0.193 ± 0.049         | 0.721 ± 0.017  | 0.297 ± 0.012         | 0.486 ± 0.017      |
| Self-CP              | 0.811 ± 0.004 | 0.806 ± 0.008       | 0.035 ± 0.001 | 0.076 ± 0.016         | 0.759 ± 0.006  | 0.301 ± 0.013         | 0.502 ± 0.022      |
| SCP-stage            | 0.799 ± 0.018 | 0.789 ± 0.017       | 0.132 ± 0.009 | 0.329 ± 0.060         | 0.573 ± 0.034  | 0.312 ± 0.017         | 0.492 ± 0.019      |
| SCP                  | 0.798 ± 0.018 | 0.762 ± 0.017       | 0.132 ± 0.009 | 0.326 ± 0.057         | 0.573 ± 0.033  | 0.311 ± 0.017         | 0.492 ± 0.019      |
| Mondrian-usage       | 0.792 ± 0.016 | 0.783 ± 0.014       | 0.131 ± 0.009 | 0.352 ± 0.059         | 0.577 ± 0.021  | 0.287 ± 0.023         | 0.506 ± 0.021      |
| Naive+SCP            | 0.803 ± 0.018 | 0.793 ± 0.014       | 0.133 ± 0.007 | 0.334 ± 0.052         | 0.580 ± 0.025  | 0.443 ± 0.031         | 0.738 ± 0.025      |
| Raw-SCP              | 0.788 ± 0.011 | 0.748 ± 0.018       | 0.192 ± 0.011 | 0.330 ± 0.022         | 0.424 ± 0.034  | 0.367 ± 0.024         | 0.658 ± 0.028      |
| HSC-CQR fixed-κ      | 0.794 ± 0.005 | 0.792 ± 0.006       | 0.021 ± 0.001 | 0.064 ± 0.014         | 0.762 ± 0.006  | 0.327 ± 0.018         | 0.456 ± 0.027      |


**Table S9. UCI, nominal 80 %.**

| Method               | Coverage      | Coverage (week 1)   | MACD          | Under-covered share   | P10 coverage   | Rel. width (median)   | Rel. IS (median)   |
|:---------------------|:--------------|:--------------------|:--------------|:----------------------|:---------------|:----------------------|:-------------------|
| HSC-CQR recency      | 0.798 ± 0.003 | 0.803 ± 0.006       | 0.013 ± 0.002 | 0.006 ± 0.009         | 0.778 ± 0.003  | 0.211 ± 0.009         | 0.301 ± 0.010      |
| HSC-SSC-CQR          | 0.805 ± 0.005 | 0.812 ± 0.014       | 0.018 ± 0.002 | 0.017 ± 0.016         | 0.781 ± 0.009  | 0.213 ± 0.008         | 0.301 ± 0.009      |
| SSC-CQR              | 0.813 ± 0.023 | 0.814 ± 0.022       | 0.062 ± 0.003 | 0.145 ± 0.051         | 0.720 ± 0.032  | 0.227 ± 0.017         | 0.301 ± 0.011      |
| HSC-CQR simple (cov) | 0.798 ± 0.006 | 0.810 ± 0.008       | 0.017 ± 0.004 | 0.023 ± 0.030         | 0.771 ± 0.008  | 0.211 ± 0.009         | 0.300 ± 0.010      |
| QShrink-CQR (cov)    | 0.795 ± 0.007 | 0.797 ± 0.013       | 0.019 ± 0.005 | 0.032 ± 0.042         | 0.768 ± 0.011  | 0.210 ± 0.009         | 0.300 ± 0.009      |
| ACI-CQR (cov)        | 0.805 ± 0.005 | 0.805 ± 0.009       | 0.013 ± 0.008 | 0.006 ± 0.014         | 0.788 ± 0.006  | 0.215 ± 0.005         | 0.304 ± 0.006      |
| HSC-CQR              | 0.797 ± 0.007 | 0.795 ± 0.012       | 0.020 ± 0.004 | 0.036 ± 0.033         | 0.769 ± 0.011  | 0.212 ± 0.009         | 0.299 ± 0.010      |
| HSC-CQR simple       | 0.800 ± 0.006 | 0.813 ± 0.008       | 0.020 ± 0.003 | 0.029 ± 0.025         | 0.772 ± 0.009  | 0.212 ± 0.009         | 0.300 ± 0.010      |
| HSC                  | 0.808 ± 0.006 | 0.798 ± 0.013       | 0.027 ± 0.001 | 0.040 ± 0.026         | 0.766 ± 0.007  | 0.196 ± 0.005         | 0.317 ± 0.011      |
| HSC simple           | 0.815 ± 0.006 | 0.815 ± 0.016       | 0.031 ± 0.004 | 0.034 ± 0.029         | 0.771 ± 0.005  | 0.203 ± 0.007         | 0.317 ± 0.011      |
| CQR                  | 0.798 ± 0.017 | 0.799 ± 0.018       | 0.046 ± 0.009 | 0.141 ± 0.086         | 0.739 ± 0.026  | 0.217 ± 0.015         | 0.301 ± 0.008      |
| Self-CQR             | 0.789 ± 0.004 | 0.764 ± 0.007       | 0.023 ± 0.003 | 0.059 ± 0.023         | 0.756 ± 0.003  | 0.209 ± 0.008         | 0.303 ± 0.008      |
| ACI-CQR              | 0.805 ± 0.005 | 0.801 ± 0.013       | 0.018 ± 0.004 | 0.011 ± 0.015         | 0.781 ± 0.005  | 0.214 ± 0.010         | 0.300 ± 0.010      |
| TQA-B-CQR            | 0.807 ± 0.012 | 0.806 ± 0.007       | 0.042 ± 0.004 | 0.109 ± 0.049         | 0.746 ± 0.023  | 0.221 ± 0.008         | 0.303 ± 0.007      |
| GHCP-CQR             | 0.804 ± 0.017 | 0.824 ± 0.012       | 0.045 ± 0.007 | 0.126 ± 0.080         | 0.748 ± 0.024  | 0.220 ± 0.015         | 0.301 ± 0.008      |
| QShrink-CQR          | 0.797 ± 0.011 | 0.801 ± 0.016       | 0.026 ± 0.007 | 0.059 ± 0.062         | 0.765 ± 0.018  | 0.211 ± 0.009         | 0.300 ± 0.010      |
| MLP-Gauss            | 0.848 ± 0.012 | 0.865 ± 0.022       | 0.058 ± 0.009 | 0.029 ± 0.020         | 0.790 ± 0.015  | 0.241 ± 0.026         | 0.323 ± 0.026      |
| CQR (MLP)            | 0.800 ± 0.014 | 0.808 ± 0.008       | 0.041 ± 0.010 | 0.137 ± 0.096         | 0.746 ± 0.019  | 0.218 ± 0.016         | 0.304 ± 0.014      |
| HSC-CQR (MLP)        | 0.794 ± 0.010 | 0.835 ± 0.014       | 0.023 ± 0.007 | 0.057 ± 0.063         | 0.764 ± 0.011  | 0.216 ± 0.014         | 0.304 ± 0.012      |
| ACI                  | 0.818 ± 0.012 | 0.808 ± 0.006       | 0.062 ± 0.017 | 0.196 ± 0.042         | 0.717 ± 0.016  | 0.210 ± 0.012         | 0.315 ± 0.011      |
| Self-CP              | 0.814 ± 0.005 | 0.826 ± 0.007       | 0.030 ± 0.004 | 0.029 ± 0.020         | 0.775 ± 0.004  | 0.203 ± 0.006         | 0.318 ± 0.010      |
| SCP-stage            | 0.802 ± 0.025 | 0.806 ± 0.007       | 0.125 ± 0.005 | 0.297 ± 0.041         | 0.588 ± 0.037  | 0.227 ± 0.014         | 0.322 ± 0.008      |
| SCP                  | 0.802 ± 0.024 | 0.777 ± 0.019       | 0.125 ± 0.005 | 0.297 ± 0.041         | 0.588 ± 0.038  | 0.227 ± 0.014         | 0.321 ± 0.009      |
| Naive+SCP            | 0.807 ± 0.013 | 0.802 ± 0.019       | 0.101 ± 0.010 | 0.276 ± 0.044         | 0.624 ± 0.032  | 0.296 ± 0.016         | 0.449 ± 0.021      |
| Raw-SCP              | 0.809 ± 0.030 | 0.788 ± 0.037       | 0.202 ± 0.013 | 0.286 ± 0.044         | 0.426 ± 0.088  | 0.384 ± 0.052         | 0.526 ± 0.055      |
| HSC-CQR fixed-κ      | 0.799 ± 0.006 | 0.812 ± 0.008       | 0.018 ± 0.004 | 0.023 ± 0.030         | 0.772 ± 0.008  | 0.211 ± 0.009         | 0.300 ± 0.010      |


**Table S10. BDG2 leave-site-out (5 site folds).**

| Method               | Coverage      | Coverage (week 1)   | MACD          | Under-covered share   | P10 coverage   | Rel. width (median)   | Rel. IS (median)   |
|:---------------------|:--------------|:--------------------|:--------------|:----------------------|:---------------|:----------------------|:-------------------|
| HSC-CQR recency      | 0.896 ± 0.004 | 0.875 ± 0.040       | 0.012 ± 0.002 | 0.004 ± 0.005         | 0.877 ± 0.005  | 0.438 ± 0.138         | 0.614 ± 0.205      |
| HSC-SSC-CQR          | 0.898 ± 0.003 | 0.880 ± 0.040       | 0.015 ± 0.001 | 0.008 ± 0.008         | 0.875 ± 0.004  | 0.439 ± 0.138         | 0.615 ± 0.207      |
| SSC-CQR              | 0.896 ± 0.017 | 0.876 ± 0.045       | 0.032 ± 0.005 | 0.138 ± 0.109         | 0.848 ± 0.018  | 0.426 ± 0.118         | 0.616 ± 0.207      |
| HSC-CQR simple (cov) | 0.895 ± 0.004 | 0.875 ± 0.043       | 0.016 ± 0.002 | 0.012 ± 0.008         | 0.870 ± 0.006  | 0.434 ± 0.134         | 0.613 ± 0.205      |
| QShrink-CQR (cov)    | 0.896 ± 0.006 | 0.875 ± 0.044       | 0.016 ± 0.002 | 0.017 ± 0.019         | 0.870 ± 0.008  | 0.433 ± 0.134         | 0.614 ± 0.206      |
| ACI-CQR (cov)        | 0.895 ± 0.012 | 0.872 ± 0.047       | 0.022 ± 0.003 | 0.042 ± 0.032         | 0.863 ± 0.011  | 0.426 ± 0.122         | 0.612 ± 0.203      |
| HSC-CQR              | 0.890 ± 0.007 | 0.862 ± 0.040       | 0.020 ± 0.004 | 0.054 ± 0.032         | 0.862 ± 0.009  | 0.423 ± 0.127         | 0.612 ± 0.204      |
| HSC-CQR simple       | 0.895 ± 0.008 | 0.873 ± 0.045       | 0.019 ± 0.003 | 0.039 ± 0.028         | 0.864 ± 0.011  | 0.428 ± 0.126         | 0.612 ± 0.204      |
| HSC                  | 0.896 ± 0.014 | 0.851 ± 0.043       | 0.030 ± 0.006 | 0.119 ± 0.090         | 0.851 ± 0.020  | 0.466 ± 0.159         | 0.770 ± 0.340      |
| HSC simple           | 0.913 ± 0.014 | 0.881 ± 0.057       | 0.032 ± 0.005 | 0.039 ± 0.030         | 0.871 ± 0.015  | 0.498 ± 0.142         | 0.772 ± 0.327      |
| CQR                  | 0.890 ± 0.024 | 0.872 ± 0.049       | 0.040 ± 0.007 | 0.214 ± 0.140         | 0.832 ± 0.024  | 0.417 ± 0.109         | 0.616 ± 0.206      |
| Self-CQR             | 0.890 ± 0.003 | 0.843 ± 0.038       | 0.021 ± 0.001 | 0.054 ± 0.013         | 0.859 ± 0.004  | 0.439 ± 0.143         | 0.621 ± 0.209      |
| ACI-CQR              | 0.894 ± 0.012 | 0.872 ± 0.047       | 0.023 ± 0.004 | 0.057 ± 0.058         | 0.860 ± 0.017  | 0.425 ± 0.119         | 0.612 ± 0.203      |
| TQA-B-CQR            | 0.892 ± 0.025 | 0.873 ± 0.047       | 0.041 ± 0.006 | 0.216 ± 0.144         | 0.835 ± 0.022  | 0.418 ± 0.111         | 0.617 ± 0.203      |
| GHCP-CQR             | 0.891 ± 0.024 | 0.873 ± 0.048       | 0.040 ± 0.006 | 0.208 ± 0.142         | 0.834 ± 0.025  | 0.419 ± 0.109         | 0.617 ± 0.206      |
| QShrink-CQR          | 0.896 ± 0.015 | 0.874 ± 0.046       | 0.027 ± 0.005 | 0.085 ± 0.069         | 0.858 ± 0.018  | 0.428 ± 0.125         | 0.614 ± 0.205      |
| QR-LGBM              | 0.865 ± 0.021 | 0.850 ± 0.045       | 0.047 ± 0.014 | 0.365 ± 0.197         | 0.807 ± 0.019  | 0.397 ± 0.112         | 0.619 ± 0.209      |
| MLP-QR               | 0.889 ± 0.021 | 0.863 ± 0.045       | 0.040 ± 0.004 | 0.224 ± 0.113         | 0.829 ± 0.026  | 0.433 ± 0.130         | 0.629 ± 0.213      |
| MLP-Gauss            | 0.931 ± 0.026 | 0.914 ± 0.046       | 0.048 ± 0.012 | 0.060 ± 0.061         | 0.876 ± 0.033  | 0.539 ± 0.097         | 0.704 ± 0.180      |
| CQR (MLP)            | 0.892 ± 0.019 | 0.872 ± 0.045       | 0.040 ± 0.004 | 0.204 ± 0.108         | 0.832 ± 0.022  | 0.436 ± 0.132         | 0.629 ± 0.214      |
| HSC-CQR (MLP)        | 0.897 ± 0.009 | 0.868 ± 0.041       | 0.021 ± 0.003 | 0.040 ± 0.034         | 0.866 ± 0.011  | 0.442 ± 0.143         | 0.627 ± 0.212      |
| ACI                  | 0.910 ± 0.037 | 0.877 ± 0.073       | 0.059 ± 0.014 | 0.219 ± 0.201         | 0.831 ± 0.038  | 0.500 ± 0.035         | 0.794 ± 0.332      |
| Self-CP              | 0.906 ± 0.005 | 0.879 ± 0.044       | 0.025 ± 0.003 | 0.046 ± 0.028         | 0.866 ± 0.009  | 0.510 ± 0.171         | 0.794 ± 0.348      |
| SCP-stage            | 0.884 ± 0.058 | 0.874 ± 0.075       | 0.095 ± 0.025 | 0.307 ± 0.201         | 0.735 ± 0.096  | 0.510 ± 0.032         | 0.829 ± 0.352      |
| SCP                  | 0.884 ± 0.058 | 0.849 ± 0.074       | 0.094 ± 0.025 | 0.307 ± 0.202         | 0.737 ± 0.095  | 0.510 ± 0.032         | 0.834 ± 0.349      |
| Mondrian-usage       | 0.879 ± 0.061 | 0.867 ± 0.079       | 0.097 ± 0.029 | 0.315 ± 0.195         | 0.736 ± 0.092  | 0.470 ± 0.059         | 0.847 ± 0.358      |
| Naive+SCP            | 0.896 ± 0.047 | 0.881 ± 0.065       | 0.086 ± 0.009 | 0.271 ± 0.161         | 0.761 ± 0.086  | 0.758 ± 0.047         | 1.131 ± 0.343      |
| Raw-SCP              | 0.894 ± 0.037 | 0.857 ± 0.025       | 0.121 ± 0.019 | 0.226 ± 0.067         | 0.670 ± 0.127  | 0.874 ± 0.574         | 1.282 ± 0.614      |
| HSC -stage           | 0.897 ± 0.012 | 0.835 ± 0.043       | 0.029 ± 0.005 | 0.102 ± 0.064         | 0.852 ± 0.018  | 0.466 ± 0.167         | 0.773 ± 0.338      |
| HSC -kNN             | 0.915 ± 0.014 | 0.900 ± 0.058       | 0.032 ± 0.005 | 0.034 ± 0.026         | 0.874 ± 0.015  | 0.507 ± 0.141         | 0.773 ± 0.327      |
| HSC -shrink          | 0.836 ± 0.051 | 0.816 ± 0.050       | 0.096 ± 0.032 | 0.483 ± 0.222         | 0.693 ± 0.066  | 0.394 ± 0.073         | 0.829 ± 0.363      |
| HSC-CQR -stage       | 0.891 ± 0.007 | 0.867 ± 0.042       | 0.019 ± 0.004 | 0.048 ± 0.034         | 0.863 ± 0.010  | 0.424 ± 0.128         | 0.612 ± 0.204      |
| HSC-CQR -kNN         | 0.895 ± 0.008 | 0.874 ± 0.045       | 0.020 ± 0.003 | 0.040 ± 0.033         | 0.863 ± 0.010  | 0.429 ± 0.126         | 0.612 ± 0.204      |
| HSC-CQR -shrink      | 0.880 ± 0.020 | 0.859 ± 0.043       | 0.039 ± 0.010 | 0.244 ± 0.161         | 0.828 ± 0.022  | 0.408 ± 0.112         | 0.617 ± 0.206      |
| HSC-CQR fixed-κ      | 0.895 ± 0.004 | 0.875 ± 0.043       | 0.016 ± 0.002 | 0.012 ± 0.008         | 0.870 ± 0.006  | 0.434 ± 0.134         | 0.613 ± 0.205      |


**Table S11. BDG2 → UCI transfer (no weather; 3 seeds).**

| Method               | Coverage      | Coverage (week 1)   | MACD          | Under-covered share   | P10 coverage   | Rel. width (median)   | Rel. IS (median)   |
|:---------------------|:--------------|:--------------------|:--------------|:----------------------|:---------------|:----------------------|:-------------------|
| HSC-CQR recency      | 0.900 ± 0.001 | 0.902 ± 0.010       | 0.009 ± 0.000 | 0.000 ± 0.000         | 0.885 ± 0.002  | 0.335 ± 0.013         | 0.436 ± 0.013      |
| HSC-SSC-CQR          | 0.901 ± 0.001 | 0.908 ± 0.010       | 0.012 ± 0.000 | 0.004 ± 0.006         | 0.883 ± 0.001  | 0.332 ± 0.016         | 0.436 ± 0.012      |
| SSC-CQR              | 0.912 ± 0.004 | 0.915 ± 0.015       | 0.023 ± 0.001 | 0.007 ± 0.012         | 0.878 ± 0.006  | 0.338 ± 0.018         | 0.434 ± 0.015      |
| HSC-CQR simple (cov) | 0.901 ± 0.001 | 0.906 ± 0.010       | 0.011 ± 0.000 | 0.004 ± 0.006         | 0.884 ± 0.003  | 0.332 ± 0.015         | 0.435 ± 0.014      |
| QShrink-CQR (cov)    | 0.901 ± 0.000 | 0.907 ± 0.012       | 0.011 ± 0.000 | 0.004 ± 0.006         | 0.884 ± 0.001  | 0.333 ± 0.015         | 0.434 ± 0.014      |
| ACI-CQR (cov)        | 0.906 ± 0.002 | 0.910 ± 0.015       | 0.015 ± 0.001 | 0.011 ± 0.011         | 0.884 ± 0.003  | 0.331 ± 0.014         | 0.432 ± 0.016      |
| HSC-CQR              | 0.900 ± 0.001 | 0.898 ± 0.014       | 0.014 ± 0.002 | 0.011 ± 0.011         | 0.879 ± 0.003  | 0.328 ± 0.013         | 0.433 ± 0.016      |
| HSC-CQR simple       | 0.903 ± 0.001 | 0.906 ± 0.012       | 0.013 ± 0.000 | 0.007 ± 0.006         | 0.883 ± 0.003  | 0.332 ± 0.017         | 0.433 ± 0.016      |
| HSC                  | 0.925 ± 0.004 | 0.899 ± 0.007       | 0.031 ± 0.004 | 0.021 ± 0.018         | 0.893 ± 0.005  | 0.370 ± 0.021         | 0.497 ± 0.030      |
| HSC simple           | 0.928 ± 0.004 | 0.913 ± 0.012       | 0.034 ± 0.004 | 0.014 ± 0.006         | 0.895 ± 0.006  | 0.382 ± 0.011         | 0.503 ± 0.023      |
| CQR                  | 0.910 ± 0.004 | 0.910 ± 0.016       | 0.026 ± 0.003 | 0.035 ± 0.006         | 0.877 ± 0.007  | 0.338 ± 0.017         | 0.432 ± 0.015      |
| Self-CQR             | 0.890 ± 0.002 | 0.858 ± 0.012       | 0.017 ± 0.002 | 0.025 ± 0.016         | 0.864 ± 0.003  | 0.327 ± 0.015         | 0.443 ± 0.014      |
| ACI-CQR              | 0.906 ± 0.001 | 0.910 ± 0.015       | 0.016 ± 0.002 | 0.018 ± 0.006         | 0.882 ± 0.006  | 0.333 ± 0.015         | 0.432 ± 0.016      |
| TQA-B-CQR            | 0.908 ± 0.005 | 0.908 ± 0.016       | 0.025 ± 0.003 | 0.028 ± 0.006         | 0.876 ± 0.008  | 0.336 ± 0.014         | 0.431 ± 0.016      |
| GHCP-CQR             | 0.911 ± 0.004 | 0.909 ± 0.013       | 0.027 ± 0.003 | 0.035 ± 0.006         | 0.878 ± 0.006  | 0.340 ± 0.017         | 0.432 ± 0.015      |
| QShrink-CQR          | 0.907 ± 0.002 | 0.912 ± 0.015       | 0.016 ± 0.001 | 0.011 ± 0.011         | 0.883 ± 0.004  | 0.334 ± 0.017         | 0.432 ± 0.016      |
| QR-LGBM              | 0.888 ± 0.003 | 0.889 ± 0.013       | 0.027 ± 0.003 | 0.102 ± 0.037         | 0.852 ± 0.006  | 0.319 ± 0.016         | 0.431 ± 0.017      |
| MLP-QR               | 0.904 ± 0.003 | 0.912 ± 0.018       | 0.024 ± 0.003 | 0.042 ± 0.021         | 0.867 ± 0.008  | 0.324 ± 0.018         | 0.422 ± 0.018      |
| MLP-Gauss            | 0.955 ± 0.014 | 0.958 ± 0.017       | 0.058 ± 0.013 | 0.011 ± 0.011         | 0.924 ± 0.017  | 0.469 ± 0.068         | 0.526 ± 0.058      |
| CQR (MLP)            | 0.906 ± 0.007 | 0.914 ± 0.009       | 0.024 ± 0.003 | 0.039 ± 0.030         | 0.870 ± 0.016  | 0.327 ± 0.022         | 0.421 ± 0.017      |
| HSC-CQR (MLP)        | 0.903 ± 0.004 | 0.914 ± 0.015       | 0.015 ± 0.002 | 0.004 ± 0.006         | 0.880 ± 0.005  | 0.318 ± 0.023         | 0.422 ± 0.018      |
| ACI                  | 0.943 ± 0.010 | 0.923 ± 0.015       | 0.053 ± 0.007 | 0.042 ± 0.000         | 0.886 ± 0.017  | 0.443 ± 0.014         | 0.525 ± 0.015      |
| Self-CP              | 0.918 ± 0.001 | 0.899 ± 0.008       | 0.025 ± 0.001 | 0.011 ± 0.011         | 0.892 ± 0.004  | 0.370 ± 0.010         | 0.505 ± 0.027      |
| SCP-stage            | 0.942 ± 0.012 | 0.921 ± 0.017       | 0.084 ± 0.006 | 0.091 ± 0.032         | 0.854 ± 0.056  | 0.546 ± 0.033         | 0.594 ± 0.011      |
| SCP                  | 0.941 ± 0.012 | 0.897 ± 0.020       | 0.082 ± 0.006 | 0.091 ± 0.032         | 0.855 ± 0.056  | 0.545 ± 0.034         | 0.598 ± 0.013      |
| Naive+SCP            | 0.960 ± 0.010 | 0.956 ± 0.011       | 0.086 ± 0.003 | 0.070 ± 0.026         | 0.892 ± 0.026  | 0.778 ± 0.039         | 0.796 ± 0.030      |
| Raw-SCP              | 0.790 ± 0.018 | 0.750 ± 0.007       | 0.188 ± 0.014 | 0.421 ± 0.018         | 0.370 ± 0.024  | 0.387 ± 0.016         | 0.747 ± 0.079      |
| HSC -stage           | 0.922 ± 0.004 | 0.889 ± 0.017       | 0.028 ± 0.003 | 0.014 ± 0.006         | 0.894 ± 0.003  | 0.362 ± 0.017         | 0.500 ± 0.030      |
| HSC -kNN             | 0.930 ± 0.004 | 0.931 ± 0.010       | 0.035 ± 0.004 | 0.014 ± 0.006         | 0.897 ± 0.007  | 0.391 ± 0.012         | 0.504 ± 0.030      |
| HSC -shrink          | 0.919 ± 0.020 | 0.878 ± 0.019       | 0.066 ± 0.002 | 0.161 ± 0.070         | 0.812 ± 0.028  | 0.419 ± 0.056         | 0.529 ± 0.024      |
| HSC-CQR -stage       | 0.902 ± 0.002 | 0.902 ± 0.012       | 0.015 ± 0.002 | 0.011 ± 0.000         | 0.878 ± 0.005  | 0.328 ± 0.017         | 0.433 ± 0.016      |
| HSC-CQR -kNN         | 0.904 ± 0.001 | 0.910 ± 0.014       | 0.014 ± 0.001 | 0.007 ± 0.006         | 0.883 ± 0.004  | 0.333 ± 0.016         | 0.433 ± 0.015      |
| HSC-CQR -shrink      | 0.902 ± 0.003 | 0.897 ± 0.013       | 0.026 ± 0.002 | 0.060 ± 0.012         | 0.863 ± 0.007  | 0.329 ± 0.013         | 0.433 ± 0.016      |
| HSC-CQR fixed-κ      | 0.901 ± 0.001 | 0.906 ± 0.010       | 0.012 ± 0.000 | 0.004 ± 0.006         | 0.885 ± 0.003  | 0.332 ± 0.015         | 0.434 ± 0.015      |


**Table S12. UCI → BDG2 transfer (no weather; 3 seeds).**

| Method               | Coverage      | Coverage (week 1)   | MACD          | Under-covered share   | P10 coverage   | Rel. width (median)   | Rel. IS (median)   |
|:---------------------|:--------------|:--------------------|:--------------|:----------------------|:---------------|:----------------------|:-------------------|
| HSC-CQR recency      | 0.899 ± 0.002 | 0.863 ± 0.006       | 0.014 ± 0.000 | 0.013 ± 0.006         | 0.877 ± 0.002  | 0.449 ± 0.022         | 0.627 ± 0.023      |
| HSC-SSC-CQR          | 0.902 ± 0.004 | 0.864 ± 0.006       | 0.018 ± 0.001 | 0.024 ± 0.005         | 0.874 ± 0.003  | 0.448 ± 0.031         | 0.629 ± 0.029      |
| SSC-CQR              | 0.890 ± 0.008 | 0.863 ± 0.010       | 0.040 ± 0.002 | 0.217 ± 0.035         | 0.823 ± 0.008  | 0.426 ± 0.010         | 0.627 ± 0.029      |
| HSC-CQR simple (cov) | 0.898 ± 0.002 | 0.856 ± 0.005       | 0.018 ± 0.001 | 0.029 ± 0.005         | 0.869 ± 0.003  | 0.441 ± 0.028         | 0.626 ± 0.027      |
| QShrink-CQR (cov)    | 0.899 ± 0.003 | 0.859 ± 0.008       | 0.018 ± 0.001 | 0.029 ± 0.004         | 0.870 ± 0.002  | 0.443 ± 0.024         | 0.627 ± 0.024      |
| ACI-CQR (cov)        | 0.889 ± 0.010 | 0.843 ± 0.009       | 0.024 ± 0.012 | 0.088 ± 0.150         | 0.852 ± 0.032  | 0.424 ± 0.027         | 0.626 ± 0.025      |
| HSC-CQR              | 0.888 ± 0.003 | 0.836 ± 0.006       | 0.023 ± 0.000 | 0.086 ± 0.018         | 0.853 ± 0.004  | 0.422 ± 0.019         | 0.625 ± 0.020      |
| HSC-CQR simple       | 0.892 ± 0.004 | 0.846 ± 0.012       | 0.021 ± 0.002 | 0.059 ± 0.017         | 0.859 ± 0.005  | 0.429 ± 0.015         | 0.622 ± 0.022      |
| HSC                  | 0.897 ± 0.010 | 0.846 ± 0.033       | 0.028 ± 0.002 | 0.099 ± 0.057         | 0.852 ± 0.012  | 0.461 ± 0.017         | 0.731 ± 0.049      |
| HSC simple           | 0.903 ± 0.007 | 0.858 ± 0.028       | 0.028 ± 0.002 | 0.082 ± 0.041         | 0.858 ± 0.011  | 0.473 ± 0.008         | 0.728 ± 0.039      |
| CQR                  | 0.864 ± 0.008 | 0.838 ± 0.010       | 0.057 ± 0.002 | 0.390 ± 0.061         | 0.779 ± 0.003  | 0.397 ± 0.006         | 0.627 ± 0.027      |
| Self-CQR             | 0.898 ± 0.003 | 0.841 ± 0.005       | 0.021 ± 0.000 | 0.054 ± 0.021         | 0.864 ± 0.001  | 0.456 ± 0.026         | 0.637 ± 0.023      |
| ACI-CQR              | 0.881 ± 0.003 | 0.839 ± 0.009       | 0.036 ± 0.007 | 0.216 ± 0.079         | 0.827 ± 0.019  | 0.411 ± 0.019         | 0.623 ± 0.022      |
| TQA-B-CQR            | 0.873 ± 0.004 | 0.847 ± 0.008       | 0.052 ± 0.001 | 0.338 ± 0.024         | 0.792 ± 0.009  | 0.403 ± 0.014         | 0.628 ± 0.027      |
| GHCP-CQR             | 0.872 ± 0.007 | 0.847 ± 0.010       | 0.054 ± 0.002 | 0.338 ± 0.047         | 0.785 ± 0.002  | 0.405 ± 0.005         | 0.625 ± 0.026      |
| QShrink-CQR          | 0.889 ± 0.009 | 0.849 ± 0.015       | 0.028 ± 0.009 | 0.126 ± 0.084         | 0.845 ± 0.019  | 0.420 ± 0.003         | 0.623 ± 0.026      |
| QR-LGBM              | 0.837 ± 0.006 | 0.808 ± 0.005       | 0.072 ± 0.003 | 0.556 ± 0.040         | 0.752 ± 0.007  | 0.375 ± 0.011         | 0.634 ± 0.025      |
| MLP-QR               | 0.850 ± 0.022 | 0.833 ± 0.021       | 0.063 ± 0.012 | 0.447 ± 0.125         | 0.771 ± 0.017  | 0.382 ± 0.016         | 0.639 ± 0.036      |
| MLP-Gauss            | 0.887 ± 0.005 | 0.874 ± 0.016       | 0.050 ± 0.004 | 0.270 ± 0.025         | 0.809 ± 0.011  | 0.457 ± 0.022         | 0.720 ± 0.063      |
| CQR (MLP)            | 0.871 ± 0.012 | 0.841 ± 0.018       | 0.052 ± 0.005 | 0.344 ± 0.063         | 0.793 ± 0.005  | 0.399 ± 0.011         | 0.633 ± 0.033      |
| HSC-CQR (MLP)        | 0.892 ± 0.006 | 0.858 ± 0.012       | 0.021 ± 0.003 | 0.059 ± 0.020         | 0.859 ± 0.007  | 0.423 ± 0.015         | 0.628 ± 0.033      |
| ACI                  | 0.885 ± 0.011 | 0.821 ± 0.007       | 0.055 ± 0.009 | 0.327 ± 0.066         | 0.806 ± 0.025  | 0.423 ± 0.031         | 0.714 ± 0.055      |
| Self-CP              | 0.905 ± 0.004 | 0.871 ± 0.009       | 0.026 ± 0.000 | 0.067 ± 0.016         | 0.863 ± 0.007  | 0.501 ± 0.014         | 0.740 ± 0.051      |
| SCP-stage            | 0.825 ± 0.025 | 0.813 ± 0.011       | 0.122 ± 0.014 | 0.475 ± 0.087         | 0.617 ± 0.037  | 0.391 ± 0.042         | 0.732 ± 0.068      |
| SCP                  | 0.825 ± 0.025 | 0.787 ± 0.024       | 0.122 ± 0.014 | 0.475 ± 0.087         | 0.619 ± 0.036  | 0.390 ± 0.043         | 0.729 ± 0.063      |
| Naive+SCP            | 0.829 ± 0.013 | 0.816 ± 0.008       | 0.120 ± 0.007 | 0.482 ± 0.042         | 0.619 ± 0.027  | 0.497 ± 0.024         | 0.996 ± 0.063      |
| Raw-SCP              | 0.946 ± 0.021 | 0.917 ± 0.022       | 0.107 ± 0.008 | 0.119 ± 0.063         | 0.825 ± 0.088  | 1.506 ± 0.271         | 1.735 ± 0.217      |
| HSC -stage           | 0.897 ± 0.010 | 0.838 ± 0.040       | 0.028 ± 0.002 | 0.094 ± 0.055         | 0.852 ± 0.014  | 0.462 ± 0.017         | 0.734 ± 0.049      |
| HSC -kNN             | 0.904 ± 0.006 | 0.873 ± 0.018       | 0.028 ± 0.002 | 0.079 ± 0.035         | 0.861 ± 0.011  | 0.478 ± 0.006         | 0.723 ± 0.037      |
| HSC -shrink          | 0.773 ± 0.016 | 0.740 ± 0.010       | 0.153 ± 0.013 | 0.661 ± 0.037         | 0.581 ± 0.022  | 0.298 ± 0.004         | 0.821 ± 0.073      |
| HSC-CQR -stage       | 0.891 ± 0.003 | 0.843 ± 0.008       | 0.022 ± 0.002 | 0.060 ± 0.010         | 0.858 ± 0.002  | 0.423 ± 0.014         | 0.623 ± 0.022      |
| HSC-CQR -kNN         | 0.893 ± 0.003 | 0.851 ± 0.012       | 0.021 ± 0.003 | 0.058 ± 0.017         | 0.860 ± 0.005  | 0.429 ± 0.015         | 0.623 ± 0.022      |
| HSC-CQR -shrink      | 0.860 ± 0.007 | 0.827 ± 0.004       | 0.058 ± 0.001 | 0.417 ± 0.048         | 0.778 ± 0.003  | 0.393 ± 0.011         | 0.630 ± 0.025      |
| HSC-CQR fixed-κ      | 0.895 ± 0.003 | 0.851 ± 0.010       | 0.019 ± 0.000 | 0.038 ± 0.008         | 0.867 ± 0.003  | 0.434 ± 0.019         | 0.625 ± 0.024      |


**Table S13. BDG2 → BDG2 without weather features (reference; 3 seeds).**

| Method               | Coverage      | Coverage (week 1)   | MACD          | Under-covered share   | P10 coverage   | Rel. width (median)   | Rel. IS (median)   |
|:---------------------|:--------------|:--------------------|:--------------|:----------------------|:---------------|:----------------------|:-------------------|
| HSC-CQR recency      | 0.897 ± 0.001 | 0.880 ± 0.012       | 0.012 ± 0.001 | 0.003 ± 0.006         | 0.878 ± 0.002  | 0.410 ± 0.023         | 0.562 ± 0.020      |
| HSC-SSC-CQR          | 0.900 ± 0.002 | 0.886 ± 0.011       | 0.015 ± 0.001 | 0.003 ± 0.000         | 0.876 ± 0.002  | 0.407 ± 0.025         | 0.562 ± 0.019      |
| SSC-CQR              | 0.902 ± 0.002 | 0.887 ± 0.015       | 0.031 ± 0.001 | 0.101 ± 0.012         | 0.851 ± 0.003  | 0.407 ± 0.024         | 0.559 ± 0.023      |
| HSC-CQR simple (cov) | 0.897 ± 0.001 | 0.882 ± 0.012       | 0.015 ± 0.001 | 0.005 ± 0.005         | 0.874 ± 0.003  | 0.406 ± 0.023         | 0.560 ± 0.020      |
| QShrink-CQR (cov)    | 0.898 ± 0.002 | 0.883 ± 0.016       | 0.015 ± 0.001 | 0.005 ± 0.005         | 0.875 ± 0.002  | 0.406 ± 0.026         | 0.561 ± 0.021      |
| ACI-CQR (cov)        | 0.899 ± 0.001 | 0.883 ± 0.015       | 0.020 ± 0.001 | 0.031 ± 0.008         | 0.865 ± 0.001  | 0.404 ± 0.022         | 0.560 ± 0.020      |
| HSC-CQR              | 0.895 ± 0.002 | 0.872 ± 0.013       | 0.018 ± 0.003 | 0.024 ± 0.016         | 0.865 ± 0.004  | 0.398 ± 0.025         | 0.559 ± 0.021      |
| HSC-CQR simple       | 0.898 ± 0.001 | 0.882 ± 0.012       | 0.017 ± 0.001 | 0.015 ± 0.004         | 0.870 ± 0.001  | 0.403 ± 0.021         | 0.559 ± 0.020      |
| HSC                  | 0.905 ± 0.002 | 0.870 ± 0.009       | 0.029 ± 0.001 | 0.061 ± 0.004         | 0.859 ± 0.006  | 0.427 ± 0.011         | 0.656 ± 0.030      |
| HSC simple           | 0.915 ± 0.001 | 0.894 ± 0.015       | 0.031 ± 0.001 | 0.031 ± 0.005         | 0.870 ± 0.001  | 0.457 ± 0.017         | 0.661 ± 0.024      |
| CQR                  | 0.899 ± 0.003 | 0.883 ± 0.015       | 0.037 ± 0.001 | 0.150 ± 0.018         | 0.839 ± 0.003  | 0.399 ± 0.022         | 0.560 ± 0.022      |
| Self-CQR             | 0.889 ± 0.002 | 0.840 ± 0.015       | 0.021 ± 0.001 | 0.061 ± 0.013         | 0.857 ± 0.003  | 0.405 ± 0.022         | 0.569 ± 0.024      |
| ACI-CQR              | 0.898 ± 0.002 | 0.883 ± 0.015       | 0.022 ± 0.005 | 0.052 ± 0.044         | 0.861 ± 0.009  | 0.405 ± 0.021         | 0.559 ± 0.021      |
| TQA-B-CQR            | 0.901 ± 0.003 | 0.884 ± 0.015       | 0.038 ± 0.002 | 0.150 ± 0.013         | 0.840 ± 0.002  | 0.399 ± 0.017         | 0.558 ± 0.028      |
| GHCP-CQR             | 0.901 ± 0.003 | 0.884 ± 0.012       | 0.037 ± 0.001 | 0.144 ± 0.014         | 0.839 ± 0.002  | 0.401 ± 0.022         | 0.559 ± 0.022      |
| QShrink-CQR          | 0.902 ± 0.002 | 0.886 ± 0.015       | 0.022 ± 0.003 | 0.026 ± 0.023         | 0.865 ± 0.005  | 0.404 ± 0.022         | 0.560 ± 0.021      |
| QR-LGBM              | 0.877 ± 0.002 | 0.863 ± 0.011       | 0.040 ± 0.002 | 0.276 ± 0.035         | 0.818 ± 0.002  | 0.382 ± 0.021         | 0.562 ± 0.024      |
| MLP-QR               | 0.895 ± 0.005 | 0.880 ± 0.005       | 0.036 ± 0.001 | 0.164 ± 0.028         | 0.837 ± 0.001  | 0.396 ± 0.021         | 0.566 ± 0.034      |
| MLP-Gauss            | 0.937 ± 0.013 | 0.928 ± 0.021       | 0.050 ± 0.007 | 0.037 ± 0.022         | 0.878 ± 0.015  | 0.525 ± 0.104         | 0.658 ± 0.084      |
| CQR (MLP)            | 0.898 ± 0.003 | 0.881 ± 0.010       | 0.035 ± 0.001 | 0.144 ± 0.003         | 0.841 ± 0.005  | 0.398 ± 0.018         | 0.565 ± 0.034      |
| HSC-CQR (MLP)        | 0.898 ± 0.004 | 0.882 ± 0.002       | 0.021 ± 0.000 | 0.037 ± 0.013         | 0.866 ± 0.003  | 0.403 ± 0.022         | 0.565 ± 0.035      |
| ACI                  | 0.924 ± 0.002 | 0.894 ± 0.018       | 0.047 ± 0.000 | 0.088 ± 0.017         | 0.852 ± 0.003  | 0.483 ± 0.026         | 0.654 ± 0.031      |
| Self-CP              | 0.906 ± 0.002 | 0.881 ± 0.010       | 0.026 ± 0.001 | 0.054 ± 0.010         | 0.865 ± 0.003  | 0.453 ± 0.015         | 0.675 ± 0.020      |
| SCP-stage            | 0.903 ± 0.009 | 0.890 ± 0.019       | 0.087 ± 0.007 | 0.231 ± 0.023         | 0.745 ± 0.033  | 0.546 ± 0.033         | 0.682 ± 0.030      |
| SCP                  | 0.903 ± 0.009 | 0.868 ± 0.021       | 0.086 ± 0.007 | 0.231 ± 0.023         | 0.746 ± 0.034  | 0.546 ± 0.034         | 0.682 ± 0.025      |
| Mondrian-usage       | 0.898 ± 0.004 | 0.884 ± 0.013       | 0.086 ± 0.004 | 0.244 ± 0.013         | 0.739 ± 0.023  | 0.498 ± 0.010         | 0.697 ± 0.034      |
| Naive+SCP            | 0.903 ± 0.008 | 0.890 ± 0.015       | 0.085 ± 0.004 | 0.237 ± 0.025         | 0.748 ± 0.021  | 0.778 ± 0.039         | 0.972 ± 0.040      |
| Raw-SCP              | 0.896 ± 0.012 | 0.858 ± 0.024       | 0.122 ± 0.010 | 0.224 ± 0.021         | 0.659 ± 0.041  | 0.744 ± 0.039         | 1.063 ± 0.051      |
| HSC -stage           | 0.904 ± 0.000 | 0.860 ± 0.020       | 0.027 ± 0.001 | 0.064 ± 0.007         | 0.860 ± 0.003  | 0.430 ± 0.020         | 0.657 ± 0.028      |
| HSC -kNN             | 0.917 ± 0.001 | 0.910 ± 0.013       | 0.032 ± 0.001 | 0.029 ± 0.007         | 0.871 ± 0.001  | 0.466 ± 0.017         | 0.659 ± 0.027      |
| HSC -shrink          | 0.863 ± 0.007 | 0.833 ± 0.015       | 0.079 ± 0.005 | 0.363 ± 0.023         | 0.722 ± 0.013  | 0.395 ± 0.017         | 0.683 ± 0.036      |
| HSC-CQR -stage       | 0.895 ± 0.001 | 0.875 ± 0.010       | 0.019 ± 0.002 | 0.032 ± 0.016         | 0.862 ± 0.004  | 0.396 ± 0.024         | 0.559 ± 0.020      |
| HSC-CQR -kNN         | 0.898 ± 0.002 | 0.884 ± 0.015       | 0.018 ± 0.003 | 0.024 ± 0.019         | 0.868 ± 0.005  | 0.402 ± 0.023         | 0.559 ± 0.021      |
| HSC-CQR -shrink      | 0.891 ± 0.001 | 0.869 ± 0.012       | 0.035 ± 0.001 | 0.188 ± 0.023         | 0.833 ± 0.004  | 0.392 ± 0.024         | 0.561 ± 0.021      |
| HSC-CQR fixed-κ      | 0.897 ± 0.001 | 0.882 ± 0.012       | 0.015 ± 0.001 | 0.007 ± 0.003         | 0.873 ± 0.002  | 0.406 ± 0.023         | 0.560 ± 0.020      |


**Table S14. Robustness conditions on BDG2, all strategies (mean over 3 seeds).**

| perturb         | method               |   mean_cov |   macd |   under_rate |   under_wk1 |   rel_IS |   rel_width |   underprot |   cost20 |
|:----------------|:---------------------|-----------:|-------:|-------------:|------------:|---------:|------------:|------------:|---------:|
| calpool10       | ACI                  |      0.919 |  0.037 |        0.026 |       0.27  |    0.643 |       0.455 |       0.027 |    1.558 |
| calpool10       | ACI-CQR              |      0.898 |  0.017 |        0.02  |       0.205 |    0.549 |       0.394 |       0.037 |    1.443 |
| calpool10       | ACI-CQR (cov)        |      0.899 |  0.015 |        0.007 |       0.201 |    0.553 |       0.396 |       0.035 |    1.443 |
| calpool10       | CQR                  |      0.898 |  0.037 |        0.145 |       0.204 |    0.55  |       0.391 |       0.071 |    1.424 |
| calpool10       | GHCP-CQR             |      0.922 |  0.04  |        0.066 |       0.125 |    0.553 |       0.425 |       0.048 |    1.426 |
| calpool10       | HSC                  |      0.908 |  0.029 |        0.055 |       0.205 |    0.65  |       0.436 |       0.026 |    1.476 |
| calpool10       | HSC-CQR              |      0.898 |  0.016 |        0.02  |       0.186 |    0.549 |       0.392 |       0.033 |    1.42  |
| calpool10       | HSC-CQR recency      |      0.897 |  0.012 |        0.002 |       0.18  |    0.551 |       0.4   |       0.025 |    1.428 |
| calpool10       | HSC-CQR simple       |      0.898 |  0.018 |        0.031 |       0.212 |    0.546 |       0.39  |       0.038 |    1.419 |
| calpool10       | HSC-CQR simple (cov) |      0.896 |  0.016 |        0.019 |       0.189 |    0.55  |       0.396 |       0.031 |    1.421 |
| calpool10       | HSC-SSC-CQR          |      0.899 |  0.016 |        0.009 |       0.148 |    0.556 |       0.402 |       0.019 |    2.003 |
| calpool10       | MLP-QR               |      0.882 |  0.038 |        0.219 |       0.226 |    0.557 |       0.382 |       0.116 |    1.426 |
| calpool10       | QR-LGBM              |      0.867 |  0.044 |        0.344 |       0.328 |    0.555 |       0.363 |       0.134 |    1.425 |
| calpool10       | QShrink-CQR          |      0.901 |  0.018 |        0.016 |       0.182 |    0.547 |       0.395 |       0.034 |    1.419 |
| calpool10       | QShrink-CQR (cov)    |      0.897 |  0.016 |        0.02  |       0.193 |    0.55  |       0.398 |       0.025 |    1.423 |
| calpool10       | SCP-stage            |      0.89  |  0.091 |        0.275 |       0.286 |    0.663 |       0.503 |       0.19  |    1.568 |
| calpool10       | SSC-CQR              |      0.941 |  0.043 |        0.003 |       0.075 |    0.603 |       0.501 |       0.008 |    1.446 |
| calpool10       | Self-CP              |      0.906 |  0.025 |        0.045 |       0.191 |    0.661 |       0.448 |       0.019 |    1.492 |
| calpool10       | Self-CQR             |      0.89  |  0.021 |        0.061 |       0.348 |    0.557 |       0.398 |       0.029 |    1.437 |
| calpool10       | TQA-B-CQR            |      0.896 |  0.037 |        0.158 |       0.221 |    0.55  |       0.387 |       0.071 |    1.424 |
| calpool25       | ACI                  |      0.92  |  0.042 |        0.073 |       0.226 |    0.643 |       0.467 |       0.029 |    1.512 |
| calpool25       | ACI-CQR              |      0.897 |  0.02  |        0.035 |       0.233 |    0.548 |       0.39  |       0.045 |    1.427 |
| calpool25       | ACI-CQR (cov)        |      0.897 |  0.017 |        0.024 |       0.232 |    0.55  |       0.393 |       0.043 |    1.435 |
| calpool25       | CQR                  |      0.895 |  0.037 |        0.161 |       0.238 |    0.551 |       0.387 |       0.072 |    1.424 |
| calpool25       | GHCP-CQR             |      0.905 |  0.037 |        0.122 |       0.193 |    0.548 |       0.397 |       0.059 |    1.424 |
| calpool25       | HSC                  |      0.906 |  0.03  |        0.067 |       0.262 |    0.641 |       0.426 |       0.03  |    1.479 |
| calpool25       | HSC-CQR              |      0.893 |  0.017 |        0.027 |       0.246 |    0.55  |       0.386 |       0.04  |    1.42  |
| calpool25       | HSC-CQR recency      |      0.896 |  0.011 |        0.002 |       0.173 |    0.55  |       0.398 |       0.021 |    1.426 |
| calpool25       | HSC-CQR simple       |      0.897 |  0.018 |        0.03  |       0.221 |    0.547 |       0.39  |       0.041 |    1.42  |
| calpool25       | HSC-CQR simple (cov) |      0.896 |  0.015 |        0.016 |       0.183 |    0.549 |       0.394 |       0.032 |    1.42  |
| calpool25       | HSC-SSC-CQR          |      0.899 |  0.015 |        0.009 |       0.159 |    0.551 |       0.395 |       0.021 |    1.805 |
| calpool25       | MLP-QR               |      0.882 |  0.038 |        0.219 |       0.226 |    0.557 |       0.382 |       0.116 |    1.426 |
| calpool25       | QR-LGBM              |      0.867 |  0.044 |        0.344 |       0.328 |    0.555 |       0.363 |       0.134 |    1.425 |
| calpool25       | QShrink-CQR          |      0.9   |  0.021 |        0.03  |       0.222 |    0.548 |       0.392 |       0.037 |    1.419 |
| calpool25       | QShrink-CQR (cov)    |      0.897 |  0.015 |        0.012 |       0.19  |    0.551 |       0.395 |       0.023 |    1.425 |
| calpool25       | SCP-stage            |      0.898 |  0.089 |        0.253 |       0.243 |    0.664 |       0.523 |       0.174 |    1.568 |
| calpool25       | SSC-CQR              |      0.913 |  0.03  |        0.041 |       0.18  |    0.553 |       0.417 |       0.037 |    1.421 |
| calpool25       | Self-CP              |      0.906 |  0.025 |        0.044 |       0.188 |    0.662 |       0.449 |       0.019 |    1.492 |
| calpool25       | Self-CQR             |      0.889 |  0.021 |        0.063 |       0.368 |    0.556 |       0.397 |       0.029 |    1.437 |
| calpool25       | TQA-B-CQR            |      0.896 |  0.037 |        0.157 |       0.234 |    0.551 |       0.387 |       0.075 |    1.424 |
| calpool50       | ACI                  |      0.923 |  0.051 |        0.102 |       0.222 |    0.645 |       0.485 |       0.055 |    1.534 |
| calpool50       | ACI-CQR              |      0.897 |  0.02  |        0.037 |       0.213 |    0.547 |       0.389 |       0.046 |    1.432 |
| calpool50       | ACI-CQR (cov)        |      0.897 |  0.02  |        0.037 |       0.213 |    0.547 |       0.389 |       0.046 |    1.432 |
| calpool50       | CQR                  |      0.896 |  0.037 |        0.158 |       0.22  |    0.55  |       0.387 |       0.074 |    1.424 |
| calpool50       | GHCP-CQR             |      0.9   |  0.037 |        0.141 |       0.212 |    0.548 |       0.391 |       0.065 |    1.423 |
| calpool50       | HSC                  |      0.907 |  0.027 |        0.044 |       0.233 |    0.649 |       0.428 |       0.026 |    1.473 |
| calpool50       | HSC-CQR              |      0.894 |  0.017 |        0.032 |       0.244 |    0.548 |       0.386 |       0.04  |    1.419 |
| calpool50       | HSC-CQR recency      |      0.896 |  0.011 |        0.002 |       0.172 |    0.549 |       0.398 |       0.021 |    1.426 |
| calpool50       | HSC-CQR simple       |      0.896 |  0.018 |        0.03  |       0.22  |    0.546 |       0.391 |       0.044 |    1.419 |
| calpool50       | HSC-CQR simple (cov) |      0.895 |  0.015 |        0.014 |       0.185 |    0.549 |       0.394 |       0.03  |    1.419 |
| calpool50       | HSC-SSC-CQR          |      0.899 |  0.015 |        0.008 |       0.158 |    0.552 |       0.397 |       0.02  |    1.521 |
| calpool50       | MLP-QR               |      0.882 |  0.038 |        0.219 |       0.226 |    0.557 |       0.382 |       0.116 |    1.426 |
| calpool50       | QR-LGBM              |      0.867 |  0.044 |        0.344 |       0.328 |    0.555 |       0.363 |       0.134 |    1.425 |
| calpool50       | QShrink-CQR          |      0.9   |  0.021 |        0.029 |       0.205 |    0.546 |       0.392 |       0.04  |    1.418 |
| calpool50       | QShrink-CQR (cov)    |      0.897 |  0.015 |        0.012 |       0.174 |    0.549 |       0.396 |       0.024 |    1.425 |
| calpool50       | SCP-stage            |      0.904 |  0.087 |        0.237 |       0.228 |    0.671 |       0.542 |       0.159 |    1.567 |
| calpool50       | SSC-CQR              |      0.905 |  0.03  |        0.076 |       0.198 |    0.552 |       0.4   |       0.052 |    1.421 |
| calpool50       | Self-CP              |      0.907 |  0.025 |        0.044 |       0.178 |    0.662 |       0.449 |       0.019 |    1.492 |
| calpool50       | Self-CQR             |      0.889 |  0.021 |        0.063 |       0.363 |    0.558 |       0.396 |       0.029 |    1.437 |
| calpool50       | TQA-B-CQR            |      0.898 |  0.037 |        0.146 |       0.21  |    0.55  |       0.387 |       0.067 |    1.423 |
| missing20       | ACI                  |      0.915 |  0.052 |        0.165 |       0.24  |    0.689 |       0.498 |       0.072 |    1.551 |
| missing20       | ACI-CQR              |      0.898 |  0.026 |        0.083 |       0.249 |    0.582 |       0.43  |       0.043 |    1.451 |
| missing20       | ACI-CQR (cov)        |      0.899 |  0.024 |        0.066 |       0.248 |    0.582 |       0.43  |       0.038 |    1.45  |
| missing20       | CQR                  |      0.899 |  0.038 |        0.15  |       0.255 |    0.587 |       0.428 |       0.068 |    1.451 |
| missing20       | GHCP-CQR             |      0.902 |  0.038 |        0.137 |       0.254 |    0.587 |       0.431 |       0.065 |    1.451 |
| missing20       | HSC                  |      0.905 |  0.028 |        0.062 |       0.249 |    0.693 |       0.459 |       0.031 |    1.49  |
| missing20       | HSC-CQR              |      0.895 |  0.019 |        0.041 |       0.28  |    0.582 |       0.423 |       0.037 |    1.447 |
| missing20       | HSC-CQR recency      |      0.898 |  0.012 |        0.003 |       0.2   |    0.585 |       0.435 |       0.024 |    1.452 |
| missing20       | HSC-CQR simple       |      0.898 |  0.019 |        0.036 |       0.246 |    0.583 |       0.43  |       0.033 |    1.447 |
| missing20       | HSC-CQR simple (cov) |      0.897 |  0.015 |        0.014 |       0.206 |    0.586 |       0.431 |       0.027 |    1.447 |
| missing20       | HSC-SSC-CQR          |      0.9   |  0.015 |        0.01  |       0.175 |    0.587 |       0.434 |       0.022 |    1.485 |
| missing20       | MLP-QR               |      0.884 |  0.038 |        0.213 |       0.252 |    0.618 |       0.428 |       0.112 |    1.477 |
| missing20       | QR-LGBM              |      0.873 |  0.042 |        0.294 |       0.351 |    0.587 |       0.405 |       0.104 |    1.452 |
| missing20       | QShrink-CQR          |      0.902 |  0.023 |        0.042 |       0.239 |    0.582 |       0.43  |       0.034 |    1.446 |
| missing20       | QShrink-CQR (cov)    |      0.898 |  0.015 |        0.011 |       0.189 |    0.588 |       0.434 |       0.024 |    1.452 |
| missing20       | SCP-stage            |      0.889 |  0.09  |        0.279 |       0.251 |    0.696 |       0.528 |       0.172 |    1.584 |
| missing20       | SSC-CQR              |      0.907 |  0.032 |        0.077 |       0.228 |    0.586 |       0.44  |       0.047 |    1.448 |
| missing20       | Self-CP              |      0.915 |  0.027 |        0.03  |       0.103 |    0.73  |       0.514 |       0.014 |    1.52  |
| missing20       | Self-CQR             |      0.889 |  0.022 |        0.072 |       0.387 |    0.595 |       0.438 |       0.025 |    1.466 |
| missing20       | TQA-B-CQR            |      0.899 |  0.037 |        0.145 |       0.258 |    0.584 |       0.426 |       0.059 |    1.449 |
| missing40       | ACI                  |      0.907 |  0.057 |        0.218 |       0.242 |    0.727 |       0.518 |       0.087 |    1.57  |
| missing40       | ACI-CQR              |      0.901 |  0.031 |        0.098 |       0.271 |    0.622 |       0.468 |       0.054 |    1.481 |
| missing40       | ACI-CQR (cov)        |      0.901 |  0.029 |        0.088 |       0.271 |    0.621 |       0.468 |       0.049 |    1.48  |
| missing40       | CQR                  |      0.901 |  0.041 |        0.153 |       0.274 |    0.621 |       0.466 |       0.063 |    1.48  |
| missing40       | GHCP-CQR             |      0.904 |  0.041 |        0.139 |       0.272 |    0.622 |       0.469 |       0.059 |    1.48  |
| missing40       | HSC                  |      0.906 |  0.032 |        0.085 |       0.265 |    0.735 |       0.493 |       0.029 |    1.512 |
| missing40       | HSC-CQR              |      0.897 |  0.023 |        0.056 |       0.297 |    0.621 |       0.459 |       0.044 |    1.475 |
| missing40       | HSC-CQR recency      |      0.9   |  0.015 |        0.008 |       0.215 |    0.625 |       0.476 |       0.02  |    1.479 |
| missing40       | HSC-CQR simple       |      0.9   |  0.023 |        0.049 |       0.272 |    0.621 |       0.466 |       0.035 |    1.475 |
| missing40       | HSC-CQR simple (cov) |      0.899 |  0.018 |        0.025 |       0.251 |    0.623 |       0.472 |       0.025 |    1.474 |
| missing40       | HSC-SSC-CQR          |      0.903 |  0.018 |        0.013 |       0.2   |    0.623 |       0.476 |       0.023 |    1.48  |
| missing40       | MLP-QR               |      0.882 |  0.043 |        0.248 |       0.269 |    0.68  |       0.465 |       0.161 |    1.524 |
| missing40       | QR-LGBM              |      0.878 |  0.043 |        0.279 |       0.379 |    0.627 |       0.443 |       0.094 |    1.481 |
| missing40       | QShrink-CQR          |      0.904 |  0.027 |        0.055 |       0.258 |    0.621 |       0.466 |       0.041 |    1.474 |
| missing40       | QShrink-CQR (cov)    |      0.9   |  0.018 |        0.016 |       0.224 |    0.623 |       0.469 |       0.023 |    1.48  |
| missing40       | SCP-stage            |      0.877 |  0.094 |        0.321 |       0.247 |    0.729 |       0.528 |       0.179 |    1.605 |
| missing40       | SSC-CQR              |      0.913 |  0.036 |        0.082 |       0.226 |    0.625 |       0.481 |       0.049 |    1.478 |
| missing40       | Self-CP              |      0.923 |  0.034 |        0.022 |       0.075 |    0.801 |       0.593 |       0.009 |    1.559 |
| missing40       | Self-CQR             |      0.889 |  0.023 |        0.083 |       0.418 |    0.633 |       0.469 |       0.027 |    1.498 |
| missing40       | TQA-B-CQR            |      0.901 |  0.038 |        0.15  |       0.284 |    0.622 |       0.46  |       0.058 |    1.476 |
| noise15         | ACI                  |      0.862 |  0.038 |        0.266 |       0.548 |    0.931 |       0.637 |       0.094 |    1.68  |
| noise15         | ACI-CQR              |      0.872 |  0.028 |        0.099 |       0.372 |    0.922 |       0.672 |       0.049 |    1.608 |
| noise15         | ACI-CQR (cov)        |      0.875 |  0.025 |        0.057 |       0.37  |    0.92  |       0.676 |       0.044 |    1.608 |
| noise15         | CQR                  |      0.857 |  0.043 |        0.295 |       0.387 |    0.927 |       0.655 |       0.114 |    1.607 |
| noise15         | GHCP-CQR             |      0.859 |  0.041 |        0.279 |       0.393 |    0.927 |       0.657 |       0.108 |    1.606 |
| noise15         | HSC                  |      0.883 |  0.023 |        0.087 |       0.713 |    0.94  |       0.674 |       0.019 |    1.616 |
| noise15         | HSC-CQR              |      0.881 |  0.019 |        0.019 |       0.417 |    0.921 |       0.689 |       0.025 |    1.597 |
| noise15         | HSC-CQR recency      |      0.896 |  0.007 |        0     |       0.115 |    0.919 |       0.718 |       0.007 |    1.6   |
| noise15         | HSC-CQR simple       |      0.884 |  0.017 |        0.021 |       0.345 |    0.919 |       0.694 |       0.024 |    1.596 |
| noise15         | HSC-CQR simple (cov) |      0.893 |  0.01  |        0.004 |       0.227 |    0.919 |       0.712 |       0.009 |    1.596 |
| noise15         | HSC-SSC-CQR          |      0.898 |  0.008 |        0.001 |       0.123 |    0.918 |       0.719 |       0.003 |    1.658 |
| noise15         | MLP-QR               |      0.855 |  0.046 |        0.391 |       0.367 |    0.949 |       0.671 |       0.138 |    1.626 |
| noise15         | QR-LGBM              |      0.842 |  0.058 |        0.54  |       0.559 |    0.936 |       0.632 |       0.189 |    1.613 |
| noise15         | QShrink-CQR          |      0.881 |  0.019 |        0.035 |       0.33  |    0.919 |       0.686 |       0.035 |    1.596 |
| noise15         | QShrink-CQR (cov)    |      0.896 |  0.009 |        0.001 |       0.171 |    0.918 |       0.716 |       0.005 |    1.598 |
| noise15         | SCP-stage            |      0.765 |  0.135 |        0.801 |       0.581 |    0.994 |       0.528 |       0.579 |    1.739 |
| noise15         | SSC-CQR              |      0.876 |  0.025 |        0.104 |       0.305 |    0.919 |       0.681 |       0.049 |    1.598 |
| noise15         | Self-CP              |      0.906 |  0.02  |        0.023 |       0.107 |    0.941 |       0.733 |       0.005 |    1.627 |
| noise15         | Self-CQR             |      0.903 |  0.011 |        0.001 |       0.107 |    0.924 |       0.734 |       0.003 |    1.608 |
| noise15         | TQA-B-CQR            |      0.853 |  0.047 |        0.37  |       0.429 |    0.93  |       0.647 |       0.127 |    1.608 |
| noise5          | ACI                  |      0.914 |  0.046 |        0.132 |       0.243 |    0.666 |       0.49  |       0.061 |    1.548 |
| noise5          | ACI-CQR              |      0.889 |  0.018 |        0.055 |       0.217 |    0.605 |       0.44  |       0.05  |    1.458 |
| noise5          | ACI-CQR (cov)        |      0.89  |  0.016 |        0.041 |       0.213 |    0.606 |       0.442 |       0.044 |    1.458 |
| noise5          | CQR                  |      0.882 |  0.028 |        0.168 |       0.225 |    0.609 |       0.434 |       0.079 |    1.451 |
| noise5          | GHCP-CQR             |      0.884 |  0.028 |        0.156 |       0.225 |    0.608 |       0.436 |       0.076 |    1.451 |
| noise5          | HSC                  |      0.898 |  0.023 |        0.06  |       0.279 |    0.675 |       0.452 |       0.032 |    1.491 |
| noise5          | HSC-CQR              |      0.889 |  0.015 |        0.023 |       0.234 |    0.606 |       0.44  |       0.038 |    1.447 |
| noise5          | HSC-CQR recency      |      0.897 |  0.009 |        0     |       0.123 |    0.609 |       0.456 |       0.014 |    1.454 |
| noise5          | HSC-CQR simple       |      0.892 |  0.013 |        0.018 |       0.205 |    0.606 |       0.443 |       0.032 |    1.446 |
| noise5          | HSC-CQR simple (cov) |      0.895 |  0.012 |        0.005 |       0.161 |    0.608 |       0.45  |       0.022 |    1.447 |
| noise5          | HSC-SSC-CQR          |      0.897 |  0.011 |        0.002 |       0.119 |    0.609 |       0.451 |       0.014 |    1.584 |
| noise5          | MLP-QR               |      0.87  |  0.037 |        0.27  |       0.23  |    0.615 |       0.434 |       0.149 |    1.456 |
| noise5          | QR-LGBM              |      0.859 |  0.043 |        0.338 |       0.324 |    0.615 |       0.411 |       0.135 |    1.454 |
| noise5          | QShrink-CQR          |      0.892 |  0.015 |        0.026 |       0.198 |    0.605 |       0.442 |       0.041 |    1.446 |
| noise5          | QShrink-CQR (cov)    |      0.896 |  0.012 |        0.005 |       0.144 |    0.608 |       0.451 |       0.015 |    1.452 |
| noise5          | SCP-stage            |      0.891 |  0.088 |        0.271 |       0.249 |    0.687 |       0.528 |       0.186 |    1.577 |
| noise5          | SSC-CQR              |      0.892 |  0.022 |        0.08  |       0.194 |    0.607 |       0.443 |       0.051 |    1.447 |
| noise5          | Self-CP              |      0.907 |  0.024 |        0.034 |       0.134 |    0.694 |       0.482 |       0.015 |    1.513 |
| noise5          | Self-CQR             |      0.894 |  0.015 |        0.016 |       0.234 |    0.616 |       0.454 |       0.011 |    1.465 |
| noise5          | TQA-B-CQR            |      0.88  |  0.028 |        0.175 |       0.227 |    0.608 |       0.432 |       0.082 |    1.45  |
| outage1-3d      | ACI                  |      0.919 |  0.051 |        0.135 |       0.235 |    0.666 |       0.489 |       0.067 |    1.547 |
| outage1-3d      | ACI-CQR              |      0.895 |  0.024 |        0.08  |       0.226 |    0.562 |       0.4   |       0.053 |    1.436 |
| outage1-3d      | ACI-CQR (cov)        |      0.895 |  0.022 |        0.065 |       0.224 |    0.562 |       0.4   |       0.048 |    1.435 |
| outage1-3d      | CQR                  |      0.894 |  0.038 |        0.184 |       0.23  |    0.564 |       0.395 |       0.082 |    1.434 |
| outage1-3d      | GHCP-CQR             |      0.896 |  0.038 |        0.166 |       0.232 |    0.563 |       0.397 |       0.08  |    1.434 |
| outage1-3d      | HSC                  |      0.903 |  0.028 |        0.072 |       0.286 |    0.664 |       0.439 |       0.034 |    1.486 |
| outage1-3d      | HSC-CQR              |      0.892 |  0.019 |        0.045 |       0.257 |    0.563 |       0.397 |       0.043 |    1.43  |
| outage1-3d      | HSC-CQR recency      |      0.896 |  0.013 |        0.005 |       0.187 |    0.567 |       0.414 |       0.022 |    1.437 |
| outage1-3d      | HSC-CQR simple       |      0.895 |  0.018 |        0.038 |       0.226 |    0.563 |       0.401 |       0.04  |    1.43  |
| outage1-3d      | HSC-CQR simple (cov) |      0.895 |  0.017 |        0.026 |       0.199 |    0.569 |       0.407 |       0.026 |    1.431 |
| outage1-3d      | HSC-SSC-CQR          |      0.898 |  0.016 |        0.014 |       0.179 |    0.571 |       0.409 |       0.024 |    1.537 |
| outage1-3d      | MLP-QR               |      0.877 |  0.041 |        0.259 |       0.246 |    0.607 |       0.404 |       0.125 |    1.452 |
| outage1-3d      | QR-LGBM              |      0.865 |  0.046 |        0.365 |       0.337 |    0.568 |       0.373 |       0.14  |    1.436 |
| outage1-3d      | QShrink-CQR          |      0.899 |  0.022 |        0.052 |       0.217 |    0.561 |       0.399 |       0.038 |    1.429 |
| outage1-3d      | QShrink-CQR (cov)    |      0.897 |  0.017 |        0.022 |       0.191 |    0.569 |       0.407 |       0.025 |    1.435 |
| outage1-3d      | SCP-stage            |      0.896 |  0.088 |        0.263 |       0.242 |    0.678 |       0.529 |       0.177 |    1.577 |
| outage1-3d      | SSC-CQR              |      0.899 |  0.032 |        0.113 |       0.223 |    0.565 |       0.403 |       0.063 |    1.43  |
| outage1-3d      | Self-CP              |      0.907 |  0.026 |        0.043 |       0.211 |    0.686 |       0.465 |       0.025 |    1.507 |
| outage1-3d      | Self-CQR             |      0.889 |  0.023 |        0.075 |       0.386 |    0.58  |       0.411 |       0.029 |    1.449 |
| outage1-3d      | TQA-B-CQR            |      0.896 |  0.038 |        0.166 |       0.222 |    0.561 |       0.393 |       0.078 |    1.433 |
| ramp+40         | ACI                  |      0.916 |  0.048 |        0.129 |       0.234 |    0.653 |       0.474 |       0.114 |    1.539 |
| ramp+40         | ACI-CQR              |      0.883 |  0.022 |        0.085 |       0.233 |    0.562 |       0.384 |       0.301 |    1.448 |
| ramp+40         | ACI-CQR (cov)        |      0.885 |  0.02  |        0.056 |       0.228 |    0.561 |       0.386 |       0.28  |    1.448 |
| ramp+40         | CQR                  |      0.872 |  0.036 |        0.268 |       0.235 |    0.564 |       0.371 |       0.383 |    1.442 |
| ramp+40         | GHCP-CQR             |      0.875 |  0.035 |        0.236 |       0.233 |    0.564 |       0.373 |       0.358 |    1.441 |
| ramp+40         | HSC                  |      0.896 |  0.023 |        0.065 |       0.263 |    0.657 |       0.428 |       0.091 |    1.485 |
| ramp+40         | HSC-CQR              |      0.881 |  0.022 |        0.06  |       0.261 |    0.563 |       0.38  |       0.316 |    1.433 |
| ramp+40         | HSC-CQR recency      |      0.89  |  0.014 |        0.008 |       0.184 |    0.564 |       0.396 |       0.224 |    1.436 |
| ramp+40         | HSC-CQR simple       |      0.885 |  0.019 |        0.036 |       0.226 |    0.562 |       0.385 |       0.284 |    1.432 |
| ramp+40         | HSC-CQR simple (cov) |      0.887 |  0.018 |        0.033 |       0.201 |    0.564 |       0.389 |       0.275 |    1.432 |
| ramp+40         | HSC-SSC-CQR          |      0.888 |  0.018 |        0.031 |       0.166 |    0.565 |       0.392 |       0.271 |    1.525 |
| ramp+40         | MLP-QR               |      0.858 |  0.049 |        0.41  |       0.243 |    0.581 |       0.366 |       0.48  |    1.449 |
| ramp+40         | QR-LGBM              |      0.841 |  0.061 |        0.538 |       0.341 |    0.571 |       0.35  |       0.622 |    1.454 |
| ramp+40         | QShrink-CQR          |      0.885 |  0.02  |        0.06  |       0.214 |    0.562 |       0.382 |       0.281 |    1.431 |
| ramp+40         | QShrink-CQR (cov)    |      0.888 |  0.018 |        0.021 |       0.194 |    0.563 |       0.392 |       0.262 |    1.435 |
| ramp+40         | SCP-stage            |      0.894 |  0.087 |        0.263 |       0.243 |    0.667 |       0.514 |       0.226 |    1.579 |
| ramp+40         | SSC-CQR              |      0.877 |  0.033 |        0.223 |       0.229 |    0.564 |       0.381 |       0.361 |    1.437 |
| ramp+40         | Self-CP              |      0.9   |  0.023 |        0.054 |       0.205 |    0.666 |       0.45  |       0.12  |    1.502 |
| ramp+40         | Self-CQR             |      0.883 |  0.024 |        0.109 |       0.38  |    0.568 |       0.396 |       0.306 |    1.447 |
| ramp+40         | TQA-B-CQR            |      0.88  |  0.036 |        0.234 |       0.222 |    0.566 |       0.373 |       0.311 |    1.44  |
| shift+40        | ACI                  |      0.905 |  0.04  |        0.14  |       0.224 |    0.737 |       0.496 |       0.137 |    1.609 |
| shift+40        | ACI-CQR              |      0.885 |  0.023 |        0.096 |       0.217 |    0.658 |       0.416 |       0.193 |    1.521 |
| shift+40        | ACI-CQR (cov)        |      0.887 |  0.021 |        0.065 |       0.214 |    0.658 |       0.42  |       0.171 |    1.521 |
| shift+40        | CQR                  |      0.876 |  0.038 |        0.258 |       0.221 |    0.656 |       0.395 |       0.306 |    1.516 |
| shift+40        | GHCP-CQR             |      0.878 |  0.037 |        0.248 |       0.224 |    0.655 |       0.398 |       0.297 |    1.515 |
| shift+40        | HSC                  |      0.887 |  0.023 |        0.084 |       0.254 |    0.743 |       0.457 |       0.143 |    1.559 |
| shift+40        | HSC-CQR              |      0.883 |  0.02  |        0.059 |       0.25  |    0.659 |       0.417 |       0.181 |    1.504 |
| shift+40        | HSC-CQR recency      |      0.892 |  0.012 |        0.004 |       0.173 |    0.664 |       0.442 |       0.081 |    1.505 |
| shift+40        | HSC-CQR simple       |      0.887 |  0.018 |        0.046 |       0.215 |    0.659 |       0.421 |       0.164 |    1.504 |
| shift+40        | HSC-CQR simple (cov) |      0.888 |  0.017 |        0.023 |       0.188 |    0.661 |       0.427 |       0.144 |    1.502 |
| shift+40        | HSC-SSC-CQR          |      0.892 |  0.014 |        0.01  |       0.16  |    0.662 |       0.431 |       0.121 |    1.599 |
| shift+40        | MLP-QR               |      0.862 |  0.044 |        0.361 |       0.226 |    0.669 |       0.383 |       0.437 |    1.523 |
| shift+40        | QR-LGBM              |      0.851 |  0.053 |        0.45  |       0.328 |    0.664 |       0.374 |       0.487 |    1.525 |
| shift+40        | QShrink-CQR          |      0.888 |  0.021 |        0.06  |       0.206 |    0.658 |       0.419 |       0.17  |    1.503 |
| shift+40        | QShrink-CQR (cov)    |      0.89  |  0.016 |        0.018 |       0.176 |    0.661 |       0.426 |       0.123 |    1.506 |
| shift+40        | SCP-stage            |      0.877 |  0.08  |        0.296 |       0.231 |    0.734 |       0.513 |       0.276 |    1.644 |
| shift+40        | SSC-CQR              |      0.883 |  0.03  |        0.175 |       0.214 |    0.656 |       0.405 |       0.243 |    1.508 |
| shift+40        | Self-CP              |      0.892 |  0.023 |        0.068 |       0.187 |    0.76  |       0.48  |       0.126 |    1.575 |
| shift+40        | Self-CQR             |      0.884 |  0.022 |        0.084 |       0.363 |    0.667 |       0.436 |       0.174 |    1.516 |
| shift+40        | TQA-B-CQR            |      0.878 |  0.037 |        0.251 |       0.213 |    0.66  |       0.405 |       0.298 |    1.514 |
| shift+40@d3-14  | ACI                  |      0.911 |  0.043 |        0.132 |       0.369 |    0.716 |       0.504 |       0.113 |    1.587 |
| shift+40@d3-14  | ACI-CQR              |      0.889 |  0.022 |        0.076 |       0.458 |    0.636 |       0.416 |       0.141 |    1.499 |
| shift+40@d3-14  | ACI-CQR (cov)        |      0.891 |  0.019 |        0.049 |       0.454 |    0.637 |       0.419 |       0.114 |    1.498 |
| shift+40@d3-14  | CQR                  |      0.878 |  0.036 |        0.234 |       0.459 |    0.635 |       0.396 |       0.243 |    1.496 |
| shift+40@d3-14  | GHCP-CQR             |      0.88  |  0.036 |        0.228 |       0.459 |    0.634 |       0.398 |       0.236 |    1.495 |
| shift+40@d3-14  | HSC                  |      0.912 |  0.028 |        0.029 |       0.479 |    0.735 |       0.505 |       0.04  |    1.54  |
| shift+40@d3-14  | HSC-CQR              |      0.895 |  0.016 |        0.024 |       0.482 |    0.641 |       0.427 |       0.096 |    1.487 |
| shift+40@d3-14  | HSC-CQR recency      |      0.901 |  0.011 |        0.001 |       0.394 |    0.646 |       0.456 |       0.038 |    1.492 |
| shift+40@d3-14  | HSC-CQR simple       |      0.899 |  0.015 |        0.019 |       0.449 |    0.64  |       0.433 |       0.078 |    1.487 |
| shift+40@d3-14  | HSC-CQR simple (cov) |      0.905 |  0.015 |        0.005 |       0.421 |    0.646 |       0.453 |       0.047 |    1.487 |
| shift+40@d3-14  | HSC-SSC-CQR          |      0.907 |  0.015 |        0.001 |       0.385 |    0.652 |       0.462 |       0.035 |    1.569 |
| shift+40@d3-14  | MLP-QR               |      0.866 |  0.042 |        0.333 |       0.448 |    0.641 |       0.389 |       0.365 |    1.498 |
| shift+40@d3-14  | QR-LGBM              |      0.853 |  0.051 |        0.433 |       0.55  |    0.64  |       0.374 |       0.407 |    1.504 |
| shift+40@d3-14  | QShrink-CQR          |      0.899 |  0.018 |        0.023 |       0.434 |    0.638 |       0.429 |       0.088 |    1.485 |
| shift+40@d3-14  | QShrink-CQR (cov)    |      0.907 |  0.016 |        0.004 |       0.401 |    0.65  |       0.46  |       0.037 |    1.49  |
| shift+40@d3-14  | SCP-stage            |      0.881 |  0.08  |        0.284 |       0.37  |    0.72  |       0.514 |       0.251 |    1.621 |
| shift+40@d3-14  | SSC-CQR              |      0.888 |  0.029 |        0.143 |       0.446 |    0.637 |       0.41  |       0.179 |    1.489 |
| shift+40@d3-14  | Self-CP              |      0.922 |  0.031 |        0.012 |       0.364 |    0.754 |       0.547 |       0.021 |    1.555 |
| shift+40@d3-14  | Self-CQR             |      0.906 |  0.018 |        0.01  |       0.53  |    0.661 |       0.478 |       0.04  |    1.503 |
| shift+40@d3-14  | TQA-B-CQR            |      0.88  |  0.036 |        0.232 |       0.45  |    0.635 |       0.397 |       0.244 |    1.495 |
| shift-40        | ACI                  |      0.888 |  0.032 |        0.171 |       0.224 |    0.873 |       0.553 |       0.014 |    1.597 |
| shift-40        | ACI-CQR              |      0.889 |  0.019 |        0.058 |       0.217 |    0.753 |       0.501 |       0.013 |    1.525 |
| shift-40        | ACI-CQR (cov)        |      0.891 |  0.017 |        0.032 |       0.214 |    0.753 |       0.502 |       0.012 |    1.525 |
| shift-40        | CQR                  |      0.879 |  0.033 |        0.21  |       0.221 |    0.753 |       0.491 |       0.019 |    1.51  |
| shift-40        | GHCP-CQR             |      0.882 |  0.032 |        0.194 |       0.224 |    0.753 |       0.494 |       0.019 |    1.51  |
| shift-40        | HSC                  |      0.87  |  0.033 |        0.206 |       0.254 |    0.887 |       0.494 |       0.007 |    1.529 |
| shift-40        | HSC-CQR              |      0.887 |  0.017 |        0.035 |       0.25  |    0.753 |       0.497 |       0.01  |    1.512 |
| shift-40        | HSC-CQR recency      |      0.896 |  0.011 |        0.002 |       0.173 |    0.759 |       0.516 |       0.004 |    1.526 |
| shift-40        | HSC-CQR simple       |      0.89  |  0.016 |        0.027 |       0.215 |    0.753 |       0.502 |       0.011 |    1.512 |
| shift-40        | HSC-CQR simple (cov) |      0.892 |  0.015 |        0.025 |       0.188 |    0.755 |       0.509 |       0.005 |    1.516 |
| shift-40        | HSC-SSC-CQR          |      0.897 |  0.013 |        0.007 |       0.16  |    0.758 |       0.515 |       0.004 |    1.622 |
| shift-40        | MLP-QR               |      0.879 |  0.036 |        0.211 |       0.226 |    0.741 |       0.48  |       0.025 |    1.497 |
| shift-40        | QR-LGBM              |      0.851 |  0.051 |        0.449 |       0.328 |    0.761 |       0.468 |       0.024 |    1.508 |
| shift-40        | QShrink-CQR          |      0.892 |  0.017 |        0.033 |       0.206 |    0.753 |       0.499 |       0.011 |    1.511 |
| shift-40        | QShrink-CQR (cov)    |      0.893 |  0.015 |        0.021 |       0.176 |    0.756 |       0.509 |       0.004 |    1.521 |
| shift-40        | SCP-stage            |      0.848 |  0.081 |        0.389 |       0.231 |    0.869 |       0.55  |       0.115 |    1.597 |
| shift-40        | SSC-CQR              |      0.888 |  0.028 |        0.128 |       0.214 |    0.755 |       0.502 |       0.013 |    1.51  |
| shift-40        | Self-CP              |      0.878 |  0.031 |        0.189 |       0.187 |    0.892 |       0.526 |       0.001 |    1.555 |
| shift-40        | Self-CQR             |      0.887 |  0.022 |        0.094 |       0.363 |    0.761 |       0.516 |       0.003 |    1.536 |
| shift-40        | TQA-B-CQR            |      0.887 |  0.032 |        0.172 |       0.213 |    0.76  |       0.497 |       0.019 |    1.516 |
| spikes2         | ACI                  |      0.89  |  0.034 |        0.183 |       0.332 |    1.52  |       0.542 |       0.041 |    2.16  |
| spikes2         | ACI-CQR              |      0.918 |  0.03  |        0.029 |       0.145 |    1.336 |       0.61  |       0.025 |    2.126 |
| spikes2         | ACI-CQR (cov)        |      0.917 |  0.028 |        0.021 |       0.145 |    1.335 |       0.608 |       0.025 |    2.126 |
| spikes2         | CQR                  |      0.921 |  0.038 |        0.069 |       0.146 |    1.34  |       0.617 |       0.029 |    2.124 |
| spikes2         | GHCP-CQR             |      0.922 |  0.038 |        0.066 |       0.148 |    1.341 |       0.619 |       0.029 |    2.124 |
| spikes2         | HSC                  |      0.891 |  0.02  |        0.058 |       0.406 |    1.528 |       0.549 |       0.014 |    2.096 |
| spikes2         | HSC-CQR              |      0.913 |  0.022 |        0.012 |       0.166 |    1.333 |       0.598 |       0.019 |    2.119 |
| spikes2         | HSC-CQR recency      |      0.908 |  0.013 |        0.002 |       0.113 |    1.334 |       0.592 |       0.014 |    2.125 |
| spikes2         | HSC-CQR simple       |      0.914 |  0.023 |        0.011 |       0.145 |    1.334 |       0.598 |       0.019 |    2.12  |
| spikes2         | HSC-CQR simple (cov) |      0.91  |  0.017 |        0.004 |       0.127 |    1.334 |       0.591 |       0.016 |    2.12  |
| spikes2         | HSC-SSC-CQR          |      0.912 |  0.017 |        0.002 |       0.098 |    1.336 |       0.593 |       0.01  |    2.198 |
| spikes2         | MLP-QR               |      0.92  |  0.038 |        0.052 |       0.134 |    1.386 |       0.651 |       0.035 |    2.142 |
| spikes2         | QR-LGBM              |      0.907 |  0.035 |        0.101 |       0.194 |    1.335 |       0.595 |       0.041 |    2.123 |
| spikes2         | QShrink-CQR          |      0.917 |  0.025 |        0.009 |       0.137 |    1.334 |       0.6   |       0.018 |    2.118 |
| spikes2         | QShrink-CQR (cov)    |      0.907 |  0.015 |        0.005 |       0.117 |    1.334 |       0.588 |       0.013 |    2.123 |
| spikes2         | SCP-stage            |      0.851 |  0.079 |        0.353 |       0.344 |    1.53  |       0.528 |       0.176 |    2.168 |
| spikes2         | SSC-CQR              |      0.932 |  0.04  |        0.021 |       0.128 |    1.35  |       0.64  |       0.023 |    2.124 |
| spikes2         | Self-CP              |      0.903 |  0.02  |        0.031 |       0.222 |    1.553 |       0.629 |       0.002 |    2.122 |
| spikes2         | Self-CQR             |      0.896 |  0.016 |        0.016 |       0.281 |    1.339 |       0.587 |       0.01  |    2.134 |
| spikes2         | TQA-B-CQR            |      0.92  |  0.037 |        0.063 |       0.147 |    1.342 |       0.616 |       0.03  |    2.124 |
| weak-forecaster | ACI                  |      0.923 |  0.052 |        0.123 |       0.213 |    0.675 |       0.514 |       0.056 |    1.554 |
| weak-forecaster | ACI-CQR              |      0.903 |  0.03  |        0.072 |       0.215 |    0.585 |       0.436 |       0.078 |    1.464 |
| weak-forecaster | ACI-CQR (cov)        |      0.903 |  0.026 |        0.053 |       0.215 |    0.584 |       0.436 |       0.059 |    1.463 |
| weak-forecaster | CQR                  |      0.9   |  0.051 |        0.202 |       0.217 |    0.585 |       0.424 |       0.12  |    1.466 |
| weak-forecaster | GHCP-CQR             |      0.902 |  0.051 |        0.192 |       0.235 |    0.585 |       0.427 |       0.114 |    1.466 |
| weak-forecaster | HSC                  |      0.903 |  0.028 |        0.067 |       0.243 |    0.668 |       0.445 |       0.041 |    1.495 |
| weak-forecaster | HSC-CQR              |      0.896 |  0.02  |        0.043 |       0.278 |    0.586 |       0.425 |       0.056 |    1.452 |
| weak-forecaster | HSC-CQR recency      |      0.899 |  0.013 |        0.004 |       0.176 |    0.585 |       0.436 |       0.032 |    1.46  |
| weak-forecaster | HSC-CQR simple       |      0.901 |  0.02  |        0.024 |       0.211 |    0.584 |       0.43  |       0.05  |    1.453 |
| weak-forecaster | HSC-CQR simple (cov) |      0.899 |  0.017 |        0.022 |       0.187 |    0.585 |       0.435 |       0.046 |    1.454 |
| weak-forecaster | HSC-SSC-CQR          |      0.903 |  0.018 |        0.013 |       0.16  |    0.588 |       0.435 |       0.029 |    1.834 |
| weak-forecaster | QR-LGBM              |      0.861 |  0.06  |        0.405 |       0.357 |    0.589 |       0.385 |       0.217 |    1.469 |
| weak-forecaster | QShrink-CQR          |      0.905 |  0.025 |        0.029 |       0.2   |    0.586 |       0.432 |       0.052 |    1.456 |
| weak-forecaster | QShrink-CQR (cov)    |      0.899 |  0.017 |        0.022 |       0.176 |    0.587 |       0.435 |       0.038 |    1.462 |
| weak-forecaster | SCP-stage            |      0.904 |  0.088 |        0.233 |       0.223 |    0.704 |       0.574 |       0.16  |    1.591 |
| weak-forecaster | SSC-CQR              |      0.903 |  0.041 |        0.147 |       0.217 |    0.585 |       0.43  |       0.097 |    1.458 |
| weak-forecaster | Self-CP              |      0.904 |  0.026 |        0.061 |       0.179 |    0.684 |       0.476 |       0.022 |    1.518 |
| weak-forecaster | Self-CQR             |      0.891 |  0.022 |        0.071 |       0.396 |    0.591 |       0.432 |       0.045 |    1.472 |
| weak-forecaster | TQA-B-CQR            |      0.904 |  0.047 |        0.187 |       0.221 |    0.585 |       0.428 |       0.109 |    1.462 |


**Table S15. Parameters selected by leave-one-building-out on calibration buildings, per run.**

| Run | κ recency (cov) | κ simple (cov) | κ simple (IS) | λ QShrink (cov) | γ ACI-CQR | γ ACI-CQR (cov) |
|:--|--:|--:|--:|--:|--:|--:|
| lso_BDG2_f0 | 96.0 | 168.0 | 336.0 | 336.0 | 0.001 | 0.001 |
| lso_BDG2_f1 | 96.0 | 168.0 | 672.0 | 168.0 | 0.001 | 0.001 |
| lso_BDG2_f2 | 48.0 | 168.0 | 336.0 | 96.0 | 0.0005 | 0.001 |
| lso_BDG2_f3 | 96.0 | 168.0 | 672.0 | 336.0 | 0.001 | 0.001 |
| lso_BDG2_f4 | 48.0 | 168.0 | 336.0 | 96.0 | 0.001 | 0.001 |
| main_BDG2_s0_a0.1 | 48.0 | 96.0 | 336.0 | 96.0 | 0.001 | 0.001 |
| main_BDG2_s1_a0.1 | 48.0 | 96.0 | 336.0 | 96.0 | 0.0005 | 0.001 |
| main_BDG2_s2_a0.1 | 48.0 | 168.0 | 336.0 | 96.0 | 0.001 | 0.001 |
| main_BDG2_s3_a0.1 | 168.0 | 168.0 | 336.0 | 672.0 | 0.001 | 0.002 |
| main_BDG2_s4_a0.1 | 96.0 | 168.0 | 336.0 | 96.0 | 0.0005 | 0.001 |
| main_UCI_s0_a0.1 | 24.0 | 48.0 | 336.0 | 48.0 | 0.001 | 0.002 |
| main_UCI_s1_a0.1 | 24.0 | 96.0 | 168.0 | 96.0 | 0.0005 | 0.0005 |
| main_UCI_s2_a0.1 | 48.0 | 168.0 | 336.0 | 96.0 | 0.0005 | 0.002 |
| main_UCI_s3_a0.1 | 24.0 | 96.0 | 336.0 | 48.0 | 0.001 | 0.001 |
| main_UCI_s4_a0.1 | 48.0 | 168.0 | 672.0 | 168.0 | 0.001 | 0.005 |
| xds_BDG2toBDG2_s0 | 48.0 | 96.0 | 336.0 | 96.0 | 0.001 | 0.001 |
| xds_BDG2toBDG2_s1 | 48.0 | 168.0 | 336.0 | 96.0 | 0.0005 | 0.001 |
| xds_BDG2toBDG2_s2 | 48.0 | 168.0 | 336.0 | 168.0 | 0.001 | 0.001 |
| xds_BDG2toUCI_s0 | 48.0 | 96.0 | 336.0 | 96.0 | 0.001 | 0.001 |
| xds_BDG2toUCI_s1 | 48.0 | 168.0 | 336.0 | 96.0 | 0.0005 | 0.001 |
| xds_BDG2toUCI_s2 | 48.0 | 168.0 | 336.0 | 168.0 | 0.001 | 0.001 |
| xds_UCItoBDG2_s0 | 24.0 | 48.0 | 336.0 | 48.0 | 0.001 | 0.002 |
| xds_UCItoBDG2_s1 | 24.0 | 96.0 | 168.0 | 96.0 | 0.0005 | 0.0005 |
| xds_UCItoBDG2_s2 | 48.0 | 168.0 | 336.0 | 96.0 | 0.0005 | 0.002 |

**Table S16. Single-timescale analysis: confirmatory family of the recommended single-timescale configuration (HSC-CQR recency) versus pooled CQR, QShrink-CQR (cov), ACI-CQR (cov) and Self-CQR (paired share differences with 95 % site-cluster (BDG2) or building (UCI) bootstrap CI, McNemar tests, TOST equivalence of the interval score within 2 %; Holm over the family).**

| exp   | dataset   | protocol   | perturb   |   alpha | primary         | baseline          | metric     |   n_buildings |   share_primary |   share_baseline |    diff | ci95               |   discordant_better |   discordant_worse |      p |   mean_ratio |   tost_equiv_2pct |   p_holm | family       |
|:------|:----------|:-----------|:----------|--------:|:----------------|:------------------|:-----------|--------------:|----------------:|-----------------:|--------:|:-------------------|--------------------:|-------------------:|-------:|-------------:|------------------:|---------:|:-------------|
| main  | BDG2      |            | none      |     0.1 | HSC-CQR recency | CQR               | under      |           837 |          0.0018 |           0.1522 | -0.1504 | [-0.2146, -0.0903] |                 238 |                  1 | 0      |     nan      |               nan |   0      | confirmatory |
| main  | BDG2      |            | none      |     0.1 | HSC-CQR recency | CQR               | under_wk1  |           837 |          0.1659 |           0.2196 | -0.0536 | [-0.0805, -0.0247] |                 124 |                 37 | 0      |     nan      |               nan |   0      | confirmatory |
| main  | BDG2      |            | none      |     0.1 | HSC-CQR recency | CQR               | log_rel_IS |           837 |        nan      |         nan      |  0.0001 | [-0.0009, 0.0008]  |                 nan |                nan | 0.0012 |       1.0185 |                 1 |   0.0112 | confirmatory |
| main  | BDG2      |            | none      |     0.1 | HSC-CQR recency | QShrink-CQR (cov) | under      |           837 |          0.0018 |           0.0153 | -0.0135 | [-0.0217, -0.0054] |                  19 |                  0 | 0      |     nan      |               nan |   0      | confirmatory |
| main  | BDG2      |            | none      |     0.1 | HSC-CQR recency | QShrink-CQR (cov) | under_wk1  |           837 |          0.1659 |           0.165  |  0.0009 | [-0.0078, 0.0128]  |                  37 |                 34 | 0.8126 |     nan      |               nan |   1      | confirmatory |
| main  | BDG2      |            | none      |     0.1 | HSC-CQR recency | QShrink-CQR (cov) | log_rel_IS |           837 |        nan      |         nan      |  0.0003 | [0.0000, 0.0005]   |                 nan |                nan | 0.6364 |       0.9931 |                 1 |   1      | confirmatory |
| main  | BDG2      |            | none      |     0.1 | HSC-CQR recency | ACI-CQR (cov)     | under      |           837 |          0.0018 |           0.0259 | -0.0241 | [-0.0416, -0.0126] |                  42 |                  1 | 0      |     nan      |               nan |   0      | confirmatory |
| main  | BDG2      |            | none      |     0.1 | HSC-CQR recency | ACI-CQR (cov)     | under_wk1  |           837 |          0.1659 |           0.2089 | -0.043  | [-0.0668, -0.0174] |                 105 |                 35 | 0      |     nan      |               nan |   0      | confirmatory |
| main  | BDG2      |            | none      |     0.1 | HSC-CQR recency | ACI-CQR (cov)     | log_rel_IS |           837 |        nan      |         nan      |  0.0019 | [0.0016, 0.0024]   |                 nan |                nan | 0      |       0.9927 |                 1 |   0      | confirmatory |
| main  | BDG2      |            | none      |     0.1 | HSC-CQR recency | Self-CQR          | under      |           837 |          0.0018 |           0.0625 | -0.0607 | [-0.0819, -0.0459] |                  87 |                  0 | 0      |     nan      |               nan |   0      | confirmatory |
| main  | BDG2      |            | none      |     0.1 | HSC-CQR recency | Self-CQR          | under_wk1  |           837 |          0.1659 |           0.348  | -0.1821 | [-0.2386, -0.1348] |                 335 |                 55 | 0      |     nan      |               nan |   0      | confirmatory |
| main  | BDG2      |            | none      |     0.1 | HSC-CQR recency | Self-CQR          | log_rel_IS |           837 |        nan      |         nan      | -0.0107 | [-0.0116, -0.0100] |                 nan |                nan | 0      |       0.934  |                 1 |   0      | confirmatory |
| main  | UCI       |            | none      |     0.1 | HSC-CQR recency | CQR               | under      |           270 |          0      |           0.1228 | -0.1228 | [-0.1611, -0.0861] |                  54 |                  0 | 0      |     nan      |               nan |   0      | confirmatory |
| main  | UCI       |            | none      |     0.1 | HSC-CQR recency | CQR               | under_wk1  |           270 |          0.0704 |           0.1522 | -0.0818 | [-0.1219, -0.0429] |                  48 |                 12 | 0      |     nan      |               nan |   0      | confirmatory |
| main  | UCI       |            | none      |     0.1 | HSC-CQR recency | CQR               | log_rel_IS |           270 |        nan      |         nan      |  0.0015 | [-0.0005, 0.0025]  |                 nan |                nan | 0.8521 |       0.9993 |                 1 |   1      | confirmatory |
| main  | UCI       |            | none      |     0.1 | HSC-CQR recency | QShrink-CQR (cov) | under      |           270 |          0      |           0.0012 | -0.0012 | [-0.0037, 0.0000]  |                   1 |                  0 | 1      |     nan      |               nan |   1      | confirmatory |
| main  | UCI       |            | none      |     0.1 | HSC-CQR recency | QShrink-CQR (cov) | under_wk1  |           270 |          0.0704 |           0.0725 | -0.0022 | [-0.0225, 0.0191]  |                  12 |                 11 | 1      |     nan      |               nan |   1      | confirmatory |
| main  | UCI       |            | none      |     0.1 | HSC-CQR recency | QShrink-CQR (cov) | log_rel_IS |           270 |        nan      |         nan      |  0.0012 | [0.0011, 0.0017]   |                 nan |                nan | 0      |       1.0027 |                 1 |   0      | confirmatory |
| main  | UCI       |            | none      |     0.1 | HSC-CQR recency | ACI-CQR (cov)     | under      |           270 |          0      |           0.017  | -0.017  | [-0.0306, -0.0055] |                   9 |                  0 | 0.0039 |     nan      |               nan |   0.0312 | confirmatory |
| main  | UCI       |            | none      |     0.1 | HSC-CQR recency | ACI-CQR (cov)     | under_wk1  |           270 |          0.0704 |           0.1448 | -0.0744 | [-0.1114, -0.0352] |                  44 |                 12 | 0      |     nan      |               nan |   0.0002 | confirmatory |
| main  | UCI       |            | none      |     0.1 | HSC-CQR recency | ACI-CQR (cov)     | log_rel_IS |           270 |        nan      |         nan      |  0.0012 | [0.0005, 0.0019]   |                 nan |                nan | 0.0358 |       0.9957 |                 1 |   0.2188 | confirmatory |
| main  | UCI       |            | none      |     0.1 | HSC-CQR recency | Self-CQR          | under      |           270 |          0      |           0.0154 | -0.0154 | [-0.0303, -0.0037] |                   6 |                  0 | 0.0312 |     nan      |               nan |   0.2188 | confirmatory |
| main  | UCI       |            | none      |     0.1 | HSC-CQR recency | Self-CQR          | under_wk1  |           270 |          0.0704 |           0.2269 | -0.1565 | [-0.1975, -0.1105] |                  85 |                 10 | 0      |     nan      |               nan |   0      | confirmatory |
| main  | UCI       |            | none      |     0.1 | HSC-CQR recency | Self-CQR          | log_rel_IS |           270 |        nan      |         nan      | -0.006  | [-0.0070, -0.0053] |                 nan |                nan | 0      |       0.9845 |                 1 |   0      | confirmatory |


**Table S17. Window, first-week and weekly under-coverage with the oracle reference and excess over it.**

| dataset   | method                      |   n_buildings |   under |   under_wk1 |   wk_under_late |   anyweek_85 |   anyweek_80 |   anyweek_75 |   wk_under_n |   ref_under_win |   ref_under_week |   ref_anyweek |   excess_win | excess_win_ci   |   excess_wk2_8 | excess_wk2_8_ci   |   excess_wk1 | excess_wk1_ci   |   excess_anyweek | excess_anyweek_ci   |
|:----------|:----------------------------|--------------:|--------:|------------:|----------------:|-------------:|-------------:|-------------:|-------------:|----------------:|-----------------:|--------------:|-------------:|:----------------|---------------:|:------------------|-------------:|:----------------|-----------------:|:--------------------|
| BDG2      | HSC-CQR recency             |           837 |  0.0018 |      0.1659 |          0.1977 |       0.8312 |       0.4393 |       0.1739 |       1.5293 |          0.0185 |           0.1731 |        0.7284 |      -0.0167 | [-2.2, -1.2]    |         0.0246 | [1.5, 3.3]        |      -0.0072 | [-4.7, 3.9]     |           0.1028 | [7.9, 12.6]         |
| BDG2      | HSC-CQR recency (capped)    |           837 |  0.004  |      0.1677 |          0.1987 |       0.8318 |       0.4403 |       0.1743 |       1.538  |          0.0185 |           0.1731 |        0.7284 |      -0.0145 | [-1.9, -0.8]    |         0.0256 | [1.6, 3.5]        |      -0.0054 | [-4.5, 4.0]     |           0.1034 | [7.9, 12.6]         |
| BDG2      | QShrink-CQR recency         |           837 |  0.0058 |      0.1736 |          0.1916 |       0.8192 |       0.4318 |       0.1738 |       1.4939 |          0.0185 |           0.1731 |        0.7284 |      -0.0127 | [-1.7, -0.7]    |         0.0185 | [0.5, 2.9]        |       0.0005 | [-4.3, 4.6]     |           0.0907 | [6.1, 11.7]         |
| BDG2      | Self-CQR recency            |           837 |  0.0165 |      0.3422 |          0.2075 |       0.8801 |       0.5    |       0.2045 |       1.7739 |          0.0185 |           0.1731 |        0.7284 |      -0.002  | [-1.2, 1.1]     |         0.0344 | [2.9, 4.4]        |       0.1691 | [13.8, 20.8]    |           0.1517 | [13.1, 17.8]        |
| BDG2      | HSC-SSC-CQR                 |           837 |  0.0078 |      0.1471 |          0.2035 |       0.8319 |       0.4803 |       0.2018 |       1.5509 |          0.0185 |           0.1731 |        0.7284 |      -0.0108 | [-1.7, -0.4]    |         0.0304 | [2.2, 4.1]        |      -0.026  | [-6.0, 3.0]     |           0.1035 | [8.5, 12.7]         |
| BDG2      | HSC-CQR simple (cov)        |           837 |  0.011  |      0.1837 |          0.2119 |       0.8591 |       0.5043 |       0.2121 |       1.6463 |          0.0185 |           0.1731 |        0.7284 |      -0.0076 | [-1.1, -0.2]    |         0.0388 | [3.2, 5.0]        |       0.0106 | [-4.1, 6.6]     |           0.1306 | [11.0, 15.2]        |
| BDG2      | QShrink-CQR (cov)           |           837 |  0.0153 |      0.165  |          0.209  |       0.8394 |       0.4973 |       0.21   |       1.6075 |          0.0185 |           0.1731 |        0.7284 |      -0.0032 | [-1.0, 0.6]     |         0.0359 | [2.7, 4.6]        |      -0.0081 | [-5.4, 4.6]     |           0.1109 | [8.0, 13.9]         |
| BDG2      | ACI-CQR (cov)               |           837 |  0.0259 |      0.2089 |          0.1981 |       0.8087 |       0.4854 |       0.2175 |       1.5747 |          0.0185 |           0.1731 |        0.7284 |       0.0074 | [-0.1, 2.2]     |         0.025  | [0.6, 4.0]        |       0.0358 | [-2.7, 9.0]     |           0.0803 | [3.9, 11.4]         |
| BDG2      | HSC-CQR fixed-κ             |           837 |  0.0098 |      0.1902 |          0.2114 |       0.8599 |       0.5071 |       0.2141 |       1.6497 |          0.0185 |           0.1731 |        0.7284 |      -0.0088 | [-1.3, -0.3]    |         0.0384 | [3.1, 4.8]        |       0.0172 | [-3.5, 7.1]     |           0.1314 | [11.2, 15.0]        |
| BDG2      | Self-CQR                    |           837 |  0.0625 |      0.348  |          0.229  |       0.8848 |       0.5709 |       0.2542 |       1.9304 |          0.0185 |           0.1731 |        0.7284 |       0.044  | [2.8, 6.6]      |         0.0559 | [4.4, 7.2]        |       0.175  | [14.2, 21.6]    |           0.1563 | [13.1, 19.0]        |
| BDG2      | ACI-CQR                     |           837 |  0.0485 |      0.2136 |          0.2079 |       0.7953 |       0.5085 |       0.2433 |       1.648  |          0.0185 |           0.1731 |        0.7284 |       0.03   | [1.7, 5.1]      |         0.0348 | [1.2, 5.3]        |       0.0405 | [-2.4, 9.3]     |           0.0668 | [1.9, 10.6]         |
| BDG2      | TQA-B-CQR                   |           837 |  0.1498 |      0.2118 |          0.2283 |       0.7177 |       0.476  |       0.2567 |       1.7892 |          0.0185 |           0.1731 |        0.7284 |       0.1313 | [7.2, 18.6]     |         0.0552 | [0.8, 9.9]        |       0.0387 | [-2.2, 9.2]     |          -0.0107 | [-9.4, 6.5]         |
| BDG2      | GHCP-CQR                    |           837 |  0.1435 |      0.221  |          0.2257 |       0.7238 |       0.502  |       0.2871 |       1.78   |          0.0185 |           0.1731 |        0.7284 |       0.1249 | [7.5, 17.8]     |         0.0526 | [1.0, 9.0]        |       0.048  | [-2.1, 10.3]    |          -0.0046 | [-8.3, 6.5]         |
| BDG2      | HSC-CQR recency κ=∞         |           837 |  0.1549 |      0.2354 |          0.2323 |       0.7347 |       0.5168 |       0.2994 |       1.8406 |          0.0185 |           0.1731 |        0.7284 |       0.1364 | [7.9, 19.3]     |         0.0592 | [1.4, 9.8]        |       0.0623 | [-0.3, 11.5]    |           0.0063 | [-6.7, 7.4]         |
| BDG2      | CQR                         |           837 |  0.1522 |      0.2196 |          0.2362 |       0.7392 |       0.5119 |       0.3002 |       1.8525 |          0.0185 |           0.1731 |        0.7284 |       0.1337 | [7.8, 19.4]     |         0.0631 | [1.9, 10.2]       |       0.0465 | [-1.9, 9.9]     |           0.0107 | [-5.9, 7.5]         |
| BDG2      | HSC-CQR recency (delay 1d)  |           837 |  0.0042 |      0.1845 |          0.2091 |       0.8595 |       0.5051 |       0.2165 |       1.6274 |          0.0185 |           0.1731 |        0.7284 |      -0.0143 | [-1.9, -1.0]    |         0.036  | [2.7, 4.4]        |       0.0114 | [-2.9, 5.4]     |           0.131  | [11.2, 15.3]        |
| BDG2      | QShrink-CQR (cov, delay 1d) |           837 |  0.0157 |      0.1826 |          0.2135 |       0.8551 |       0.5307 |       0.2451 |       1.6565 |          0.0185 |           0.1731 |        0.7284 |      -0.0028 | [-0.9, 0.6]     |         0.0404 | [3.2, 4.9]        |       0.0095 | [-3.9, 5.6]     |           0.1267 | [10.7, 14.7]        |
| BDG2      | ACI-CQR (cov, delay 1d)     |           837 |  0.025  |      0.2138 |          0.2049 |       0.8223 |       0.5102 |       0.2431 |       1.6276 |          0.0185 |           0.1731 |        0.7284 |       0.0065 | [-0.2, 2.1]     |         0.0318 | [1.4, 4.7]        |       0.0407 | [-2.1, 9.4]     |           0.0939 | [5.7, 12.5]         |
| UCI       | HSC-CQR recency             |           270 |  0      |      0.0704 |          0.1321 |       0.6836 |       0.2142 |       0.0321 |       0.9948 |          0.006  |           0.128  |        0.6079 |      -0.006  | [-0.7, -0.5]    |         0.004  | [-0.7, 1.4]       |      -0.0577 | [-8.5, -3.0]    |           0.0758 | [3.3, 11.2]         |
| UCI       | HSC-CQR recency (capped)    |           270 |  0.0012 |      0.0759 |          0.1339 |       0.6855 |       0.2179 |       0.0358 |       1.0133 |          0.006  |           0.128  |        0.6079 |      -0.0047 | [-0.7, -0.2]    |         0.0059 | [-0.5, 1.6]       |      -0.0521 | [-8.0, -2.3]    |           0.0776 | [3.6, 11.4]         |
| UCI       | QShrink-CQR recency         |           270 |  0      |      0.0836 |          0.1334 |       0.6864 |       0.209  |       0.0272 |       1.0176 |          0.006  |           0.128  |        0.6079 |      -0.006  | [-0.7, -0.5]    |         0.0054 | [-0.6, 1.6]       |      -0.0444 | [-7.1, -1.6]    |           0.0785 | [3.3, 11.6]         |
| UCI       | Self-CQR recency            |           270 |  0.0012 |      0.2182 |          0.1436 |       0.7744 |       0.2642 |       0.0395 |       1.2231 |          0.006  |           0.128  |        0.6079 |      -0.0047 | [-0.7, -0.2]    |         0.0155 | [0.4, 2.7]        |       0.0902 | [5.0, 13.0]     |           0.1665 | [12.5, 20.6]        |
| UCI       | HSC-SSC-CQR                 |           270 |  0.0012 |      0.0728 |          0.1377 |       0.6991 |       0.2272 |       0.0503 |       1.037  |          0.006  |           0.128  |        0.6079 |      -0.0047 | [-0.7, -0.2]    |         0.0097 | [-0.2, 2.2]       |      -0.0552 | [-8.1, -2.6]    |           0.0912 | [5.0, 13.1]         |
| UCI       | HSC-CQR simple (cov)        |           270 |  0.0052 |      0.0997 |          0.1445 |       0.7238 |       0.2565 |       0.0497 |       1.1111 |          0.006  |           0.128  |        0.6079 |      -0.0007 | [-0.5, 0.5]     |         0.0165 | [0.4, 2.9]        |      -0.0283 | [-6.1, 0.4]     |           0.1159 | [7.9, 15.3]         |
| UCI       | QShrink-CQR (cov)           |           270 |  0.0012 |      0.0725 |          0.1461 |       0.6988 |       0.242  |       0.0503 |       1.0954 |          0.006  |           0.128  |        0.6079 |      -0.0047 | [-0.7, -0.2]    |         0.0181 | [0.5, 3.1]        |      -0.0555 | [-8.1, -2.8]    |           0.0909 | [5.0, 12.9]         |
| UCI       | ACI-CQR (cov)               |           270 |  0.017  |      0.1448 |          0.1226 |       0.6441 |       0.2148 |       0.0568 |       1.0031 |          0.006  |           0.128  |        0.6079 |       0.011  | [-0.1, 2.5]     |        -0.0054 | [-1.8, 0.6]       |       0.0167 | [-2.1, 5.6]     |           0.0363 | [-1.3, 8.2]         |
| UCI       | HSC-CQR fixed-κ             |           270 |  0.0052 |      0.1188 |          0.1393 |       0.7247 |       0.2651 |       0.0478 |       1.0938 |          0.006  |           0.128  |        0.6079 |      -0.0007 | [-0.5, 0.5]     |         0.0113 | [-0.1, 2.3]       |      -0.0092 | [-4.3, 2.6]     |           0.1168 | [7.8, 15.3]         |
| UCI       | Self-CQR                    |           270 |  0.0154 |      0.2269 |          0.1612 |       0.779  |       0.3269 |       0.0688 |       1.3552 |          0.006  |           0.128  |        0.6079 |       0.0095 | [-0.2, 2.4]     |         0.0332 | [2.0, 4.6]        |       0.0988 | [5.9, 13.9]     |           0.1711 | [13.0, 21.0]        |
| UCI       | ACI-CQR                     |           270 |  0.0519 |      0.1497 |          0.1493 |       0.6691 |       0.283  |       0.075  |       1.1948 |          0.006  |           0.128  |        0.6079 |       0.0459 | [2.3, 7.2]      |         0.0213 | [0.6, 3.7]        |       0.0217 | [-1.7, 6.2]     |           0.0613 | [1.5, 10.5]         |
| UCI       | TQA-B-CQR                   |           270 |  0.1046 |      0.1367 |          0.1764 |       0.579  |       0.2849 |       0.1201 |       1.3713 |          0.006  |           0.128  |        0.6079 |       0.0987 | [6.6, 13.3]     |         0.0483 | [2.3, 7.5]        |       0.0087 | [-2.9, 4.8]     |          -0.0289 | [-8.3, 2.1]         |
| UCI       | GHCP-CQR                    |           270 |  0.0926 |      0.1454 |          0.1494 |       0.5457 |       0.2688 |       0.1105 |       1.1914 |          0.006  |           0.128  |        0.6079 |       0.0866 | [5.5, 12.1]     |         0.0214 | [0.1, 4.3]        |       0.0173 | [-1.9, 5.8]     |          -0.0622 | [-11.1, -1.2]       |
| UCI       | HSC-CQR recency κ=∞         |           270 |  0.1216 |      0.1716 |          0.1735 |       0.5904 |       0.3022 |       0.1401 |       1.3861 |          0.006  |           0.128  |        0.6079 |       0.1156 | [7.9, 15.3]     |         0.0455 | [2.2, 7.0]        |       0.0436 | [0.4, 8.6]      |          -0.0174 | [-6.5, 3.1]         |
| UCI       | CQR                         |           270 |  0.1228 |      0.1522 |          0.1832 |       0.604  |       0.3176 |       0.1373 |       1.4349 |          0.006  |           0.128  |        0.6079 |       0.1169 | [8.1, 15.5]     |         0.0552 | [3.2, 8.0]        |       0.0241 | [-1.5, 6.5]     |          -0.0039 | [-5.3, 4.3]         |
| UCI       | HSC-CQR recency (delay 1d)  |           270 |  0.0012 |      0.0948 |          0.1462 |       0.7222 |       0.2747 |       0.0556 |       1.1179 |          0.006  |           0.128  |        0.6079 |      -0.0047 | [-0.7, -0.2]    |         0.0181 | [0.6, 2.9]        |      -0.0333 | [-6.4, -0.4]    |           0.1143 | [7.4, 15.3]         |
| UCI       | QShrink-CQR (cov, delay 1d) |           270 |  0.0049 |      0.1028 |          0.1514 |       0.7343 |       0.2926 |       0.0614 |       1.1623 |          0.006  |           0.128  |        0.6079 |      -0.001  | [-0.6, 0.8]     |         0.0233 | [1.0, 3.6]        |      -0.0253 | [-5.6, 0.6]     |           0.1264 | [8.6, 16.3]         |
| UCI       | ACI-CQR (cov, delay 1d)     |           270 |  0.017  |      0.1485 |          0.1327 |       0.6836 |       0.2451 |       0.0645 |       1.0775 |          0.006  |           0.128  |        0.6079 |       0.011  | [-0.1, 2.5]     |         0.0047 | [-0.8, 1.6]       |       0.0204 | [-1.7, 6.0]     |           0.0758 | [3.4, 11.5]         |


**Table S18. Sharpness tails: median and mean relative interval score, width ratio to pooled CQR, capacity-headroom cost.**

| dataset   | method                      |   rel_IS_median |   rel_IS_mean |   width_ratio_p99 |   width_ratio_max |   n_width_gt5x |   rel_IS_early_median |   cost20_mean |   cost20_worst10 |   cost20_max |   underprot |
|:----------|:----------------------------|----------------:|--------------:|------------------:|------------------:|---------------:|----------------------:|--------------:|-----------------:|-------------:|------------:|
| BDG2      | HSC-CQR recency             |          0.5591 |        0.7464 |            1.431  |            6.517  |              2 |                0.5667 |        1.4299 |           2.5897 |      21.8977 |      0.0232 |
| BDG2      | HSC-CQR recency (capped)    |          0.5591 |        0.7257 |            1.3608 |            1.5397 |              0 |                0.5667 |        1.4205 |           2.4977 |      15.0506 |      0.0239 |
| BDG2      | QShrink-CQR recency         |          0.5587 |        0.7553 |            1.486  |            8.4719 |              3 |                0.5669 |        1.4333 |           2.6214 |      24.3973 |      0.0206 |
| BDG2      | Self-CQR recency            |          0.5666 |        0.7968 |            1.6945 |           26.4    |              4 |                0.6055 |        1.4526 |           2.787  |      35.1916 |      0.0179 |
| BDG2      | HSC-SSC-CQR                 |          0.5627 |        0.8971 |            1.6547 |           87.8963 |              3 |                0.5657 |        1.5044 |           3.3295 |      92.5471 |      0.0206 |
| BDG2      | HSC-CQR simple (cov)        |          0.5603 |        0.7329 |            1.3824 |            3.9086 |              0 |                0.5657 |        1.4233 |           2.5258 |      17.7018 |      0.0299 |
| BDG2      | QShrink-CQR (cov)           |          0.5609 |        0.7516 |            1.4538 |            8.8225 |              3 |                0.5637 |        1.4317 |           2.6051 |      24.7203 |      0.0265 |
| BDG2      | ACI-CQR (cov)               |          0.557  |        0.7519 |            1.8245 |           14.6058 |              1 |                0.5592 |        1.4342 |           2.6353 |      14.9549 |      0.0398 |
| BDG2      | HSC-CQR fixed-κ             |          0.5597 |        0.7298 |            1.3501 |            3.3845 |              0 |                0.5626 |        1.4226 |           2.5201 |      17.7018 |      0.0299 |
| BDG2      | Self-CQR                    |          0.5659 |        0.7992 |            1.7785 |           30.988  |              4 |                0.6051 |        1.4538 |           2.7963 |      35.2602 |      0.0285 |
| BDG2      | ACI-CQR                     |          0.5566 |        0.7427 |            1.242  |           14.6058 |              1 |                0.5592 |        1.4298 |           2.5943 |      14.94   |      0.0484 |
| BDG2      | TQA-B-CQR                   |          0.5579 |        0.7336 |            2.0191 |            3.5034 |              0 |                0.5582 |        1.4261 |           2.5244 |      15.0289 |      0.0664 |
| BDG2      | GHCP-CQR                    |          0.5569 |        0.7326 |            1.0191 |            1.0309 |              0 |                0.5617 |        1.4252 |           2.5348 |      14.9361 |      0.0717 |
| BDG2      | HSC-CQR recency κ=∞         |          0.5572 |        0.7328 |            1.0023 |            1.0062 |              0 |                0.5607 |        1.4252 |           2.5356 |      14.9353 |      0.077  |
| BDG2      | CQR                         |          0.5574 |        0.7328 |            1      |            1      |              0 |                0.5601 |        1.4252 |           2.5354 |      14.9378 |      0.077  |
| BDG2      | HSC-CQR recency (delay 1d)  |          0.5636 |        0.7498 |            1.4343 |            6.6629 |              2 |                0.5659 |        1.4313 |           2.5922 |      21.4383 |      0.0239 |
| BDG2      | QShrink-CQR (cov, delay 1d) |          0.5637 |        0.7532 |            1.4943 |            7.8211 |              3 |                0.564  |        1.4324 |           2.604  |      23.4067 |      0.0265 |
| BDG2      | ACI-CQR (cov, delay 1d)     |          0.5582 |        0.7647 |            2.1986 |           12.3469 |              2 |                0.5595 |        1.4403 |           2.6823 |      15.8694 |      0.0398 |
| BDG2      | HSC-CQR recency (MLP)       |          0.5642 |        0.7553 |            1.4834 |           10.7039 |              2 |                0.5917 |        1.4341 |           2.5808 |      26.6318 |      0.0511 |
| BDG2      | HSC-CQR (MLP)               |          0.5607 |        0.7306 |            1.3075 |            1.9215 |              0 |                0.5867 |        1.4226 |           2.4725 |      15.186  |      0.0584 |
| BDG2      | CQR (MLP)                   |          0.562  |        0.7387 |            1.2662 |            2.0353 |              0 |                0.5855 |        1.4263 |           2.4981 |      14.9603 |      0.0883 |
| UCI       | HSC-CQR recency             |          0.3643 |        0.5415 |            1.4625 |            2.5345 |              0 |                0.417  |        1.3126 |           2.2649 |       7.8974 |      0.0021 |
| UCI       | HSC-CQR recency (capped)    |          0.3643 |        0.5371 |            1.3132 |            1.6279 |              0 |                0.417  |        1.312  |           2.2614 |       7.9708 |      0.0042 |
| UCI       | QShrink-CQR recency         |          0.365  |        0.5425 |            1.5278 |            2.7085 |              0 |                0.4159 |        1.3126 |           2.2648 |       7.8887 |      0.0021 |
| UCI       | Self-CQR recency            |          0.3677 |        0.5496 |            1.6897 |            2.8953 |              0 |                0.4332 |        1.3153 |           2.2808 |       8.1629 |      0.0042 |
| UCI       | HSC-SSC-CQR                 |          0.364  |        0.5616 |            1.7888 |            4.0762 |              0 |                0.4106 |        1.3225 |           2.3645 |       7.8981 |      0.0042 |
| UCI       | HSC-CQR simple (cov)        |          0.364  |        0.5392 |            1.3954 |            2.0269 |              0 |                0.41   |        1.3127 |           2.2714 |       7.9506 |      0.0042 |
| UCI       | QShrink-CQR (cov)           |          0.3642 |        0.5401 |            1.46   |            2.1668 |              0 |                0.4116 |        1.3125 |           2.2666 |       7.8539 |      0.0042 |
| UCI       | ACI-CQR (cov)               |          0.3627 |        0.5439 |            1.5722 |            2.996  |              0 |                0.4079 |        1.3145 |           2.2828 |       7.7266 |      0.0063 |
| UCI       | HSC-CQR fixed-κ             |          0.3637 |        0.537  |            1.3511 |            1.7734 |              0 |                0.4075 |        1.3117 |           2.2636 |       7.9506 |      0.0042 |
| UCI       | Self-CQR                    |          0.368  |        0.5501 |            1.7979 |            2.3753 |              0 |                0.4323 |        1.3163 |           2.2887 |       8.2221 |      0.0063 |
| UCI       | ACI-CQR                     |          0.3615 |        0.5393 |            1.1684 |            2.9779 |              0 |                0.4079 |        1.3131 |           2.2752 |       7.9627 |      0.0105 |
| UCI       | TQA-B-CQR                   |          0.3622 |        0.5422 |            1.9294 |            3.3512 |              0 |                0.4055 |        1.3147 |           2.276  |       8.0042 |      0.0316 |
| UCI       | GHCP-CQR                    |          0.3628 |        0.5421 |            1.0531 |            1.0712 |              0 |                0.4075 |        1.3149 |           2.284  |       8.0871 |      0.0211 |
| UCI       | HSC-CQR recency κ=∞         |          0.3629 |        0.5418 |            1.0026 |            1.0038 |              0 |                0.4056 |        1.3147 |           2.2862 |       8.0911 |      0.0274 |
| UCI       | CQR                         |          0.3623 |        0.5419 |            1      |            1      |              0 |                0.4063 |        1.3148 |           2.2855 |       8.0924 |      0.0274 |
| UCI       | HSC-CQR recency (delay 1d)  |          0.366  |        0.5443 |            1.4742 |            2.6194 |              0 |                0.4173 |        1.3138 |           2.2711 |       7.8934 |      0.0021 |
| UCI       | QShrink-CQR (cov, delay 1d) |          0.3646 |        0.5427 |            1.4533 |            2.1552 |              0 |                0.4139 |        1.3137 |           2.2749 |       7.9759 |      0.0042 |
| UCI       | ACI-CQR (cov, delay 1d)     |          0.366  |        0.5496 |            1.7672 |            2.9491 |              0 |                0.4086 |        1.3178 |           2.3008 |       7.786  |      0.0063 |
| UCI       | HSC-CQR recency (MLP)       |          0.3706 |        0.5343 |            1.4256 |            1.9681 |              0 |                0.4331 |        1.303  |           2.151  |       6.187  |      0      |
| UCI       | HSC-CQR (MLP)               |          0.3694 |        0.5314 |            1.3742 |            1.5914 |              0 |                0.4256 |        1.3023 |           2.1475 |       6.1815 |      0      |
| UCI       | CQR (MLP)                   |          0.3704 |        0.5352 |            1.2638 |            1.6232 |              0 |                0.4244 |        1.3041 |           2.1583 |       6.2152 |      0.0189 |


**Table S19. Under-covered share over the window and in the first week at matched pseudo-count for own-score decay factors 0.8–1.0.**

| dataset   |   param |   under | HSC (decay 0.8) |   under | HSC (decay 0.9) |   under | HSC (decay 0.95) |   under | HSC (decay 1.0) |   under_wk1 | HSC (decay 0.8) |   under_wk1 | HSC (decay 0.9) |   under_wk1 | HSC (decay 0.95) |   under_wk1 | HSC (decay 1.0) |
|:----------|--------:|--------------------------:|--------------------------:|---------------------------:|--------------------------:|------------------------------:|------------------------------:|-------------------------------:|------------------------------:|
| BDG2      |       0 |                    0.0027 |                    0.006  |                     0.0153 |                    0.0577 |                        0.2906 |                        0.2952 |                         0.3012 |                        0.3098 |
| BDG2      |       6 |                    0.0007 |                    0.0026 |                     0.0073 |                    0.0438 |                        0.193  |                        0.2128 |                         0.2234 |                        0.2321 |
| BDG2      |      12 |                    0.0007 |                    0.0013 |                     0.0033 |                    0.0358 |                        0.1584 |                        0.1737 |                         0.1843 |                        0.1902 |
| BDG2      |      24 |                    0.0007 |                    0.0007 |                     0.002  |                    0.0252 |                        0.1438 |                        0.1563 |                         0.1616 |                        0.1677 |
| BDG2      |      48 |                    0.0027 |                    0.0007 |                     0.0013 |                    0.0225 |                        0.1399 |                        0.1458 |                         0.1524 |                        0.1557 |
| BDG2      |      96 |                    0.0126 |                    0.0039 |                     0.002  |                    0.0132 |                        0.1604 |                        0.1604 |                         0.1617 |                        0.163  |
| BDG2      |     168 |                    0.0385 |                    0.0146 |                     0.0066 |                    0.0093 |                        0.1917 |                        0.1943 |                         0.1896 |                        0.189  |
| BDG2      |     336 |                    0.0876 |                    0.0557 |                     0.0345 |                    0.0166 |                        0.215  |                        0.2123 |                         0.2089 |                        0.2056 |
| BDG2      |     672 |                    0.1174 |                    0.1015 |                     0.0743 |                    0.0497 |                        0.2256 |                        0.2249 |                         0.2243 |                        0.2236 |
| BDG2      |    1344 |                    0.1367 |                    0.1268 |                     0.1128 |                    0.0816 |                        0.2289 |                        0.2303 |                         0.2296 |                        0.2296 |
| BDG2      |     inf |                    0.162  |                    0.162  |                     0.162  |                    0.162  |                        0.2369 |                        0.2369 |                         0.2369 |                        0.2369 |
| UCI       |       0 |                    0      |                    0      |                     0.0021 |                    0.0126 |                        0.1705 |                        0.1832 |                         0.2063 |                        0.2147 |
| UCI       |       6 |                    0      |                    0      |                     0      |                    0.0063 |                        0.0947 |                        0.1179 |                         0.1179 |                        0.1263 |
| UCI       |      12 |                    0      |                    0      |                     0      |                    0.0063 |                        0.0632 |                        0.08   |                         0.0863 |                        0.0947 |
| UCI       |      24 |                    0      |                    0      |                     0      |                    0.0063 |                        0.0674 |                        0.0695 |                         0.0737 |                        0.0779 |
| UCI       |      48 |                    0      |                    0      |                     0      |                    0.0063 |                        0.08   |                        0.0779 |                         0.0758 |                        0.0737 |
| UCI       |      96 |                    0.0042 |                    0.0021 |                     0.0021 |                    0.0042 |                        0.0968 |                        0.0905 |                         0.0863 |                        0.0863 |
| UCI       |     168 |                    0.0274 |                    0.0063 |                     0.0021 |                    0.0084 |                        0.1284 |                        0.1284 |                         0.12   |                        0.1221 |
| UCI       |     336 |                    0.0716 |                    0.0421 |                     0.0295 |                    0.0084 |                        0.1474 |                        0.1453 |                         0.1453 |                        0.1432 |
| UCI       |     672 |                    0.0905 |                    0.0779 |                     0.0526 |                    0.0316 |                        0.1621 |                        0.16   |                         0.1621 |                        0.1621 |
| UCI       |    1344 |                    0.0926 |                    0.0905 |                     0.0863 |                    0.0568 |                        0.1642 |                        0.1642 |                         0.1642 |                        0.1642 |
| UCI       |     inf |                    0.1116 |                    0.1116 |                     0.1116 |                    0.1116 |                        0.1642 |                        0.1642 |                         0.1642 |                        0.1642 |


**Table S20. Stress tests on BDG2, all strategies (3 seeds; unit = building; McNemar against the recommended configuration).**

| perturb         | method                   |   under |   under_sd_seeds |   under_wk1 |   rel_IS |   rel_IS_mean |   underprot |   cov_post_mean |   diff_vs_primary |   p_mcnemar |
|:----------------|:-------------------------|--------:|-----------------:|------------:|---------:|--------------:|------------:|----------------:|------------------:|------------:|
| calpool10       | HSC-CQR recency          |  0.0022 |           0.0038 |      0.18   |   0.5569 |        0.7466 |      0.0252 |          0.8965 |          nan      |    nan      |
| calpool10       | HSC-CQR recency (capped) |  0.0044 |           0.0038 |      0.1844 |   0.5569 |        0.7217 |      0.0263 |          0.8963 |            0.002  |      0.5    |
| calpool10       | QShrink-CQR recency      |  0.0055 |           0.005  |      0.2294 |   0.5615 |        0.757  |      0.0165 |          0.8966 |            0.0036 |      0.25   |
| calpool10       | Self-CQR recency         |  0.011  |           0.005  |      0.3359 |   0.5619 |        0.7657 |      0.0187 |          0.8955 |            0.0082 |      0.0078 |
| calpool10       | HSC-SSC-CQR              |  0.0088 |           0.0019 |      0.1482 |   0.5585 |        1.8961 |      0.0187 |          0.8968 |            0.0059 |      0.0703 |
| calpool10       | HSC-CQR simple (cov)     |  0.0187 |           0.005  |      0.1888 |   0.5582 |        0.7298 |      0.0307 |          0.8948 |            0.0156 |      0.0001 |
| calpool10       | QShrink-CQR (cov)        |  0.0198 |           0.0119 |      0.1932 |   0.5576 |        0.7368 |      0.0252 |          0.8955 |            0.0179 |      0      |
| calpool10       | ACI-CQR (cov)            |  0.0066 |           0.0114 |      0.2009 |   0.5548 |        0.7685 |      0.0351 |          0.8956 |            0.0026 |      0.2891 |
| calpool10       | HSC-CQR fixed-κ          |  0.0121 |           0.0068 |      0.1932 |   0.5544 |        0.722  |      0.0307 |          0.895  |            0.0089 |      0.0039 |
| calpool10       | Self-CQR                 |  0.0615 |           0.0132 |      0.348  |   0.5633 |        0.767  |      0.0285 |          0.8938 |            0.0616 |      0      |
| calpool10       | ACI-CQR                  |  0.0198 |           0.0198 |      0.2053 |   0.5543 |        0.7665 |      0.0373 |          0.8944 |            0.0151 |      0.0004 |
| calpool10       | TQA-B-CQR                |  0.1581 |           0.0117 |      0.2206 |   0.5544 |        0.7278 |      0.0714 |          0.8919 |            0.1544 |      0      |
| calpool10       | GHCP-CQR                 |  0.0659 |           0.0129 |      0.1251 |   0.5539 |        0.7317 |      0.0483 |          0.9095 |            0.0598 |      0      |
| calpool10       | HSC-CQR recency κ=∞      |  0.1471 |           0.0056 |      0.225  |   0.5543 |        0.7263 |      0.0692 |          0.8968 |            0.1478 |      0      |
| calpool10       | CQR                      |  0.1449 |           0.0124 |      0.2042 |   0.555  |        0.7275 |      0.0714 |          0.8928 |            0.1442 |      0      |
| calpool25       | HSC-CQR recency          |  0.0022 |           0.0038 |      0.1734 |   0.5565 |        0.7403 |      0.0209 |          0.8959 |          nan      |    nan      |
| calpool25       | HSC-CQR recency (capped) |  0.0044 |           0.0038 |      0.1756 |   0.556  |        0.7205 |      0.0209 |          0.8956 |            0.002  |      0.5    |
| calpool25       | QShrink-CQR recency      |  0.0022 |           0.0038 |      0.2031 |   0.559  |        0.7504 |      0.0176 |          0.8966 |           -0      |      1      |
| calpool25       | Self-CQR recency         |  0.011  |           0.005  |      0.3535 |   0.5622 |        0.7653 |      0.0187 |          0.8955 |            0.0082 |      0.0078 |
| calpool25       | HSC-SSC-CQR              |  0.0088 |           0.0019 |      0.1592 |   0.5569 |        1.4987 |      0.0209 |          0.8967 |            0.0059 |      0.0703 |
| calpool25       | HSC-CQR simple (cov)     |  0.0165 |           0.0086 |      0.1833 |   0.555  |        0.7271 |      0.0318 |          0.8945 |            0.0118 |      0.0002 |
| calpool25       | QShrink-CQR (cov)        |  0.0121 |           0.0037 |      0.1899 |   0.5584 |        0.7395 |      0.0231 |          0.8954 |            0.0087 |      0.0039 |
| calpool25       | ACI-CQR (cov)            |  0.0241 |           0.023  |      0.2316 |   0.5562 |        0.7507 |      0.0428 |          0.8962 |            0.0204 |      0      |
| calpool25       | HSC-CQR fixed-κ          |  0.0143 |           0.0105 |      0.1921 |   0.5542 |        0.722  |      0.0307 |          0.8945 |            0.0105 |      0.001  |
| calpool25       | Self-CQR                 |  0.0626 |           0.0113 |      0.3677 |   0.5656 |        0.7666 |      0.0285 |          0.8938 |            0.0621 |      0      |
| calpool25       | ACI-CQR                  |  0.0351 |           0.0099 |      0.2327 |   0.5556 |        0.7337 |      0.045  |          0.8953 |            0.0307 |      0      |
| calpool25       | TQA-B-CQR                |  0.157  |           0.0217 |      0.2338 |   0.5549 |        0.7276 |      0.0746 |          0.8937 |            0.1559 |      0      |
| calpool25       | GHCP-CQR                 |  0.1218 |           0.0237 |      0.1932 |   0.5534 |        0.7266 |      0.0593 |          0.8989 |            0.1199 |      0      |
| calpool25       | HSC-CQR recency κ=∞      |  0.1614 |           0.0271 |      0.2393 |   0.5536 |        0.7265 |      0.0724 |          0.894  |            0.1598 |      0      |
| calpool25       | CQR                      |  0.1614 |           0.0281 |      0.2382 |   0.5529 |        0.7272 |      0.0724 |          0.8923 |            0.1587 |      0      |
| calpool50       | HSC-CQR recency          |  0.0022 |           0.0038 |      0.1723 |   0.5566 |        0.7402 |      0.0209 |          0.8959 |          nan      |    nan      |
| calpool50       | HSC-CQR recency (capped) |  0.0044 |           0.0038 |      0.1745 |   0.5566 |        0.7206 |      0.0209 |          0.8956 |            0.002  |      0.5    |
| calpool50       | QShrink-CQR recency      |  0.0022 |           0.0038 |      0.1899 |   0.5555 |        0.7451 |      0.0176 |          0.8965 |           -0      |      1      |
| calpool50       | Self-CQR recency         |  0.011  |           0.005  |      0.3524 |   0.5607 |        0.7652 |      0.0187 |          0.8955 |            0.0082 |      0.0078 |
| calpool50       | HSC-SSC-CQR              |  0.0077 |           0.0038 |      0.1581 |   0.5572 |        0.9313 |      0.0198 |          0.8961 |            0.0054 |      0.125  |
| calpool50       | HSC-CQR simple (cov)     |  0.0143 |           0.0105 |      0.1855 |   0.5551 |        0.7233 |      0.0296 |          0.8941 |            0.011  |      0.001  |
| calpool50       | QShrink-CQR (cov)        |  0.0121 |           0.0068 |      0.1745 |   0.5553 |        0.7386 |      0.0241 |          0.8951 |            0.0089 |      0.0039 |
| calpool50       | ACI-CQR (cov)            |  0.0373 |           0.0124 |      0.213  |   0.553  |        0.7433 |      0.0461 |          0.8941 |            0.034  |      0      |
| calpool50       | HSC-CQR fixed-κ          |  0.0132 |           0.0086 |      0.1965 |   0.5539 |        0.7219 |      0.0307 |          0.8945 |            0.0097 |      0.002  |
| calpool50       | Self-CQR                 |  0.0626 |           0.0113 |      0.3633 |   0.5638 |        0.7665 |      0.0285 |          0.8938 |            0.0621 |      0      |
| calpool50       | ACI-CQR                  |  0.0373 |           0.0124 |      0.213  |   0.553  |        0.7433 |      0.0461 |          0.8941 |            0.034  |      0      |
| calpool50       | TQA-B-CQR                |  0.146  |           0.0087 |      0.2097 |   0.5518 |        0.7271 |      0.067  |          0.8953 |            0.1444 |      0      |
| calpool50       | GHCP-CQR                 |  0.1405 |           0.005  |      0.2119 |   0.5538 |        0.7262 |      0.0648 |          0.8964 |            0.1385 |      0      |
| calpool50       | HSC-CQR recency κ=∞      |  0.157  |           0.016  |      0.2371 |   0.5537 |        0.7264 |      0.0746 |          0.8941 |            0.1582 |      0      |
| calpool50       | CQR                      |  0.1581 |           0.0155 |      0.2195 |   0.5537 |        0.7265 |      0.0735 |          0.8918 |            0.1587 |      0      |
| missing20       | HSC-CQR recency          |  0.0033 |           0.0057 |      0.1998 |   0.5831 |        0.7721 |      0.0241 |          0.8966 |          nan      |    nan      |
| missing20       | HSC-CQR recency (capped) |  0.0055 |           0.005  |      0.2009 |   0.5831 |        0.757  |      0.0241 |          0.8964 |            0.002  |      0.5    |
| missing20       | QShrink-CQR recency      |  0.0022 |           0.0038 |      0.1943 |   0.5836 |        0.7809 |      0.0187 |          0.8973 |           -0.0015 |      1      |
| missing20       | Self-CQR recency         |  0.0209 |           0.0082 |      0.3798 |   0.5897 |        0.8055 |      0.0165 |          0.8951 |            0.0151 |      0.0001 |
| missing20       | HSC-SSC-CQR              |  0.0099 |           0.0033 |      0.1745 |   0.5858 |        0.8421 |      0.022  |          0.897  |            0.0043 |      0.1094 |
| missing20       | HSC-CQR simple (cov)     |  0.0143 |           0.0115 |      0.2064 |   0.5824 |        0.7619 |      0.0274 |          0.8946 |            0.0079 |      0.002  |
| missing20       | QShrink-CQR (cov)        |  0.011  |           0.0068 |      0.1888 |   0.5841 |        0.7742 |      0.0241 |          0.8951 |            0.0064 |      0.0156 |
| missing20       | ACI-CQR (cov)            |  0.0659 |           0.0203 |      0.2481 |   0.5824 |        0.7642 |      0.0384 |          0.8962 |            0.0585 |      0      |
| missing20       | HSC-CQR fixed-κ          |  0.0154 |           0.0137 |      0.2294 |   0.5817 |        0.7579 |      0.0296 |          0.8952 |            0.0087 |      0.001  |
| missing20       | Self-CQR                 |  0.0724 |           0.0234 |      0.3875 |   0.5893 |        0.8072 |      0.0252 |          0.8928 |            0.0731 |      0      |
| missing20       | ACI-CQR                  |  0.0834 |           0.0317 |      0.2492 |   0.5822 |        0.7644 |      0.0428 |          0.8958 |            0.0782 |      0      |
| missing20       | TQA-B-CQR                |  0.1449 |           0.0197 |      0.258  |   0.5828 |        0.7618 |      0.0593 |          0.8972 |            0.1401 |      0      |
| missing20       | GHCP-CQR                 |  0.1372 |           0.0217 |      0.2536 |   0.5828 |        0.765  |      0.0648 |          0.8997 |            0.1337 |      0      |
| missing20       | HSC-CQR recency κ=∞      |  0.146  |           0.0152 |      0.2667 |   0.5831 |        0.765  |      0.0681 |          0.898  |            0.1452 |      0      |
| missing20       | CQR                      |  0.1504 |           0.0165 |      0.2547 |   0.5824 |        0.765  |      0.0681 |          0.8966 |            0.1498 |      0      |
| missing40       | HSC-CQR recency          |  0.0077 |           0.005  |      0.2151 |   0.6221 |        0.8112 |      0.0198 |          0.8993 |          nan      |    nan      |
| missing40       | HSC-CQR recency (capped) |  0.0121 |           0.0037 |      0.2173 |   0.6221 |        0.7953 |      0.0198 |          0.8989 |            0.0043 |      0.125  |
| missing40       | QShrink-CQR recency      |  0.0055 |           0.0068 |      0.2141 |   0.6235 |        0.8226 |      0.0143 |          0.8997 |           -0.0015 |      0.625  |
| missing40       | Self-CQR recency         |  0.0285 |           0.0267 |      0.4083 |   0.6319 |        0.8539 |      0.0154 |          0.8965 |            0.0207 |      0.0001 |
| missing40       | HSC-SSC-CQR              |  0.0132 |           0.0118 |      0.1998 |   0.6231 |        0.8137 |      0.0231 |          0.8997 |            0.0051 |      0.1797 |
| missing40       | HSC-CQR simple (cov)     |  0.0252 |           0.0186 |      0.2514 |   0.6214 |        0.7997 |      0.0252 |          0.8967 |            0.0164 |      0      |
| missing40       | QShrink-CQR (cov)        |  0.0165 |           0.0118 |      0.2239 |   0.6227 |        0.8151 |      0.0231 |          0.8969 |            0.0082 |      0.0215 |
| missing40       | ACI-CQR (cov)            |  0.0878 |           0.0191 |      0.2711 |   0.6232 |        0.8085 |      0.0494 |          0.8995 |            0.0767 |      0      |
| missing40       | HSC-CQR fixed-κ          |  0.0285 |           0.0154 |      0.2634 |   0.6216 |        0.7969 |      0.0285 |          0.8975 |            0.0184 |      0      |
| missing40       | Self-CQR                 |  0.0834 |           0.0302 |      0.4182 |   0.6323 |        0.8555 |      0.0274 |          0.8934 |            0.0833 |      0      |
| missing40       | ACI-CQR                  |  0.0977 |           0.0299 |      0.2711 |   0.6238 |        0.8093 |      0.0538 |          0.8992 |            0.089  |      0      |
| missing40       | TQA-B-CQR                |  0.1504 |           0.0284 |      0.2843 |   0.6214 |        0.8007 |      0.0582 |          0.9002 |            0.1431 |      0      |
| missing40       | GHCP-CQR                 |  0.1394 |           0.0209 |      0.2722 |   0.6247 |        0.8067 |      0.0593 |          0.9034 |            0.1347 |      0      |
| missing40       | HSC-CQR recency κ=∞      |  0.1504 |           0.0159 |      0.2876 |   0.6256 |        0.8067 |      0.0637 |          0.9014 |            0.1444 |      0      |
| missing40       | CQR                      |  0.1526 |           0.0207 |      0.2744 |   0.625  |        0.8067 |      0.0626 |          0.8999 |            0.1472 |      0      |
| noise15         | HSC-CQR recency          |  0      |           0      |      0.1153 |   0.9176 |        1.1023 |      0.0066 |          0.8969 |          nan      |    nan      |
| noise15         | HSC-CQR recency (capped) |  0.0033 |           0.0033 |      0.1207 |   0.9176 |        1.0866 |      0.0066 |          0.8967 |            0.0026 |      0.25   |
| noise15         | QShrink-CQR recency      |  0      |           0      |      0.1131 |   0.9184 |        1.1058 |      0.0044 |          0.8983 |           -0      |      1      |
| noise15         | Self-CQR recency         |  0      |           0      |      0.0988 |   0.9221 |        1.1224 |      0.0011 |          0.9013 |           -0      |      1      |
| noise15         | HSC-SSC-CQR              |  0.0011 |           0.0019 |      0.1229 |   0.9177 |        1.221  |      0.0033 |          0.8997 |            0.0005 |      1      |
| noise15         | HSC-CQR simple (cov)     |  0.0044 |           0.005  |      0.2272 |   0.9169 |        1.092  |      0.0088 |          0.8973 |            0.0036 |      0.125  |
| noise15         | QShrink-CQR (cov)        |  0.0011 |           0.0019 |      0.1712 |   0.9174 |        1.0998 |      0.0055 |          0.8989 |            0.0005 |      1      |
| noise15         | ACI-CQR (cov)            |  0.0571 |           0.0048 |      0.3699 |   0.9187 |        1.1115 |      0.0439 |          0.8829 |            0.0557 |      0      |
| noise15         | HSC-CQR fixed-κ          |  0.0066 |           0.0033 |      0.281  |   0.9165 |        1.0879 |      0.0132 |          0.8957 |            0.0056 |      0.0312 |
| noise15         | Self-CQR                 |  0.0011 |           0.0019 |      0.1065 |   0.9237 |        1.1227 |      0.0033 |          0.9022 |            0.0005 |      1      |
| noise15         | ACI-CQR                  |  0.0988 |           0.0717 |      0.3721 |   0.9208 |        1.1115 |      0.0494 |          0.8791 |            0.0989 |      0      |
| noise15         | TQA-B-CQR                |  0.3699 |           0.0763 |      0.4292 |   0.9299 |        1.1038 |      0.1273 |          0.8537 |            0.3722 |      0      |
| noise15         | GHCP-CQR                 |  0.2788 |           0.051  |      0.393  |   0.9253 |        1.1021 |      0.1076 |          0.8593 |            0.2799 |      0      |
| noise15         | HSC-CQR recency κ=∞      |  0.2997 |           0.0554 |      0.4182 |   0.9266 |        1.1031 |      0.1142 |          0.8585 |            0.3004 |      0      |
| noise15         | CQR                      |  0.2953 |           0.0581 |      0.3875 |   0.9261 |        1.1031 |      0.1142 |          0.8575 |            0.2945 |      0      |
| noise5          | HSC-CQR recency          |  0      |           0      |      0.1229 |   0.6116 |        0.804  |      0.0143 |          0.897  |          nan      |    nan      |
| noise5          | HSC-CQR recency (capped) |  0.0033 |           0.0033 |      0.1262 |   0.6116 |        0.7835 |      0.0143 |          0.8968 |            0.0026 |      0.25   |
| noise5          | QShrink-CQR recency      |  0      |           0      |      0.135  |   0.6118 |        0.8091 |      0.011  |          0.8973 |           -0      |      1      |
| noise5          | Self-CQR recency         |  0      |           0      |      0.2184 |   0.6151 |        0.8295 |      0.0099 |          0.8982 |           -0      |      1      |
| noise5          | HSC-SSC-CQR              |  0.0022 |           0.0019 |      0.1186 |   0.6079 |        1.0665 |      0.0143 |          0.8959 |            0.0031 |      0.5    |
| noise5          | HSC-CQR simple (cov)     |  0.0055 |           0.0068 |      0.1614 |   0.6058 |        0.7894 |      0.022  |          0.8957 |            0.0059 |      0.0625 |
| noise5          | QShrink-CQR (cov)        |  0.0055 |           0.0068 |      0.1438 |   0.6081 |        0.8018 |      0.0154 |          0.8959 |            0.0059 |      0.0625 |
| noise5          | ACI-CQR (cov)            |  0.0406 |           0.0124 |      0.213  |   0.6049 |        0.8038 |      0.0439 |          0.8908 |            0.0383 |      0      |
| noise5          | HSC-CQR fixed-κ          |  0.0055 |           0.0068 |      0.1789 |   0.6048 |        0.7843 |      0.0252 |          0.8951 |            0.0059 |      0.0625 |
| noise5          | Self-CQR                 |  0.0165 |           0.0065 |      0.2338 |   0.6171 |        0.8303 |      0.011  |          0.8969 |            0.0161 |      0.0001 |
| noise5          | ACI-CQR                  |  0.0549 |           0.0317 |      0.2173 |   0.6049 |        0.8035 |      0.0505 |          0.8888 |            0.056  |      0      |
| noise5          | TQA-B-CQR                |  0.1745 |           0.0034 |      0.2272 |   0.608  |        0.7863 |      0.0823 |          0.8767 |            0.1764 |      0      |
| noise5          | GHCP-CQR                 |  0.1559 |           0.0013 |      0.225  |   0.6056 |        0.788  |      0.0757 |          0.8814 |            0.1562 |      0      |
| noise5          | HSC-CQR recency κ=∞      |  0.1647 |           0.0034 |      0.2459 |   0.6065 |        0.7884 |      0.0768 |          0.8802 |            0.1662 |      0      |
| noise5          | CQR                      |  0.1679 |           0.0006 |      0.225  |   0.6067 |        0.7885 |      0.079  |          0.8788 |            0.1679 |      0      |
| outage1-3d      | HSC-CQR recency          |  0.0055 |           0.005  |      0.1866 |   0.5725 |        0.7592 |      0.022  |          0.8946 |          nan      |    nan      |
| outage1-3d      | HSC-CQR recency (capped) |  0.0077 |           0.0069 |      0.1877 |   0.5725 |        0.7388 |      0.0241 |          0.8943 |            0.002  |      0.5    |
| outage1-3d      | QShrink-CQR recency      |  0.0044 |           0.0019 |      0.225  |   0.5712 |        0.7644 |      0.0187 |          0.8956 |           -0.0008 |      1      |
| outage1-3d      | Self-CQR recency         |  0.0285 |           0.0019 |      0.3776 |   0.5795 |        0.7872 |      0.0176 |          0.8943 |            0.0248 |      0      |
| outage1-3d      | HSC-SSC-CQR              |  0.0143 |           0.0019 |      0.1789 |   0.5737 |        0.9605 |      0.0241 |          0.8951 |            0.0072 |      0.0386 |
| outage1-3d      | HSC-CQR simple (cov)     |  0.0263 |           0.0034 |      0.1987 |   0.572  |        0.7451 |      0.0263 |          0.8935 |            0.0204 |      0      |
| outage1-3d      | QShrink-CQR (cov)        |  0.022  |           0.0019 |      0.191  |   0.5719 |        0.757  |      0.0252 |          0.8941 |            0.0158 |      0.0003 |
| outage1-3d      | ACI-CQR (cov)            |  0.0648 |           0.0116 |      0.2239 |   0.5668 |        0.7483 |      0.0483 |          0.8928 |            0.057  |      0      |
| outage1-3d      | HSC-CQR fixed-κ          |  0.0241 |           0.002  |      0.213  |   0.5718 |        0.7393 |      0.0318 |          0.8935 |            0.0166 |      0      |
| outage1-3d      | Self-CQR                 |  0.0746 |           0.0113 |      0.3864 |   0.5797 |        0.7878 |      0.0285 |          0.8929 |            0.0782 |      0      |
| outage1-3d      | ACI-CQR                  |  0.0801 |           0.0369 |      0.2261 |   0.5656 |        0.7488 |      0.0527 |          0.8918 |            0.0749 |      0      |
| outage1-3d      | TQA-B-CQR                |  0.1658 |           0.0166 |      0.2217 |   0.5679 |        0.7438 |      0.0779 |          0.8928 |            0.1582 |      0      |
| outage1-3d      | GHCP-CQR                 |  0.1658 |           0.0055 |      0.2316 |   0.5657 |        0.7438 |      0.0801 |          0.8925 |            0.16   |      0      |
| outage1-3d      | HSC-CQR recency κ=∞      |  0.1822 |           0.0075 |      0.2437 |   0.5642 |        0.7439 |      0.0845 |          0.8911 |            0.1751 |      0      |
| outage1-3d      | CQR                      |  0.1844 |           0.0072 |      0.2305 |   0.5656 |        0.744  |      0.0823 |          0.8895 |            0.1777 |      0      |
| ramp+40         | HSC-CQR recency          |  0.0077 |           0.0069 |      0.1844 |   0.5693 |        0.7612 |      0.2239 |          0.8928 |          nan      |    nan      |
| ramp+40         | HSC-CQR recency (capped) |  0.0099 |           0.0099 |      0.1888 |   0.5693 |        0.7429 |      0.2239 |          0.8925 |            0.002  |      0.5    |
| ramp+40         | QShrink-CQR recency      |  0.0066 |           0.0057 |      0.1976 |   0.57   |        0.7655 |      0.2195 |          0.8931 |           -0      |      1      |
| ramp+40         | Self-CQR recency         |  0.0373 |           0.0037 |      0.3765 |   0.5757 |        0.784  |      0.2459 |          0.8947 |            0.0314 |      0      |
| ramp+40         | HSC-SSC-CQR              |  0.0307 |           0.0068 |      0.1658 |   0.5699 |        0.9397 |      0.2711 |          0.8886 |            0.0238 |      0      |
| ramp+40         | HSC-CQR simple (cov)     |  0.0329 |           0.0058 |      0.2009 |   0.5688 |        0.7491 |      0.2755 |          0.8886 |            0.0263 |      0      |
| ramp+40         | QShrink-CQR (cov)        |  0.0209 |           0.0038 |      0.1943 |   0.5689 |        0.7594 |      0.2623 |          0.889  |            0.0141 |      0.0018 |
| ramp+40         | ACI-CQR (cov)            |  0.056  |           0.0087 |      0.2283 |   0.567  |        0.7712 |      0.2799 |          0.8855 |            0.0493 |      0      |
| ramp+40         | HSC-CQR fixed-κ          |  0.0285 |           0.005  |      0.2108 |   0.5683 |        0.7445 |      0.2678 |          0.8879 |            0.0225 |      0      |
| ramp+40         | Self-CQR                 |  0.1087 |           0.0172 |      0.3798 |   0.5747 |        0.785  |      0.3063 |          0.8903 |            0.1051 |      0      |
| ramp+40         | ACI-CQR                  |  0.0845 |           0.0557 |      0.2327 |   0.5663 |        0.7705 |      0.3008 |          0.8822 |            0.078  |      0      |
| ramp+40         | TQA-B-CQR                |  0.2338 |           0.0067 |      0.2217 |   0.5654 |        0.7518 |      0.3106 |          0.8738 |            0.2275 |      0      |
| ramp+40         | GHCP-CQR                 |  0.236  |           0.0142 |      0.2327 |   0.5654 |        0.7505 |      0.3578 |          0.8674 |            0.2249 |      0      |
| ramp+40         | HSC-CQR recency κ=∞      |  0.2656 |           0.0172 |      0.2459 |   0.5652 |        0.751  |      0.382  |          0.8659 |            0.2541 |      0      |
| ramp+40         | CQR                      |  0.2678 |           0.0197 |      0.2349 |   0.565  |        0.7512 |      0.3831 |          0.8639 |            0.2543 |      0      |
| shift+40        | HSC-CQR recency          |  0.0044 |           0.005  |      0.1734 |   0.6642 |        0.85   |      0.0812 |          0.9124 |          nan      |    nan      |
| shift+40        | HSC-CQR recency (capped) |  0.0077 |           0.0038 |      0.1745 |   0.6642 |        0.8316 |      0.0823 |          0.9121 |            0.0028 |      0.25   |
| shift+40        | QShrink-CQR recency      |  0.0044 |           0.005  |      0.1965 |   0.6647 |        0.8546 |      0.0681 |          0.9135 |           -0      |      1      |
| shift+40        | Self-CQR recency         |  0.0187 |           0.005  |      0.3535 |   0.6725 |        0.8736 |      0.0801 |          0.9155 |            0.0151 |      0.0002 |
| shift+40        | HSC-SSC-CQR              |  0.0099 |           0.0057 |      0.1603 |   0.6629 |        1.0347 |      0.1207 |          0.9076 |            0.0054 |      0.125  |
| shift+40        | HSC-CQR simple (cov)     |  0.0231 |           0.0056 |      0.1877 |   0.6614 |        0.8364 |      0.1438 |          0.9045 |            0.0197 |      0      |
| shift+40        | QShrink-CQR (cov)        |  0.0176 |           0.0075 |      0.1756 |   0.6622 |        0.8466 |      0.1229 |          0.9055 |            0.0135 |      0.0005 |
| shift+40        | ACI-CQR (cov)            |  0.0648 |           0.0096 |      0.2141 |   0.6588 |        0.8626 |      0.1712 |          0.9003 |            0.0601 |      0      |
| shift+40        | HSC-CQR fixed-κ          |  0.0231 |           0.0056 |      0.2031 |   0.6594 |        0.8318 |      0.1504 |          0.9036 |            0.0197 |      0      |
| shift+40        | Self-CQR                 |  0.0845 |           0.0092 |      0.3633 |   0.6677 |        0.872  |      0.1745 |          0.9069 |            0.0867 |      0      |
| shift+40        | ACI-CQR                  |  0.0955 |           0.063  |      0.2173 |   0.659  |        0.8595 |      0.1932 |          0.897  |            0.0925 |      0      |
| shift+40        | TQA-B-CQR                |  0.2514 |           0.0128 |      0.213  |   0.6617 |        0.8397 |      0.2975 |          0.8821 |            0.2485 |      0      |
| shift+40        | GHCP-CQR                 |  0.2481 |           0.0215 |      0.2239 |   0.6576 |        0.8384 |      0.2975 |          0.8812 |            0.2439 |      0      |
| shift+40        | HSC-CQR recency κ=∞      |  0.2547 |           0.0224 |      0.236  |   0.6577 |        0.8388 |      0.3085 |          0.8802 |            0.2492 |      0      |
| shift+40        | CQR                      |  0.258  |           0.0209 |      0.2206 |   0.6586 |        0.8392 |      0.3063 |          0.8788 |            0.252  |      0      |
| shift+40@d3-14  | HSC-CQR recency          |  0.0011 |           0.0019 |      0.3941 |   0.6497 |        0.8368 |      0.0384 |          0.9071 |          nan      |    nan      |
| shift+40@d3-14  | HSC-CQR recency (capped) |  0.0033 |           0.0033 |      0.3952 |   0.6497 |        0.8173 |      0.0395 |          0.9068 |            0.002  |      0.5    |
| shift+40@d3-14  | QShrink-CQR recency      |  0.0011 |           0.0019 |      0.4171 |   0.6506 |        0.8431 |      0.0307 |          0.9077 |           -0      |      1      |
| shift+40@d3-14  | Self-CQR recency         |  0.0022 |           0.0019 |      0.5269 |   0.6584 |        0.865  |      0.034  |          0.9077 |           -0.0003 |      1      |
| shift+40@d3-14  | HSC-SSC-CQR              |  0.0011 |           0.0019 |      0.3853 |   0.6504 |        0.9927 |      0.0351 |          0.916  |           -0      |      1      |
| shift+40@d3-14  | HSC-CQR simple (cov)     |  0.0055 |           0.0068 |      0.4215 |   0.6437 |        0.8222 |      0.0472 |          0.9164 |            0.0038 |      0.125  |
| shift+40@d3-14  | QShrink-CQR (cov)        |  0.0044 |           0.005  |      0.4007 |   0.6474 |        0.8351 |      0.0373 |          0.9174 |            0.0031 |      0.25   |
| shift+40@d3-14  | ACI-CQR (cov)            |  0.0494 |           0.0173 |      0.4544 |   0.6373 |        0.8252 |      0.1142 |          0.9062 |            0.0486 |      0      |
| shift+40@d3-14  | HSC-CQR fixed-κ          |  0.0066 |           0.0066 |      0.4358 |   0.6423 |        0.8148 |      0.0483 |          0.9157 |            0.0043 |      0.0625 |
| shift+40@d3-14  | Self-CQR                 |  0.0099 |           0.0057 |      0.5302 |   0.6591 |        0.8657 |      0.0395 |          0.9185 |            0.0089 |      0.0078 |
| shift+40@d3-14  | ACI-CQR                  |  0.0757 |           0.0541 |      0.4577 |   0.6362 |        0.8256 |      0.1405 |          0.9041 |            0.0767 |      0      |
| shift+40@d3-14  | TQA-B-CQR                |  0.2316 |           0.0123 |      0.4501 |   0.6391 |        0.8139 |      0.2437 |          0.8938 |            0.2301 |      0      |
| shift+40@d3-14  | GHCP-CQR                 |  0.2283 |           0.0112 |      0.4588 |   0.6362 |        0.8127 |      0.236  |          0.8946 |            0.2267 |      0      |
| shift+40@d3-14  | HSC-CQR recency κ=∞      |  0.2349 |           0.0138 |      0.4698 |   0.6371 |        0.8132 |      0.2404 |          0.8934 |            0.2339 |      0      |
| shift+40@d3-14  | CQR                      |  0.2338 |           0.0125 |      0.4588 |   0.6369 |        0.8132 |      0.2426 |          0.8917 |            0.2316 |      0      |
| shift-40        | HSC-CQR recency          |  0.0022 |           0.0038 |      0.1734 |   0.7571 |        0.9397 |      0.0044 |          0.9241 |          nan      |    nan      |
| shift-40        | HSC-CQR recency (capped) |  0.0044 |           0.0038 |      0.1745 |   0.7571 |        0.9176 |      0.0044 |          0.9238 |            0.002  |      0.5    |
| shift-40        | QShrink-CQR recency      |  0.0011 |           0.0019 |      0.1965 |   0.7592 |        0.9457 |      0.0033 |          0.9247 |           -0.0015 |      1      |
| shift-40        | Self-CQR recency         |  0.0209 |           0.0082 |      0.3535 |   0.7642 |        0.9691 |      0.0022 |          0.9264 |            0.0169 |      0.0001 |
| shift-40        | HSC-SSC-CQR              |  0.0066 |           0.0033 |      0.1603 |   0.7574 |        1.1363 |      0.0044 |          0.9203 |            0.0054 |      0.2188 |
| shift-40        | HSC-CQR simple (cov)     |  0.0252 |           0.0019 |      0.1877 |   0.7558 |        0.9234 |      0.0055 |          0.9144 |            0.0261 |      0      |
| shift-40        | QShrink-CQR (cov)        |  0.0209 |           0.0049 |      0.1756 |   0.7564 |        0.9363 |      0.0044 |          0.9151 |            0.0217 |      0      |
| shift-40        | ACI-CQR (cov)            |  0.0318 |           0.0132 |      0.2141 |   0.7543 |        0.9408 |      0.0121 |          0.9118 |            0.0279 |      0      |
| shift-40        | HSC-CQR fixed-κ          |  0.0198 |           0.0065 |      0.2031 |   0.7548 |        0.9173 |      0.0066 |          0.9136 |            0.0204 |      0      |
| shift-40        | Self-CQR                 |  0.0944 |           0.0097 |      0.3633 |   0.7674 |        0.9683 |      0.0033 |          0.9165 |            0.0987 |      0      |
| shift-40        | ACI-CQR                  |  0.0582 |           0.0458 |      0.2173 |   0.7551 |        0.9409 |      0.0132 |          0.9082 |            0.0555 |      0      |
| shift-40        | TQA-B-CQR                |  0.1723 |           0.0305 |      0.213  |   0.7612 |        0.9264 |      0.0187 |          0.9027 |            0.1692 |      0      |
| shift-40        | GHCP-CQR                 |  0.1943 |           0.037  |      0.2239 |   0.7536 |        0.9191 |      0.0187 |          0.8925 |            0.1904 |      0      |
| shift-40        | HSC-CQR recency κ=∞      |  0.2162 |           0.0341 |      0.236  |   0.7556 |        0.9197 |      0.022  |          0.891  |            0.2129 |      0      |
| shift-40        | CQR                      |  0.2097 |           0.0301 |      0.2206 |   0.7556 |        0.92   |      0.0187 |          0.8886 |            0.2053 |      0      |
| spikes2         | HSC-CQR recency          |  0.0022 |           0.0019 |      0.1131 |   1.3353 |        1.4758 |      0.0143 |          0.905  |          nan      |    nan      |
| spikes2         | HSC-CQR recency (capped) |  0.0044 |           0.0019 |      0.1142 |   1.3353 |        1.4586 |      0.0143 |          0.9048 |            0.002  |      0.5    |
| spikes2         | QShrink-CQR recency      |  0.0011 |           0.0019 |      0.1251 |   1.3374 |        1.4818 |      0.0088 |          0.9029 |           -0.0008 |      1      |
| spikes2         | Self-CQR recency         |  0.0044 |           0.005  |      0.2711 |   1.3413 |        1.5015 |      0.0088 |          0.8985 |            0.002  |      0.625  |
| spikes2         | HSC-SSC-CQR              |  0.0022 |           0.0019 |      0.0977 |   1.3379 |        1.6254 |      0.0099 |          0.9077 |           -0      |      1      |
| spikes2         | HSC-CQR simple (cov)     |  0.0044 |           0.0038 |      0.1273 |   1.3369 |        1.4645 |      0.0165 |          0.9059 |            0.002  |      0.5    |
| spikes2         | QShrink-CQR (cov)        |  0.0055 |           0.005  |      0.1175 |   1.3377 |        1.4757 |      0.0132 |          0.9035 |            0.0036 |      0.25   |
| spikes2         | ACI-CQR (cov)            |  0.0209 |           0.0051 |      0.1449 |   1.3388 |        1.4719 |      0.0252 |          0.9161 |            0.0166 |      0      |
| spikes2         | HSC-CQR fixed-κ          |  0.0044 |           0.0038 |      0.1361 |   1.3372 |        1.4604 |      0.0165 |          0.9077 |            0.002  |      0.5    |
| spikes2         | Self-CQR                 |  0.0165 |           0.0066 |      0.281  |   1.3417 |        1.5028 |      0.0099 |          0.8991 |            0.0128 |      0.0002 |
| spikes2         | ACI-CQR                  |  0.0285 |           0.0182 |      0.1449 |   1.3389 |        1.4722 |      0.0252 |          0.9168 |            0.0251 |      0      |
| spikes2         | TQA-B-CQR                |  0.0626 |           0.0056 |      0.1471 |   1.3424 |        1.4679 |      0.0296 |          0.9203 |            0.0601 |      0      |
| spikes2         | GHCP-CQR                 |  0.0659 |           0.0054 |      0.1482 |   1.3414 |        1.4692 |      0.0285 |          0.9221 |            0.0624 |      0      |
| spikes2         | HSC-CQR recency κ=∞      |  0.0692 |           0.0031 |      0.1548 |   1.3411 |        1.4688 |      0.0285 |          0.9216 |            0.0654 |      0      |
| spikes2         | CQR                      |  0.0692 |           0.0031 |      0.146  |   1.3415 |        1.4688 |      0.0285 |          0.9209 |            0.0662 |      0      |
| weak-forecaster | HSC-CQR recency          |  0.0044 |           0.0038 |      0.1756 |   0.5888 |        0.7981 |      0.0318 |          0.8993 |          nan      |    nan      |
| weak-forecaster | HSC-CQR recency (capped) |  0.0066 |           0      |      0.1778 |   0.5888 |        0.7756 |      0.034  |          0.8989 |            0.002  |      0.5    |
| weak-forecaster | QShrink-CQR recency      |  0.0055 |           0.0038 |      0.1976 |   0.5926 |        0.8096 |      0.0263 |          0.8994 |            0.0023 |      1      |
| weak-forecaster | Self-CQR recency         |  0.0165 |           0.0087 |      0.3864 |   0.5971 |        0.8261 |      0.0318 |          0.8978 |            0.0112 |      0.0034 |
| weak-forecaster | HSC-SSC-CQR              |  0.0132 |           0      |      0.1603 |   0.5929 |        1.5488 |      0.0285 |          0.9018 |            0.0082 |      0.0215 |
| weak-forecaster | HSC-CQR simple (cov)     |  0.022  |           0.0116 |      0.1866 |   0.5865 |        0.7844 |      0.0461 |          0.8978 |            0.0179 |      0      |
| weak-forecaster | QShrink-CQR (cov)        |  0.022  |           0.0019 |      0.1756 |   0.5897 |        0.8037 |      0.0384 |          0.8981 |            0.0194 |      0.0001 |
| weak-forecaster | ACI-CQR (cov)            |  0.0527 |           0.0132 |      0.2151 |   0.5859 |        0.7964 |      0.0593 |          0.9005 |            0.0478 |      0      |
| weak-forecaster | HSC-CQR fixed-κ          |  0.0241 |           0.0101 |      0.1976 |   0.5857 |        0.7783 |      0.045  |          0.8985 |            0.0202 |      0      |
| weak-forecaster | Self-CQR                 |  0.0714 |           0.0103 |      0.3963 |   0.597  |        0.828  |      0.045  |          0.8965 |            0.0688 |      0      |
| weak-forecaster | ACI-CQR                  |  0.0724 |           0.0463 |      0.2151 |   0.5859 |        0.7963 |      0.0779 |          0.8995 |            0.068  |      0      |
| weak-forecaster | TQA-B-CQR                |  0.1866 |           0.016  |      0.2206 |   0.5873 |        0.791  |      0.1087 |          0.9012 |            0.1802 |      0      |
| weak-forecaster | GHCP-CQR                 |  0.1921 |           0.0133 |      0.2349 |   0.5913 |        0.7983 |      0.1142 |          0.9    |            0.1856 |      0      |
| weak-forecaster | HSC-CQR recency κ=∞      |  0.202  |           0.0179 |      0.2371 |   0.5906 |        0.7984 |      0.1175 |          0.8987 |            0.1961 |      0      |
| weak-forecaster | CQR                      |  0.202  |           0.0154 |      0.2173 |   0.5902 |        0.7985 |      0.1196 |          0.8959 |            0.195  |      0      |


**Table S21. Share of buildings more than 2, 3, 5 and 10 points below the 90 % target.**

| dataset   | method                   |   under_2pt |   under_3pt |   under_5pt |   under_10pt |
|:----------|:-------------------------|------------:|------------:|------------:|-------------:|
| BDG2      | HSC-CQR recency          |      0.1063 |      0.0358 |      0.0012 |       0      |
| BDG2      | HSC-CQR recency (capped) |      0.1099 |      0.0406 |      0.0036 |       0      |
| BDG2      | QShrink-CQR recency      |      0.1087 |      0.0406 |      0.0048 |       0      |
| BDG2      | Self-CQR recency         |      0.2019 |      0.0836 |      0.0108 |       0      |
| BDG2      | HSC-SSC-CQR              |      0.1147 |      0.0442 |      0.0048 |       0      |
| BDG2      | HSC-CQR simple (cov)     |      0.1565 |      0.0562 |      0.0036 |       0      |
| BDG2      | QShrink-CQR (cov)        |      0.1541 |      0.0693 |      0.0084 |       0      |
| BDG2      | ACI-CQR (cov)            |      0.1995 |      0.1016 |      0.0167 |       0      |
| BDG2      | HSC-CQR fixed-κ          |      0.1505 |      0.0621 |      0.0036 |       0      |
| BDG2      | Self-CQR                 |      0.2915 |      0.1625 |      0.0394 |       0.0012 |
| BDG2      | ACI-CQR                  |      0.2473 |      0.1481 |      0.0418 |       0      |
| BDG2      | TQA-B-CQR                |      0.3214 |      0.2605 |      0.1362 |       0.0143 |
| BDG2      | GHCP-CQR                 |      0.3202 |      0.2425 |      0.135  |       0.0227 |
| BDG2      | HSC-CQR recency κ=∞      |      0.3357 |      0.264  |      0.1446 |       0.0239 |
| BDG2      | CQR                      |      0.3393 |      0.264  |      0.1422 |       0.0239 |
| UCI       | HSC-CQR recency          |      0.0333 |      0.0111 |      0      |       0      |
| UCI       | HSC-CQR recency (capped) |      0.0407 |      0.0185 |      0      |       0      |
| UCI       | QShrink-CQR recency      |      0.037  |      0.0074 |      0      |       0      |
| UCI       | Self-CQR recency         |      0.063  |      0.0185 |      0      |       0      |
| UCI       | HSC-SSC-CQR              |      0.0407 |      0.0222 |      0      |       0      |
| UCI       | HSC-CQR simple (cov)     |      0.0444 |      0.0222 |      0      |       0      |
| UCI       | QShrink-CQR (cov)        |      0.0519 |      0.0222 |      0      |       0      |
| UCI       | ACI-CQR (cov)            |      0.0815 |      0.0519 |      0.0074 |       0      |
| UCI       | HSC-CQR fixed-κ          |      0.0407 |      0.0222 |      0      |       0      |
| UCI       | Self-CQR                 |      0.137  |      0.0444 |      0.0111 |       0      |
| UCI       | ACI-CQR                  |      0.1519 |      0.1    |      0.0444 |       0      |
| UCI       | TQA-B-CQR                |      0.2333 |      0.1741 |      0.0889 |       0.0296 |
| UCI       | GHCP-CQR                 |      0.1778 |      0.1407 |      0.0815 |       0.0185 |
| UCI       | HSC-CQR recency κ=∞      |      0.2185 |      0.1704 |      0.1111 |       0.0333 |
| UCI       | CQR                      |      0.2222 |      0.1741 |      0.1148 |       0.0296 |


**Table S22. Stage-wise coverage (coverage over all target buildings at each onboarding day, mean over five seeds; nominal 0.90). The stage-wise guarantee of SSC-CQR assumes exchangeable calibration and target periods, which does not hold in this protocol.**

| Data | Method | Mean stage-wise coverage | Stages below 0.90 (%) | Lowest stage-wise coverage |
|:--|:--|--:|--:|--:|
| BDG2 | SSC-CQR | 0.886 | 93 | 0.862 |
| BDG2 | HSC-SSC-CQR | 0.886 | 100 | 0.866 |
| BDG2 | HSC-CQR recency | 0.884 | 100 | 0.860 |
| BDG2 | CQR | 0.882 | 100 | 0.861 |
| UCI | SSC-CQR | 0.915 | 2 | 0.899 |
| UCI | HSC-SSC-CQR | 0.903 | 34 | 0.893 |
| UCI | HSC-CQR recency | 0.901 | 48 | 0.889 |
| UCI | CQR | 0.901 | 48 | 0.881 |

**Table S23. TTSC: paired per-building comparisons (difference TTSC minus baseline in shares; 95 % site-cluster (BDG2) or building (UCI) bootstrap CI; Wilcoxon signed-rank; Holm over the declared family; 'seeds 2–4' = held-out runs).**

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


**Table S24. TTSC and comparators, main protocol (90 %), all metrics, all and held-out seeds.**

| dataset          | method                      | n   | under   | wk1   | wk_late   | any85   | any80   | any_m10   | breach_wk   | breach_any   | rel_IS_median   | rel_IS_mean   | rel_width_median   | cost10   | cost20   | cost40   | cost20_worst10   | ref_win   | ref_week   | ref_any   | cost10_vs_cqr   | cost20_vs_cqr   | cost40_vs_cqr   | cost20_worst10_vs_cqr   | rel_IS_median_vs_cqr   | rel_IS_mean_vs_cqr   |
|:-----------------|:----------------------------|:----|:--------|:------|:----------|:--------|:--------|:----------|:------------|:-------------|:----------------|:--------------|:-------------------|:---------|:---------|:---------|:-----------------|:----------|:-----------|:----------|:----------------|:----------------|:----------------|:------------------------|:-----------------------|:---------------------|
| BDG2             | TTSC                        | 837 | 0.3     | 11.2  | 13.6      | 69.4    | 20.0    | 20.0      | 14.1        | 64.9         | 0.589           | 0.738         | 0.439              | 1.344    | 1.424    | 1.586    | 2.433            | 1.8       | 17.3       | 72.8      | +0.9            | -0.0            | -1.6            | -1.6                    | +3.6                   | +0.9                 |
| BDG2             | HSC-CQR recency (capped)    | 837 | 0.5     | 14.7  | 19.9      | 83.1    | 43.9    | 43.9      | 15.6        | 67.9         | 0.568           | 0.725         | 0.408              | 1.335    | 1.420    | 1.589    | 2.439            | 1.8       | 17.3       | 72.8      | +0.3            | -0.3            | -1.4            | -1.3                    | +0.1                   | -0.9                 |
| BDG2             | HSC-CQR recency             | 837 | 0.2     | 14.5  | 19.8      | 83.0    | 43.8    | 43.8      | 15.5        | 67.7         | 0.568           | 0.743         | 0.408              | 1.345    | 1.428    | 1.595    | 2.518            | 1.8       | 17.3       | 72.8      | +1.0            | +0.2            | -1.0            | +1.8                    | +0.1                   | +1.5                 |
| BDG2             | QShrink-CQR (cov)           | 837 | 1.4     | 14.3  | 20.9      | 84.0    | 49.7    | 49.7      | 15.6        | 68.1         | 0.568           | 0.748         | 0.405              | 1.347    | 1.430    | 1.596    | 2.533            | 1.8       | 17.3       | 72.8      | +1.2            | +0.4            | -0.9            | +2.4                    | -0.0                   | +2.2                 |
| BDG2             | ACI-CQR (cov)               | 837 | 2.6     | 19.2  | 20.0      | 81.0    | 48.5    | 48.5      | 16.1        | 67.7         | 0.564           | 0.748         | 0.405              | 1.344    | 1.432    | 1.607    | 2.554            | 1.8       | 17.3       | 72.8      | +1.0            | +0.5            | -0.2            | +3.3                    | -0.7                   | +2.3                 |
| BDG2             | CQR                         | 837 | 15.5    | 20.1  | 23.7      | 73.9    | 51.2    | 51.2      | 17.5        | 62.9         | 0.568           | 0.731         | 0.401              | 1.331    | 1.425    | 1.611    | 2.473            | 1.8       | 17.3       | 72.8      | +0.0            | +0.0            | +0.0            | +0.0                    | +0.0                   | +0.0                 |
| BDG2             | ACI (weekly-tuned)          | 837 | 0.4     | 14.4  | 15.8      | 79.9    | 28.2    | 28.2      | 14.5        | 66.7         | 0.581           | 0.733         | 0.423              | 1.341    | 1.423    | 1.589    | 2.440            | 1.8       | 17.3       | 72.8      | +0.7            | -0.1            | -1.4            | -1.3                    | +2.3                   | +0.2                 |
| BDG2             | Windowed ACI (weekly-tuned) | 837 | 2.1     | 14.2  | 14.3      | 62.4    | 21.1    | 21.1      | 14.8        | 62.4         | 0.585           | 0.738         | 0.431              | 1.341    | 1.426    | 1.595    | 2.445            | 1.8       | 17.3       | 72.8      | +0.8            | +0.1            | -1.0            | -1.1                    | +2.9                   | +0.9                 |
| BDG2             | TTSC (cumulative feedback)  | 837 | 0.4     | 11.2  | 15.6      | 77.0    | 25.2    | 25.2      | 14.0        | 66.3         | 0.592           | 0.740         | 0.440              | 1.346    | 1.426    | 1.585    | 2.436            | 1.8       | 17.3       | 72.8      | +1.1            | +0.1            | -1.6            | -1.5                    | +4.2                   | +1.2                 |
| BDG2             | TTSC (uncapped)             | 837 | 0.0     | 10.4  | 13.1      | 68.7    | 17.3    | 17.3      | 13.7        | 64.3         | 0.816           | 2.333         | 0.597              | 2.143    | 2.219    | 2.371    | 8.189            | 1.8       | 17.3       | 72.8      | +61.0           | +55.8           | +47.1           | +231.2                  | +43.7                  | +219.0               |
| BDG2             | TTSC (delay 1d)             | 837 | 0.4     | 17.6  | 18.4      | 82.2    | 38.7    | 38.7      | 15.2        | 69.4         | 0.599           | 0.753         | 0.448              | 1.351    | 1.433    | 1.597    | 2.443            | 1.8       | 17.3       | 72.8      | +1.5            | +0.6            | -0.9            | -1.2                    | +5.5                   | +2.9                 |
| UCI              | TTSC                        | 270 | 0.1     | 7.5   | 6.7       | 41.6    | 4.9     | 4.9       | 9.8         | 54.7         | 0.375           | 0.556         | 0.284              | 1.265    | 1.325    | 1.444    | 2.314            | 0.6       | 12.8       | 60.7      | +0.7            | +0.2            | -0.7            | -0.9                    | +4.0                   | +1.1                 |
| UCI              | HSC-CQR recency (capped)    | 270 | 0.1     | 7.6   | 13.4      | 68.5    | 22.3    | 22.3      | 11.2        | 57.8         | 0.361           | 0.545         | 0.263              | 1.259    | 1.320    | 1.441    | 2.313            | 0.6       | 12.8       | 60.7      | +0.2            | -0.2            | -0.9            | -1.0                    | -0.0                   | -0.9                 |
| UCI              | HSC-CQR recency             | 270 | 0.0     | 7.0   | 13.2      | 68.4    | 22.0    | 22.0      | 11.1        | 57.7         | 0.361           | 0.549         | 0.263              | 1.262    | 1.321    | 1.438    | 2.319            | 0.6       | 12.8       | 60.7      | +0.4            | -0.1            | -1.1            | -0.7                    | -0.0                   | -0.1                 |
| UCI              | QShrink-CQR (cov)           | 270 | 0.1     | 7.3   | 14.6      | 70.1    | 24.2    | 24.2      | 11.2        | 57.4         | 0.362           | 0.548         | 0.260              | 1.261    | 1.320    | 1.438    | 2.319            | 0.6       | 12.8       | 60.7      | +0.4            | -0.2            | -1.1            | -0.7                    | +0.4                   | -0.4                 |
| UCI              | ACI-CQR (cov)               | 270 | 1.7     | 14.5  | 12.3      | 64.4    | 21.7    | 21.7      | 11.4        | 57.7         | 0.367           | 0.551         | 0.269              | 1.261    | 1.322    | 1.443    | 2.325            | 0.6       | 12.8       | 60.7      | +0.3            | -0.1            | -0.7            | -0.5                    | +1.8                   | +0.1                 |
| UCI              | CQR                         | 270 | 12.3    | 15.2  | 18.4      | 60.4    | 31.8    | 31.8      | 12.9        | 55.2         | 0.361           | 0.550         | 0.273              | 1.257    | 1.322    | 1.454    | 2.336            | 0.6       | 12.8       | 60.7      | +0.0            | +0.0            | +0.0            | +0.0                    | +0.0                   | +0.0                 |
| UCI              | ACI (weekly-tuned)          | 270 | 0.1     | 6.4   | 8.1       | 46.4    | 8.2     | 8.2       | 10.6        | 55.4         | 0.374           | 0.554         | 0.272              | 1.263    | 1.324    | 1.445    | 2.317            | 0.6       | 12.8       | 60.7      | +0.5            | +0.1            | -0.6            | -0.8                    | +3.5                   | +0.7                 |
| UCI              | Windowed ACI (weekly-tuned) | 270 | 2.3     | 6.8   | 7.7       | 39.1    | 7.4     | 7.4       | 10.3        | 50.5         | 0.373           | 0.554         | 0.279              | 1.263    | 1.325    | 1.447    | 2.322            | 0.6       | 12.8       | 60.7      | +0.5            | +0.2            | -0.4            | -0.6                    | +3.4                   | +0.8                 |
| UCI              | TTSC (cumulative feedback)  | 270 | 0.1     | 7.5   | 9.8       | 55.4    | 8.4     | 8.4       | 10.2        | 57.6         | 0.374           | 0.556         | 0.280              | 1.265    | 1.324    | 1.443    | 2.314            | 0.6       | 12.8       | 60.7      | +0.6            | +0.1            | -0.7            | -0.9                    | +3.7                   | +1.0                 |
| UCI              | TTSC (uncapped)             | 270 | 0.0     | 6.5   | 6.1       | 39.4    | 2.6     | 2.6       | 9.4         | 54.6         | 0.505           | 1.638         | 0.392              | 1.807    | 1.861    | 1.967    | 5.187            | 0.6       | 12.8       | 60.7      | +43.8           | +40.7           | +35.3           | +122.1                  | +40.0                  | +197.8               |
| UCI              | TTSC (delay 1d)             | 270 | 0.1     | 11.6  | 12.8      | 65.4    | 15.7    | 15.7      | 10.5        | 53.6         | 0.390           | 0.572         | 0.299              | 1.272    | 1.331    | 1.451    | 2.312            | 0.6       | 12.8       | 60.7      | +1.2            | +0.7            | -0.2            | -1.0                    | +8.1                   | +3.9                 |
| BDG2 (seeds 2–4) | TTSC                        | 651 | 0.5     | 10.6  | 14.0      | 68.7    | 21.1    | 21.1      | 13.8        | 63.4         | 0.588           | 0.739         | 0.433              | 1.343    | 1.423    | 1.583    | 2.425            | 1.9       | 17.5       | 73.3      | +0.9            | -0.0            | -1.6            | -1.7                    | +3.7                   | +0.5                 |
| BDG2 (seeds 2–4) | HSC-CQR recency (capped)    | 651 | 0.7     | 16.1  | 20.3      | 83.6    | 45.1    | 45.1      | 15.6        | 67.4         | 0.571           | 0.727         | 0.406              | 1.335    | 1.419    | 1.587    | 2.436            | 1.9       | 17.5       | 73.3      | +0.3            | -0.3            | -1.3            | -1.3                    | +0.6                   | -1.2                 |
| BDG2 (seeds 2–4) | HSC-CQR recency             | 651 | 0.4     | 15.7  | 20.2      | 83.4    | 45.1    | 45.1      | 15.5        | 67.3         | 0.571           | 0.748         | 0.406              | 1.346    | 1.430    | 1.597    | 2.541            | 1.9       | 17.5       | 73.3      | +1.1            | +0.5            | -0.7            | +3.0                    | +0.6                   | +1.7                 |
| BDG2 (seeds 2–4) | QShrink-CQR (cov)           | 651 | 1.9     | 14.9  | 21.5      | 84.0    | 50.4    | 50.4      | 15.6        | 68.0         | 0.570           | 0.761         | 0.403              | 1.352    | 1.436    | 1.603    | 2.596            | 1.9       | 17.5       | 73.3      | +1.6            | +0.9            | -0.3            | +5.2                    | +0.4                   | +3.5                 |
| BDG2 (seeds 2–4) | ACI-CQR (cov)               | 651 | 2.2     | 19.9  | 19.4      | 80.0    | 46.6    | 46.6      | 15.7        | 66.6         | 0.565           | 0.758         | 0.400              | 1.347    | 1.433    | 1.605    | 2.567            | 1.9       | 17.5       | 73.3      | +1.2            | +0.7            | -0.2            | +4.0                    | -0.4                   | +3.0                 |
| BDG2 (seeds 2–4) | CQR                         | 651 | 15.5    | 21.4  | 23.6      | 73.3    | 49.3    | 49.3      | 17.3        | 62.0         | 0.567           | 0.736         | 0.398              | 1.331    | 1.423    | 1.608    | 2.467            | 1.9       | 17.5       | 73.3      | +0.0            | +0.0            | +0.0            | +0.0                    | +0.0                   | +0.0                 |
| BDG2 (seeds 2–4) | ACI (weekly-tuned)          | 651 | 0.5     | 14.7  | 15.8      | 79.3    | 28.2    | 28.2      | 14.0        | 64.7         | 0.582           | 0.735         | 0.423              | 1.340    | 1.422    | 1.585    | 2.434            | 1.9       | 17.5       | 73.3      | +0.7            | -0.1            | -1.4            | -1.3                    | +2.5                   | -0.1                 |
| BDG2 (seeds 2–4) | Windowed ACI (weekly-tuned) | 651 | 2.2     | 13.5  | 13.9      | 60.4    | 19.5    | 19.5      | 14.3        | 61.4         | 0.591           | 0.745         | 0.432              | 1.343    | 1.426    | 1.592    | 2.439            | 1.9       | 17.5       | 73.3      | +0.9            | +0.2            | -1.0            | -1.1                    | +4.2                   | +1.2                 |
| BDG2 (seeds 2–4) | TTSC (cumulative feedback)  | 651 | 0.6     | 10.6  | 16.0      | 77.3    | 26.3    | 26.3      | 13.6        | 64.2         | 0.594           | 0.742         | 0.433              | 1.345    | 1.424    | 1.582    | 2.429            | 1.9       | 17.5       | 73.3      | +1.1            | +0.1            | -1.6            | -1.5                    | +4.7                   | +0.9                 |
| BDG2 (seeds 2–4) | TTSC (uncapped)             | 651 | 0.0     | 9.9   | 13.4      | 68.2    | 18.3    | 18.3      | 13.5        | 63.1         | 0.796           | 3.159         | 0.570              | 2.555    | 2.632    | 2.785    | 11.417           | 1.9       | 17.5       | 73.3      | +92.0           | +84.9           | +73.2           | +362.8                  | +40.2                  | +329.4               |
| BDG2 (seeds 2–4) | TTSC (delay 1d)             | 651 | 0.6     | 17.1  | 18.5      | 81.6    | 40.0    | 40.0      | 14.8        | 66.7         | 0.609           | 0.753         | 0.443              | 1.350    | 1.431    | 1.594    | 2.437            | 1.9       | 17.5       | 73.3      | +1.4            | +0.6            | -0.9            | -1.2                    | +7.3                   | +2.4                 |
| UCI (seeds 2–4)  | TTSC                        | 214 | 0.5     | 7.9   | 7.1       | 41.8    | 5.4     | 5.4       | 10.0        | 55.9         | 0.371           | 0.573         | 0.275              | 1.272    | 1.340    | 1.474    | 2.459            | 0.6       | 13.0       | 61.2      | +0.5            | -0.1            | -1.1            | -1.5                    | +3.3                   | +0.1                 |
| UCI (seeds 2–4)  | HSC-CQR recency (capped)    | 214 | 0.5     | 8.2   | 13.8      | 69.2    | 23.5    | 23.5      | 11.7        | 58.6         | 0.366           | 0.565         | 0.264              | 1.268    | 1.336    | 1.473    | 2.458            | 0.6       | 13.0       | 61.2      | +0.2            | -0.3            | -1.2            | -1.5                    | +1.7                   | -1.4                 |
| UCI (seeds 2–4)  | HSC-CQR recency             | 214 | 0.0     | 7.9   | 13.5      | 68.9    | 23.1    | 23.1      | 11.5        | 58.3         | 0.366           | 0.570         | 0.266              | 1.271    | 1.335    | 1.465    | 2.450            | 0.6       | 13.0       | 61.2      | +0.4            | -0.4            | -1.7            | -1.9                    | +1.7                   | -0.5                 |
| UCI (seeds 2–4)  | QShrink-CQR (cov)           | 214 | 0.5     | 9.3   | 15.1      | 71.3    | 27.0    | 27.0      | 11.9        | 58.3         | 0.365           | 0.569         | 0.259              | 1.270    | 1.335    | 1.466    | 2.447            | 0.6       | 13.0       | 61.2      | +0.3            | -0.4            | -1.7            | -2.0                    | +1.6                   | -0.8                 |
| UCI (seeds 2–4)  | ACI-CQR (cov)               | 214 | 1.6     | 15.3  | 12.9      | 66.0    | 21.0    | 21.0      | 12.0        | 60.0         | 0.363           | 0.576         | 0.267              | 1.272    | 1.340    | 1.476    | 2.485            | 0.6       | 13.0       | 61.2      | +0.5            | -0.1            | -1.0            | -0.5                    | +1.0                   | +0.6                 |
| UCI (seeds 2–4)  | CQR                         | 214 | 13.9    | 16.3  | 20.5      | 62.9    | 34.7    | 34.7      | 13.6        | 57.4         | 0.359           | 0.573         | 0.271              | 1.266    | 1.341    | 1.491    | 2.497            | 0.6       | 13.0       | 61.2      | +0.0            | +0.0            | +0.0            | +0.0                    | +0.0                   | +0.0                 |
| UCI (seeds 2–4)  | ACI (weekly-tuned)          | 214 | 0.5     | 9.0   | 8.9       | 50.4    | 10.0    | 10.0      | 11.0        | 57.5         | 0.365           | 0.572         | 0.271              | 1.271    | 1.339    | 1.476    | 2.460            | 0.6       | 13.0       | 61.2      | +0.4            | -0.1            | -1.0            | -1.5                    | +1.7                   | -0.1                 |
| UCI (seeds 2–4)  | Windowed ACI (weekly-tuned) | 214 | 2.6     | 8.6   | 8.8       | 43.0    | 7.9     | 7.9       | 11.0        | 52.9         | 0.368           | 0.573         | 0.276              | 1.270    | 1.340    | 1.480    | 2.470            | 0.6       | 13.0       | 61.2      | +0.4            | -0.0            | -0.7            | -1.1                    | +2.3                   | -0.1                 |
| UCI (seeds 2–4)  | TTSC (cumulative feedback)  | 214 | 0.5     | 7.9   | 10.2      | 55.8    | 8.9     | 8.9       | 10.4        | 59.1         | 0.369           | 0.574         | 0.272              | 1.272    | 1.339    | 1.473    | 2.458            | 0.6       | 13.0       | 61.2      | +0.5            | -0.1            | -1.2            | -1.5                    | +2.7                   | +0.1                 |
| UCI (seeds 2–4)  | TTSC (uncapped)             | 214 | 0.0     | 7.2   | 6.1       | 39.6    | 2.6     | 2.6       | 9.5         | 55.9         | 0.450           | 1.147         | 0.338              | 1.561    | 1.619    | 1.736    | 4.353            | 0.6       | 13.0       | 61.2      | +23.3           | +20.8           | +16.5           | +74.4                   | +25.3                  | +100.2               |
| UCI (seeds 2–4)  | TTSC (delay 1d)             | 214 | 0.5     | 10.9  | 12.9      | 65.3    | 16.5    | 16.5      | 10.4        | 54.2         | 0.381           | 0.584         | 0.291              | 1.277    | 1.344    | 1.479    | 2.456            | 0.6       | 13.0       | 61.2      | +0.9            | +0.2            | -0.8            | -1.6                    | +6.0                   | +1.9                 |


**Table S25. TTSC and comparators under all other protocols, stress tests and nominal levels.**

| condition              | dataset   | method                      | n   | under   | wk1   | wk_late   | any85   | any80   | any_m10   | breach_wk   | breach_any   | rel_IS_median   | rel_IS_mean   | rel_width_median   | cost10   | cost20   | cost40   | cost20_worst10   | ref_win   | ref_week   | ref_any   | cost10_vs_cqr   | cost20_vs_cqr   | cost40_vs_cqr   | cost20_worst10_vs_cqr   | rel_IS_median_vs_cqr   | rel_IS_mean_vs_cqr   |
|:-----------------------|:----------|:----------------------------|:----|:--------|:------|:----------|:--------|:--------|:----------|:------------|:-------------|:----------------|:--------------|:-------------------|:---------|:---------|:---------|:-----------------|:----------|:-----------|:----------|:----------------|:----------------|:----------------|:------------------------|:-----------------------|:---------------------|
| lso:none               | BDG2      | TTSC                        | 996 | 0.4     | 14.4  | 14.0      | 71.3    | 21.2    | 21.2      | 14.4        | 66.7         | 0.625           | 0.774         | 0.447              | 1.362    | 1.448    | 1.619    | 2.530            | 1.8       | 17.9       | 74.3      | +1.0            | -0.1            | -2.0            | -1.6                    | +2.5                   | +0.6                 |
| lso:none               | BDG2      | HSC-CQR recency (capped)    | 996 | 0.7     | 19.7  | 19.7      | 85.5    | 46.2    | 46.2      | 16.1        | 70.8         | 0.609           | 0.761         | 0.418              | 1.354    | 1.444    | 1.623    | 2.533            | 1.8       | 17.9       | 74.3      | +0.4            | -0.4            | -1.8            | -1.5                    | -0.1                   | -1.0                 |
| lso:none               | BDG2      | HSC-CQR recency             | 996 | 0.4     | 19.5  | 19.5      | 85.3    | 45.9    | 45.9      | 15.9        | 70.6         | 0.609           | 0.767         | 0.418              | 1.357    | 1.444    | 1.619    | 2.540            | 1.8       | 17.9       | 74.3      | +0.7            | -0.4            | -2.0            | -1.3                    | -0.1                   | -0.3                 |
| lso:none               | BDG2      | QShrink-CQR (cov)           | 996 | 1.8     | 21.7  | 20.7      | 85.1    | 52.0    | 52.0      | 16.3        | 70.1         | 0.610           | 0.768         | 0.413              | 1.357    | 1.445    | 1.620    | 2.541            | 1.8       | 17.9       | 74.3      | +0.7            | -0.3            | -2.0            | -1.2                    | +0.1                   | -0.2                 |
| lso:none               | BDG2      | ACI-CQR (cov)               | 996 | 4.0     | 28.0  | 21.5      | 83.0    | 55.3    | 55.3      | 17.4        | 68.9         | 0.607           | 0.792         | 0.411              | 1.365    | 1.460    | 1.649    | 2.694            | 1.8       | 17.9       | 74.3      | +1.3            | +0.7            | -0.2            | +4.7                    | -0.4                   | +2.9                 |
| lso:none               | BDG2      | CQR                         | 996 | 23.4    | 28.5  | 26.5      | 75.3    | 57.1    | 57.1      | 19.3        | 65.6         | 0.610           | 0.769         | 0.400              | 1.348    | 1.450    | 1.652    | 2.572            | 1.8       | 17.9       | 74.3      | +0.0            | +0.0            | +0.0            | +0.0                    | +0.0                   | +0.0                 |
| lso:none               | BDG2      | ACI (weekly-tuned)          | 996 | 0.6     | 20.8  | 15.4      | 80.4    | 30.2    | 30.2      | 15.2        | 69.9         | 0.621           | 0.769         | 0.436              | 1.359    | 1.447    | 1.623    | 2.534            | 1.8       | 17.9       | 74.3      | +0.8            | -0.2            | -1.8            | -1.5                    | +1.9                   | -0.0                 |
| lso:none               | BDG2      | Windowed ACI (weekly-tuned) | 996 | 2.6     | 18.0  | 15.5      | 66.0    | 23.1    | 23.1      | 15.3        | 64.4         | 0.635           | 0.777         | 0.445              | 1.361    | 1.451    | 1.633    | 2.546            | 1.8       | 17.9       | 74.3      | +0.9            | +0.1            | -1.2            | -1.0                    | +4.2                   | +1.0                 |
| lso:none               | BDG2      | TTSC (cumulative feedback)  | 996 | 0.3     | 14.4  | 15.6      | 76.9    | 26.9    | 26.9      | 14.2        | 68.0         | 0.631           | 0.777         | 0.459              | 1.364    | 1.449    | 1.619    | 2.532            | 1.8       | 17.9       | 74.3      | +1.2            | -0.0            | -2.0            | -1.6                    | +3.5                   | +0.9                 |
| lso:none               | BDG2      | TTSC (uncapped)             | 996 | 0.0     | 13.7  | 13.2      | 70.1    | 18.1    | 18.1      | 13.9        | 65.8         | 0.760           | 2.552         | 0.558              | 2.253    | 2.331    | 2.489    | 8.667            | 1.8       | 17.9       | 74.3      | +67.1           | +60.8           | +50.6           | +237.0                  | +24.7                  | +231.8               |
| lso:none               | BDG2      | TTSC (delay 1d)             | 996 | 0.8     | 21.5  | 18.8      | 83.8    | 39.6    | 39.6      | 15.5        | 70.2         | 0.644           | 0.788         | 0.460              | 1.369    | 1.456    | 1.631    | 2.541            | 1.8       | 17.9       | 74.3      | +1.5            | +0.4            | -1.3            | -1.2                    | +5.6                   | +2.5                 |
| main:none:alpha=0.05   | BDG2      | TTSC                        | 837 | 0.4     | 10.3  | 10.6      | 57.9    | 3.0     | 11.1      | 19.7        | 77.8         | 0.740           | 0.972         | 0.563              | 1.394    | 1.452    | 1.569    | 2.444            | 0.5       | 12.6       | 59.3      | +2.4            | +1.1            | -1.1            | -0.2                    | +6.3                   | -0.3                 |
| main:none:alpha=0.05   | BDG2      | HSC-CQR recency (capped)    | 837 | 0.3     | 12.0  | 13.8      | 70.2    | 7.8     | 24.7      | 20.0        | 76.9         | 0.707           | 0.945         | 0.517              | 1.376    | 1.437    | 1.559    | 2.441            | 0.5       | 12.6       | 59.3      | +1.0            | +0.0            | -1.7            | -0.3                    | +1.5                   | -3.1                 |
| main:none:alpha=0.05   | BDG2      | HSC-CQR recency             | 837 | 0.1     | 11.5  | 13.6      | 69.9    | 7.3     | 24.0      | 19.9        | 76.9         | 0.707           | 1.035         | 0.517              | 1.425    | 1.483    | 1.597    | 2.886            | 0.5       | 12.6       | 59.3      | +4.7            | +3.2            | +0.7            | +17.8                   | +1.5                   | +6.1                 |
| main:none:alpha=0.05   | BDG2      | QShrink-CQR (cov)           | 837 | 1.0     | 12.5  | 14.7      | 69.7    | 11.5    | 28.6      | 20.0        | 76.1         | 0.710           | 1.028         | 0.508              | 1.420    | 1.478    | 1.595    | 2.849            | 0.5       | 12.6       | 59.3      | +4.3            | +2.9            | +0.6            | +16.3                   | +2.0                   | +5.4                 |
| main:none:alpha=0.05   | BDG2      | ACI-CQR (cov)               | 837 | 2.4     | 15.2  | 14.3      | 64.4    | 13.8    | 31.0      | 20.4        | 71.2         | 0.698           | 1.005         | 0.498              | 1.395    | 1.461    | 1.592    | 2.706            | 0.5       | 12.6       | 59.3      | +2.5            | +1.7            | +0.4            | +10.5                   | +0.2                   | +3.0                 |
| main:none:alpha=0.05   | BDG2      | CQR                         | 837 | 12.1    | 15.7  | 18.1      | 60.9    | 18.7    | 34.9      | 21.8        | 65.3         | 0.696           | 0.975         | 0.498              | 1.361    | 1.436    | 1.586    | 2.449            | 0.5       | 12.6       | 59.3      | +0.0            | +0.0            | +0.0            | +0.0                    | +0.0                   | +0.0                 |
| main:none:alpha=0.05   | BDG2      | ACI (weekly-tuned)          | 837 | 0.4     | 9.6   | 11.3      | 63.4    | 3.8     | 15.1      | 20.1        | 78.7         | 0.749           | 0.971         | 0.561              | 1.392    | 1.451    | 1.571    | 2.450            | 0.5       | 12.6       | 59.3      | +2.2            | +1.1            | -0.9            | +0.1                    | +7.6                   | -0.5                 |
| main:none:alpha=0.05   | BDG2      | Windowed ACI (weekly-tuned) | 837 | 1.5     | 10.6  | 10.1      | 47.0    | 3.2     | 10.9      | 19.4        | 68.1         | 0.742           | 0.979         | 0.565              | 1.389    | 1.452    | 1.577    | 2.442            | 0.5       | 12.6       | 59.3      | +2.0            | +1.1            | -0.5            | -0.3                    | +6.6                   | +0.3                 |
| main:none:alpha=0.05   | BDG2      | TTSC (cumulative feedback)  | 837 | 0.3     | 10.3  | 12.0      | 67.7    | 3.8     | 13.9      | 20.0        | 80.3         | 0.750           | 0.980         | 0.569              | 1.401    | 1.458    | 1.572    | 2.455            | 0.5       | 12.6       | 59.3      | +2.9            | +1.5            | -0.9            | +0.3                    | +7.7                   | +0.5                 |
| main:none:alpha=0.05   | BDG2      | TTSC (uncapped)             | 837 | 0.0     | 9.1   | 9.9       | 56.1    | 1.4     | 8.1       | 19.1        | 77.1         | 2.286           | 8.028         | 2.040              | 4.931    | 4.982    | 5.083    | 24.017           | 0.5       | 12.6       | 59.3      | +262.2          | +246.9          | +220.6          | +880.7                  | +228.3                 | +723.1               |
| main:none:alpha=0.05   | BDG2      | TTSC (delay 1d)             | 837 | 0.4     | 13.8  | 14.5      | 72.3    | 8.2     | 24.8      | 20.6        | 79.9         | 0.777           | 1.001         | 0.586              | 1.406    | 1.466    | 1.586    | 2.456            | 0.5       | 12.6       | 59.3      | +3.3            | +2.1            | +0.0            | +0.3                    | +11.6                  | +2.6                 |
| main:none:alpha=0.2    | BDG2      | TTSC                        | 837 | 0.2     | 14.6  | 17.6      | 79.0    | 100.0   | 26.5      | 5.5         | 33.4         | 0.476           | 0.580         | 0.350              | 1.325    | 1.435    | 1.654    | 2.479            | 4.1       | 23.1       | 84.4      | +0.3            | +0.0            | -0.4            | -0.7                    | +1.6                   | +1.4                 |
| main:none:alpha=0.2    | BDG2      | HSC-CQR recency (capped)    | 837 | 2.8     | 16.9  | 26.2      | 91.6    | 100.0   | 61.7      | 7.2         | 41.1         | 0.467           | 0.571         | 0.336              | 1.322    | 1.434    | 1.659    | 2.486            | 4.1       | 23.1       | 84.4      | -0.0            | -0.1            | -0.1            | -0.4                    | -0.3                   | -0.1                 |
| main:none:alpha=0.2    | BDG2      | HSC-CQR recency             | 837 | 2.8     | 16.8  | 26.2      | 91.6    | 100.0   | 61.7      | 7.2         | 41.1         | 0.467           | 0.574         | 0.336              | 1.324    | 1.436    | 1.660    | 2.503            | 4.1       | 23.1       | 84.4      | +0.1            | +0.1            | -0.1            | +0.3                    | -0.3                   | +0.4                 |
| main:none:alpha=0.2    | BDG2      | QShrink-CQR (cov)           | 837 | 8.3     | 22.2  | 28.6      | 92.6    | 99.9    | 67.7      | 7.9         | 43.1         | 0.467           | 0.575         | 0.333              | 1.324    | 1.436    | 1.662    | 2.504            | 4.1       | 23.1       | 84.4      | +0.1            | +0.1            | +0.0            | +0.3                    | -0.3                   | +0.6                 |
| main:none:alpha=0.2    | BDG2      | ACI-CQR (cov)               | 837 | 0.4     | 22.2  | 22.0      | 88.8    | 99.8    | 56.1      | 6.6         | 39.2         | 0.473           | 0.583         | 0.343              | 1.328    | 1.439    | 1.661    | 2.521            | 4.1       | 23.1       | 84.4      | +0.4            | +0.3            | +0.0            | +1.0                    | +1.0                   | +2.0                 |
| main:none:alpha=0.2    | BDG2      | CQR                         | 837 | 17.8    | 25.6  | 27.8      | 78.8    | 93.8    | 59.0      | 9.1         | 42.3         | 0.468           | 0.572         | 0.342              | 1.322    | 1.435    | 1.661    | 2.496            | 4.1       | 23.1       | 84.4      | +0.0            | +0.0            | +0.0            | +0.0                    | +0.0                   | +0.0                 |
| main:none:alpha=0.2    | BDG2      | ACI (weekly-tuned)          | 837 | 0.3     | 13.6  | 17.8      | 82.2    | 100.0   | 34.0      | 5.5         | 33.4         | 0.473           | 0.577         | 0.344              | 1.324    | 1.435    | 1.655    | 2.485            | 4.1       | 23.1       | 84.4      | +0.2            | -0.0            | -0.4            | -0.4                    | +1.1                   | +0.9                 |
| main:none:alpha=0.2    | BDG2      | Windowed ACI (weekly-tuned) | 837 | 1.0     | 12.5  | 16.8      | 69.0    | 98.3    | 25.9      | 5.7         | 32.1         | 0.477           | 0.581         | 0.353              | 1.326    | 1.436    | 1.655    | 2.485            | 4.1       | 23.1       | 84.4      | +0.3            | +0.1            | -0.4            | -0.4                    | +2.0                   | +1.6                 |
| main:none:alpha=0.2    | BDG2      | TTSC (cumulative feedback)  | 837 | 0.3     | 14.6  | 19.5      | 85.6    | 100.0   | 35.0      | 5.6         | 34.9         | 0.475           | 0.579         | 0.345              | 1.325    | 1.435    | 1.655    | 2.483            | 4.1       | 23.1       | 84.4      | +0.3            | +0.0            | -0.4            | -0.5                    | +1.5                   | +1.3                 |
| main:none:alpha=0.2    | BDG2      | TTSC (uncapped)             | 837 | 0.0     | 14.0  | 17.2      | 78.5    | 100.0   | 25.0      | 5.3         | 32.3         | 0.609           | 1.970         | 0.435              | 2.020    | 2.127    | 2.341    | 7.760            | 4.1       | 23.1       | 84.4      | +52.8           | +48.2           | +41.0           | +210.9                  | +30.2                  | +244.5               |
| main:none:alpha=0.2    | BDG2      | TTSC (delay 1d)             | 837 | 0.4     | 21.7  | 23.8      | 89.5    | 100.0   | 52.2      | 6.7         | 39.6         | 0.491           | 0.592         | 0.358              | 1.332    | 1.443    | 1.665    | 2.486            | 4.1       | 23.1       | 84.4      | +0.7            | +0.5            | +0.2            | -0.4                    | +4.9                   | +3.6                 |
| main:none:alpha=0.05   | UCI       | TTSC                        | 270 | 0.7     | 8.8   | 5.3       | 33.0    | 0.5     | 4.9       | 17.0        | 74.8         | 0.472           | 0.725         | 0.366              | 1.300    | 1.344    | 1.433    | 2.324            | 0.2       | 8.9        | 45.9      | +1.5            | +0.9            | -0.3            | +0.1                    | +6.9                   | +0.4                 |
| main:none:alpha=0.05   | UCI       | HSC-CQR recency (capped)    | 270 | 0.7     | 7.9   | 8.7       | 50.8    | 1.3     | 8.0       | 16.7        | 75.9         | 0.446           | 0.701         | 0.333              | 1.288    | 1.332    | 1.421    | 2.322            | 0.2       | 8.9        | 45.9      | +0.5            | -0.1            | -1.1            | -0.0                    | +1.0                   | -2.9                 |
| main:none:alpha=0.05   | UCI       | HSC-CQR recency             | 270 | 0.0     | 7.0   | 8.1       | 50.0    | 0.8     | 7.4       | 16.5        | 75.9         | 0.446           | 0.708         | 0.333              | 1.299    | 1.337    | 1.414    | 2.367            | 0.2       | 8.9        | 45.9      | +1.4            | +0.3            | -1.6            | +1.9                    | +1.0                   | -2.0                 |
| main:none:alpha=0.05   | UCI       | QShrink-CQR (cov)           | 270 | 0.0     | 7.9   | 9.4       | 55.2    | 1.9     | 10.2      | 17.2        | 76.5         | 0.443           | 0.704         | 0.323              | 1.296    | 1.335    | 1.413    | 2.358            | 0.2       | 8.9        | 45.9      | +1.2            | +0.2            | -1.7            | +1.5                    | +0.3                   | -2.5                 |
| main:none:alpha=0.05   | UCI       | ACI-CQR (cov)               | 270 | 1.6     | 13.1  | 9.0       | 49.6    | 3.9     | 12.0      | 17.2        | 72.8         | 0.440           | 0.717         | 0.344              | 1.293    | 1.338    | 1.427    | 2.378            | 0.2       | 8.9        | 45.9      | +1.0            | +0.4            | -0.7            | +2.4                    | -0.4                   | -0.7                 |
| main:none:alpha=0.05   | UCI       | CQR                         | 270 | 8.2     | 14.2  | 13.1      | 45.9    | 8.9     | 20.2      | 17.7        | 62.1         | 0.442           | 0.722         | 0.351              | 1.281    | 1.333    | 1.437    | 2.322            | 0.2       | 8.9        | 45.9      | +0.0            | +0.0            | +0.0            | +0.0                    | +0.0                   | +0.0                 |
| main:none:alpha=0.05   | UCI       | ACI (weekly-tuned)          | 270 | 0.7     | 8.3   | 6.3       | 38.5    | 0.7     | 5.9       | 17.8        | 78.3         | 0.466           | 0.721         | 0.360              | 1.297    | 1.342    | 1.433    | 2.333            | 0.2       | 8.9        | 45.9      | +1.3            | +0.7            | -0.3            | +0.5                    | +5.5                   | -0.1                 |
| main:none:alpha=0.05   | UCI       | Windowed ACI (weekly-tuned) | 270 | 1.6     | 9.5   | 5.9       | 29.6    | 1.3     | 6.1       | 16.5        | 68.2         | 0.462           | 0.726         | 0.365              | 1.296    | 1.342    | 1.435    | 2.328            | 0.2       | 8.9        | 45.9      | +1.1            | +0.7            | -0.1            | +0.2                    | +4.6                   | +0.5                 |
| main:none:alpha=0.05   | UCI       | TTSC (cumulative feedback)  | 270 | 0.7     | 8.8   | 7.1       | 42.7    | 0.7     | 6.4       | 18.2        | 79.9         | 0.472           | 0.724         | 0.364              | 1.300    | 1.344    | 1.432    | 2.329            | 0.2       | 8.9        | 45.9      | +1.5            | +0.8            | -0.3            | +0.3                    | +6.8                   | +0.3                 |
| main:none:alpha=0.05   | UCI       | TTSC (uncapped)             | 270 | 0.0     | 7.2   | 4.2       | 29.8    | 0.0     | 2.5       | 16.4        | 74.8         | 0.924           | 3.148         | 0.801              | 2.525    | 2.559    | 2.627    | 8.918            | 0.2       | 8.9        | 45.9      | +97.1           | +92.0           | +82.8           | +284.0                  | +109.1                 | +336.0               |
| main:none:alpha=0.05   | UCI       | TTSC (delay 1d)             | 270 | 0.7     | 11.2  | 8.3       | 49.7    | 1.5     | 9.8       | 18.1        | 77.2         | 0.500           | 0.750         | 0.401              | 1.311    | 1.356    | 1.445    | 2.325            | 0.2       | 8.9        | 45.9      | +2.4            | +1.7            | +0.5            | +0.1                    | +13.1                  | +3.9                 |
| main:none:alpha=0.2    | UCI       | TTSC                        | 270 | 0.1     | 8.8   | 9.9       | 56.6    | 100.0   | 8.2       | 2.8         | 20.7         | 0.304           | 0.438         | 0.213              | 1.250    | 1.332    | 1.497    | 2.344            | 1.7       | 18.4       | 76.1      | +0.2            | +0.1            | -0.0            | -0.5                    | +2.0                   | +0.9                 |
| main:none:alpha=0.2    | UCI       | HSC-CQR recency (capped)    | 270 | 0.8     | 12.8  | 21.1      | 85.9    | 99.7    | 39.1      | 3.8         | 25.1         | 0.298           | 0.432         | 0.209              | 1.247    | 1.330    | 1.496    | 2.343            | 1.7       | 18.4       | 76.1      | +0.0            | -0.0            | -0.1            | -0.5                    | -0.1                   | -0.5                 |
| main:none:alpha=0.2    | UCI       | HSC-CQR recency             | 270 | 0.7     | 12.2  | 21.1      | 85.5    | 99.7    | 38.9      | 3.8         | 25.1         | 0.298           | 0.433         | 0.209              | 1.248    | 1.331    | 1.496    | 2.346            | 1.7       | 18.4       | 76.1      | +0.1            | -0.0            | -0.1            | -0.4                    | -0.1                   | -0.3                 |
| main:none:alpha=0.2    | UCI       | QShrink-CQR (cov)           | 270 | 3.4     | 15.6  | 23.8      | 88.1    | 99.7    | 45.8      | 4.0         | 27.7         | 0.297           | 0.432         | 0.209              | 1.247    | 1.331    | 1.497    | 2.344            | 1.7       | 18.4       | 76.1      | +0.0            | +0.0            | +0.0            | -0.5                    | -0.4                   | -0.5                 |
| main:none:alpha=0.2    | UCI       | ACI-CQR (cov)               | 270 | 0.6     | 14.0  | 15.5      | 75.0    | 98.0    | 25.1      | 3.2         | 21.2         | 0.300           | 0.436         | 0.215              | 1.249    | 1.331    | 1.494    | 2.348            | 1.7       | 18.4       | 76.1      | +0.1            | -0.0            | -0.2            | -0.3                    | +0.7                   | +0.4                 |
| main:none:alpha=0.2    | UCI       | CQR                         | 270 | 14.4    | 19.8  | 22.9      | 71.2    | 90.9    | 45.6      | 4.4         | 24.9         | 0.298           | 0.434         | 0.217              | 1.247    | 1.331    | 1.497    | 2.356            | 1.7       | 18.4       | 76.1      | +0.0            | +0.0            | +0.0            | +0.0                    | +0.0                   | +0.0                 |
| main:none:alpha=0.2    | UCI       | ACI (weekly-tuned)          | 270 | 0.1     | 10.1  | 10.6      | 57.7    | 100.0   | 8.4       | 2.6         | 17.8         | 0.304           | 0.437         | 0.218              | 1.249    | 1.332    | 1.496    | 2.344            | 1.7       | 18.4       | 76.1      | +0.2            | +0.1            | -0.1            | -0.5                    | +1.8                   | +0.6                 |
| main:none:alpha=0.2    | UCI       | Windowed ACI (weekly-tuned) | 270 | 1.9     | 9.0   | 11.8      | 53.8    | 96.8    | 10.3      | 2.9         | 20.4         | 0.302           | 0.436         | 0.215              | 1.249    | 1.331    | 1.495    | 2.346            | 1.7       | 18.4       | 76.1      | +0.1            | +0.0            | -0.2            | -0.4                    | +1.3                   | +0.4                 |
| main:none:alpha=0.2    | UCI       | TTSC (cumulative feedback)  | 270 | 0.0     | 8.8   | 12.0      | 63.8    | 100.0   | 11.0      | 3.0         | 19.5         | 0.301           | 0.437         | 0.212              | 1.249    | 1.332    | 1.496    | 2.344            | 1.7       | 18.4       | 76.1      | +0.2            | +0.1            | -0.1            | -0.5                    | +0.9                   | +0.6                 |
| main:none:alpha=0.2    | UCI       | TTSC (uncapped)             | 270 | 0.0     | 8.3   | 9.6       | 55.8    | 100.0   | 6.8       | 2.7         | 20.4         | 0.327           | 0.537         | 0.235              | 1.298    | 1.378    | 1.536    | 2.570            | 1.7       | 18.4       | 76.1      | +4.1            | +3.5            | +2.6            | +9.1                    | +9.7                   | +23.6                |
| main:none:alpha=0.2    | UCI       | TTSC (delay 1d)             | 270 | 0.1     | 16.5  | 18.6      | 83.6    | 100.0   | 32.1      | 3.3         | 22.4         | 0.318           | 0.448         | 0.229              | 1.254    | 1.336    | 1.500    | 2.343            | 1.7       | 18.4       | 76.1      | +0.5            | +0.4            | +0.2            | -0.5                    | +6.7                   | +3.2                 |
| robust:calpool10       | BDG2      | TTSC                        | 652 | 0.4     | 12.2  | 12.8      | 67.9    | 18.9    | 18.9      | 14.2        | 64.9         | 0.593           | 0.749         | 0.446              | 1.349    | 1.429    | 1.589    | 2.448            | 1.9       | 17.2       | 72.6      | +1.2            | +0.1            | -1.7            | -1.9                    | +4.7                   | +1.8                 |
| robust:calpool10       | BDG2      | HSC-CQR recency (capped)    | 652 | 0.5     | 16.0  | 19.8      | 82.8    | 41.5    | 41.5      | 16.0        | 68.4         | 0.572           | 0.730         | 0.411              | 1.338    | 1.422    | 1.590    | 2.456            | 1.9       | 17.2       | 72.6      | +0.4            | -0.4            | -1.6            | -1.6                    | +0.9                   | -0.8                 |
| robust:calpool10       | BDG2      | HSC-CQR recency             | 652 | 0.3     | 15.5  | 19.6      | 82.5    | 41.3    | 41.3      | 15.8        | 68.1         | 0.572           | 0.760         | 0.411              | 1.353    | 1.434    | 1.598    | 2.577            | 1.9       | 17.2       | 72.6      | +1.5            | +0.5            | -1.1            | +3.3                    | +0.9                   | +3.2                 |
| robust:calpool10       | BDG2      | QShrink-CQR (cov)           | 652 | 1.9     | 16.4  | 20.8      | 84.5    | 48.2    | 48.2      | 15.9        | 68.6         | 0.569           | 0.748         | 0.406              | 1.347    | 1.429    | 1.594    | 2.519            | 1.9       | 17.2       | 72.6      | +1.0            | +0.1            | -1.4            | +0.9                    | +0.4                   | +1.6                 |
| robust:calpool10       | BDG2      | ACI-CQR (cov)               | 652 | 0.6     | 18.0  | 19.6      | 83.2    | 46.0    | 46.0      | 16.3        | 68.9         | 0.568           | 0.790         | 0.409              | 1.365    | 1.453    | 1.628    | 2.752            | 1.9       | 17.2       | 72.6      | +2.4            | +1.8            | +0.8            | +10.3                   | +0.2                   | +7.3                 |
| robust:calpool10       | BDG2      | CQR                         | 652 | 15.0    | 18.1  | 23.4      | 73.5    | 50.4    | 50.4      | 17.3        | 62.3         | 0.567           | 0.736         | 0.405              | 1.333    | 1.427    | 1.616    | 2.496            | 1.9       | 17.2       | 72.6      | +0.0            | +0.0            | +0.0            | +0.0                    | +0.0                   | +0.0                 |
| robust:calpool10       | BDG2      | TTSC (cumulative feedback)  | 652 | 0.4     | 12.2  | 14.3      | 73.0    | 24.4    | 24.4      | 14.3        | 66.6         | 0.597           | 0.750         | 0.453              | 1.350    | 1.429    | 1.589    | 2.453            | 1.9       | 17.2       | 72.6      | +1.3            | +0.2            | -1.7            | -1.7                    | +5.4                   | +1.9                 |
| robust:calpool10       | BDG2      | TTSC (uncapped)             | 652 | 0.0     | 11.4  | 12.1      | 66.8    | 15.5    | 15.5      | 13.6        | 63.2         | 0.905           | 1.721         | 0.680              | 1.836    | 1.909    | 2.053    | 4.937            | 1.9       | 17.2       | 72.6      | +37.8           | +33.8           | +27.1           | +97.8                   | +59.7                  | +133.9               |
| robust:calpool10       | BDG2      | TTSC (delay 1d)             | 652 | 0.6     | 19.3  | 18.8      | 82.9    | 37.7    | 37.7      | 15.4        | 70.9         | 0.618           | 0.775         | 0.469              | 1.361    | 1.442    | 1.606    | 2.467            | 1.9       | 17.2       | 72.6      | +2.1            | +1.1            | -0.6            | -1.1                    | +9.0                   | +5.2                 |
| robust:calpool25       | BDG2      | TTSC                        | 652 | 0.2     | 14.1  | 15.3      | 75.9    | 23.9    | 23.9      | 14.7        | 66.1         | 0.585           | 0.737         | 0.433              | 1.342    | 1.424    | 1.587    | 2.449            | 1.9       | 17.2       | 72.6      | +0.8            | -0.2            | -1.9            | -1.9                    | +3.1                   | +0.2                 |
| robust:calpool25       | BDG2      | HSC-CQR recency (capped)    | 652 | 0.5     | 14.8  | 19.9      | 83.4    | 42.3    | 42.3      | 16.1        | 68.8         | 0.570           | 0.729         | 0.410              | 1.337    | 1.422    | 1.591    | 2.456            | 1.9       | 17.2       | 72.6      | +0.4            | -0.4            | -1.6            | -1.7                    | +0.5                   | -0.9                 |
| robust:calpool25       | BDG2      | HSC-CQR recency             | 652 | 0.3     | 14.5  | 19.7      | 83.4    | 42.3    | 42.3      | 16.0        | 68.6         | 0.570           | 0.750         | 0.410              | 1.348    | 1.431    | 1.596    | 2.543            | 1.9       | 17.2       | 72.6      | +1.2            | +0.3            | -1.3            | +1.8                    | +0.5                   | +2.0                 |
| robust:calpool25       | BDG2      | QShrink-CQR (cov)           | 652 | 1.0     | 16.7  | 20.6      | 84.6    | 48.7    | 48.7      | 16.1        | 68.9         | 0.571           | 0.751         | 0.405              | 1.348    | 1.431    | 1.596    | 2.541            | 1.9       | 17.2       | 72.6      | +1.2            | +0.3            | -1.3            | +1.8                    | +0.7                   | +2.1                 |
| robust:calpool25       | BDG2      | ACI-CQR (cov)               | 652 | 2.8     | 21.3  | 20.0      | 83.1    | 47.1    | 47.1      | 16.7        | 68.2         | 0.568           | 0.758         | 0.407              | 1.348    | 1.437    | 1.616    | 2.608            | 1.9       | 17.2       | 72.6      | +1.2            | +0.7            | -0.1            | +4.4                    | +0.1                   | +3.0                 |
| robust:calpool25       | BDG2      | CQR                         | 652 | 16.3    | 21.8  | 24.2      | 74.4    | 50.3    | 50.3      | 17.8        | 63.6         | 0.567           | 0.736         | 0.399              | 1.332    | 1.427    | 1.617    | 2.497            | 1.9       | 17.2       | 72.6      | +0.0            | +0.0            | +0.0            | +0.0                    | +0.0                   | +0.0                 |
| robust:calpool25       | BDG2      | TTSC (cumulative feedback)  | 652 | 0.4     | 14.1  | 16.5      | 80.1    | 29.7    | 29.7      | 14.9        | 68.7         | 0.588           | 0.741         | 0.436              | 1.345    | 1.426    | 1.587    | 2.454            | 1.9       | 17.2       | 72.6      | +1.0            | -0.1            | -1.9            | -1.7                    | +3.6                   | +0.7                 |
| robust:calpool25       | BDG2      | TTSC (uncapped)             | 652 | 0.0     | 12.8  | 14.9      | 75.3    | 22.8    | 22.8      | 14.4        | 65.7         | 0.626           | 0.909         | 0.471              | 1.430    | 1.506    | 1.659    | 2.910            | 1.9       | 17.2       | 72.6      | +7.3            | +5.5            | +2.6            | +16.5                   | +10.4                  | +23.5                |
| robust:calpool25       | BDG2      | TTSC (delay 1d)             | 652 | 0.4     | 19.1  | 19.1      | 85.0    | 39.2    | 39.2      | 16.2        | 72.4         | 0.591           | 0.748         | 0.441              | 1.347    | 1.430    | 1.596    | 2.460            | 1.9       | 17.2       | 72.6      | +1.2            | +0.2            | -1.3            | -1.5                    | +4.2                   | +1.7                 |
| robust:calpool50       | BDG2      | TTSC                        | 652 | 0.4     | 13.0  | 14.3      | 72.2    | 22.0    | 22.0      | 14.5        | 65.8         | 0.586           | 0.739         | 0.436              | 1.344    | 1.425    | 1.588    | 2.452            | 1.9       | 17.2       | 72.6      | +0.9            | -0.1            | -1.8            | -1.8                    | +3.3                   | +0.6                 |
| robust:calpool50       | BDG2      | HSC-CQR recency (capped)    | 652 | 0.5     | 14.7  | 19.9      | 83.6    | 42.5    | 42.5      | 16.1        | 69.0         | 0.570           | 0.729         | 0.410              | 1.337    | 1.422    | 1.592    | 2.456            | 1.9       | 17.2       | 72.6      | +0.4            | -0.3            | -1.6            | -1.6                    | +0.5                   | -0.8                 |
| robust:calpool50       | BDG2      | HSC-CQR recency             | 652 | 0.3     | 14.5  | 19.8      | 83.6    | 42.4    | 42.4      | 16.0        | 68.7         | 0.570           | 0.750         | 0.410              | 1.348    | 1.431    | 1.596    | 2.543            | 1.9       | 17.2       | 72.6      | +1.2            | +0.3            | -1.3            | +1.9                    | +0.5                   | +2.1                 |
| robust:calpool50       | BDG2      | QShrink-CQR (cov)           | 652 | 1.0     | 14.6  | 20.6      | 84.4    | 48.3    | 48.3      | 15.9        | 68.5         | 0.569           | 0.750         | 0.405              | 1.348    | 1.430    | 1.595    | 2.539            | 1.9       | 17.2       | 72.6      | +1.2            | +0.3            | -1.3            | +1.7                    | +0.2                   | +2.1                 |
| robust:calpool50       | BDG2      | ACI-CQR (cov)               | 652 | 3.7     | 19.0  | 20.9      | 80.8    | 49.9    | 49.9      | 16.7        | 68.0         | 0.566           | 0.756         | 0.404              | 1.346    | 1.437    | 1.617    | 2.610            | 1.9       | 17.2       | 72.6      | +1.1            | +0.7            | +0.0            | +4.5                    | -0.3                   | +2.8                 |
| robust:calpool50       | BDG2      | CQR                         | 652 | 16.4    | 19.8  | 24.0      | 74.1    | 51.3    | 51.3      | 17.7        | 63.9         | 0.567           | 0.735         | 0.401              | 1.332    | 1.427    | 1.617    | 2.497            | 1.9       | 17.2       | 72.6      | +0.0            | +0.0            | +0.0            | +0.0                    | +0.0                   | +0.0                 |
| robust:calpool50       | BDG2      | TTSC (cumulative feedback)  | 652 | 0.5     | 13.0  | 15.9      | 77.3    | 27.5    | 27.5      | 14.5        | 67.4         | 0.589           | 0.742         | 0.442              | 1.346    | 1.426    | 1.588    | 2.455            | 1.9       | 17.2       | 72.6      | +1.1            | -0.0            | -1.8            | -1.7                    | +3.7                   | +1.0                 |
| robust:calpool50       | BDG2      | TTSC (uncapped)             | 652 | 0.0     | 11.8  | 13.8      | 71.3    | 19.6    | 19.6      | 14.1        | 65.2         | 0.709           | 1.214         | 0.516              | 1.583    | 1.658    | 1.810    | 3.644            | 1.9       | 17.2       | 72.6      | +18.9           | +16.2           | +11.9           | +45.9                   | +24.9                  | +65.2                |
| robust:calpool50       | BDG2      | TTSC (delay 1d)             | 652 | 0.4     | 19.4  | 19.0      | 85.1    | 39.4    | 39.4      | 16.0        | 72.3         | 0.592           | 0.752         | 0.446              | 1.349    | 1.432    | 1.598    | 2.462            | 1.9       | 17.2       | 72.6      | +1.3            | +0.4            | -1.1            | -1.4                    | +4.3                   | +2.3                 |
| robust:missing20       | BDG2      | TTSC                        | 652 | 0.4     | 11.2  | 14.1      | 69.8    | 19.1    | 19.1      | 12.1        | 57.5         | 0.629           | 0.786         | 0.485              | 1.379    | 1.461    | 1.626    | 2.539            | 1.8       | 17.3       | 72.6      | +0.6            | -0.3            | -1.7            | -1.8                    | +2.4                   | -0.2                 |
| robust:missing20       | BDG2      | HSC-CQR recency (capped)    | 652 | 0.6     | 13.1  | 18.9      | 81.5    | 38.1    | 38.1      | 12.8        | 58.8         | 0.613           | 0.780         | 0.465              | 1.374    | 1.460    | 1.631    | 2.545            | 1.8       | 17.3       | 72.6      | +0.3            | -0.4            | -1.5            | -1.5                    | -0.2                   | -1.1                 |
| robust:missing20       | BDG2      | HSC-CQR recency             | 652 | 0.3     | 13.0  | 18.7      | 81.3    | 37.8    | 37.8      | 12.7        | 58.7         | 0.613           | 0.796         | 0.465              | 1.383    | 1.467    | 1.633    | 2.609            | 1.8       | 17.3       | 72.6      | +0.9            | +0.1            | -1.3            | +1.0                    | -0.2                   | +1.0                 |
| robust:missing20       | BDG2      | QShrink-CQR (cov)           | 652 | 1.0     | 15.3  | 20.0      | 84.2    | 43.1    | 43.1      | 13.0        | 58.9         | 0.614           | 0.799         | 0.457              | 1.384    | 1.467    | 1.633    | 2.614            | 1.8       | 17.3       | 72.6      | +1.0            | +0.1            | -1.3            | +1.2                    | -0.1                   | +1.4                 |
| robust:missing20       | BDG2      | ACI-CQR (cov)               | 652 | 5.7     | 20.1  | 19.6      | 75.2    | 45.1    | 45.1      | 14.2        | 57.8         | 0.614           | 0.785         | 0.460              | 1.372    | 1.464    | 1.646    | 2.583            | 1.8       | 17.3       | 72.6      | +0.1            | -0.1            | -0.5            | -0.1                    | -0.2                   | -0.4                 |
| robust:missing20       | BDG2      | CQR                         | 652 | 14.0    | 20.5  | 21.4      | 68.3    | 46.1    | 46.1      | 15.0        | 55.1         | 0.615           | 0.788         | 0.457              | 1.371    | 1.465    | 1.655    | 2.584            | 1.8       | 17.3       | 72.6      | +0.0            | +0.0            | +0.0            | +0.0                    | +0.0                   | +0.0                 |
| robust:missing20       | BDG2      | TTSC (cumulative feedback)  | 652 | 0.5     | 11.2  | 16.9      | 79.2    | 25.3    | 25.3      | 12.3        | 59.3         | 0.628           | 0.790         | 0.487              | 1.381    | 1.463    | 1.626    | 2.538            | 1.8       | 17.3       | 72.6      | +0.7            | -0.2            | -1.7            | -1.8                    | +2.1                   | +0.2                 |
| robust:missing20       | BDG2      | TTSC (uncapped)             | 652 | 0.0     | 10.9  | 13.5      | 69.3    | 16.7    | 16.7      | 11.8        | 57.2         | 0.669           | 1.044         | 0.519              | 1.509    | 1.586    | 1.739    | 3.344            | 1.8       | 17.3       | 72.6      | +10.1           | +8.2            | +5.1            | +29.4                   | +8.8                   | +32.4                |
| robust:missing20       | BDG2      | TTSC (delay 1d)             | 652 | 0.6     | 15.2  | 18.3      | 82.4    | 31.9    | 31.9      | 13.2        | 61.5         | 0.635           | 0.797         | 0.490              | 1.383    | 1.467    | 1.635    | 2.549            | 1.8       | 17.3       | 72.6      | +0.9            | +0.1            | -1.2            | -1.4                    | +3.2                   | +1.0                 |
| robust:missing40       | BDG2      | TTSC                        | 652 | 0.4     | 10.0  | 14.2      | 70.9    | 22.8    | 22.8      | 11.8        | 55.4         | 0.676           | 0.840         | 0.534              | 1.418    | 1.503    | 1.674    | 2.634            | 1.9       | 17.6       | 73.6      | +0.3            | -0.6            | -2.0            | -2.2                    | +0.3                   | -1.2                 |
| robust:missing40       | BDG2      | HSC-CQR recency (capped)    | 652 | 0.8     | 12.2  | 17.2      | 78.3    | 39.3    | 39.3      | 12.4        | 57.1         | 0.670           | 0.838         | 0.523              | 1.415    | 1.504    | 1.680    | 2.645            | 1.9       | 17.6       | 73.6      | +0.1            | -0.5            | -1.6            | -1.8                    | -0.5                   | -1.5                 |
| robust:missing40       | BDG2      | HSC-CQR recency             | 652 | 0.2     | 11.9  | 17.0      | 78.0    | 39.0    | 39.0      | 12.3        | 57.0         | 0.670           | 0.854         | 0.523              | 1.424    | 1.510    | 1.681    | 2.703            | 1.9       | 17.6       | 73.6      | +0.8            | -0.1            | -1.6            | +0.4                    | -0.5                   | +0.4                 |
| robust:missing40       | BDG2      | QShrink-CQR (cov)           | 652 | 1.4     | 14.1  | 18.9      | 83.0    | 42.5    | 42.5      | 12.9        | 58.5         | 0.671           | 0.860         | 0.512              | 1.427    | 1.512    | 1.683    | 2.722            | 1.9       | 17.6       | 73.6      | +1.0            | +0.1            | -1.4            | +1.1                    | -0.4                   | +1.2                 |
| robust:missing40       | BDG2      | ACI-CQR (cov)               | 652 | 7.7     | 20.3  | 19.4      | 71.4    | 45.2    | 45.2      | 13.8        | 56.2         | 0.670           | 0.852         | 0.515              | 1.417    | 1.512    | 1.701    | 2.712            | 1.9       | 17.6       | 73.6      | +0.3            | +0.0            | -0.4            | +0.7                    | -0.5                   | +0.1                 |
| robust:missing40       | BDG2      | CQR                         | 652 | 14.6    | 20.8  | 20.8      | 65.5    | 44.0    | 44.0      | 14.0        | 52.2         | 0.674           | 0.850         | 0.516              | 1.413    | 1.511    | 1.708    | 2.692            | 1.9       | 17.6       | 73.6      | +0.0            | +0.0            | +0.0            | +0.0                    | +0.0                   | +0.0                 |
| robust:missing40       | BDG2      | TTSC (cumulative feedback)  | 652 | 0.4     | 10.0  | 17.1      | 80.3    | 31.0    | 31.0      | 12.2        | 58.3         | 0.681           | 0.844         | 0.533              | 1.419    | 1.504    | 1.675    | 2.635            | 1.9       | 17.6       | 73.6      | +0.4            | -0.5            | -1.9            | -2.1                    | +1.1                   | -0.8                 |
| robust:missing40       | BDG2      | TTSC (uncapped)             | 652 | 0.0     | 9.5   | 13.7      | 70.4    | 21.7    | 21.7      | 11.6        | 54.9         | 0.680           | 0.948         | 0.541              | 1.473    | 1.551    | 1.709    | 3.007            | 1.9       | 17.6       | 73.6      | +4.2            | +2.6            | +0.1            | +11.7                   | +1.0                   | +11.4                |
| robust:missing40       | BDG2      | TTSC (delay 1d)             | 652 | 0.8     | 14.5  | 17.4      | 81.8    | 33.7    | 33.7      | 12.4        | 58.0         | 0.687           | 0.848         | 0.537              | 1.420    | 1.507    | 1.681    | 2.645            | 1.9       | 17.6       | 73.6      | +0.5            | -0.3            | -1.6            | -1.8                    | +2.0                   | -0.3                 |
| robust:noise15         | BDG2      | TTSC                        | 652 | 0.3     | 5.0   | 4.7       | 29.4    | 6.5     | 6.5       | 7.7         | 39.7         | 0.932           | 1.099         | 0.735              | 1.507    | 1.598    | 1.779    | 2.499            | 0.4       | 7.8        | 39.3      | +1.2            | -0.7            | -3.8            | -2.2                    | -0.2                   | -0.9                 |
| robust:noise15         | BDG2      | HSC-CQR recency (capped)    | 652 | 0.3     | 9.8   | 8.4       | 49.2    | 14.6    | 14.6      | 9.6         | 49.8         | 0.925           | 1.092         | 0.721              | 1.503    | 1.596    | 1.781    | 2.499            | 0.4       | 7.8        | 39.3      | +0.9            | -0.8            | -3.7            | -2.2                    | -1.0                   | -1.5                 |
| robust:noise15         | BDG2      | HSC-CQR recency             | 652 | 0.0     | 9.4   | 8.3       | 48.7    | 14.4    | 14.4      | 9.5         | 49.4         | 0.925           | 1.109         | 0.721              | 1.512    | 1.603    | 1.785    | 2.565            | 0.4       | 7.8        | 39.3      | +1.5            | -0.4            | -3.5            | +0.5                    | -1.0                   | +0.0                 |
| robust:noise15         | BDG2      | QShrink-CQR (cov)           | 652 | 0.1     | 14.7  | 9.1       | 55.1    | 18.1    | 18.1      | 9.9         | 50.7         | 0.926           | 1.107         | 0.722              | 1.511    | 1.602    | 1.783    | 2.554            | 0.4       | 7.8        | 39.3      | +1.5            | -0.4            | -3.6            | -0.0                    | -0.9                   | -0.1                 |
| robust:noise15         | BDG2      | ACI-CQR (cov)               | 652 | 5.8     | 34.8  | 19.6      | 84.0    | 35.8    | 35.8      | 16.3        | 67.6         | 0.928           | 1.117         | 0.686              | 1.504    | 1.610    | 1.823    | 2.615            | 0.4       | 7.8        | 39.3      | +1.0            | +0.1            | -1.4            | +2.4                    | -0.6                   | +0.8                 |
| robust:noise15         | BDG2      | CQR                         | 652 | 30.1    | 36.6  | 34.2      | 90.5    | 47.9    | 47.9      | 22.7        | 75.1         | 0.934           | 1.109         | 0.663              | 1.489    | 1.609    | 1.849    | 2.554            | 0.4       | 7.8        | 39.3      | +0.0            | +0.0            | +0.0            | +0.0                    | +0.0                   | +0.0                 |
| robust:noise15         | BDG2      | TTSC (cumulative feedback)  | 652 | 0.4     | 5.0   | 5.6       | 33.5    | 7.2     | 7.2       | 7.5         | 40.0         | 0.936           | 1.101         | 0.739              | 1.508    | 1.598    | 1.778    | 2.499            | 0.4       | 7.8        | 39.3      | +1.3            | -0.7            | -3.9            | -2.1                    | +0.2                   | -0.7                 |
| robust:noise15         | BDG2      | TTSC (uncapped)             | 652 | 0.0     | 4.3   | 4.1       | 27.7    | 4.1     | 4.1       | 7.3         | 38.7         | 0.934           | 1.272         | 0.739              | 1.595    | 1.680    | 1.851    | 3.172            | 0.4       | 7.8        | 39.3      | +7.1            | +4.4            | +0.1            | +24.2                   | -0.0                   | +14.8                |
| robust:noise15         | BDG2      | TTSC (delay 1d)             | 652 | 0.3     | 8.7   | 7.1       | 41.9    | 9.5     | 9.5       | 8.3         | 43.7         | 0.937           | 1.104         | 0.737              | 1.509    | 1.601    | 1.785    | 2.508            | 0.4       | 7.8        | 39.3      | +1.4            | -0.5            | -3.4            | -1.8                    | +0.4                   | -0.4                 |
| robust:noise5          | BDG2      | TTSC                        | 652 | 0.3     | 7.1   | 9.6       | 51.0    | 12.4    | 12.4      | 12.0        | 57.3         | 0.635           | 0.800         | 0.485              | 1.369    | 1.451    | 1.615    | 2.454            | 1.0       | 13.2       | 60.1      | +0.9            | -0.2            | -2.0            | -1.8                    | +2.4                   | +0.5                 |
| robust:noise5          | BDG2      | HSC-CQR recency (capped)    | 652 | 0.3     | 10.6  | 15.1      | 73.9    | 27.3    | 27.3      | 13.9        | 64.2         | 0.624           | 0.791         | 0.463              | 1.364    | 1.449    | 1.618    | 2.457            | 1.0       | 13.2       | 60.1      | +0.5            | -0.3            | -1.8            | -1.7                    | +0.7                   | -0.6                 |
| robust:noise5          | BDG2      | HSC-CQR recency             | 652 | 0.0     | 10.2  | 15.0      | 73.6    | 27.2    | 27.2      | 13.8        | 63.9         | 0.624           | 0.814         | 0.463              | 1.376    | 1.458    | 1.624    | 2.550            | 1.0       | 13.2       | 60.1      | +1.4            | +0.3            | -1.5            | +2.0                    | +0.7                   | +2.2                 |
| robust:noise5          | BDG2      | QShrink-CQR (cov)           | 652 | 0.6     | 12.2  | 16.7      | 76.8    | 32.8    | 32.8      | 14.4        | 65.6         | 0.622           | 0.813         | 0.459              | 1.375    | 1.457    | 1.623    | 2.541            | 1.0       | 13.2       | 60.1      | +1.4            | +0.3            | -1.5            | +1.6                    | +0.4                   | +2.1                 |
| robust:noise5          | BDG2      | ACI-CQR (cov)               | 652 | 3.8     | 19.1  | 18.9      | 76.1    | 40.5    | 40.5      | 16.5        | 66.9         | 0.619           | 0.814         | 0.453              | 1.370    | 1.462    | 1.644    | 2.593            | 1.0       | 13.2       | 60.1      | +1.0            | +0.6            | -0.2            | +3.7                    | -0.1                   | +2.2                 |
| robust:noise5          | BDG2      | CQR                         | 652 | 16.9    | 20.2  | 24.5      | 76.9    | 46.6    | 46.6      | 18.4        | 65.1         | 0.620           | 0.796         | 0.446              | 1.357    | 1.454    | 1.648    | 2.500            | 1.0       | 13.2       | 60.1      | +0.0            | +0.0            | +0.0            | +0.0                    | +0.0                   | +0.0                 |
| robust:noise5          | BDG2      | TTSC (cumulative feedback)  | 652 | 0.4     | 7.1   | 11.3      | 58.2    | 15.0    | 15.0      | 12.3        | 59.9         | 0.638           | 0.803         | 0.488              | 1.371    | 1.453    | 1.615    | 2.455            | 1.0       | 13.2       | 60.1      | +1.1            | -0.1            | -2.0            | -1.8                    | +2.9                   | +0.9                 |
| robust:noise5          | BDG2      | TTSC (uncapped)             | 652 | 0.0     | 6.6   | 8.9       | 50.4    | 10.0    | 10.0      | 11.6        | 56.7         | 0.664           | 1.109         | 0.507              | 1.526    | 1.601    | 1.753    | 3.473            | 1.0       | 13.2       | 60.1      | +12.5           | +10.2           | +6.4            | +38.9                   | +7.0                   | +39.3                |
| robust:noise5          | BDG2      | TTSC (delay 1d)             | 652 | 0.4     | 12.4  | 13.3      | 68.1    | 22.2    | 22.2      | 13.2        | 62.8         | 0.648           | 0.810         | 0.495              | 1.374    | 1.457    | 1.624    | 2.467            | 1.0       | 13.2       | 60.1      | +1.3            | +0.2            | -1.4            | -1.3                    | +4.4                   | +1.7                 |
| robust:outage1-3d      | BDG2      | TTSC                        | 652 | 0.2     | 15.1  | 15.4      | 76.0    | 28.4    | 28.4      | 14.4        | 67.0         | 0.613           | 0.764         | 0.453              | 1.357    | 1.440    | 1.606    | 2.492            | 2.2       | 18.4       | 75.7      | +1.1            | +0.1            | -1.7            | -1.6                    | +3.7                   | +1.0                 |
| robust:outage1-3d      | BDG2      | HSC-CQR recency (capped)    | 652 | 0.4     | 16.4  | 21.1      | 86.7    | 47.5    | 47.5      | 15.8        | 69.2         | 0.596           | 0.751         | 0.425              | 1.349    | 1.435    | 1.608    | 2.495            | 2.2       | 18.4       | 75.7      | +0.5            | -0.3            | -1.6            | -1.4                    | +0.9                   | -0.7                 |
| robust:outage1-3d      | BDG2      | HSC-CQR recency             | 652 | 0.2     | 16.2  | 20.9      | 86.4    | 47.3    | 47.3      | 15.6        | 69.0         | 0.596           | 0.774         | 0.425              | 1.360    | 1.445    | 1.613    | 2.587            | 2.2       | 18.4       | 75.7      | +1.4            | +0.4            | -1.3            | +2.2                    | +0.9                   | +2.2                 |
| robust:outage1-3d      | BDG2      | QShrink-CQR (cov)           | 652 | 1.3     | 16.8  | 22.1      | 87.3    | 51.4    | 51.4      | 15.8        | 69.8         | 0.595           | 0.773         | 0.421              | 1.360    | 1.444    | 1.612    | 2.578            | 2.2       | 18.4       | 75.7      | +1.3            | +0.3            | -1.3            | +1.8                    | +0.8                   | +2.2                 |
| robust:outage1-3d      | BDG2      | ACI-CQR (cov)               | 652 | 5.4     | 21.1  | 21.8      | 82.6    | 54.7    | 54.7      | 16.9        | 70.0         | 0.592           | 0.759         | 0.420              | 1.348    | 1.440    | 1.625    | 2.554            | 2.2       | 18.4       | 75.7      | +0.4            | +0.1            | -0.6            | +0.9                    | +0.2                   | +0.3                 |
| robust:outage1-3d      | BDG2      | CQR                         | 652 | 19.0    | 21.5  | 24.8      | 73.4    | 56.8    | 56.8      | 17.5        | 64.6         | 0.591           | 0.757         | 0.413              | 1.342    | 1.440    | 1.634    | 2.532            | 2.2       | 18.4       | 75.7      | +0.0            | +0.0            | +0.0            | +0.0                    | +0.0                   | +0.0                 |
| robust:outage1-3d      | BDG2      | TTSC (cumulative feedback)  | 652 | 0.2     | 15.1  | 17.4      | 82.0    | 34.4    | 34.4      | 14.4        | 67.7         | 0.611           | 0.767         | 0.459              | 1.359    | 1.442    | 1.606    | 2.495            | 2.2       | 18.4       | 75.7      | +1.3            | +0.1            | -1.7            | -1.5                    | +3.5                   | +1.4                 |
| robust:outage1-3d      | BDG2      | TTSC (uncapped)             | 652 | 0.0     | 14.1  | 14.8      | 74.5    | 25.8    | 25.8      | 13.9        | 66.2         | 0.806           | 1.413         | 0.594              | 1.683    | 1.760    | 1.913    | 4.094            | 2.2       | 18.4       | 75.7      | +25.4           | +22.2           | +17.1           | +61.7                   | +36.4                  | +86.7                |
| robust:outage1-3d      | BDG2      | TTSC (delay 1d)             | 652 | 0.3     | 21.6  | 20.3      | 88.6    | 47.7    | 47.7      | 16.0        | 72.0         | 0.627           | 0.779         | 0.465              | 1.364    | 1.449    | 1.619    | 2.502            | 2.2       | 18.4       | 75.7      | +1.6            | +0.7            | -0.9            | -1.2                    | +6.2                   | +3.0                 |
| robust:ramp+40         | BDG2      | TTSC                        | 652 | 0.4     | 14.3  | 15.4      | 73.3    | 21.3    | 21.3      | 33.4        | 95.0         | 0.607           | 0.764         | 0.435              | 1.335    | 1.435    | 1.635    | 2.466            | 1.7       | 17.3       | 72.3      | +1.0            | -0.7            | -3.4            | -2.9                    | +3.0                   | +0.7                 |
| robust:ramp+40         | BDG2      | HSC-CQR recency (capped)    | 652 | 1.0     | 16.7  | 22.9      | 89.4    | 49.0    | 49.0      | 35.8        | 96.2         | 0.589           | 0.751         | 0.408              | 1.327    | 1.432    | 1.643    | 2.473            | 1.7       | 17.3       | 72.3      | +0.4            | -0.9            | -2.9            | -2.6                    | -0.0                   | -1.1                 |
| robust:ramp+40         | BDG2      | HSC-CQR recency             | 652 | 0.8     | 16.4  | 22.7      | 89.1    | 48.6    | 48.6      | 35.7        | 96.1         | 0.589           | 0.771         | 0.408              | 1.338    | 1.440    | 1.646    | 2.551            | 1.7       | 17.3       | 72.3      | +1.2            | -0.3            | -2.7            | +0.5                    | -0.0                   | +1.5                 |
| robust:ramp+40         | BDG2      | QShrink-CQR (cov)           | 652 | 2.4     | 16.7  | 26.0      | 91.7    | 54.6    | 54.6      | 36.9        | 95.7         | 0.588           | 0.770         | 0.402              | 1.337    | 1.441    | 1.648    | 2.545            | 1.7       | 17.3       | 72.3      | +1.2            | -0.3            | -2.6            | +0.2                    | -0.3                   | +1.5                 |
| robust:ramp+40         | BDG2      | ACI-CQR (cov)               | 652 | 6.0     | 20.3  | 25.9      | 90.6    | 58.6    | 58.6      | 37.3        | 95.6         | 0.586           | 0.784         | 0.394              | 1.340    | 1.453    | 1.680    | 2.670            | 1.7       | 17.3       | 72.3      | +1.4            | +0.6            | -0.7            | +5.1                    | -0.5                   | +3.3                 |
| robust:ramp+40         | BDG2      | CQR                         | 652 | 26.8    | 21.2  | 34.0      | 89.5    | 64.4    | 64.4      | 41.0        | 95.3         | 0.590           | 0.759         | 0.383              | 1.321    | 1.445    | 1.692    | 2.540            | 1.7       | 17.3       | 72.3      | +0.0            | +0.0            | +0.0            | +0.0                    | +0.0                   | +0.0                 |
| robust:ramp+40         | BDG2      | TTSC (cumulative feedback)  | 652 | 0.5     | 14.3  | 15.2      | 76.6    | 26.6    | 26.6      | 29.8        | 93.9         | 0.612           | 0.769         | 0.451              | 1.338    | 1.436    | 1.632    | 2.466            | 1.7       | 17.3       | 72.3      | +1.3            | -0.6            | -3.6            | -2.9                    | +3.8                   | +1.3                 |
| robust:ramp+40         | BDG2      | TTSC (uncapped)             | 652 | 0.0     | 13.0  | 14.6      | 71.8    | 18.2    | 18.2      | 32.8        | 94.8         | 0.811           | 1.331         | 0.595              | 1.620    | 1.713    | 1.898    | 3.761            | 1.7       | 17.3       | 72.3      | +22.6           | +18.5           | +12.2           | +48.1                   | +37.5                  | +75.3                |
| robust:ramp+40         | BDG2      | TTSC (delay 1d)             | 652 | 0.8     | 19.2  | 20.4      | 84.7    | 40.6    | 40.6      | 33.8        | 95.1         | 0.618           | 0.782         | 0.452              | 1.343    | 1.445    | 1.649    | 2.477            | 1.7       | 17.3       | 72.3      | +1.6            | +0.0            | -2.5            | -2.5                    | +4.8                   | +3.0                 |
| robust:shift+40        | BDG2      | TTSC                        | 652 | 0.4     | 12.7  | 20.5      | 94.6    | 58.6    | 58.6      | 27.2        | 96.4         | 0.702           | 0.864         | 0.494              | 1.381    | 1.505    | 1.753    | 2.496            | 2.8       | 20.4       | 80.5      | +1.5            | -0.8            | -4.2            | -3.3                    | +3.9                   | +2.2                 |
| robust:shift+40        | BDG2      | HSC-CQR recency (capped)    | 652 | 0.8     | 14.9  | 24.9      | 97.7    | 70.1    | 70.1      | 30.1        | 98.3         | 0.680           | 0.838         | 0.453              | 1.368    | 1.500    | 1.764    | 2.501            | 2.8       | 20.4       | 80.5      | +0.4            | -1.2            | -3.5            | -3.1                    | +0.7                   | -0.9                 |
| robust:shift+40        | BDG2      | HSC-CQR recency             | 652 | 0.5     | 14.6  | 24.7      | 97.6    | 69.9    | 69.9      | 29.9        | 98.2         | 0.680           | 0.858         | 0.453              | 1.378    | 1.508    | 1.767    | 2.578            | 2.8       | 20.4       | 80.5      | +1.2            | -0.6            | -3.4            | -0.2                    | +0.7                   | +1.5                 |
| robust:shift+40        | BDG2      | QShrink-CQR (cov)           | 652 | 1.9     | 14.9  | 27.2      | 96.8    | 71.7    | 71.7      | 32.4        | 98.1         | 0.677           | 0.856         | 0.439              | 1.377    | 1.510    | 1.775    | 2.575            | 2.8       | 20.4       | 80.5      | +1.1            | -0.5            | -2.9            | -0.2                    | +0.2                   | +1.2                 |
| robust:shift+40        | BDG2      | ACI-CQR (cov)               | 652 | 6.6     | 19.1  | 28.7      | 97.7    | 72.3    | 72.3      | 34.1        | 98.4         | 0.675           | 0.873         | 0.433              | 1.382    | 1.525    | 1.811    | 2.714            | 2.8       | 20.4       | 80.5      | +1.5            | +0.5            | -1.0            | +5.1                    | -0.1                   | +3.3                 |
| robust:shift+40        | BDG2      | CQR                         | 652 | 26.0    | 19.6  | 35.0      | 93.8    | 70.1    | 70.1      | 38.6        | 98.7         | 0.675           | 0.846         | 0.409              | 1.362    | 1.517    | 1.829    | 2.582            | 2.8       | 20.4       | 80.5      | +0.0            | +0.0            | +0.0            | +0.0                    | +0.0                   | +0.0                 |
| robust:shift+40        | BDG2      | TTSC (cumulative feedback)  | 652 | 0.5     | 12.7  | 20.0      | 93.6    | 62.9    | 62.9      | 24.6        | 96.8         | 0.717           | 0.873         | 0.520              | 1.387    | 1.507    | 1.746    | 2.494            | 2.8       | 20.4       | 80.5      | +1.9            | -0.7            | -4.5            | -3.4                    | +6.1                   | +3.3                 |
| robust:shift+40        | BDG2      | TTSC (uncapped)             | 652 | 0.0     | 11.7  | 19.7      | 93.9    | 56.0    | 56.0      | 26.5        | 96.0         | 1.504           | 1.944         | 1.230              | 1.923    | 2.039    | 2.270    | 4.101            | 2.8       | 20.4       | 80.5      | +41.2           | +34.4           | +24.1           | +58.9                   | +122.6                 | +129.9               |
| robust:shift+40        | BDG2      | TTSC (delay 1d)             | 652 | 0.7     | 19.4  | 24.0      | 96.7    | 69.9    | 69.9      | 29.1        | 97.9         | 0.718           | 0.879         | 0.507              | 1.389    | 1.514    | 1.765    | 2.503            | 2.8       | 20.4       | 80.5      | +2.0            | -0.2            | -3.5            | -3.0                    | +6.4                   | +4.0                 |
| robust:shift+40@d3-14  | BDG2      | TTSC                        | 652 | 0.4     | 36.7  | 15.0      | 88.7    | 40.4    | 40.4      | 26.2        | 97.2         | 0.678           | 0.850         | 0.498              | 1.382    | 1.497    | 1.726    | 2.496            | 2.5       | 20.2       | 80.7      | +1.9            | -0.2            | -3.4            | -2.8                    | +4.7                   | +3.3                 |
| robust:shift+40@d3-14  | BDG2      | HSC-CQR recency (capped)    | 652 | 0.4     | 38.4  | 18.2      | 94.5    | 55.4    | 55.4      | 25.5        | 98.6         | 0.661           | 0.826         | 0.470              | 1.370    | 1.489    | 1.726    | 2.496            | 2.5       | 20.2       | 80.7      | +1.0            | -0.7            | -3.4            | -2.8                    | +2.2                   | +0.5                 |
| robust:shift+40@d3-14  | BDG2      | HSC-CQR recency             | 652 | 0.2     | 38.1  | 18.0      | 94.3    | 54.7    | 54.7      | 25.3        | 98.1         | 0.663           | 0.847         | 0.470              | 1.381    | 1.497    | 1.729    | 2.574            | 2.5       | 20.2       | 80.7      | +1.8            | -0.2            | -3.2            | +0.2                    | +2.4                   | +3.0                 |
| robust:shift+40@d3-14  | BDG2      | QShrink-CQR (cov)           | 652 | 0.5     | 38.5  | 16.5      | 92.7    | 56.4    | 56.4      | 24.3        | 98.2         | 0.664           | 0.846         | 0.472              | 1.382    | 1.496    | 1.724    | 2.563            | 2.5       | 20.2       | 80.7      | +1.9            | -0.2            | -3.5            | -0.2                    | +2.6                   | +2.9                 |
| robust:shift+40@d3-14  | BDG2      | ACI-CQR (cov)               | 652 | 5.4     | 44.1  | 23.0      | 95.8    | 70.4    | 70.4      | 30.0        | 98.9         | 0.647           | 0.837         | 0.429              | 1.371    | 1.504    | 1.769    | 2.642            | 2.5       | 20.2       | 80.7      | +1.1            | +0.3            | -1.0            | +2.9                    | -0.0                   | +1.8                 |
| robust:shift+40@d3-14  | BDG2      | CQR                         | 652 | 23.8    | 44.4  | 30.3      | 94.1    | 73.8    | 73.8      | 34.5        | 99.0         | 0.647           | 0.822         | 0.405              | 1.357    | 1.500    | 1.786    | 2.568            | 2.5       | 20.2       | 80.7      | +0.0            | +0.0            | +0.0            | +0.0                    | +0.0                   | +0.0                 |
| robust:shift+40@d3-14  | BDG2      | TTSC (cumulative feedback)  | 652 | 0.4     | 36.7  | 16.9      | 92.0    | 46.2    | 46.2      | 25.3        | 97.8         | 0.693           | 0.856         | 0.507              | 1.385    | 1.498    | 1.723    | 2.491            | 2.5       | 20.2       | 80.7      | +2.1            | -0.1            | -3.5            | -3.0                    | +7.2                   | +4.2                 |
| robust:shift+40@d3-14  | BDG2      | TTSC (uncapped)             | 652 | 0.0     | 35.7  | 14.1      | 87.5    | 35.5    | 35.5      | 25.4        | 96.6         | 1.602           | 2.170         | 1.337              | 2.044    | 2.150    | 2.363    | 4.505            | 2.5       | 20.2       | 80.7      | +50.6           | +43.4           | +32.3           | +75.4                   | +147.7                 | +163.9               |
| robust:shift+40@d3-14  | BDG2      | TTSC (delay 1d)             | 652 | 0.7     | 40.7  | 19.5      | 92.6    | 54.2    | 54.2      | 27.0        | 97.3         | 0.702           | 0.864         | 0.507              | 1.388    | 1.505    | 1.738    | 2.508            | 2.5       | 20.2       | 80.7      | +2.3            | +0.3            | -2.7            | -2.3                    | +8.5                   | +5.1                 |
| robust:shift-40        | BDG2      | TTSC                        | 652 | 0.4     | 12.7  | 21.4      | 98.0    | 66.8    | 66.8      | 8.5         | 47.1         | 0.809           | 0.959         | 0.576              | 1.470    | 1.538    | 1.675    | 2.524            | 3.8       | 21.7       | 83.0      | +2.5            | +1.7            | +0.3            | -0.5                    | +5.9                   | +3.4                 |
| robust:shift-40        | BDG2      | HSC-CQR recency (capped)    | 652 | 0.5     | 14.9  | 24.6      | 98.0    | 73.7    | 73.7      | 9.1         | 48.8         | 0.768           | 0.924         | 0.531              | 1.448    | 1.519    | 1.660    | 2.522            | 3.8       | 21.7       | 83.0      | +1.0            | +0.4            | -0.6            | -0.6                    | +0.5                   | -0.3                 |
| robust:shift-40        | BDG2      | HSC-CQR recency             | 652 | 0.3     | 14.6  | 24.5      | 97.6    | 73.5    | 73.5      | 9.0         | 48.3         | 0.768           | 0.948         | 0.531              | 1.461    | 1.530    | 1.667    | 2.626            | 3.8       | 21.7       | 83.0      | +1.9            | +1.1            | -0.2            | +3.5                    | +0.5                   | +2.3                 |
| robust:shift-40        | BDG2      | QShrink-CQR (cov)           | 652 | 2.6     | 14.9  | 26.9      | 97.6    | 76.4    | 76.4      | 9.0         | 49.7         | 0.771           | 0.946         | 0.518              | 1.458    | 1.527    | 1.664    | 2.622            | 3.8       | 21.7       | 83.0      | +1.7            | +0.9            | -0.4            | +3.3                    | +1.0                   | +2.1                 |
| robust:shift-40        | BDG2      | ACI-CQR (cov)               | 652 | 3.1     | 19.1  | 27.9      | 98.4    | 77.5    | 77.5      | 9.9         | 49.7         | 0.762           | 0.953         | 0.516              | 1.455    | 1.531    | 1.682    | 2.689            | 3.8       | 21.7       | 83.0      | +1.5            | +1.2            | +0.7            | +6.0                    | -0.3                   | +2.9                 |
| robust:shift-40        | BDG2      | CQR                         | 652 | 21.3    | 19.6  | 33.8      | 96.1    | 76.1    | 76.1      | 10.7        | 49.7         | 0.764           | 0.927         | 0.503              | 1.433    | 1.512    | 1.670    | 2.537            | 3.8       | 21.7       | 83.0      | +0.0            | +0.0            | +0.0            | +0.0                    | +0.0                   | +0.0                 |
| robust:shift-40        | BDG2      | TTSC (cumulative feedback)  | 652 | 0.4     | 12.7  | 21.2      | 96.2    | 66.3    | 66.3      | 8.8         | 49.1         | 0.818           | 0.964         | 0.590              | 1.474    | 1.542    | 1.678    | 2.525            | 3.8       | 21.7       | 83.0      | +2.9            | +2.0            | +0.5            | -0.5                    | +7.1                   | +4.0                 |
| robust:shift-40        | BDG2      | TTSC (uncapped)             | 652 | 0.0     | 11.7  | 20.7      | 97.0    | 64.0    | 64.0      | 8.1         | 46.3         | 1.824           | 2.318         | 1.543              | 2.152    | 2.214    | 2.339    | 4.547            | 3.8       | 21.7       | 83.0      | +50.1           | +46.4           | +40.0           | +79.2                   | +138.8                 | +150.2               |
| robust:shift-40        | BDG2      | TTSC (delay 1d)             | 652 | 0.4     | 19.4  | 24.5      | 98.8    | 73.5    | 73.5      | 9.5         | 51.6         | 0.819           | 0.972         | 0.590              | 1.476    | 1.545    | 1.684    | 2.535            | 3.8       | 21.7       | 83.0      | +2.9            | +2.2            | +0.8            | -0.1                    | +7.2                   | +4.9                 |
| robust:spikes2         | BDG2      | TTSC                        | 652 | 0.4     | 7.7   | 10.4      | 57.6    | 13.2    | 13.2      | 8.9         | 45.4         | 1.351           | 1.476         | 0.617              | 1.766    | 2.122    | 2.834    | 2.982            | 1.3       | 15.4       | 68.2      | +0.2            | -0.1            | -0.5            | -1.0                    | +0.4                   | +0.1                 |
| robust:spikes2         | BDG2      | HSC-CQR recency (capped)    | 652 | 0.4     | 9.3   | 13.2      | 68.5    | 28.3    | 28.3      | 8.9         | 43.2         | 1.338           | 1.464         | 0.600              | 1.760    | 2.119    | 2.837    | 2.986            | 1.3       | 15.4       | 68.2      | -0.1            | -0.3            | -0.4            | -0.9                    | -0.6                   | -0.7                 |
| robust:spikes2         | BDG2      | HSC-CQR recency             | 652 | 0.2     | 9.2   | 13.1      | 68.4    | 28.2    | 28.2      | 8.9         | 43.1         | 1.338           | 1.483         | 0.600              | 1.770    | 2.127    | 2.840    | 3.058            | 1.3       | 15.4       | 68.2      | +0.4            | +0.1            | -0.3            | +1.5                    | -0.6                   | +0.6                 |
| robust:spikes2         | BDG2      | QShrink-CQR (cov)           | 652 | 0.4     | 10.1  | 14.4      | 71.5    | 33.2    | 33.2      | 8.6         | 43.4         | 1.338           | 1.485         | 0.598              | 1.770    | 2.126    | 2.839    | 3.056            | 1.3       | 15.4       | 68.2      | +0.4            | +0.1            | -0.3            | +1.5                    | -0.6                   | +0.7                 |
| robust:spikes2         | BDG2      | ACI-CQR (cov)               | 652 | 1.8     | 12.6  | 12.2      | 57.2    | 28.5    | 28.5      | 8.7         | 39.0         | 1.341           | 1.476         | 0.613              | 1.765    | 2.126    | 2.848    | 3.045            | 1.3       | 15.4       | 68.2      | +0.1            | +0.1            | -0.0            | +1.1                    | -0.4                   | +0.1                 |
| robust:spikes2         | BDG2      | CQR                         | 652 | 6.7     | 12.8  | 12.3      | 50.2    | 28.0    | 28.0      | 9.0         | 38.0         | 1.346           | 1.474         | 0.623              | 1.762    | 2.125    | 2.849    | 3.012            | 1.3       | 15.4       | 68.2      | +0.0            | +0.0            | +0.0            | +0.0                    | +0.0                   | +0.0                 |
| robust:spikes2         | BDG2      | TTSC (cumulative feedback)  | 652 | 0.4     | 7.7   | 14.2      | 72.7    | 23.3    | 23.3      | 9.5         | 49.2         | 1.354           | 1.477         | 0.615              | 1.766    | 2.122    | 2.836    | 2.984            | 1.3       | 15.4       | 68.2      | +0.2            | -0.1            | -0.5            | -0.9                    | +0.6                   | +0.2                 |
| robust:spikes2         | BDG2      | TTSC (uncapped)             | 652 | 0.0     | 6.8   | 9.8       | 56.6    | 11.2    | 11.2      | 8.6         | 45.0         | 1.417           | 1.805         | 0.680              | 1.932    | 2.279    | 2.972    | 3.954            | 1.3       | 15.4       | 68.2      | +9.6            | +7.3            | +4.3            | +31.3                   | +5.3                   | +22.4                |
| robust:spikes2         | BDG2      | TTSC (delay 1d)             | 652 | 0.5     | 9.7   | 14.1      | 72.0    | 29.4    | 29.4      | 9.1         | 47.1         | 1.361           | 1.486         | 0.630              | 1.770    | 2.126    | 2.837    | 2.986            | 1.3       | 15.4       | 68.2      | +0.5            | +0.1            | -0.4            | -0.9                    | +1.1                   | +0.8                 |
| robust:weak-forecaster | BDG2      | TTSC                        | 652 | 0.4     | 12.0  | 12.0      | 62.1    | 17.1    | 17.1      | 15.0        | 65.3         | 0.638           | 0.811         | 0.487              | 1.380    | 1.468    | 1.645    | 2.598            | 2.0       | 17.7       | 73.3      | +1.1            | -0.2            | -2.4            | -2.5                    | +5.5                   | +0.3                 |
| robust:weak-forecaster | BDG2      | HSC-CQR recency (capped)    | 652 | 0.6     | 15.5  | 18.5      | 82.0    | 41.8    | 41.8      | 16.6        | 69.0         | 0.609           | 0.785         | 0.449              | 1.365    | 1.458    | 1.643    | 2.595            | 2.0       | 17.7       | 73.3      | +0.1            | -0.9            | -2.5            | -2.6                    | +0.7                   | -3.0                 |
| robust:weak-forecaster | BDG2      | HSC-CQR recency             | 652 | 0.4     | 15.2  | 18.3      | 81.9    | 41.5    | 41.5      | 16.5        | 68.7         | 0.609           | 0.811         | 0.449              | 1.379    | 1.467    | 1.643    | 2.672            | 2.0       | 17.7       | 73.3      | +1.1            | -0.3            | -2.5            | +0.3                    | +0.7                   | +0.2                 |
| robust:weak-forecaster | BDG2      | QShrink-CQR (cov)           | 652 | 2.0     | 15.5  | 19.7      | 82.6    | 45.8    | 45.8      | 16.9        | 69.3         | 0.608           | 0.819         | 0.444              | 1.383    | 1.470    | 1.646    | 2.700            | 2.0       | 17.7       | 73.3      | +1.4            | -0.0            | -2.3            | +1.4                    | +0.5                   | +1.2                 |
| robust:weak-forecaster | BDG2      | ACI-CQR (cov)               | 652 | 5.9     | 19.3  | 18.8      | 73.7    | 49.0    | 49.0      | 17.3        | 65.3         | 0.604           | 0.808         | 0.444              | 1.372    | 1.470    | 1.664    | 2.701            | 2.0       | 17.7       | 73.3      | +0.6            | -0.1            | -1.3            | +1.4                    | -0.1                   | -0.2                 |
| robust:weak-forecaster | BDG2      | CQR                         | 652 | 20.0    | 19.4  | 23.8      | 64.5    | 48.2    | 48.2      | 18.7        | 60.2         | 0.605           | 0.809         | 0.441              | 1.364    | 1.471    | 1.685    | 2.664            | 2.0       | 17.7       | 73.3      | +0.0            | +0.0            | +0.0            | +0.0                    | +0.0                   | +0.0                 |
| robust:weak-forecaster | BDG2      | TTSC (cumulative feedback)  | 652 | 0.5     | 12.0  | 14.0      | 71.1    | 23.9    | 23.9      | 15.0        | 66.9         | 0.641           | 0.809         | 0.488              | 1.379    | 1.467    | 1.642    | 2.592            | 2.0       | 17.7       | 73.3      | +1.1            | -0.3            | -2.5            | -2.7                    | +5.9                   | -0.1                 |
| robust:weak-forecaster | BDG2      | TTSC (uncapped)             | 652 | 0.0     | 10.6  | 11.2      | 60.3    | 12.7    | 12.7      | 14.5        | 64.8         | 1.418           | 2.248         | 1.221              | 2.099    | 2.177    | 2.333    | 5.251            | 2.0       | 17.7       | 73.3      | +53.9           | +48.0           | +38.4           | +97.1                   | +134.5                 | +177.8               |
| robust:weak-forecaster | BDG2      | TTSC (delay 1d)             | 652 | 0.6     | 19.8  | 19.2      | 82.9    | 38.0    | 38.0      | 16.7        | 70.2         | 0.677           | 0.846         | 0.511              | 1.395    | 1.485    | 1.666    | 2.616            | 2.0       | 17.7       | 73.3      | +2.3            | +1.0            | -1.1            | -1.8                    | +12.0                  | +4.5                 |
| xds:BDG2->BDG2         | BDG2      | TTSC                        | 652 | 0.4     | 11.0  | 13.6      | 68.8    | 17.2    | 17.2      | 15.1        | 67.6         | 0.600           | 0.749         | 0.446              | 1.349    | 1.431    | 1.594    | 2.459            | 1.8       | 17.0       | 72.5      | +1.0            | -0.0            | -1.6            | -1.7                    | +2.2                   | +1.0                 |
| xds:BDG2->BDG2         | BDG2      | HSC-CQR recency (capped)    | 652 | 0.5     | 13.9  | 19.1      | 83.8    | 42.1    | 42.1      | 16.5        | 70.2         | 0.586           | 0.736         | 0.425              | 1.341    | 1.427    | 1.598    | 2.466            | 1.8       | 17.0       | 72.5      | +0.4            | -0.3            | -1.4            | -1.4                    | -0.1                   | -0.7                 |
| xds:BDG2->BDG2         | BDG2      | HSC-CQR recency             | 652 | 0.3     | 13.8  | 18.9      | 83.7    | 41.9    | 41.9      | 16.4        | 70.1         | 0.586           | 0.757         | 0.425              | 1.353    | 1.436    | 1.603    | 2.552            | 1.8       | 17.0       | 72.5      | +1.2            | +0.3            | -1.1            | +2.0                    | -0.1                   | +2.1                 |
| xds:BDG2->BDG2         | BDG2      | QShrink-CQR (cov)           | 652 | 0.5     | 14.9  | 19.6      | 84.0    | 47.0    | 47.0      | 16.6        | 71.8         | 0.586           | 0.757         | 0.421              | 1.352    | 1.436    | 1.602    | 2.551            | 1.8       | 17.0       | 72.5      | +1.2            | +0.3            | -1.1            | +2.0                    | -0.1                   | +2.2                 |
| xds:BDG2->BDG2         | BDG2      | ACI-CQR (cov)               | 652 | 2.9     | 19.3  | 19.4      | 78.8    | 49.4    | 49.4      | 17.4        | 69.8         | 0.585           | 0.758         | 0.414              | 1.349    | 1.439    | 1.620    | 2.593            | 1.8       | 17.0       | 72.5      | +0.9            | +0.6            | -0.0            | +3.7                    | -0.2                   | +2.2                 |
| xds:BDG2->BDG2         | BDG2      | CQR                         | 652 | 15.6    | 19.9  | 22.3      | 69.1    | 49.6    | 49.6      | 17.9        | 64.3         | 0.587           | 0.741         | 0.413              | 1.336    | 1.431    | 1.620    | 2.501            | 1.8       | 17.0       | 72.5      | +0.0            | +0.0            | +0.0            | +0.0                    | +0.0                   | +0.0                 |
| xds:BDG2->BDG2         | BDG2      | ACI (weekly-tuned)          | 652 | 0.4     | 14.8  | 15.2      | 76.9    | 27.7    | 27.7      | 15.5        | 69.6         | 0.598           | 0.744         | 0.439              | 1.346    | 1.430    | 1.599    | 2.469            | 1.8       | 17.0       | 72.5      | +0.7            | -0.0            | -1.3            | -1.2                    | +1.8                   | +0.3                 |
| xds:BDG2->BDG2         | BDG2      | Windowed ACI (weekly-tuned) | 652 | 2.0     | 16.8  | 14.3      | 60.8    | 24.1    | 24.1      | 15.7        | 63.2         | 0.595           | 0.743         | 0.435              | 1.344    | 1.430    | 1.603    | 2.473            | 1.8       | 17.0       | 72.5      | +0.6            | -0.1            | -1.1            | -1.1                    | +1.4                   | +0.3                 |
| xds:BDG2->BDG2         | BDG2      | TTSC (cumulative feedback)  | 652 | 0.4     | 11.0  | 15.1      | 75.4    | 23.7    | 23.7      | 14.8        | 67.7         | 0.606           | 0.751         | 0.452              | 1.351    | 1.432    | 1.595    | 2.462            | 1.8       | 17.0       | 72.5      | +1.1            | +0.1            | -1.6            | -1.5                    | +3.2                   | +1.4                 |
| xds:BDG2->BDG2         | BDG2      | TTSC (uncapped)             | 652 | 0.0     | 10.2  | 12.9      | 67.3    | 14.7    | 14.7      | 14.6        | 67.2         | 0.752           | 1.258         | 0.566              | 1.605    | 1.680    | 1.831    | 3.738            | 1.8       | 17.0       | 72.5      | +20.1           | +17.4           | +13.0           | +49.5                   | +28.2                  | +69.8                |
| xds:BDG2->BDG2         | BDG2      | TTSC (delay 1d)             | 652 | 0.4     | 18.5  | 19.0      | 83.3    | 34.2    | 34.2      | 16.0        | 71.2         | 0.618           | 0.766         | 0.460              | 1.357    | 1.440    | 1.606    | 2.474            | 1.8       | 17.0       | 72.5      | +1.5            | +0.6            | -0.9            | -1.1                    | +5.2                   | +3.3                 |
| xds:UCI->BDG2          | BDG2      | TTSC                        | 652 | 0.8     | 18.2  | 13.2      | 68.6    | 25.1    | 25.1      | 15.8        | 69.3         | 0.654           | 0.808         | 0.483              | 1.378    | 1.460    | 1.624    | 2.421            | 2.6       | 19.0       | 76.5      | +1.7            | -0.2            | -3.3            | -2.9                    | +2.2                   | -0.7                 |
| xds:UCI->BDG2          | BDG2      | HSC-CQR recency (capped)    | 652 | 1.9     | 24.5  | 18.4      | 83.5    | 50.2    | 50.2      | 16.0        | 70.3         | 0.630           | 0.787         | 0.450              | 1.366    | 1.450    | 1.618    | 2.418            | 2.6       | 19.0       | 76.5      | +0.9            | -0.9            | -3.7            | -3.0                    | -1.5                   | -3.2                 |
| xds:UCI->BDG2          | BDG2      | HSC-CQR recency             | 652 | 1.3     | 23.4  | 17.9      | 83.1    | 48.9    | 48.9      | 15.6        | 69.9         | 0.632           | 0.800         | 0.451              | 1.373    | 1.452    | 1.610    | 2.427            | 2.6       | 19.0       | 76.5      | +1.4            | -0.7            | -4.1            | -2.7                    | -1.2                   | -1.7                 |
| xds:UCI->BDG2          | BDG2      | QShrink-CQR (cov)           | 652 | 2.3     | 27.1  | 18.6      | 84.8    | 53.5    | 53.5      | 15.4        | 69.0         | 0.632           | 0.798         | 0.447              | 1.371    | 1.451    | 1.612    | 2.425            | 2.6       | 19.0       | 76.5      | +1.3            | -0.8            | -4.0            | -2.8                    | -1.3                   | -1.9                 |
| xds:UCI->BDG2          | BDG2      | ACI-CQR (cov)               | 652 | 9.0     | 40.1  | 22.5      | 88.3    | 60.5    | 60.5      | 18.4        | 71.6         | 0.634           | 0.825         | 0.427              | 1.377    | 1.465    | 1.642    | 2.510            | 2.6       | 19.0       | 76.5      | +1.7            | +0.2            | -2.2            | +0.6                    | -0.8                   | +1.5                 |
| xds:UCI->BDG2          | BDG2      | CQR                         | 652 | 40.0    | 42.0  | 35.9      | 83.1    | 68.8    | 68.8      | 24.3        | 72.6         | 0.640           | 0.813         | 0.403              | 1.354    | 1.463    | 1.679    | 2.494            | 2.6       | 19.0       | 76.5      | +0.0            | +0.0            | +0.0            | +0.0                    | +0.0                   | +0.0                 |
| xds:UCI->BDG2          | BDG2      | ACI (weekly-tuned)          | 652 | 2.3     | 20.6  | 14.5      | 73.5    | 28.9    | 28.9      | 16.1        | 71.0         | 0.662           | 0.806         | 0.476              | 1.375    | 1.460    | 1.630    | 2.430            | 2.6       | 19.0       | 76.5      | +1.6            | -0.2            | -2.9            | -2.5                    | +3.5                   | -0.8                 |
| xds:UCI->BDG2          | BDG2      | Windowed ACI (weekly-tuned) | 652 | 7.6     | 23.8  | 19.8      | 72.6    | 32.5    | 32.5      | 18.3        | 70.4         | 0.656           | 0.813         | 0.465              | 1.373    | 1.463    | 1.642    | 2.440            | 2.6       | 19.0       | 76.5      | +1.4            | +0.0            | -2.2            | -2.2                    | +2.5                   | -0.1                 |
| xds:UCI->BDG2          | BDG2      | TTSC (cumulative feedback)  | 652 | 0.8     | 18.2  | 14.7      | 74.7    | 30.4    | 30.4      | 16.3        | 72.8         | 0.657           | 0.806         | 0.483              | 1.378    | 1.460    | 1.624    | 2.422            | 2.6       | 19.0       | 76.5      | +1.8            | -0.2            | -3.3            | -2.9                    | +2.7                   | -0.8                 |
| xds:UCI->BDG2          | BDG2      | TTSC (uncapped)             | 652 | 0.0     | 14.1  | 11.1      | 63.3    | 15.4    | 15.4      | 14.6        | 67.7         | 1.504           | 4.905         | 1.246              | 3.429    | 3.500    | 3.642    | 11.931           | 2.6       | 19.0       | 76.5      | +153.2          | +139.3          | +116.8          | +378.4                  | +135.2                 | +503.1               |
| xds:UCI->BDG2          | BDG2      | TTSC (delay 1d)             | 652 | 1.8     | 27.4  | 20.8      | 86.8    | 48.9    | 48.9      | 17.6        | 73.5         | 0.693           | 0.836         | 0.502              | 1.390    | 1.474    | 1.643    | 2.430            | 2.6       | 19.0       | 76.5      | +2.6            | +0.8            | -2.2            | -2.6                    | +8.4                   | +2.8                 |
| xds:BDG2->UCI          | UCI       | TTSC                        | 211 | 0.0     | 4.9   | 7.5       | 44.3    | 7.2     | 7.2       | 11.7        | 57.8         | 0.446           | 0.575         | 0.344              | 1.261    | 1.312    | 1.415    | 1.985            | 0.6       | 12.9       | 60.5      | +0.4            | +0.2            | -0.1            | -0.3                    | +2.1                   | +1.7                 |
| xds:BDG2->UCI          | UCI       | HSC-CQR recency (capped)    | 211 | 0.0     | 8.2   | 13.5      | 64.8    | 18.7    | 18.7      | 13.2        | 62.5         | 0.439           | 0.567         | 0.329              | 1.257    | 1.310    | 1.416    | 1.987            | 0.6       | 12.9       | 60.5      | +0.1            | +0.1            | -0.0            | -0.2                    | +0.3                   | +0.3                 |
| xds:BDG2->UCI          | UCI       | HSC-CQR recency             | 211 | 0.0     | 8.2   | 13.5      | 64.8    | 18.7    | 18.7      | 13.1        | 62.3         | 0.439           | 0.574         | 0.329              | 1.261    | 1.313    | 1.418    | 2.019            | 0.6       | 12.9       | 60.5      | +0.4            | +0.3            | +0.1            | +1.4                    | +0.3                   | +1.6                 |
| xds:BDG2->UCI          | UCI       | QShrink-CQR (cov)           | 211 | 0.5     | 8.3   | 14.3      | 66.7    | 21.9    | 21.9      | 13.7        | 63.8         | 0.437           | 0.570         | 0.328              | 1.259    | 1.311    | 1.417    | 2.007            | 0.6       | 12.9       | 60.5      | +0.3            | +0.2            | +0.1            | +0.8                    | -0.0                   | +0.8                 |
| xds:BDG2->UCI          | UCI       | ACI-CQR (cov)               | 211 | 1.1     | 11.4  | 12.5      | 63.0    | 19.5    | 19.5      | 12.2        | 57.0         | 0.437           | 0.564         | 0.334              | 1.255    | 1.309    | 1.416    | 1.988            | 0.6       | 12.9       | 60.5      | -0.0            | -0.0            | -0.0            | -0.2                    | -0.0                   | -0.3                 |
| xds:BDG2->UCI          | UCI       | CQR                         | 211 | 3.6     | 12.8  | 12.1      | 51.6    | 21.2    | 21.2      | 11.4        | 52.4         | 0.437           | 0.565         | 0.340              | 1.255    | 1.309    | 1.416    | 1.991            | 0.6       | 12.9       | 60.5      | +0.0            | +0.0            | +0.0            | +0.0                    | +0.0                   | +0.0                 |
| xds:BDG2->UCI          | UCI       | ACI (weekly-tuned)          | 211 | 0.0     | 7.2   | 9.9       | 57.7    | 9.2     | 9.2       | 12.0        | 59.0         | 0.442           | 0.570         | 0.338              | 1.259    | 1.311    | 1.415    | 1.992            | 0.6       | 12.9       | 60.5      | +0.3            | +0.1            | -0.1            | +0.0                    | +1.1                   | +0.9                 |
| xds:BDG2->UCI          | UCI       | Windowed ACI (weekly-tuned) | 211 | 0.7     | 6.5   | 6.6       | 36.5    | 6.6     | 6.6       | 10.2        | 51.7         | 0.443           | 0.569         | 0.347              | 1.258    | 1.310    | 1.413    | 1.984            | 0.6       | 12.9       | 60.5      | +0.2            | +0.1            | -0.2            | -0.3                    | +1.2                   | +0.7                 |
| xds:BDG2->UCI          | UCI       | TTSC (cumulative feedback)  | 211 | 0.0     | 4.9   | 9.3       | 56.1    | 8.9     | 8.9       | 11.9        | 60.6         | 0.447           | 0.577         | 0.342              | 1.262    | 1.314    | 1.417    | 1.993            | 0.6       | 12.9       | 60.5      | +0.5            | +0.4            | +0.0            | +0.1                    | +2.1                   | +2.1                 |
| xds:BDG2->UCI          | UCI       | TTSC (uncapped)             | 211 | 0.0     | 4.9   | 7.3       | 43.7    | 6.5     | 6.5       | 11.4        | 57.7         | 0.453           | 0.761         | 0.351              | 1.354    | 1.403    | 1.503    | 2.733            | 0.6       | 12.9       | 60.5      | +7.8            | +7.2            | +6.1            | +37.2                   | +3.5                   | +34.6                |
| xds:BDG2->UCI          | UCI       | TTSC (delay 1d)             | 211 | 0.0     | 12.4  | 11.6      | 64.5    | 16.5    | 16.5      | 12.6        | 61.7         | 0.455           | 0.584         | 0.355              | 1.265    | 1.316    | 1.420    | 1.992            | 0.6       | 12.9       | 60.5      | +0.7            | +0.6            | +0.3            | +0.1                    | +4.1                   | +3.3                 |


**Table S26. Pseudo-count κ and feedback gain γ selected by leave-one-building-out, per run.**

| part                          | gamma   | kappa   | gamma_edge   |
|:------------------------------|:--------|:--------|:-------------|
| lso_BDG2_f0                   | 0.005   | 96.0    | False        |
| lso_BDG2_f1                   | 0.005   | 96.0    | False        |
| lso_BDG2_f2                   | 0.005   | 48.0    | False        |
| lso_BDG2_f3                   | 0.005   | 96.0    | False        |
| lso_BDG2_f4                   | 0.005   | 48.0    | False        |
| main_BDG2_s0_a0.05            | 0.003   | 24.0    | False        |
| main_BDG2_s0_a0.1             | 0.005   | 48.0    | False        |
| main_BDG2_s0_a0.2             | 0.0075  | 48.0    | False        |
| main_BDG2_s1_a0.05            | 0.003   | 24.0    | False        |
| main_BDG2_s1_a0.1             | 0.005   | 48.0    | False        |
| main_BDG2_s1_a0.2             | 0.0075  | 48.0    | False        |
| main_BDG2_s2_a0.05            | 0.005   | 48.0    | False        |
| main_BDG2_s2_a0.1             | 0.005   | 48.0    | False        |
| main_BDG2_s2_a0.2             | 0.0075  | 48.0    | False        |
| main_BDG2_s3_a0.05            | 0.005   | 336.0   | False        |
| main_BDG2_s3_a0.1             | 0.005   | 168.0   | False        |
| main_BDG2_s3_a0.2             | 0.01    | 48.0    | True         |
| main_BDG2_s4_a0.05            | 0.005   | 96.0    | False        |
| main_BDG2_s4_a0.1             | 0.005   | 96.0    | False        |
| main_BDG2_s4_a0.2             | 0.0075  | 48.0    | False        |
| main_UCI_s0_a0.05             | 0.005   | 24.0    | False        |
| main_UCI_s0_a0.1              | 0.005   | 24.0    | False        |
| main_UCI_s0_a0.2              | 0.01    | 24.0    | True         |
| main_UCI_s1_a0.05             | 0.0075  | 24.0    | False        |
| main_UCI_s1_a0.1              | 0.01    | 24.0    | True         |
| main_UCI_s1_a0.2              | 0.01    | 48.0    | True         |
| main_UCI_s2_a0.05             | 0.005   | 48.0    | False        |
| main_UCI_s2_a0.1              | 0.0075  | 48.0    | False        |
| main_UCI_s2_a0.2              | 0.01    | 24.0    | True         |
| main_UCI_s3_a0.05             | 0.005   | 24.0    | False        |
| main_UCI_s3_a0.1              | 0.0075  | 24.0    | False        |
| main_UCI_s3_a0.2              | 0.01    | 24.0    | True         |
| main_UCI_s4_a0.05             | 0.003   | 96.0    | False        |
| main_UCI_s4_a0.1              | 0.005   | 48.0    | False        |
| main_UCI_s4_a0.2              | 0.01    | 48.0    | True         |
| robust_BDG2_s0_cal10          | 0.005   | 24.0    | False        |
| robust_BDG2_s0_cal25          | 0.003   | 48.0    | False        |
| robust_BDG2_s0_cal50          | 0.003   | 48.0    | False        |
| robust_BDG2_s0_missing20      | 0.005   | 48.0    | False        |
| robust_BDG2_s0_missing40      | 0.005   | 48.0    | False        |
| robust_BDG2_s0_noise15        | 0.005   | 48.0    | False        |
| robust_BDG2_s0_noise5         | 0.005   | 48.0    | False        |
| robust_BDG2_s0_outage1-3d     | 0.005   | 48.0    | False        |
| robust_BDG2_s0_ramp+40        | 0.005   | 48.0    | False        |
| robust_BDG2_s0_shift+40       | 0.005   | 48.0    | False        |
| robust_BDG2_s0_shift+40@d3-14 | 0.005   | 48.0    | False        |
| robust_BDG2_s0_shift-40       | 0.005   | 48.0    | False        |
| robust_BDG2_s0_spikes2        | 0.005   | 48.0    | False        |
| robust_BDG2_s0_weak           | 0.0075  | 48.0    | False        |
| robust_BDG2_s1_cal10          | 0.005   | 24.0    | False        |
| robust_BDG2_s1_cal25          | 0.005   | 48.0    | False        |
| robust_BDG2_s1_cal50          | 0.005   | 48.0    | False        |
| robust_BDG2_s1_missing20      | 0.005   | 48.0    | False        |
| robust_BDG2_s1_missing40      | 0.005   | 48.0    | False        |
| robust_BDG2_s1_noise15        | 0.005   | 48.0    | False        |
| robust_BDG2_s1_noise5         | 0.005   | 48.0    | False        |
| robust_BDG2_s1_outage1-3d     | 0.005   | 48.0    | False        |
| robust_BDG2_s1_ramp+40        | 0.005   | 48.0    | False        |
| robust_BDG2_s1_shift+40       | 0.005   | 48.0    | False        |
| robust_BDG2_s1_shift+40@d3-14 | 0.005   | 48.0    | False        |
| robust_BDG2_s1_shift-40       | 0.005   | 48.0    | False        |
| robust_BDG2_s1_spikes2        | 0.005   | 48.0    | False        |
| robust_BDG2_s1_weak           | 0.005   | 48.0    | False        |
| robust_BDG2_s2_cal10          | 0.0075  | 96.0    | False        |
| robust_BDG2_s2_cal25          | 0.003   | 48.0    | False        |
| robust_BDG2_s2_cal50          | 0.005   | 48.0    | False        |
| robust_BDG2_s2_missing20      | 0.005   | 48.0    | False        |
| robust_BDG2_s2_missing40      | 0.005   | 48.0    | False        |
| robust_BDG2_s2_noise15        | 0.005   | 48.0    | False        |
| robust_BDG2_s2_noise5         | 0.005   | 48.0    | False        |
| robust_BDG2_s2_outage1-3d     | 0.005   | 48.0    | False        |
| robust_BDG2_s2_ramp+40        | 0.005   | 48.0    | False        |
| robust_BDG2_s2_shift+40       | 0.005   | 48.0    | False        |
| robust_BDG2_s2_shift+40@d3-14 | 0.005   | 48.0    | False        |
| robust_BDG2_s2_shift-40       | 0.005   | 48.0    | False        |
| robust_BDG2_s2_spikes2        | 0.005   | 48.0    | False        |
| robust_BDG2_s2_weak           | 0.0075  | 48.0    | False        |
| xds_BDG2toBDG2_s0             | 0.005   | 48.0    | False        |
| xds_BDG2toBDG2_s1             | 0.005   | 48.0    | False        |
| xds_BDG2toBDG2_s2             | 0.005   | 48.0    | False        |
| xds_BDG2toUCI_s0              | 0.005   | 48.0    | False        |
| xds_BDG2toUCI_s1              | 0.005   | 48.0    | False        |
| xds_BDG2toUCI_s2              | 0.005   | 48.0    | False        |
| xds_UCItoBDG2_s0              | 0.005   | 24.0    | False        |
| xds_UCItoBDG2_s1              | 0.01    | 24.0    | True         |
| xds_UCItoBDG2_s2              | 0.0075  | 48.0    | False        |


**Table S27. Single-timescale strategies: per-building reliability and sharpness (90 %).**

| Data   | Method                     | Under-cov. window (%)   | Under-cov. wk 1 (%)   | Under-cov. per wk 2–8 (%)   | Any wk < 0.80 (%)   | Rel. IS median   | Rel. IS mean   | Width ratio P99 / max   |
|:-------|:---------------------------|:------------------------|:----------------------|:----------------------------|:--------------------|:-----------------|:---------------|:------------------------|
| BDG2   | HSC-CQR recency            | 0.2                     | 16.6                  | 19.8                        | 43.9                | 0.559            | 0.746          | 1.43 / 6.5              |
| BDG2   | HSC-CQR recency (capped)   | 0.4                     | 16.8                  | 19.9                        | 44.0                | 0.559            | 0.726          | 1.36 / 1.5              |
| BDG2   | HSC-CQR recency (delay 1d) | 0.4                     | 18.5                  | 20.9                        | 50.5                | 0.564            | 0.750          | 1.43 / 6.7              |
| BDG2   | QShrink-CQR recency        | 0.6                     | 17.4                  | 19.2                        | 43.2                | 0.559            | 0.755          | 1.49 / 8.5              |
| BDG2   | QShrink-CQR (cov)          | 1.5                     | 16.5                  | 20.9                        | 49.7                | 0.561            | 0.752          | 1.45 / 8.8              |
| BDG2   | HSC-SSC-CQR                | 0.8                     | 14.7                  | 20.3                        | 48.0                | 0.563            | 0.897          | 1.65 / 87.9             |
| BDG2   | HSC-CQR simple (cov)       | 1.1                     | 18.4                  | 21.2                        | 50.4                | 0.560            | 0.733          | 1.38 / 3.9              |
| BDG2   | HSC-CQR fixed-κ            | 1.0                     | 19.0                  | 21.1                        | 50.7                | 0.560            | 0.730          | 1.35 / 3.4              |
| BDG2   | ACI-CQR (cov)              | 2.6                     | 20.9                  | 19.8                        | 48.5                | 0.557            | 0.752          | 1.82 / 14.6             |
| BDG2   | ACI-CQR                    | 4.8                     | 21.4                  | 20.8                        | 50.8                | 0.557            | 0.743          | 1.24 / 14.6             |
| BDG2   | Self-CQR recency           | 1.7                     | 34.2                  | 20.7                        | 50.0                | 0.567            | 0.797          | 1.69 / 26.4             |
| BDG2   | Self-CQR                   | 6.3                     | 34.8                  | 22.9                        | 57.1                | 0.566            | 0.799          | 1.78 / 31.0             |
| BDG2   | TQA-B-CQR                  | 15.0                    | 21.2                  | 22.8                        | 47.6                | 0.558            | 0.734          | 2.02 / 3.5              |
| BDG2   | GHCP-CQR                   | 14.3                    | 22.1                  | 22.6                        | 50.2                | 0.557            | 0.733          | 1.02 / 1.0              |
| BDG2   | CQR                        | 15.2                    | 22.0                  | 23.6                        | 51.2                | 0.557            | 0.733          | 1.00 / 1.0              |
| BDG2   | Oracle reference           | 1.9                     | 17.3                  | 17.3                        | –                   | –                | –              | –                       |
| UCI    | HSC-CQR recency            | 0.0                     | 7.0                   | 13.2                        | 21.4                | 0.364            | 0.542          | 1.46 / 2.5              |
| UCI    | HSC-CQR recency (capped)   | 0.1                     | 7.6                   | 13.4                        | 21.8                | 0.364            | 0.537          | 1.31 / 1.6              |
| UCI    | HSC-CQR recency (delay 1d) | 0.1                     | 9.5                   | 14.6                        | 27.5                | 0.366            | 0.544          | 1.47 / 2.6              |
| UCI    | QShrink-CQR recency        | 0.0                     | 8.4                   | 13.3                        | 20.9                | 0.365            | 0.542          | 1.53 / 2.7              |
| UCI    | QShrink-CQR (cov)          | 0.1                     | 7.3                   | 14.6                        | 24.2                | 0.364            | 0.540          | 1.46 / 2.2              |
| UCI    | HSC-SSC-CQR                | 0.1                     | 7.3                   | 13.8                        | 22.7                | 0.364            | 0.562          | 1.79 / 4.1              |
| UCI    | HSC-CQR simple (cov)       | 0.5                     | 10.0                  | 14.4                        | 25.6                | 0.364            | 0.539          | 1.40 / 2.0              |
| UCI    | HSC-CQR fixed-κ            | 0.5                     | 11.9                  | 13.9                        | 26.5                | 0.364            | 0.537          | 1.35 / 1.8              |
| UCI    | ACI-CQR (cov)              | 1.7                     | 14.5                  | 12.3                        | 21.5                | 0.363            | 0.544          | 1.57 / 3.0              |
| UCI    | ACI-CQR                    | 5.2                     | 15.0                  | 14.9                        | 28.3                | 0.362            | 0.539          | 1.17 / 3.0              |
| UCI    | Self-CQR recency           | 0.1                     | 21.8                  | 14.4                        | 26.4                | 0.368            | 0.550          | 1.69 / 2.9              |
| UCI    | Self-CQR                   | 1.5                     | 22.7                  | 16.1                        | 32.7                | 0.368            | 0.550          | 1.80 / 2.4              |
| UCI    | TQA-B-CQR                  | 10.5                    | 13.7                  | 17.6                        | 28.5                | 0.362            | 0.542          | 1.93 / 3.4              |
| UCI    | GHCP-CQR                   | 9.3                     | 14.5                  | 14.9                        | 26.9                | 0.363            | 0.542          | 1.05 / 1.1              |
| UCI    | CQR                        | 12.3                    | 15.2                  | 18.3                        | 31.8                | 0.362            | 0.542          | 1.00 / 1.0              |
| UCI    | Oracle reference           | 0.6                     | 12.8                  | 12.8                        | –                   | –                | –              | –                       |


**Table S28. Single-timescale strategies: stress tests on BDG2.**

| Condition                           | HSC-CQR recency   | QShrink-CQR (cov)   | ACI-CQR (cov)   | CQR   | Wk 1: layer / CQR   | Under-prot.: layer / CQR   |
|:------------------------------------|:------------------|:--------------------|:----------------|:------|:--------------------|:---------------------------|
| Meter noise 5 %                     | 0.0 ± 0.0         | 0.5                 | 4.1*            | 16.8* | 12.3 / 22.5         | 1.4 / 7.9                  |
| Meter noise 15 %                    | 0.0 ± 0.0         | 0.1                 | 5.7*            | 29.5* | 11.5 / 38.7         | 0.7 / 11.4                 |
| Spikes (2 % of hours)               | 0.2 ± 0.2         | 0.5                 | 2.1*            | 6.9*  | 11.3 / 14.6         | 1.4 / 2.9                  |
| Missing hours 20 %                  | 0.3 ± 0.6         | 1.1*                | 6.6*            | 15.0* | 20.0 / 25.5         | 2.4 / 6.8                  |
| Missing hours 40 %                  | 0.8 ± 0.5         | 1.6*                | 8.8*            | 15.3* | 21.5 / 27.4         | 2.0 / 6.3                  |
| Outages 1–3 days                    | 0.5 ± 0.5         | 2.2*                | 6.5*            | 18.4* | 18.7 / 23.1         | 2.2 / 8.2                  |
| Level shift +40 % (day 28)          | 0.4 ± 0.5         | 1.8*                | 6.5*            | 25.8* | 17.3 / 22.1         | 8.1 / 30.6                 |
| Level shift −40 % (day 28)          | 0.2 ± 0.4         | 2.1*                | 3.2*            | 21.0* | 17.3 / 22.1         | 0.4 / 1.9                  |
| Level shift +40 % (random day 3–14) | 0.1 ± 0.2         | 0.4                 | 4.9*            | 23.4* | 39.4 / 45.9         | 3.8 / 24.3                 |
| Ramp +40 % (days 14–42)             | 0.8 ± 0.7         | 2.1*                | 5.6*            | 26.8* | 18.4 / 23.5         | 22.4 / 38.3                |
| Calibration pool 10 %               | 0.2 ± 0.4         | 2.0*                | 0.7             | 14.5* | 18.0 / 20.4         | 2.5 / 7.1                  |
| Calibration pool 25 %               | 0.2 ± 0.4         | 1.2*                | 2.4*            | 16.1* | 17.3 / 23.8         | 2.1 / 7.2                  |
| Calibration pool 50 %               | 0.2 ± 0.4         | 1.2*                | 3.7*            | 15.8* | 17.2 / 22.0         | 2.1 / 7.4                  |
| Weak forecaster                     | 0.4 ± 0.4         | 2.2*                | 5.3*            | 20.2* | 17.6 / 21.7         | 3.2 / 12.0                 |


**Table S29. Single-timescale strategies: capacity-headroom cost.**

| Data   | Method               | Upper exceed. (%)   | Under-prot. (%)   | Cost Δ ρ_p=10 (%)   | Cost Δ ρ_p=20 (%)   | Cost Δ ρ_p=40 (%)   |
|:-------|:---------------------|:--------------------|:------------------|:--------------------|:--------------------|:--------------------|
| BDG2   | HSC-CQR recency      | 5.2 ± 0.1           | 2.3 ± 0.8         | +1.2 ± 1.0          | +0.3 ± 0.8          | -1.1 ± 1.0          |
| BDG2   | HSC-SSC-CQR          | 5.1 ± 0.1           | 2.1 ± 0.5         | +6.8 ± 9.8          | +5.4 ± 8.7          | +3.1 ± 7.1          |
| BDG2   | SSC-CQR              | 5.1 ± 0.2           | 5.2 ± 1.6         | +0.2 ± 0.1          | -0.1 ± 0.2          | -0.8 ± 0.4          |
| BDG2   | HSC-CQR simple (cov) | 5.2 ± 0.1           | 3.0 ± 0.7         | +0.6 ± 0.4          | -0.1 ± 0.4          | -1.4 ± 0.8          |
| BDG2   | HSC-CQR              | 5.4 ± 0.1           | 3.7 ± 0.5         | +0.1 ± 0.1          | -0.3 ± 0.1          | -1.0 ± 0.4          |
| BDG2   | QShrink-CQR (cov)    | 5.2 ± 0.1           | 2.7 ± 1.2         | +1.3 ± 1.2          | +0.5 ± 1.1          | -1.0 ± 1.3          |
| BDG2   | QShrink-CQR          | 5.2 ± 0.2           | 4.9 ± 2.5         | +0.3 ± 0.2          | -0.2 ± 0.3          | -0.9 ± 0.9          |
| BDG2   | Self-CQR             | 5.4 ± 0.1           | 2.9 ± 0.4         | +3.1 ± 2.3          | +2.0 ± 2.1          | +0.1 ± 2.0          |
| BDG2   | ACI-CQR              | 5.2 ± 0.2           | 4.8 ± 0.7         | +0.7 ± 0.8          | +0.3 ± 0.7          | -0.2 ± 0.7          |
| BDG2   | ACI-CQR (cov)        | 5.2 ± 0.2           | 4.0 ± 1.3         | +1.1 ± 1.1          | +0.6 ± 0.8          | -0.2 ± 0.6          |
| BDG2   | TQA-B-CQR            | 5.1 ± 0.2           | 6.6 ± 1.0         | +0.3 ± 0.1          | +0.1 ± 0.1          | -0.3 ± 0.3          |
| BDG2   | GHCP-CQR             | 5.2 ± 0.2           | 7.2 ± 1.0         | +0.0 ± 0.0          | -0.0 ± 0.0          | -0.1 ± 0.0          |
| BDG2   | CQR                  | 5.3 ± 0.2           | 7.7 ± 1.4         | +0.0 ± 0.0          | +0.0 ± 0.0          | +0.0 ± 0.0          |
| BDG2   | MLP-QR               | 6.1 ± 0.6           | 10.2 ± 4.8        | +0.1 ± 0.2          | +0.1 ± 0.4          | +0.2 ± 1.2          |
| BDG2   | MLP-Gauss            | 3.6 ± 0.5           | 4.6 ± 2.3         | +6.4 ± 3.6          | +5.0 ± 3.6          | +2.8 ± 3.8          |
| UCI    | HSC-CQR recency      | 5.0 ± 0.2           | 0.2 ± 0.5         | +0.4 ± 0.3          | -0.2 ± 0.3          | -1.1 ± 0.8          |
| UCI    | HSC-SSC-CQR          | 4.9 ± 0.2           | 0.4 ± 0.6         | +1.2 ± 1.6          | +0.6 ± 1.6          | -0.5 ± 1.8          |
| UCI    | SSC-CQR              | 4.4 ± 0.3           | 0.8 ± 0.5         | +0.4 ± 0.1          | -0.1 ± 0.1          | -1.1 ± 0.4          |
| UCI    | HSC-CQR simple (cov) | 5.0 ± 0.2           | 0.4 ± 0.6         | +0.3 ± 0.3          | -0.2 ± 0.3          | -0.9 ± 0.7          |
| UCI    | HSC-CQR              | 5.1 ± 0.2           | 1.3 ± 1.2         | -0.0 ± 0.1          | -0.2 ± 0.1          | -0.5 ± 0.4          |
| UCI    | QShrink-CQR (cov)    | 5.0 ± 0.2           | 0.4 ± 0.6         | +0.3 ± 0.3          | -0.2 ± 0.3          | -1.0 ± 0.9          |
| UCI    | QShrink-CQR          | 4.9 ± 0.2           | 0.6 ± 0.9         | +0.1 ± 0.1          | -0.2 ± 0.1          | -0.7 ± 0.6          |
| UCI    | Self-CQR             | 5.1 ± 0.2           | 0.6 ± 0.9         | +0.7 ± 0.4          | +0.1 ± 0.4          | -0.9 ± 1.0          |
| UCI    | ACI-CQR              | 4.9 ± 0.2           | 1.1 ± 0.7         | +0.1 ± 0.2          | -0.1 ± 0.1          | -0.4 ± 0.4          |
| UCI    | ACI-CQR (cov)        | 4.9 ± 0.2           | 0.6 ± 0.6         | +0.3 ± 0.5          | -0.0 ± 0.2          | -0.6 ± 0.7          |
| UCI    | TQA-B-CQR            | 4.9 ± 0.2           | 3.2 ± 1.3         | +0.1 ± 0.1          | +0.0 ± 0.1          | -0.1 ± 0.3          |
| UCI    | GHCP-CQR             | 4.6 ± 0.3           | 2.1 ± 1.5         | +0.1 ± 0.0          | +0.0 ± 0.0          | -0.2 ± 0.0          |
| UCI    | CQR                  | 4.9 ± 0.3           | 2.7 ± 1.8         | +0.0 ± 0.0          | +0.0 ± 0.0          | +0.0 ± 0.0          |
| UCI    | MLP-QR               | 5.1 ± 0.8           | 3.2 ± 2.5         | -0.6 ± 0.5          | -0.8 ± 1.6          | -1.0 ± 3.6          |
| UCI    | MLP-Gauss            | 5.1 ± 0.5           | 3.6 ± 1.2         | +0.7 ± 0.7          | +0.7 ± 0.8          | +0.7 ± 2.6          |


**Table S30. TTSC: sensitivity to the feedback window W (γ re-selected for each W; mean over five seeds, building × seed units) and share of building-days at the radius cap.**

| dataset   |   W |   gamma |   at_cap |    wk1 |   wk_late |   any80 |   rel_IS_median |
|:----------|----:|--------:|---------:|-------:|----------:|--------:|----------------:|
| BDG2      |   3 |  0.0065 |   0.0458 | 0.1187 |    0.1346 |  0.2196 |          0.5821 |
| BDG2      |   7 |  0.005  |   0.0408 | 0.116  |    0.1363 |  0.2025 |          0.5775 |
| BDG2      |  14 |  0.0046 |   0.0461 | 0.1166 |    0.1671 |  0.2848 |          0.5839 |
| BDG2      |  28 |  0.0042 |   0.0429 | 0.1173 |    0.1734 |  0.3172 |          0.5806 |
| UCI       |   3 |  0.008  |   0.0411 | 0.0737 |    0.0767 |  0.0589 |          0.3761 |
| UCI       |   7 |  0.007  |   0.0389 | 0.0716 |    0.0656 |  0.0484 |          0.3775 |
| UCI       |  14 |  0.0065 |   0.0418 | 0.0695 |    0.1008 |  0.1095 |          0.3805 |
| UCI       |  28 |  0.0061 |   0.0394 | 0.0737 |    0.1086 |  0.1137 |          0.3795 |


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
## Addendum A (2026-11-20, after the pilot evaluation) — written BEFORE any of the following was implemented or run

Context: the pilot evaluation (results/raw_results.csv) showed that (i) no shrinkage
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

