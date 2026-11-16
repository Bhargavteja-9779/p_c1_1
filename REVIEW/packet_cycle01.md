# Review packet — cycle 1
Repository root: /home/user/p_c1_1 (read-only for reviewers).

## 1. Manuscript (as built; all numbers filled from results files)

---
title: "Reliable day-ahead prediction intervals for newly metered buildings: a building-level comparison of conformal calibration strategies"
---

**Authors:** [Author 1]^a,\*^, [Author 2]^b^

^a^ [Department, Institution, City, Country] · ^b^ [Department, Institution, City, Country]

\* Corresponding author. E-mail: [corresponding.author@institution]

# Highlights

- Day-ahead load interval reliability is assessed per newly metered building
- Pooled conformal calibration leaves many new buildings clearly under-covered
- Calibration strategies incl. ACI, TQA and GHCP-style pooling are compared
- Shrinking pooled scores toward each building's own errors is the most reliable
- One pseudo-count suffices; similarity and onboarding-stage priors add nothing

# Abstract

Demand response, flexibility bidding and measurement-and-verification need day-ahead prediction intervals for individual buildings, often from the first days after a building is metered. Interval methods are usually judged by coverage pooled over many buildings, which can hide buildings whose intervals are systematically too narrow. We evaluate per-building interval reliability during onboarding under a pre-registered, building- and period-disjoint protocol on 842 buildings at 10 sites (Building Data Genome 2) and 315 Portuguese electricity clients, with five seeds, unseen sites, cross-country transfer and stress tests. Using one global forecaster, we compare pooled split conformal prediction, conformalised quantile regression (CQR), group-wise, self-only, adaptive (ACI), temporal-quantile-adjustment and hierarchical calibration, quantile shrinkage, and a pseudo-count shrinkage of the nonconformity-score distribution towards each building's own accumulating scores, with the pseudo-count selected by leave-one-building-out. Pooled CQR left 18.7% (BDG2) and 9.5% (UCI) of new buildings with coverage more than five points below the 90 % target. Score-distribution shrinkage was the most reliable strategy, reducing these shares to 3.4% and 0.6% and the mean absolute coverage deviation from 0.038 to 0.018 (BDG2) at an essentially unchanged interval score; it also improved intervals from a neural quantile model. Similarity-weighted priors and onboarding-stage matching added nothing, leaving a one-parameter layer whose pseudo-count of one to two weeks of hourly scores costs 0.437 ms per building-day.

**Keywords:** probabilistic load forecasting; conformal prediction; cold start; building energy; prediction intervals; empirical Bayes


# 1. Introduction

Buildings account for a large share of electricity demand, and their flexible loads are increasingly used for grid services, demand response and on-site renewable integration [1]. Most of these applications need more than a point forecast. Demand-response baselines, day-ahead flexibility bids, measurement-and-verification and anomaly alarms all act on a statement of the form "tomorrow's hourly load of *this* building will lie between $L$ and $U$ with probability $1-\alpha$". Probabilistic load forecasting has therefore become a central topic in energy forecasting [2,3], and recent work, including several studies in this journal, has developed increasingly expressive probabilistic models for loads, renewables and multi-energy systems [4–6].

A practical difficulty is that interval forecasts are most needed when a building has just been connected to a monitoring, aggregation or demand-response platform — exactly when the least building-specific data exist. Data-driven building forecasting traditionally relies on months to years of history per building [7]. Transfer learning, federated learning and global or pretrained models now provide useful *point* forecasts for buildings with little history [8–12], and large pretrained models report zero-shot probabilistic forecasts for unseen buildings [13]. Whether the *intervals* attached to such forecasts are reliable for each new building, and how quickly they become reliable, has received little attention: a recent cross-building study reports that split-conformal intervals under-cover on average when transferred to unseen buildings and recommends recalibration before deployment [14], but it evaluates pooled coverage and does not study how a new building's own data should enter the calibration.

Conformal prediction offers distribution-free calibration of intervals around any forecaster [15–17] and is increasingly used in energy forecasting [18,19]. Its standard guarantee is *marginal*: averaged over exchangeable test points, coverage is at least $1-\alpha$. For a fleet of newly metered buildings, a marginal guarantee is compatible with a situation that operators would consider unacceptable — intervals that are far too narrow for volatile buildings and needlessly wide for regular ones, while the pooled coverage looks perfect. Several families of remedies exist in the statistics and machine-learning literature: group-wise (Mondrian) calibration [15]; calibration on the unit's own past errors; online adjustment of the miscoverage level, such as adaptive conformal inference [20,21] and temporal quantile adjustment for panels of time series [22]; hierarchical conformal prediction for new groups with few observations [23–25]; and empirical-Bayes or credibility-type *shrinkage* of a unit's calibration towards a pooled one, which has recently been proposed for sites in federated medical imaging [26], for survey subgroups [27], as a Bayesian regularisation in online conformal prediction [28], and as a donor–local mixture for newly commissioned solar-irradiance stations [29]. These methods have been developed under different assumptions and evaluated on different problems; which of them makes day-ahead load intervals reliable for each newly metered building, from which day onwards and at what cost in sharpness, is not known.

This paper answers that question for building loads. Our contributions are:

1. **Problem and evaluation protocol.** We formalise *per-building interval reliability during onboarding* — coverage of each new building over its first weeks, the dispersion of coverage across buildings, the share of clearly under-covered buildings and the evolution with the number of days since metering started — and evaluate it under a pre-registered, strictly building- and period-disjoint protocol on two public datasets with 842 buildings and 315 clients, including leave-site-out and cross-country transfer and stress tests.
2. **A head-to-head comparison of calibration strategies.** Under one protocol, forecaster and score, we compare pooled split conformal and CQR, Mondrian calibration, self-only calibration, adaptive conformal inference, temporal quantile adjustment (TQA-B), a GHCP-style hierarchical pooling, quantile-level shrinkage ("regularised Mondrian"), and pseudo-count shrinkage of the score distribution — together with direct quantile regression and deep probabilistic baselines.
3. **Design evidence for the shrinkage layer.** We study a closed-form pseudo-count shrinkage of the score distribution — referred to as hierarchical shrinkage conformal (HSC) calibration — whose pseudo-count is selected by leave-one-building-out on calibration buildings, and we test whether two building-specific refinements (a similarity-localised population prior and onboarding-stage matching) add value. We find that the shrinkage itself is the active ingredient and that the refinements are unnecessary, which yields a one-parameter layer that can be placed on top of any interval forecaster.

All code, data instructions and machine-generated results are released. The remainder of the paper reviews related work (Section 2), presents the calibration layer (Section 3) and the experimental setup (Section 4), reports results (Section 5) and discusses implications and limitations (Sections 6 and 7).


# 2. Related work

## 2.1 Probabilistic load forecasting for buildings

Probabilistic load forecasting is commonly approached through quantile regression, parametric likelihood models or ensembles, and evaluated with the pinball loss, the continuous ranked probability score, or interval coverage and width [2,3,30]. For individual consumers, quantile neural networks [31] and global autoregressive likelihood models [32] learn across many series. Recent studies in this journal developed theory-guided and adaptive deep models for district loads [11,33], attentive quantile temporal convolutional networks for multi-energy loads [4], data-driven city-scale demand models [34], and probabilistic forecasting for solar and co-located wind–PV generation [5,6]. Conformal prediction is increasingly used as a model-agnostic calibration layer in this domain, for example with adaptive conformal inference for short-term load [18], online conformal prediction for power-load intervals [35] or context-weighted calibration for renewable forecasts [19]. These works assess reliability with *pooled* metrics over a site, a system or a test period, typically for systems with long histories; how reliability is distributed across many individual buildings, and how it evolves during the first weeks of data, has not been their object. An early comparison of interval methods across electricity-load profiles already noted that interval reliability differs between profiles [36].

## 2.2 Forecasting with little building-specific data

Cold-start building forecasting has mainly been studied as transfer learning. Seasonal and trend adjustment allows models from data-rich buildings to be reused [8], fine-tuning pretrained networks helps when only weeks of target data exist [9], a review of 77 studies identifies load prediction as the main application of transfer learning in smart buildings [10], and federated transfer learning reaches warm-start accuracy after a few weeks of local data [12]. Large-scale pretraining on simulated buildings enables zero-shot forecasting, with probabilistic outputs, for unseen real buildings including BDG2 [13]. The BDG2 dataset [37] and the ASHRAE Great Energy Predictor III competition [38] established it as a benchmark for meter-level forecasting. A recent cross-building evaluation found split-conformal intervals to under-cover unseen buildings on average [14]. The emphasis of this line of work is point accuracy or aggregate interval scores; our study is complementary and concerns the calibration layer and its per-building reliability.

## 2.3 Conformal prediction across units and over time

Split conformal prediction [15,16,39] and conformalised quantile regression (CQR) [40] provide finite-sample marginal coverage under exchangeability. For time series, exchangeability fails: adaptive conformal inference (ACI) [20] and its aggregated variants [21] adjust the miscoverage level online, and ensemble or weighted methods bound the coverage gap under weak dependence or distribution drift [41–43]. For *panels* of time series, Lin et al. distinguish cross-sectional from longitudinal (per-series) coverage, show that distribution-free longitudinal validity is impossible in general [44], and propose temporal quantile adjustment (TQA), which queries a series-specific quantile of the cross-sectional score distribution based on the series' own past errors and evaluates the coverage of the least-covered 10 % of series [22]; residual quantile regression with unit effects targets the same goal [45]. Group- or unit-level validity is harder still. Mondrian conformal prediction [15] requires enough calibration data in every group; conditional calibration over a function class gives guarantees for pre-specified groups [46]; clustered conformal prediction pools groups with similar score distributions [47]; few-shot conformal prediction meta-learns from auxiliary tasks [48]; and personalised or federated methods weight other agents' scores [49]. For hierarchical data, Dunn et al. [23] and Lee et al. [24] obtain marginal coverage for a new group, and generalised hierarchical conformal prediction (GHCP) uses a new group's first few observations together with reference groups while retaining a finite-sample guarantee, by giving the new group the weight of a single reference group [25]. Small-area conformal prediction borrows strength through the conformity score instead [50], and synthetic or auxiliary scores can augment scarce calibration data with guarantees [51].

Closest to the calibration layer studied here are shrinkage estimators that mix a unit's own calibration with a pooled one through a weight $n/(n+n_0)$ — the classical credibility form [52]: risk-curve shrinkage for sites in federated conformal risk control [26], a "regularised Mondrian" that shrinks group-wise quantile thresholds towards the global one [27], a Dirichlet-process-type prior regularisation of the empirical score distribution in online conformal prediction [28,53], and a donor–local mixture with a fixed pseudo-count for newly commissioned solar-irradiance stations, released as an analysis-code record together with pooled, distance-weighted and delayed-feedback ACI calibration strategies [29]. The pseudo-count mixture we use is therefore not new as a mechanism. What has been missing is evidence on *which* of these strategies makes day-ahead **load** intervals reliable for each newly metered building — a setting with a large, heterogeneous population of units, a forecaster whose accuracy itself improves with the history length, and a need for calibration from the first day. We compare the strategies directly, select the pseudo-count by leave-one-building-out rather than fixing it, test the value of building similarity and onboarding-stage information, and evaluate the full distribution of per-building coverage under stress and transfer.


# 3. Method

## 3.1 Problem setting and notation

Let $y_{b,t,j}\ge 0$ denote the metered electricity use (kWh) of building $b$ on day $t$ and hour $j\in\{0,\dots,23\}$. Building $b$ is metered from day $t_{0,b}$ onward. At the end of day $t_{0,b}+h-1$, after $h$ days of the building's own history have been observed, a day-ahead forecast is issued for the 24 hours of day $t=t_{0,b}+h$; we call $h$ the *onboarding stage*. For a miscoverage level $\alpha$ (main analysis: $\alpha=0.1$), the goal is an interval $C_{b,h,j}=[L_{b,h,j},U_{b,h,j}]$ such that, **for every individual building**, the share of hours with $y_{b,t,j}\in C_{b,h,j}$ is close to $1-\alpha$ from the first days after metering starts, while the intervals remain as narrow as possible. The empirical target is therefore the distribution of per-building coverage across buildings, not only its mean.

Three disjoint sets of buildings are available (Section 4): *training* buildings for the global forecaster, *calibration* buildings whose (simulated) onboarding windows provide nonconformity scores, and *target* buildings, which are metered in a later period and on which all methods are evaluated.

## 3.2 Scale-normalised global forecaster

Buildings differ in mean load by four orders of magnitude (Fig. 2). Every load-derived quantity is therefore expressed relative to the scale

$$
s_{b,h}=\frac{1}{24\,m_h}\sum_{k=1}^{m_h}\sum_{j=0}^{23} y_{b,\,t-k,\,j},\qquad m_h=\min(h,7),\qquad\qquad (1)
$$

which uses only the last $m_h$ observed days. A single model $f$ is trained on the training buildings to predict $y_{b,t,j}/s_{b,h}$ from calendar variables, the normalised loads of the previous 1, 2, 7 and 14 days (missing if $h$ is smaller), normalised daily statistics and hour-of-day/day-type profiles computed over at most the last 28 observed days, the day-to-day variability of the normalised profile, the history length $\min(h,28)$, and, for BDG2, outdoor air temperature (Table 1). During training, the history length of every sample is drawn uniformly from $\{1,\dots,28\}$ and all features are masked accordingly, so the model learns to forecast from short histories. The point forecast is $\hat y_{b,t,j}=s_{b,h}\,f(\mathbf x_{b,t,j})$; quantile models $f^{\mathrm{lo}},f^{\mathrm{hi}}$ (levels $\alpha/2$ and $1-\alpha/2$) are trained in the same way with the pinball loss [54].

**Table 1.** Input features of the global forecasters (identical for LightGBM and MLP models).

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


## 3.3 Nonconformity scores

We use two normalised scores: the absolute residual and the conformalised-quantile-regression (CQR) score [40]:

$$
e^{\mathrm{abs}}_{b,h,j}=\frac{|y_{b,t,j}-\hat y_{b,t,j}|}{s_{b,h}},\qquad
e^{\mathrm{cqr}}_{b,h,j}=\frac{\max\{\hat y^{\mathrm{lo}}_{b,t,j}-y_{b,t,j},\; y_{b,t,j}-\hat y^{\mathrm{hi}}_{b,t,j}\}}{s_{b,h}} .\qquad\qquad (2)
$$

Given a radius $q_{b,h}$ (in units of $s_{b,h}$), the interval is

$$
C_{b,h,j}=\big[\hat y^{\mathrm{lo}}_{b,t,j}-q_{b,h}\,s_{b,h},\;\hat y^{\mathrm{hi}}_{b,t,j}+q_{b,h}\,s_{b,h}\big],\qquad\qquad (3)
$$

with $\hat y^{\mathrm{lo}}=\hat y^{\mathrm{hi}}=\hat y$ for the absolute score. Division by $s_{b,h}$ is what makes scores from buildings of different size comparable and therefore poolable.

## 3.4 Hierarchical shrinkage conformal calibration (HSC)

Fig. 1 summarises the calibration layer.

![**Fig. 1.** Calibration layer for newly metered buildings. A global forecaster is trained on scale-normalised loads of training buildings; calibration buildings provide nonconformity scores per onboarding stage; for a new building, a population prior (optionally stage-matched and similarity-localised) is shrunk toward the building's own accumulating scores with pseudo-count κ; κ and K are chosen by leave-one-building-out on calibration buildings only.](figures/Fig1_method.png){width=16.5cm}


Split conformal prediction [15,16] would set $q$ to the $\lceil(1-\alpha)(N+1)\rceil$-th smallest of $N$ pooled calibration scores. This gives coverage that is valid on average over exchangeable test points. It cannot adapt to an individual building whose errors are systematically larger or smaller than average, which is precisely the situation of a building that has just been metered. HSC combines three elements.

**(i) Onboarding-stage matching.** Forecast errors depend on how much history is available. Calibration scores are therefore grouped into stage bins $\mathcal B\in\{\{1\},\{2\},\{3\},\{4..6\},\{7..13\},\{14..27\},\{28..56\}\}$, and a forecast at stage $h$ is calibrated with scores from the bin $\mathcal B(h)$ containing $h$.

**(ii) Similarity-localised population prior.** From its most recent $\min(h,28)$ observed days, each building is summarised by a descriptor $\mathbf z_{b,h}$: its mean daily load profile divided by its mean load (24 values), the mean absolute day-to-day change of that normalised profile, and the logarithm of the mean load. These quantities are computed in the same way for calibration buildings at the same stage. With $\mathcal N_K(b,h)$ the $K$ calibration buildings closest to $\mathbf z_{b,h}$ (Euclidean distance after standardisation), the prior score distribution is

$$
F^{\mathrm{prior}}_{b,h}(e)=\frac{1}{K}\sum_{c\in\mathcal N_K(b,h)}\hat F_{c,\mathcal B(h)}(e),\qquad\qquad (4)
$$

where $\hat F_{c,\mathcal B}$ is the empirical distribution function of the scores of calibration building $c$ in stage bin $\mathcal B$. Buildings without any valid score in $\mathcal B$ are left out of the average, and buildings whose descriptor is undefined (no valid data in the descriptor window) are never selected as neighbours. With $K$ equal to the number of calibration buildings, the prior is the unweighted (building-weighted) population average.

**(iii) Shrinkage toward the building's own scores.** By the time the stage-$h$ forecast is issued, the building's own scores from stages $1,\dots,h-1$ have been observed: $n_{b,h}=24(h-1)$ values $e_{b,1},\dots,e_{b,n_{b,h}}$ (fewer if data are missing). HSC uses the mixture distribution

$$
\tilde F_{b,h}(e)=\frac{\kappa\,F^{\mathrm{prior}}_{b,h}(e)+\sum_{i=1}^{n_{b,h}}\mathbb 1\{e_{b,i}\le e\}}{\kappa+n_{b,h}+1},\qquad
q_{b,h}=\inf\{e:\tilde F_{b,h}(e)\ge 1-\alpha\},\qquad\qquad (5)
$$

where the "+1" in the denominator is a point mass at $+\infty$ that represents the not-yet-observed test score, as in (weighted) split conformal prediction [43]. The building's own scores thus receive the weight $n_{b,h}/(\kappa+n_{b,h}+1)$, the classical credibility (empirical-Bayes) form [52] that has recently also been used to shrink site- or group-specific conformal calibration towards a pooled one [26,27] and, with a fixed pseudo-count, to mix donor and local scores for new solar stations [29]. Equation (5) is the posterior mean of the building's score distribution under a Dirichlet-process prior with base measure $F^{\mathrm{prior}}_{b,h}$ and concentration $\kappa$ [55], with the test point appended; the same prior-regularised form has been analysed for online conformal prediction with an uninformative base measure [28]. The pseudo-count $\kappa$ (in hours of scores) has a direct interpretation: after $\kappa/24$ days, the building's own errors carry as much weight as the population prior. Two limits recover familiar methods. $\kappa\to\infty$ gives the (localised, stage-matched) population split-conformal quantile, with the usual finite-sample correction applied in that case. $\kappa=0$ gives split conformal prediction on the building's own past scores, which is undefined (infinite) until enough own scores exist. HSC interpolates between the two as data accumulate.

**Selection of $\kappa$ and $K$.** Both are selected on the calibration buildings only, by leave-one-building-out. Each calibration building in turn plays the role of a new building, with the prior built from the remaining calibration buildings. The pair minimising the interval score of Eq. (6) — computed per hour, divided by the scale $s_{b,h}$ and averaged over all calibration building-hours of all stages — is chosen from $\kappa\in\{0,24,48,96,168,336,672,1344,\infty\}$ and $K\in\{10,25,50,100,\text{all}\}$. Target buildings are never used for any choice.

**Computation.** Score distributions are stored as cumulative counts on a fixed grid of 4000 asinh-spaced points between $-10$ and $500$ (in units of $s$; relative spacing ≈ 0.5 %). Mixture quantiles in Eq. (5) then reduce to a vectorised search; the grid quantile is rounded upwards (conservatively) for all methods alike, and a quantile above the grid range is capped at $500\,s_{b,h}$ (a conservative stand-in for an unbounded radius). Whether an own-score quantile exists ($\lceil(1-\alpha)(n+1)\rceil\le n$) is decided from the number of own scores. The calibration store holds one cumulative-count vector per calibration building and stage bin, plus the descriptors.

**Validity.** For a fixed $\kappa\in(0,\infty)$, Eq. (5) does not inherit the finite-sample marginal guarantee of split conformal prediction: neither the target's own past scores nor the calibration scores are exchangeable with its future scores, because the forecast quality changes with $h$ and load is autocorrelated. HSC should therefore be read as a principled, tunable interpolation between two conformal limits. Its reliability is assessed empirically below, including under distribution shift, rather than claimed theoretically.


# 4. Experimental setup

## 4.1 Data

**BDG2.** The Building Data Genome Project 2 [37] provides two years (2016–2017) of hourly meter data from non-residential buildings on university and public campuses in North America and Europe, together with site weather and building metadata. It is the dataset of the ASHRAE Great Energy Predictor III competition [38]. We use the cleaned electricity meters, site air temperature and the primary-space-usage attribute.

**UCI.** The ElectricityLoadDiagrams20112014 dataset [56] contains 15-min consumption of 370 Portuguese electricity clients (2011–2014). We aggregate it to hourly energy and use 2012–2014, because most clients have no data in 2011. It has no weather or metadata and represents a different country, customer mix and metering infrastructure. We use it to test generality and transfer.

**Quality rules** (applied identically to all methods and fixed before the main experiments): runs of at least 24 identical consecutive readings (meter outage or stuck meter) are treated as missing; gaps of at most 6 h are linearly interpolated; a building is retained if at most 5 % of its hours are missing in every period used and its mean load is at least 1 kWh/h. This leaves **842 BDG2 buildings at 10 sites** and **315 UCI clients** (Fig. 2). Training rows whose normalised target exceeds 20 (meter restarts after near-zero history) are excluded from model fitting only.

![**Fig. 2.** Data after the quality filter: (a) primary space usage of the BDG2 buildings; (b) distribution of mean hourly load of BDG2 buildings and UCI clients (log scale).](figures/Fig2_data.png){width=16.5cm}

## 4.2 Protocols and leakage control

*Random-building protocol (main).* For each of five pre-specified seeds, buildings are randomly partitioned into training (50 %, of which one tenth is held out as building-disjoint validation data for early stopping), calibration (20 %) and target (30 %) sets. The forecaster and all calibration scores use only the training period (BDG2: 2016; UCI: 2012–2013). Each calibration building is "onboarded" at a random date in the training period. Each target building is onboarded at a random date in the later period (BDG2: 2017; UCI: 2014), drawn among windows with at least 80 % valid hours. Every building is followed for 56 day-ahead forecasts ($h=1,\dots,56$). Features at stage $h$ use only the $h$ days after $t_{0,b}$ (verified by unit tests that perturb all data outside this window). Target buildings, their period and their data are therefore never seen by the forecaster, the calibration scores, or any hyper-parameter selection.

*Leave-site-out (BDG2).* The 10 sites are grouped into five folds of similar size. All buildings of a fold are targets; the remaining buildings are split 70/30 into training and calibration sets. This tests transfer to unseen campuses, climates and operators.

*Cross-dataset.* Models and calibration scores from one dataset are applied to the target buildings of the other (BDG2→UCI and UCI→BDG2), without weather features, which UCI lacks. A BDG2→BDG2 run without weather serves as the within-dataset reference (three seeds each).

## 4.3 Compared methods

All conformal-type methods share the same forecaster, scores, grid and stage bins; they differ only in how the radius $q_{b,h}$ is obtained.

* **Naive+SCP** (classical): seasonal-naive forecast (same hour one week earlier if $h\ge7$, else the previous day) with stage-matched split conformal intervals.
* **Raw-SCP**: split conformal prediction on unnormalised absolute residuals (kWh).
* **SCP**: split conformal on normalised absolute scores pooled over all stages [16].
* **SCP-stage**: as SCP, with stage-bin matching (the score-weighted analogue of HSC with $\kappa=\infty$, $K=$ all, whose prior weights buildings equally).
* **Mondrian-usage** (BDG2): SCP-stage computed separately per primary-usage class (classes with at least 10 calibration buildings), a group-conditional (Mondrian) variant [15].
* **Self-CP**: split conformal on the building's own past scores ($\kappa=0$), falling back to SCP-stage until enough own scores exist.
* **ACI** [20]: adaptive conformal inference on top of the SCP-stage distribution, $\alpha_{h+1}=\alpha_h+\gamma\sum_j(\alpha-\mathrm{err}_{h,j})$, with $\gamma$ chosen by leave-one-building-out on calibration buildings from $\{0,10^{-4},2\!\times\!10^{-4},5\!\times\!10^{-4},10^{-3},2\!\times\!10^{-3},5\!\times\!10^{-3},10^{-2}\}$ (the three smallest values were added after a code audit showed that the pre-registered grid's lower edge was selected in most runs; $\gamma=0$ recovers the pooled method). When $\alpha_h$ leaves $[0,1]$, the radius is set to the largest grid value ($\alpha_h\le 0$) or to the smallest observed score ($\alpha_h\ge1$, empty-set convention).
* **QR-LGBM**: direct LightGBM quantile regression [54,57].
* **CQR** [40]: QR-LGBM conformalised with stage-matched pooled CQR scores.
* **MLP-Gauss**: a global multilayer perceptron (256-256-128, ReLU) with a Gaussian output trained by negative log-likelihood, a deep probabilistic baseline in the spirit of DeepAR's likelihood training [32].
* **MLP-QR**: the same network trained with the pinball loss for the two quantiles [31].
* **Self-CQR** and **ACI-CQR**: self-only calibration and ACI applied to the CQR scores (same quantile models as CQR).
* **TQA-B-CQR** [22]: temporal quantile adjustment ("budgeting" variant) on the CQR scores. The building's exponentially decayed mean own score (decay 0.8 per day, normalised by the weight sum, days before the forecast only) is ranked among the calibration buildings' decayed means at the same stage; the rank $r=|\{j:\bar e_j<\bar e_b\}|/(N+1)$ is mapped to the queried level $1-a$ with $a=\alpha-\lambda g^B(r)$, $g^B(r)=C(r-(1-\alpha))$ for $r<1-\alpha$ and $r-(1-\alpha)$ otherwise, $C=\alpha^2/(1-\alpha)^2$, $\lambda\le1$ chosen per stage so that $a\ge0.01$, and the quantile is taken over the pooled scores together with a point at $+\infty$, as in the original method; the paper's TQA-E variant is an ACI-type update and is represented by ACI-CQR.
* **GHCP-CQR**: the calibration step of generalised hierarchical conformal prediction [25], adapted to our setting: with $M$ calibration buildings, every calibration building receives total weight $1/(M+1)$ spread over its scores (pooled over all onboarding stages, since GHCP has no notion of stages), and the new building receives the same group share, spread over its observed own scores and a point mass at $+\infty$ for its not-yet-observed scores. Deviations from the original: the surrogate group size is the median number of scores per calibration building (≈1344 in all runs) instead of a randomly drawn donor, and no observations are set aside to fit a local predictor, because our global forecaster already conditions on the building's own history (omitting this step most likely favours GHCP-CQR). GHCP's finite-sample guarantee relies on within-group exchangeability, which hourly loads violate.
* **QShrink-CQR** (regularised Mondrian [27]): quantile-level shrinkage $q=w\,q^{\mathrm{own}}+(1-w)\,q^{\mathrm{pool}}$ with $w=n_{b,h}/(n_{b,h}+\lambda)$, $q^{\mathrm{own}}$ the split-conformal quantile of the own scores (w = 0 while undefined) and $q^{\mathrm{pool}}$ the CQR radius; $\lambda$ is selected by leave-one-building-out from the same grid as $\kappa$, including $\lambda=0$ (own quantile whenever it exists) and $\lambda=\infty$ (pooled CQR radius).
* **HSC** and **HSC-CQR**: Eq. (5) with all three elements (stage matching, similarity prior, shrinkage) applied to absolute and CQR scores; **HSC simple** and **HSC-CQR simple**: the same with a uniform prior ($K$ = all) and without stage matching, i.e. a single pseudo-count shrinkage towards the pooled score distribution; **HSC-CQR fixed-κ**: HSC-CQR simple with the pseudo-count fixed at one week of hourly scores ($\kappa=168$) instead of being selected — a donor–local mixture with fixed pseudo-count as in [29].
* **CQR (MLP)** and **HSC-CQR (MLP)**: CQR and HSC-CQR simple on the quantiles of the MLP quantile model, to check that the calibration layer is not specific to LightGBM.

The neural networks use the same features (missing values set to zero with missingness indicators, standardised), Adam (learning rate $10^{-3}$, batch 4096), at most 12 epochs, and early stopping on the validation buildings (patience 3). LightGBM uses 63 leaves, learning rate 0.05, at least 200 samples per leaf, 0.8 feature and bagging fractions, L2 regularisation 1, and early stopping (50 rounds) on the validation buildings. These are conventional settings, applied identically to point and quantile models. No method was tuned on target buildings.

## 4.4 Metrics and statistical analysis

For target building $b$ with valid hourly observations over its 56-day window, we compute coverage $\mathrm{cov}_b$, relative width $\overline{U-L}/\bar y_b$, and the relative interval (Winkler) score [30,58]

$$
\mathrm{IS}_b=\frac{1}{\bar y_b}\,\overline{(U-L)+\tfrac{2}{\alpha}(L-y)_+ +\tfrac{2}{\alpha}(y-U)_+},\qquad\qquad (6)
$$

a proper score that rewards narrow intervals and penalises misses in proportion to their size. Across buildings we report the mean coverage; the **mean absolute coverage deviation** $\mathrm{MACD}=\mathrm{mean}_b|\mathrm{cov}_b-(1-\alpha)|$; the **under-covered share**, i.e. the share of buildings with $\mathrm{cov}_b<1-\alpha-0.05$; the 10th percentile of $\mathrm{cov}_b$; and the medians of relative width and $\mathrm{IS}_b$. The medians are used because a few buildings with erratic loads dominate means. Means are reported in the supplementary tables. Point accuracy is reported as CV(RMSE) [59].

The unit of statistical analysis is the target building. A building's metrics are averaged over the seeds in which it was a target, and HSC variants are compared with each baseline by two-sided Wilcoxon signed-rank tests [60] on paired per-building values of $\mathrm{IS}_b$ and $|\mathrm{cov}_b-(1-\alpha)|$. $p$-values are Holm-adjusted [61] within each family of comparisons. Effect sizes are matched-pairs rank-biserial correlations [62], positive when HSC is better. 95 % confidence intervals of the mean paired difference come from a cluster bootstrap over sites for BDG2 (buildings at a site share weather and operation) and over buildings for UCI (2000 resamples). Seed-level results are reported as mean ± standard deviation over seeds. All settings were fixed in a pre-registration file before any full experiment was run.


# 5. Results

## 5.1 Point accuracy and the reliability problem (RQ1)

The global LightGBM forecaster reaches a median CV(RMSE) of 0.136 on new BDG2 buildings over their first 56 forecast days (seasonal naive: 0.197; MLP: 0.137) and 0.089 on UCI clients (naive 0.120; MLP 0.087). The forecasters are therefore reasonable; the question is whether their intervals can be trusted building by building.

Tables 2 and 3 show that they cannot when calibration is pooled. Stage-matched split conformal prediction (SCP-stage) attains a mean per-building coverage of 0.881 on BDG2, close to the 0.90 target, yet 29.0% of the new buildings have coverage below 0.85 and the 10th percentile of per-building coverage is 0.700. Direct quantile regression under-covers on average (0.859); conformalising it (CQR) restores the mean (0.891) but leaves 18.7% of the buildings under-covered. Calibrating separately per usage type (Mondrian-usage, 28.5%) does not help, and the deep quantile model (MLP-QR, 20.6%) does not solve the problem either; the Gaussian MLP lowers under-coverage only by over-covering on average (0.924) with wider intervals (median relative width 0.451 vs 0.383 for CQR). The same pattern appears on UCI, where SCP-stage and CQR leave 20.2% and 9.5% of the clients under-covered. Fig. 3 shows the full distributions: pooled methods have long lower tails of buildings with 0.70–0.85 coverage.

**Table 2.** Per-building interval reliability and sharpness on BDG2 (random-building protocol, nominal 90 %, 5 seeds, ≈253 target buildings per seed). Coverage: mean per-building coverage over the 56-day onboarding window; wk 1: first 7 forecast days; MACD: mean |coverage − 0.90|; Under-cov.: share of buildings with coverage < 0.85; P10: 10th percentile of per-building coverage; Rel. width and Rel. IS: medians over buildings of width and interval score divided by the building's mean load. Mean ± s.d. over seeds.

| Method         | Coverage      | Coverage wk 1   | MACD          | Under-cov. (%)   | P10 cov.      | Rel. width    | Rel. IS       |
|:---------------|:--------------|:----------------|:--------------|:-----------------|:--------------|:--------------|:--------------|
| HSC-CQR        | 0.891 ± 0.003 | 0.885 ± 0.007   | 0.018 ± 0.001 | 3.4 ± 0.8        | 0.864 ± 0.003 | 0.385 ± 0.011 | 0.564 ± 0.024 |
| HSC-CQR simple | 0.895 ± 0.002 | 0.895 ± 0.004   | 0.017 ± 0.001 | 2.9 ± 0.7        | 0.869 ± 0.001 | 0.388 ± 0.013 | 0.563 ± 0.023 |
| Self-CQR       | 0.889 ± 0.002 | 0.864 ± 0.003   | 0.021 ± 0.001 | 6.1 ± 1.7        | 0.857 ± 0.003 | 0.395 ± 0.016 | 0.575 ± 0.018 |
| ACI-CQR        | 0.894 ± 0.003 | 0.892 ± 0.005   | 0.027 ± 0.005 | 10.5 ± 4.2       | 0.850 ± 0.009 | 0.385 ± 0.013 | 0.562 ± 0.025 |
| TQA-B-CQR      | 0.894 ± 0.003 | 0.894 ± 0.004   | 0.038 ± 0.001 | 17.0 ± 1.5       | 0.836 ± 0.002 | 0.384 ± 0.012 | 0.567 ± 0.023 |
| QShrink-CQR    | 0.897 ± 0.002 | 0.895 ± 0.005   | 0.022 ± 0.004 | 4.1 ± 1.6        | 0.862 ± 0.003 | 0.390 ± 0.013 | 0.562 ± 0.024 |
| GHCP-CQR       | 0.894 ± 0.004 | 0.897 ± 0.004   | 0.038 ± 0.001 | 16.8 ± 1.0       | 0.834 ± 0.003 | 0.385 ± 0.014 | 0.565 ± 0.023 |
| CQR            | 0.891 ± 0.004 | 0.892 ± 0.006   | 0.038 ± 0.001 | 18.7 ± 1.8       | 0.831 ± 0.003 | 0.383 ± 0.014 | 0.564 ± 0.023 |
| QR-LGBM        | 0.859 ± 0.009 | 0.865 ± 0.008   | 0.050 ± 0.006 | 40.3 ± 8.4       | 0.799 ± 0.008 | 0.357 ± 0.013 | 0.573 ± 0.025 |
| MLP-QR         | 0.885 ± 0.010 | 0.884 ± 0.016   | 0.039 ± 0.005 | 20.6 ± 6.2       | 0.826 ± 0.015 | 0.383 ± 0.024 | 0.571 ± 0.021 |
| MLP-Gauss      | 0.924 ± 0.009 | 0.934 ± 0.019   | 0.041 ± 0.002 | 5.6 ± 3.3        | 0.867 ± 0.013 | 0.451 ± 0.030 | 0.604 ± 0.036 |
| HSC-CQR (MLP)  | 0.897 ± 0.003 | 0.897 ± 0.004   | 0.018 ± 0.001 | 2.5 ± 1.0        | 0.869 ± 0.002 | 0.398 ± 0.014 | 0.569 ± 0.022 |
| CQR (MLP)      | 0.895 ± 0.004 | 0.897 ± 0.007   | 0.037 ± 0.004 | 15.6 ± 1.9       | 0.838 ± 0.005 | 0.392 ± 0.016 | 0.568 ± 0.023 |
| HSC            | 0.899 ± 0.003 | 0.880 ± 0.010   | 0.029 ± 0.002 | 9.2 ± 1.9        | 0.853 ± 0.005 | 0.413 ± 0.014 | 0.642 ± 0.024 |
| HSC simple     | 0.910 ± 0.001 | 0.906 ± 0.006   | 0.029 ± 0.002 | 5.5 ± 0.8        | 0.865 ± 0.002 | 0.437 ± 0.018 | 0.643 ± 0.021 |
| ACI            | 0.893 ± 0.004 | 0.889 ± 0.013   | 0.078 ± 0.002 | 26.2 ± 2.5       | 0.746 ± 0.010 | 0.454 ± 0.024 | 0.637 ± 0.024 |
| Self-CP        | 0.904 ± 0.003 | 0.899 ± 0.004   | 0.026 ± 0.001 | 5.8 ± 0.9        | 0.862 ± 0.003 | 0.440 ± 0.018 | 0.656 ± 0.023 |
| SCP-stage      | 0.881 ± 0.009 | 0.888 ± 0.013   | 0.094 ± 0.005 | 29.0 ± 3.4       | 0.700 ± 0.020 | 0.461 ± 0.024 | 0.639 ± 0.022 |
| SCP            | 0.881 ± 0.008 | 0.863 ± 0.012   | 0.093 ± 0.005 | 28.9 ± 3.6       | 0.701 ± 0.020 | 0.460 ± 0.024 | 0.640 ± 0.023 |
| Mondrian-usage | 0.883 ± 0.011 | 0.887 ± 0.016   | 0.092 ± 0.004 | 28.5 ± 4.4       | 0.706 ± 0.011 | 0.435 ± 0.040 | 0.666 ± 0.031 |
| Naive+SCP      | 0.883 ± 0.011 | 0.891 ± 0.011   | 0.092 ± 0.006 | 30.4 ± 2.3       | 0.707 ± 0.032 | 0.691 ± 0.053 | 0.978 ± 0.044 |
| Raw-SCP        | 0.907 ± 0.024 | 0.895 ± 0.029   | 0.118 ± 0.014 | 18.8 ± 4.7       | 0.700 ± 0.113 | 0.769 ± 0.077 | 1.130 ± 0.034 |


**Table 3.** Per-building interval reliability and sharpness on UCI (random-building protocol, nominal 90 %, 5 seeds, ≈95 target buildings per seed). Coverage: mean per-building coverage over the 56-day onboarding window; wk 1: first 7 forecast days; MACD: mean |coverage − 0.90|; Under-cov.: share of buildings with coverage < 0.85; P10: 10th percentile of per-building coverage; Rel. width and Rel. IS: medians over buildings of width and interval score divided by the building's mean load. Mean ± s.d. over seeds.

| Method         | Coverage      | Coverage wk 1   | MACD          | Under-cov. (%)   | P10 cov.      | Rel. width    | Rel. IS       |
|:---------------|:--------------|:----------------|:--------------|:-----------------|:--------------|:--------------|:--------------|
| HSC-CQR        | 0.898 ± 0.003 | 0.894 ± 0.007   | 0.014 ± 0.002 | 0.6 ± 0.9        | 0.878 ± 0.005 | 0.266 ± 0.012 | 0.368 ± 0.016 |
| HSC-CQR simple | 0.901 ± 0.004 | 0.902 ± 0.006   | 0.014 ± 0.003 | 1.1 ± 1.5        | 0.879 ± 0.009 | 0.267 ± 0.013 | 0.366 ± 0.015 |
| Self-CQR       | 0.896 ± 0.002 | 0.880 ± 0.008   | 0.016 ± 0.002 | 1.3 ± 1.9        | 0.871 ± 0.002 | 0.263 ± 0.011 | 0.372 ± 0.014 |
| ACI-CQR        | 0.903 ± 0.005 | 0.902 ± 0.007   | 0.020 ± 0.006 | 3.6 ± 3.1        | 0.871 ± 0.011 | 0.271 ± 0.015 | 0.366 ± 0.015 |
| TQA-B-CQR      | 0.900 ± 0.007 | 0.902 ± 0.008   | 0.032 ± 0.006 | 9.1 ± 4.1        | 0.857 ± 0.014 | 0.272 ± 0.014 | 0.368 ± 0.013 |
| QShrink-CQR    | 0.902 ± 0.005 | 0.905 ± 0.006   | 0.016 ± 0.004 | 1.7 ± 2.4        | 0.879 ± 0.011 | 0.267 ± 0.012 | 0.367 ± 0.015 |
| GHCP-CQR       | 0.906 ± 0.010 | 0.909 ± 0.011   | 0.034 ± 0.006 | 7.8 ± 3.6        | 0.864 ± 0.016 | 0.280 ± 0.019 | 0.369 ± 0.016 |
| CQR            | 0.899 ± 0.011 | 0.900 ± 0.010   | 0.033 ± 0.005 | 9.5 ± 4.3        | 0.856 ± 0.016 | 0.273 ± 0.019 | 0.368 ± 0.015 |
| QR-LGBM        | 0.877 ± 0.009 | 0.879 ± 0.010   | 0.035 ± 0.006 | 18.1 ± 6.9       | 0.832 ± 0.017 | 0.257 ± 0.015 | 0.368 ± 0.014 |
| MLP-QR         | 0.889 ± 0.013 | 0.886 ± 0.018   | 0.034 ± 0.008 | 13.3 ± 8.6       | 0.849 ± 0.022 | 0.268 ± 0.012 | 0.379 ± 0.017 |
| MLP-Gauss      | 0.927 ± 0.005 | 0.927 ± 0.013   | 0.037 ± 0.002 | 2.5 ± 1.6        | 0.885 ± 0.011 | 0.299 ± 0.017 | 0.394 ± 0.017 |
| HSC-CQR (MLP)  | 0.901 ± 0.006 | 0.896 ± 0.014   | 0.016 ± 0.004 | 2.1 ± 2.5        | 0.877 ± 0.010 | 0.274 ± 0.010 | 0.378 ± 0.016 |
| CQR (MLP)      | 0.899 ± 0.010 | 0.899 ± 0.011   | 0.033 ± 0.005 | 7.8 ± 3.8        | 0.860 ± 0.015 | 0.276 ± 0.012 | 0.377 ± 0.016 |
| HSC            | 0.904 ± 0.003 | 0.891 ± 0.010   | 0.021 ± 0.001 | 4.2 ± 2.6        | 0.870 ± 0.003 | 0.286 ± 0.012 | 0.418 ± 0.018 |
| HSC simple     | 0.912 ± 0.004 | 0.917 ± 0.010   | 0.023 ± 0.002 | 1.9 ± 1.4        | 0.880 ± 0.004 | 0.299 ± 0.013 | 0.418 ± 0.014 |
| ACI            | 0.911 ± 0.013 | 0.905 ± 0.016   | 0.076 ± 0.006 | 18.1 ± 4.4       | 0.795 ± 0.022 | 0.364 ± 0.026 | 0.434 ± 0.013 |
| Self-CP        | 0.908 ± 0.003 | 0.912 ± 0.003   | 0.021 ± 0.001 | 2.1 ± 1.8        | 0.878 ± 0.003 | 0.294 ± 0.012 | 0.420 ± 0.012 |
| SCP-stage      | 0.903 ± 0.015 | 0.904 ± 0.017   | 0.090 ± 0.006 | 20.2 ± 4.7       | 0.771 ± 0.025 | 0.377 ± 0.031 | 0.443 ± 0.018 |
| SCP            | 0.904 ± 0.014 | 0.884 ± 0.018   | 0.090 ± 0.006 | 20.0 ± 4.5       | 0.771 ± 0.023 | 0.376 ± 0.031 | 0.444 ± 0.018 |
| Naive+SCP      | 0.905 ± 0.008 | 0.904 ± 0.008   | 0.075 ± 0.004 | 21.5 ± 3.6       | 0.762 ± 0.018 | 0.475 ± 0.028 | 0.583 ± 0.020 |
| Raw-SCP        | 0.908 ± 0.048 | 0.898 ± 0.050   | 0.130 ± 0.028 | 17.9 ± 9.8       | 0.681 ± 0.218 | 0.967 ± 0.321 | 1.137 ± 0.207 |


![**Fig. 3.** Empirical distribution of per-building coverage over the 56-day onboarding window for the CQR-score calibration strategies and stage-matched split conformal prediction (all target buildings of all five seeds; dashed: nominal 0.90; dotted: 0.85).](figures/Fig4_coverage_cdf.png){width=16.5cm}

## 5.2 Comparison of building-adaptive calibration strategies (RQ2)

All strategies in this subsection use the same LightGBM quantile models and the same CQR scores; they differ only in how a new building's own scores enter the calibration. Pseudo-count shrinkage of the score distribution (HSC-CQR) is the most reliable of the tuned strategies on both datasets: on BDG2 its MACD is 0.018 and 3.4% of the buildings are under-covered (CQR: 0.038, 18.7%), and on UCI 0.014 and 0.6% (CQR: 0.033, 9.5%). The 10th-percentile coverage rises from 0.831 to 0.864 on BDG2. The median relative interval score is essentially unchanged (0.564 vs 0.564 on BDG2; 0.368 vs 0.368 on UCI), so the gain in reliability does not come from wider intervals. For reference, perfectly calibrated intervals with independent misses would have an expected MACD of about 0.0066 (BDG2) and 0.0065 (UCI) from sampling noise alone (1344 hourly observations per building); autocorrelated misses raise this floor further.

The competing mechanisms behave as their designs suggest. Quantile-level shrinkage (QShrink-CQR, the "regularised Mondrian") is the closest competitor (MACD 0.022 on BDG2, 0.016 on UCI; under-covered 4.1% and 1.7%). Self-only calibration (Self-CQR) is reliable later in the window but poor in the first week (coverage 0.864 on BDG2), when a handful of own scores yields noisy quantiles. Adaptive conformal inference on the same scores (ACI-CQR; MACD 0.027, under-covered 10.5%) adapts more slowly because it reacts to the building's errors only through the miscoverage indicator with a small step size. Temporal quantile adjustment (TQA-B-CQR; 0.038, 17.0%) and the GHCP-style pooling (GHCP-CQR; 0.038, 16.8%) remain close to pooled CQR: TQA-B bounds the quantile adjustment by design, and GHCP never gives the new building more weight than one reference building, which secures marginal validity across buildings but cannot correct a building whose errors are systematically larger than average.

Table 4 reports the paired per-building tests of HSC-CQR against each strategy. On BDG2, HSC-CQR has a smaller absolute coverage deviation than CQR for 84% of the 713 buildings ($r_{rb}$ = 0.86, Holm-adjusted $p$ < 0.001); against QShrink-CQR the corresponding values are 63% ($r_{rb}$ = 0.40, $p$ < 0.001), against Self-CQR 56% ($r_{rb}$ = 0.22, $p$ < 0.001) and against ACI-CQR 74% ($r_{rb}$ = 0.66, $p$ < 0.001). The reliability gain does not cost sharpness: HSC-CQR's per-building interval score is lower than CQR's for 58% of the buildings ($r_{rb}$ = 0.41, $p$ < 0.001) and statistically indistinguishable from QShrink-CQR's ($p$ = 0.688). The UCI comparisons, based on 270 clients, are reported in the same table. Fig. 4 summarises reliability and sharpness of all methods.

The calibration layer is not specific to LightGBM: applied to the quantiles of the MLP quantile model, it reduces the MACD from 0.037 (CQR on MLP quantiles) to 0.018 and the under-covered share from 15.6% to 2.5% on BDG2 (0.033 → 0.016 on UCI). On the absolute-residual score, HSC improves on pooled SCP (MACD 0.029 vs 0.094) but not on self-only calibration (Self-CP: 0.026); for that score the stage-agnostic simple variant is the better choice (0.029).

**Table 4.** Paired per-building comparison of HSC-CQR with each baseline (random-building protocol, nominal 90 %). CD = absolute coverage deviation |cov_b − 0.9|; IS = relative interval score. Mean diff. = HSC-CQR minus baseline, averaged over buildings (negative = HSC-CQR better); 95 % CI by site-cluster bootstrap (BDG2) or building bootstrap (UCI); Better = share of buildings for which HSC-CQR is better; r_rb = matched-pairs rank-biserial correlation (positive = HSC-CQR better); p = two-sided Wilcoxon signed-rank, Holm-adjusted within dataset and metric.

| Data   | Baseline        | Metric   |   n |   Mean diff. | 95 % CI            |   Better (%) |   r_rb | p (Holm)   |
|:-------|:----------------|:---------|----:|-------------:|:-------------------|-------------:|-------:|:-----------|
| BDG2   | CQR             | CD       | 713 |      -0.0204 | [-0.0237, -0.0185] |           84 |   0.86 | <0.001     |
| BDG2   | CQR             | IS       | 713 |      -0.009  | [-0.0137, -0.0060] |           58 |   0.41 | <0.001     |
| BDG2   | QShrink-CQR     | CD       | 713 |      -0.0047 | [-0.0069, -0.0031] |           63 |   0.4  | <0.001     |
| BDG2   | QShrink-CQR     | IS       | 713 |      -0.0034 | [-0.0098, -0.0000] |           46 |   0.02 | 0.688      |
| BDG2   | Self-CQR        | CD       | 713 |      -0.0034 | [-0.0067, -0.0011] |           56 |   0.22 | <0.001     |
| BDG2   | Self-CQR        | IS       | 713 |      -0.0519 | [-0.1584, -0.0135] |           93 |   0.92 | <0.001     |
| BDG2   | ACI-CQR         | CD       | 713 |      -0.0098 | [-0.0127, -0.0081] |           74 |   0.66 | <0.001     |
| BDG2   | ACI-CQR         | IS       | 713 |      -0.1718 | [-0.5050, -0.0022] |           51 |   0.16 | <0.001     |
| BDG2   | TQA-B-CQR       | CD       | 713 |      -0.0206 | [-0.0232, -0.0191] |           85 |   0.85 | <0.001     |
| BDG2   | TQA-B-CQR       | IS       | 713 |      -0.0097 | [-0.0119, -0.0064] |           65 |   0.52 | <0.001     |
| BDG2   | GHCP-CQR        | CD       | 713 |      -0.0201 | [-0.0237, -0.0179] |           83 |   0.85 | <0.001     |
| BDG2   | GHCP-CQR        | IS       | 713 |      -0.0088 | [-0.0135, -0.0057] |           60 |   0.41 | <0.001     |
| BDG2   | QR-LGBM         | CD       | 713 |      -0.032  | [-0.0378, -0.0244] |           91 |   0.96 | <0.001     |
| BDG2   | QR-LGBM         | IS       | 713 |      -0.0151 | [-0.0205, -0.0090] |           71 |   0.66 | <0.001     |
| BDG2   | MLP-QR          | CD       | 713 |      -0.0208 | [-0.0230, -0.0194] |           82 |   0.83 | <0.001     |
| BDG2   | MLP-QR          | IS       | 713 |      -0.0101 | [-0.0170, -0.0064] |           66 |   0.37 | <0.001     |
| BDG2   | MLP-Gauss       | CD       | 713 |      -0.0238 | [-0.0325, -0.0171] |           80 |   0.77 | <0.001     |
| BDG2   | MLP-Gauss       | IS       | 713 |      -0.1307 | [-0.1879, -0.0841] |           93 |   0.93 | <0.001     |
| BDG2   | HSC-CQR fixed-κ | CD       | 713 |       0.0026 | [+0.0015, +0.0036] |           31 |  -0.45 | <0.001     |
| BDG2   | HSC-CQR fixed-κ | IS       | 713 |      -0.0064 | [-0.0259, -0.0004] |           67 |   0.34 | <0.001     |
| UCI    | CQR             | CD       | 270 |      -0.0195 | [-0.0246, -0.0153] |           86 |   0.89 | <0.001     |
| UCI    | CQR             | IS       | 270 |      -0.0081 | [-0.0137, -0.0036] |           60 |   0.38 | <0.001     |
| UCI    | QShrink-CQR     | CD       | 270 |      -0.0028 | [-0.0045, -0.0015] |           59 |   0.37 | <0.001     |
| UCI    | QShrink-CQR     | IS       | 270 |       0.0002 | [-0.0007, +0.0012] |           50 |   0.08 | 0.277      |
| UCI    | Self-CQR        | CD       | 270 |      -0.0028 | [-0.0042, -0.0014] |           62 |   0.3  | <0.001     |
| UCI    | Self-CQR        | IS       | 270 |      -0.0155 | [-0.0239, -0.0087] |           94 |   0.96 | <0.001     |
| UCI    | ACI-CQR         | CD       | 270 |      -0.0064 | [-0.0079, -0.0049] |           69 |   0.57 | <0.001     |
| UCI    | ACI-CQR         | IS       | 270 |      -1.9143 | [-4.5953, -0.1544] |           54 |   0.16 | 0.045      |
| UCI    | TQA-B-CQR       | CD       | 270 |      -0.0181 | [-0.0228, -0.0141] |           84 |   0.84 | <0.001     |
| UCI    | TQA-B-CQR       | IS       | 270 |      -0.0065 | [-0.0110, -0.0027] |           62 |   0.41 | <0.001     |
| UCI    | GHCP-CQR        | CD       | 270 |      -0.0206 | [-0.0256, -0.0165] |           87 |   0.88 | <0.001     |
| UCI    | GHCP-CQR        | IS       | 270 |      -0.008  | [-0.0131, -0.0039] |           65 |   0.5  | <0.001     |
| UCI    | QR-LGBM         | CD       | 270 |      -0.0219 | [-0.0274, -0.0173] |           82 |   0.82 | <0.001     |
| UCI    | QR-LGBM         | IS       | 270 |      -0.01   | [-0.0166, -0.0046] |           52 |   0.24 | 0.002      |
| UCI    | MLP-QR          | CD       | 270 |      -0.021  | [-0.0265, -0.0163] |           85 |   0.85 | <0.001     |
| UCI    | MLP-QR          | IS       | 270 |      -0.0035 | [-0.0119, +0.0072] |           77 |   0.61 | <0.001     |
| UCI    | MLP-Gauss       | CD       | 270 |      -0.0231 | [-0.0260, -0.0204] |           85 |   0.86 | <0.001     |
| UCI    | MLP-Gauss       | IS       | 270 |      -0.045  | [-0.0627, -0.0294] |           93 |   0.93 | <0.001     |
| UCI    | HSC-CQR fixed-κ | CD       | 270 |       0.001  | [+0.0004, +0.0017] |           41 |  -0.18 | 0.058      |
| UCI    | HSC-CQR fixed-κ | IS       | 270 |      -0.0004 | [-0.0020, +0.0008] |           57 |   0.16 | 0.100      |


![**Fig. 4.** Reliability (a, MACD) and sharpness (b, median relative interval score) of all interval methods on BDG2 and UCI (random-building protocol, nominal 90 %; mean ± s.d. over five seeds; methods sorted by BDG2 MACD; HSC-CQR variants in bold).](figures/Fig5_tradeoff.png){width=16.5cm}

## 5.3 Onboarding dynamics

Fig. 5 resolves coverage and interval score by onboarding day. All methods have their largest interval scores in the first days, when the forecaster has least history. Pooled calibration keeps a fixed radius per stage bin and therefore cannot react to an individual building, whereas the shrinkage strategies move towards the building's own error level as scores accumulate. In the first week, HSC-CQR's mean coverage is 0.885 on BDG2 and 0.894 on UCI (CQR: 0.892 and 0.900); until own scores accumulate, every strategy can only be as reliable as its population calibration.

![**Fig. 5.** Mean coverage (a, b) and median relative interval score (c, d) by days of own history; daily for the first week (shaded), weekly means afterwards; over buildings and seeds.](figures/Fig3_stage_curves.png){width=16.5cm}

## 5.4 Which design elements matter (RQ3)

Table 5 and Fig. 6 isolate the elements of the calibration layer. Removing the shrinkage towards own scores (κ = ∞) is decisive: HSC-CQR's under-covered share rises from 3.4% to 21.7% on BDG2 and from 0.6% to 12.6% on UCI. Removing the similarity prior (K = all) or the stage matching changes the MACD by less than its seed-to-seed standard deviation (BDG2: 0.017 and 0.017 vs 0.018); the simple variant without both refinements reaches 0.017 on BDG2 and 0.014 on UCI. The value of the pseudo-count matters more than the refinements. Fixing it at one week of hourly scores (κ = 168 h, a donor–local mixture with fixed pseudo-count) gives a MACD of 0.015 and 1.9% under-covered buildings on BDG2 at a median interval score of 0.566, i.e. more reliable but marginally less sharp than the tuned HSC-CQR (paired tests: $r_{rb}$ = -0.45 for the coverage deviation and 0.34 for the interval score, positive values favouring the tuned variant); on UCI the two are statistically indistinguishable (0.013 vs 0.014; $p$ = 0.058). Leave-one-building-out tuning on the interval score selected κ values of 336 h for the simple variant on BDG2 and 168, 336, 672 h on UCI (across seeds); the tuning objective rewards sharpness as well as coverage (see the sensitivity analysis below).

**Table 5.** Component ablation (random-building protocol, 90 %, mean ± s.d. over 5 seeds). '-stage': prior pooled over all onboarding stages; '-kNN': prior from all calibration buildings (K = all); 'simple': both removed; '-shrink': prior only (κ = ∞); 'fixed-κ': simple variant with κ = 168 h (one week) instead of the leave-one-building-out choice (a donor–local mixture with fixed pseudo-count); Self-*: κ = 0 with fallback to the pooled quantile. Except for fixed-κ, every variant is re-tuned on calibration buildings with the component removed.

| Variant         | BDG2 MACD     | BDG2 Under (%)   | BDG2 Rel. IS   | UCI MACD      | UCI Under (%)   | UCI Rel. IS   |
|:----------------|:--------------|:-----------------|:---------------|:--------------|:----------------|:--------------|
| HSC-CQR         | 0.018 ± 0.001 | 3.4 ± 0.8        | 0.564 ± 0.024  | 0.014 ± 0.002 | 0.6 ± 0.9       | 0.368 ± 0.016 |
| HSC-CQR -stage  | 0.017 ± 0.001 | 3.2 ± 0.9        | 0.564 ± 0.024  | 0.014 ± 0.003 | 1.1 ± 1.5       | 0.366 ± 0.015 |
| HSC-CQR -kNN    | 0.017 ± 0.001 | 3.1 ± 0.9        | 0.563 ± 0.024  | 0.014 ± 0.002 | 1.1 ± 1.5       | 0.366 ± 0.016 |
| HSC-CQR simple  | 0.017 ± 0.001 | 2.9 ± 0.7        | 0.563 ± 0.023  | 0.014 ± 0.003 | 1.1 ± 1.5       | 0.366 ± 0.015 |
| HSC-CQR fixed-κ | 0.015 ± 0.001 | 1.9 ± 0.8        | 0.566 ± 0.022  | 0.013 ± 0.002 | 0.4 ± 0.6       | 0.366 ± 0.015 |
| HSC-CQR -shrink | 0.037 ± 0.001 | 21.7 ± 2.6       | 0.567 ± 0.023  | 0.031 ± 0.005 | 12.6 ± 4.0      | 0.369 ± 0.016 |
| Self-CQR        | 0.021 ± 0.001 | 6.1 ± 1.7        | 0.575 ± 0.018  | 0.016 ± 0.002 | 1.3 ± 1.9       | 0.372 ± 0.014 |
| CQR             | 0.038 ± 0.001 | 18.7 ± 1.8       | 0.564 ± 0.023  | 0.033 ± 0.005 | 9.5 ± 4.3       | 0.368 ± 0.015 |
| HSC             | 0.029 ± 0.002 | 9.2 ± 1.9        | 0.642 ± 0.024  | 0.021 ± 0.001 | 4.2 ± 2.6       | 0.418 ± 0.018 |
| HSC -stage      | 0.028 ± 0.002 | 9.3 ± 2.5        | 0.646 ± 0.021  | 0.021 ± 0.001 | 4.4 ± 3.3       | 0.419 ± 0.016 |
| HSC -kNN        | 0.029 ± 0.002 | 5.3 ± 0.9        | 0.642 ± 0.022  | 0.027 ± 0.005 | 2.9 ± 2.2       | 0.420 ± 0.014 |
| HSC simple      | 0.029 ± 0.002 | 5.5 ± 0.8        | 0.643 ± 0.021  | 0.023 ± 0.002 | 1.9 ± 1.4       | 0.418 ± 0.014 |
| HSC -shrink     | 0.093 ± 0.005 | 45.8 ± 3.4       | 0.662 ± 0.030  | 0.078 ± 0.004 | 31.4 ± 3.7      | 0.435 ± 0.030 |
| Self-CP         | 0.026 ± 0.001 | 5.8 ± 0.9        | 0.656 ± 0.023  | 0.021 ± 0.001 | 2.1 ± 1.8       | 0.420 ± 0.012 |
| SCP-stage       | 0.094 ± 0.005 | 29.0 ± 3.4       | 0.639 ± 0.022  | 0.090 ± 0.006 | 20.2 ± 4.7      | 0.443 ± 0.018 |


![**Fig. 6.** Ablation of the HSC-CQR elements: '-stage' removes onboarding-stage matching, '-kNN' the similarity prior, 'simple' both, 'fixed-κ' fixes κ = 168 h, '-shrink' removes the shrinkage towards own scores (κ = ∞); Self-CQR is κ = 0; mean ± s.d. over five seeds.](figures/Fig6_ablation.png){width=16.5cm}

## 5.5 Robustness (RQ4)

Table 6 and Fig. 7 stress the strategies on BDG2. With 15 % meter noise on the new buildings, pooled calibration from clean calibration buildings breaks down (SCP-stage: 100.0% under-covered; CQR: 30.7%), whereas HSC-CQR leaves 1.7% under-covered because the building's own, noisy scores enter the mixture. Missing data (up to 40 % of hours) mainly delays adaptation (HSC-CQR 5.4% vs CQR 16.9%). Abrupt level changes of ±40 % at day 28 degrade every strategy, because pre-change scores remain in the calibration, but the shrinkage strategies least: with the downward shift HSC-CQR leaves 4.2% of the buildings under-covered (QShrink-CQR 5.9%, ACI-CQR 10.9%, CQR 28.6%) and with the upward shift 6.5% (ACI-CQR 16.3%, CQR 30.3%). A very small calibration pool (10 % of the calibration buildings, 16 buildings) raises HSC-CQR's under-covered share to 7.9% (CQR 21.6%), whereas pools of 25 % and 50 % have little effect (3.2% and 4.1%); a forecaster trained on only 10 % of the training buildings increases it to 5.4% (CQR 25.0%).

**Table 6.** Stress tests on BDG2 (3 seeds): MACD / share of under-covered buildings (%). Noise, missing data and level shifts are applied to the target buildings' onboarding windows (history and truth); calibration-pool conditions keep a random fraction of calibration buildings; the weak forecaster is trained on 10 % of the training buildings (no MLP baselines, '–').

| Condition                                 | HSC-CQR   | HSC-CQR simple   | ACI-CQR    | Self-CQR   | TQA-B-CQR   | QShrink-CQR   | GHCP-CQR   | CQR        | MLP-QR     |
|:------------------------------------------|:----------|:-----------------|:-----------|:-----------|:------------|:--------------|:-----------|:-----------|:-----------|
| Meter noise 5 %                           | 0.015 / 3 | 0.013 / 3        | 0.020 / 8  | 0.016 / 2  | 0.029 / 19  | 0.015 / 3     | 0.028 / 15 | 0.029 / 17 | 0.031 / 19 |
| Meter noise 15 %                          | 0.018 / 2 | 0.017 / 1        | 0.030 / 10 | 0.010 / 0  | 0.044 / 36  | 0.020 / 3     | 0.039 / 27 | 0.041 / 31 | 0.039 / 26 |
| Missing 20 %                              | 0.019 / 4 | 0.018 / 3        | 0.028 / 10 | 0.022 / 6  | 0.036 / 16  | 0.022 / 3     | 0.037 / 16 | 0.038 / 18 | 0.047 / 33 |
| Missing 40 %                              | 0.023 / 5 | 0.023 / 5        | 0.033 / 12 | 0.023 / 6  | 0.038 / 17  | 0.027 / 6     | 0.040 / 15 | 0.040 / 17 | 0.063 / 47 |
| Level +40 % (day 28)                      | 0.021 / 6 | 0.020 / 5        | 0.027 / 16 | 0.022 / 8  | 0.040 / 30  | 0.022 / 7     | 0.039 / 28 | 0.041 / 30 | 0.043 / 31 |
| Level −40 % (day 28)                      | 0.019 / 4 | 0.017 / 4        | 0.024 / 11 | 0.023 / 9  | 0.035 / 22  | 0.019 / 6     | 0.037 / 26 | 0.039 / 29 | 0.035 / 19 |
| Cal. pool 10 %                            | 0.020 / 8 | 0.020 / 6        | 0.026 / 10 | 0.021 / 7  | 0.040 / 24  | 0.019 / 6     | 0.036 / 9  | 0.039 / 22 | 0.037 / 20 |
| Cal. pool 25 %                            | 0.017 / 3 | 0.018 / 4        | 0.020 / 4  | 0.021 / 7  | 0.038 / 18  | 0.020 / 3     | 0.037 / 13 | 0.037 / 18 | 0.037 / 20 |
| Cal. pool 50 %                            | 0.018 / 4 | 0.018 / 4        | 0.022 / 6  | 0.021 / 7  | 0.037 / 16  | 0.019 / 3     | 0.037 / 15 | 0.037 / 18 | 0.037 / 20 |
| Weak forecaster (10 % training buildings) | 0.021 / 5 | 0.021 / 4        | 0.033 / 13 | 0.022 / 8  | 0.049 / 22  | 0.022 / 4     | 0.052 / 23 | 0.052 / 25 | –          |


![**Fig. 7.** Robustness on BDG2: MACD (a) and share of under-covered buildings (b) under meter noise, missing data, level shifts, reduced calibration pools and a weak forecaster (3 seeds).](figures/Fig7_robustness.png){width=16.5cm}

## 5.6 Generalisation (RQ5)

Under the leave-site-out protocol the target buildings are on campuses from which no training or calibration building comes. HSC-CQR's MACD is 0.020 (CQR 0.044; QShrink-CQR 0.026), with 5.3% versus 21.8% of the buildings under-covered (QShrink-CQR 4.2%; HSC-CQR simple 3.5%) (Table 7, Fig. 8). With models and calibration scores from BDG2 applied to Portuguese UCI clients, CQR leaves 5.6% under-covered and HSC-CQR 0.4%. The opposite direction is much harder: a model and calibration population from UCI clients, without weather information, leave 41.8% of BDG2 buildings under-covered with CQR; HSC-CQR reduces this to 8.7%, but self-only calibration does as well (6.9%), because a prior from a different population adds nothing — the gain under such transfer rests entirely on the building's own scores.

**Table 7.** Generalisation to unseen sites (BDG2 leave-site-out, 5 folds) and across datasets/countries (models and calibration scores from the source dataset, no weather features; 3 seeds). The BDG2→BDG2 (no wx) rows are the within-dataset reference without weather features.

| Setting             |   Runs | Method         | Coverage      | MACD          | Under-cov. (%)   | Rel. IS       |
|:--------------------|-------:|:---------------|:--------------|:--------------|:-----------------|:--------------|
| BDG2 random         |      5 | HSC-CQR        | 0.891 ± 0.003 | 0.018 ± 0.001 | 3.4 ± 0.8        | 0.564 ± 0.024 |
| BDG2 random         |      5 | HSC-CQR simple | 0.895 ± 0.002 | 0.017 ± 0.001 | 2.9 ± 0.7        | 0.563 ± 0.023 |
| BDG2 random         |      5 | ACI-CQR        | 0.894 ± 0.003 | 0.027 ± 0.005 | 10.5 ± 4.2       | 0.562 ± 0.025 |
| BDG2 random         |      5 | Self-CQR       | 0.889 ± 0.002 | 0.021 ± 0.001 | 6.1 ± 1.7        | 0.575 ± 0.018 |
| BDG2 random         |      5 | TQA-B-CQR      | 0.894 ± 0.003 | 0.038 ± 0.001 | 17.0 ± 1.5       | 0.567 ± 0.023 |
| BDG2 random         |      5 | QShrink-CQR    | 0.897 ± 0.002 | 0.022 ± 0.004 | 4.1 ± 1.6        | 0.562 ± 0.024 |
| BDG2 random         |      5 | GHCP-CQR       | 0.894 ± 0.004 | 0.038 ± 0.001 | 16.8 ± 1.0       | 0.565 ± 0.023 |
| BDG2 random         |      5 | CQR            | 0.891 ± 0.004 | 0.038 ± 0.001 | 18.7 ± 1.8       | 0.564 ± 0.023 |
| BDG2 random         |      5 | MLP-QR         | 0.885 ± 0.010 | 0.039 ± 0.005 | 20.6 ± 6.2       | 0.571 ± 0.021 |
| BDG2 leave-site-out |      5 | HSC-CQR        | 0.893 ± 0.009 | 0.020 ± 0.004 | 5.3 ± 2.6        | 0.533 ± 0.116 |
| BDG2 leave-site-out |      5 | HSC-CQR simple | 0.897 ± 0.010 | 0.020 ± 0.004 | 3.5 ± 1.8        | 0.533 ± 0.116 |
| BDG2 leave-site-out |      5 | ACI-CQR        | 0.897 ± 0.014 | 0.026 ± 0.006 | 8.4 ± 6.7        | 0.534 ± 0.115 |
| BDG2 leave-site-out |      5 | Self-CQR       | 0.889 ± 0.005 | 0.022 ± 0.003 | 6.3 ± 3.7        | 0.545 ± 0.114 |
| BDG2 leave-site-out |      5 | TQA-B-CQR      | 0.897 ± 0.027 | 0.043 ± 0.007 | 19.8 ± 17.5      | 0.541 ± 0.117 |
| BDG2 leave-site-out |      5 | QShrink-CQR    | 0.900 ± 0.014 | 0.026 ± 0.010 | 4.2 ± 5.2        | 0.536 ± 0.117 |
| BDG2 leave-site-out |      5 | GHCP-CQR       | 0.896 ± 0.027 | 0.044 ± 0.007 | 20.3 ± 16.3      | 0.538 ± 0.117 |
| BDG2 leave-site-out |      5 | CQR            | 0.894 ± 0.027 | 0.044 ± 0.008 | 21.8 ± 17.6      | 0.539 ± 0.117 |
| BDG2 leave-site-out |      5 | MLP-QR         | 0.889 ± 0.029 | 0.043 ± 0.011 | 25.0 ± 19.0      | 0.547 ± 0.108 |
| BDG2→BDG2 (no wx)   |      3 | HSC-CQR        | 0.893 ± 0.004 | 0.017 ± 0.000 | 2.9 ± 0.6        | 0.575 ± 0.025 |
| BDG2→BDG2 (no wx)   |      3 | HSC-CQR simple | 0.896 ± 0.003 | 0.017 ± 0.001 | 2.2 ± 1.0        | 0.574 ± 0.025 |
| BDG2→BDG2 (no wx)   |      3 | ACI-CQR        | 0.897 ± 0.003 | 0.022 ± 0.004 | 6.2 ± 3.2        | 0.573 ± 0.025 |
| BDG2→BDG2 (no wx)   |      3 | Self-CQR       | 0.888 ± 0.003 | 0.022 ± 0.002 | 7.4 ± 0.8        | 0.583 ± 0.021 |
| BDG2→BDG2 (no wx)   |      3 | TQA-B-CQR      | 0.896 ± 0.002 | 0.038 ± 0.002 | 17.7 ± 2.0       | 0.573 ± 0.022 |
| BDG2→BDG2 (no wx)   |      3 | QShrink-CQR    | 0.898 ± 0.004 | 0.021 ± 0.001 | 3.6 ± 1.0        | 0.575 ± 0.026 |
| BDG2→BDG2 (no wx)   |      3 | GHCP-CQR       | 0.896 ± 0.003 | 0.037 ± 0.001 | 15.7 ± 0.6       | 0.574 ± 0.026 |
| BDG2→BDG2 (no wx)   |      3 | CQR            | 0.894 ± 0.003 | 0.037 ± 0.001 | 17.4 ± 1.8       | 0.574 ± 0.026 |
| BDG2→BDG2 (no wx)   |      3 | MLP-QR         | 0.900 ± 0.006 | 0.036 ± 0.004 | 12.6 ± 5.0       | 0.564 ± 0.023 |
| UCI→BDG2 (no wx)    |      3 | HSC-CQR        | 0.887 ± 0.001 | 0.023 ± 0.002 | 8.7 ± 4.0        | 0.605 ± 0.026 |
| UCI→BDG2 (no wx)    |      3 | HSC-CQR simple | 0.889 ± 0.001 | 0.022 ± 0.003 | 6.7 ± 3.6        | 0.603 ± 0.025 |
| UCI→BDG2 (no wx)    |      3 | ACI-CQR        | 0.880 ± 0.011 | 0.035 ± 0.017 | 20.9 ± 17.8      | 0.608 ± 0.025 |
| UCI→BDG2 (no wx)    |      3 | Self-CQR       | 0.893 ± 0.003 | 0.022 ± 0.002 | 6.9 ± 2.8        | 0.617 ± 0.027 |
| UCI→BDG2 (no wx)    |      3 | TQA-B-CQR      | 0.869 ± 0.004 | 0.056 ± 0.003 | 37.4 ± 2.6       | 0.609 ± 0.025 |
| UCI→BDG2 (no wx)    |      3 | QShrink-CQR    | 0.888 ± 0.003 | 0.026 ± 0.006 | 11.2 ± 6.2       | 0.603 ± 0.025 |
| UCI→BDG2 (no wx)    |      3 | GHCP-CQR       | 0.869 ± 0.001 | 0.056 ± 0.004 | 36.6 ± 1.9       | 0.611 ± 0.030 |
| UCI→BDG2 (no wx)    |      3 | CQR            | 0.861 ± 0.001 | 0.060 ± 0.004 | 41.8 ± 2.9       | 0.613 ± 0.031 |
| UCI→BDG2 (no wx)    |      3 | MLP-QR         | 0.855 ± 0.007 | 0.061 ± 0.005 | 43.2 ± 4.2       | 0.623 ± 0.034 |
| UCI random          |      5 | HSC-CQR        | 0.898 ± 0.003 | 0.014 ± 0.002 | 0.6 ± 0.9        | 0.368 ± 0.016 |
| UCI random          |      5 | HSC-CQR simple | 0.901 ± 0.004 | 0.014 ± 0.003 | 1.1 ± 1.5        | 0.366 ± 0.015 |
| UCI random          |      5 | ACI-CQR        | 0.903 ± 0.005 | 0.020 ± 0.006 | 3.6 ± 3.1        | 0.366 ± 0.015 |
| UCI random          |      5 | Self-CQR       | 0.896 ± 0.002 | 0.016 ± 0.002 | 1.3 ± 1.9        | 0.372 ± 0.014 |
| UCI random          |      5 | TQA-B-CQR      | 0.900 ± 0.007 | 0.032 ± 0.006 | 9.1 ± 4.1        | 0.368 ± 0.013 |
| UCI random          |      5 | QShrink-CQR    | 0.902 ± 0.005 | 0.016 ± 0.004 | 1.7 ± 2.4        | 0.367 ± 0.015 |
| UCI random          |      5 | GHCP-CQR       | 0.906 ± 0.010 | 0.034 ± 0.006 | 7.8 ± 3.6        | 0.369 ± 0.016 |
| UCI random          |      5 | CQR            | 0.899 ± 0.011 | 0.033 ± 0.005 | 9.5 ± 4.3        | 0.368 ± 0.015 |
| UCI random          |      5 | MLP-QR         | 0.889 ± 0.013 | 0.034 ± 0.008 | 13.3 ± 8.6       | 0.379 ± 0.017 |
| BDG2→UCI (no wx)    |      3 | HSC-CQR        | 0.899 ± 0.002 | 0.013 ± 0.000 | 0.4 ± 0.6        | 0.437 ± 0.016 |
| BDG2→UCI (no wx)    |      3 | HSC-CQR simple | 0.902 ± 0.003 | 0.013 ± 0.001 | 0.7 ± 0.6        | 0.438 ± 0.016 |
| BDG2→UCI (no wx)    |      3 | ACI-CQR        | 0.905 ± 0.006 | 0.016 ± 0.003 | 1.1 ± 1.1        | 0.438 ± 0.017 |
| BDG2→UCI (no wx)    |      3 | Self-CQR       | 0.892 ± 0.003 | 0.016 ± 0.001 | 2.1 ± 2.8        | 0.447 ± 0.016 |
| BDG2→UCI (no wx)    |      3 | TQA-B-CQR      | 0.901 ± 0.013 | 0.027 ± 0.005 | 6.3 ± 3.8        | 0.442 ± 0.019 |
| BDG2→UCI (no wx)    |      3 | QShrink-CQR    | 0.903 ± 0.004 | 0.014 ± 0.001 | 0.4 ± 0.6        | 0.436 ± 0.017 |
| BDG2→UCI (no wx)    |      3 | GHCP-CQR       | 0.905 ± 0.013 | 0.028 ± 0.003 | 4.9 ± 3.4        | 0.443 ± 0.015 |
| BDG2→UCI (no wx)    |      3 | CQR            | 0.903 ± 0.013 | 0.028 ± 0.004 | 5.6 ± 4.3        | 0.442 ± 0.016 |
| BDG2→UCI (no wx)    |      3 | MLP-QR         | 0.908 ± 0.002 | 0.024 ± 0.003 | 3.2 ± 2.1        | 0.435 ± 0.014 |


![**Fig. 8.** Generalisation: MACD (a) and median relative interval score (b) for random-building, leave-site-out and cross-dataset settings.](figures/Fig8_generalisation.png){width=16.5cm}

## 5.7 Sensitivity and computational cost

Fig. 9 shows the target-building MACD and interval score of HSC-CQR over the full grid of κ and K (for transparency only; not used for any choice). MACD is lowest for κ of about four days to one week of hourly scores (96–168 h; BDG2 0.015, UCI 0.012), increases moderately up to two weeks and sharply towards κ = ∞ (0.037 on BDG2), whereas the interval score is lowest for two to four weeks (336–672 h); K has little influence. This explains why the leave-one-building-out selection, which minimises the interval score, mostly chose 336 h. Results at nominal 95 % and 80 % show the same ordering of the absolute-score strategies (supplementary Tables S3–S6).

Table 8 reports costs on a 4-core CPU. Once the scores are stored, the calibration layer adds 0.437 ms per building-day and needs 19.8 MB for about 170 calibration buildings; the one-off leave-one-building-out tuning takes 36.7 s. Both are negligible next to training the global forecaster (106 s for the three LightGBM models).

![**Fig. 9.** Sensitivity of HSC-CQR to κ and K on target buildings (mean over five seeds; not used for selection).](figures/Fig9_sensitivity.png){width=16.5cm}

**Table 8.** Computational cost on a 4-core CPU (mean over 5 seeds). HSC tuning = leave-one-building-out grid search over (κ, K) on all calibration buildings; HSC update = computing one building's radius for one day (including neighbour search) once its scores are stored.

| Data   |   Training rows (M) |   LightGBM training, 3 models (s) |   MLP training, 2 models (s) |   LightGBM inference (ms / building-day) |   HSC tuning, LOBO (s) |   HSC update (ms / building-day) |   HSC store (MB) |
|:-------|--------------------:|----------------------------------:|-----------------------------:|-----------------------------------------:|-----------------------:|---------------------------------:|-----------------:|
| BDG2   |                1.32 |                               106 |                           92 |                                    0.668 |                   36.7 |                            0.437 |             19.8 |
| UCI    |                1    |                               298 |                          239 |                                    0.106 |                    9.6 |                            0.172 |              7.4 |


## 5.8 Error analysis

On BDG2 the Spearman correlation between per-building coverage and CV(RMSE) is -0.65 for CQR and -0.36 for HSC-CQR (-0.96 for SCP-stage), i.e. HSC weakens the dependence of reliability on forecast difficulty. Across usage classes with at least 30 building × seed units, the largest reduction of the absolute coverage deviation is observed for 'Education' and the smallest for 'Lodging/residential' (Fig. 10b). Of the 1265 building × seed units, 43 remain under-covered by HSC-CQR. Their median within-window level change |log(mean load weeks 5–8 / weeks 1–4)| is 0.197 versus 0.053 for the others (Mann–Whitney p < 0.001); remaining failures are therefore associated with regime changes during onboarding. Their first-week volatility is 0.118 versus 0.113 (p = 0.725). On UCI, 3 of 475 units remain under-covered; the corresponding level-change medians are 0.838 versus 0.049 (p < 0.001). Fig. 11 shows two pre-specified buildings: the one at the 10th percentile and the one at the median of per-building CQR coverage.

![**Fig. 10.** Error analysis on BDG2: (a) per-building coverage vs. point-forecast CV(RMSE); (b) mean coverage by primary usage (usage classes with at least 30 building × seed units).](figures/Fig10_error_analysis.png){width=16.5cm}

![**Fig. 11.** Day-ahead 90 % intervals for two pre-specified BDG2 buildings during their first 10 forecast days (seed 0): the building at the 10th percentile (a) and at the median (b) of per-building CQR coverage. Markers show observations outside the respective interval.](figures/Fig11_examples.png){width=16.5cm}


# 6. Discussion

## 6.1 Why pooled calibration fails per building, and why shrinkage helps

A global forecaster normalised by building scale yields scores that are comparable *on average* across buildings, but not identically distributed: some buildings have regular schedules and small errors, others irregular occupancy, plug loads or weather sensitivity that the first days of data cannot reveal. A pooled quantile is a compromise that over-covers the former and under-covers the latter; in our data this leaves a substantial share of new buildings well below the nominal coverage although the pooled coverage looks satisfactory (Tables 2–3). Calibration on the building's own errors alone removes this bias but replaces it with variance — with a few dozen hourly scores, the empirical 90 % quantile is a noisy estimate, which is visible in Self-CQR's first-week coverage. Shrinkage trades the two off explicitly, and its pseudo-count κ has a direct operational reading: the number of hourly own scores that the population prior is worth. The leave-one-building-out selections (336 h on BDG2 and 168, 336, 672 h on UCI for the simple variant) mean that a building's own errors dominate after about one to two weeks of data.

The comparison with the other building-adaptive strategies clarifies what matters. Mixing *distributions* (HSC) and shrinking *quantiles* (QShrink) behave similarly when κ and λ are tuned in the same way, with an advantage for the distribution mixture in our data; both clearly outperform strategies that adapt the queried level instead of the score distribution (ACI, TQA-B). ACI updates the level through the binary miscoverage signal with a small step size, which is what keeps it stable over long series but makes it slow from a poor starting point; TQA-B bounds its adjustment by design. The GHCP-style pooling secures marginal validity across buildings by never giving the new building more weight than one reference building — a sound choice for exchangeable groups, but one that cannot correct a building whose errors are systematically larger than average. In short, per-building reliability during onboarding requires the building's own errors to gain weight as they accumulate, and the rate at which they gain weight (κ) is the one parameter that needs care.

## 6.2 What did not help, and what the pseudo-count trades off

Two refinements that we expected to matter did not. Similarity localisation of the prior (nearest calibration buildings by load-shape descriptor) produced no measurable gain. After normalisation by scale and conditioning of the forecaster on history-derived features, the remaining between-building differences in score distributions appear to be driven by events — occupancy changes, equipment faults, schedule irregularities — rather than by load shape or usage type; the usage-based Mondrian baseline failed for the same reason. Stage matching was unnecessary because the forecaster is told how much history it has (history-length feature and masked lags), so its errors at different stages are already on a comparable scale after normalisation.

The choice of κ embodies a trade-off between sharpness and per-building reliability. The leave-one-building-out objective, the interval score, rewards both and selected mostly two weeks of hourly scores; per-building reliability is best at four days to one week, and a pre-specified pseudo-count of one week produced fewer under-covered buildings on BDG2 at a marginally higher interval score (Table 5; on UCI the two were indistinguishable). Operators who weight under-coverage more heavily than sharpness — for example, when intervals protect demand-response baselines — can therefore choose a pseudo-count of about one week rather than the interval-score optimum; the sensitivity analysis (Fig. 9) shows that any value between about one day and two weeks performs far better than pooled calibration.

## 6.3 Practical implications

For aggregators, utilities and demand-response platforms that onboard buildings continuously, the results support a simple operating rule: calibrate the intervals of a global forecaster with CQR scores of previously onboarded buildings, and blend each new building's own scores in with a pseudo-count of about one to two weeks of hourly scores. This keeps the share of buildings with clearly unreliable intervals small throughout onboarding and avoids a failure mode that pooled calibration hides — systematically under-protected baselines for the most irregular buildings, which are the ones for which settlements and alarms are most error-prone. The layer costs well under a millisecond per building-day and a few megabytes of memory, works on top of different forecasters (LightGBM and MLP quantiles here) and is therefore compatible with portfolio-scale deployment, including with pretrained forecasting models.

## 6.4 Limitations

1. **No finite-sample guarantee for intermediate κ.** The shrinkage layer reduces to split conformal prediction only in its limits, and its reliability for $0<\kappa<\infty$ is established empirically. Distribution-free per-series (longitudinal) validity is impossible in general [44]; GHCP retains a finite-sample marginal guarantee [25] but, as our results show, at the price of little per-building adaptation.
2. **Tuning reflects the calibration population.** κ is selected on calibration buildings; if new buildings differ systematically from them, the population prior is of little value. In the UCI→BDG2 transfer the shrinkage still removed most of the under-coverage, but it was no better than self-only calibration (Table 7).
3. **Observed weather.** BDG2 experiments use observed temperature as a stand-in for day-ahead weather forecasts, which favours point accuracy for all methods equally; the UCI and cross-dataset experiments use no weather and show the same qualitative findings.
4. **Simulated onboarding.** Onboarding dates were sampled within existing meter histories. Real onboarding can coincide with commissioning problems or behaviour changes after enrolment, which our level-shift stress tests only approximate.
5. **Data coverage.** BDG2 consists mostly of campus buildings in North America and Europe and UCI has no metadata; residential portfolios, industrial sites and other climates remain to be tested.
6. **Abrupt changes and small pools.** Because past own scores remain in the mixture, level shifts during onboarding increase under-coverage for all strategies, although least for the shrinkage strategies (Table 6); the remaining failures of HSC-CQR are concentrated in buildings with large within-window level changes (Section 5.8). A very small calibration pool (16 buildings) also degrades reliability. Recency weighting of own scores or a combination with online miscoverage control are untested remedies.
7. **Baselines.** Large pretrained probabilistic forecasters [13] were not run because of the CPU-only budget, and the GHCP and TQA baselines are adaptations of methods designed for other settings (documented in Section 4).
8. **Per-building coverage is itself an estimate.** With about 1344 hourly observations per building, per-building coverage carries sampling noise (MACD floor ≈ 0.0066 for independent misses, higher with autocorrelation), so differences between the best strategies are partly within this noise; the paired tests address this at the population level.

# 7. Conclusion

Day-ahead prediction intervals are needed from the first days after a building is metered, and they must be reliable for each building, not just on average. Across 1,157 buildings and clients from two public datasets, pooled conformal and quantile-regression intervals left many new buildings substantially under-covered although their average coverage was close to nominal. Among the building-adaptive calibration strategies compared under one protocol — self-only calibration, adaptive conformal inference, temporal quantile adjustment, GHCP-style hierarchical pooling, quantile shrinkage and pseudo-count shrinkage of the score distribution — the latter was the most reliable: applied to conformalised quantile regression, it reduced the share of under-covered new buildings from 18.7% to 3.4% on BDG2 and from 9.5% to 0.6% on UCI with an essentially unchanged interval score, worked on top of two different forecasters, and remained beneficial for unseen sites, under meter noise, missing data, abrupt level changes, reduced calibration pools and a weak forecaster; under transfer from a different population, the benefit came from the building's own scores alone. The active ingredient is the shrinkage itself; similarity weighting and onboarding-stage matching were unnecessary, which leaves a one-parameter layer whose pseudo-count of one to two weeks of hourly scores can be set from operational priorities. Future work should combine the layer with recency weighting or online miscoverage control for abrupt changes, establish finite-sample guarantees for the shrinkage estimator, and test it with pretrained forecasting models and residential portfolios.


# CRediT authorship contribution statement

**[Author 1]:** Conceptualization, Methodology, Software, Formal analysis, Investigation, Data curation, Writing – original draft, Visualization. **[Author 2]:** Supervision, Writing – review & editing. *(To be completed by the authors.)*

# Declaration of competing interest

The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

# Declaration of generative AI and AI-assisted technologies in the manuscript preparation process

During the preparation of this work the author(s) used an AI assistant (Claude, Anthropic) to support literature screening, software development, execution of the experiments and drafting of the manuscript. All experiments were executed with the released code, and every reported number is generated automatically from the released result files. After using this tool, the author(s) reviewed and edited the content as needed and take(s) full responsibility for the content of the published article. *(Authors: verify that this statement matches your actual use and the journal's current policy.)*

# Data and code availability

Both datasets are public. BDG2 (CC-BY-4.0) is available at https://github.com/buds-lab/building-data-genome-project-2 [37], and ElectricityLoadDiagrams20112014 (CC-BY-4.0) at https://doi.org/10.24432/C58C86 [56]. The complete code (data download and cleaning, models, HSC, all baselines, experiments, statistics, figures, tables and this manuscript's numbers) is provided as supplementary material and will be released in a public repository [repository URL to be inserted upon acceptance]. `python run_all.py --mode full` reproduces all results.

# Acknowledgements

*(To be completed by the authors; no specific funding was received for this work unless stated here.)*

# References

1. Li H, Wang Z, Hong T, Piette MA. Energy flexibility of residential buildings: A systematic review of characterization and quantification methods and applications. Adv Appl Energy 2021;3:100054. https://doi.org/10.1016/j.adapen.2021.100054.
2. Hong T, Fan S. Probabilistic electric load forecasting: A tutorial review. Int J Forecast 2016;32:914–38. https://doi.org/10.1016/j.ijforecast.2015.11.011.
3. Hong T, Pinson P, Fan S, Zareipour H, Troccoli A, Hyndman RJ. Probabilistic energy forecasting: Global Energy Forecasting Competition 2014 and beyond. Int J Forecast 2016;32:896–913. https://doi.org/10.1016/j.ijforecast.2016.02.001.
4. Guo H, Huang B, Wang J. Probabilistic load forecasting for integrated energy systems using attentive quantile regression temporal convolutional network. Adv Appl Energy 2024;14:100165. https://doi.org/10.1016/j.adapen.2024.100165.
5. Nie Y, Zelikman E, Scott A, Paletta Q, Brandt A. SkyGPT: Probabilistic ultra-short-term solar forecasting using synthetic sky images from physics-constrained VideoGPT. Adv Appl Energy 2024;14:100172. https://doi.org/10.1016/j.adapen.2024.100172.
6. Lindberg O, Lingfors D, Arnqvist J, van der Meer D, Munkhammar J. Day-ahead probabilistic forecasting at a co-located wind and solar power park in Sweden: Trading and forecast verification. Adv Appl Energy 2023;9:100120. https://doi.org/10.1016/j.adapen.2022.100120.
7. Amasyali K, El-Gohary NM. A review of data-driven building energy consumption prediction studies. Renew Sustain Energy Rev 2018;81:1192–205. https://doi.org/10.1016/j.rser.2017.04.095.
8. Ribeiro M, Grolinger K, ElYamany HF, Higashino WA, Capretz MAM. Transfer learning with seasonal and trend adjustment for cross-building energy forecasting. Energy Build 2018;165:352–63. https://doi.org/10.1016/j.enbuild.2018.01.034.
9. Fan C, Sun Y, Xiao F, Ma J, Lee D, Wang J, et al. Statistical investigations of transfer learning-based methodology for short-term building energy predictions. Appl Energy 2020;262:114499. https://doi.org/10.1016/j.apenergy.2020.114499.
10. Pinto G, Wang Z, Roy A, Hong T, Capozzoli A. Transfer learning for smart buildings: A critical review of algorithms, applications, and future perspectives. Adv Appl Energy 2022;5:100084. https://doi.org/10.1016/j.adapen.2022.100084.
11. Gao J, Chen Y, Hu W, Zhang D. An adaptive deep-learning load forecasting framework by integrating transformer and domain knowledge. Adv Appl Energy 2023;10:100142. https://doi.org/10.1016/j.adapen.2023.100142.
12. Ristovska T, González-Vidal A, Skarmeta AF, Kovatcheva E, Gotsev L. Federated transfer learning for cold-start building energy prediction under data scarcity and privacy constraints. Energy AI 2026;25:100815. https://doi.org/10.1016/j.egyai.2026.100815.
13. Emami P, Sahu A, Graf P. BuildingsBench: A large-scale dataset of 900K buildings and benchmark for short-term load forecasting. In: Advances in Neural Information Processing Systems 36 (NeurIPS 2023), Datasets and Benchmarks Track; 2023.
14. Hao Y, Yang J, Ji Z. Evaluating the reliability of cross-building load forecasting under distribution shift and sensor missingness. Appl Sci 2026;16:7984. https://doi.org/10.3390/app16167984.
15. Vovk V, Gammerman A, Shafer G. Algorithmic learning in a random world. New York: Springer; 2005. https://doi.org/10.1007/b106715.
16. Lei J, G'Sell M, Rinaldo A, Tibshirani RJ, Wasserman L. Distribution-free predictive inference for regression. J Am Stat Assoc 2018;113:1094–111. https://doi.org/10.1080/01621459.2017.1307116.
17. Angelopoulos AN, Bates S. Conformal prediction: A gentle introduction. Found Trends Mach Learn 2023;16:494–591. https://doi.org/10.1561/2200000101.
18. Suresh V, Swain A, Revathi BS, Guerrero JM. Mamba based adaptive conformal inference for probabilistic short-term load forecasting. Knowl Based Syst 2025;328:114222. https://doi.org/10.1016/j.knosys.2025.114222.
19. Moradi A, Tanneau M, Zandehshahvar R, Van Hentenryck P. Enhanced renewable energy forecasting using context-aware conformal prediction. arXiv:2510.15780 [Preprint]; 2025. https://doi.org/10.48550/arXiv.2510.15780.
20. Gibbs I, Candès E. Adaptive conformal inference under distribution shift. In: Advances in Neural Information Processing Systems 34 (NeurIPS 2021); 2021.
21. Zaffran M, Féron O, Goude Y, Josse J, Dieuleveut A. Adaptive conformal predictions for time series. In: Proceedings of the 39th International Conference on Machine Learning, PMLR 162; 2022, p. 25834–66.
22. Lin Z, Trivedi S, Sun J. Conformal prediction with temporal quantile adjustments. In: Advances in Neural Information Processing Systems 35 (NeurIPS 2022); 2022.
23. Dunn R, Wasserman L, Ramdas A. Distribution-free prediction sets for two-layer hierarchical models. J Am Stat Assoc 2023;118:2491–502. https://doi.org/10.1080/01621459.2022.2060112.
24. Lee Y, Barber RF, Willett R. Distribution-free inference with hierarchical data. arXiv:2306.06342 [Preprint]; 2023. https://doi.org/10.48550/arXiv.2306.06342.
25. Mallick S, Tchetgen Tchetgen E, Dobriban E, Lee Y. Generalized hierarchical conformal prediction. arXiv:2608.15500 [Preprint]; 2026. https://doi.org/10.48550/arXiv.2608.15500.
26. Shahid NF. When average calibration fails: Site-conditional federated conformal risk control. arXiv:2606.20115 [Preprint]; 2026. https://doi.org/10.48550/arXiv.2606.20115.
27. Rafe A, Das S. Socio-conformal calibration in complex survey data: Marginal validity is not enough for subgroup reliability. arXiv:2605.05562 [Preprint]; 2026. https://doi.org/10.48550/arXiv.2605.05562.
28. Zhang Z, Lu Z, Yang H. The benefit of being Bayesian in online conformal prediction. arXiv:2410.02561 [Preprint]; 2024. https://doi.org/10.48550/arXiv.2410.02561.
29. Jeon B. coldstart-conformal-solar: Analysis code for auditing cold-start conformal prediction intervals of solar irradiance forecasts at unseen stations (v1.2) [software]. Zenodo; 2026. https://doi.org/10.5281/zenodo.24002627.
30. Gneiting T, Raftery AE. Strictly proper scoring rules, prediction, and estimation. J Am Stat Assoc 2007;102:359–78. https://doi.org/10.1198/016214506000001437.
31. Wang Y, Gan D, Sun M, Zhang N, Lu Z, Kang C. Probabilistic individual load forecasting using pinball loss guided LSTM. Appl Energy 2019;235:10–20. https://doi.org/10.1016/j.apenergy.2018.10.078.
32. Salinas D, Flunkert V, Gasthaus J, Januschowski T. DeepAR: Probabilistic forecasting with autoregressive recurrent networks. Int J Forecast 2020;36:1181–91. https://doi.org/10.1016/j.ijforecast.2019.07.001.
33. Chen Y, Zhang D. Theory-guided deep-learning for electrical load forecasting (TgDLF) via ensemble long short-term memory. Adv Appl Energy 2021;1:100004. https://doi.org/10.1016/j.adapen.2020.100004.
34. Wang Z, Hong T, Li H, Piette MA. Predicting city-scale daily electricity consumption using data-driven models. Adv Appl Energy 2021;2:100025. https://doi.org/10.1016/j.adapen.2021.100025.
35. Shi L, Shen Z, Lyu T. Local online conformal prediction for power load forecasting intervals. Electr Power Syst Res 2026;261:113412. https://doi.org/10.1016/j.epsr.2026.113412.
36. Almeida V, Gama J. Prediction intervals for electric load forecast: Evaluation for different profiles. In: 2015 18th International Conference on Intelligent System Application to Power Systems (ISAP); 2015. https://doi.org/10.1109/isap.2015.7325539.
37. Miller C, Kathirgamanathan A, Picchetti B, Arjunan P, Park JY, Nagy Z, et al. The Building Data Genome Project 2, energy meter data from the ASHRAE Great Energy Predictor III competition. Sci Data 2020;7:368. https://doi.org/10.1038/s41597-020-00712-x.
38. Miller C, Arjunan P, Kathirgamanathan A, Fu C, Roth J, Park JY, et al. The ASHRAE Great Energy Predictor III competition: Overview and results. Sci Technol Built Environ 2020;26:1427–47. https://doi.org/10.1080/23744731.2020.1795514.
39. Papadopoulos H, Proedrou K, Vovk V, Gammerman A. Inductive confidence machines for regression. In: Machine Learning: ECML 2002. Lecture Notes in Computer Science, vol. 2430. Berlin: Springer; 2002, p. 345–56. https://doi.org/10.1007/3-540-36755-1_29.
40. Romano Y, Patterson E, Candès E. Conformalized quantile regression. In: Advances in Neural Information Processing Systems 32 (NeurIPS 2019); 2019.
41. Xu C, Xie Y. Conformal prediction interval for dynamic time-series. In: Proceedings of the 38th International Conference on Machine Learning, PMLR 139; 2021, p. 11559–69.
42. Barber RF, Candès EJ, Ramdas A, Tibshirani RJ. Conformal prediction beyond exchangeability. Ann Stat 2023;51:816–45. https://doi.org/10.1214/23-AOS2276.
43. Tibshirani RJ, Barber RF, Candès E, Ramdas A. Conformal prediction under covariate shift. In: Advances in Neural Information Processing Systems 32 (NeurIPS 2019); 2019.
44. Lin Z, Trivedi S, Sun J. Conformal prediction intervals with temporal dependence. Trans Mach Learn Res 2022. https://doi.org/10.48550/arXiv.2205.12940.
45. Batra D, Mercuri S, Khraishi R. Conformal predictions for longitudinal data. arXiv:2310.02863 [Preprint]; 2023. https://doi.org/10.48550/arXiv.2310.02863.
46. Gibbs I, Cherian JJ, Candès EJ. Conformal prediction with conditional guarantees. J R Stat Soc Series B Stat Methodol 2025;87:1100–26. https://doi.org/10.1093/jrsssb/qkaf008.
47. Ding T, Angelopoulos AN, Bates S, Jordan MI, Tibshirani RJ. Class-conditional conformal prediction with many classes. In: Advances in Neural Information Processing Systems 36 (NeurIPS 2023); 2023.
48. Fisch A, Schuster T, Jaakkola T, Barzilay R. Few-shot conformal prediction with auxiliary tasks. In: Proceedings of the 38th International Conference on Machine Learning, PMLR 139; 2021, p. 3329–39.
49. Vejling MV, Biscio CAN, Mazoyer A, Popovski P, Pandey SR. Multi-agent conformal prediction with personalized statistical validity. arXiv:2606.00717 [Preprint]; 2026. https://doi.org/10.48550/arXiv.2606.00717.
50. Bersson E, Hoff PD. Optimal conformal prediction for small areas. J Surv Stat Methodol 2024;12:1464–88. https://doi.org/10.1093/jssam/smae010.
51. Bashari M, Lotan RM, Lee Y, Dobriban E, Romano Y. Synthetic-powered predictive inference. arXiv:2505.13432 [Preprint]; 2025. https://doi.org/10.48550/arXiv.2505.13432.
52. Hong L. Conformal prediction credibility intervals. N Am Actuar J 2023;27:675–88. https://doi.org/10.1080/10920277.2022.2123364.
53. Gibson G. Bayesian conformal prediction via the Bayesian bootstrap. arXiv:2508.01418 [Preprint]; 2025. https://doi.org/10.48550/arXiv.2508.01418.
54. Koenker R, Bassett G. Regression quantiles. Econometrica 1978;46:33–50. https://doi.org/10.2307/1913643.
55. Ferguson TS. A Bayesian analysis of some nonparametric problems. Ann Stat 1973;1:209–30. https://doi.org/10.1214/aos/1176342360.
56. Trindade A. ElectricityLoadDiagrams20112014 [dataset]. UCI Machine Learning Repository; 2015. https://doi.org/10.24432/C58C86.
57. Ke G, Meng Q, Finley T, Wang T, Chen W, Ma W, et al. LightGBM: A highly efficient gradient boosting decision tree. In: Advances in Neural Information Processing Systems 30 (NIPS 2017); 2017.
58. Winkler RL. A decision-theoretic approach to interval estimation. J Am Stat Assoc 1972;67:187–91. https://doi.org/10.1080/01621459.1972.10481224.
59. ASHRAE. Guideline 14-2014: Measurement of energy, demand, and water savings. Atlanta, GA: ASHRAE; 2014.
60. Wilcoxon F. Individual comparisons by ranking methods. Biometrics Bull 1945;1:80–3. https://doi.org/10.2307/3001968.
61. Holm S. A simple sequentially rejective multiple test procedure. Scand J Stat 1979;6:65–70.
62. Kerby DS. The simple difference formula: An approach to teaching nonparametric correlation. Compr Psychol 2014;3:11.IT.3.1. https://doi.org/10.2466/11.IT.3.1.


## 2. Supplementary tables (machine-generated)

### T_ablation_BDG2.md

**Ablation, BDG2**

| Method          | Coverage      | Coverage (week 1)   | MACD          | Under-covered share   | P10 coverage   | Rel. width (median)   | Rel. IS (median)   |
|:----------------|:--------------|:--------------------|:--------------|:----------------------|:---------------|:----------------------|:-------------------|
| HSC             | 0.899 ± 0.003 | 0.880 ± 0.010       | 0.029 ± 0.002 | 0.092 ± 0.019         | 0.853 ± 0.005  | 0.413 ± 0.014         | 0.642 ± 0.024      |
| HSC -stage      | 0.898 ± 0.003 | 0.863 ± 0.010       | 0.028 ± 0.002 | 0.093 ± 0.025         | 0.853 ± 0.004  | 0.409 ± 0.014         | 0.646 ± 0.021      |
| HSC -kNN        | 0.911 ± 0.002 | 0.921 ± 0.004       | 0.029 ± 0.002 | 0.053 ± 0.009         | 0.867 ± 0.002  | 0.443 ± 0.019         | 0.642 ± 0.022      |
| HSC -shrink     | 0.841 ± 0.008 | 0.834 ± 0.016       | 0.093 ± 0.005 | 0.458 ± 0.034         | 0.689 ± 0.014  | 0.364 ± 0.009         | 0.662 ± 0.030      |
| HSC simple      | 0.910 ± 0.001 | 0.906 ± 0.006       | 0.029 ± 0.002 | 0.055 ± 0.008         | 0.865 ± 0.002  | 0.437 ± 0.018         | 0.643 ± 0.021      |
| SCP-stage       | 0.881 ± 0.009 | 0.888 ± 0.013       | 0.094 ± 0.005 | 0.290 ± 0.034         | 0.700 ± 0.020  | 0.461 ± 0.024         | 0.639 ± 0.022      |
| Self-CP         | 0.904 ± 0.003 | 0.899 ± 0.004       | 0.026 ± 0.001 | 0.058 ± 0.009         | 0.862 ± 0.003  | 0.440 ± 0.018         | 0.656 ± 0.023      |
| HSC-CQR         | 0.891 ± 0.003 | 0.885 ± 0.007       | 0.018 ± 0.001 | 0.034 ± 0.008         | 0.864 ± 0.003  | 0.385 ± 0.011         | 0.564 ± 0.024      |
| HSC-CQR -stage  | 0.892 ± 0.002 | 0.889 ± 0.006       | 0.017 ± 0.001 | 0.032 ± 0.009         | 0.865 ± 0.002  | 0.384 ± 0.010         | 0.564 ± 0.024      |
| HSC-CQR -kNN    | 0.894 ± 0.002 | 0.895 ± 0.005       | 0.017 ± 0.001 | 0.031 ± 0.009         | 0.868 ± 0.001  | 0.389 ± 0.012         | 0.563 ± 0.024      |
| HSC-CQR -shrink | 0.884 ± 0.004 | 0.879 ± 0.008       | 0.037 ± 0.001 | 0.217 ± 0.026         | 0.826 ± 0.002  | 0.377 ± 0.012         | 0.567 ± 0.023      |
| HSC-CQR fixed-κ | 0.895 ± 0.002 | 0.897 ± 0.004       | 0.015 ± 0.001 | 0.019 ± 0.008         | 0.873 ± 0.001  | 0.392 ± 0.016         | 0.566 ± 0.022      |
| Self-CQR        | 0.889 ± 0.002 | 0.864 ± 0.003       | 0.021 ± 0.001 | 0.061 ± 0.017         | 0.857 ± 0.003  | 0.395 ± 0.016         | 0.575 ± 0.018      |
| CQR             | 0.891 ± 0.004 | 0.892 ± 0.006       | 0.038 ± 0.001 | 0.187 ± 0.018         | 0.831 ± 0.003  | 0.383 ± 0.014         | 0.564 ± 0.023      |

### T_ablation_UCI.md

**Ablation, UCI**

| Method          | Coverage      | Coverage (week 1)   | MACD          | Under-covered share   | P10 coverage   | Rel. width (median)   | Rel. IS (median)   |
|:----------------|:--------------|:--------------------|:--------------|:----------------------|:---------------|:----------------------|:-------------------|
| HSC             | 0.904 ± 0.003 | 0.891 ± 0.010       | 0.021 ± 0.001 | 0.042 ± 0.026         | 0.870 ± 0.003  | 0.286 ± 0.012         | 0.418 ± 0.018      |
| HSC -stage      | 0.903 ± 0.004 | 0.880 ± 0.016       | 0.021 ± 0.001 | 0.044 ± 0.033         | 0.868 ± 0.004  | 0.282 ± 0.012         | 0.419 ± 0.016      |
| HSC -kNN        | 0.916 ± 0.006 | 0.926 ± 0.008       | 0.027 ± 0.005 | 0.029 ± 0.022         | 0.876 ± 0.004  | 0.308 ± 0.015         | 0.420 ± 0.014      |
| HSC -shrink     | 0.857 ± 0.007 | 0.846 ± 0.013       | 0.078 ± 0.004 | 0.314 ± 0.037         | 0.719 ± 0.011  | 0.254 ± 0.011         | 0.435 ± 0.030      |
| HSC simple      | 0.912 ± 0.004 | 0.917 ± 0.010       | 0.023 ± 0.002 | 0.019 ± 0.014         | 0.880 ± 0.004  | 0.299 ± 0.013         | 0.418 ± 0.014      |
| SCP-stage       | 0.903 ± 0.015 | 0.904 ± 0.017       | 0.090 ± 0.006 | 0.202 ± 0.047         | 0.771 ± 0.025  | 0.377 ± 0.031         | 0.443 ± 0.018      |
| Self-CP         | 0.908 ± 0.003 | 0.912 ± 0.003       | 0.021 ± 0.001 | 0.021 ± 0.018         | 0.878 ± 0.003  | 0.294 ± 0.012         | 0.420 ± 0.012      |
| HSC-CQR         | 0.898 ± 0.003 | 0.894 ± 0.007       | 0.014 ± 0.002 | 0.006 ± 0.009         | 0.878 ± 0.005  | 0.266 ± 0.012         | 0.368 ± 0.016      |
| HSC-CQR -stage  | 0.899 ± 0.003 | 0.897 ± 0.004       | 0.014 ± 0.003 | 0.011 ± 0.015         | 0.877 ± 0.008  | 0.265 ± 0.012         | 0.366 ± 0.015      |
| HSC-CQR -kNN    | 0.901 ± 0.004 | 0.905 ± 0.006       | 0.014 ± 0.002 | 0.011 ± 0.015         | 0.880 ± 0.007  | 0.268 ± 0.012         | 0.366 ± 0.016      |
| HSC-CQR -shrink | 0.891 ± 0.007 | 0.887 ± 0.009       | 0.031 ± 0.005 | 0.126 ± 0.040         | 0.847 ± 0.012  | 0.267 ± 0.017         | 0.369 ± 0.016      |
| HSC-CQR fixed-κ | 0.901 ± 0.003 | 0.904 ± 0.004       | 0.013 ± 0.002 | 0.004 ± 0.006         | 0.882 ± 0.005  | 0.267 ± 0.014         | 0.366 ± 0.015      |
| Self-CQR        | 0.896 ± 0.002 | 0.880 ± 0.008       | 0.016 ± 0.002 | 0.013 ± 0.019         | 0.871 ± 0.002  | 0.263 ± 0.011         | 0.372 ± 0.014      |
| CQR             | 0.899 ± 0.011 | 0.900 ± 0.010       | 0.033 ± 0.005 | 0.095 ± 0.043         | 0.856 ± 0.016  | 0.273 ± 0.019         | 0.368 ± 0.015      |

### T_alpha0.05_BDG2.md

**BDG2, nominal 95%**

| Method         | Coverage      | Coverage (week 1)   | MACD          | Under-covered share   | P10 coverage   | Rel. width (median)   | Rel. IS (median)   |
|:---------------|:--------------|:--------------------|:--------------|:----------------------|:---------------|:----------------------|:-------------------|
| HSC            | 0.950 ± 0.003 | 0.939 ± 0.009       | 0.019 ± 0.002 | 0.034 ± 0.016         | 0.918 ± 0.007  | 0.571 ± 0.017         | 0.805 ± 0.026      |
| HSC simple     | 0.957 ± 0.002 | 0.956 ± 0.002       | 0.019 ± 0.003 | 0.017 ± 0.009         | 0.927 ± 0.002  | 0.608 ± 0.024         | 0.808 ± 0.026      |
| MLP-Gauss      | 0.950 ± 0.006 | 0.956 ± 0.013       | 0.026 ± 0.002 | 0.087 ± 0.048         | 0.904 ± 0.012  | 0.537 ± 0.036         | 0.739 ± 0.044      |
| ACI            | 0.945 ± 0.006 | 0.944 ± 0.012       | 0.050 ± 0.004 | 0.189 ± 0.032         | 0.843 ± 0.017  | 0.681 ± 0.041         | 0.807 ± 0.029      |
| Self-CP        | 0.950 ± 0.002 | 0.937 ± 0.003       | 0.017 ± 0.001 | 0.028 ± 0.012         | 0.921 ± 0.003  | 0.591 ± 0.029         | 0.823 ± 0.023      |
| SCP-stage      | 0.937 ± 0.006 | 0.943 ± 0.012       | 0.059 ± 0.004 | 0.205 ± 0.027         | 0.820 ± 0.018  | 0.695 ± 0.045         | 0.810 ± 0.030      |
| SCP            | 0.937 ± 0.006 | 0.926 ± 0.012       | 0.059 ± 0.004 | 0.204 ± 0.026         | 0.821 ± 0.019  | 0.694 ± 0.044         | 0.814 ± 0.026      |
| Mondrian-usage | 0.938 ± 0.008 | 0.942 ± 0.011       | 0.058 ± 0.004 | 0.215 ± 0.046         | 0.825 ± 0.017  | 0.661 ± 0.064         | 0.879 ± 0.060      |
| Naive+SCP      | 0.940 ± 0.008 | 0.944 ± 0.008       | 0.058 ± 0.005 | 0.212 ± 0.031         | 0.823 ± 0.022  | 1.059 ± 0.081         | 1.222 ± 0.053      |
| Raw-SCP        | 0.953 ± 0.020 | 0.948 ± 0.024       | 0.071 ± 0.013 | 0.115 ± 0.049         | 0.863 ± 0.096  | 1.439 ± 0.240         | 1.831 ± 0.174      |

### T_alpha0.05_UCI.md

**UCI, nominal 95%**

| Method     | Coverage      | Coverage (week 1)   | MACD          | Under-covered share   | P10 coverage   | Rel. width (median)   | Rel. IS (median)   |
|:-----------|:--------------|:--------------------|:--------------|:----------------------|:---------------|:----------------------|:-------------------|
| HSC        | 0.953 ± 0.004 | 0.945 ± 0.009       | 0.015 ± 0.001 | 0.023 ± 0.017         | 0.928 ± 0.008  | 0.381 ± 0.022         | 0.519 ± 0.020      |
| HSC simple | 0.959 ± 0.002 | 0.959 ± 0.014       | 0.017 ± 0.002 | 0.011 ± 0.013         | 0.937 ± 0.004  | 0.412 ± 0.011         | 0.523 ± 0.018      |
| MLP-Gauss  | 0.954 ± 0.004 | 0.952 ± 0.011       | 0.020 ± 0.001 | 0.036 ± 0.019         | 0.924 ± 0.006  | 0.357 ± 0.020         | 0.480 ± 0.023      |
| ACI        | 0.959 ± 0.010 | 0.949 ± 0.015       | 0.049 ± 0.007 | 0.120 ± 0.034         | 0.892 ± 0.022  | 0.558 ± 0.070         | 0.596 ± 0.051      |
| Self-CP    | 0.954 ± 0.002 | 0.950 ± 0.004       | 0.014 ± 0.001 | 0.004 ± 0.009         | 0.932 ± 0.002  | 0.390 ± 0.024         | 0.521 ± 0.014      |
| SCP-stage  | 0.950 ± 0.015 | 0.948 ± 0.015       | 0.059 ± 0.009 | 0.135 ± 0.033         | 0.877 ± 0.030  | 0.579 ± 0.083         | 0.615 ± 0.067      |
| SCP        | 0.950 ± 0.015 | 0.934 ± 0.020       | 0.059 ± 0.009 | 0.131 ± 0.035         | 0.878 ± 0.030  | 0.576 ± 0.084         | 0.613 ± 0.066      |
| Naive+SCP  | 0.951 ± 0.008 | 0.948 ± 0.005       | 0.053 ± 0.003 | 0.162 ± 0.022         | 0.862 ± 0.027  | 0.711 ± 0.076         | 0.765 ± 0.057      |
| Raw-SCP    | 0.951 ± 0.036 | 0.945 ± 0.039       | 0.079 ± 0.024 | 0.114 ± 0.090         | 0.842 ± 0.203  | 1.998 ± 0.831         | 2.153 ± 0.676      |

### T_alpha0.2_BDG2.md

**BDG2, nominal 80%**

| Method         | Coverage      | Coverage (week 1)   | MACD          | Under-covered share   | P10 coverage   | Rel. width (median)   | Rel. IS (median)   |
|:---------------|:--------------|:--------------------|:--------------|:----------------------|:---------------|:----------------------|:-------------------|
| HSC            | 0.799 ± 0.003 | 0.776 ± 0.009       | 0.039 ± 0.002 | 0.150 ± 0.025         | 0.733 ± 0.005  | 0.277 ± 0.011         | 0.493 ± 0.025      |
| HSC simple     | 0.811 ± 0.003 | 0.804 ± 0.008       | 0.041 ± 0.002 | 0.118 ± 0.016         | 0.745 ± 0.005  | 0.287 ± 0.012         | 0.496 ± 0.021      |
| MLP-Gauss      | 0.868 ± 0.014 | 0.887 ± 0.029       | 0.077 ± 0.009 | 0.028 ± 0.018         | 0.789 ± 0.018  | 0.351 ± 0.024         | 0.479 ± 0.032      |
| ACI            | 0.794 ± 0.009 | 0.786 ± 0.014       | 0.106 ± 0.013 | 0.338 ± 0.021         | 0.614 ± 0.031  | 0.280 ± 0.012         | 0.490 ± 0.025      |
| Self-CP        | 0.809 ± 0.004 | 0.816 ± 0.004       | 0.038 ± 0.002 | 0.102 ± 0.021         | 0.750 ± 0.008  | 0.293 ± 0.012         | 0.501 ± 0.020      |
| SCP-stage      | 0.775 ± 0.011 | 0.783 ± 0.014       | 0.139 ± 0.007 | 0.383 ± 0.028         | 0.529 ± 0.030  | 0.282 ± 0.012         | 0.493 ± 0.022      |
| SCP            | 0.775 ± 0.011 | 0.752 ± 0.011       | 0.138 ± 0.007 | 0.385 ± 0.031         | 0.531 ± 0.030  | 0.281 ± 0.013         | 0.494 ± 0.021      |
| Mondrian-usage | 0.778 ± 0.015 | 0.786 ± 0.020       | 0.136 ± 0.004 | 0.378 ± 0.041         | 0.541 ± 0.018  | 0.266 ± 0.023         | 0.507 ± 0.024      |
| Naive+SCP      | 0.778 ± 0.013 | 0.787 ± 0.013       | 0.142 ± 0.006 | 0.404 ± 0.027         | 0.534 ± 0.028  | 0.402 ± 0.027         | 0.745 ± 0.033      |
| Raw-SCP        | 0.813 ± 0.025 | 0.793 ± 0.030       | 0.181 ± 0.014 | 0.279 ± 0.041         | 0.467 ± 0.094  | 0.391 ± 0.019         | 0.692 ± 0.034      |

### T_alpha0.2_UCI.md

**UCI, nominal 80%**

| Method     | Coverage      | Coverage (week 1)   | MACD          | Under-covered share   | P10 coverage   | Rel. width (median)   | Rel. IS (median)   |
|:-----------|:--------------|:--------------------|:--------------|:----------------------|:---------------|:----------------------|:-------------------|
| HSC        | 0.805 ± 0.005 | 0.791 ± 0.003       | 0.028 ± 0.001 | 0.074 ± 0.017         | 0.762 ± 0.006  | 0.198 ± 0.005         | 0.321 ± 0.013      |
| HSC simple | 0.814 ± 0.006 | 0.815 ± 0.011       | 0.031 ± 0.004 | 0.046 ± 0.033         | 0.768 ± 0.006  | 0.205 ± 0.006         | 0.322 ± 0.012      |
| MLP-Gauss  | 0.869 ± 0.007 | 0.878 ± 0.016       | 0.073 ± 0.005 | 0.008 ± 0.014         | 0.810 ± 0.017  | 0.233 ± 0.013         | 0.317 ± 0.016      |
| ACI        | 0.811 ± 0.013 | 0.810 ± 0.020       | 0.100 ± 0.018 | 0.255 ± 0.047         | 0.658 ± 0.028  | 0.223 ± 0.013         | 0.326 ± 0.011      |
| Self-CP    | 0.811 ± 0.005 | 0.824 ± 0.004       | 0.029 ± 0.002 | 0.042 ± 0.027         | 0.769 ± 0.005  | 0.205 ± 0.005         | 0.323 ± 0.011      |
| SCP-stage  | 0.805 ± 0.017 | 0.809 ± 0.019       | 0.124 ± 0.006 | 0.280 ± 0.045         | 0.614 ± 0.026  | 0.231 ± 0.013         | 0.327 ± 0.010      |
| SCP        | 0.805 ± 0.017 | 0.780 ± 0.014       | 0.124 ± 0.006 | 0.282 ± 0.044         | 0.613 ± 0.027  | 0.231 ± 0.013         | 0.328 ± 0.009      |
| Naive+SCP  | 0.807 ± 0.015 | 0.807 ± 0.016       | 0.097 ± 0.010 | 0.263 ± 0.051         | 0.638 ± 0.046  | 0.294 ± 0.013         | 0.449 ± 0.017      |
| Raw-SCP    | 0.807 ± 0.056 | 0.791 ± 0.055       | 0.208 ± 0.024 | 0.284 ± 0.086         | 0.408 ± 0.154  | 0.406 ± 0.097         | 0.559 ± 0.028      |

### T_efficiency.md

**Computational cost (4 CPU cores)**

| part              |   train_total_s |   lgb_train_s |   mlp_train_s |   n_train_rows |   lgb_pred_ms_per_target_day |   hsc_tune_s |   hsc_apply_ms_per_target_day |   scp_s |   calibration_total_s |   hsc_store_MB |
|:------------------|----------------:|--------------:|--------------:|---------------:|-----------------------------:|-------------:|------------------------------:|--------:|----------------------:|---------------:|
| main_BDG2_s0_a0.1 |         221.817 |       93.9226 |      108.361  |        1318757 |                       0.2311 |      29.2093 |                        0.3552 |  0.352  |              285.037  |        19.7944 |
| main_BDG2_s1_a0.1 |         256.459 |      130.341  |       83.5969 |        1322913 |                       0.9403 |      40.019  |                        0.5551 |  0.488  |              294.329  |        19.7944 |
| main_BDG2_s2_a0.1 |         189.055 |       76.9424 |       90.7035 |        1320185 |                       0.1375 |      44.3517 |                        0.639  |  0.4677 |              339.126  |        19.7944 |
| main_BDG2_s3_a0.1 |         238.754 |      113.983  |       89.6552 |        1318589 |                       0.7114 |      31.3224 |                        0.1747 |  0.3499 |              229.981  |        19.7944 |
| main_BDG2_s4_a0.1 |         257.499 |      114.191  |       90.1424 |        1317922 |                       1.3186 |      38.7803 |                        0.4606 |  0.3646 |              277.389  |        19.7944 |
| main_UCI_s0_a0.1  |         117.929 |       46.4723 |       65.0577 |         992746 |                       0.1631 |       6.6369 |                        0.0981 |  0.1474 |               53.165  |         7.4229 |
| main_UCI_s1_a0.1  |        2254.06  |     1316.66   |      929.31   |         998092 |                       0.1788 |       7.6092 |                        0.0675 |  0.0972 |               69.8857 |         7.4229 |
| main_UCI_s2_a0.1  |         125.871 |       49.5258 |       67.2107 |         994452 |                       0.0463 |      11.8525 |                        0.4672 |  0.108  |               93.6075 |         7.4229 |
| main_UCI_s3_a0.1  |         101.718 |       26.789  |       70.7713 |         994891 |                       0.0809 |      10.6699 |                        0.0797 |  0.159  |               77.0217 |         7.4229 |
| main_UCI_s4_a0.1  |         124.01  |       51.6016 |       64.2448 |         995880 |                       0.0618 |      11.2922 |                        0.1464 |  0.3283 |               79.1053 |         7.4229 |

### T_gen_BDG2toBDG2_nw.md

**Generalisation: BDG2->BDG2 (no weather)**

| Method          | Coverage      | Coverage (week 1)   | MACD          | Under-covered share   | P10 coverage   | Rel. width (median)   | Rel. IS (median)   |
|:----------------|:--------------|:--------------------|:--------------|:----------------------|:---------------|:----------------------|:-------------------|
| HSC-CQR         | 0.893 ± 0.004 | 0.887 ± 0.006       | 0.017 ± 0.000 | 0.029 ± 0.006         | 0.866 ± 0.004  | 0.395 ± 0.016         | 0.575 ± 0.025      |
| HSC-CQR simple  | 0.896 ± 0.003 | 0.896 ± 0.003       | 0.017 ± 0.001 | 0.022 ± 0.010         | 0.869 ± 0.004  | 0.399 ± 0.015         | 0.574 ± 0.025      |
| HSC             | 0.902 ± 0.002 | 0.883 ± 0.012       | 0.029 ± 0.002 | 0.078 ± 0.013         | 0.857 ± 0.001  | 0.429 ± 0.024         | 0.652 ± 0.019      |
| HSC simple      | 0.910 ± 0.002 | 0.905 ± 0.002       | 0.028 ± 0.001 | 0.049 ± 0.006         | 0.865 ± 0.002  | 0.453 ± 0.033         | 0.654 ± 0.009      |
| CQR             | 0.894 ± 0.003 | 0.892 ± 0.004       | 0.037 ± 0.001 | 0.174 ± 0.018         | 0.835 ± 0.007  | 0.391 ± 0.012         | 0.574 ± 0.026      |
| Self-CQR        | 0.888 ± 0.003 | 0.860 ± 0.005       | 0.022 ± 0.002 | 0.074 ± 0.008         | 0.857 ± 0.001  | 0.404 ± 0.015         | 0.583 ± 0.021      |
| ACI-CQR         | 0.897 ± 0.003 | 0.892 ± 0.003       | 0.022 ± 0.004 | 0.062 ± 0.032         | 0.861 ± 0.009  | 0.394 ± 0.013         | 0.573 ± 0.025      |
| TQA-B-CQR       | 0.896 ± 0.002 | 0.896 ± 0.003       | 0.038 ± 0.002 | 0.177 ± 0.020         | 0.836 ± 0.002  | 0.394 ± 0.012         | 0.573 ± 0.022      |
| GHCP-CQR        | 0.896 ± 0.003 | 0.899 ± 0.003       | 0.037 ± 0.001 | 0.157 ± 0.006         | 0.837 ± 0.006  | 0.393 ± 0.012         | 0.574 ± 0.026      |
| QShrink-CQR     | 0.898 ± 0.004 | 0.894 ± 0.003       | 0.021 ± 0.001 | 0.036 ± 0.010         | 0.867 ± 0.004  | 0.401 ± 0.021         | 0.575 ± 0.026      |
| QR-LGBM         | 0.873 ± 0.012 | 0.879 ± 0.009       | 0.043 ± 0.005 | 0.278 ± 0.087         | 0.815 ± 0.012  | 0.373 ± 0.007         | 0.576 ± 0.025      |
| MLP-QR          | 0.900 ± 0.006 | 0.896 ± 0.011       | 0.036 ± 0.004 | 0.126 ± 0.050         | 0.845 ± 0.012  | 0.400 ± 0.006         | 0.564 ± 0.023      |
| MLP-Gauss       | 0.929 ± 0.009 | 0.934 ± 0.014       | 0.042 ± 0.003 | 0.038 ± 0.023         | 0.873 ± 0.015  | 0.463 ± 0.047         | 0.613 ± 0.044      |
| CQR (MLP)       | 0.895 ± 0.005 | 0.897 ± 0.011       | 0.035 ± 0.004 | 0.148 ± 0.050         | 0.841 ± 0.010  | 0.395 ± 0.007         | 0.562 ± 0.023      |
| HSC-CQR (MLP)   | 0.898 ± 0.002 | 0.893 ± 0.009       | 0.020 ± 0.003 | 0.041 ± 0.022         | 0.867 ± 0.004  | 0.399 ± 0.012         | 0.562 ± 0.024      |
| ACI             | 0.894 ± 0.003 | 0.884 ± 0.010       | 0.077 ± 0.003 | 0.262 ± 0.022         | 0.750 ± 0.006  | 0.458 ± 0.026         | 0.639 ± 0.023      |
| Self-CP         | 0.905 ± 0.001 | 0.898 ± 0.002       | 0.027 ± 0.001 | 0.066 ± 0.010         | 0.861 ± 0.001  | 0.457 ± 0.031         | 0.664 ± 0.017      |
| SCP-stage       | 0.881 ± 0.006 | 0.883 ± 0.011       | 0.094 ± 0.006 | 0.289 ± 0.021         | 0.702 ± 0.024  | 0.466 ± 0.024         | 0.642 ± 0.020      |
| SCP             | 0.882 ± 0.006 | 0.861 ± 0.006       | 0.093 ± 0.006 | 0.291 ± 0.019         | 0.704 ± 0.026  | 0.466 ± 0.025         | 0.643 ± 0.015      |
| Mondrian-usage  | 0.881 ± 0.009 | 0.880 ± 0.011       | 0.093 ± 0.005 | 0.299 ± 0.019         | 0.706 ± 0.008  | 0.430 ± 0.030         | 0.669 ± 0.031      |
| Naive+SCP       | 0.876 ± 0.006 | 0.884 ± 0.006       | 0.096 ± 0.006 | 0.314 ± 0.010         | 0.692 ± 0.031  | 0.661 ± 0.041         | 0.970 ± 0.053      |
| Raw-SCP         | 0.906 ± 0.031 | 0.892 ± 0.037       | 0.119 ± 0.019 | 0.190 ± 0.069         | 0.684 ± 0.153  | 0.744 ± 0.043         | 1.117 ± 0.016      |
| HSC -stage      | 0.900 ± 0.002 | 0.866 ± 0.012       | 0.028 ± 0.002 | 0.078 ± 0.009         | 0.855 ± 0.002  | 0.428 ± 0.025         | 0.657 ± 0.017      |
| HSC -kNN        | 0.911 ± 0.002 | 0.918 ± 0.000       | 0.029 ± 0.001 | 0.046 ± 0.008         | 0.867 ± 0.003  | 0.458 ± 0.033         | 0.655 ± 0.012      |
| HSC -shrink     | 0.847 ± 0.006 | 0.838 ± 0.017       | 0.091 ± 0.004 | 0.437 ± 0.012         | 0.693 ± 0.020  | 0.375 ± 0.013         | 0.668 ± 0.029      |
| HSC-CQR -stage  | 0.893 ± 0.003 | 0.892 ± 0.006       | 0.017 ± 0.000 | 0.028 ± 0.004         | 0.866 ± 0.003  | 0.394 ± 0.017         | 0.574 ± 0.026      |
| HSC-CQR -kNN    | 0.895 ± 0.004 | 0.893 ± 0.003       | 0.018 ± 0.003 | 0.037 ± 0.018         | 0.867 ± 0.001  | 0.398 ± 0.016         | 0.575 ± 0.025      |
| HSC-CQR -shrink | 0.888 ± 0.005 | 0.882 ± 0.007       | 0.036 ± 0.001 | 0.182 ± 0.029         | 0.831 ± 0.003  | 0.387 ± 0.010         | 0.574 ± 0.026      |
| HSC-CQR fixed-κ | 0.895 ± 0.003 | 0.897 ± 0.003       | 0.015 ± 0.000 | 0.016 ± 0.004         | 0.871 ± 0.003  | 0.403 ± 0.015         | 0.575 ± 0.024      |

### T_gen_BDG2toUCI_nw.md

**Generalisation: BDG2->UCI (no weather)**

| Method          | Coverage      | Coverage (week 1)   | MACD          | Under-covered share   | P10 coverage   | Rel. width (median)   | Rel. IS (median)   |
|:----------------|:--------------|:--------------------|:--------------|:----------------------|:---------------|:----------------------|:-------------------|
| HSC-CQR         | 0.899 ± 0.002 | 0.895 ± 0.006       | 0.013 ± 0.000 | 0.004 ± 0.006         | 0.880 ± 0.002  | 0.312 ± 0.002         | 0.437 ± 0.016      |
| HSC-CQR simple  | 0.902 ± 0.003 | 0.907 ± 0.011       | 0.013 ± 0.001 | 0.007 ± 0.006         | 0.886 ± 0.003  | 0.318 ± 0.006         | 0.438 ± 0.016      |
| HSC             | 0.920 ± 0.002 | 0.885 ± 0.005       | 0.032 ± 0.005 | 0.042 ± 0.000         | 0.880 ± 0.009  | 0.361 ± 0.009         | 0.477 ± 0.018      |
| HSC simple      | 0.923 ± 0.002 | 0.901 ± 0.002       | 0.031 ± 0.003 | 0.011 ± 0.018         | 0.889 ± 0.010  | 0.372 ± 0.015         | 0.479 ± 0.017      |
| CQR             | 0.903 ± 0.013 | 0.903 ± 0.011       | 0.028 ± 0.004 | 0.056 ± 0.043         | 0.870 ± 0.011  | 0.318 ± 0.013         | 0.442 ± 0.016      |
| Self-CQR        | 0.892 ± 0.003 | 0.866 ± 0.008       | 0.016 ± 0.001 | 0.021 ± 0.028         | 0.866 ± 0.004  | 0.316 ± 0.005         | 0.447 ± 0.016      |
| ACI-CQR         | 0.905 ± 0.006 | 0.904 ± 0.009       | 0.016 ± 0.003 | 0.011 ± 0.011         | 0.884 ± 0.003  | 0.319 ± 0.009         | 0.438 ± 0.017      |
| TQA-B-CQR       | 0.901 ± 0.013 | 0.902 ± 0.011       | 0.027 ± 0.005 | 0.063 ± 0.038         | 0.867 ± 0.010  | 0.315 ± 0.012         | 0.442 ± 0.019      |
| GHCP-CQR        | 0.905 ± 0.013 | 0.909 ± 0.014       | 0.028 ± 0.003 | 0.049 ± 0.034         | 0.873 ± 0.009  | 0.321 ± 0.013         | 0.443 ± 0.015      |
| QShrink-CQR     | 0.903 ± 0.004 | 0.907 ± 0.007       | 0.014 ± 0.001 | 0.004 ± 0.006         | 0.883 ± 0.003  | 0.316 ± 0.004         | 0.436 ± 0.017      |
| QR-LGBM         | 0.882 ± 0.006 | 0.889 ± 0.009       | 0.031 ± 0.006 | 0.158 ± 0.018         | 0.841 ± 0.003  | 0.301 ± 0.006         | 0.440 ± 0.017      |
| MLP-QR          | 0.908 ± 0.002 | 0.907 ± 0.015       | 0.024 ± 0.003 | 0.032 ± 0.021         | 0.873 ± 0.005  | 0.327 ± 0.004         | 0.435 ± 0.014      |
| MLP-Gauss       | 0.947 ± 0.014 | 0.948 ± 0.008       | 0.048 ± 0.014 | 0.004 ± 0.006         | 0.919 ± 0.014  | 0.384 ± 0.038         | 0.457 ± 0.024      |
| CQR (MLP)       | 0.902 ± 0.004 | 0.909 ± 0.007       | 0.024 ± 0.003 | 0.035 ± 0.026         | 0.867 ± 0.005  | 0.322 ± 0.004         | 0.435 ± 0.017      |
| HSC-CQR (MLP)   | 0.902 ± 0.000 | 0.903 ± 0.014       | 0.014 ± 0.002 | 0.011 ± 0.018         | 0.881 ± 0.003  | 0.325 ± 0.009         | 0.433 ± 0.016      |
| ACI             | 0.924 ± 0.008 | 0.892 ± 0.008       | 0.075 ± 0.004 | 0.140 ± 0.022         | 0.821 ± 0.012  | 0.446 ± 0.021         | 0.508 ± 0.017      |
| Self-CP         | 0.920 ± 0.001 | 0.900 ± 0.000       | 0.026 ± 0.001 | 0.018 ± 0.016         | 0.892 ± 0.003  | 0.366 ± 0.010         | 0.490 ± 0.023      |
| SCP-stage       | 0.916 ± 0.009 | 0.891 ± 0.009       | 0.088 ± 0.008 | 0.154 ± 0.024         | 0.801 ± 0.017  | 0.466 ± 0.024         | 0.524 ± 0.014      |
| SCP             | 0.915 ± 0.010 | 0.866 ± 0.011       | 0.087 ± 0.008 | 0.154 ± 0.024         | 0.804 ± 0.016  | 0.466 ± 0.025         | 0.527 ± 0.017      |
| Naive+SCP       | 0.941 ± 0.007 | 0.938 ± 0.012       | 0.085 ± 0.002 | 0.105 ± 0.000         | 0.848 ± 0.006  | 0.661 ± 0.041         | 0.691 ± 0.030      |
| Raw-SCP         | 0.787 ± 0.043 | 0.740 ± 0.040       | 0.195 ± 0.036 | 0.411 ± 0.079         | 0.360 ± 0.136  | 0.413 ± 0.038         | 0.758 ± 0.049      |
| HSC -stage      | 0.919 ± 0.003 | 0.874 ± 0.005       | 0.031 ± 0.005 | 0.046 ± 0.006         | 0.878 ± 0.011  | 0.362 ± 0.012         | 0.476 ± 0.019      |
| HSC -kNN        | 0.925 ± 0.002 | 0.917 ± 0.001       | 0.032 ± 0.003 | 0.007 ± 0.012         | 0.892 ± 0.009  | 0.377 ± 0.015         | 0.483 ± 0.016      |
| HSC -shrink     | 0.897 ± 0.010 | 0.850 ± 0.010       | 0.077 ± 0.008 | 0.207 ± 0.034         | 0.778 ± 0.013  | 0.397 ± 0.026         | 0.503 ± 0.008      |
| HSC-CQR -stage  | 0.899 ± 0.002 | 0.901 ± 0.011       | 0.013 ± 0.001 | 0.004 ± 0.006         | 0.881 ± 0.002  | 0.312 ± 0.001         | 0.438 ± 0.016      |
| HSC-CQR -kNN    | 0.902 ± 0.003 | 0.904 ± 0.009       | 0.013 ± 0.001 | 0.011 ± 0.011         | 0.883 ± 0.004  | 0.317 ± 0.006         | 0.437 ± 0.016      |
| HSC-CQR -shrink | 0.894 ± 0.012 | 0.890 ± 0.014       | 0.029 ± 0.008 | 0.095 ± 0.079         | 0.855 ± 0.015  | 0.308 ± 0.008         | 0.444 ± 0.014      |
| HSC-CQR fixed-κ | 0.901 ± 0.002 | 0.907 ± 0.010       | 0.011 ± 0.001 | 0.004 ± 0.006         | 0.885 ± 0.001  | 0.316 ± 0.008         | 0.439 ± 0.016      |

### T_gen_UCItoBDG2_nw.md

**Generalisation: UCI->BDG2 (no weather)**

| Method          | Coverage      | Coverage (week 1)   | MACD          | Under-covered share   | P10 coverage   | Rel. width (median)   | Rel. IS (median)   |
|:----------------|:--------------|:--------------------|:--------------|:----------------------|:---------------|:----------------------|:-------------------|
| HSC-CQR         | 0.887 ± 0.001 | 0.862 ± 0.007       | 0.023 ± 0.002 | 0.087 ± 0.040         | 0.853 ± 0.006  | 0.403 ± 0.023         | 0.605 ± 0.026      |
| HSC-CQR simple  | 0.889 ± 0.001 | 0.864 ± 0.009       | 0.022 ± 0.003 | 0.067 ± 0.036         | 0.855 ± 0.006  | 0.407 ± 0.024         | 0.603 ± 0.025      |
| HSC             | 0.897 ± 0.006 | 0.864 ± 0.027       | 0.029 ± 0.002 | 0.111 ± 0.022         | 0.848 ± 0.005  | 0.438 ± 0.043         | 0.696 ± 0.048      |
| HSC simple      | 0.905 ± 0.001 | 0.888 ± 0.006       | 0.027 ± 0.000 | 0.072 ± 0.018         | 0.859 ± 0.004  | 0.460 ± 0.020         | 0.695 ± 0.043      |
| CQR             | 0.861 ± 0.001 | 0.859 ± 0.001       | 0.060 ± 0.004 | 0.418 ± 0.029         | 0.782 ± 0.012  | 0.376 ± 0.024         | 0.613 ± 0.031      |
| Self-CQR        | 0.893 ± 0.003 | 0.852 ± 0.004       | 0.022 ± 0.002 | 0.069 ± 0.028         | 0.858 ± 0.005  | 0.426 ± 0.019         | 0.617 ± 0.027      |
| ACI-CQR         | 0.880 ± 0.011 | 0.861 ± 0.003       | 0.035 ± 0.017 | 0.209 ± 0.178         | 0.830 ± 0.036  | 0.399 ± 0.008         | 0.608 ± 0.025      |
| TQA-B-CQR       | 0.869 ± 0.004 | 0.866 ± 0.003       | 0.056 ± 0.003 | 0.374 ± 0.026         | 0.788 ± 0.009  | 0.376 ± 0.020         | 0.609 ± 0.025      |
| GHCP-CQR        | 0.869 ± 0.001 | 0.864 ± 0.005       | 0.056 ± 0.004 | 0.366 ± 0.019         | 0.790 ± 0.012  | 0.382 ± 0.024         | 0.611 ± 0.030      |
| QShrink-CQR     | 0.888 ± 0.003 | 0.870 ± 0.004       | 0.026 ± 0.006 | 0.112 ± 0.062         | 0.848 ± 0.013  | 0.404 ± 0.027         | 0.603 ± 0.025      |
| QR-LGBM         | 0.838 ± 0.003 | 0.832 ± 0.007       | 0.072 ± 0.004 | 0.555 ± 0.028         | 0.756 ± 0.013  | 0.357 ± 0.020         | 0.623 ± 0.035      |
| MLP-QR          | 0.855 ± 0.007 | 0.836 ± 0.021       | 0.061 ± 0.005 | 0.432 ± 0.042         | 0.776 ± 0.015  | 0.373 ± 0.010         | 0.623 ± 0.034      |
| MLP-Gauss       | 0.894 ± 0.011 | 0.892 ± 0.018       | 0.047 ± 0.003 | 0.231 ± 0.060         | 0.819 ± 0.013  | 0.436 ± 0.014         | 0.663 ± 0.047      |
| CQR (MLP)       | 0.861 ± 0.007 | 0.855 ± 0.014       | 0.058 ± 0.003 | 0.406 ± 0.029         | 0.782 ± 0.012  | 0.379 ± 0.012         | 0.623 ± 0.035      |
| HSC-CQR (MLP)   | 0.890 ± 0.001 | 0.854 ± 0.020       | 0.023 ± 0.004 | 0.065 ± 0.034         | 0.856 ± 0.005  | 0.417 ± 0.023         | 0.614 ± 0.026      |
| ACI             | 0.857 ± 0.012 | 0.842 ± 0.008       | 0.089 ± 0.010 | 0.387 ± 0.035         | 0.696 ± 0.032  | 0.400 ± 0.015         | 0.679 ± 0.048      |
| Self-CP         | 0.905 ± 0.002 | 0.892 ± 0.001       | 0.027 ± 0.000 | 0.078 ± 0.010         | 0.861 ± 0.002  | 0.470 ± 0.020         | 0.700 ± 0.042      |
| SCP-stage       | 0.837 ± 0.006 | 0.840 ± 0.008       | 0.112 ± 0.001 | 0.420 ± 0.024         | 0.634 ± 0.018  | 0.395 ± 0.011         | 0.681 ± 0.049      |
| SCP             | 0.837 ± 0.006 | 0.808 ± 0.006       | 0.111 ± 0.001 | 0.423 ± 0.021         | 0.635 ± 0.017  | 0.394 ± 0.012         | 0.683 ± 0.044      |
| Naive+SCP       | 0.824 ± 0.016 | 0.842 ± 0.012       | 0.123 ± 0.011 | 0.474 ± 0.043         | 0.605 ± 0.034  | 0.490 ± 0.008         | 0.958 ± 0.080      |
| Raw-SCP         | 0.963 ± 0.016 | 0.951 ± 0.023       | 0.103 ± 0.005 | 0.075 ± 0.036         | 0.898 ± 0.060  | 1.901 ± 0.389         | 2.087 ± 0.278      |
| HSC -stage      | 0.897 ± 0.004 | 0.850 ± 0.020       | 0.029 ± 0.003 | 0.108 ± 0.018         | 0.847 ± 0.006  | 0.436 ± 0.036         | 0.698 ± 0.049      |
| HSC -kNN        | 0.906 ± 0.001 | 0.897 ± 0.006       | 0.029 ± 0.002 | 0.071 ± 0.016         | 0.858 ± 0.003  | 0.459 ± 0.023         | 0.690 ± 0.048      |
| HSC -shrink     | 0.771 ± 0.025 | 0.764 ± 0.021       | 0.152 ± 0.021 | 0.657 ± 0.063         | 0.570 ± 0.025  | 0.292 ± 0.036         | 0.774 ± 0.069      |
| HSC-CQR -stage  | 0.887 ± 0.000 | 0.860 ± 0.006       | 0.023 ± 0.002 | 0.079 ± 0.024         | 0.853 ± 0.004  | 0.403 ± 0.022         | 0.604 ± 0.026      |
| HSC-CQR -kNN    | 0.890 ± 0.001 | 0.871 ± 0.002       | 0.022 ± 0.002 | 0.065 ± 0.030         | 0.856 ± 0.005  | 0.408 ± 0.024         | 0.602 ± 0.027      |
| HSC-CQR -shrink | 0.856 ± 0.004 | 0.851 ± 0.006       | 0.062 ± 0.004 | 0.441 ± 0.059         | 0.775 ± 0.012  | 0.369 ± 0.018         | 0.614 ± 0.032      |
| HSC-CQR fixed-κ | 0.892 ± 0.001 | 0.868 ± 0.006       | 0.019 ± 0.001 | 0.043 ± 0.014         | 0.863 ± 0.003  | 0.408 ± 0.025         | 0.603 ± 0.027      |

### T_gen_leave-site-out.md

**Generalisation: leave-site-out**

| Method          | Coverage      | Coverage (week 1)   | MACD          | Under-covered share   | P10 coverage   | Rel. width (median)   | Rel. IS (median)   |
|:----------------|:--------------|:--------------------|:--------------|:----------------------|:---------------|:----------------------|:-------------------|
| HSC-CQR         | 0.893 ± 0.009 | 0.888 ± 0.029       | 0.020 ± 0.004 | 0.053 ± 0.026         | 0.863 ± 0.008  | 0.374 ± 0.071         | 0.533 ± 0.116      |
| HSC-CQR simple  | 0.897 ± 0.010 | 0.896 ± 0.030       | 0.020 ± 0.004 | 0.035 ± 0.018         | 0.868 ± 0.008  | 0.380 ± 0.071         | 0.533 ± 0.116      |
| HSC             | 0.900 ± 0.013 | 0.886 ± 0.032       | 0.030 ± 0.002 | 0.107 ± 0.062         | 0.850 ± 0.015  | 0.404 ± 0.065         | 0.610 ± 0.127      |
| HSC simple      | 0.913 ± 0.012 | 0.903 ± 0.030       | 0.034 ± 0.005 | 0.068 ± 0.034         | 0.861 ± 0.011  | 0.427 ± 0.069         | 0.612 ± 0.126      |
| CQR             | 0.894 ± 0.027 | 0.896 ± 0.037       | 0.044 ± 0.008 | 0.218 ± 0.176         | 0.835 ± 0.029  | 0.374 ± 0.052         | 0.539 ± 0.117      |
| Self-CQR        | 0.889 ± 0.005 | 0.863 ± 0.006       | 0.022 ± 0.003 | 0.063 ± 0.037         | 0.859 ± 0.009  | 0.388 ± 0.088         | 0.545 ± 0.114      |
| ACI-CQR         | 0.897 ± 0.014 | 0.896 ± 0.035       | 0.026 ± 0.006 | 0.084 ± 0.067         | 0.858 ± 0.019  | 0.377 ± 0.065         | 0.534 ± 0.115      |
| TQA-B-CQR       | 0.897 ± 0.027 | 0.898 ± 0.034       | 0.043 ± 0.007 | 0.198 ± 0.175         | 0.837 ± 0.025  | 0.373 ± 0.053         | 0.541 ± 0.117      |
| GHCP-CQR        | 0.896 ± 0.027 | 0.897 ± 0.036       | 0.044 ± 0.007 | 0.203 ± 0.163         | 0.836 ± 0.029  | 0.376 ± 0.052         | 0.538 ± 0.117      |
| QShrink-CQR     | 0.900 ± 0.014 | 0.901 ± 0.032       | 0.026 ± 0.010 | 0.042 ± 0.052         | 0.864 ± 0.009  | 0.380 ± 0.068         | 0.536 ± 0.117      |
| QR-LGBM         | 0.867 ± 0.023 | 0.871 ± 0.035       | 0.049 ± 0.014 | 0.346 ± 0.205         | 0.807 ± 0.024  | 0.352 ± 0.054         | 0.539 ± 0.121      |
| MLP-QR          | 0.889 ± 0.029 | 0.898 ± 0.044       | 0.043 ± 0.011 | 0.250 ± 0.190         | 0.833 ± 0.031  | 0.379 ± 0.054         | 0.547 ± 0.108      |
| MLP-Gauss       | 0.931 ± 0.013 | 0.935 ± 0.016       | 0.045 ± 0.007 | 0.050 ± 0.040         | 0.878 ± 0.022  | 0.462 ± 0.088         | 0.584 ± 0.122      |
| CQR (MLP)       | 0.896 ± 0.024 | 0.898 ± 0.037       | 0.041 ± 0.007 | 0.191 ± 0.142         | 0.839 ± 0.025  | 0.385 ± 0.051         | 0.545 ± 0.106      |
| HSC-CQR (MLP)   | 0.895 ± 0.011 | 0.905 ± 0.036       | 0.020 ± 0.005 | 0.042 ± 0.024         | 0.866 ± 0.009  | 0.386 ± 0.065         | 0.542 ± 0.108      |
| ACI             | 0.902 ± 0.036 | 0.893 ± 0.054       | 0.075 ± 0.012 | 0.271 ± 0.140         | 0.786 ± 0.055  | 0.455 ± 0.020         | 0.627 ± 0.095      |
| Self-CP         | 0.905 ± 0.003 | 0.902 ± 0.008       | 0.026 ± 0.001 | 0.063 ± 0.021         | 0.861 ± 0.007  | 0.427 ± 0.083         | 0.619 ± 0.129      |
| SCP-stage       | 0.881 ± 0.064 | 0.890 ± 0.057       | 0.100 ± 0.028 | 0.308 ± 0.178         | 0.714 ± 0.129  | 0.457 ± 0.049         | 0.641 ± 0.105      |
| SCP             | 0.881 ± 0.063 | 0.863 ± 0.067       | 0.099 ± 0.027 | 0.305 ± 0.177         | 0.716 ± 0.130  | 0.456 ± 0.048         | 0.643 ± 0.104      |
| Mondrian-usage  | 0.872 ± 0.064 | 0.884 ± 0.057       | 0.103 ± 0.032 | 0.330 ± 0.194         | 0.703 ± 0.117  | 0.409 ± 0.028         | 0.661 ± 0.125      |
| Naive+SCP       | 0.887 ± 0.073 | 0.900 ± 0.038       | 0.099 ± 0.033 | 0.287 ± 0.232         | 0.739 ± 0.135  | 0.691 ± 0.093         | 0.957 ± 0.174      |
| Raw-SCP         | 0.891 ± 0.039 | 0.877 ± 0.045       | 0.120 ± 0.028 | 0.235 ± 0.071         | 0.676 ± 0.139  | 0.646 ± 0.255         | 1.023 ± 0.254      |
| HSC -stage      | 0.897 ± 0.013 | 0.859 ± 0.038       | 0.029 ± 0.003 | 0.121 ± 0.066         | 0.848 ± 0.017  | 0.398 ± 0.065         | 0.614 ± 0.130      |
| HSC -kNN        | 0.915 ± 0.011 | 0.923 ± 0.024       | 0.034 ± 0.005 | 0.060 ± 0.025         | 0.864 ± 0.009  | 0.433 ± 0.068         | 0.612 ± 0.121      |
| HSC -shrink     | 0.834 ± 0.077 | 0.833 ± 0.067       | 0.103 ± 0.056 | 0.457 ± 0.245         | 0.696 ± 0.106  | 0.339 ± 0.037         | 0.659 ± 0.158      |
| HSC-CQR -stage  | 0.891 ± 0.011 | 0.888 ± 0.030       | 0.022 ± 0.006 | 0.068 ± 0.043         | 0.860 ± 0.010  | 0.372 ± 0.068         | 0.534 ± 0.117      |
| HSC-CQR -kNN    | 0.897 ± 0.010 | 0.900 ± 0.030       | 0.020 ± 0.004 | 0.035 ± 0.019         | 0.869 ± 0.008  | 0.381 ± 0.071         | 0.533 ± 0.116      |
| HSC-CQR -shrink | 0.885 ± 0.023 | 0.884 ± 0.035       | 0.042 ± 0.011 | 0.243 ± 0.187         | 0.826 ± 0.027  | 0.362 ± 0.049         | 0.539 ± 0.119      |
| HSC-CQR fixed-κ | 0.896 ± 0.005 | 0.897 ± 0.025       | 0.016 ± 0.002 | 0.017 ± 0.010         | 0.870 ± 0.004  | 0.381 ± 0.077         | 0.535 ± 0.117      |

### T_main_BDG2.md

**Main results, BDG2, 90 % nominal, mean ± s.d. over seeds**

| Method          | Coverage      | Coverage (week 1)   | MACD          | Under-covered share   | P10 coverage   | Rel. width (median)   | Rel. IS (median)   |
|:----------------|:--------------|:--------------------|:--------------|:----------------------|:---------------|:----------------------|:-------------------|
| HSC-CQR         | 0.891 ± 0.003 | 0.885 ± 0.007       | 0.018 ± 0.001 | 0.034 ± 0.008         | 0.864 ± 0.003  | 0.385 ± 0.011         | 0.564 ± 0.024      |
| HSC-CQR simple  | 0.895 ± 0.002 | 0.895 ± 0.004       | 0.017 ± 0.001 | 0.029 ± 0.007         | 0.869 ± 0.001  | 0.388 ± 0.013         | 0.563 ± 0.023      |
| HSC             | 0.899 ± 0.003 | 0.880 ± 0.010       | 0.029 ± 0.002 | 0.092 ± 0.019         | 0.853 ± 0.005  | 0.413 ± 0.014         | 0.642 ± 0.024      |
| HSC simple      | 0.910 ± 0.001 | 0.906 ± 0.006       | 0.029 ± 0.002 | 0.055 ± 0.008         | 0.865 ± 0.002  | 0.437 ± 0.018         | 0.643 ± 0.021      |
| CQR             | 0.891 ± 0.004 | 0.892 ± 0.006       | 0.038 ± 0.001 | 0.187 ± 0.018         | 0.831 ± 0.003  | 0.383 ± 0.014         | 0.564 ± 0.023      |
| Self-CQR        | 0.889 ± 0.002 | 0.864 ± 0.003       | 0.021 ± 0.001 | 0.061 ± 0.017         | 0.857 ± 0.003  | 0.395 ± 0.016         | 0.575 ± 0.018      |
| ACI-CQR         | 0.894 ± 0.003 | 0.892 ± 0.005       | 0.027 ± 0.005 | 0.105 ± 0.042         | 0.850 ± 0.009  | 0.385 ± 0.013         | 0.562 ± 0.025      |
| TQA-B-CQR       | 0.894 ± 0.003 | 0.894 ± 0.004       | 0.038 ± 0.001 | 0.170 ± 0.015         | 0.836 ± 0.002  | 0.384 ± 0.012         | 0.567 ± 0.023      |
| GHCP-CQR        | 0.894 ± 0.004 | 0.897 ± 0.004       | 0.038 ± 0.001 | 0.168 ± 0.010         | 0.834 ± 0.003  | 0.385 ± 0.014         | 0.565 ± 0.023      |
| QShrink-CQR     | 0.897 ± 0.002 | 0.895 ± 0.005       | 0.022 ± 0.004 | 0.041 ± 0.016         | 0.862 ± 0.003  | 0.390 ± 0.013         | 0.562 ± 0.024      |
| QR-LGBM         | 0.859 ± 0.009 | 0.865 ± 0.008       | 0.050 ± 0.006 | 0.403 ± 0.084         | 0.799 ± 0.008  | 0.357 ± 0.013         | 0.573 ± 0.025      |
| MLP-QR          | 0.885 ± 0.010 | 0.884 ± 0.016       | 0.039 ± 0.005 | 0.206 ± 0.062         | 0.826 ± 0.015  | 0.383 ± 0.024         | 0.571 ± 0.021      |
| MLP-Gauss       | 0.924 ± 0.009 | 0.934 ± 0.019       | 0.041 ± 0.002 | 0.056 ± 0.033         | 0.867 ± 0.013  | 0.451 ± 0.030         | 0.604 ± 0.036      |
| CQR (MLP)       | 0.895 ± 0.004 | 0.897 ± 0.007       | 0.037 ± 0.004 | 0.156 ± 0.019         | 0.838 ± 0.005  | 0.392 ± 0.016         | 0.568 ± 0.023      |
| HSC-CQR (MLP)   | 0.897 ± 0.003 | 0.897 ± 0.004       | 0.018 ± 0.001 | 0.025 ± 0.010         | 0.869 ± 0.002  | 0.398 ± 0.014         | 0.569 ± 0.022      |
| ACI             | 0.893 ± 0.004 | 0.889 ± 0.013       | 0.078 ± 0.002 | 0.262 ± 0.025         | 0.746 ± 0.010  | 0.454 ± 0.024         | 0.637 ± 0.024      |
| Self-CP         | 0.904 ± 0.003 | 0.899 ± 0.004       | 0.026 ± 0.001 | 0.058 ± 0.009         | 0.862 ± 0.003  | 0.440 ± 0.018         | 0.656 ± 0.023      |
| SCP-stage       | 0.881 ± 0.009 | 0.888 ± 0.013       | 0.094 ± 0.005 | 0.290 ± 0.034         | 0.700 ± 0.020  | 0.461 ± 0.024         | 0.639 ± 0.022      |
| SCP             | 0.881 ± 0.008 | 0.863 ± 0.012       | 0.093 ± 0.005 | 0.289 ± 0.036         | 0.701 ± 0.020  | 0.460 ± 0.024         | 0.640 ± 0.023      |
| Mondrian-usage  | 0.883 ± 0.011 | 0.887 ± 0.016       | 0.092 ± 0.004 | 0.285 ± 0.044         | 0.706 ± 0.011  | 0.435 ± 0.040         | 0.666 ± 0.031      |
| Naive+SCP       | 0.883 ± 0.011 | 0.891 ± 0.011       | 0.092 ± 0.006 | 0.304 ± 0.023         | 0.707 ± 0.032  | 0.691 ± 0.053         | 0.978 ± 0.044      |
| Raw-SCP         | 0.907 ± 0.024 | 0.895 ± 0.029       | 0.118 ± 0.014 | 0.188 ± 0.047         | 0.700 ± 0.113  | 0.769 ± 0.077         | 1.130 ± 0.034      |
| HSC -stage      | 0.898 ± 0.003 | 0.863 ± 0.010       | 0.028 ± 0.002 | 0.093 ± 0.025         | 0.853 ± 0.004  | 0.409 ± 0.014         | 0.646 ± 0.021      |
| HSC -kNN        | 0.911 ± 0.002 | 0.921 ± 0.004       | 0.029 ± 0.002 | 0.053 ± 0.009         | 0.867 ± 0.002  | 0.443 ± 0.019         | 0.642 ± 0.022      |
| HSC -shrink     | 0.841 ± 0.008 | 0.834 ± 0.016       | 0.093 ± 0.005 | 0.458 ± 0.034         | 0.689 ± 0.014  | 0.364 ± 0.009         | 0.662 ± 0.030      |
| HSC-CQR -stage  | 0.892 ± 0.002 | 0.889 ± 0.006       | 0.017 ± 0.001 | 0.032 ± 0.009         | 0.865 ± 0.002  | 0.384 ± 0.010         | 0.564 ± 0.024      |
| HSC-CQR -kNN    | 0.894 ± 0.002 | 0.895 ± 0.005       | 0.017 ± 0.001 | 0.031 ± 0.009         | 0.868 ± 0.001  | 0.389 ± 0.012         | 0.563 ± 0.024      |
| HSC-CQR -shrink | 0.884 ± 0.004 | 0.879 ± 0.008       | 0.037 ± 0.001 | 0.217 ± 0.026         | 0.826 ± 0.002  | 0.377 ± 0.012         | 0.567 ± 0.023      |
| HSC-CQR fixed-κ | 0.895 ± 0.002 | 0.897 ± 0.004       | 0.015 ± 0.001 | 0.019 ± 0.008         | 0.873 ± 0.001  | 0.392 ± 0.016         | 0.566 ± 0.022      |

### T_main_UCI.md

**Main results, UCI, 90 % nominal, mean ± s.d. over seeds**

| Method          | Coverage      | Coverage (week 1)   | MACD          | Under-covered share   | P10 coverage   | Rel. width (median)   | Rel. IS (median)   |
|:----------------|:--------------|:--------------------|:--------------|:----------------------|:---------------|:----------------------|:-------------------|
| HSC-CQR         | 0.898 ± 0.003 | 0.894 ± 0.007       | 0.014 ± 0.002 | 0.006 ± 0.009         | 0.878 ± 0.005  | 0.266 ± 0.012         | 0.368 ± 0.016      |
| HSC-CQR simple  | 0.901 ± 0.004 | 0.902 ± 0.006       | 0.014 ± 0.003 | 0.011 ± 0.015         | 0.879 ± 0.009  | 0.267 ± 0.013         | 0.366 ± 0.015      |
| HSC             | 0.904 ± 0.003 | 0.891 ± 0.010       | 0.021 ± 0.001 | 0.042 ± 0.026         | 0.870 ± 0.003  | 0.286 ± 0.012         | 0.418 ± 0.018      |
| HSC simple      | 0.912 ± 0.004 | 0.917 ± 0.010       | 0.023 ± 0.002 | 0.019 ± 0.014         | 0.880 ± 0.004  | 0.299 ± 0.013         | 0.418 ± 0.014      |
| CQR             | 0.899 ± 0.011 | 0.900 ± 0.010       | 0.033 ± 0.005 | 0.095 ± 0.043         | 0.856 ± 0.016  | 0.273 ± 0.019         | 0.368 ± 0.015      |
| Self-CQR        | 0.896 ± 0.002 | 0.880 ± 0.008       | 0.016 ± 0.002 | 0.013 ± 0.019         | 0.871 ± 0.002  | 0.263 ± 0.011         | 0.372 ± 0.014      |
| ACI-CQR         | 0.903 ± 0.005 | 0.902 ± 0.007       | 0.020 ± 0.006 | 0.036 ± 0.031         | 0.871 ± 0.011  | 0.271 ± 0.015         | 0.366 ± 0.015      |
| TQA-B-CQR       | 0.900 ± 0.007 | 0.902 ± 0.008       | 0.032 ± 0.006 | 0.091 ± 0.041         | 0.857 ± 0.014  | 0.272 ± 0.014         | 0.368 ± 0.013      |
| GHCP-CQR        | 0.906 ± 0.010 | 0.909 ± 0.011       | 0.034 ± 0.006 | 0.078 ± 0.036         | 0.864 ± 0.016  | 0.280 ± 0.019         | 0.369 ± 0.016      |
| QShrink-CQR     | 0.902 ± 0.005 | 0.905 ± 0.006       | 0.016 ± 0.004 | 0.017 ± 0.024         | 0.879 ± 0.011  | 0.267 ± 0.012         | 0.367 ± 0.015      |
| QR-LGBM         | 0.877 ± 0.009 | 0.879 ± 0.010       | 0.035 ± 0.006 | 0.181 ± 0.069         | 0.832 ± 0.017  | 0.257 ± 0.015         | 0.368 ± 0.014      |
| MLP-QR          | 0.889 ± 0.013 | 0.886 ± 0.018       | 0.034 ± 0.008 | 0.133 ± 0.086         | 0.849 ± 0.022  | 0.268 ± 0.012         | 0.379 ± 0.017      |
| MLP-Gauss       | 0.927 ± 0.005 | 0.927 ± 0.013       | 0.037 ± 0.002 | 0.025 ± 0.016         | 0.885 ± 0.011  | 0.299 ± 0.017         | 0.394 ± 0.017      |
| CQR (MLP)       | 0.899 ± 0.010 | 0.899 ± 0.011       | 0.033 ± 0.005 | 0.078 ± 0.038         | 0.860 ± 0.015  | 0.276 ± 0.012         | 0.377 ± 0.016      |
| HSC-CQR (MLP)   | 0.901 ± 0.006 | 0.896 ± 0.014       | 0.016 ± 0.004 | 0.021 ± 0.025         | 0.877 ± 0.010  | 0.274 ± 0.010         | 0.378 ± 0.016      |
| ACI             | 0.911 ± 0.013 | 0.905 ± 0.016       | 0.076 ± 0.006 | 0.181 ± 0.044         | 0.795 ± 0.022  | 0.364 ± 0.026         | 0.434 ± 0.013      |
| Self-CP         | 0.908 ± 0.003 | 0.912 ± 0.003       | 0.021 ± 0.001 | 0.021 ± 0.018         | 0.878 ± 0.003  | 0.294 ± 0.012         | 0.420 ± 0.012      |
| SCP-stage       | 0.903 ± 0.015 | 0.904 ± 0.017       | 0.090 ± 0.006 | 0.202 ± 0.047         | 0.771 ± 0.025  | 0.377 ± 0.031         | 0.443 ± 0.018      |
| SCP             | 0.904 ± 0.014 | 0.884 ± 0.018       | 0.090 ± 0.006 | 0.200 ± 0.045         | 0.771 ± 0.023  | 0.376 ± 0.031         | 0.444 ± 0.018      |
| Naive+SCP       | 0.905 ± 0.008 | 0.904 ± 0.008       | 0.075 ± 0.004 | 0.215 ± 0.036         | 0.762 ± 0.018  | 0.475 ± 0.028         | 0.583 ± 0.020      |
| Raw-SCP         | 0.908 ± 0.048 | 0.898 ± 0.050       | 0.130 ± 0.028 | 0.179 ± 0.098         | 0.681 ± 0.218  | 0.967 ± 0.321         | 1.137 ± 0.207      |
| HSC -stage      | 0.903 ± 0.004 | 0.880 ± 0.016       | 0.021 ± 0.001 | 0.044 ± 0.033         | 0.868 ± 0.004  | 0.282 ± 0.012         | 0.419 ± 0.016      |
| HSC -kNN        | 0.916 ± 0.006 | 0.926 ± 0.008       | 0.027 ± 0.005 | 0.029 ± 0.022         | 0.876 ± 0.004  | 0.308 ± 0.015         | 0.420 ± 0.014      |
| HSC -shrink     | 0.857 ± 0.007 | 0.846 ± 0.013       | 0.078 ± 0.004 | 0.314 ± 0.037         | 0.719 ± 0.011  | 0.254 ± 0.011         | 0.435 ± 0.030      |
| HSC-CQR -stage  | 0.899 ± 0.003 | 0.897 ± 0.004       | 0.014 ± 0.003 | 0.011 ± 0.015         | 0.877 ± 0.008  | 0.265 ± 0.012         | 0.366 ± 0.015      |
| HSC-CQR -kNN    | 0.901 ± 0.004 | 0.905 ± 0.006       | 0.014 ± 0.002 | 0.011 ± 0.015         | 0.880 ± 0.007  | 0.268 ± 0.012         | 0.366 ± 0.016      |
| HSC-CQR -shrink | 0.891 ± 0.007 | 0.887 ± 0.009       | 0.031 ± 0.005 | 0.126 ± 0.040         | 0.847 ± 0.012  | 0.267 ± 0.017         | 0.369 ± 0.016      |
| HSC-CQR fixed-κ | 0.901 ± 0.003 | 0.904 ± 0.004       | 0.013 ± 0.002 | 0.004 ± 0.006         | 0.882 ± 0.005  | 0.267 ± 0.014         | 0.366 ± 0.015      |

### T_robustness.md

**Robustness (BDG2, mean over seeds)**

| perturb         | method         |   mean_cov |   macd |   under_rate |   rel_IS |   rel_width |
|:----------------|:---------------|-----------:|-------:|-------------:|---------:|------------:|
| calpool10       | ACI            |      0.877 |  0.075 |        0.354 |    0.627 |       0.388 |
| calpool10       | ACI-CQR        |      0.889 |  0.026 |        0.101 |    0.558 |       0.379 |
| calpool10       | CQR            |      0.883 |  0.039 |        0.216 |    0.56  |       0.375 |
| calpool10       | GHCP-CQR       |      0.911 |  0.036 |        0.087 |    0.557 |       0.411 |
| calpool10       | HSC            |      0.904 |  0.028 |        0.072 |    0.644 |       0.428 |
| calpool10       | HSC-CQR        |      0.889 |  0.02  |        0.079 |    0.562 |       0.387 |
| calpool10       | HSC-CQR simple |      0.89  |  0.02  |        0.062 |    0.56  |       0.388 |
| calpool10       | MLP-QR         |      0.885 |  0.037 |        0.196 |    0.563 |       0.381 |
| calpool10       | QR-LGBM        |      0.861 |  0.048 |        0.383 |    0.565 |       0.359 |
| calpool10       | QShrink-CQR    |      0.891 |  0.019 |        0.059 |    0.56  |       0.388 |
| calpool10       | SCP-stage      |      0.846 |  0.111 |        0.395 |    0.627 |       0.385 |
| calpool10       | Self-CP        |      0.905 |  0.026 |        0.055 |    0.65  |       0.445 |
| calpool10       | Self-CQR       |      0.889 |  0.021 |        0.07  |    0.573 |       0.395 |
| calpool10       | TQA-B-CQR      |      0.882 |  0.04  |        0.237 |    0.561 |       0.373 |
| calpool25       | ACI            |      0.9   |  0.07  |        0.235 |    0.628 |       0.449 |
| calpool25       | ACI-CQR        |      0.894 |  0.02  |        0.041 |    0.554 |       0.387 |
| calpool25       | CQR            |      0.891 |  0.037 |        0.175 |    0.557 |       0.383 |
| calpool25       | GHCP-CQR       |      0.902 |  0.037 |        0.126 |    0.557 |       0.394 |
| calpool25       | HSC            |      0.903 |  0.029 |        0.078 |    0.637 |       0.421 |
| calpool25       | HSC-CQR        |      0.893 |  0.017 |        0.032 |    0.554 |       0.388 |
| calpool25       | HSC-CQR simple |      0.895 |  0.018 |        0.036 |    0.554 |       0.388 |
| calpool25       | MLP-QR         |      0.885 |  0.037 |        0.196 |    0.563 |       0.381 |
| calpool25       | QR-LGBM        |      0.861 |  0.048 |        0.383 |    0.565 |       0.359 |
| calpool25       | QShrink-CQR    |      0.898 |  0.02  |        0.03  |    0.552 |       0.393 |
| calpool25       | SCP-stage      |      0.884 |  0.093 |        0.274 |    0.635 |       0.468 |
| calpool25       | Self-CP        |      0.906 |  0.026 |        0.053 |    0.652 |       0.447 |
| calpool25       | Self-CQR       |      0.89  |  0.021 |        0.066 |    0.573 |       0.395 |
| calpool25       | TQA-B-CQR      |      0.892 |  0.038 |        0.178 |    0.56  |       0.385 |
| calpool50       | ACI            |      0.901 |  0.066 |        0.25  |    0.63  |       0.44  |
| calpool50       | ACI-CQR        |      0.894 |  0.022 |        0.062 |    0.553 |       0.384 |
| calpool50       | CQR            |      0.891 |  0.037 |        0.178 |    0.557 |       0.382 |
| calpool50       | GHCP-CQR       |      0.896 |  0.037 |        0.148 |    0.557 |       0.387 |
| calpool50       | HSC            |      0.901 |  0.027 |        0.066 |    0.642 |       0.417 |
| calpool50       | HSC-CQR        |      0.893 |  0.018 |        0.041 |    0.553 |       0.385 |
| calpool50       | HSC-CQR simple |      0.894 |  0.018 |        0.036 |    0.554 |       0.387 |
| calpool50       | MLP-QR         |      0.885 |  0.037 |        0.196 |    0.563 |       0.381 |
| calpool50       | QR-LGBM        |      0.861 |  0.048 |        0.383 |    0.565 |       0.359 |
| calpool50       | QShrink-CQR    |      0.898 |  0.019 |        0.032 |    0.552 |       0.394 |
| calpool50       | SCP-stage      |      0.879 |  0.095 |        0.294 |    0.63  |       0.453 |
| calpool50       | Self-CP        |      0.906 |  0.026 |        0.054 |    0.652 |       0.447 |
| calpool50       | Self-CQR       |      0.89  |  0.021 |        0.066 |    0.573 |       0.395 |
| calpool50       | TQA-B-CQR      |      0.893 |  0.037 |        0.165 |    0.559 |       0.384 |
| missing20       | ACI            |      0.88  |  0.085 |        0.312 |    0.653 |       0.445 |
| missing20       | ACI-CQR        |      0.896 |  0.028 |        0.099 |    0.585 |       0.421 |
| missing20       | CQR            |      0.895 |  0.038 |        0.175 |    0.585 |       0.416 |
| missing20       | GHCP-CQR       |      0.897 |  0.037 |        0.157 |    0.583 |       0.419 |
| missing20       | HSC            |      0.901 |  0.029 |        0.086 |    0.663 |       0.437 |
| missing20       | HSC-CQR        |      0.895 |  0.019 |        0.04  |    0.585 |       0.416 |
| missing20       | HSC-CQR simple |      0.898 |  0.018 |        0.033 |    0.585 |       0.42  |
| missing20       | MLP-QR         |      0.865 |  0.047 |        0.335 |    0.632 |       0.422 |
| missing20       | QR-LGBM        |      0.87  |  0.044 |        0.302 |    0.589 |       0.395 |
| missing20       | QShrink-CQR    |      0.9   |  0.022 |        0.034 |    0.585 |       0.423 |
| missing20       | SCP-stage      |      0.866 |  0.101 |        0.339 |    0.653 |       0.447 |
| missing20       | Self-CP        |      0.913 |  0.028 |        0.04  |    0.675 |       0.492 |
| missing20       | Self-CQR       |      0.892 |  0.022 |        0.059 |    0.599 |       0.426 |
| missing20       | TQA-B-CQR      |      0.895 |  0.036 |        0.163 |    0.585 |       0.415 |
| missing40       | ACI            |      0.868 |  0.092 |        0.356 |    0.67  |       0.448 |
| missing40       | ACI-CQR        |      0.898 |  0.033 |        0.12  |    0.613 |       0.449 |
| missing40       | CQR            |      0.897 |  0.04  |        0.169 |    0.614 |       0.449 |
| missing40       | GHCP-CQR       |      0.9   |  0.04  |        0.15  |    0.613 |       0.453 |
| missing40       | HSC            |      0.902 |  0.032 |        0.107 |    0.681 |       0.464 |
| missing40       | HSC-CQR        |      0.899 |  0.023 |        0.054 |    0.611 |       0.45  |
| missing40       | HSC-CQR simple |      0.901 |  0.023 |        0.047 |    0.612 |       0.454 |
| missing40       | MLP-QR         |      0.847 |  0.063 |        0.47  |    0.699 |       0.446 |
| missing40       | QR-LGBM        |      0.874 |  0.044 |        0.287 |    0.616 |       0.428 |
| missing40       | QShrink-CQR    |      0.903 |  0.027 |        0.061 |    0.611 |       0.452 |
| missing40       | SCP-stage      |      0.855 |  0.107 |        0.37  |    0.67  |       0.447 |
| missing40       | Self-CP        |      0.92  |  0.033 |        0.037 |    0.705 |       0.531 |
| missing40       | Self-CQR       |      0.896 |  0.023 |        0.055 |    0.627 |       0.465 |
| missing40       | TQA-B-CQR      |      0.896 |  0.038 |        0.167 |    0.615 |       0.447 |
| noise15         | ACI            |      0.761 |  0.139 |        0.995 |    1.016 |       0.506 |
| noise15         | ACI-CQR        |      0.87  |  0.03  |        0.104 |    0.921 |       0.661 |
| noise15         | CQR            |      0.859 |  0.041 |        0.307 |    0.925 |       0.641 |
| noise15         | GHCP-CQR       |      0.861 |  0.039 |        0.271 |    0.924 |       0.643 |
| noise15         | HSC            |      0.88  |  0.025 |        0.103 |    0.934 |       0.673 |
| noise15         | HSC-CQR        |      0.882 |  0.018 |        0.017 |    0.917 |       0.681 |
| noise15         | HSC-CQR simple |      0.883 |  0.017 |        0.014 |    0.916 |       0.684 |
| noise15         | MLP-QR         |      0.861 |  0.039 |        0.264 |    0.95  |       0.683 |
| noise15         | QR-LGBM        |      0.846 |  0.054 |        0.519 |    0.935 |       0.619 |
| noise15         | QShrink-CQR    |      0.881 |  0.02  |        0.026 |    0.918 |       0.677 |
| noise15         | SCP-stage      |      0.696 |  0.204 |        1     |    1.093 |       0.447 |
| noise15         | Self-CP        |      0.907 |  0.019 |        0.02  |    0.938 |       0.732 |
| noise15         | Self-CQR       |      0.902 |  0.01  |        0.001 |    0.918 |       0.725 |
| noise15         | TQA-B-CQR      |      0.856 |  0.044 |        0.357 |    0.929 |       0.634 |
| noise5          | ACI            |      0.879 |  0.077 |        0.324 |    0.658 |       0.445 |
| noise5          | ACI-CQR        |      0.886 |  0.02  |        0.083 |    0.611 |       0.438 |
| noise5          | CQR            |      0.879 |  0.029 |        0.169 |    0.612 |       0.43  |
| noise5          | GHCP-CQR       |      0.882 |  0.028 |        0.154 |    0.611 |       0.433 |
| noise5          | HSC            |      0.895 |  0.024 |        0.083 |    0.67  |       0.448 |
| noise5          | HSC-CQR        |      0.889 |  0.015 |        0.028 |    0.611 |       0.443 |
| noise5          | HSC-CQR simple |      0.891 |  0.013 |        0.025 |    0.61  |       0.446 |
| noise5          | MLP-QR         |      0.876 |  0.031 |        0.192 |    0.623 |       0.435 |
| noise5          | QR-LGBM        |      0.856 |  0.045 |        0.383 |    0.615 |       0.408 |
| noise5          | QShrink-CQR    |      0.89  |  0.015 |        0.026 |    0.611 |       0.443 |
| noise5          | SCP-stage      |      0.862 |  0.098 |        0.344 |    0.657 |       0.448 |
| noise5          | Self-CP        |      0.907 |  0.024 |        0.04  |    0.683 |       0.488 |
| noise5          | Self-CQR       |      0.894 |  0.016 |        0.018 |    0.624 |       0.456 |
| noise5          | TQA-B-CQR      |      0.877 |  0.029 |        0.19  |    0.61  |       0.428 |
| shift+40        | ACI            |      0.866 |  0.073 |        0.352 |    0.727 |       0.44  |
| shift+40        | ACI-CQR        |      0.879 |  0.027 |        0.163 |    0.664 |       0.412 |
| shift+40        | CQR            |      0.869 |  0.041 |        0.303 |    0.666 |       0.397 |
| shift+40        | GHCP-CQR       |      0.872 |  0.039 |        0.283 |    0.666 |       0.4   |
| shift+40        | HSC            |      0.883 |  0.025 |        0.105 |    0.741 |       0.447 |
| shift+40        | HSC-CQR        |      0.882 |  0.021 |        0.065 |    0.665 |       0.417 |
| shift+40        | HSC-CQR simple |      0.884 |  0.02  |        0.053 |    0.665 |       0.418 |
| shift+40        | MLP-QR         |      0.867 |  0.043 |        0.314 |    0.668 |       0.389 |
| shift+40        | QR-LGBM        |      0.845 |  0.058 |        0.502 |    0.677 |       0.376 |
| shift+40        | QShrink-CQR    |      0.884 |  0.022 |        0.074 |    0.665 |       0.419 |
| shift+40        | SCP-stage      |      0.849 |  0.092 |        0.383 |    0.727 |       0.436 |
| shift+40        | Self-CP        |      0.891 |  0.024 |        0.082 |    0.756 |       0.48  |
| shift+40        | Self-CQR       |      0.883 |  0.022 |        0.079 |    0.68  |       0.441 |
| shift+40        | TQA-B-CQR      |      0.873 |  0.04  |        0.295 |    0.673 |       0.401 |
| shift-40        | ACI            |      0.834 |  0.079 |        0.49  |    0.872 |       0.474 |
| shift-40        | ACI-CQR        |      0.882 |  0.024 |        0.109 |    0.748 |       0.488 |
| shift-40        | CQR            |      0.869 |  0.039 |        0.286 |    0.75  |       0.482 |
| shift-40        | GHCP-CQR       |      0.872 |  0.037 |        0.262 |    0.749 |       0.486 |
| shift-40        | HSC            |      0.866 |  0.036 |        0.242 |    0.875 |       0.49  |
| shift-40        | HSC-CQR        |      0.884 |  0.019 |        0.042 |    0.749 |       0.494 |
| shift-40        | HSC-CQR simple |      0.887 |  0.017 |        0.036 |    0.751 |       0.499 |
| shift-40        | MLP-QR         |      0.881 |  0.035 |        0.195 |    0.723 |       0.47  |
| shift-40        | QR-LGBM        |      0.841 |  0.06  |        0.542 |    0.762 |       0.46  |
| shift-40        | QShrink-CQR    |      0.886 |  0.019 |        0.059 |    0.751 |       0.498 |
| shift-40        | SCP-stage      |      0.809 |  0.106 |        0.534 |    0.883 |       0.465 |
| shift-40        | Self-CP        |      0.877 |  0.032 |        0.19  |    0.88  |       0.531 |
| shift-40        | Self-CQR       |      0.887 |  0.023 |        0.086 |    0.762 |       0.511 |
| shift-40        | TQA-B-CQR      |      0.882 |  0.035 |        0.22  |    0.76  |       0.489 |
| weak-forecaster | ACI            |      0.894 |  0.076 |        0.271 |    0.653 |       0.473 |
| weak-forecaster | ACI-CQR        |      0.897 |  0.033 |        0.13  |    0.59  |       0.425 |
| weak-forecaster | CQR            |      0.89  |  0.052 |        0.25  |    0.592 |       0.42  |
| weak-forecaster | GHCP-CQR       |      0.893 |  0.052 |        0.231 |    0.592 |       0.423 |
| weak-forecaster | HSC            |      0.9   |  0.028 |        0.083 |    0.664 |       0.442 |
| weak-forecaster | HSC-CQR        |      0.894 |  0.021 |        0.054 |    0.593 |       0.423 |
| weak-forecaster | HSC-CQR simple |      0.898 |  0.021 |        0.043 |    0.593 |       0.425 |
| weak-forecaster | QR-LGBM        |      0.849 |  0.067 |        0.482 |    0.599 |       0.382 |
| weak-forecaster | QShrink-CQR    |      0.901 |  0.022 |        0.037 |    0.591 |       0.428 |
| weak-forecaster | SCP-stage      |      0.882 |  0.092 |        0.286 |    0.655 |       0.482 |
| weak-forecaster | Self-CP        |      0.904 |  0.027 |        0.055 |    0.683 |       0.469 |
| weak-forecaster | Self-CQR       |      0.893 |  0.022 |        0.076 |    0.602 |       0.429 |
| weak-forecaster | TQA-B-CQR      |      0.894 |  0.049 |        0.224 |    0.589 |       0.425 |


## 3. Code map (verify claims here)


- src/data/datasets.py — download, cleaning (stuck-meter runs >=24 h, interpolation <=6 h, filters), cubes.
- src/preprocessing/features.py — build(): history-masked, scale-normalised features (Eq. 1 scale);
  descriptor(): load-shape descriptor for the kNN prior.
- src/models/forecasters.py — LightGBM point/quantile, MLP Gaussian/quantile (early stopping on validation buildings).
- src/models/calibration.py — grid CDFs; pooled_quantile; neighbours (NaN-safe); prior_cdf; hsc_quantiles
  (Eq. hsc); aci_quantiles; normalized_IS (tuning objective); ghcp_quantiles; qshrink_quantiles; tqab_quantiles.
- src/training/pipeline.py — split() (building/period-disjoint), sample_training, train_models, onboard_dates,
  window_predictions, tune_hsc / tune_aci / tune_qshrink (LOBO on calibration buildings), run_calibration
  (all interval methods), common_mask/evaluate.
- src/experiments.py — experiment plan (E1-E8), prepared() caches, robustness perturbations, sensitivity.
- src/evaluation/metrics.py — per-building coverage, width, Winkler interval score, MACD.
- src/statistics/analysis.py — seed-level tables, paired Wilcoxon + Holm + rank-biserial + cluster bootstrap.
- src/statistics/manuscript_tables.py, error_analysis.py; manuscript/values.py (every number in the text);
  manuscript/build_docx.py; tests/test_core.py (11 tests); experiments/PREREGISTRATION.md; CHANGELOG.md.
- results/raw_results.csv (per building × seed × method), results/statistics.csv, results/run_info.json
  (tuned parameters + tuning tables), results/seed_level_metrics.csv, results/stage_curves.csv.


## 4. Review history (issues already raised and how they were resolved)

# REVIEW_HISTORY

Ten reviewer perspectives (R1 novelty/prior art, R2 methodology, R3 experimental design, R4 statistics,
R5 data & leakage, R6 robustness & generalisation, R7 computation, R8 literature & citations,
R9 associate editor, R10 hostile competitor) review the complete package in each of 10 cycles.
Per-cycle consolidated reviews: REVIEW/review_XX.md. Corrective actions: CHANGELOG.md.

## Pre-review self-audit (author, before cycle 1)
| Issue | Severity | Action | Status |
|---|---|---|---|
| Stuck-meter artefacts (Lamb site) inflate errors ~80x | Critical | stuck-run masking rule; training filter y/s<=20 | fixed (before full run) |
| HSC-CQR missing in robustness experiments | Major | moved out of ablation-only block | fixed |
| Same-score competitors for HSC-CQR missing (self-only, ACI on CQR) | Major | Self-CQR, ACI-CQR added | fixed (before full run) |
| HSC-CQR lacked component ablation | Major | -stage, -kNN, -shrink for HSC-CQR | fixed (before full run) |
| Descriptor described as "first h days" but uses last min(h,28) days | Minor | manuscript corrected | fixed |
| First full-run look (seed 0 BDG2): kNN localisation and stage matching show ~no benefit; ACI-CQR close to HSC-CQR | Major (claims) | do not claim benefit of these components unless supported across seeds/datasets; report honestly | pending full results |
