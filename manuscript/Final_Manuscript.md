---
title: "Reliable day-ahead prediction intervals for newly metered buildings: comparing and tuning conformal calibration strategies"
---

**Authors:** [Author 1]^a,\*^, [Author 2]^b^

^a^ [Department, Institution, City, Country] · ^b^ [Department, Institution, City, Country]

\* Corresponding author. E-mail: [corresponding.author@institution]

# Highlights

- Interval reliability is assessed per building during its first weeks of metering
- Pooled conformal calibration leaves many newly metered buildings under-covered
- Shrinking pooled scores toward each building's own errors restores reliability
- Interval-score tuning is flat; tune for reliability or fix one week of scores
- No method of comparable width fixes week 1; similarity priors add nothing

# Abstract

Demand response, flexibility bidding and measurement-and-verification need day-ahead prediction intervals for individual buildings, often from the first days after metering starts. Interval methods are usually judged by coverage pooled over many buildings, which can hide buildings whose intervals are systematically too narrow. We evaluate per-building interval reliability during onboarding on 842 buildings at 10 sites (Building Data Genome 2) and 315 Portuguese electricity clients, under a building- and period-disjoint protocol with five seeds, every site held out in turn, cross-country transfer and stress tests. On one global quantile forecaster we compare pooled conformalised quantile regression (CQR) with self-only, adaptive (ACI), temporal-quantile-adjustment, hierarchical and quantile-shrinkage calibration and with a pseudo-count shrinkage of the score distribution towards each building's accumulating own scores (PCS). Pooled CQR left 18.2% (BDG2) and 9.1% (UCI) of new buildings more than five points below the 90 % target. PCS, with its pseudo-count chosen by leave-one-building-out for reliability, reduced these shares to 1.4% and 0.4% without a loss in interval score. A fixed one-week pseudo-count did equally well, as did quantile shrinkage tuned the same way, whereas ACI tuned purely for coverage was more reliable only with intervals 2.4 (BDG2) and 1.2 (UCI) times as wide. No strategy of comparable width repaired first-week under-coverage (PCS: 19.4% of BDG2 buildings). Similarity-weighted priors and onboarding-stage matching added nothing, leaving a one-parameter layer that costs well under a millisecond per building-day.

**Keywords:** probabilistic load forecasting; conformal prediction; cold start; building energy; prediction intervals; credibility; demand response


# 1. Introduction

Buildings account for a large share of electricity demand, and their flexible loads are increasingly used for demand response, grid services and on-site renewable integration [1]. Most of these applications need more than a point forecast. Demand-response baselines, day-ahead flexibility commitments, measurement-and-verification and anomaly alarms act on statements of the form "tomorrow's hourly load of *this* building will lie between $L$ and $U$ with probability $1-\alpha$". If the upper bound is too low for a particular building, a capacity reservation sized by it fails repeatedly, whatever the average over the portfolio. Probabilistic load forecasting has accordingly become a central topic in energy forecasting [2,3], and recent work in this journal has developed increasingly expressive probabilistic models [4–6].

Interval forecasts are needed most when a building has just been connected to a monitoring, aggregation or demand-response platform — exactly when the least building-specific data exist. Transfer learning, federated learning and global or pretrained models now give useful point forecasts for buildings with little history [7–11]. Whether the *intervals* attached to them are reliable for each new building, and from which day, has received little attention: a recent cross-building study found that split-conformal intervals under-cover unseen buildings on average and recommended recalibration [12], but it evaluated pooled coverage and did not ask how a new building's own errors should enter the calibration.

Conformal prediction calibrates intervals around any forecaster [13–15]. Its standard guarantee is *marginal*: averaged over exchangeable test points, coverage is at least $1-\alpha$. For a fleet of newly metered buildings, this is compatible with intervals that are far too narrow for volatile buildings and needlessly wide for regular ones while pooled coverage looks perfect. Several families of remedies exist — calibration on the unit's own past errors, online adjustment of the miscoverage level [16,17], hierarchical conformal prediction for new groups [18,19], and credibility-type shrinkage of a unit's calibration towards a pooled one [20–22] — but they were developed under different assumptions and evaluated on different problems. Which of them makes day-ahead load intervals reliable for each newly metered building, from which day, at what cost in sharpness and how it should be tuned is not known.

This paper answers these questions for building loads. Our contributions are:

1. **Per-building reliability over time since metering.** We apply per-unit coverage evaluation [17,20] to building onboarding — the distribution of coverage across new buildings, the share of clearly under-covered buildings, its evolution week by week since metering started and its operational meaning for capacity reservations — on 1,157 buildings and clients from two countries, with every site held out in turn, cross-country transfer and stress tests.
2. **A head-to-head comparison of calibration strategies** under one forecaster, score and protocol: pooled CQR, self-only calibration, ACI, temporal quantile adjustment, GHCP-style hierarchical pooling, quantile-level shrinkage and pseudo-count shrinkage of the score distribution (PCS), together with direct quantile and neural baselines.
3. **Evidence on how the shrinkage should be tuned and designed.** The usual interval-score tuning is nearly flat and does not deliver per-building reliability; a reliability-aware leave-one-building-out rule does, for PCS and quantile shrinkage alike, without loss of sharpness, and a fixed one-week pseudo-count does equally well, whereas online adaptation reaches comparable reliability only with much wider intervals. Similarity-localised priors and onboarding-stage matching — the refinements of our own pre-registered design — add nothing on the CQR score, leaving a one-parameter layer that can be placed on top of any interval forecaster.

We also report what does not work: no strategy of comparable width repairs under-coverage in the first week after metering starts, and none copes with a sharp increase in day-to-day volatility. Code, data instructions and machine-generated results are released. Section 2 reviews related work, Section 3 presents the calibration layer, Section 4 the experimental setup, Section 5 the results, and Section 6 implications and limitations.


# 2. Related work

## 2.1 Probabilistic forecasting for buildings with little data

Probabilistic load forecasting uses quantile regression, likelihood models or ensembles, evaluated with the pinball loss, proper scores or interval coverage and width [2,3,23]. Global quantile and likelihood networks learn across many consumers [24,25], and recent studies in this journal developed deep models for district, city-scale and multi-energy loads and probabilistic renewable forecasts [4–6,26–28]. Conformal prediction is increasingly used as a calibration layer for load and renewable forecasts [29–31]. These studies assess reliability with *pooled* metrics for systems with long histories, although interval reliability is known to differ between load profiles [32].

For buildings with little own data, transfer learning reuses models from data-rich buildings [7–9], federated transfer learning reaches warm-start accuracy after a few weeks [10], and transfer with an interval-adjustment step targets intervals under data scarcity [33]. BuildingsBench pretrains on simulated buildings and reports zero-shot probabilistic forecasts on real buildings, including the two datasets used here [11]. A recent cross-building study found split-conformal intervals to under-cover unseen buildings on average and recommended recalibration [12]. This line of work concentrates on point accuracy or aggregate interval scores; we study the calibration layer that any of these forecasters needs and its reliability for each building.

## 2.2 Conformal calibration across units and over time

Split conformal prediction and CQR give finite-sample marginal coverage under exchangeability [13–15,34]. For time series, adaptive conformal inference (ACI) adjusts the miscoverage level online [16,35], multi-step variants account for the autocorrelation of horizon errors [36], and weighted methods bound the coverage gap under drift [37–39]. For *panels* of series, longitudinal (per-series) coverage cannot be guaranteed distribution-free in general [40]; temporal quantile adjustment (TQA) queries a series-specific quantile of the cross-sectional score distribution and evaluates the worst-covered 10 % of series [17], and unit-level residual models pursue the same goal [41]. Group-level validity is addressed by Mondrian calibration [13], conditional calibration over function classes [42], clustered calibration [43], few-shot and personalised calibration [44,45], hierarchical conformal prediction for new groups [18,46] and its generalisation (GHCP), which uses a new group's first observations with a finite-sample guarantee [19], and empirical-Bayes small-area conformal prediction [47].

Closest to this study are estimators that mix a unit's own calibration with a pooled one through the credibility weight $n/(n+n_0)$ [48,49]: shrinkage of per-site risk curves in federated conformal risk control [20], a "regularised Mondrian" that shrinks group-wise quantiles to the global one [21], Dirichlet-process-type regularisation in online conformal prediction [50,51], and a donor–local mixture with fixed pseudo-count for newly commissioned solar-irradiance stations, available as an analysis-code record that also implements pooled, distance-weighted and delayed-feedback ACI strategies [22]. We found no publication reporting results from that record, so its findings cannot be compared with ours directly. Two prior findings bear on the present question: per-site evaluation shows that average calibration can hide failing sites [20], and quantile shrinkage gave no decisive subgroup gain in survey data [21].

The pseudo-count mixture is therefore not new, and neither are per-unit coverage metrics. What is missing is evidence on *which* calibration strategy makes day-ahead **load** intervals reliable for each newly metered building — a large, heterogeneous population of units, a forecaster whose accuracy improves with history length, and a need for intervals from the first day — and on how such a strategy should be tuned. We compare the strategies under one protocol, show that the usual interval-score tuning does not deliver per-building reliability and replace it by a reliability-aware rule, test whether building similarity or onboarding stage add information, and evaluate the full distribution of per-building coverage over time since metering, across sites and countries and under stress.


# 3. Method

## 3.1 Problem setting and notation

Let $y_{b,t,j}\ge 0$ denote the metered electricity use (kWh) of building $b$ on day $t$ and hour $j\in\{0,\dots,23\}$. Building $b$ is metered from day $t_{0,b}$ onward. After $h$ days of its own history have been observed, a day-ahead forecast is issued for the 24 hours of day $t=t_{0,b}+h$; we call $h$ the *onboarding stage*. For a miscoverage level $\alpha$ (main analysis $\alpha=0.1$), the goal is an interval $C_{b,h,j}=[L_{b,h,j},U_{b,h,j}]$ whose coverage is close to $1-\alpha$ **for every individual building**, while the intervals remain as narrow as possible. The empirical target is therefore the distribution of per-building coverage across buildings, not only its mean. Three disjoint sets of buildings are used (Section 4): *training* buildings for the global forecaster, *calibration* buildings whose simulated onboarding windows provide nonconformity scores, and *target* buildings, metered in a later period, on which all methods are evaluated.

## 3.2 Scale-normalised global forecaster

Buildings differ in mean load by four orders of magnitude (Supplementary Fig. S1). Every load-derived quantity is therefore expressed relative to the scale

$$
s_{b,h}=\frac{1}{24\,m_h}\sum_{k=1}^{m_h}\sum_{j=0}^{23} y_{b,\,t-k,\,j},\qquad m_h=\min(h,7),\qquad\qquad (1)
$$

which uses only the last $m_h$ observed days. A single LightGBM model [52] is trained on the training buildings to predict $y_{b,t,j}/s_{b,h}$ from calendar variables, normalised loads of the previous 1, 2, 7 and 14 days (missing if $h$ is smaller), normalised daily statistics and hour-of-day/day-type profiles over at most the last 28 observed days, the day-to-day variability of the normalised profile, the history length $\min(h,28)$ and, for BDG2, outdoor air temperature (Supplementary Table S2). During training the history length of each sample is drawn uniformly from $\{1,\dots,28\}$ and all features are masked accordingly, so the model learns to forecast from short histories. Quantile models $f^{\mathrm{lo}},f^{\mathrm{hi}}$ (levels $\alpha/2$, $1-\alpha/2$) are trained in the same way with the pinball loss [53], giving $\hat y^{\mathrm{lo}}_{b,t,j}=s_{b,h}f^{\mathrm{lo}}(\mathbf x_{b,t,j})$ and $\hat y^{\mathrm{hi}}_{b,t,j}$.

## 3.3 Nonconformity scores

The main score is the conformalised-quantile-regression (CQR) score [15], normalised by the scale:

$$
e_{b,h,j}=\frac{\max\{\hat y^{\mathrm{lo}}_{b,t,j}-y_{b,t,j},\; y_{b,t,j}-\hat y^{\mathrm{hi}}_{b,t,j}\}}{s_{b,h}},\qquad
C_{b,h,j}=\big[\hat y^{\mathrm{lo}}_{b,t,j}-q_{b,h}\,s_{b,h},\;\hat y^{\mathrm{hi}}_{b,t,j}+q_{b,h}\,s_{b,h}\big].\qquad\qquad (2)
$$

The normalisation makes scores of buildings of different size comparable, and therefore poolable. All calibration strategies compared in this paper use the same scores and differ only in how the radius $q_{b,h}$ is obtained. The absolute residual $|y-\hat y|/s$ of a point forecast is used as a secondary score. Only hours whose reading was actually observed (not interpolated or masked by the quality rules) contribute scores.

## 3.4 Pseudo-count shrinkage of the score distribution (PCS)

Fig. 1 summarises the calibration layer.

![**Fig. 1.** Calibration layer for newly metered buildings (PCS-CQR). A global quantile forecaster is trained on scale-normalised loads of training buildings; calibration buildings provide CQR nonconformity scores; for a new building, the pooled score distribution of the calibration buildings is shrunk toward the building's own accumulating scores with pseudo-count κ, which is chosen by leave-one-building-out on calibration buildings only.](figures/Fig1_method.png){width=16.5cm}

Pooled split conformal prediction [13,14] sets $q$ to the $\lceil(1-\alpha)(N+1)\rceil$-th smallest of the $N$ pooled calibration scores. This guarantees coverage on average over exchangeable test points but cannot adapt to a building whose errors are systematically larger or smaller than average — the situation of a building that has just been metered. When the stage-$h$ forecast is issued, the building's own scores from days $1,\dots,h-1$ are available: $n_{b,h}\le 24(h-1)$ values $e_{b,1},\dots,e_{b,n_{b,h}}$. PCS uses the mixture distribution

$$
\tilde F_{b,h}(e)=\frac{\kappa\,F^{\mathrm{pop}}(e)+\sum_{i=1}^{n_{b,h}}\mathbb 1\{e_{b,i}\le e\}}{\kappa+n_{b,h}+1},\qquad
q_{b,h}=\inf\{e:\tilde F_{b,h}(e)\ge 1-\alpha\},\qquad\qquad (3)
$$

where $F^{\mathrm{pop}}=M^{-1}\sum_{c=1}^{M}\hat F_c$ is the average of the empirical score distributions of the $M$ calibration buildings, and the "+1" in the denominator is a point mass at $+\infty$ for the not-yet-observed test score, as in weighted split conformal prediction [39]. The building's own scores receive the credibility weight $n_{b,h}/(\kappa+n_{b,h}+1)$ [48], so after $\kappa/24$ days they carry as much weight as the population. The mixture numerator is the predictive distribution of a Dirichlet-process model with base measure $F^{\mathrm{pop}}$ and concentration $\kappa$ [54]; Eq. (3) adds the conformal-style point at infinity and should be read as a Dirichlet-process-motivated heuristic, not as a posterior. The same form appears in prior-regularised online conformal prediction [50], in credibility-type shrinkage of site- or group-specific conformal calibration [20,21] and, with a fixed pseudo-count, as a donor–local mixture for newly commissioned solar stations [22]; we do not claim the mechanism as new. As $\kappa\to\infty$, Eq. (3) tends to the building-weighted population quantile, which is used with the usual finite-sample correction at $\kappa=\infty$ (the correction is not applied for large finite $\kappa$). $\kappa=0$ is split conformal prediction on the building's own past scores, used — like the Self-CQR baseline — with a pooled fallback until enough own scores exist.

**Selection of κ.** $\kappa$ is selected on calibration buildings only, by leave-one-building-out (LOBO): each calibration building in turn plays the role of a new building, with $F^{\mathrm{pop}}$ built from the remaining calibration buildings, and the 56-day onboarding window is replayed. For each $\kappa\in\{0,24,48,96,168,336,672,1344,\infty\}$ two objectives are computed over the pseudo-targets: the mean interval score (Eq. 4, divided by $s$) and the mean absolute deviation of their window coverage from $1-\alpha$. The pre-registered rule minimised the interval score. Because this objective is almost flat in $\kappa$ (Section 5) and does not target per-building reliability, PCS uses a **reliability-aware rule**: among the values of $\kappa$ whose LOBO interval score is within 2 % of the minimum, choose the one with the smallest LOBO coverage deviation (ties broken by the interval score). The 2 % tolerance keeps the sharpness loss below the seed-to-seed variability of the interval score. The same rule is applied to the tuning parameters of the competing strategies (Section 4).

**Optional refinements (tested, not recommended).** The pre-registered design, called **HSC** (absolute score) and **HSC-CQR** (CQR score) below, added two building-specific refinements to Eq. (3) and selected $\kappa$ by the interval score. (i) *Onboarding-stage matching*: the prior uses only calibration scores from the same stage bin $\{1\},\{2\},\{3\},\{4..6\},\{7..13\},\{14..27\},\{28..56\}$ as $h$. (ii) *Similarity-localised prior*: $F^{\mathrm{pop}}$ is replaced by the average over the $K$ calibration buildings nearest to the new building in a descriptor of its last $\min(h,28)$ days (24 values of the normalised mean daily profile, its mean absolute day-to-day change and the log mean load; standardised Euclidean distance), with $K\in\{10,25,50,100,\text{all}\}$ selected jointly with $\kappa$. Section 5 shows that neither refinement improves reliability, so the recommended layer is the one-parameter form of Eq. (3).

**Computation and state.** Score distributions are stored as cumulative counts on a fixed grid of 4000 asinh-spaced points between $-10$ and $500$ (in units of $s$; relative spacing about 0.5 %), and the grid quantile is rounded upwards for all methods alike. A deployed PCS layer stores one shared vector $F^{\mathrm{pop}}$ and, per building, one running count vector of its own scores (16 kB as int32; alternatively the at most $24h$ raw scores). The daily update adds 24 scores and recomputes one quantile.

**Validity.** For finite $\kappa>0$, Eq. (3) does not inherit the finite-sample guarantee of split conformal prediction: neither the building's own past scores nor the calibration scores are exchangeable with its future scores, because forecast quality changes with $h$, the own scores pool all earlier stages, and load is autocorrelated. Its per-building reliability is therefore assessed empirically, including under distribution shift.


# 4. Experimental setup

## 4.1 Data

**BDG2.** The Building Data Genome Project 2 [55] provides hourly meter data for 2016–2017 from non-residential buildings on university and public campuses in North America and Europe, with site weather and metadata; it is the dataset of the ASHRAE Great Energy Predictor III competition [56]. We use the cleaned electricity meters, site air temperature (whose timestamps are in local time: the mean diurnal temperature peaks at 14–16 h at every site) and the primary-space-usage attribute. **UCI.** ElectricityLoadDiagrams20112014 [57] contains 15-min consumption of 370 Portuguese electricity clients; we aggregate to hourly energy, use 2012–2014 and mask the documented daylight-saving artefacts (zero hour in March, double hour in October). It has no weather or metadata and represents a different country, customer mix and metering infrastructure. Both datasets are CC-BY-4.0.

**Quality rules** (identical for all methods): runs of at least 24 identical readings (outage or stuck meter) are treated as missing; gaps of at most 6 h are interpolated for use as forecast *inputs* only — interpolated and masked hours never enter a nonconformity score or an evaluation; a building is retained if at most 5 % of its hours are missing in every period used and its mean load is at least 1 kWh/h. Of 1,578 BDG2 electricity meters at 19 sites, 842 buildings at 10 sites remain (the missing-data rule removes 732, the load floor 4); of 370 UCI clients, 315 remain. The missing-data rule also uses the target year, so very poorly metered buildings are excluded from the targets; Section 6.4 discusses this. Training rows whose normalised target exceeds 20 (meter restarts after near-zero history) are excluded from model fitting only.

## 4.2 Protocols

*Random-building protocol (main).* For each of five seeds, buildings are partitioned into training (50 %, one tenth of which is held out for early stopping), calibration (20 %) and target (30 %) sets. The forecaster and all calibration scores use only the training period (BDG2: 2016; UCI: 2012–2013); each calibration building is onboarded at a random date in it. Each target building is onboarded at a random date in the later period (BDG2: 2017; UCI: 2014) among windows with at least 80 % valid hours, and followed for 56 day-ahead forecasts. Features at stage $h$ use only the $h$ days since onboarding. Target buildings never influence the forecaster, the calibration scores or any tuning.

*Leave-one-site-out (BDG2).* Each of the 10 sites is held out in turn as the target set; the remaining buildings are split 70/30 into training and calibration sets, with three training seeds per site (30 trained forecasters). *Cross-dataset.* Forecaster and calibration scores from one dataset are applied to the targets of the other (BDG2→UCI, UCI→BDG2) without weather features; a BDG2→BDG2 run without weather is the reference (three seeds each). *Disjoint calibration period.* To check that calibration scores from the training period do not favour building-specific methods, the forecaster is trained on the first half of 2016 and calibration buildings are onboarded in the second half (BDG2, three seeds).

*Stress tests (BDG2, three seeds)* perturb the target buildings' onboarding windows: Gaussian meter noise of 15 % of the window mean added to history and truth, or to the history only (clean truth); 40 % of hours missing at random; a contiguous 3- or 7-day outage starting on day 3–20; a +40 % level shift from day 7 or day 28 and a −40 % shift from day 28; and random day-to-day load factors $1+\mathcal N(0,0.25^2)$ from day 28 (higher volatility than in the history). A weak forecaster is trained on 10 % of the training buildings. *Small calibration pools*: 5, 10, 20 or 40 randomly drawn calibration buildings, five draws per seed. *Other nominal levels*: all strategies are also run at 80 % and 95 %; the quantile models stay at 5 %/95 %, which the conformal radius corrects.

## 4.3 Compared calibration strategies

All strategies use the same forecaster, CQR scores and score grid (details and equations in Supplementary Section S2). **CQR** [15]: pooled, stage-matched split conformal radius. **Self-CQR**: split conformal on the building's own past scores, with the pooled radius as fallback until an own quantile exists. **ACI-CQR** [16]: adaptive conformal inference on top of the pooled distribution with daily batches of 24 feedback signals; the step size $\gamma\in\{0,10^{-4},\dots,10^{-2}\}$ is selected by LOBO. When $\alpha_h$ falls to $1/(N+1)$ or below, the radius is the largest observed calibration score. **TQA-B-CQR** [17]: temporal quantile adjustment ("budgeting" variant), ranking the building's exponentially decayed mean own score among the calibration buildings at the same stage. **GHCP-CQR**: the calibration step of generalised hierarchical conformal prediction [19], giving every calibration building and the new building one group share. **QShrink-CQR**: quantile-level shrinkage ("regularised Mondrian" [21]), $q=w\,q^{\mathrm{own}}+(1-w)\,q^{\mathrm{pool}}$ with $w=n/(n+\lambda)$ and $\lambda$ from the same grid as $\kappa$. **PCS-CQR**: Eq. (3). For ACI, QShrink and PCS, both the pre-registered interval-score rule and the reliability-aware rule are reported (labelled "(MACD)" for ACI and QShrink); in addition, **ACI-CQR (coverage only)** selects $\gamma$ by LOBO coverage deviation alone, as a reference for what unconstrained coverage-targeting costs. Fixed-pseudo-count versions (**PCS-CQR κ=168**, **QShrink-CQR λ=168**, i.e. one week of hourly scores) separate the mechanism from its tuning. **HSC-CQR** is the pre-registered configuration (stage-matched, similarity-localised prior, interval-score tuning).

Reference methods without building adaptation are direct LightGBM quantile regression (**QR-LGBM**), a multilayer perceptron with Gaussian output (**MLP-Gauss**) or pinball loss (**MLP-QR**) [24], and, on the absolute score, pooled (**SCP**, **SCP-stage**), Mondrian-by-usage, self-only (**Self-CP**), **ACI**, a seasonal-naive forecast with conformal intervals and the absolute-score versions **PCS** and **HSC**. **PCS-CQR (MLP)** applies the layer to the MLP quantile model. Hyper-parameters of the forecasters are conventional and identical for all methods (Supplementary Section S2); no method is tuned on target buildings.

## 4.4 Metrics and statistical analysis

For target building $b$ with $n_b$ observed hours in its 56-day window we compute coverage $\mathrm{cov}_b$, relative width $\overline{U-L}/\bar y_b$ and the relative interval (Winkler) score [23,58]

$$
\mathrm{IS}_b=\frac{1}{\bar y_b}\,\overline{(U-L)+\tfrac{2}{\alpha}(L-y)_+ +\tfrac{2}{\alpha}(y-U)_+}.\qquad\qquad (4)
$$

Across buildings we report the **mean absolute coverage deviation** $\mathrm{MACD}=\mathrm{mean}_b|\mathrm{cov}_b-(1-\alpha)|$, the **under-covered share** (buildings with $\mathrm{cov}_b<1-\alpha-0.05$), the 10th percentile of $\mathrm{cov}_b$, the same quantities within onboarding weeks 1, 2, 3–4 and 5–8, and medians of width and $\mathrm{IS}_b$. Two operational measures translate the upper bound into a capacity reservation (e.g. a demand-response baseline or a day-ahead flexibility commitment sized by $U$): the share of **booking failures** — buildings whose load exceeds $U$ in more than $\alpha$ of hours, twice the nominal $\alpha/2$, which is what contractual performance factors typically penalise — and the **reserve cost**, the pinball loss of $U$ at level $1-\alpha/2$ relative to mean load (booked-but-unused capacity costs $\alpha/2$ per kWh, shortfall $1-\alpha/2$). Even a perfectly calibrated building has sampling noise: with $n_b\approx1300$ hours and independent misses, its expected $|\mathrm{cov}_b-0.9|$ is 0.0066, and positive autocorrelation of misses makes it larger.

The unit of analysis is the target building; its metrics are averaged over the seeds in which it was a target. For each comparison we report the building-weighted mean paired difference with a 95 % percentile bootstrap interval (2000 resamples), the median difference with its bootstrap interval, the share of buildings that are better and the matched-pairs rank-biserial correlation. Because BDG2 buildings are clustered in 10 sites of very unequal size, BDG2 resamples whole sites, and the primary *p*-value is an exact sign-flip randomisation test in which whole sites change sign (1024 patterns, so $p\ge0.002$). UCI resamples and flips individual clients. *p*-values are Holm-adjusted [59] within each family (one proposed method, protocol, condition, nominal level and metric); building-level Wilcoxon tests are reported in the supplement. Metrics tested are $|\mathrm{cov}_b-(1-\alpha)|$ (CD), the under-covered indicator, $\mathrm{IS}_b$ and the booking-failure indicator. Seed-level summaries are mean ± standard deviation over seeds.

**Analysis plan and deviations.** The forecaster, protocols, metrics and the pre-registered HSC/HSC-CQR configurations were fixed in an internal analysis plan before the full experiments (experiments/PREREGISTRATION.md, not externally registered). Supplementary Table S1 lists every later change with its date, its reason and whether target results had been seen. These are: the GHCP, TQA-B and QShrink baselines (added after a prior-art audit); the PCS variants, fixed-pseudo-count versions and the reliability-aware rule (added after interim and review results showed that the planned interval-score tuning does not target reliability); the extended ACI grid; and the protocols added in revision (leave-one-site-out with three seeds per site, disjoint calibration period, further stress tests, small pools, other nominal levels). Results for PCS-CQR are therefore exploratory, and the planned primary comparison (HSC against the absolute-score baselines) is reported in full in Supplementary Table S23.

**Research software.** All code was written for this study in Python (LightGBM, PyTorch [60], NumPy, pandas, SciPy) with the assistance of an AI coding assistant (Claude, Anthropic), which also executed the experiments and ran independent code and manuscript audits. Correctness was checked by unit tests of leakage guards and calibration primitives (Supplementary Section S2.3), by two independent code audits whose findings and fixes are logged in the repository, and by regenerating every reported number, table and figure from the released result files.


# 5. Results

## 5.1 The reliability problem

The global LightGBM forecaster reaches a mean CV(RMSE) of 0.135 on new BDG2 buildings over their first 56 forecast days (seasonal naive: 0.197) and 0.089 on UCI clients (naive: 0.120). The point forecasts are therefore reasonable. The question is whether their intervals hold building by building.

With pooled calibration they do not (Table 1; UCI in Supplementary Table S4). Conformalised quantile regression (CQR) brings the mean per-building coverage on BDG2 to 0.891. Yet 18.2% of the new buildings are covered less than 85 % of the time, and the 10th percentile of per-building coverage is 0.829. Direct quantile regression is worse (41.6% under-covered), and so is pooled split conformal prediction on absolute residuals (29.3%). The Gaussian MLP lowers the under-covered share to 4.7% only by over-covering on average (0.927) with wider intervals. On UCI, CQR leaves 9.1% of the clients under-covered.

These are not sampling artefacts. With 1344 observed hours per building and independent misses, a perfectly calibrated interval would have an expected $|\mathrm{cov}_b-0.9|$ of 0.0066, and fewer than 0.00% of buildings would fall below 0.85. The observed under-coverage is therefore a systematic, building-specific error.

For a capacity reservation sized by the upper bound, CQR produces a booking failure — the upper bound exceeded in more than 10 % of hours, twice the nominal 5 % — for 7.3% of the BDG2 buildings.

**Table 1.** Per-building interval reliability and sharpness on BDG2 (random-building protocol, nominal 90%, 5 seeds, ≈253 target buildings per seed). MACD: mean |coverage − 0.90| over buildings (coverage over the 56-day onboarding window); Under-cov.: share of buildings with coverage below 0.85 (wk 1: first 7 forecast days only); P10: 10th percentile of per-building coverage; Rel. width and Rel. IS: medians over buildings of width and interval score divided by the building's mean load; Booking failures: share of buildings whose upper bound is exceeded in more than 10 % of hours (twice the nominal 5.0 %), e.g. a capacity reservation sized by the upper bound; Reserve cost: capacity-booking cost of the upper bound (pinball loss at 0.950) in % of mean load. Mean ± s.d. over seeds. HSC-CQR = the pre-registered configuration (similarity prior, stage matching, κ tuned on the interval score).

| Method                  | Coverage      | MACD          | Under-cov. (%)   | Under-cov. wk 1 (%)   | P10 cov.      | Rel. width    | Rel. IS       | Booking failures (%)   | Reserve cost (%)   |
|:------------------------|:--------------|:--------------|:-----------------|:----------------------|:--------------|:--------------|:--------------|:-----------------------|:-------------------|
| PCS-CQR                 | 0.895 ± 0.001 | 0.015 ± 0.001 | 1.4 ± 0.8        | 19.4 ± 2.1            | 0.871 ± 0.001 | 0.391 ± 0.014 | 0.562 ± 0.025 | 2.1 ± 1.2              | 2.1 ± 0.1          |
| PCS-CQR κ=168           | 0.895 ± 0.002 | 0.015 ± 0.001 | 1.5 ± 0.9        | 19.7 ± 2.2            | 0.871 ± 0.001 | 0.390 ± 0.014 | 0.562 ± 0.025 | 2.0 ± 1.0              | 2.1 ± 0.1          |
| HSC-CQR (pre-reg.)      | 0.892 ± 0.003 | 0.018 ± 0.001 | 3.4 ± 1.0        | 25.2 ± 3.6            | 0.865 ± 0.002 | 0.384 ± 0.011 | 0.561 ± 0.025 | 2.6 ± 1.4              | 2.1 ± 0.1          |
| QShrink-CQR (MACD)      | 0.896 ± 0.001 | 0.015 ± 0.001 | 1.3 ± 0.8        | 17.7 ± 2.5            | 0.873 ± 0.002 | 0.392 ± 0.013 | 0.562 ± 0.024 | 1.4 ± 1.1              | 2.1 ± 0.1          |
| QShrink-CQR             | 0.897 ± 0.002 | 0.021 ± 0.005 | 4.3 ± 2.8        | 20.7 ± 3.6            | 0.865 ± 0.006 | 0.387 ± 0.012 | 0.561 ± 0.024 | 2.9 ± 1.3              | 2.1 ± 0.1          |
| Self-CQR                | 0.889 ± 0.002 | 0.021 ± 0.001 | 7.6 ± 2.2        | 33.8 ± 0.9            | 0.856 ± 0.005 | 0.396 ± 0.015 | 0.571 ± 0.022 | 2.2 ± 0.9              | 2.2 ± 0.2          |
| ACI-CQR                 | 0.894 ± 0.002 | 0.025 ± 0.004 | 8.7 ± 3.5        | 23.8 ± 2.9            | 0.853 ± 0.009 | 0.384 ± 0.013 | 0.560 ± 0.024 | 3.9 ± 1.3              | 2.1 ± 0.1          |
| ACI-CQR (MACD)          | 0.895 ± 0.002 | 0.020 ± 0.001 | 4.2 ± 1.0        | 23.7 ± 2.7            | 0.862 ± 0.001 | 0.387 ± 0.012 | 0.560 ± 0.024 | 2.9 ± 1.0              | 2.1 ± 0.1          |
| ACI-CQR (coverage only) | 0.900 ± 0.000 | 0.004 ± 0.000 | 0.0 ± 0.0        | 8.9 ± 1.4             | 0.894 ± 0.001 | 0.949 ± 0.179 | 1.110 ± 0.184 | 0.1 ± 0.2              | 4.4 ± 0.7          |
| TQA-B-CQR               | 0.894 ± 0.003 | 0.039 ± 0.001 | 17.3 ± 1.6       | 23.2 ± 1.7            | 0.834 ± 0.003 | 0.382 ± 0.011 | 0.562 ± 0.024 | 6.7 ± 1.8              | 2.1 ± 0.1          |
| GHCP-CQR                | 0.893 ± 0.004 | 0.038 ± 0.002 | 17.2 ± 1.1       | 22.5 ± 2.1            | 0.831 ± 0.004 | 0.385 ± 0.013 | 0.560 ± 0.023 | 6.7 ± 1.9              | 2.1 ± 0.1          |
| CQR                     | 0.891 ± 0.004 | 0.039 ± 0.002 | 18.2 ± 1.7       | 24.2 ± 2.8            | 0.829 ± 0.003 | 0.382 ± 0.013 | 0.560 ± 0.023 | 7.3 ± 2.1              | 2.1 ± 0.1          |
| QR-LGBM                 | 0.857 ± 0.010 | 0.052 ± 0.008 | 41.6 ± 11.0      | 37.2 ± 3.5            | 0.796 ± 0.009 | 0.355 ± 0.008 | 0.570 ± 0.030 | 14.2 ± 4.2             | 2.1 ± 0.1          |
| MLP-QR                  | 0.882 ± 0.007 | 0.038 ± 0.002 | 23.2 ± 4.7       | 25.1 ± 5.2            | 0.827 ± 0.007 | 0.374 ± 0.008 | 0.562 ± 0.029 | 7.7 ± 3.8              | 2.1 ± 0.1          |
| MLP-Gauss               | 0.927 ± 0.009 | 0.042 ± 0.004 | 4.7 ± 2.1        | 9.9 ± 2.3             | 0.871 ± 0.010 | 0.455 ± 0.034 | 0.609 ± 0.037 | 3.2 ± 1.0              | 2.6 ± 0.6          |
| PCS-CQR (MLP)           | 0.895 ± 0.003 | 0.015 ± 0.001 | 1.8 ± 1.7        | 16.1 ± 2.8            | 0.871 ± 0.004 | 0.395 ± 0.017 | 0.566 ± 0.027 | 1.1 ± 0.8              | 2.1 ± 0.1          |
| CQR (MLP)               | 0.894 ± 0.004 | 0.036 ± 0.001 | 15.7 ± 2.3       | 21.5 ± 2.8            | 0.840 ± 0.004 | 0.385 ± 0.013 | 0.561 ± 0.031 | 6.2 ± 3.6              | 2.1 ± 0.1          |


## 5.2 Comparison of calibration strategies

All strategies in Table 1 above CQR use the same quantile models and the same CQR scores. They differ only in how a new building's own scores enter the calibration.

**Pseudo-count shrinkage.** PCS-CQR reduces the under-covered share from 18.2% to 1.4% on BDG2 and from 9.1% to 0.4% on UCI. The 10th-percentile coverage rises from 0.829 to 0.871, and booking failures fall from 7.3% to 2.1%. The median relative interval score is unchanged (0.562 vs 0.560). The intervals are +2% wider in median on BDG2 and -3% on UCI: PCS redistributes width from regular to volatile buildings rather than widening all of them.

The paired tests (Table 2) confirm these gains on BDG2. PCS-CQR has a smaller coverage deviation than CQR for 87% of 713 buildings (site-level randomisation test, Holm-adjusted p = 0.018). The under-covered share falls by -15.8 percentage points ([-23.5, -7.5]; p = 0.031). The interval-score difference is negligible (-0.0016; p = 1.000). The booking-failure reduction is large but, with ten sites, not significant after Holm adjustment (p = 0.070).

**Other strategies.**

- *Self-only calibration* (Self-CQR) leaves 7.6% of BDG2 buildings under-covered and has a higher interval score (p = 0.018 in favour of PCS-CQR). Its quantiles from a few own scores are noisy, and in the first week it is the worst CQR-score strategy (Section 5.5).
- *ACI* with its step size tuned for the interval score (ACI-CQR) or by the reliability-aware rule (ACI-CQR (MACD)) leaves 8.7% and 4.2% of buildings under-covered. Tuned for coverage alone, ACI is the most reliable strategy in the study (MACD 0.004, no under-covered building). The price is intervals 2.4 times as wide as PCS-CQR's on BDG2 (1.2 on UCI) and a reserve cost of 4.4% instead of 2.1% of mean load. It always selected the largest step size in the grid ($\gamma$ = 0.01).
- *TQA-B* and *GHCP* stay close to pooled CQR (17.3% and 17.2%). TQA-B bounds the quantile adjustment by design, and GHCP never gives the new building more weight than one calibration building. That weighting protects marginal validity across buildings but cannot correct a building whose errors are systematically larger than average.

**Quantile-level shrinkage.** Tuned by the same reliability-aware rule, QShrink-CQR (MACD) is statistically indistinguishable from PCS-CQR in coverage deviation (p = 0.600) and under-covered share (p = 0.875). PCS-CQR has a slightly lower interval score on BDG2 (-0.0085; p = 0.041), but not on UCI. Shrinking the score distribution and shrinking the quantile are therefore practically equivalent here.

**Other forecasters and the absolute score.** The layer is not specific to LightGBM. On the MLP quantile model it reduces the under-covered share from 15.7% (CQR) to 1.8% on BDG2 and from 8.2% to 0.8% on UCI. On absolute residuals, PCS reduces the under-covered share from 29.3% (SCP-stage) to 6.0%, but there it does no better than self-only calibration (Self-CP: 6.1%; Supplementary Table S3).

Figure 2 places all methods on the reliability–sharpness–cost plane. The CQR-score shrinkage strategies are the only ones that are both reliable and as sharp as pooled CQR.

**Table 2.** Paired per-building comparison of PCS-CQR with each strategy (random-building protocol, nominal 90 %). CD = |coverage − 0.9|; Under = under-covered indicator (percentage points); IS = relative interval score. Diff. = PCS-CQR minus baseline, building-weighted mean (negative = PCS-CQR better); 95 % CI by site-cluster bootstrap (BDG2, 10 sites) or building bootstrap (UCI); p = two-sided sign-flip randomisation test with whole sites flipped (BDG2; exact, 1024 patterns, so p ≥ 0.002) or buildings flipped (UCI), Holm-adjusted within dataset, family and metric. Median differences, rank-biserial correlations and building-level Wilcoxon tests are in Supplementary Table S23.

| Data   | Baseline           | CD: diff. [95 % CI]        | CD: p   | Under: diff. [95 % CI]   | Under: p   | IS: diff. [95 % CI]        | IS: p   |
|:-------|:-------------------|:---------------------------|:--------|:-------------------------|:-----------|:---------------------------|:--------|
| BDG2   | CQR                | -0.0237 [-0.0271, -0.0212] | 0.018   | -15.8 [-23.5, -7.5]      | 0.031      | -0.0016 [-0.0109, +0.0196] | 1.000   |
| BDG2   | QShrink-CQR (MACD) | -0.0003 [-0.0006, +0.0003] | 0.600   | +0.1 [-0.2, +0.6]        | 0.875      | -0.0085 [-0.0227, -0.0008] | 0.041   |
| BDG2   | QShrink-CQR        | -0.0066 [-0.0075, -0.0060] | 0.018   | -2.8 [-4.0, -1.4]        | 0.047      | +0.0039 [-0.0013, +0.0200] | 1.000   |
| BDG2   | Self-CQR           | -0.0060 [-0.0084, -0.0046] | 0.018   | -6.0 [-9.4, -3.6]        | 0.018      | -0.0444 [-0.1310, -0.0121] | 0.018   |
| BDG2   | ACI-CQR            | -0.0098 [-0.0124, -0.0085] | 0.018   | -7.0 [-11.2, -2.7]       | 0.039      | -0.0013 [-0.0140, +0.0192] | 1.000   |
| BDG2   | ACI-CQR (MACD)     | -0.0055 [-0.0075, -0.0045] | 0.018   | -2.7 [-4.6, -0.7]        | 0.047      | -0.0029 [-0.0129, +0.0097] | 1.000   |
| BDG2   | TQA-B-CQR          | -0.0238 [-0.0261, -0.0224] | 0.018   | -15.4 [-21.6, -8.2]      | 0.031      | -0.0031 [-0.0124, +0.0232] | 1.000   |
| BDG2   | GHCP-CQR           | -0.0234 [-0.0269, -0.0212] | 0.018   | -15.0 [-22.2, -7.3]      | 0.031      | -0.0013 [-0.0108, +0.0196] | 1.000   |
| BDG2   | HSC-CQR (pre-reg.) | -0.0026 [-0.0036, -0.0014] | 0.018   | -1.7 [-3.2, -0.6]        | 0.039      | +0.0076 [+0.0006, +0.0310] | 0.031   |
| BDG2   | PCS-CQR κ=168      | +0.0000 [-0.0001, +0.0002] | 1.000   | -0.0 [-0.2, +0.0]        | 1.000      | +0.0009 [+0.0001, +0.0033] | 0.068   |
| BDG2   | PCS-CQR +kNN+stage | -0.0005 [-0.0008, -0.0002] | 0.176   | -0.3 [-0.7, -0.1]        | 0.750      | +0.0004 [-0.0004, +0.0026] | 0.863   |
| UCI    | CQR                | -0.0202 [-0.0256, -0.0155] | <0.001  | -9.1 [-12.5, -5.9]       | <0.001     | -0.0047 [-0.0096, -0.0001] | 0.261   |
| UCI    | QShrink-CQR (MACD) | +0.0002 [-0.0002, +0.0006] | 0.439   | +0.3 [-0.4, +1.2]        | 0.749      | +0.0001 [-0.0019, +0.0018] | 1.000   |
| UCI    | QShrink-CQR        | -0.0031 [-0.0049, -0.0016] | <0.001  | -1.3 [-2.7, +0.1]        | 0.306      | +0.0033 [+0.0011, +0.0064] | 0.006   |
| UCI    | Self-CQR           | -0.0035 [-0.0045, -0.0025] | <0.001  | -1.4 [-2.7, -0.2]        | 0.203      | -0.0122 [-0.0208, -0.0068] | <0.001  |
| UCI    | ACI-CQR            | -0.0055 [-0.0071, -0.0039] | <0.001  | -2.3 [-4.2, -0.6]        | 0.140      | -0.0054 [-0.0174, +0.0020] | 1.000   |
| UCI    | ACI-CQR (MACD)     | -0.0044 [-0.0060, -0.0028] | <0.001  | -1.9 [-3.6, -0.2]        | 0.203      | -0.0058 [-0.0177, +0.0018] | 1.000   |
| UCI    | TQA-B-CQR          | -0.0188 [-0.0239, -0.0145] | <0.001  | -8.9 [-12.3, -5.6]       | <0.001     | -0.0033 [-0.0070, +0.0006] | 0.403   |
| UCI    | GHCP-CQR           | -0.0214 [-0.0269, -0.0169] | <0.001  | -7.6 [-10.9, -4.6]       | <0.001     | -0.0045 [-0.0090, -0.0002] | 0.236   |
| UCI    | HSC-CQR (pre-reg.) | -0.0009 [-0.0019, +0.0001] | 0.208   | -0.9 [-2.3, +0.4]        | 0.630      | +0.0033 [+0.0008, +0.0065] | 0.040   |
| UCI    | PCS-CQR κ=168      | +0.0006 [+0.0001, +0.0011] | 0.160   | -0.1 [-1.0, +0.9]        | 1.000      | +0.0031 [+0.0014, +0.0053] | <0.001  |
| UCI    | PCS-CQR +kNN+stage | -0.0001 [-0.0004, +0.0002] | 1.000   | -0.2 [-0.7, +0.0]        | 1.000      | +0.0028 [+0.0003, +0.0074] | 0.040   |


![**Fig. 2.** Reliability (a, MACD), sharpness (b, median relative interval score) and reserve cost (c, pinball loss of the upper bound in % of mean load) of all interval methods on BDG2 and UCI (random-building protocol, nominal 90 %; mean ± s.d. over five seeds; sorted by BDG2 MACD; PCS-CQR variants in bold).](figures/Fig5_tradeoff.png){width=16.5cm}

## 5.3 Tuning the pseudo-count

The interval score cannot select $\kappa$. Across finite $\kappa>0$ its leave-one-building-out (LOBO) value on calibration buildings varies by only 1.2 % (BDG2; UCI 1.1 %), and dropping the building's own scores altogether ($\kappa=\infty$) raises it by only 0.9 % (median over runs; Supplementary Table S20). Coverage deviation, in contrast, varies strongly with $\kappa$.

On target buildings the picture is the same (Fig. 3). The median relative interval score stays within 0.561–0.569 on BDG2 for every finite $\kappa$, while MACD ranges over 0.015–0.027 with its minimum at $\kappa$ = 168, and reaches 0.039 at $\kappa=\infty$. Too small a pseudo-count (24–48 h) also under-covers, because the quantile of a few own scores is noisy.

The pre-registered interval-score rule mostly selected $\kappa$ = 336 and left 2.9% of BDG2 buildings under-covered (PCS-CQR (IS-tuned)). The reliability-aware rule selected $\kappa\in\{$96, 168$\}$ on BDG2 and $\{$48, 96, 168$\}$ on UCI and halved that share (1.4%). The coverage-deviation difference is significant on BDG2 (p = 0.014), but the difference in the under-covered share is not (p = 0.164).

A fixed one-week pseudo-count, chosen without any data, performs as well as the tuned one: PCS-CQR κ=168 leaves 1.5% of BDG2 and 0.8% of UCI buildings under-covered (paired test vs PCS-CQR: p = 1.000). Selecting $\kappa$ by leave-*site*-out instead of leave-building-out changes nothing (1.5%). The same holds for quantile shrinkage (QShrink-CQR λ=168: 1.2%), whose interval-score-tuned version selected large $\lambda$ and is less reliable (4.3%).

![**Fig. 3.** Sensitivity of PCS-CQR to the pseudo-count κ on target buildings, with uniform (solid) and onboarding-stage-matched (dashed) prior (random-building protocol, nominal 90 %, mean over five seeds; ∞ = pooled calibration).](figures/Fig9_sensitivity.png){width=16.5cm}

## 5.4 Which design elements matter

The refinements of the pre-registered design add nothing on the CQR score (Supplementary Table S6):

- *Onboarding-stage matching of the prior* leaves MACD and the under-covered share unchanged (PCS-CQR +stage: 1.4%; dashed lines in Fig. 3).
- *A similarity-localised prior* slightly increases under-coverage (PCS-CQR +kNN: 1.8%; +kNN+stage: 1.8%).
- *The pre-registered HSC-CQR*, which combines both refinements with interval-score tuning, is less reliable than PCS-CQR (3.4%; coverage deviation p = 0.018). It also has the worst first week of all shrinkage variants (25.2% under-covered).
- *Removing the shrinkage* (κ=∞) returns pooled CQR (18.5%).

The one element that matters is therefore shrinkage toward the building's own scores, tuned for reliability or fixed at about one week.

The planned primary comparison concerned the absolute score (Supplementary Table S23, family "preregistered-abs"). Its hypothesis is only partly supported:

- HSC has a lower interval score than every planned baseline, including self-only calibration (BDG2 p = 0.018; UCI p < 0.001).
- It does not reduce per-building miscalibration relative to Self-CP (BDG2 p = 0.059; UCI p = 1.000).
- For the absolute score, stage matching does help in the first week. Without the similarity prior, stage-matched HSC leaves 14.3% of BDG2 buildings under-covered in week 1, compared with 18.7% for PCS. Absolute residuals of a forecaster with a few days of history are much larger than later ones, whereas the CQR quantile models already widen with little history.

## 5.5 Onboarding dynamics

Figure 4 follows coverage and interval score by days since metering, and Supplementary Table S5 gives the under-covered share per week.

The first week is hard for every strategy. On BDG2, 24.2% of buildings are under-covered within week 1 with CQR and 19.4% with PCS-CQR. Self-CQR is worst at 33.8%. With independent misses, sampling noise alone would put only 1.7% of 168-hour windows below 0.85. The first-week failures are real, and no strategy of comparable width repairs them. Coverage-only ACI reduces them to 8.9%, but with intervals 2.4 times as wide.

The gain of PCS-CQR over CQR grows with time since metering. In weeks 5–8 the under-covered share is 11.0% versus 20.7% on BDG2, and 4.4% versus 11.4% on UCI. Pooled strategies do not improve over the window because their radius does not learn from the building.

In the first days, the interval score falls steeply for all strategies as the forecaster's features fill (Fig. 4c, d). Self-CQR's interval score stays higher throughout.

![**Fig. 4.** Mean per-building coverage (a, b) and median relative interval score (c, d) by days of own history h (daily for h ≤ 7, then weekly means; shaded: first week) for the CQR-score calibration strategies (random-building protocol, nominal 90 %, five seeds).](figures/Fig3_stage_curves.png){width=16.5cm}

## 5.6 Generalisation, other nominal levels and stress

Table 3 reports the under-covered share of every CQR-score strategy across protocols and stress tests. MACD, interval scores and paired tests for every condition are given in Supplementary Tables S11–S18 and S23.

**Unseen sites, countries and calibration periods.**

- *Leave-one-site-out.* With every BDG2 site held out in turn, PCS-CQR leaves 2.4% of buildings under-covered, against 24.8% for CQR (p = 0.043) and 7.1% for Self-CQR (p = 0.023). It stays below 5 % at every one of the ten sites, including the two where pooled CQR fails for half or more of the buildings (Supplementary Table S12).
- *Cross-dataset.* When forecaster and calibration scores come from Portuguese clients and the targets are North American and European campus buildings (UCI → BDG2), pooled CQR fails for 41.9% of buildings. PCS-CQR fails for 4.2% (p = 0.043), because the building's own scores take over from the mismatched prior.
- *Disjoint calibration period.* Calibrating on a period disjoint from the forecaster's training period leaves the picture unchanged (PCS-CQR 1.8%, CQR 18.4%).

**Other nominal levels.** At 95 %, PCS-CQR leaves 0.3% of BDG2 buildings below 90 % coverage, against 14.7% for CQR. At 80 % the shares below 75 % are 6.3% and 16.6% (Supplementary Tables S7–S10).

**Stress tests.**

- *Shrinkage strategies are the most reliable* under missing data, contiguous outages, level shifts in either direction and a weak forecaster. Here PCS-CQR, its fixed-κ version and QShrink-CQR (MACD) stay at or below about 4 % under-covered, while pooled strategies reach 17–30 %.
- *Self-CQR is as reliable or more* when meter noise is added to history and truth (0.1% vs 0.4%, p = 1.000) and after an early level shift. In both cases the pooled prior no longer describes the building.
- *Day-to-day volatility* defeats every strategy: random daily load factors with 25 % standard deviation from day 28 leave 84.8% of buildings under-covered with PCS-CQR and 75.8% with Self-CQR (p = 0.020). Four weeks of own scores cannot anticipate an unpredictable change of this size, and a larger pseudo-count slows the adaptation further.
- *Small calibration pools.* With only 5 calibration buildings the tuned layer leaves 2.7% under-covered and the fixed one-week pseudo-count 1.7%, compared with 16.6% for CQR. LOBO tuning on very few buildings is noisy, so the fixed value is the safer choice for small pools. GHCP-CQR with 5 calibration buildings frequently returns unbounded intervals (Supplementary Table S18).

**Table 3.** Share of under-covered buildings (%, coverage < 0.85 at nominal 90 %) across protocols and stress tests (mean over runs). Leave-one-site-out: every BDG2 site held out in turn, 3 training seeds per site; cross-dataset: forecaster and calibration scores from the source dataset, no weather features (3 seeds); stress tests on BDG2 (3 seeds) perturb the target buildings' onboarding windows; small pools: 5 random calibration subsets per seed. MACD, interval scores and paired tests for every condition are in the Supplementary Tables S11–S18 and S23.

| Condition                                 |   Runs |   PCS-CQR |   PCS-CQR κ=168 | HSC-CQR (pre-reg.)   |   QShrink-CQR (MACD) |   Self-CQR |   ACI-CQR |   TQA-B-CQR |   GHCP-CQR |   CQR |
|:------------------------------------------|-------:|----------:|----------------:|:---------------------|---------------------:|-----------:|----------:|------------:|-----------:|------:|
| BDG2, random buildings                    |      5 |       1.4 |             1.5 | 3.4                  |                  1.3 |        7.6 |       8.7 |        17.3 |       17.2 |  18.2 |
| BDG2, leave-one-site-out                  |      3 |       2.4 |             2.3 | 4.6                  |                  2   |        7.1 |       7.7 |        23.6 |       23.8 |  24.8 |
| BDG2, no weather                          |      3 |       1.3 |             1.6 | 2.8                  |                  1.2 |        7.5 |       4.2 |        17.8 |       15.5 |  17.8 |
| UCI → BDG2                                |      3 |       4.2 |             4.5 | 8.7                  |                  3.4 |        8   |      16.5 |        37.7 |       37   |  41.9 |
| UCI, random clients                       |      5 |       0.4 |             0.8 | 1.3                  |                  0.2 |        1.9 |       2.7 |         9.3 |        7.6 |   9.1 |
| BDG2 → UCI                                |      3 |       0.4 |             0.4 | 0.4                  |                  0   |        2.1 |       1.1 |         6.3 |        5.3 |   5.6 |
| Calibration period disjoint from training |      3 |       1.8 |             2   | 4.0                  |                  1.6 |        7.9 |       7.4 |        18.1 |       17.3 |  18.4 |
| Weak forecaster                           |      3 |       2.8 |             3.6 | 5.1                  |                  2.8 |        7.5 |      13.8 |        22.5 |       23.8 |  25.2 |
| Meter noise 15 % (history and truth)      |      3 |       0.4 |             0.7 | 1.8                  |                  0.5 |        0.1 |      10.3 |        39.3 |       30.7 |  32.9 |
| Meter noise 15 % (history only)           |      3 |       0.3 |             0.3 | 0.4                  |                  0.5 |        1.6 |       0.8 |         0.9 |        0.9 |   1.1 |
| Missing hours 40 %                        |      3 |       2.6 |             2.9 | 6.1                  |                  2.2 |        4.9 |      10.9 |        17.4 |       16.7 |  17.7 |
| 7-day outage in weeks 1-3                 |      3 |       3.6 |             3.6 | 5.4                  |                  3   |        8.8 |       8   |        17.9 |       17.9 |  18.8 |
| Level +40 % from day 7                    |      3 |       0.5 |             0.7 | 2.2                  |                  0.5 |        0.7 |       9.2 |        26.6 |       26.7 |  28.3 |
| Level +40 % from day 28                   |      3 |       2.8 |             2.8 | 6.5                  |                  2.6 |        8.3 |      11.7 |        29.1 |       29.4 |  30.4 |
| Day-to-day volatility from day 28         |      3 |      84.8 |            85.8 | 94.2                 |                 83.1 |       75.8 |      94.6 |        90.1 |       98.9 |  99.1 |
| 10 calibration buildings                  |      3 |       3   |             1.9 | –                    |                  2.5 |        7.9 |       4.5 |        21.2 |        3.2 |  19.3 |
| 20 calibration buildings                  |      3 |       2.6 |             1.8 | –                    |                  2.2 |        7.9 |       6.1 |        18.6 |        9.1 |  17.3 |


## 5.7 Remaining failures and cost

On BDG2 the Spearman correlation between per-building coverage and CV(RMSE) is -0.67 for CQR and -0.20 for PCS-CQR, i.e. PCS weakens the dependence of reliability on forecast difficulty. Across usage classes with at least 30 building × seed units, the coverage deviation falls in every class; the reduction is smallest for 'Lodging/residential'. Of 713 BDG2 target buildings (seed-averaged), 6 remain under-covered by PCS-CQR. Their median within-window level change |log(mean load weeks 5–8 / weeks 1–4)| is 0.289 versus 0.058 for the others (too few buildings for a test; descriptive only). On UCI, 1 of 270 clients remains under-covered (descriptive only).

The layer is cheap (Supplementary Table S21):

- The daily update of one building — adding 24 scores and recomputing one quantile — takes 0.023 ms on one CPU core.
- Batch-updating 10 000 buildings takes 0.3 s.
- The per-building state is 16 kB as implemented.
- Selecting $\kappa$ by LOBO takes 1.1 s on BDG2, against 29.1 s for the pre-registered similarity-localised design.
- Training the three LightGBM quantile models takes 107 s.


# 6. Discussion

## 6.1 Why pooled calibration fails per building, and what shrinkage changes

**Why pooling fails.** A global forecaster normalised by building scale yields scores that are comparable *on average* across buildings but not identically distributed. Some buildings have regular schedules and small errors. Others have irregular occupancy, plug loads or faults that a few days of data cannot reveal. A pooled radius is a compromise: it over-covers the former and under-covers the latter. In our data it left about one in five new BDG2 buildings clearly under-covered while the mean coverage looked acceptable. The error analysis shows the mechanism: under pooled CQR, per-building coverage falls with forecast difficulty, and PCS largely removes this dependence.

**Why self-only calibration is not enough.** Calibration on the building's own errors alone removes this bias but replaces it with variance. A few dozen hourly scores give a noisy 90 % quantile, which is why Self-CQR is the worst strategy in week 1.

**What shrinkage does.** Shrinkage trades bias against variance explicitly. Its pseudo-count has a direct reading: the number of hourly own scores that the population prior is worth. The selected values of 2–7 days, and the equally good fixed value of one week, mean that a building's own errors dominate after one to two weeks.

**What the other strategies show.** Adjusting the *queried level* rather than the *score distribution* is a weaker lever in this setting:

- ACI with a step size tuned for sharpness changes the level too slowly.
- ACI tuned for coverage alone reaches near-perfect per-building coverage only by inflating the intervals.
- TQA-B bounds its adjustment by design.
- GHCP-style pooling secures marginal validity across buildings by never giving the new building more weight than one reference building.

Per-building reliability during onboarding requires the building's own errors to gain weight as they accumulate, at a rate set by one parameter.

**Relation to prior findings.**

- *Per-site evaluation.* Shahid et al. [20] found in federated risk control that average calibration can hide failing sites. We find the same at building level, and the result persists under site hold-out, where pooled CQR fails for half or more of the buildings at two sites.
- *Quantile shrinkage.* Rafe and Das [21] reported no decisive subgroup gain from quantile shrinkage in survey data. Here the same mechanism gives a decisive gain over pooled calibration. The difference is plausibly the setting: each building contributes a growing stream of its own scores, so its "group" quickly becomes large, whereas survey subgroups are fixed and often small.
- *Donor–local mixture.* The fixed one-week pseudo-count performed as well as the tuned one. This supports the fixed donor–local mixture implemented for new solar stations [22], for which no results have been published.

## 6.2 How the layer should be tuned and designed

**Tuning.** The practically important finding is negative: the interval score — the usual tuning target and the primary endpoint of our analysis plan — is nearly flat in the pseudo-count. It cannot distinguish a layer that leaves 3 % of buildings under-covered from one that leaves 1.5 %, nor, at $\kappa=\infty$, from pooled calibration. The reason is that a proper score aggregated over buildings rewards average sharpness and average calibration, and is insensitive to how miscoverage is distributed across buildings. A rule that looks at the per-building coverage deviation of calibration buildings, with the interval score only as a guard-rail, selects pseudo-counts of 2–7 days. A fixed one-week value is equally good. With a small calibration pool, where LOBO estimates are noisy, the fixed value is preferable.

**Design.** Neither refinement of our pre-registered design helped on the CQR score:

- *Similarity-localised prior.* After scale normalisation and history-derived features, the remaining between-building differences in score distributions seem to be driven by events (occupancy changes, equipment faults, irregular schedules) rather than by load shape or usage type. The usage-based Mondrian baseline fails for the same reason.
- *Onboarding-stage matching.* Unnecessary for CQR scores, because the quantile models already widen when little history is available.

On absolute residuals, stage matching did improve the first week, so the value of this refinement depends on the score. The planned comparison of the absolute-score design with self-only calibration found a lower interval score but no gain in per-building reliability. The recommendation therefore changed during the study (Supplementary Table S1), and results for PCS-CQR should be read as exploratory evidence that the confirmatory comparisons of a future study can build on.

## 6.3 Practical implications

For aggregators, utilities and demand-response platforms that onboard buildings continuously, the results support a simple operating rule:

1. Train one global quantile forecaster.
2. Calibrate it with CQR scores of previously onboarded buildings.
3. Blend each new building's own scores in with a pseudo-count of about one week of hourly scores, or one selected by the reliability-aware rule when the calibration pool is large.

This keeps the share of buildings with clearly unreliable intervals small after the first week. It avoids a failure mode that pooled calibration hides: systematically under-protected capacity reservations and baselines for the most irregular buildings, which are the ones where settlements and alarms are most error-prone. The layer adds a few hundredths of a millisecond per building-day and 16 kB per building, and it works on top of different forecasters. It is therefore compatible with portfolio-scale deployment, including with pretrained forecasting models.

Two cautions apply:

- *The first week remains unreliable.* About one in five BDG2 buildings is under-covered with every strategy of comparable width. A platform that must act in week 1 should widen its intervals or reserves explicitly for that period, accepting a higher reserve cost — as coverage-targeting ACI does automatically.
- *Volatility increases defeat any method* that learns from a few weeks of history, including this one.

## 6.4 Limitations

1. **No finite-sample guarantee.** For $0<\kappa<\infty$ the layer does not inherit the guarantee of split conformal prediction, and its per-building reliability is established empirically. Distribution-free per-series validity is impossible in general [40]. GHCP keeps a marginal guarantee [19] but adapts little per building.
2. **Exploratory status.** The recommended configuration and the reliability-aware rule were defined after interim and review results had been seen (Supplementary Table S1). Their benefit was consistent across both datasets, ten held-out sites, two cross-dataset transfers, a disjoint calibration period and the stress tests, but it has not been confirmed in a separately planned study.
3. **Data selection and setting.** The quality filter uses completeness in the target year, so very poorly metered buildings are excluded from the targets. Onboarding dates were sampled within existing meter histories. Real onboarding can coincide with commissioning problems or behaviour changes, which the level-shift and volatility tests only approximate. BDG2 uses observed temperature as a stand-in for weather forecasts; the UCI and cross-dataset runs use no weather and give the same qualitative results.
4. **Scope.** BDG2 is dominated by campus buildings in North America and Europe, and UCI has no metadata. Residential portfolios, industrial sites and other climates remain untested, as does any horizon beyond 56 days after metering.
5. **Abrupt changes.** Past own scores remain in the mixture, so level shifts and volatility increases during onboarding degrade all strategies. Self-only calibration was more reliable under added meter noise and an increase in volatility. Recency weighting of own scores, or combining shrinkage with online miscoverage control, are plausible but untested remedies.
6. **Baselines and metrics.** Large pretrained probabilistic forecasters [11] were not run, and the GHCP and TQA-B baselines are adaptations of methods designed for other settings. The operational metrics are stylised: booking failures and reserve cost translate the upper bound into a capacity reservation but do not model a specific market or contract.
7. **Per-building coverage is itself an estimate.** With about 1344 hourly observations per building, its sampling noise (MACD ≈ 0.0066 for independent misses, more with autocorrelation) is of the same order as the differences among the best strategies. With ten BDG2 sites, site-level tests have limited power.

# 7. Conclusion

Day-ahead prediction intervals are needed from the first days after a building is metered, and they must be reliable for each building, not just on average. Across 1,157 buildings and clients from two public datasets, pooled conformalised quantile regression left 18.2% (BDG2) and 9.1% (UCI) of new buildings clearly under-covered although their mean coverage was close to nominal.

Shrinking the pooled score distribution toward each building's own accumulating scores reduced these shares to 1.4% and 0.4% at an unchanged interval score. The benefit held on two forecasters, at unseen sites and in cross-country transfer. Quantile-level shrinkage tuned the same way was equivalent. Adaptive conformal inference matched the reliability only with much wider intervals.

What mattered was how the shrinkage was tuned: for per-building reliability, or simply fixed at one week of hourly scores, not for the interval score. Similarity-weighted priors and onboarding-stage matching added nothing on the CQR score. No strategy of comparable width made the first week reliable, and none coped with a sharp increase in day-to-day volatility. Future work should address these two gaps, establish finite-sample guarantees for the shrinkage estimator and test the layer on pretrained forecasters and residential portfolios.


# CRediT authorship contribution statement

**[Author 1]:** Conceptualization, Methodology, Software, Formal analysis, Investigation, Data curation, Writing – original draft, Visualization. **[Author 2]:** Supervision, Writing – review & editing. *(To be completed by the authors.)*

# Declaration of competing interest

The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

# Declaration of generative AI and AI-assisted technologies in the manuscript preparation process

During the preparation of this work the author(s) used an AI assistant (Claude, Anthropic) for drafting and editing the text. Its use in the research itself (software development, execution of the experiments and independent code and manuscript reviews) is described in Section 4 ("Research software"). After using this tool, the author(s) reviewed and edited the content as needed and take(s) full responsibility for the content of the published article.

# Data and code availability

Both datasets are public. BDG2 (CC-BY-4.0) is available at https://github.com/buds-lab/building-data-genome-project-2 [55], and ElectricityLoadDiagrams20112014 (CC-BY-4.0) at https://doi.org/10.24432/C58C86 [57]. The complete code (data download and cleaning, models, the PCS layer, all baselines, experiments, statistics, figures, tables and this manuscript's numbers) is provided as supplementary material and will be released in a public repository [repository URL to be inserted upon acceptance]. `python run_all.py --mode full` reproduces all results.

# Acknowledgements

*(To be completed by the authors; no specific funding was received for this work unless stated here.)*

# References

1. Li H, Wang Z, Hong T, Piette MA. Energy flexibility of residential buildings: A systematic review of characterization and quantification methods and applications. Adv Appl Energy 2021;3:100054. https://doi.org/10.1016/j.adapen.2021.100054.
2. Hong T, Fan S. Probabilistic electric load forecasting: A tutorial review. Int J Forecast 2016;32:914–38. https://doi.org/10.1016/j.ijforecast.2015.11.011.
3. Hong T, Pinson P, Fan S, Zareipour H, Troccoli A, Hyndman RJ. Probabilistic energy forecasting: Global Energy Forecasting Competition 2014 and beyond. Int J Forecast 2016;32:896–913. https://doi.org/10.1016/j.ijforecast.2016.02.001.
4. Guo H, Huang B, Wang J. Probabilistic load forecasting for integrated energy systems using attentive quantile regression temporal convolutional network. Adv Appl Energy 2024;14:100165. https://doi.org/10.1016/j.adapen.2024.100165.
5. Nie Y, Zelikman E, Scott A, Paletta Q, Brandt A. SkyGPT: Probabilistic ultra-short-term solar forecasting using synthetic sky images from physics-constrained VideoGPT. Adv Appl Energy 2024;14:100172. https://doi.org/10.1016/j.adapen.2024.100172.
6. Lindberg O, Lingfors D, Arnqvist J, van der Meer D, Munkhammar J. Day-ahead probabilistic forecasting at a co-located wind and solar power park in Sweden: Trading and forecast verification. Adv Appl Energy 2023;9:100120. https://doi.org/10.1016/j.adapen.2022.100120.
7. Ribeiro M, Grolinger K, ElYamany HF, Higashino WA, Capretz MAM. Transfer learning with seasonal and trend adjustment for cross-building energy forecasting. Energy Build 2018;165:352–63. https://doi.org/10.1016/j.enbuild.2018.01.034.
8. Fan C, Sun Y, Xiao F, Ma J, Lee D, Wang J, et al. Statistical investigations of transfer learning-based methodology for short-term building energy predictions. Appl Energy 2020;262:114499. https://doi.org/10.1016/j.apenergy.2020.114499.
9. Pinto G, Wang Z, Roy A, Hong T, Capozzoli A. Transfer learning for smart buildings: A critical review of algorithms, applications, and future perspectives. Adv Appl Energy 2022;5:100084. https://doi.org/10.1016/j.adapen.2022.100084.
10. Ristovska T, González-Vidal A, Skarmeta AF, Kovatcheva E, Gotsev L. Federated transfer learning for cold-start building energy prediction under data scarcity and privacy constraints. Energy AI 2026;25:100815. https://doi.org/10.1016/j.egyai.2026.100815.
11. Emami P, Sahu A, Graf P. BuildingsBench: A large-scale dataset of 900K buildings and benchmark for short-term load forecasting. In: Advances in Neural Information Processing Systems 36 (NeurIPS 2023), Datasets and Benchmarks Track; 2023.
12. Hao Y, Yang J, Ji Z. Evaluating the reliability of cross-building load forecasting under distribution shift and sensor missingness. Appl Sci 2026;16:7984. https://doi.org/10.3390/app16167984.
13. Vovk V, Gammerman A, Shafer G. Algorithmic learning in a random world. New York: Springer; 2005. https://doi.org/10.1007/b106715.
14. Lei J, G'Sell M, Rinaldo A, Tibshirani RJ, Wasserman L. Distribution-free predictive inference for regression. J Am Stat Assoc 2018;113:1094–111. https://doi.org/10.1080/01621459.2017.1307116.
15. Romano Y, Patterson E, Candès E. Conformalized quantile regression. In: Advances in Neural Information Processing Systems 32 (NeurIPS 2019); 2019.
16. Gibbs I, Candès E. Adaptive conformal inference under distribution shift. In: Advances in Neural Information Processing Systems 34 (NeurIPS 2021); 2021.
17. Lin Z, Trivedi S, Sun J. Conformal prediction with temporal quantile adjustments. In: Advances in Neural Information Processing Systems 35 (NeurIPS 2022); 2022.
18. Dunn R, Wasserman L, Ramdas A. Distribution-free prediction sets for two-layer hierarchical models. J Am Stat Assoc 2023;118:2491–502. https://doi.org/10.1080/01621459.2022.2060112.
19. Mallick S, Tchetgen Tchetgen E, Dobriban E, Lee Y. Generalized hierarchical conformal prediction. arXiv:2608.15500 [Preprint]; 2026. https://doi.org/10.48550/arXiv.2608.15500.
20. Shahid NF. When average calibration fails: Site-conditional federated conformal risk control. arXiv:2606.20115 [Preprint]; 2026. https://doi.org/10.48550/arXiv.2606.20115.
21. Rafe A, Das S. Socio-conformal calibration in complex survey data: Marginal validity is not enough for subgroup reliability. arXiv:2605.05562 [Preprint]; 2026. https://doi.org/10.48550/arXiv.2605.05562.
22. Jeon B. coldstart-conformal-solar: Analysis code for auditing cold-start conformal prediction intervals of solar irradiance forecasts at unseen stations (v1.2) [software]. Zenodo; 2026. https://doi.org/10.5281/zenodo.24002627.
23. Gneiting T, Raftery AE. Strictly proper scoring rules, prediction, and estimation. J Am Stat Assoc 2007;102:359–78. https://doi.org/10.1198/016214506000001437.
24. Wang Y, Gan D, Sun M, Zhang N, Lu Z, Kang C. Probabilistic individual load forecasting using pinball loss guided LSTM. Appl Energy 2019;235:10–20. https://doi.org/10.1016/j.apenergy.2018.10.078.
25. Salinas D, Flunkert V, Gasthaus J, Januschowski T. DeepAR: Probabilistic forecasting with autoregressive recurrent networks. Int J Forecast 2020;36:1181–91. https://doi.org/10.1016/j.ijforecast.2019.07.001.
26. Chen Y, Zhang D. Theory-guided deep-learning for electrical load forecasting (TgDLF) via ensemble long short-term memory. Adv Appl Energy 2021;1:100004. https://doi.org/10.1016/j.adapen.2020.100004.
27. Gao J, Chen Y, Hu W, Zhang D. An adaptive deep-learning load forecasting framework by integrating transformer and domain knowledge. Adv Appl Energy 2023;10:100142. https://doi.org/10.1016/j.adapen.2023.100142.
28. Wang Z, Hong T, Li H, Piette MA. Predicting city-scale daily electricity consumption using data-driven models. Adv Appl Energy 2021;2:100025. https://doi.org/10.1016/j.adapen.2021.100025.
29. Suresh V, Swain A, Revathi BS, Guerrero JM. Mamba based adaptive conformal inference for probabilistic short-term load forecasting. Knowl Based Syst 2025;328:114222. https://doi.org/10.1016/j.knosys.2025.114222.
30. Shi L, Shen Z, Lyu T. Local online conformal prediction for power load forecasting intervals. Electr Power Syst Res 2026;261:113412. https://doi.org/10.1016/j.epsr.2026.113412.
31. Moradi A, Tanneau M, Zandehshahvar R, Van Hentenryck P. Enhanced renewable energy forecasting using context-aware conformal prediction. arXiv:2510.15780 [Preprint]; 2025. https://doi.org/10.48550/arXiv.2510.15780.
32. Almeida V, Gama J. Prediction intervals for electric load forecast: Evaluation for different profiles. In: 2015 18th International Conference on Intelligent System Application to Power Systems (ISAP); 2015. https://doi.org/10.1109/isap.2015.7325539.
33. Jin Y, Acquah MA, Seo M, Han S. Short-term electric load prediction using transfer learning with interval estimate adjustment. Energy Build 2022;258:111846. https://doi.org/10.1016/j.enbuild.2022.111846.
34. Papadopoulos H, Proedrou K, Vovk V, Gammerman A. Inductive confidence machines for regression. In: Machine Learning: ECML 2002. Lecture Notes in Computer Science, vol. 2430. Berlin: Springer; 2002, p. 345–56. https://doi.org/10.1007/3-540-36755-1_29.
35. Zaffran M, Féron O, Goude Y, Josse J, Dieuleveut A. Adaptive conformal predictions for time series. In: Proceedings of the 39th International Conference on Machine Learning, PMLR 162; 2022, p. 25834–66.
36. Wang X, Hyndman RJ. Online conformal inference for multi-step time series forecasting. arXiv:2410.13115v2 [Preprint]; 2024 (revised 2026). https://doi.org/10.48550/arXiv.2410.13115.
37. Xu C, Xie Y. Conformal prediction interval for dynamic time-series. In: Proceedings of the 38th International Conference on Machine Learning, PMLR 139; 2021, p. 11559–69.
38. Barber RF, Candès EJ, Ramdas A, Tibshirani RJ. Conformal prediction beyond exchangeability. Ann Stat 2023;51:816–45. https://doi.org/10.1214/23-AOS2276.
39. Tibshirani RJ, Barber RF, Candès E, Ramdas A. Conformal prediction under covariate shift. In: Advances in Neural Information Processing Systems 32 (NeurIPS 2019); 2019.
40. Lin Z, Trivedi S, Sun J. Conformal prediction intervals with temporal dependence. Trans Mach Learn Res 2022. https://doi.org/10.48550/arXiv.2205.12940.
41. Batra D, Mercuri S, Khraishi R. Conformal predictions for longitudinal data. arXiv:2310.02863 [Preprint]; 2023. https://doi.org/10.48550/arXiv.2310.02863.
42. Gibbs I, Cherian JJ, Candès EJ. Conformal prediction with conditional guarantees. J R Stat Soc Series B Stat Methodol 2025;87:1100–26. https://doi.org/10.1093/jrsssb/qkaf008.
43. Ding T, Angelopoulos AN, Bates S, Jordan MI, Tibshirani RJ. Class-conditional conformal prediction with many classes. In: Advances in Neural Information Processing Systems 36 (NeurIPS 2023); 2023.
44. Fisch A, Schuster T, Jaakkola T, Barzilay R. Few-shot conformal prediction with auxiliary tasks. In: Proceedings of the 38th International Conference on Machine Learning, PMLR 139; 2021, p. 3329–39.
45. Vejling MV, Biscio CAN, Mazoyer A, Popovski P, Pandey SR. Multi-agent conformal prediction with personalized statistical validity. arXiv:2606.00717 [Preprint]; 2026. https://doi.org/10.48550/arXiv.2606.00717.
46. Lee Y, Barber RF, Willett R. Distribution-free inference with hierarchical data. arXiv:2306.06342 [Preprint]; 2023. https://doi.org/10.48550/arXiv.2306.06342.
47. Bersson E, Hoff PD. Optimal conformal prediction for small areas. J Surv Stat Methodol 2024;12:1464–88. https://doi.org/10.1093/jssam/smae010.
48. Bühlmann H. Experience rating and credibility. ASTIN Bull 1967;4:199–207. https://doi.org/10.1017/S0515036100008989.
49. Hong L. Conformal prediction credibility intervals. N Am Actuar J 2023;27:675–88. https://doi.org/10.1080/10920277.2022.2123364.
50. Zhang Z, Lu Z, Yang H. The benefit of being Bayesian in online conformal prediction. arXiv:2410.02561 [Preprint]; 2024. https://doi.org/10.48550/arXiv.2410.02561.
51. Gibson G. Bayesian conformal prediction via the Bayesian bootstrap. arXiv:2508.01418 [Preprint]; 2025. https://doi.org/10.48550/arXiv.2508.01418.
52. Ke G, Meng Q, Finley T, Wang T, Chen W, Ma W, et al. LightGBM: A highly efficient gradient boosting decision tree. In: Advances in Neural Information Processing Systems 30 (NIPS 2017); 2017.
53. Koenker R, Bassett G. Regression quantiles. Econometrica 1978;46:33–50. https://doi.org/10.2307/1913643.
54. Ferguson TS. A Bayesian analysis of some nonparametric problems. Ann Stat 1973;1:209–30. https://doi.org/10.1214/aos/1176342360.
55. Miller C, Kathirgamanathan A, Picchetti B, Arjunan P, Park JY, Nagy Z, et al. The Building Data Genome Project 2, energy meter data from the ASHRAE Great Energy Predictor III competition. Sci Data 2020;7:368. https://doi.org/10.1038/s41597-020-00712-x.
56. Miller C, Arjunan P, Kathirgamanathan A, Fu C, Roth J, Park JY, et al. The ASHRAE Great Energy Predictor III competition: Overview and results. Sci Technol Built Environ 2020;26:1427–47. https://doi.org/10.1080/23744731.2020.1795514.
57. Trindade A. ElectricityLoadDiagrams20112014 [dataset]. UCI Machine Learning Repository; 2015. https://doi.org/10.24432/C58C86.
58. Winkler RL. A decision-theoretic approach to interval estimation. J Am Stat Assoc 1972;67:187–91. https://doi.org/10.1080/01621459.1972.10481224.
59. Holm S. A simple sequentially rejective multiple test procedure. Scand J Stat 1979;6:65–70.
60. Paszke A, Gross S, Massa F, Lerer A, Bradbury J, Chanan G, et al. PyTorch: An imperative style, high-performance deep learning library. In: Advances in Neural Information Processing Systems 32 (NeurIPS 2019); 2019.
