# Review packet — cycle 2
Repository root: /home/user/p_c1_1 (read-only for reviewers).

## 1. Manuscript (as built; all numbers filled from results files)

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


## 2. Supplementary tables (machine-generated)

### T_ablation_BDG2.md

**Design elements and ablations, BDG2**

| Method               | Coverage      | MACD          | Under-covered share   | P10 coverage   | Under-covered, week 1   | Rel. width (median)   | Rel. IS (median)   | Reserve cost    |
|:---------------------|:--------------|:--------------|:----------------------|:---------------|:------------------------|:----------------------|:-------------------|:----------------|
| PCS-CQR              | 0.895 ± 0.001 | 0.015 ± 0.001 | 0.014 ± 0.008         | 0.871 ± 0.001  | 0.194 ± 0.021           | 0.391 ± 0.014         | 0.562 ± 0.025      | 0.0209 ± 0.0012 |
| PCS-CQR κ=168        | 0.895 ± 0.002 | 0.015 ± 0.001 | 0.015 ± 0.009         | 0.871 ± 0.001  | 0.197 ± 0.022           | 0.390 ± 0.014         | 0.562 ± 0.025      | 0.0208 ± 0.0012 |
| PCS-CQR (IS-tuned)   | 0.894 ± 0.002 | 0.017 ± 0.001 | 0.029 ± 0.014         | 0.868 ± 0.002  | 0.214 ± 0.020           | 0.386 ± 0.012         | 0.561 ± 0.025      | 0.0206 ± 0.0010 |
| PCS-CQR +stage       | 0.895 ± 0.002 | 0.015 ± 0.001 | 0.014 ± 0.008         | 0.870 ± 0.002  | 0.193 ± 0.030           | 0.391 ± 0.013         | 0.563 ± 0.024      | 0.0209 ± 0.0012 |
| PCS-CQR +kNN         | 0.894 ± 0.001 | 0.015 ± 0.001 | 0.018 ± 0.010         | 0.870 ± 0.001  | 0.203 ± 0.016           | 0.390 ± 0.014         | 0.562 ± 0.025      | 0.0208 ± 0.0012 |
| PCS-CQR +kNN+stage   | 0.893 ± 0.001 | 0.016 ± 0.001 | 0.018 ± 0.010         | 0.870 ± 0.001  | 0.217 ± 0.026           | 0.390 ± 0.014         | 0.563 ± 0.024      | 0.0208 ± 0.0012 |
| PCS-CQR site-grouped | 0.895 ± 0.001 | 0.015 ± 0.001 | 0.015 ± 0.006         | 0.871 ± 0.002  | 0.191 ± 0.028           | 0.391 ± 0.014         | 0.562 ± 0.025      | 0.0209 ± 0.0012 |
| QShrink-CQR λ=168    | 0.897 ± 0.002 | 0.015 ± 0.001 | 0.012 ± 0.007         | 0.873 ± 0.002  | 0.181 ± 0.022           | 0.392 ± 0.014         | 0.562 ± 0.024      | 0.0211 ± 0.0014 |
| CQR                  | 0.891 ± 0.004 | 0.039 ± 0.002 | 0.182 ± 0.017         | 0.829 ± 0.003  | 0.242 ± 0.028           | 0.382 ± 0.013         | 0.560 ± 0.023      | 0.0208 ± 0.0010 |
| Self-CQR             | 0.889 ± 0.002 | 0.021 ± 0.001 | 0.076 ± 0.022         | 0.856 ± 0.005  | 0.338 ± 0.009           | 0.396 ± 0.015         | 0.571 ± 0.022      | 0.0221 ± 0.0023 |
| HSC                  | 0.899 ± 0.003 | 0.029 ± 0.002 | 0.096 ± 0.017         | 0.852 ± 0.003  | 0.313 ± 0.058           | 0.411 ± 0.016         | 0.635 ± 0.028      | 0.0231 ± 0.0014 |
| HSC -stage           | 0.898 ± 0.003 | 0.029 ± 0.002 | 0.101 ± 0.020         | 0.851 ± 0.005  | 0.383 ± 0.054           | 0.410 ± 0.015         | 0.640 ± 0.026      | 0.0232 ± 0.0014 |
| HSC -kNN             | 0.911 ± 0.002 | 0.029 ± 0.002 | 0.050 ± 0.009         | 0.867 ± 0.003  | 0.143 ± 0.026           | 0.441 ± 0.020         | 0.638 ± 0.027      | 0.0236 ± 0.0018 |
| HSC -shrink          | 0.839 ± 0.008 | 0.094 ± 0.005 | 0.467 ± 0.030         | 0.690 ± 0.015  | 0.465 ± 0.068           | 0.360 ± 0.010         | 0.660 ± 0.031      | 0.0255 ± 0.0010 |
| PCS                  | 0.905 ± 0.001 | 0.026 ± 0.002 | 0.060 ± 0.010         | 0.860 ± 0.002  | 0.187 ± 0.028           | 0.437 ± 0.022         | 0.646 ± 0.025      | 0.0243 ± 0.0023 |
| Self-CP              | 0.904 ± 0.003 | 0.026 ± 0.001 | 0.061 ± 0.014         | 0.861 ± 0.003  | 0.162 ± 0.031           | 0.440 ± 0.023         | 0.646 ± 0.028      | 0.0245 ± 0.0026 |
| SCP-stage            | 0.880 ± 0.009 | 0.094 ± 0.005 | 0.293 ± 0.029         | 0.701 ± 0.018  | 0.270 ± 0.032           | 0.458 ± 0.025         | 0.631 ± 0.026      | 0.0269 ± 0.0010 |

### T_ablation_UCI.md

**Design elements and ablations, UCI**

| Method             | Coverage      | MACD          | Under-covered share   | P10 coverage   | Under-covered, week 1   | Rel. width (median)   | Rel. IS (median)   | Reserve cost    |
|:-------------------|:--------------|:--------------|:----------------------|:---------------|:------------------------|:----------------------|:-------------------|:----------------|
| PCS-CQR            | 0.900 ± 0.002 | 0.013 ± 0.002 | 0.004 ± 0.009         | 0.879 ± 0.004  | 0.103 ± 0.026           | 0.266 ± 0.013         | 0.367 ± 0.014      | 0.0162 ± 0.0021 |
| PCS-CQR κ=168      | 0.901 ± 0.003 | 0.013 ± 0.002 | 0.008 ± 0.014         | 0.881 ± 0.006  | 0.120 ± 0.022           | 0.266 ± 0.013         | 0.365 ± 0.015      | 0.0161 ± 0.0021 |
| PCS-CQR (IS-tuned) | 0.901 ± 0.004 | 0.014 ± 0.003 | 0.011 ± 0.015         | 0.879 ± 0.009  | 0.135 ± 0.033           | 0.267 ± 0.013         | 0.365 ± 0.015      | 0.0161 ± 0.0021 |
| PCS-CQR +stage     | 0.900 ± 0.002 | 0.013 ± 0.002 | 0.004 ± 0.009         | 0.880 ± 0.004  | 0.086 ± 0.024           | 0.267 ± 0.013         | 0.366 ± 0.015      | 0.0162 ± 0.0021 |
| PCS-CQR +kNN       | 0.899 ± 0.002 | 0.013 ± 0.002 | 0.006 ± 0.009         | 0.879 ± 0.003  | 0.112 ± 0.028           | 0.265 ± 0.013         | 0.366 ± 0.014      | 0.0162 ± 0.0021 |
| PCS-CQR +kNN+stage | 0.899 ± 0.002 | 0.013 ± 0.002 | 0.006 ± 0.009         | 0.879 ± 0.003  | 0.116 ± 0.044           | 0.266 ± 0.011         | 0.367 ± 0.015      | 0.0161 ± 0.0020 |
| QShrink-CQR λ=168  | 0.902 ± 0.003 | 0.013 ± 0.001 | 0.004 ± 0.009         | 0.883 ± 0.006  | 0.095 ± 0.027           | 0.265 ± 0.011         | 0.365 ± 0.015      | 0.0161 ± 0.0021 |
| CQR                | 0.899 ± 0.010 | 0.033 ± 0.005 | 0.091 ± 0.049         | 0.855 ± 0.015  | 0.156 ± 0.027           | 0.273 ± 0.017         | 0.364 ± 0.014      | 0.0162 ± 0.0020 |
| Self-CQR           | 0.895 ± 0.002 | 0.016 ± 0.002 | 0.019 ± 0.019         | 0.870 ± 0.004  | 0.227 ± 0.038           | 0.264 ± 0.011         | 0.372 ± 0.014      | 0.0163 ± 0.0022 |
| HSC                | 0.905 ± 0.004 | 0.021 ± 0.001 | 0.038 ± 0.022         | 0.871 ± 0.005  | 0.179 ± 0.045           | 0.288 ± 0.014         | 0.416 ± 0.016      | 0.0177 ± 0.0019 |
| HSC -stage         | 0.904 ± 0.005 | 0.021 ± 0.001 | 0.038 ± 0.027         | 0.871 ± 0.006  | 0.225 ± 0.067           | 0.286 ± 0.014         | 0.417 ± 0.016      | 0.0178 ± 0.0020 |
| HSC -kNN           | 0.914 ± 0.005 | 0.025 ± 0.003 | 0.023 ± 0.017         | 0.879 ± 0.007  | 0.097 ± 0.040           | 0.306 ± 0.015         | 0.420 ± 0.013      | 0.0179 ± 0.0020 |
| HSC -shrink        | 0.857 ± 0.007 | 0.078 ± 0.004 | 0.318 ± 0.042         | 0.719 ± 0.013  | 0.364 ± 0.059           | 0.254 ± 0.011         | 0.438 ± 0.034      | 0.0210 ± 0.0028 |
| PCS                | 0.908 ± 0.003 | 0.021 ± 0.001 | 0.023 ± 0.017         | 0.878 ± 0.003  | 0.099 ± 0.019           | 0.295 ± 0.013         | 0.419 ± 0.011      | 0.0179 ± 0.0021 |
| Self-CP            | 0.908 ± 0.003 | 0.021 ± 0.001 | 0.023 ± 0.017         | 0.877 ± 0.002  | 0.076 ± 0.016           | 0.297 ± 0.014         | 0.420 ± 0.012      | 0.0180 ± 0.0021 |
| SCP-stage          | 0.903 ± 0.016 | 0.089 ± 0.006 | 0.204 ± 0.044         | 0.771 ± 0.028  | 0.181 ± 0.019           | 0.377 ± 0.033         | 0.441 ± 0.018      | 0.0217 ± 0.0028 |

### T_alpha0.05_BDG2.md

**BDG2, nominal 95%**

| Method                  | Coverage      | MACD          | Under-covered share   | P10 coverage   | Under-covered, week 1   | Rel. width (median)   | Rel. IS (median)   | Reserve cost    |
|:------------------------|:--------------|:--------------|:----------------------|:---------------|:------------------------|:----------------------|:-------------------|:----------------|
| PCS-CQR                 | 0.948 ± 0.001 | 0.012 ± 0.002 | 0.003 ± 0.002         | 0.930 ± 0.002  | 0.147 ± 0.023           | 0.495 ± 0.025         | 0.691 ± 0.024      | 0.0143 ± 0.0013 |
| PCS-CQR κ=168           | 0.948 ± 0.001 | 0.011 ± 0.001 | 0.004 ± 0.003         | 0.930 ± 0.001  | 0.155 ± 0.022           | 0.493 ± 0.025         | 0.689 ± 0.026      | 0.0143 ± 0.0016 |
| PCS-CQR (IS-tuned)      | 0.949 ± 0.001 | 0.013 ± 0.001 | 0.004 ± 0.003         | 0.927 ± 0.001  | 0.184 ± 0.024           | 0.488 ± 0.022         | 0.686 ± 0.025      | 0.0138 ± 0.0011 |
| PCS-CQR site-grouped    | 0.948 ± 0.001 | 0.012 ± 0.002 | 0.003 ± 0.002         | 0.930 ± 0.002  | 0.147 ± 0.023           | 0.495 ± 0.025         | 0.691 ± 0.024      | 0.0143 ± 0.0013 |
| HSC-CQR                 | 0.946 ± 0.002 | 0.013 ± 0.001 | 0.006 ± 0.004         | 0.925 ± 0.002  | 0.198 ± 0.037           | 0.481 ± 0.022         | 0.685 ± 0.025      | 0.0138 ± 0.0011 |
| CQR                     | 0.942 ± 0.004 | 0.032 ± 0.001 | 0.147 ± 0.019         | 0.887 ± 0.007  | 0.204 ± 0.035           | 0.471 ± 0.020         | 0.676 ± 0.030      | 0.0143 ± 0.0009 |
| Self-CQR                | 0.942 ± 0.001 | 0.015 ± 0.001 | 0.018 ± 0.011         | 0.918 ± 0.003  | 0.317 ± 0.032           | 0.499 ± 0.028         | 0.704 ± 0.027      | 0.0152 ± 0.0021 |
| ACI-CQR                 | 0.947 ± 0.002 | 0.022 ± 0.001 | 0.051 ± 0.016         | 0.910 ± 0.003  | 0.199 ± 0.033           | 0.477 ± 0.020         | 0.678 ± 0.031      | 0.0140 ± 0.0010 |
| ACI-CQR (MACD)          | 0.948 ± 0.002 | 0.021 ± 0.003 | 0.037 ± 0.022         | 0.913 ± 0.005  | 0.199 ± 0.033           | 0.478 ± 0.019         | 0.678 ± 0.031      | 0.0141 ± 0.0009 |
| ACI-CQR (coverage only) | 0.950 ± 0.000 | 0.003 ± 0.000 | 0.000 ± 0.000         | 0.945 ± 0.001  | 0.077 ± 0.013           | 2.128 ± 0.410         | 2.311 ± 0.417      | 0.0393 ± 0.0067 |
| TQA-B-CQR               | 0.943 ± 0.003 | 0.031 ± 0.001 | 0.143 ± 0.021         | 0.889 ± 0.007  | 0.203 ± 0.034           | 0.470 ± 0.018         | 0.677 ± 0.030      | 0.0142 ± 0.0009 |
| GHCP-CQR                | 0.945 ± 0.004 | 0.031 ± 0.001 | 0.132 ± 0.020         | 0.890 ± 0.008  | 0.203 ± 0.035           | 0.479 ± 0.021         | 0.677 ± 0.028      | 0.0143 ± 0.0009 |
| QShrink-CQR             | 0.951 ± 0.001 | 0.017 ± 0.003 | 0.010 ± 0.013         | 0.924 ± 0.006  | 0.175 ± 0.030           | 0.490 ± 0.022         | 0.685 ± 0.025      | 0.0140 ± 0.0011 |
| QShrink-CQR (MACD)      | 0.949 ± 0.001 | 0.012 ± 0.002 | 0.003 ± 0.002         | 0.930 ± 0.002  | 0.136 ± 0.036           | 0.496 ± 0.027         | 0.693 ± 0.025      | 0.0145 ± 0.0015 |
| QShrink-CQR λ=168       | 0.950 ± 0.001 | 0.012 ± 0.000 | 0.002 ± 0.002         | 0.931 ± 0.001  | 0.149 ± 0.028           | 0.495 ± 0.024         | 0.689 ± 0.024      | 0.0143 ± 0.0014 |
| CQR (MLP)               | 0.944 ± 0.003 | 0.030 ± 0.001 | 0.119 ± 0.012         | 0.893 ± 0.007  | 0.187 ± 0.031           | 0.473 ± 0.017         | 0.682 ± 0.034      | 0.0141 ± 0.0010 |
| PCS-CQR (MLP)           | 0.948 ± 0.001 | 0.011 ± 0.001 | 0.002 ± 0.002         | 0.930 ± 0.002  | 0.123 ± 0.022           | 0.495 ± 0.023         | 0.691 ± 0.030      | 0.0142 ± 0.0014 |
| PCS                     | 0.951 ± 0.003 | 0.017 ± 0.001 | 0.021 ± 0.012         | 0.922 ± 0.003  | 0.218 ± 0.059           | 0.586 ± 0.027         | 0.817 ± 0.031      | 0.0168 ± 0.0023 |
| PCS (IS-tuned)          | 0.956 ± 0.001 | 0.019 ± 0.001 | 0.016 ± 0.007         | 0.926 ± 0.001  | 0.123 ± 0.028           | 0.600 ± 0.024         | 0.802 ± 0.022      | 0.0166 ± 0.0021 |
| HSC                     | 0.949 ± 0.003 | 0.020 ± 0.002 | 0.040 ± 0.018         | 0.914 ± 0.005  | 0.258 ± 0.073           | 0.560 ± 0.018         | 0.797 ± 0.023      | 0.0156 ± 0.0014 |
| ACI                     | 0.960 ± 0.004 | 0.029 ± 0.004 | 0.052 ± 0.070         | 0.912 ± 0.015  | 0.189 ± 0.044           | 0.631 ± 0.034         | 0.794 ± 0.025      | 0.0170 ± 0.0011 |
| Self-CP                 | 0.950 ± 0.002 | 0.017 ± 0.001 | 0.028 ± 0.015         | 0.921 ± 0.003  | 0.209 ± 0.025           | 0.588 ± 0.027         | 0.820 ± 0.031      | 0.0169 ± 0.0024 |
| SCP-stage               | 0.937 ± 0.006 | 0.059 ± 0.003 | 0.205 ± 0.025         | 0.821 ± 0.017  | 0.197 ± 0.044           | 0.690 ± 0.047         | 0.808 ± 0.028      | 0.0192 ± 0.0009 |
| SCP                     | 0.937 ± 0.006 | 0.059 ± 0.003 | 0.206 ± 0.027         | 0.823 ± 0.018  | 0.258 ± 0.042           | 0.688 ± 0.046         | 0.809 ± 0.028      | 0.0192 ± 0.0009 |
| Mondrian-usage          | 0.937 ± 0.008 | 0.058 ± 0.004 | 0.216 ± 0.049         | 0.823 ± 0.017  | 0.194 ± 0.046           | 0.655 ± 0.066         | 0.872 ± 0.059      | 0.0192 ± 0.0008 |
| Naive+SCP               | 0.939 ± 0.008 | 0.058 ± 0.005 | 0.209 ± 0.031         | 0.822 ± 0.023  | 0.226 ± 0.036           | 1.053 ± 0.080         | 1.216 ± 0.055      | 0.0268 ± 0.0018 |
| Raw-SCP                 | 0.953 ± 0.020 | 0.071 ± 0.014 | 0.121 ± 0.051         | 0.860 ± 0.098  | 0.140 ± 0.054           | 1.425 ± 0.238         | 1.812 ± 0.181      | 0.0588 ± 0.0101 |

### T_alpha0.05_UCI.md

**UCI, nominal 95%**

| Method                  | Coverage      | MACD          | Under-covered share   | P10 coverage   | Under-covered, week 1   | Rel. width (median)   | Rel. IS (median)   | Reserve cost    |
|:------------------------|:--------------|:--------------|:----------------------|:---------------|:------------------------|:----------------------|:-------------------|:----------------|
| PCS-CQR                 | 0.951 ± 0.002 | 0.009 ± 0.001 | 0.000 ± 0.000         | 0.936 ± 0.004  | 0.088 ± 0.019           | 0.329 ± 0.012         | 0.443 ± 0.019      | 0.0105 ± 0.0016 |
| PCS-CQR κ=168           | 0.952 ± 0.002 | 0.010 ± 0.001 | 0.000 ± 0.000         | 0.938 ± 0.004  | 0.088 ± 0.021           | 0.332 ± 0.015         | 0.441 ± 0.018      | 0.0104 ± 0.0016 |
| PCS-CQR (IS-tuned)      | 0.951 ± 0.003 | 0.010 ± 0.001 | 0.006 ± 0.009         | 0.935 ± 0.004  | 0.116 ± 0.042           | 0.332 ± 0.013         | 0.442 ± 0.020      | 0.0105 ± 0.0016 |
| HSC-CQR                 | 0.949 ± 0.002 | 0.010 ± 0.001 | 0.006 ± 0.009         | 0.932 ± 0.004  | 0.124 ± 0.020           | 0.327 ± 0.011         | 0.441 ± 0.019      | 0.0105 ± 0.0016 |
| CQR                     | 0.950 ± 0.007 | 0.027 ± 0.005 | 0.069 ± 0.022         | 0.913 ± 0.009  | 0.122 ± 0.032           | 0.348 ± 0.025         | 0.440 ± 0.019      | 0.0110 ± 0.0018 |
| Self-CQR                | 0.948 ± 0.002 | 0.011 ± 0.001 | 0.000 ± 0.000         | 0.929 ± 0.002  | 0.211 ± 0.058           | 0.328 ± 0.013         | 0.446 ± 0.015      | 0.0106 ± 0.0016 |
| ACI-CQR                 | 0.953 ± 0.004 | 0.018 ± 0.006 | 0.027 ± 0.021         | 0.924 ± 0.006  | 0.116 ± 0.028           | 0.345 ± 0.021         | 0.440 ± 0.017      | 0.0107 ± 0.0015 |
| ACI-CQR (MACD)          | 0.953 ± 0.004 | 0.017 ± 0.005 | 0.021 ± 0.015         | 0.924 ± 0.006  | 0.114 ± 0.025           | 0.343 ± 0.020         | 0.440 ± 0.017      | 0.0107 ± 0.0015 |
| ACI-CQR (coverage only) | 0.950 ± 0.001 | 0.003 ± 0.000 | 0.000 ± 0.000         | 0.946 ± 0.000  | 0.048 ± 0.012           | 0.831 ± 0.334         | 0.952 ± 0.348      | 0.0258 ± 0.0132 |
| TQA-B-CQR               | 0.949 ± 0.006 | 0.027 ± 0.005 | 0.078 ± 0.030         | 0.912 ± 0.008  | 0.128 ± 0.026           | 0.345 ± 0.023         | 0.439 ± 0.019      | 0.0109 ± 0.0017 |
| GHCP-CQR                | 0.959 ± 0.006 | 0.028 ± 0.004 | 0.051 ± 0.009         | 0.923 ± 0.007  | 0.099 ± 0.026           | 0.371 ± 0.028         | 0.450 ± 0.022      | 0.0110 ± 0.0018 |
| QShrink-CQR             | 0.954 ± 0.003 | 0.012 ± 0.002 | 0.002 ± 0.005         | 0.935 ± 0.006  | 0.103 ± 0.020           | 0.339 ± 0.018         | 0.441 ± 0.018      | 0.0105 ± 0.0016 |
| QShrink-CQR (MACD)      | 0.951 ± 0.002 | 0.010 ± 0.001 | 0.000 ± 0.000         | 0.936 ± 0.004  | 0.078 ± 0.024           | 0.330 ± 0.011         | 0.442 ± 0.017      | 0.0104 ± 0.0015 |
| QShrink-CQR λ=168       | 0.953 ± 0.003 | 0.010 ± 0.001 | 0.000 ± 0.000         | 0.940 ± 0.003  | 0.084 ± 0.011           | 0.335 ± 0.015         | 0.442 ± 0.017      | 0.0104 ± 0.0015 |
| CQR (MLP)               | 0.950 ± 0.006 | 0.028 ± 0.006 | 0.080 ± 0.041         | 0.913 ± 0.014  | 0.116 ± 0.049           | 0.351 ± 0.025         | 0.456 ± 0.025      | 0.0105 ± 0.0012 |
| PCS-CQR (MLP)           | 0.953 ± 0.003 | 0.010 ± 0.001 | 0.002 ± 0.005         | 0.938 ± 0.005  | 0.088 ± 0.035           | 0.340 ± 0.017         | 0.455 ± 0.020      | 0.0101 ± 0.0012 |
| PCS                     | 0.954 ± 0.002 | 0.014 ± 0.001 | 0.002 ± 0.005         | 0.933 ± 0.004  | 0.128 ± 0.022           | 0.390 ± 0.017         | 0.517 ± 0.011      | 0.0116 ± 0.0016 |
| PCS (IS-tuned)          | 0.958 ± 0.003 | 0.017 ± 0.003 | 0.008 ± 0.014         | 0.935 ± 0.004  | 0.124 ± 0.064           | 0.404 ± 0.020         | 0.517 ± 0.013      | 0.0116 ± 0.0016 |
| HSC                     | 0.953 ± 0.004 | 0.015 ± 0.001 | 0.015 ± 0.022         | 0.929 ± 0.009  | 0.143 ± 0.038           | 0.382 ± 0.021         | 0.513 ± 0.013      | 0.0115 ± 0.0015 |
| ACI                     | 0.968 ± 0.006 | 0.028 ± 0.005 | 0.008 ± 0.012         | 0.929 ± 0.006  | 0.122 ± 0.028           | 0.480 ± 0.065         | 0.545 ± 0.040      | 0.0131 ± 0.0016 |
| Self-CP                 | 0.954 ± 0.002 | 0.014 ± 0.001 | 0.004 ± 0.006         | 0.933 ± 0.004  | 0.112 ± 0.024           | 0.394 ± 0.019         | 0.521 ± 0.010      | 0.0116 ± 0.0016 |
| SCP-stage               | 0.950 ± 0.015 | 0.060 ± 0.009 | 0.139 ± 0.040         | 0.878 ± 0.032  | 0.139 ± 0.027           | 0.575 ± 0.082         | 0.608 ± 0.066      | 0.0162 ± 0.0029 |
| SCP                     | 0.950 ± 0.015 | 0.059 ± 0.009 | 0.137 ± 0.037         | 0.877 ± 0.033  | 0.189 ± 0.055           | 0.572 ± 0.082         | 0.605 ± 0.065      | 0.0162 ± 0.0029 |
| Naive+SCP               | 0.951 ± 0.008 | 0.053 ± 0.003 | 0.160 ± 0.023         | 0.861 ± 0.027  | 0.156 ± 0.017           | 0.708 ± 0.076         | 0.760 ± 0.057      | 0.0206 ± 0.0029 |
| Raw-SCP                 | 0.951 ± 0.036 | 0.079 ± 0.024 | 0.107 ± 0.087         | 0.844 ± 0.205  | 0.133 ± 0.088           | 1.999 ± 0.841         | 2.152 ± 0.689      | 0.0881 ± 0.0949 |

### T_alpha0.2_BDG2.md

**BDG2, nominal 80%**

| Method                  | Coverage      | MACD          | Under-covered share   | P10 coverage   | Under-covered, week 1   | Rel. width (median)   | Rel. IS (median)   | Reserve cost    |
|:------------------------|:--------------|:--------------|:----------------------|:---------------|:------------------------|:----------------------|:-------------------|:----------------|
| PCS-CQR                 | 0.793 ± 0.002 | 0.021 ± 0.001 | 0.063 ± 0.007         | 0.759 ± 0.004  | 0.183 ± 0.014           | 0.318 ± 0.011         | 0.460 ± 0.018      | 0.0318 ± 0.0012 |
| PCS-CQR κ=168           | 0.794 ± 0.002 | 0.021 ± 0.001 | 0.062 ± 0.009         | 0.760 ± 0.004  | 0.182 ± 0.017           | 0.319 ± 0.011         | 0.460 ± 0.018      | 0.0318 ± 0.0012 |
| PCS-CQR (IS-tuned)      | 0.796 ± 0.003 | 0.023 ± 0.001 | 0.074 ± 0.010         | 0.757 ± 0.005  | 0.191 ± 0.018           | 0.320 ± 0.010         | 0.460 ± 0.018      | 0.0318 ± 0.0012 |
| PCS-CQR site-grouped    | 0.793 ± 0.002 | 0.021 ± 0.001 | 0.065 ± 0.006         | 0.759 ± 0.004  | 0.183 ± 0.013           | 0.318 ± 0.011         | 0.460 ± 0.018      | 0.0318 ± 0.0012 |
| HSC-CQR                 | 0.794 ± 0.003 | 0.023 ± 0.001 | 0.061 ± 0.017         | 0.758 ± 0.005  | 0.240 ± 0.029           | 0.316 ± 0.009         | 0.460 ± 0.019      | 0.0317 ± 0.0012 |
| CQR                     | 0.794 ± 0.006 | 0.048 ± 0.003 | 0.166 ± 0.024         | 0.720 ± 0.010  | 0.262 ± 0.032           | 0.325 ± 0.010         | 0.460 ± 0.017      | 0.0318 ± 0.0012 |
| Self-CQR                | 0.782 ± 0.002 | 0.030 ± 0.002 | 0.155 ± 0.029         | 0.739 ± 0.005  | 0.397 ± 0.040           | 0.317 ± 0.013         | 0.466 ± 0.019      | 0.0331 ± 0.0028 |
| ACI-CQR                 | 0.802 ± 0.001 | 0.019 ± 0.003 | 0.014 ± 0.012         | 0.772 ± 0.004  | 0.247 ± 0.034           | 0.320 ± 0.010         | 0.460 ± 0.018      | 0.0319 ± 0.0014 |
| ACI-CQR (MACD)          | 0.802 ± 0.001 | 0.018 ± 0.001 | 0.009 ± 0.004         | 0.775 ± 0.002  | 0.245 ± 0.034           | 0.321 ± 0.010         | 0.460 ± 0.018      | 0.0319 ± 0.0014 |
| ACI-CQR (coverage only) | 0.801 ± 0.000 | 0.006 ± 0.000 | 0.000 ± 0.000         | 0.792 ± 0.001  | 0.157 ± 0.011           | 0.379 ± 0.023         | 0.517 ± 0.039      | 0.0415 ± 0.0036 |
| TQA-B-CQR               | 0.818 ± 0.003 | 0.040 ± 0.003 | 0.053 ± 0.013         | 0.762 ± 0.002  | 0.184 ± 0.021           | 0.325 ± 0.008         | 0.462 ± 0.019      | 0.0323 ± 0.0012 |
| GHCP-CQR                | 0.797 ± 0.005 | 0.047 ± 0.003 | 0.159 ± 0.020         | 0.724 ± 0.009  | 0.192 ± 0.022           | 0.327 ± 0.010         | 0.460 ± 0.017      | 0.0318 ± 0.0012 |
| QShrink-CQR             | 0.793 ± 0.004 | 0.029 ± 0.004 | 0.109 ± 0.033         | 0.746 ± 0.012  | 0.247 ± 0.037           | 0.320 ± 0.011         | 0.460 ± 0.019      | 0.0318 ± 0.0013 |
| QShrink-CQR (MACD)      | 0.789 ± 0.003 | 0.023 ± 0.002 | 0.088 ± 0.017         | 0.754 ± 0.005  | 0.243 ± 0.027           | 0.317 ± 0.012         | 0.461 ± 0.019      | 0.0321 ± 0.0015 |
| QShrink-CQR λ=168       | 0.790 ± 0.004 | 0.023 ± 0.002 | 0.090 ± 0.015         | 0.754 ± 0.005  | 0.235 ± 0.035           | 0.318 ± 0.012         | 0.461 ± 0.019      | 0.0321 ± 0.0015 |
| CQR (MLP)               | 0.796 ± 0.006 | 0.049 ± 0.005 | 0.187 ± 0.031         | 0.716 ± 0.018  | 0.244 ± 0.050           | 0.325 ± 0.013         | 0.463 ± 0.021      | 0.0321 ± 0.0014 |
| PCS-CQR (MLP)           | 0.795 ± 0.004 | 0.023 ± 0.003 | 0.074 ± 0.041         | 0.757 ± 0.010  | 0.164 ± 0.070           | 0.321 ± 0.014         | 0.462 ± 0.024      | 0.0320 ± 0.0014 |
| PCS                     | 0.809 ± 0.002 | 0.038 ± 0.002 | 0.108 ± 0.018         | 0.748 ± 0.006  | 0.204 ± 0.022           | 0.291 ± 0.013         | 0.498 ± 0.021      | 0.0347 ± 0.0025 |
| PCS (IS-tuned)          | 0.811 ± 0.003 | 0.040 ± 0.002 | 0.116 ± 0.013         | 0.746 ± 0.004  | 0.265 ± 0.045           | 0.286 ± 0.010         | 0.493 ± 0.021      | 0.0339 ± 0.0020 |
| HSC                     | 0.799 ± 0.003 | 0.039 ± 0.001 | 0.159 ± 0.030         | 0.734 ± 0.006  | 0.353 ± 0.039           | 0.276 ± 0.010         | 0.490 ± 0.024      | 0.0335 ± 0.0015 |
| ACI                     | 0.811 ± 0.004 | 0.060 ± 0.014 | 0.209 ± 0.083         | 0.716 ± 0.028  | 0.346 ± 0.025           | 0.279 ± 0.011         | 0.486 ± 0.024      | 0.0354 ± 0.0013 |
| Self-CP                 | 0.809 ± 0.004 | 0.038 ± 0.001 | 0.108 ± 0.022         | 0.748 ± 0.007  | 0.168 ± 0.015           | 0.294 ± 0.012         | 0.499 ± 0.021      | 0.0350 ± 0.0030 |
| SCP-stage               | 0.773 ± 0.011 | 0.139 ± 0.006 | 0.389 ± 0.026         | 0.527 ± 0.030  | 0.354 ± 0.024           | 0.280 ± 0.012         | 0.488 ± 0.025      | 0.0366 ± 0.0013 |
| SCP                     | 0.773 ± 0.011 | 0.139 ± 0.006 | 0.386 ± 0.027         | 0.526 ± 0.030  | 0.425 ± 0.031           | 0.279 ± 0.012         | 0.489 ± 0.025      | 0.0366 ± 0.0013 |
| Mondrian-usage          | 0.777 ± 0.015 | 0.137 ± 0.004 | 0.384 ± 0.039         | 0.539 ± 0.015  | 0.344 ± 0.049           | 0.265 ± 0.023         | 0.503 ± 0.024      | 0.0365 ± 0.0012 |
| Naive+SCP               | 0.777 ± 0.013 | 0.142 ± 0.006 | 0.404 ± 0.029         | 0.534 ± 0.025  | 0.347 ± 0.017           | 0.401 ± 0.027         | 0.738 ± 0.035      | 0.0525 ± 0.0025 |
| Raw-SCP                 | 0.812 ± 0.024 | 0.182 ± 0.014 | 0.280 ± 0.040         | 0.468 ± 0.086  | 0.316 ± 0.052           | 0.389 ± 0.019         | 0.692 ± 0.037      | 0.0731 ± 0.0050 |

### T_alpha0.2_UCI.md

**UCI, nominal 80%**

| Method                  | Coverage      | MACD          | Under-covered share   | P10 coverage   | Under-covered, week 1   | Rel. width (median)   | Rel. IS (median)   | Reserve cost    |
|:------------------------|:--------------|:--------------|:----------------------|:---------------|:------------------------|:----------------------|:-------------------|:----------------|
| PCS-CQR                 | 0.796 ± 0.003 | 0.019 ± 0.003 | 0.032 ± 0.018         | 0.768 ± 0.004  | 0.093 ± 0.038           | 0.213 ± 0.012         | 0.301 ± 0.013      | 0.0249 ± 0.0031 |
| PCS-CQR κ=168           | 0.798 ± 0.004 | 0.019 ± 0.003 | 0.038 ± 0.021         | 0.769 ± 0.008  | 0.114 ± 0.035           | 0.214 ± 0.011         | 0.301 ± 0.013      | 0.0249 ± 0.0030 |
| PCS-CQR (IS-tuned)      | 0.799 ± 0.004 | 0.021 ± 0.003 | 0.042 ± 0.020         | 0.769 ± 0.008  | 0.122 ± 0.040           | 0.215 ± 0.011         | 0.301 ± 0.013      | 0.0249 ± 0.0030 |
| HSC-CQR                 | 0.796 ± 0.003 | 0.021 ± 0.003 | 0.048 ± 0.022         | 0.767 ± 0.005  | 0.208 ± 0.036           | 0.214 ± 0.009         | 0.302 ± 0.012      | 0.0249 ± 0.0030 |
| CQR                     | 0.798 ± 0.017 | 0.048 ± 0.009 | 0.137 ± 0.090         | 0.745 ± 0.031  | 0.208 ± 0.049           | 0.219 ± 0.015         | 0.303 ± 0.011      | 0.0249 ± 0.0029 |
| Self-CQR                | 0.786 ± 0.002 | 0.025 ± 0.002 | 0.093 ± 0.027         | 0.751 ± 0.005  | 0.360 ± 0.049           | 0.209 ± 0.010         | 0.302 ± 0.013      | 0.0252 ± 0.0032 |
| ACI-CQR                 | 0.806 ± 0.006 | 0.021 ± 0.003 | 0.019 ± 0.014         | 0.779 ± 0.006  | 0.196 ± 0.040           | 0.217 ± 0.012         | 0.301 ± 0.012      | 0.0249 ± 0.0030 |
| ACI-CQR (MACD)          | 0.806 ± 0.005 | 0.017 ± 0.005 | 0.011 ± 0.015         | 0.782 ± 0.007  | 0.179 ± 0.036           | 0.217 ± 0.011         | 0.301 ± 0.013      | 0.0249 ± 0.0030 |
| ACI-CQR (coverage only) | 0.802 ± 0.001 | 0.006 ± 0.000 | 0.000 ± 0.000         | 0.793 ± 0.001  | 0.097 ± 0.025           | 0.220 ± 0.011         | 0.308 ± 0.016      | 0.0280 ± 0.0037 |
| TQA-B-CQR               | 0.808 ± 0.003 | 0.043 ± 0.005 | 0.103 ± 0.052         | 0.753 ± 0.017  | 0.149 ± 0.038           | 0.220 ± 0.006         | 0.306 ± 0.012      | 0.0250 ± 0.0030 |
| GHCP-CQR                | 0.805 ± 0.017 | 0.048 ± 0.007 | 0.120 ± 0.076         | 0.755 ± 0.029  | 0.120 ± 0.049           | 0.222 ± 0.015         | 0.303 ± 0.011      | 0.0249 ± 0.0029 |
| QShrink-CQR             | 0.795 ± 0.007 | 0.026 ± 0.008 | 0.067 ± 0.047         | 0.766 ± 0.015  | 0.171 ± 0.038           | 0.214 ± 0.011         | 0.302 ± 0.012      | 0.0249 ± 0.0030 |
| QShrink-CQR (MACD)      | 0.794 ± 0.004 | 0.020 ± 0.003 | 0.048 ± 0.021         | 0.767 ± 0.007  | 0.154 ± 0.035           | 0.212 ± 0.011         | 0.301 ± 0.013      | 0.0249 ± 0.0031 |
| QShrink-CQR λ=168       | 0.794 ± 0.004 | 0.020 ± 0.003 | 0.048 ± 0.026         | 0.766 ± 0.009  | 0.160 ± 0.043           | 0.213 ± 0.011         | 0.301 ± 0.013      | 0.0249 ± 0.0030 |
| CQR (MLP)               | 0.800 ± 0.010 | 0.045 ± 0.007 | 0.124 ± 0.073         | 0.746 ± 0.018  | 0.213 ± 0.036           | 0.213 ± 0.018         | 0.307 ± 0.011      | 0.0240 ± 0.0020 |
| PCS-CQR (MLP)           | 0.803 ± 0.010 | 0.022 ± 0.003 | 0.025 ± 0.027         | 0.774 ± 0.012  | 0.126 ± 0.053           | 0.214 ± 0.013         | 0.304 ± 0.011      | 0.0240 ± 0.0021 |
| PCS                     | 0.811 ± 0.003 | 0.029 ± 0.000 | 0.051 ± 0.025         | 0.768 ± 0.004  | 0.133 ± 0.031           | 0.205 ± 0.005         | 0.324 ± 0.010      | 0.0268 ± 0.0028 |
| PCS (IS-tuned)          | 0.813 ± 0.005 | 0.031 ± 0.003 | 0.046 ± 0.028         | 0.767 ± 0.004  | 0.166 ± 0.048           | 0.206 ± 0.006         | 0.322 ± 0.012      | 0.0265 ± 0.0025 |
| HSC                     | 0.805 ± 0.005 | 0.028 ± 0.001 | 0.067 ± 0.018         | 0.762 ± 0.005  | 0.242 ± 0.013           | 0.198 ± 0.007         | 0.321 ± 0.013      | 0.0265 ± 0.0026 |
| ACI                     | 0.816 ± 0.012 | 0.067 ± 0.031 | 0.162 ± 0.080         | 0.711 ± 0.049  | 0.267 ± 0.052           | 0.215 ± 0.013         | 0.324 ± 0.015      | 0.0277 ± 0.0025 |
| Self-CP                 | 0.811 ± 0.004 | 0.029 ± 0.002 | 0.046 ± 0.023         | 0.769 ± 0.005  | 0.093 ± 0.029           | 0.206 ± 0.005         | 0.324 ± 0.010      | 0.0268 ± 0.0029 |
| SCP-stage               | 0.806 ± 0.018 | 0.123 ± 0.006 | 0.278 ± 0.046         | 0.613 ± 0.032  | 0.276 ± 0.047           | 0.232 ± 0.014         | 0.327 ± 0.012      | 0.0289 ± 0.0027 |
| SCP                     | 0.805 ± 0.018 | 0.124 ± 0.006 | 0.276 ± 0.051         | 0.612 ± 0.033  | 0.322 ± 0.031           | 0.231 ± 0.014         | 0.328 ± 0.011      | 0.0288 ± 0.0027 |
| Naive+SCP               | 0.807 ± 0.016 | 0.097 ± 0.010 | 0.263 ± 0.051         | 0.638 ± 0.046  | 0.295 ± 0.062           | 0.294 ± 0.013         | 0.448 ± 0.018      | 0.0364 ± 0.0026 |
| Raw-SCP                 | 0.807 ± 0.056 | 0.208 ± 0.024 | 0.284 ± 0.086         | 0.407 ± 0.147  | 0.320 ± 0.089           | 0.405 ± 0.096         | 0.560 ± 0.026      | 0.0772 ± 0.0625 |

### T_cost_strategies.md

**Wall-clock time per calibration strategy and run (tuning + application for all targets; median and range over seeds)**

| dataset   | strategy                   |   median |    min |    max |
|:----------|:---------------------------|---------:|-------:|-------:|
| BDG2      | ACI-CQR                    |    1.201 |  1.137 |  1.474 |
| BDG2      | GHCP-CQR                   |    0.279 |  0.222 |  0.314 |
| BDG2      | HSC-CQR                    |   29.075 | 23.798 | 36.186 |
| BDG2      | PCS-CQR apply              |    0.258 |  0.216 |  0.298 |
| BDG2      | PCS-CQR tuning             |    1.072 |  0.957 |  1.307 |
| BDG2      | QShrink-CQR                |    1.663 |  1.45  |  1.822 |
| BDG2      | Self-CQR                   |    0.279 |  0.236 |  0.373 |
| BDG2      | TQA-B-CQR                  |    0.018 |  0.016 |  0.019 |
| BDG2      | own-score histograms (CQR) |    0.235 |  0.225 |  0.304 |
| UCI       | ACI-CQR                    |    0.39  |  0.39  |  0.475 |
| UCI       | GHCP-CQR                   |    0.08  |  0.075 |  0.113 |
| UCI       | HSC-CQR                    |    6.498 |  4.98  |  9.149 |
| UCI       | PCS-CQR apply              |    0.084 |  0.069 |  0.114 |
| UCI       | PCS-CQR tuning             |    0.31  |  0.302 |  0.43  |
| UCI       | QShrink-CQR                |    0.532 |  0.508 |  0.695 |
| UCI       | Self-CQR                   |    0.079 |  0.07  |  0.108 |
| UCI       | TQA-B-CQR                  |    0.007 |  0.006 |  0.008 |
| UCI       | own-score histograms (CQR) |    0.084 |  0.084 |  0.091 |

### T_efficiency.md

**Computational cost per run (calibration in single-threaded workers)**

| part              |   train_total_s |   lgb_train_s |   mlp_train_s |   n_train_rows |   lgb_pred_ms_per_target_day |   pcs_apply_ms_per_target_day |   pcs_apply_incl_hist_ms |   calibration_total_s |   pcs_store_MB |
|:------------------|----------------:|--------------:|--------------:|---------------:|-----------------------------:|------------------------------:|-------------------------:|----------------------:|---------------:|
| main_BDG2_s0_a0.1 |        152.469  |       70.185  |       80.0844 |        1318757 |                       0.7854 |                        0.021  |                   0.0369 |              162.312  |          0.016 |
| main_BDG2_s1_a0.1 |        340.926  |      288.62   |       50.5643 |        1322913 |                       0.6196 |                        0.0182 |                   0.0348 |              175.861  |          0.016 |
| main_BDG2_s2_a0.1 |        159.872  |       72.1269 |       86.3024 |        1320185 |                       0.1508 |                        0.0193 |                   0.0358 |              171.18   |          0.016 |
| main_BDG2_s3_a0.1 |        380.365  |      245.071  |      133.341  |        1318589 |                       1.1486 |                        0.0164 |                   0.0331 |              167.483  |          0.016 |
| main_BDG2_s4_a0.1 |        176.681  |      106.665  |       68.3012 |        1317922 |                       1.3921 |                        0.0152 |                   0.0367 |              148.195  |          0.016 |
| main_UCI_s0_a0.1  |         66.8659 |       25.0224 |       40.7428 |         992746 |                       0.0373 |                        0.0158 |                   0.033  |               37.8707 |          0.016 |
| main_UCI_s1_a0.1  |         65.0323 |       24.049  |       40.0236 |         998092 |                       0.0454 |                        0.0167 |                   0.0331 |               47.7622 |          0.016 |
| main_UCI_s2_a0.1  |         98.9822 |       44.2536 |       53.6681 |         994452 |                       0.0435 |                        0.0215 |                   0.0373 |               53.7682 |          0.016 |
| main_UCI_s3_a0.1  |         79.4134 |       22.279  |       55.9506 |         994891 |                       0.0445 |                        0.0149 |                   0.0306 |               47.8619 |          0.016 |
| main_UCI_s4_a0.1  |         96.9905 |       38.6432 |       57.3307 |         995880 |                       0.0699 |                        0.013  |                   0.0288 |               41.0963 |          0.016 |

### T_gen_BDG2toBDG2_nw.md

**Generalisation: BDG2->BDG2 (no weather)**

| Method                  | Coverage      | MACD          | Under-covered share   | P10 coverage   | Under-covered, week 1   | Rel. width (median)   | Rel. IS (median)   | Reserve cost    |
|:------------------------|:--------------|:--------------|:----------------------|:---------------|:------------------------|:----------------------|:-------------------|:----------------|
| PCS-CQR                 | 0.895 ± 0.002 | 0.015 ± 0.000 | 0.013 ± 0.002         | 0.870 ± 0.002  | 0.184 ± 0.005           | 0.403 ± 0.015         | 0.571 ± 0.025      | 0.0208 ± 0.0008 |
| PCS-CQR κ=168           | 0.895 ± 0.003 | 0.015 ± 0.000 | 0.016 ± 0.004         | 0.871 ± 0.003  | 0.191 ± 0.010           | 0.403 ± 0.015         | 0.571 ± 0.025      | 0.0208 ± 0.0008 |
| PCS-CQR (IS-tuned)      | 0.895 ± 0.003 | 0.017 ± 0.000 | 0.024 ± 0.008         | 0.869 ± 0.004  | 0.215 ± 0.024           | 0.398 ± 0.015         | 0.570 ± 0.025      | 0.0207 ± 0.0007 |
| PCS-CQR site-grouped    | 0.895 ± 0.002 | 0.015 ± 0.000 | 0.013 ± 0.002         | 0.870 ± 0.002  | 0.184 ± 0.005           | 0.403 ± 0.015         | 0.571 ± 0.025      | 0.0208 ± 0.0008 |
| PCS-CQR +stage          | 0.895 ± 0.003 | 0.015 ± 0.000 | 0.014 ± 0.005         | 0.870 ± 0.003  | 0.199 ± 0.015           | 0.403 ± 0.014         | 0.572 ± 0.025      | 0.0209 ± 0.0008 |
| PCS-CQR +kNN            | 0.895 ± 0.002 | 0.015 ± 0.000 | 0.016 ± 0.004         | 0.871 ± 0.001  | 0.195 ± 0.009           | 0.400 ± 0.018         | 0.572 ± 0.024      | 0.0208 ± 0.0008 |
| PCS-CQR +kNN+stage      | 0.894 ± 0.002 | 0.016 ± 0.000 | 0.016 ± 0.004         | 0.870 ± 0.002  | 0.216 ± 0.009           | 0.402 ± 0.016         | 0.573 ± 0.024      | 0.0208 ± 0.0008 |
| PCS-CQR -shrink         | 0.893 ± 0.004 | 0.037 ± 0.001 | 0.171 ± 0.016         | 0.834 ± 0.007  | 0.225 ± 0.024           | 0.389 ± 0.011         | 0.570 ± 0.022      | 0.0209 ± 0.0008 |
| HSC-CQR                 | 0.894 ± 0.003 | 0.017 ± 0.001 | 0.028 ± 0.008         | 0.867 ± 0.003  | 0.240 ± 0.008           | 0.394 ± 0.018         | 0.570 ± 0.025      | 0.0207 ± 0.0007 |
| CQR                     | 0.893 ± 0.003 | 0.037 ± 0.001 | 0.178 ± 0.018         | 0.833 ± 0.007  | 0.245 ± 0.014           | 0.390 ± 0.012         | 0.571 ± 0.023      | 0.0209 ± 0.0008 |
| Self-CQR                | 0.888 ± 0.003 | 0.022 ± 0.002 | 0.075 ± 0.007         | 0.857 ± 0.001  | 0.347 ± 0.023           | 0.404 ± 0.015         | 0.583 ± 0.022      | 0.0220 ± 0.0015 |
| ACI-CQR                 | 0.897 ± 0.002 | 0.020 ± 0.001 | 0.042 ± 0.005         | 0.865 ± 0.002  | 0.238 ± 0.012           | 0.397 ± 0.019         | 0.571 ± 0.026      | 0.0209 ± 0.0009 |
| ACI-CQR (MACD)          | 0.897 ± 0.002 | 0.020 ± 0.001 | 0.042 ± 0.005         | 0.865 ± 0.002  | 0.238 ± 0.012           | 0.397 ± 0.019         | 0.571 ± 0.026      | 0.0209 ± 0.0009 |
| ACI-CQR (coverage only) | 0.900 ± 0.000 | 0.004 ± 0.000 | 0.000 ± 0.000         | 0.894 ± 0.001  | 0.087 ± 0.014           | 0.878 ± 0.119         | 1.043 ± 0.130      | 0.0437 ± 0.0067 |
| TQA-B-CQR               | 0.896 ± 0.002 | 0.038 ± 0.002 | 0.178 ± 0.022         | 0.837 ± 0.003  | 0.235 ± 0.009           | 0.394 ± 0.012         | 0.569 ± 0.025      | 0.0210 ± 0.0007 |
| GHCP-CQR                | 0.896 ± 0.003 | 0.037 ± 0.001 | 0.155 ± 0.006         | 0.837 ± 0.007  | 0.216 ± 0.023           | 0.392 ± 0.012         | 0.569 ± 0.022      | 0.0209 ± 0.0008 |
| QShrink-CQR             | 0.898 ± 0.004 | 0.020 ± 0.003 | 0.030 ± 0.024         | 0.868 ± 0.004  | 0.221 ± 0.010           | 0.400 ± 0.020         | 0.571 ± 0.024      | 0.0210 ± 0.0010 |
| QShrink-CQR (MACD)      | 0.896 ± 0.003 | 0.015 ± 0.001 | 0.012 ± 0.004         | 0.872 ± 0.004  | 0.194 ± 0.004           | 0.403 ± 0.014         | 0.571 ± 0.025      | 0.0212 ± 0.0011 |
| QShrink-CQR λ=168       | 0.896 ± 0.003 | 0.015 ± 0.001 | 0.012 ± 0.004         | 0.872 ± 0.004  | 0.194 ± 0.004           | 0.403 ± 0.014         | 0.571 ± 0.025      | 0.0212 ± 0.0011 |
| QR-LGBM                 | 0.874 ± 0.012 | 0.042 ± 0.005 | 0.274 ± 0.089         | 0.815 ± 0.012  | 0.296 ± 0.031           | 0.373 ± 0.007         | 0.574 ± 0.027      | 0.0210 ± 0.0008 |
| MLP-QR                  | 0.900 ± 0.006 | 0.036 ± 0.004 | 0.125 ± 0.048         | 0.846 ± 0.011  | 0.216 ± 0.047           | 0.400 ± 0.007         | 0.561 ± 0.024      | 0.0207 ± 0.0008 |
| MLP-Gauss               | 0.929 ± 0.009 | 0.043 ± 0.003 | 0.038 ± 0.023         | 0.874 ± 0.016  | 0.100 ± 0.040           | 0.463 ± 0.047         | 0.606 ± 0.046      | 0.0240 ± 0.0031 |
| CQR (MLP)               | 0.894 ± 0.005 | 0.035 ± 0.004 | 0.146 ± 0.049         | 0.841 ± 0.010  | 0.217 ± 0.063           | 0.395 ± 0.008         | 0.560 ± 0.024      | 0.0207 ± 0.0008 |
| PCS-CQR (MLP)           | 0.898 ± 0.002 | 0.015 ± 0.000 | 0.016 ± 0.010         | 0.874 ± 0.003  | 0.162 ± 0.045           | 0.406 ± 0.018         | 0.561 ± 0.021      | 0.0207 ± 0.0009 |
| PCS                     | 0.904 ± 0.001 | 0.026 ± 0.001 | 0.066 ± 0.014         | 0.860 ± 0.000  | 0.182 ± 0.014           | 0.453 ± 0.030         | 0.655 ± 0.021      | 0.0243 ± 0.0018 |
| PCS (IS-tuned)          | 0.910 ± 0.002 | 0.028 ± 0.001 | 0.049 ± 0.006         | 0.864 ± 0.002  | 0.191 ± 0.026           | 0.450 ± 0.028         | 0.647 ± 0.017      | 0.0235 ± 0.0011 |
| HSC                     | 0.901 ± 0.002 | 0.029 ± 0.002 | 0.076 ± 0.015         | 0.856 ± 0.002  | 0.307 ± 0.067           | 0.428 ± 0.023         | 0.648 ± 0.020      | 0.0231 ± 0.0008 |
| HSC -stage              | 0.900 ± 0.001 | 0.028 ± 0.002 | 0.080 ± 0.008         | 0.855 ± 0.002  | 0.373 ± 0.074           | 0.427 ± 0.024         | 0.648 ± 0.018      | 0.0231 ± 0.0009 |
| HSC -kNN                | 0.911 ± 0.002 | 0.029 ± 0.001 | 0.049 ± 0.009         | 0.867 ± 0.003  | 0.144 ± 0.022           | 0.455 ± 0.028         | 0.646 ± 0.018      | 0.0236 ± 0.0011 |
| HSC -shrink             | 0.846 ± 0.006 | 0.092 ± 0.003 | 0.441 ± 0.016         | 0.692 ± 0.017  | 0.436 ± 0.071           | 0.373 ± 0.013         | 0.661 ± 0.031      | 0.0256 ± 0.0003 |
| ACI                     | 0.912 ± 0.003 | 0.049 ± 0.008 | 0.152 ± 0.047         | 0.831 ± 0.027  | 0.281 ± 0.031           | 0.444 ± 0.029         | 0.633 ± 0.021      | 0.0244 ± 0.0005 |
| Self-CP                 | 0.905 ± 0.001 | 0.027 ± 0.001 | 0.065 ± 0.012         | 0.861 ± 0.001  | 0.155 ± 0.005           | 0.457 ± 0.031         | 0.654 ± 0.024      | 0.0243 ± 0.0018 |
| SCP-stage               | 0.881 ± 0.005 | 0.094 ± 0.005 | 0.286 ± 0.019         | 0.701 ± 0.023  | 0.295 ± 0.022           | 0.463 ± 0.024         | 0.637 ± 0.023      | 0.0271 ± 0.0004 |
| SCP                     | 0.881 ± 0.005 | 0.094 ± 0.005 | 0.289 ± 0.022         | 0.701 ± 0.026  | 0.356 ± 0.008           | 0.462 ± 0.024         | 0.639 ± 0.016      | 0.0271 ± 0.0004 |
| Mondrian-usage          | 0.880 ± 0.008 | 0.093 ± 0.005 | 0.303 ± 0.020         | 0.707 ± 0.009  | 0.294 ± 0.014           | 0.427 ± 0.029         | 0.665 ± 0.036      | 0.0270 ± 0.0005 |
| Naive+SCP               | 0.876 ± 0.006 | 0.096 ± 0.006 | 0.314 ± 0.006         | 0.694 ± 0.033  | 0.314 ± 0.008           | 0.657 ± 0.041         | 0.965 ± 0.060      | 0.0388 ± 0.0012 |
| Raw-SCP                 | 0.905 ± 0.032 | 0.119 ± 0.019 | 0.191 ± 0.068         | 0.682 ± 0.155  | 0.212 ± 0.066           | 0.741 ± 0.046         | 1.114 ± 0.017      | 0.0635 ± 0.0058 |

### T_gen_BDG2toUCI_nw.md

**Generalisation: BDG2->UCI (no weather)**

| Method                  | Coverage      | MACD          | Under-covered share   | P10 coverage   | Under-covered, week 1   | Rel. width (median)   | Rel. IS (median)   | Reserve cost    |
|:------------------------|:--------------|:--------------|:----------------------|:---------------|:------------------------|:----------------------|:-------------------|:----------------|
| PCS-CQR                 | 0.901 ± 0.002 | 0.011 ± 0.001 | 0.004 ± 0.006         | 0.885 ± 0.001  | 0.081 ± 0.034           | 0.314 ± 0.007         | 0.439 ± 0.015      | 0.0164 ± 0.0014 |
| PCS-CQR κ=168           | 0.901 ± 0.002 | 0.011 ± 0.001 | 0.004 ± 0.006         | 0.885 ± 0.001  | 0.088 ± 0.043           | 0.315 ± 0.007         | 0.439 ± 0.016      | 0.0164 ± 0.0013 |
| PCS-CQR (IS-tuned)      | 0.902 ± 0.003 | 0.013 ± 0.001 | 0.007 ± 0.006         | 0.885 ± 0.003  | 0.102 ± 0.032           | 0.315 ± 0.005         | 0.438 ± 0.016      | 0.0163 ± 0.0013 |
| PCS-CQR +stage          | 0.900 ± 0.002 | 0.011 ± 0.001 | 0.004 ± 0.006         | 0.884 ± 0.001  | 0.098 ± 0.022           | 0.313 ± 0.007         | 0.438 ± 0.015      | 0.0164 ± 0.0014 |
| PCS-CQR +kNN            | 0.899 ± 0.003 | 0.012 ± 0.001 | 0.004 ± 0.006         | 0.882 ± 0.003  | 0.123 ± 0.084           | 0.313 ± 0.008         | 0.439 ± 0.016      | 0.0164 ± 0.0013 |
| PCS-CQR +kNN+stage      | 0.898 ± 0.003 | 0.012 ± 0.000 | 0.004 ± 0.006         | 0.882 ± 0.001  | 0.147 ± 0.086           | 0.312 ± 0.008         | 0.439 ± 0.013      | 0.0164 ± 0.0014 |
| PCS-CQR -shrink         | 0.902 ± 0.013 | 0.028 ± 0.005 | 0.056 ± 0.043         | 0.867 ± 0.011  | 0.137 ± 0.046           | 0.315 ± 0.013         | 0.440 ± 0.015      | 0.0163 ± 0.0013 |
| HSC-CQR                 | 0.899 ± 0.004 | 0.013 ± 0.000 | 0.004 ± 0.006         | 0.881 ± 0.005  | 0.172 ± 0.090           | 0.311 ± 0.007         | 0.437 ± 0.016      | 0.0163 ± 0.0013 |
| CQR                     | 0.902 ± 0.013 | 0.027 ± 0.005 | 0.056 ± 0.043         | 0.868 ± 0.011  | 0.151 ± 0.030           | 0.316 ± 0.013         | 0.439 ± 0.015      | 0.0163 ± 0.0013 |
| Self-CQR                | 0.892 ± 0.003 | 0.016 ± 0.001 | 0.021 ± 0.028         | 0.866 ± 0.004  | 0.316 ± 0.092           | 0.314 ± 0.007         | 0.444 ± 0.014      | 0.0169 ± 0.0015 |
| ACI-CQR                 | 0.903 ± 0.005 | 0.015 ± 0.000 | 0.011 ± 0.011         | 0.884 ± 0.004  | 0.133 ± 0.016           | 0.315 ± 0.007         | 0.437 ± 0.016      | 0.0163 ± 0.0013 |
| ACI-CQR (MACD)          | 0.903 ± 0.005 | 0.015 ± 0.000 | 0.011 ± 0.011         | 0.884 ± 0.004  | 0.133 ± 0.016           | 0.315 ± 0.007         | 0.437 ± 0.016      | 0.0163 ± 0.0013 |
| ACI-CQR (coverage only) | 0.901 ± 0.001 | 0.004 ± 0.000 | 0.000 ± 0.000         | 0.896 ± 0.001  | 0.046 ± 0.012           | 0.465 ± 0.036         | 0.572 ± 0.032      | 0.0269 ± 0.0064 |
| TQA-B-CQR               | 0.900 ± 0.013 | 0.027 ± 0.005 | 0.063 ± 0.038         | 0.866 ± 0.012  | 0.161 ± 0.037           | 0.312 ± 0.012         | 0.438 ± 0.017      | 0.0163 ± 0.0012 |
| GHCP-CQR                | 0.905 ± 0.013 | 0.028 ± 0.004 | 0.053 ± 0.038         | 0.871 ± 0.010  | 0.105 ± 0.028           | 0.318 ± 0.013         | 0.440 ± 0.015      | 0.0163 ± 0.0013 |
| QShrink-CQR             | 0.902 ± 0.003 | 0.014 ± 0.001 | 0.004 ± 0.006         | 0.882 ± 0.003  | 0.116 ± 0.021           | 0.314 ± 0.004         | 0.436 ± 0.016      | 0.0163 ± 0.0013 |
| QShrink-CQR (MACD)      | 0.900 ± 0.002 | 0.011 ± 0.001 | 0.000 ± 0.000         | 0.884 ± 0.000  | 0.105 ± 0.032           | 0.313 ± 0.006         | 0.437 ± 0.016      | 0.0165 ± 0.0014 |
| QShrink-CQR λ=168       | 0.900 ± 0.002 | 0.011 ± 0.001 | 0.000 ± 0.000         | 0.884 ± 0.000  | 0.105 ± 0.032           | 0.313 ± 0.006         | 0.437 ± 0.016      | 0.0165 ± 0.0014 |
| QR-LGBM                 | 0.882 ± 0.005 | 0.031 ± 0.006 | 0.161 ± 0.016         | 0.841 ± 0.004  | 0.207 ± 0.037           | 0.299 ± 0.006         | 0.440 ± 0.016      | 0.0163 ± 0.0013 |
| MLP-QR                  | 0.908 ± 0.002 | 0.024 ± 0.002 | 0.035 ± 0.022         | 0.873 ± 0.005  | 0.130 ± 0.070           | 0.326 ± 0.003         | 0.433 ± 0.013      | 0.0162 ± 0.0013 |
| MLP-Gauss               | 0.947 ± 0.014 | 0.048 ± 0.014 | 0.004 ± 0.006         | 0.919 ± 0.014  | 0.025 ± 0.006           | 0.383 ± 0.039         | 0.455 ± 0.024      | 0.0175 ± 0.0011 |
| CQR (MLP)               | 0.901 ± 0.003 | 0.024 ± 0.003 | 0.042 ± 0.021         | 0.866 ± 0.005  | 0.112 ± 0.024           | 0.321 ± 0.003         | 0.433 ± 0.016      | 0.0162 ± 0.0013 |
| PCS-CQR (MLP)           | 0.900 ± 0.004 | 0.013 ± 0.001 | 0.004 ± 0.006         | 0.880 ± 0.007  | 0.105 ± 0.056           | 0.327 ± 0.016         | 0.434 ± 0.013      | 0.0164 ± 0.0014 |
| PCS                     | 0.918 ± 0.001 | 0.026 ± 0.001 | 0.018 ± 0.016         | 0.890 ± 0.002  | 0.140 ± 0.034           | 0.363 ± 0.009         | 0.485 ± 0.023      | 0.0197 ± 0.0018 |
| PCS (IS-tuned)          | 0.923 ± 0.002 | 0.031 ± 0.003 | 0.011 ± 0.018         | 0.889 ± 0.009  | 0.102 ± 0.016           | 0.372 ± 0.015         | 0.478 ± 0.016      | 0.0194 ± 0.0018 |
| HSC                     | 0.920 ± 0.002 | 0.031 ± 0.005 | 0.042 ± 0.000         | 0.881 ± 0.009  | 0.186 ± 0.016           | 0.359 ± 0.009         | 0.474 ± 0.016      | 0.0192 ± 0.0018 |
| HSC -stage              | 0.919 ± 0.003 | 0.031 ± 0.005 | 0.042 ± 0.000         | 0.877 ± 0.010  | 0.235 ± 0.016           | 0.359 ± 0.009         | 0.474 ± 0.016      | 0.0193 ± 0.0018 |
| HSC -kNN                | 0.925 ± 0.002 | 0.032 ± 0.003 | 0.007 ± 0.012         | 0.892 ± 0.009  | 0.074 ± 0.011           | 0.377 ± 0.015         | 0.481 ± 0.015      | 0.0194 ± 0.0018 |
| HSC -shrink             | 0.896 ± 0.010 | 0.077 ± 0.008 | 0.207 ± 0.034         | 0.776 ± 0.012  | 0.365 ± 0.044           | 0.392 ± 0.026         | 0.498 ± 0.007      | 0.0223 ± 0.0035 |
| ACI                     | 0.931 ± 0.004 | 0.052 ± 0.008 | 0.095 ± 0.021         | 0.856 ± 0.010  | 0.207 ± 0.043           | 0.405 ± 0.032         | 0.484 ± 0.022      | 0.0221 ± 0.0041 |
| Self-CP                 | 0.920 ± 0.001 | 0.026 ± 0.001 | 0.018 ± 0.016         | 0.892 ± 0.003  | 0.130 ± 0.026           | 0.366 ± 0.010         | 0.488 ± 0.023      | 0.0197 ± 0.0018 |
| SCP-stage               | 0.915 ± 0.009 | 0.088 ± 0.009 | 0.158 ± 0.028         | 0.800 ± 0.016  | 0.221 ± 0.038           | 0.463 ± 0.024         | 0.519 ± 0.018      | 0.0231 ± 0.0032 |
| SCP                     | 0.914 ± 0.010 | 0.087 ± 0.008 | 0.158 ± 0.028         | 0.802 ± 0.015  | 0.284 ± 0.038           | 0.462 ± 0.024         | 0.521 ± 0.017      | 0.0233 ± 0.0033 |
| Naive+SCP               | 0.941 ± 0.007 | 0.085 ± 0.001 | 0.109 ± 0.006         | 0.847 ± 0.006  | 0.140 ± 0.022           | 0.657 ± 0.041         | 0.686 ± 0.029      | 0.0279 ± 0.0017 |
| Raw-SCP                 | 0.786 ± 0.043 | 0.196 ± 0.036 | 0.411 ± 0.079         | 0.358 ± 0.136  | 0.512 ± 0.043           | 0.410 ± 0.038         | 0.754 ± 0.048      | 0.0319 ± 0.0017 |

### T_gen_UCItoBDG2_nw.md

**Generalisation: UCI->BDG2 (no weather)**

| Method                  | Coverage      | MACD          | Under-covered share   | P10 coverage   | Under-covered, week 1   | Rel. width (median)   | Rel. IS (median)   | Reserve cost    |
|:------------------------|:--------------|:--------------|:----------------------|:---------------|:------------------------|:----------------------|:-------------------|:----------------|
| PCS-CQR                 | 0.893 ± 0.004 | 0.019 ± 0.002 | 0.042 ± 0.032         | 0.865 ± 0.008  | 0.298 ± 0.035           | 0.413 ± 0.016         | 0.603 ± 0.028      | 0.0227 ± 0.0017 |
| PCS-CQR κ=168           | 0.891 ± 0.002 | 0.019 ± 0.002 | 0.045 ± 0.030         | 0.862 ± 0.005  | 0.333 ± 0.024           | 0.406 ± 0.019         | 0.602 ± 0.030      | 0.0224 ± 0.0014 |
| PCS-CQR (IS-tuned)      | 0.888 ± 0.002 | 0.022 ± 0.003 | 0.070 ± 0.051         | 0.856 ± 0.008  | 0.362 ± 0.050           | 0.403 ± 0.021         | 0.601 ± 0.030      | 0.0224 ± 0.0014 |
| PCS-CQR +stage          | 0.894 ± 0.004 | 0.019 ± 0.002 | 0.040 ± 0.025         | 0.866 ± 0.007  | 0.265 ± 0.043           | 0.414 ± 0.015         | 0.603 ± 0.030      | 0.0227 ± 0.0017 |
| PCS-CQR +kNN            | 0.892 ± 0.004 | 0.019 ± 0.002 | 0.043 ± 0.029         | 0.863 ± 0.007  | 0.316 ± 0.025           | 0.410 ± 0.015         | 0.604 ± 0.029      | 0.0227 ± 0.0017 |
| PCS-CQR +kNN+stage      | 0.893 ± 0.003 | 0.019 ± 0.002 | 0.041 ± 0.024         | 0.865 ± 0.006  | 0.291 ± 0.016           | 0.407 ± 0.020         | 0.603 ± 0.033      | 0.0227 ± 0.0017 |
| PCS-CQR -shrink         | 0.861 ± 0.002 | 0.060 ± 0.005 | 0.416 ± 0.030         | 0.780 ± 0.015  | 0.419 ± 0.029           | 0.373 ± 0.021         | 0.606 ± 0.028      | 0.0228 ± 0.0012 |
| HSC-CQR                 | 0.886 ± 0.002 | 0.023 ± 0.003 | 0.087 ± 0.049         | 0.853 ± 0.007  | 0.397 ± 0.037           | 0.399 ± 0.020         | 0.601 ± 0.030      | 0.0224 ± 0.0014 |
| CQR                     | 0.861 ± 0.002 | 0.059 ± 0.005 | 0.419 ± 0.028         | 0.780 ± 0.015  | 0.399 ± 0.049           | 0.374 ± 0.020         | 0.606 ± 0.029      | 0.0228 ± 0.0012 |
| Self-CQR                | 0.893 ± 0.004 | 0.023 ± 0.002 | 0.080 ± 0.036         | 0.855 ± 0.008  | 0.394 ± 0.038           | 0.426 ± 0.019         | 0.613 ± 0.032      | 0.0236 ± 0.0024 |
| ACI-CQR                 | 0.882 ± 0.011 | 0.030 ± 0.014 | 0.165 ± 0.148         | 0.843 ± 0.029  | 0.377 ± 0.037           | 0.399 ± 0.003         | 0.601 ± 0.027      | 0.0228 ± 0.0013 |
| ACI-CQR (MACD)          | 0.882 ± 0.011 | 0.030 ± 0.014 | 0.165 ± 0.148         | 0.843 ± 0.029  | 0.377 ± 0.037           | 0.399 ± 0.003         | 0.601 ± 0.027      | 0.0228 ± 0.0013 |
| ACI-CQR (coverage only) | 0.899 ± 0.000 | 0.005 ± 0.000 | 0.000 ± 0.000         | 0.892 ± 0.001  | 0.144 ± 0.022           | 1.690 ± 1.207         | 1.934 ± 1.271      | 0.0676 ± 0.0436 |
| TQA-B-CQR               | 0.868 ± 0.006 | 0.056 ± 0.004 | 0.377 ± 0.022         | 0.788 ± 0.012  | 0.379 ± 0.035           | 0.377 ± 0.019         | 0.605 ± 0.029      | 0.0227 ± 0.0012 |
| GHCP-CQR                | 0.868 ± 0.002 | 0.056 ± 0.005 | 0.370 ± 0.005         | 0.789 ± 0.015  | 0.369 ± 0.018           | 0.380 ± 0.021         | 0.605 ± 0.030      | 0.0227 ± 0.0012 |
| QShrink-CQR             | 0.888 ± 0.003 | 0.026 ± 0.006 | 0.107 ± 0.064         | 0.849 ± 0.013  | 0.337 ± 0.033           | 0.400 ± 0.021         | 0.603 ± 0.031      | 0.0226 ± 0.0016 |
| QShrink-CQR (MACD)      | 0.895 ± 0.004 | 0.019 ± 0.002 | 0.034 ± 0.022         | 0.866 ± 0.006  | 0.283 ± 0.008           | 0.412 ± 0.013         | 0.605 ± 0.032      | 0.0228 ± 0.0018 |
| QShrink-CQR λ=168       | 0.893 ± 0.003 | 0.019 ± 0.002 | 0.041 ± 0.018         | 0.865 ± 0.005  | 0.292 ± 0.024           | 0.408 ± 0.014         | 0.603 ± 0.032      | 0.0226 ± 0.0016 |
| QR-LGBM                 | 0.838 ± 0.007 | 0.072 ± 0.007 | 0.555 ± 0.050         | 0.757 ± 0.020  | 0.499 ± 0.026           | 0.355 ± 0.017         | 0.616 ± 0.035      | 0.0230 ± 0.0012 |
| MLP-QR                  | 0.854 ± 0.019 | 0.065 ± 0.012 | 0.439 ± 0.122         | 0.763 ± 0.027  | 0.480 ± 0.064           | 0.376 ± 0.009         | 0.623 ± 0.038      | 0.0226 ± 0.0005 |
| MLP-Gauss               | 0.892 ± 0.014 | 0.050 ± 0.005 | 0.240 ± 0.090         | 0.814 ± 0.018  | 0.256 ± 0.064           | 0.428 ± 0.034         | 0.659 ± 0.044      | 0.0308 ± 0.0071 |
| CQR (MLP)               | 0.859 ± 0.005 | 0.061 ± 0.008 | 0.399 ± 0.042         | 0.769 ± 0.019  | 0.404 ± 0.042           | 0.381 ± 0.013         | 0.622 ± 0.035      | 0.0226 ± 0.0004 |
| PCS-CQR (MLP)           | 0.898 ± 0.006 | 0.020 ± 0.002 | 0.032 ± 0.004         | 0.867 ± 0.005  | 0.296 ± 0.079           | 0.429 ± 0.013         | 0.613 ± 0.029      | 0.0225 ± 0.0013 |
| PCS                     | 0.904 ± 0.001 | 0.026 ± 0.001 | 0.074 ± 0.013         | 0.859 ± 0.002  | 0.196 ± 0.042           | 0.472 ± 0.022         | 0.704 ± 0.039      | 0.0256 ± 0.0022 |
| PCS (IS-tuned)          | 0.905 ± 0.001 | 0.028 ± 0.001 | 0.072 ± 0.018         | 0.859 ± 0.005  | 0.235 ± 0.076           | 0.461 ± 0.027         | 0.688 ± 0.042      | 0.0251 ± 0.0022 |
| HSC                     | 0.897 ± 0.006 | 0.029 ± 0.002 | 0.107 ± 0.040         | 0.846 ± 0.008  | 0.365 ± 0.176           | 0.438 ± 0.043         | 0.688 ± 0.045      | 0.0250 ± 0.0022 |
| HSC -stage              | 0.898 ± 0.003 | 0.028 ± 0.001 | 0.096 ± 0.011         | 0.850 ± 0.003  | 0.408 ± 0.119           | 0.444 ± 0.034         | 0.692 ± 0.046      | 0.0250 ± 0.0022 |
| HSC -kNN                | 0.906 ± 0.002 | 0.028 ± 0.001 | 0.072 ± 0.011         | 0.862 ± 0.004  | 0.163 ± 0.041           | 0.466 ± 0.028         | 0.690 ± 0.049      | 0.0253 ± 0.0024 |
| HSC -shrink             | 0.772 ± 0.026 | 0.151 ± 0.020 | 0.655 ± 0.058         | 0.570 ± 0.032  | 0.635 ± 0.026           | 0.292 ± 0.036         | 0.763 ± 0.068      | 0.0296 ± 0.0018 |
| ACI                     | 0.893 ± 0.006 | 0.046 ± 0.008 | 0.235 ± 0.044         | 0.825 ± 0.026  | 0.385 ± 0.026           | 0.416 ± 0.015         | 0.670 ± 0.048      | 0.0252 ± 0.0008 |
| Self-CP                 | 0.905 ± 0.002 | 0.027 ± 0.001 | 0.071 ± 0.010         | 0.860 ± 0.002  | 0.169 ± 0.038           | 0.475 ± 0.022         | 0.698 ± 0.043      | 0.0256 ± 0.0022 |
| SCP-stage               | 0.837 ± 0.006 | 0.111 ± 0.001 | 0.419 ± 0.029         | 0.635 ± 0.017  | 0.401 ± 0.023           | 0.396 ± 0.016         | 0.674 ± 0.048      | 0.0290 ± 0.0012 |
| SCP                     | 0.837 ± 0.006 | 0.111 ± 0.001 | 0.424 ± 0.026         | 0.635 ± 0.019  | 0.486 ± 0.007           | 0.394 ± 0.016         | 0.674 ± 0.047      | 0.0290 ± 0.0012 |
| Naive+SCP               | 0.824 ± 0.015 | 0.123 ± 0.010 | 0.472 ± 0.042         | 0.605 ± 0.034  | 0.436 ± 0.014           | 0.490 ± 0.007         | 0.956 ± 0.082      | 0.0402 ± 0.0006 |
| Raw-SCP                 | 0.963 ± 0.017 | 0.103 ± 0.005 | 0.076 ± 0.034         | 0.896 ± 0.065  | 0.094 ± 0.053           | 1.917 ± 0.384         | 2.077 ± 0.292      | 0.1387 ± 0.0166 |

### T_gen_leave-site-out.md

**Generalisation: leave-site-out**

| Method                  | Coverage      | MACD          | Under-covered share   | P10 coverage   | Under-covered, week 1   | Rel. width (median)   | Rel. IS (median)   | Reserve cost    |
|:------------------------|:--------------|:--------------|:----------------------|:---------------|:------------------------|:----------------------|:-------------------|:----------------|
| PCS-CQR                 | 0.894 ± 0.001 | 0.016 ± 0.001 | 0.024 ± 0.002         | 0.868 ± 0.002  | 0.222 ± 0.010           | 0.378 ± 0.005         | 0.541 ± 0.008      | 0.0187 ± 0.0005 |
| PCS-CQR κ=168           | 0.894 ± 0.000 | 0.016 ± 0.000 | 0.023 ± 0.002         | 0.868 ± 0.001  | 0.229 ± 0.014           | 0.376 ± 0.004         | 0.541 ± 0.008      | 0.0186 ± 0.0006 |
| PCS-CQR (IS-tuned)      | 0.893 ± 0.000 | 0.019 ± 0.000 | 0.038 ± 0.003         | 0.863 ± 0.001  | 0.255 ± 0.012           | 0.374 ± 0.001         | 0.540 ± 0.008      | 0.0186 ± 0.0006 |
| PCS-CQR site-grouped    | 0.894 ± 0.001 | 0.016 ± 0.001 | 0.023 ± 0.002         | 0.868 ± 0.003  | 0.222 ± 0.010           | 0.377 ± 0.005         | 0.541 ± 0.008      | 0.0187 ± 0.0005 |
| PCS-CQR +stage          | 0.895 ± 0.001 | 0.016 ± 0.001 | 0.022 ± 0.002         | 0.869 ± 0.002  | 0.209 ± 0.020           | 0.378 ± 0.004         | 0.541 ± 0.008      | 0.0187 ± 0.0005 |
| PCS-CQR +kNN            | 0.893 ± 0.001 | 0.016 ± 0.000 | 0.024 ± 0.002         | 0.867 ± 0.002  | 0.237 ± 0.012           | 0.374 ± 0.004         | 0.541 ± 0.008      | 0.0186 ± 0.0006 |
| PCS-CQR +kNN+stage      | 0.893 ± 0.001 | 0.016 ± 0.000 | 0.026 ± 0.001         | 0.867 ± 0.001  | 0.234 ± 0.023           | 0.375 ± 0.005         | 0.541 ± 0.009      | 0.0186 ± 0.0006 |
| PCS-CQR -shrink         | 0.887 ± 0.001 | 0.044 ± 0.001 | 0.247 ± 0.014         | 0.815 ± 0.003  | 0.281 ± 0.001           | 0.366 ± 0.003         | 0.543 ± 0.005      | 0.0189 ± 0.0006 |
| HSC-CQR                 | 0.890 ± 0.001 | 0.020 ± 0.000 | 0.046 ± 0.004         | 0.860 ± 0.001  | 0.282 ± 0.041           | 0.370 ± 0.001         | 0.541 ± 0.007      | 0.0186 ± 0.0006 |
| CQR                     | 0.887 ± 0.001 | 0.044 ± 0.001 | 0.248 ± 0.013         | 0.815 ± 0.004  | 0.273 ± 0.017           | 0.366 ± 0.003         | 0.543 ± 0.005      | 0.0189 ± 0.0006 |
| Self-CQR                | 0.890 ± 0.000 | 0.021 ± 0.000 | 0.071 ± 0.006         | 0.856 ± 0.002  | 0.356 ± 0.015           | 0.385 ± 0.004         | 0.549 ± 0.008      | 0.0191 ± 0.0006 |
| ACI-CQR                 | 0.894 ± 0.000 | 0.026 ± 0.001 | 0.077 ± 0.005         | 0.854 ± 0.001  | 0.267 ± 0.019           | 0.375 ± 0.001         | 0.540 ± 0.007      | 0.0192 ± 0.0009 |
| ACI-CQR (MACD)          | 0.893 ± 0.000 | 0.024 ± 0.001 | 0.069 ± 0.007         | 0.856 ± 0.001  | 0.266 ± 0.018           | 0.374 ± 0.001         | 0.540 ± 0.007      | 0.0191 ± 0.0009 |
| ACI-CQR (coverage only) | 0.900 ± 0.000 | 0.004 ± 0.000 | 0.000 ± 0.000         | 0.893 ± 0.000  | 0.111 ± 0.008           | 1.770 ± 0.505         | 1.949 ± 0.504      | 0.0807 ± 0.0262 |
| TQA-B-CQR               | 0.890 ± 0.001 | 0.043 ± 0.002 | 0.236 ± 0.015         | 0.820 ± 0.004  | 0.268 ± 0.014           | 0.367 ± 0.002         | 0.542 ± 0.007      | 0.0189 ± 0.0006 |
| GHCP-CQR                | 0.889 ± 0.001 | 0.044 ± 0.001 | 0.238 ± 0.012         | 0.818 ± 0.003  | 0.269 ± 0.006           | 0.368 ± 0.003         | 0.543 ± 0.006      | 0.0189 ± 0.0006 |
| QShrink-CQR             | 0.896 ± 0.000 | 0.024 ± 0.001 | 0.057 ± 0.011         | 0.859 ± 0.002  | 0.241 ± 0.021           | 0.373 ± 0.001         | 0.541 ± 0.008      | 0.0186 ± 0.0006 |
| QShrink-CQR (MACD)      | 0.896 ± 0.000 | 0.016 ± 0.001 | 0.020 ± 0.001         | 0.870 ± 0.001  | 0.210 ± 0.023           | 0.378 ± 0.003         | 0.542 ± 0.007      | 0.0187 ± 0.0006 |
| QShrink-CQR λ=168       | 0.896 ± 0.000 | 0.016 ± 0.000 | 0.021 ± 0.001         | 0.869 ± 0.001  | 0.213 ± 0.021           | 0.378 ± 0.004         | 0.542 ± 0.007      | 0.0187 ± 0.0006 |
| QR-LGBM                 | 0.860 ± 0.002 | 0.052 ± 0.002 | 0.412 ± 0.015         | 0.790 ± 0.009  | 0.367 ± 0.011           | 0.345 ± 0.001         | 0.548 ± 0.004      | 0.0190 ± 0.0006 |
| MLP-QR                  | 0.883 ± 0.005 | 0.044 ± 0.001 | 0.259 ± 0.023         | 0.818 ± 0.001  | 0.293 ± 0.010           | 0.378 ± 0.007         | 0.551 ± 0.001      | 0.0190 ± 0.0002 |
| MLP-Gauss               | 0.935 ± 0.008 | 0.048 ± 0.004 | 0.042 ± 0.014         | 0.878 ± 0.013  | 0.097 ± 0.020           | 0.489 ± 0.022         | 0.625 ± 0.014      | 0.0224 ± 0.0006 |
| CQR (MLP)               | 0.887 ± 0.001 | 0.042 ± 0.002 | 0.231 ± 0.007         | 0.820 ± 0.003  | 0.279 ± 0.010           | 0.381 ± 0.003         | 0.549 ± 0.001      | 0.0190 ± 0.0002 |
| PCS-CQR (MLP)           | 0.894 ± 0.001 | 0.017 ± 0.000 | 0.027 ± 0.012         | 0.867 ± 0.001  | 0.215 ± 0.025           | 0.389 ± 0.007         | 0.548 ± 0.002      | 0.0188 ± 0.0002 |
| PCS                     | 0.905 ± 0.001 | 0.026 ± 0.000 | 0.061 ± 0.003         | 0.861 ± 0.002  | 0.194 ± 0.013           | 0.424 ± 0.001         | 0.634 ± 0.016      | 0.0213 ± 0.0004 |
| PCS (IS-tuned)          | 0.910 ± 0.001 | 0.029 ± 0.002 | 0.059 ± 0.006         | 0.864 ± 0.002  | 0.219 ± 0.027           | 0.420 ± 0.001         | 0.625 ± 0.014      | 0.0210 ± 0.0005 |
| HSC                     | 0.899 ± 0.002 | 0.028 ± 0.002 | 0.094 ± 0.020         | 0.851 ± 0.005  | 0.301 ± 0.042           | 0.403 ± 0.008         | 0.624 ± 0.010      | 0.0209 ± 0.0004 |
| HSC -stage              | 0.899 ± 0.001 | 0.027 ± 0.001 | 0.089 ± 0.015         | 0.853 ± 0.003  | 0.365 ± 0.044           | 0.402 ± 0.005         | 0.626 ± 0.010      | 0.0209 ± 0.0005 |
| HSC -kNN                | 0.912 ± 0.001 | 0.030 ± 0.002 | 0.051 ± 0.004         | 0.867 ± 0.002  | 0.147 ± 0.009           | 0.427 ± 0.001         | 0.625 ± 0.012      | 0.0210 ± 0.0005 |
| HSC -shrink             | 0.821 ± 0.011 | 0.110 ± 0.008 | 0.505 ± 0.020         | 0.640 ± 0.018  | 0.485 ± 0.019           | 0.327 ± 0.017         | 0.673 ± 0.005      | 0.0243 ± 0.0007 |
| ACI                     | 0.905 ± 0.002 | 0.060 ± 0.002 | 0.220 ± 0.023         | 0.806 ± 0.015  | 0.278 ± 0.005           | 0.441 ± 0.006         | 0.623 ± 0.011      | 0.0241 ± 0.0013 |
| Self-CP                 | 0.905 ± 0.001 | 0.026 ± 0.000 | 0.059 ± 0.003         | 0.862 ± 0.002  | 0.157 ± 0.010           | 0.428 ± 0.002         | 0.635 ± 0.017      | 0.0213 ± 0.0004 |
| SCP-stage               | 0.873 ± 0.006 | 0.101 ± 0.005 | 0.327 ± 0.010         | 0.681 ± 0.013  | 0.283 ± 0.003           | 0.452 ± 0.007         | 0.632 ± 0.009      | 0.0253 ± 0.0006 |
| SCP                     | 0.874 ± 0.006 | 0.100 ± 0.004 | 0.323 ± 0.008         | 0.684 ± 0.013  | 0.366 ± 0.006           | 0.452 ± 0.007         | 0.633 ± 0.010      | 0.0253 ± 0.0006 |
| Mondrian-usage          | 0.866 ± 0.005 | 0.103 ± 0.006 | 0.350 ± 0.021         | 0.673 ± 0.020  | 0.306 ± 0.006           | 0.405 ± 0.016         | 0.654 ± 0.009      | 0.0253 ± 0.0007 |
| Naive+SCP               | 0.877 ± 0.004 | 0.101 ± 0.004 | 0.318 ± 0.010         | 0.674 ± 0.009  | 0.279 ± 0.014           | 0.698 ± 0.006         | 0.935 ± 0.023      | 0.0354 ± 0.0011 |
| Raw-SCP                 | 0.895 ± 0.010 | 0.120 ± 0.003 | 0.220 ± 0.017         | 0.652 ± 0.030  | 0.255 ± 0.022           | 0.665 ± 0.037         | 1.021 ± 0.037      | 0.0590 ± 0.0037 |

### T_loso_site_balanced.md

**Leave-one-site-out, site-balanced means**

| method             |   under |   macd |
|:-------------------|--------:|-------:|
| ACI-CQR            |   0.081 |  0.026 |
| CQR                |   0.205 |  0.043 |
| GHCP-CQR           |   0.197 |  0.043 |
| HSC-CQR            |   0.04  |  0.018 |
| PCS-CQR            |   0.017 |  0.015 |
| PCS-CQR +kNN+stage |   0.019 |  0.016 |
| PCS-CQR κ=168      |   0.016 |  0.015 |
| QShrink-CQR (MACD) |   0.013 |  0.015 |
| Self-CQR           |   0.084 |  0.022 |
| TQA-B-CQR          |   0.182 |  0.04  |

### T_loso_sites.md

**Leave-one-site-out: under-covered share per held-out site (building x seed units, 3 training seeds)**

| site_id   |   n_buildings |   PCS-CQR |   PCS-CQR κ=168 |   PCS-CQR +kNN+stage |   HSC-CQR |   CQR |   Self-CQR |   QShrink-CQR (MACD) |   ACI-CQR |   TQA-B-CQR |   GHCP-CQR |
|:----------|--------------:|----------:|----------------:|---------------------:|----------:|------:|-----------:|---------------------:|----------:|------------:|-----------:|
| Bear      |            72 |     0.009 |           0.009 |                0.009 |     0.009 | 0.079 |      0.074 |                0.009 |     0.037 |       0.083 |      0.079 |
| Bull      |           109 |     0.015 |           0.012 |                0.015 |     0.012 | 0.092 |      0.098 |                0.006 |     0.043 |       0.08  |      0.092 |
| Eagle     |            60 |     0.006 |           0.006 |                0.006 |     0.006 | 0.072 |      0.044 |                0.006 |     0.006 |       0.1   |      0.056 |
| Fox       |           119 |     0.02  |           0.017 |                0.02  |     0.025 | 0.112 |      0.078 |                0.011 |     0.05  |       0.12  |      0.112 |
| Hog       |           134 |     0.022 |           0.022 |                0.027 |     0.032 | 0.117 |      0.087 |                0.012 |     0.052 |       0.107 |      0.104 |
| Moose     |             6 |     0     |           0     |                0     |     0     | 0     |      0.167 |                0     |     0     |       0     |      0     |
| Peacock   |            36 |     0.009 |           0.009 |                0.009 |     0.019 | 0.074 |      0.074 |                0.009 |     0.019 |       0.102 |      0.074 |
| Rat       |           248 |     0.04  |           0.042 |                0.042 |     0.082 | 0.497 |      0.047 |                0.044 |     0.106 |       0.488 |      0.476 |
| Robin     |            22 |     0     |           0     |                0     |     0     | 0.152 |      0.091 |                0     |     0.045 |       0.136 |      0.136 |
| Wolf      |            36 |     0.046 |           0.046 |                0.065 |     0.213 | 0.852 |      0.083 |                0.028 |     0.454 |       0.602 |      0.843 |

### T_main_BDG2.md

**Main results, BDG2, 90 % nominal, mean ± s.d. over seeds**

| Method                  | Coverage      | MACD          | Under-covered share   | P10 coverage   | Under-covered, week 1   | Rel. width (median)   | Rel. IS (median)   | Reserve cost    |
|:------------------------|:--------------|:--------------|:----------------------|:---------------|:------------------------|:----------------------|:-------------------|:----------------|
| PCS-CQR                 | 0.895 ± 0.001 | 0.015 ± 0.001 | 0.014 ± 0.008         | 0.871 ± 0.001  | 0.194 ± 0.021           | 0.391 ± 0.014         | 0.562 ± 0.025      | 0.0209 ± 0.0012 |
| PCS-CQR κ=168           | 0.895 ± 0.002 | 0.015 ± 0.001 | 0.015 ± 0.009         | 0.871 ± 0.001  | 0.197 ± 0.022           | 0.390 ± 0.014         | 0.562 ± 0.025      | 0.0208 ± 0.0012 |
| PCS-CQR (IS-tuned)      | 0.894 ± 0.002 | 0.017 ± 0.001 | 0.029 ± 0.014         | 0.868 ± 0.002  | 0.214 ± 0.020           | 0.386 ± 0.012         | 0.561 ± 0.025      | 0.0206 ± 0.0010 |
| PCS-CQR site-grouped    | 0.895 ± 0.001 | 0.015 ± 0.001 | 0.015 ± 0.006         | 0.871 ± 0.002  | 0.191 ± 0.028           | 0.391 ± 0.014         | 0.562 ± 0.025      | 0.0209 ± 0.0012 |
| PCS-CQR +stage          | 0.895 ± 0.002 | 0.015 ± 0.001 | 0.014 ± 0.008         | 0.870 ± 0.002  | 0.193 ± 0.030           | 0.391 ± 0.013         | 0.563 ± 0.024      | 0.0209 ± 0.0012 |
| PCS-CQR +kNN            | 0.894 ± 0.001 | 0.015 ± 0.001 | 0.018 ± 0.010         | 0.870 ± 0.001  | 0.203 ± 0.016           | 0.390 ± 0.014         | 0.562 ± 0.025      | 0.0208 ± 0.0012 |
| PCS-CQR +kNN+stage      | 0.893 ± 0.001 | 0.016 ± 0.001 | 0.018 ± 0.010         | 0.870 ± 0.001  | 0.217 ± 0.026           | 0.390 ± 0.014         | 0.563 ± 0.024      | 0.0208 ± 0.0012 |
| PCS-CQR -shrink         | 0.891 ± 0.004 | 0.039 ± 0.002 | 0.185 ± 0.019         | 0.829 ± 0.003  | 0.242 ± 0.021           | 0.382 ± 0.013         | 0.560 ± 0.023      | 0.0208 ± 0.0010 |
| HSC-CQR                 | 0.892 ± 0.003 | 0.018 ± 0.001 | 0.034 ± 0.010         | 0.865 ± 0.002  | 0.252 ± 0.036           | 0.384 ± 0.011         | 0.561 ± 0.025      | 0.0206 ± 0.0010 |
| CQR                     | 0.891 ± 0.004 | 0.039 ± 0.002 | 0.182 ± 0.017         | 0.829 ± 0.003  | 0.242 ± 0.028           | 0.382 ± 0.013         | 0.560 ± 0.023      | 0.0208 ± 0.0010 |
| Self-CQR                | 0.889 ± 0.002 | 0.021 ± 0.001 | 0.076 ± 0.022         | 0.856 ± 0.005  | 0.338 ± 0.009           | 0.396 ± 0.015         | 0.571 ± 0.022      | 0.0221 ± 0.0023 |
| ACI-CQR                 | 0.894 ± 0.002 | 0.025 ± 0.004 | 0.087 ± 0.035         | 0.853 ± 0.009  | 0.238 ± 0.029           | 0.384 ± 0.013         | 0.560 ± 0.024      | 0.0208 ± 0.0010 |
| ACI-CQR (MACD)          | 0.895 ± 0.002 | 0.020 ± 0.001 | 0.042 ± 0.010         | 0.862 ± 0.001  | 0.237 ± 0.027           | 0.387 ± 0.012         | 0.560 ± 0.024      | 0.0208 ± 0.0011 |
| ACI-CQR (coverage only) | 0.900 ± 0.000 | 0.004 ± 0.000 | 0.000 ± 0.000         | 0.894 ± 0.001  | 0.089 ± 0.014           | 0.949 ± 0.179         | 1.110 ± 0.184      | 0.0445 ± 0.0065 |
| TQA-B-CQR               | 0.894 ± 0.003 | 0.039 ± 0.001 | 0.173 ± 0.016         | 0.834 ± 0.003  | 0.232 ± 0.017           | 0.382 ± 0.011         | 0.562 ± 0.024      | 0.0209 ± 0.0009 |
| GHCP-CQR                | 0.893 ± 0.004 | 0.038 ± 0.002 | 0.172 ± 0.011         | 0.831 ± 0.004  | 0.225 ± 0.021           | 0.385 ± 0.013         | 0.560 ± 0.023      | 0.0208 ± 0.0010 |
| QShrink-CQR             | 0.897 ± 0.002 | 0.021 ± 0.005 | 0.043 ± 0.028         | 0.865 ± 0.006  | 0.207 ± 0.036           | 0.387 ± 0.012         | 0.561 ± 0.024      | 0.0208 ± 0.0011 |
| QShrink-CQR (MACD)      | 0.896 ± 0.001 | 0.015 ± 0.001 | 0.013 ± 0.008         | 0.873 ± 0.002  | 0.177 ± 0.025           | 0.392 ± 0.013         | 0.562 ± 0.024      | 0.0211 ± 0.0014 |
| QShrink-CQR λ=168       | 0.897 ± 0.002 | 0.015 ± 0.001 | 0.012 ± 0.007         | 0.873 ± 0.002  | 0.181 ± 0.022           | 0.392 ± 0.014         | 0.562 ± 0.024      | 0.0211 ± 0.0014 |
| QR-LGBM                 | 0.857 ± 0.010 | 0.052 ± 0.008 | 0.416 ± 0.110         | 0.796 ± 0.009  | 0.372 ± 0.035           | 0.355 ± 0.008         | 0.570 ± 0.030      | 0.0209 ± 0.0010 |
| MLP-QR                  | 0.882 ± 0.007 | 0.038 ± 0.002 | 0.232 ± 0.047         | 0.827 ± 0.007  | 0.251 ± 0.052           | 0.374 ± 0.008         | 0.562 ± 0.029      | 0.0208 ± 0.0010 |
| MLP-Gauss               | 0.927 ± 0.009 | 0.042 ± 0.004 | 0.047 ± 0.021         | 0.871 ± 0.010  | 0.099 ± 0.023           | 0.455 ± 0.034         | 0.609 ± 0.037      | 0.0264 ± 0.0063 |
| CQR (MLP)               | 0.894 ± 0.004 | 0.036 ± 0.001 | 0.157 ± 0.023         | 0.840 ± 0.004  | 0.215 ± 0.028           | 0.385 ± 0.013         | 0.561 ± 0.031      | 0.0208 ± 0.0010 |
| PCS-CQR (MLP)           | 0.895 ± 0.003 | 0.015 ± 0.001 | 0.018 ± 0.017         | 0.871 ± 0.004  | 0.161 ± 0.028           | 0.395 ± 0.017         | 0.566 ± 0.027      | 0.0208 ± 0.0013 |
| PCS                     | 0.905 ± 0.001 | 0.026 ± 0.002 | 0.060 ± 0.010         | 0.860 ± 0.002  | 0.187 ± 0.028           | 0.437 ± 0.022         | 0.646 ± 0.025      | 0.0243 ± 0.0023 |
| PCS (IS-tuned)          | 0.910 ± 0.001 | 0.029 ± 0.002 | 0.055 ± 0.010         | 0.865 ± 0.002  | 0.204 ± 0.026           | 0.436 ± 0.020         | 0.640 ± 0.026      | 0.0236 ± 0.0018 |
| HSC                     | 0.899 ± 0.003 | 0.029 ± 0.002 | 0.096 ± 0.017         | 0.852 ± 0.003  | 0.313 ± 0.058           | 0.411 ± 0.016         | 0.635 ± 0.028      | 0.0231 ± 0.0014 |
| HSC -stage              | 0.898 ± 0.003 | 0.029 ± 0.002 | 0.101 ± 0.020         | 0.851 ± 0.005  | 0.383 ± 0.054           | 0.410 ± 0.015         | 0.640 ± 0.026      | 0.0232 ± 0.0014 |
| HSC -kNN                | 0.911 ± 0.002 | 0.029 ± 0.002 | 0.050 ± 0.009         | 0.867 ± 0.003  | 0.143 ± 0.026           | 0.441 ± 0.020         | 0.638 ± 0.027      | 0.0236 ± 0.0018 |
| HSC -shrink             | 0.839 ± 0.008 | 0.094 ± 0.005 | 0.467 ± 0.030         | 0.690 ± 0.015  | 0.465 ± 0.068           | 0.360 ± 0.010         | 0.660 ± 0.031      | 0.0255 ± 0.0010 |
| ACI                     | 0.914 ± 0.003 | 0.044 ± 0.001 | 0.128 ± 0.010         | 0.845 ± 0.002  | 0.258 ± 0.039           | 0.433 ± 0.020         | 0.627 ± 0.029      | 0.0249 ± 0.0013 |
| Self-CP                 | 0.904 ± 0.003 | 0.026 ± 0.001 | 0.061 ± 0.014         | 0.861 ± 0.003  | 0.162 ± 0.031           | 0.440 ± 0.023         | 0.646 ± 0.028      | 0.0245 ± 0.0026 |
| SCP-stage               | 0.880 ± 0.009 | 0.094 ± 0.005 | 0.293 ± 0.029         | 0.701 ± 0.018  | 0.270 ± 0.032           | 0.458 ± 0.025         | 0.631 ± 0.026      | 0.0269 ± 0.0010 |
| SCP                     | 0.881 ± 0.008 | 0.094 ± 0.005 | 0.292 ± 0.033         | 0.701 ± 0.020  | 0.342 ± 0.032           | 0.457 ± 0.024         | 0.637 ± 0.025      | 0.0269 ± 0.0010 |
| Mondrian-usage          | 0.882 ± 0.011 | 0.093 ± 0.004 | 0.286 ± 0.042         | 0.703 ± 0.011  | 0.265 ± 0.047           | 0.431 ± 0.040         | 0.662 ± 0.034      | 0.0268 ± 0.0009 |
| Naive+SCP               | 0.882 ± 0.011 | 0.092 ± 0.006 | 0.303 ± 0.022         | 0.708 ± 0.031  | 0.293 ± 0.034           | 0.688 ± 0.053         | 0.973 ± 0.047      | 0.0383 ± 0.0021 |
| Raw-SCP                 | 0.906 ± 0.024 | 0.119 ± 0.014 | 0.189 ± 0.047         | 0.696 ± 0.114  | 0.218 ± 0.058           | 0.761 ± 0.077         | 1.127 ± 0.043      | 0.0660 ± 0.0074 |

### T_main_UCI.md

**Main results, UCI, 90 % nominal, mean ± s.d. over seeds**

| Method                  | Coverage      | MACD          | Under-covered share   | P10 coverage   | Under-covered, week 1   | Rel. width (median)   | Rel. IS (median)   | Reserve cost    |
|:------------------------|:--------------|:--------------|:----------------------|:---------------|:------------------------|:----------------------|:-------------------|:----------------|
| PCS-CQR                 | 0.900 ± 0.002 | 0.013 ± 0.002 | 0.004 ± 0.009         | 0.879 ± 0.004  | 0.103 ± 0.026           | 0.266 ± 0.013         | 0.367 ± 0.014      | 0.0162 ± 0.0021 |
| PCS-CQR κ=168           | 0.901 ± 0.003 | 0.013 ± 0.002 | 0.008 ± 0.014         | 0.881 ± 0.006  | 0.120 ± 0.022           | 0.266 ± 0.013         | 0.365 ± 0.015      | 0.0161 ± 0.0021 |
| PCS-CQR (IS-tuned)      | 0.901 ± 0.004 | 0.014 ± 0.003 | 0.011 ± 0.015         | 0.879 ± 0.009  | 0.135 ± 0.033           | 0.267 ± 0.013         | 0.365 ± 0.015      | 0.0161 ± 0.0021 |
| PCS-CQR +stage          | 0.900 ± 0.002 | 0.013 ± 0.002 | 0.004 ± 0.009         | 0.880 ± 0.004  | 0.086 ± 0.024           | 0.267 ± 0.013         | 0.366 ± 0.015      | 0.0162 ± 0.0021 |
| PCS-CQR +kNN            | 0.899 ± 0.002 | 0.013 ± 0.002 | 0.006 ± 0.009         | 0.879 ± 0.003  | 0.112 ± 0.028           | 0.265 ± 0.013         | 0.366 ± 0.014      | 0.0162 ± 0.0021 |
| PCS-CQR +kNN+stage      | 0.899 ± 0.002 | 0.013 ± 0.002 | 0.006 ± 0.009         | 0.879 ± 0.003  | 0.116 ± 0.044           | 0.266 ± 0.011         | 0.367 ± 0.015      | 0.0161 ± 0.0020 |
| PCS-CQR -shrink         | 0.899 ± 0.010 | 0.033 ± 0.005 | 0.093 ± 0.048         | 0.855 ± 0.015  | 0.166 ± 0.036           | 0.273 ± 0.018         | 0.364 ± 0.014      | 0.0162 ± 0.0020 |
| HSC-CQR                 | 0.898 ± 0.004 | 0.014 ± 0.003 | 0.013 ± 0.017         | 0.876 ± 0.008  | 0.164 ± 0.026           | 0.265 ± 0.012         | 0.365 ± 0.015      | 0.0161 ± 0.0020 |
| CQR                     | 0.899 ± 0.010 | 0.033 ± 0.005 | 0.091 ± 0.049         | 0.855 ± 0.015  | 0.156 ± 0.027           | 0.273 ± 0.017         | 0.364 ± 0.014      | 0.0162 ± 0.0020 |
| Self-CQR                | 0.895 ± 0.002 | 0.016 ± 0.002 | 0.019 ± 0.019         | 0.870 ± 0.004  | 0.227 ± 0.038           | 0.264 ± 0.011         | 0.372 ± 0.014      | 0.0163 ± 0.0022 |
| ACI-CQR                 | 0.903 ± 0.005 | 0.019 ± 0.006 | 0.027 ± 0.018         | 0.873 ± 0.007  | 0.149 ± 0.024           | 0.270 ± 0.015         | 0.364 ± 0.015      | 0.0162 ± 0.0021 |
| ACI-CQR (MACD)          | 0.903 ± 0.004 | 0.018 ± 0.007 | 0.025 ± 0.019         | 0.876 ± 0.008  | 0.149 ± 0.024           | 0.271 ± 0.013         | 0.364 ± 0.015      | 0.0162 ± 0.0021 |
| ACI-CQR (coverage only) | 0.901 ± 0.001 | 0.004 ± 0.000 | 0.000 ± 0.000         | 0.895 ± 0.001  | 0.046 ± 0.021           | 0.330 ± 0.024         | 0.430 ± 0.023      | 0.0274 ± 0.0085 |
| TQA-B-CQR               | 0.900 ± 0.006 | 0.032 ± 0.006 | 0.093 ± 0.056         | 0.857 ± 0.015  | 0.147 ± 0.029           | 0.271 ± 0.013         | 0.366 ± 0.012      | 0.0162 ± 0.0020 |
| GHCP-CQR                | 0.906 ± 0.010 | 0.034 ± 0.006 | 0.076 ± 0.033         | 0.864 ± 0.015  | 0.135 ± 0.030           | 0.279 ± 0.018         | 0.366 ± 0.013      | 0.0162 ± 0.0020 |
| QShrink-CQR             | 0.902 ± 0.004 | 0.016 ± 0.004 | 0.019 ± 0.023         | 0.878 ± 0.012  | 0.139 ± 0.026           | 0.266 ± 0.012         | 0.364 ± 0.016      | 0.0161 ± 0.0021 |
| QShrink-CQR (MACD)      | 0.901 ± 0.002 | 0.013 ± 0.002 | 0.002 ± 0.005         | 0.882 ± 0.004  | 0.093 ± 0.016           | 0.265 ± 0.011         | 0.366 ± 0.015      | 0.0161 ± 0.0021 |
| QShrink-CQR λ=168       | 0.902 ± 0.003 | 0.013 ± 0.001 | 0.004 ± 0.009         | 0.883 ± 0.006  | 0.095 ± 0.027           | 0.265 ± 0.011         | 0.365 ± 0.015      | 0.0161 ± 0.0021 |
| QR-LGBM                 | 0.877 ± 0.008 | 0.036 ± 0.006 | 0.187 ± 0.073         | 0.835 ± 0.017  | 0.229 ± 0.023           | 0.256 ± 0.012         | 0.367 ± 0.016      | 0.0163 ± 0.0020 |
| MLP-QR                  | 0.892 ± 0.016 | 0.036 ± 0.007 | 0.135 ± 0.116         | 0.845 ± 0.024  | 0.177 ± 0.051           | 0.265 ± 0.027         | 0.373 ± 0.015      | 0.0156 ± 0.0015 |
| MLP-Gauss               | 0.925 ± 0.006 | 0.037 ± 0.001 | 0.038 ± 0.019         | 0.882 ± 0.011  | 0.091 ± 0.064           | 0.298 ± 0.013         | 0.391 ± 0.013      | 0.0161 ± 0.0014 |
| CQR (MLP)               | 0.901 ± 0.007 | 0.033 ± 0.006 | 0.082 ± 0.028         | 0.858 ± 0.014  | 0.145 ± 0.036           | 0.272 ± 0.019         | 0.373 ± 0.018      | 0.0156 ± 0.0015 |
| PCS-CQR (MLP)           | 0.903 ± 0.006 | 0.015 ± 0.002 | 0.008 ± 0.014         | 0.881 ± 0.004  | 0.082 ± 0.050           | 0.272 ± 0.017         | 0.374 ± 0.016      | 0.0156 ± 0.0015 |
| PCS                     | 0.908 ± 0.003 | 0.021 ± 0.001 | 0.023 ± 0.017         | 0.878 ± 0.003  | 0.099 ± 0.019           | 0.295 ± 0.013         | 0.419 ± 0.011      | 0.0179 ± 0.0021 |
| PCS (IS-tuned)          | 0.913 ± 0.004 | 0.024 ± 0.002 | 0.023 ± 0.017         | 0.879 ± 0.007  | 0.120 ± 0.066           | 0.301 ± 0.013         | 0.419 ± 0.013      | 0.0179 ± 0.0020 |
| HSC                     | 0.905 ± 0.004 | 0.021 ± 0.001 | 0.038 ± 0.022         | 0.871 ± 0.005  | 0.179 ± 0.045           | 0.288 ± 0.014         | 0.416 ± 0.016      | 0.0177 ± 0.0019 |
| HSC -stage              | 0.904 ± 0.005 | 0.021 ± 0.001 | 0.038 ± 0.027         | 0.871 ± 0.006  | 0.225 ± 0.067           | 0.286 ± 0.014         | 0.417 ± 0.016      | 0.0178 ± 0.0020 |
| HSC -kNN                | 0.914 ± 0.005 | 0.025 ± 0.003 | 0.023 ± 0.017         | 0.879 ± 0.007  | 0.097 ± 0.040           | 0.306 ± 0.015         | 0.420 ± 0.013      | 0.0179 ± 0.0020 |
| HSC -shrink             | 0.857 ± 0.007 | 0.078 ± 0.004 | 0.318 ± 0.042         | 0.719 ± 0.013  | 0.364 ± 0.059           | 0.254 ± 0.011         | 0.438 ± 0.034      | 0.0210 ± 0.0028 |
| ACI                     | 0.920 ± 0.011 | 0.050 ± 0.019 | 0.095 ± 0.054         | 0.844 ± 0.035  | 0.168 ± 0.022           | 0.335 ± 0.032         | 0.423 ± 0.014      | 0.0193 ± 0.0021 |
| Self-CP                 | 0.908 ± 0.003 | 0.021 ± 0.001 | 0.023 ± 0.017         | 0.877 ± 0.002  | 0.076 ± 0.016           | 0.297 ± 0.014         | 0.420 ± 0.012      | 0.0180 ± 0.0021 |
| SCP-stage               | 0.903 ± 0.016 | 0.089 ± 0.006 | 0.204 ± 0.044         | 0.771 ± 0.028  | 0.181 ± 0.019           | 0.377 ± 0.033         | 0.441 ± 0.018      | 0.0217 ± 0.0028 |
| SCP                     | 0.904 ± 0.015 | 0.089 ± 0.006 | 0.208 ± 0.043         | 0.773 ± 0.029  | 0.238 ± 0.039           | 0.376 ± 0.032         | 0.443 ± 0.017      | 0.0217 ± 0.0028 |
| Naive+SCP               | 0.905 ± 0.009 | 0.076 ± 0.004 | 0.215 ± 0.036         | 0.762 ± 0.017  | 0.215 ± 0.030           | 0.474 ± 0.028         | 0.581 ± 0.018      | 0.0275 ± 0.0028 |
| Raw-SCP                 | 0.908 ± 0.048 | 0.130 ± 0.028 | 0.177 ± 0.100         | 0.681 ± 0.218  | 0.185 ± 0.104           | 0.967 ± 0.323         | 1.128 ± 0.210      | 0.0869 ± 0.0853 |

### T_pools.md

**Small calibration pools (BDG2; mean over 3 seeds x 5 resamples)**

| perturb   | method             |   macd |   under_rate |   under_w1 |   rel_IS |   mean_cov |   under_rate_sd |
|:----------|:-------------------|-------:|-------------:|-----------:|---------:|-----------:|----------------:|
| n_cal=5   | ACI-CQR            |  0.018 |        0.032 |      0.216 |    0.559 |      0.899 |           0.021 |
| n_cal=5   | CQR                |  0.038 |        0.166 |      0.236 |    0.557 |      0.895 |           0.028 |
| n_cal=5   | GHCP-CQR           |  0.068 |        0.001 |      0     |  411.482 |      0.968 |           0.002 |
| n_cal=5   | PCS-CQR            |  0.016 |        0.027 |      0.182 |    0.556 |      0.895 |           0.009 |
| n_cal=5   | PCS-CQR (IS-tuned) |  0.021 |        0.066 |      0.202 |    0.554 |      0.895 |           0.02  |
| n_cal=5   | PCS-CQR κ=168      |  0.015 |        0.017 |      0.186 |    0.555 |      0.896 |           0.006 |
| n_cal=5   | QShrink-CQR (MACD) |  0.017 |        0.026 |      0.191 |    0.559 |      0.897 |           0.01  |
| n_cal=5   | Self-CQR           |  0.021 |        0.081 |      0.348 |    0.567 |      0.889 |           0.015 |
| n_cal=5   | TQA-B-CQR          |  0.039 |        0.193 |      0.251 |    0.557 |      0.891 |           0.042 |
| n_cal=10  | ACI-CQR            |  0.019 |        0.045 |      0.261 |    0.554 |      0.895 |           0.035 |
| n_cal=10  | CQR                |  0.038 |        0.193 |      0.28  |    0.553 |      0.888 |           0     |
| n_cal=10  | GHCP-CQR           |  0.045 |        0.032 |      0.025 |    0.596 |      0.935 |           0.006 |
| n_cal=10  | PCS-CQR            |  0.017 |        0.03  |      0.184 |    0.556 |      0.894 |           0.015 |
| n_cal=10  | PCS-CQR (IS-tuned) |  0.019 |        0.052 |      0.225 |    0.553 |      0.893 |           0.004 |
| n_cal=10  | PCS-CQR κ=168      |  0.015 |        0.019 |      0.2   |    0.555 |      0.894 |           0.002 |
| n_cal=10  | QShrink-CQR (MACD) |  0.017 |        0.025 |      0.211 |    0.557 |      0.895 |           0.008 |
| n_cal=10  | Self-CQR           |  0.021 |        0.079 |      0.345 |    0.567 |      0.889 |           0.017 |
| n_cal=10  | TQA-B-CQR          |  0.04  |        0.212 |      0.289 |    0.553 |      0.886 |           0.004 |
| n_cal=20  | ACI-CQR            |  0.021 |        0.061 |      0.237 |    0.553 |      0.895 |           0.037 |
| n_cal=20  | CQR                |  0.038 |        0.173 |      0.249 |    0.554 |      0.892 |           0.028 |
| n_cal=20  | GHCP-CQR           |  0.039 |        0.091 |      0.127 |    0.553 |      0.914 |           0.018 |
| n_cal=20  | PCS-CQR            |  0.016 |        0.026 |      0.186 |    0.555 |      0.894 |           0.012 |
| n_cal=20  | PCS-CQR (IS-tuned) |  0.019 |        0.05  |      0.214 |    0.553 |      0.894 |           0.016 |
| n_cal=20  | PCS-CQR κ=168      |  0.015 |        0.018 |      0.193 |    0.555 |      0.895 |           0.001 |
| n_cal=20  | QShrink-CQR (MACD) |  0.016 |        0.022 |      0.193 |    0.555 |      0.896 |           0.016 |
| n_cal=20  | Self-CQR           |  0.021 |        0.079 |      0.337 |    0.567 |      0.89  |           0.017 |
| n_cal=20  | TQA-B-CQR          |  0.039 |        0.186 |      0.252 |    0.554 |      0.892 |           0.032 |
| n_cal=40  | ACI-CQR            |  0.021 |        0.051 |      0.255 |    0.552 |      0.895 |           0.015 |
| n_cal=40  | CQR                |  0.038 |        0.19  |      0.267 |    0.553 |      0.89  |           0.031 |
| n_cal=40  | GHCP-CQR           |  0.038 |        0.139 |      0.194 |    0.551 |      0.9   |           0.02  |
| n_cal=40  | PCS-CQR            |  0.016 |        0.024 |      0.198 |    0.555 |      0.894 |           0.011 |
| n_cal=40  | PCS-CQR (IS-tuned) |  0.019 |        0.045 |      0.225 |    0.553 |      0.893 |           0.019 |
| n_cal=40  | PCS-CQR κ=168      |  0.015 |        0.019 |      0.202 |    0.555 |      0.894 |           0.001 |
| n_cal=40  | QShrink-CQR (MACD) |  0.016 |        0.02  |      0.202 |    0.555 |      0.896 |           0.006 |
| n_cal=40  | Self-CQR           |  0.021 |        0.08  |      0.339 |    0.567 |      0.89  |           0.017 |
| n_cal=40  | TQA-B-CQR          |  0.039 |        0.189 |      0.261 |    0.554 |      0.891 |           0.029 |

### T_robustness.md

**Robustness (BDG2, mean over 3 seeds; s.d. over seeds)**

| perturb             | method             |   mean_cov |   macd |   under_rate |   under_w1 |   under_w58 |   rel_IS |   rel_width |   book_fail |   macd_sd |   under_rate_sd |
|:--------------------|:-------------------|-----------:|-------:|-------------:|-----------:|------------:|---------:|------------:|------------:|----------:|----------------:|
| calpool10           | ACI-CQR            |      0.888 |  0.026 |        0.109 |      0.366 |       0.124 |    0.555 |       0.377 |       0.055 |     0.003 |           0.01  |
| calpool10           | ACI-CQR (MACD)     |      0.889 |  0.024 |        0.088 |      0.361 |       0.097 |    0.553 |       0.379 |       0.049 |     0.005 |           0.029 |
| calpool10           | CQR                |      0.881 |  0.04  |        0.229 |      0.381 |       0.249 |    0.554 |       0.371 |       0.1   |     0.003 |           0.051 |
| calpool10           | GHCP-CQR           |      0.909 |  0.037 |        0.104 |      0.116 |       0.177 |    0.554 |       0.406 |       0.05  |     0.001 |           0.03  |
| calpool10           | HSC-CQR            |      0.888 |  0.019 |        0.058 |      0.348 |       0.129 |    0.556 |       0.384 |       0.042 |     0.005 |           0.066 |
| calpool10           | PCS-CQR            |      0.89  |  0.019 |        0.047 |      0.212 |       0.137 |    0.555 |       0.387 |       0.04  |     0.004 |           0.042 |
| calpool10           | PCS-CQR κ=168      |      0.892 |  0.016 |        0.022 |      0.221 |       0.113 |    0.555 |       0.387 |       0.026 |     0.001 |           0.011 |
| calpool10           | QR-LGBM            |      0.857 |  0.051 |        0.401 |      0.372 |       0.423 |    0.56  |       0.354 |       0.153 |     0.007 |           0.116 |
| calpool10           | QShrink-CQR        |      0.891 |  0.018 |        0.042 |      0.296 |       0.117 |    0.555 |       0.386 |       0.03  |     0.005 |           0.042 |
| calpool10           | QShrink-CQR (MACD) |      0.891 |  0.019 |        0.043 |      0.3   |       0.124 |    0.555 |       0.387 |       0.028 |     0.004 |           0.042 |
| calpool10           | SCP-stage          |      0.843 |  0.112 |        0.408 |      0.387 |       0.39  |    0.629 |       0.379 |       0.298 |     0.012 |           0.048 |
| calpool10           | Self-CP            |      0.905 |  0.027 |        0.061 |      0.181 |       0.154 |    0.647 |       0.445 |       0.025 |     0.001 |           0.011 |
| calpool10           | Self-CQR           |      0.889 |  0.021 |        0.079 |      0.361 |       0.128 |    0.566 |       0.397 |       0.026 |     0.001 |           0.018 |
| calpool10           | TQA-B-CQR          |      0.88  |  0.041 |        0.256 |      0.373 |       0.26  |    0.555 |       0.368 |       0.107 |     0.004 |           0.039 |
| calpool25           | ACI-CQR            |      0.894 |  0.02  |        0.047 |      0.208 |       0.082 |    0.551 |       0.385 |       0.036 |     0.001 |           0.007 |
| calpool25           | ACI-CQR (MACD)     |      0.894 |  0.02  |        0.047 |      0.208 |       0.082 |    0.551 |       0.385 |       0.036 |     0.001 |           0.007 |
| calpool25           | CQR                |      0.891 |  0.038 |        0.187 |      0.212 |       0.224 |    0.553 |       0.381 |       0.076 |     0.001 |           0.04  |
| calpool25           | GHCP-CQR           |      0.901 |  0.038 |        0.133 |      0.192 |       0.167 |    0.551 |       0.392 |       0.062 |     0.001 |           0.019 |
| calpool25           | HSC-CQR            |      0.894 |  0.017 |        0.03  |      0.211 |       0.104 |    0.552 |       0.384 |       0.032 |     0.001 |           0.006 |
| calpool25           | PCS-CQR            |      0.895 |  0.015 |        0.017 |      0.192 |       0.107 |    0.555 |       0.392 |       0.026 |     0.001 |           0.002 |
| calpool25           | PCS-CQR κ=168      |      0.895 |  0.015 |        0.017 |      0.195 |       0.105 |    0.555 |       0.391 |       0.025 |     0.001 |           0.002 |
| calpool25           | QR-LGBM            |      0.857 |  0.051 |        0.401 |      0.372 |       0.423 |    0.56  |       0.354 |       0.153 |     0.007 |           0.116 |
| calpool25           | QShrink-CQR        |      0.898 |  0.019 |        0.025 |      0.19  |       0.091 |    0.553 |       0.389 |       0.033 |     0.002 |           0.014 |
| calpool25           | QShrink-CQR (MACD) |      0.897 |  0.015 |        0.012 |      0.162 |       0.107 |    0.555 |       0.395 |       0.02  |     0     |           0     |
| calpool25           | SCP-stage          |      0.883 |  0.094 |        0.285 |      0.274 |       0.308 |    0.629 |       0.464 |       0.192 |     0.007 |           0.024 |
| calpool25           | Self-CP            |      0.906 |  0.027 |        0.058 |      0.169 |       0.154 |    0.644 |       0.448 |       0.025 |     0     |           0.009 |
| calpool25           | Self-CQR           |      0.89  |  0.021 |        0.079 |      0.337 |       0.128 |    0.567 |       0.398 |       0.025 |     0.001 |           0.018 |
| calpool25           | TQA-B-CQR          |      0.892 |  0.039 |        0.188 |      0.206 |       0.225 |    0.554 |       0.381 |       0.08  |     0.001 |           0.035 |
| calpool50           | ACI-CQR            |      0.894 |  0.02  |        0.053 |      0.22  |       0.071 |    0.551 |       0.384 |       0.037 |     0     |           0.006 |
| calpool50           | ACI-CQR (MACD)     |      0.894 |  0.02  |        0.053 |      0.22  |       0.071 |    0.551 |       0.384 |       0.037 |     0     |           0.006 |
| calpool50           | CQR                |      0.89  |  0.038 |        0.174 |      0.228 |       0.203 |    0.552 |       0.379 |       0.079 |     0.001 |           0.016 |
| calpool50           | GHCP-CQR           |      0.895 |  0.037 |        0.159 |      0.216 |       0.195 |    0.552 |       0.384 |       0.07  |     0     |           0.006 |
| calpool50           | HSC-CQR            |      0.893 |  0.019 |        0.042 |      0.219 |       0.108 |    0.552 |       0.383 |       0.038 |     0.002 |           0.025 |
| calpool50           | PCS-CQR            |      0.895 |  0.015 |        0.017 |      0.182 |       0.111 |    0.555 |       0.392 |       0.025 |     0.001 |           0.002 |
| calpool50           | PCS-CQR κ=168      |      0.895 |  0.015 |        0.018 |      0.199 |       0.107 |    0.555 |       0.39  |       0.025 |     0     |           0.002 |
| calpool50           | QR-LGBM            |      0.857 |  0.051 |        0.401 |      0.372 |       0.423 |    0.56  |       0.354 |       0.153 |     0.007 |           0.116 |
| calpool50           | QShrink-CQR        |      0.897 |  0.021 |        0.042 |      0.204 |       0.094 |    0.552 |       0.387 |       0.034 |     0     |           0.016 |
| calpool50           | QShrink-CQR (MACD) |      0.896 |  0.015 |        0.013 |      0.159 |       0.108 |    0.555 |       0.394 |       0.02  |     0     |           0.002 |
| calpool50           | SCP-stage          |      0.877 |  0.096 |        0.302 |      0.287 |       0.302 |    0.623 |       0.448 |       0.204 |     0.004 |           0.026 |
| calpool50           | Self-CP            |      0.906 |  0.027 |        0.059 |      0.17  |       0.154 |    0.646 |       0.448 |       0.025 |     0.001 |           0.01  |
| calpool50           | Self-CQR           |      0.89  |  0.021 |        0.079 |      0.331 |       0.128 |    0.567 |       0.397 |       0.025 |     0.001 |           0.018 |
| calpool50           | TQA-B-CQR          |      0.893 |  0.038 |        0.173 |      0.216 |       0.2   |    0.555 |       0.38  |       0.079 |     0.001 |           0.012 |
| disjoint-cal-period | ACI-CQR            |      0.893 |  0.023 |        0.074 |      0.242 |       0.088 |    0.551 |       0.382 |       0.046 |     0.004 |           0.042 |
| disjoint-cal-period | ACI-CQR (MACD)     |      0.894 |  0.02  |        0.049 |      0.242 |       0.069 |    0.552 |       0.384 |       0.036 |     0     |           0.002 |
| disjoint-cal-period | CQR                |      0.889 |  0.038 |        0.184 |      0.25  |       0.204 |    0.552 |       0.378 |       0.084 |     0.001 |           0.024 |
| disjoint-cal-period | GHCP-CQR           |      0.891 |  0.038 |        0.173 |      0.231 |       0.206 |    0.552 |       0.38  |       0.078 |     0.001 |           0.016 |
| disjoint-cal-period | HSC-CQR            |      0.891 |  0.018 |        0.04  |      0.265 |       0.104 |    0.553 |       0.382 |       0.034 |     0.001 |           0.007 |
| disjoint-cal-period | PCS-CQR            |      0.894 |  0.015 |        0.018 |      0.2   |       0.108 |    0.555 |       0.391 |       0.026 |     0.001 |           0.002 |
| disjoint-cal-period | PCS-CQR κ=168      |      0.894 |  0.015 |        0.02  |      0.204 |       0.107 |    0.555 |       0.39  |       0.025 |     0.001 |           0     |
| disjoint-cal-period | QR-LGBM            |      0.857 |  0.051 |        0.401 |      0.372 |       0.423 |    0.56  |       0.354 |       0.153 |     0.007 |           0.116 |
| disjoint-cal-period | QShrink-CQR        |      0.896 |  0.021 |        0.045 |      0.216 |       0.094 |    0.553 |       0.385 |       0.037 |     0     |           0.02  |
| disjoint-cal-period | QShrink-CQR (MACD) |      0.896 |  0.015 |        0.016 |      0.183 |       0.104 |    0.555 |       0.393 |       0.02  |     0     |           0.004 |
| disjoint-cal-period | SCP-stage          |      0.875 |  0.097 |        0.311 |      0.285 |       0.307 |    0.621 |       0.443 |       0.202 |     0.003 |           0.016 |
| disjoint-cal-period | Self-CP            |      0.906 |  0.027 |        0.059 |      0.169 |       0.154 |    0.646 |       0.447 |       0.025 |     0.001 |           0.01  |
| disjoint-cal-period | Self-CQR           |      0.89  |  0.021 |        0.079 |      0.335 |       0.128 |    0.566 |       0.397 |       0.025 |     0.001 |           0.018 |
| disjoint-cal-period | TQA-B-CQR          |      0.892 |  0.039 |        0.181 |      0.227 |       0.198 |    0.555 |       0.38  |       0.079 |     0.001 |           0.016 |
| missing20           | ACI-CQR            |      0.896 |  0.026 |        0.097 |      0.266 |       0.103 |    0.577 |       0.416 |       0.046 |     0.005 |           0.059 |
| missing20           | ACI-CQR (MACD)     |      0.897 |  0.024 |        0.067 |      0.267 |       0.082 |    0.577 |       0.417 |       0.038 |     0.001 |           0.008 |
| missing20           | CQR                |      0.894 |  0.039 |        0.178 |      0.273 |       0.178 |    0.579 |       0.412 |       0.07  |     0.002 |           0.018 |
| missing20           | GHCP-CQR           |      0.896 |  0.039 |        0.169 |      0.262 |       0.175 |    0.579 |       0.415 |       0.065 |     0.002 |           0.02  |
| missing20           | HSC-CQR            |      0.895 |  0.019 |        0.037 |      0.289 |       0.095 |    0.578 |       0.413 |       0.03  |     0     |           0.014 |
| missing20           | PCS-CQR            |      0.898 |  0.016 |        0.016 |      0.22  |       0.083 |    0.58  |       0.418 |       0.018 |     0     |           0.004 |
| missing20           | PCS-CQR κ=168      |      0.898 |  0.016 |        0.016 |      0.228 |       0.083 |    0.58  |       0.419 |       0.02  |     0.001 |           0.004 |
| missing20           | QR-LGBM            |      0.866 |  0.046 |        0.333 |      0.397 |       0.335 |    0.583 |       0.388 |       0.121 |     0.006 |           0.083 |
| missing20           | QShrink-CQR        |      0.9   |  0.023 |        0.046 |      0.246 |       0.087 |    0.578 |       0.417 |       0.03  |     0.001 |           0.024 |
| missing20           | QShrink-CQR (MACD) |      0.9   |  0.016 |        0.014 |      0.196 |       0.083 |    0.582 |       0.419 |       0.013 |     0.001 |           0.006 |
| missing20           | SCP-stage          |      0.864 |  0.102 |        0.347 |      0.31  |       0.336 |    0.649 |       0.443 |       0.225 |     0.002 |           0.015 |
| missing20           | Self-CP            |      0.913 |  0.028 |        0.036 |      0.097 |       0.134 |    0.675 |       0.487 |       0.014 |     0.001 |           0.01  |
| missing20           | Self-CQR           |      0.893 |  0.021 |        0.055 |      0.321 |       0.103 |    0.591 |       0.425 |       0.02  |     0.001 |           0.007 |
| missing20           | TQA-B-CQR          |      0.894 |  0.037 |        0.171 |      0.275 |       0.174 |    0.581 |       0.411 |       0.066 |     0.002 |           0.018 |
| missing40           | ACI-CQR            |      0.898 |  0.032 |        0.109 |      0.289 |       0.119 |    0.606 |       0.446 |       0.058 |     0.006 |           0.066 |
| missing40           | ACI-CQR (MACD)     |      0.899 |  0.03  |        0.097 |      0.289 |       0.099 |    0.606 |       0.448 |       0.051 |     0.002 |           0.046 |
| missing40           | CQR                |      0.895 |  0.041 |        0.177 |      0.299 |       0.196 |    0.605 |       0.442 |       0.072 |     0.004 |           0.039 |
| missing40           | GHCP-CQR           |      0.898 |  0.041 |        0.167 |      0.277 |       0.187 |    0.605 |       0.445 |       0.069 |     0.004 |           0.04  |
| missing40           | HSC-CQR            |      0.899 |  0.024 |        0.061 |      0.308 |       0.1   |    0.606 |       0.448 |       0.034 |     0.001 |           0.02  |
| missing40           | PCS-CQR            |      0.903 |  0.021 |        0.026 |      0.253 |       0.1   |    0.608 |       0.453 |       0.028 |     0.001 |           0.014 |
| missing40           | PCS-CQR κ=168      |      0.903 |  0.021 |        0.029 |      0.258 |       0.101 |    0.607 |       0.453 |       0.026 |     0.001 |           0.015 |
| missing40           | QR-LGBM            |      0.87  |  0.047 |        0.312 |      0.422 |       0.318 |    0.61  |       0.418 |       0.112 |     0.007 |           0.061 |
| missing40           | QShrink-CQR        |      0.902 |  0.028 |        0.069 |      0.271 |       0.097 |    0.606 |       0.451 |       0.038 |     0.002 |           0.045 |
| missing40           | QShrink-CQR (MACD) |      0.904 |  0.021 |        0.022 |      0.245 |       0.095 |    0.608 |       0.456 |       0.018 |     0.001 |           0.013 |
| missing40           | SCP-stage          |      0.852 |  0.108 |        0.381 |      0.319 |       0.374 |    0.677 |       0.443 |       0.262 |     0.001 |           0.018 |
| missing40           | Self-CP            |      0.92  |  0.033 |        0.03  |      0.07  |       0.128 |    0.704 |       0.534 |       0.016 |     0.001 |           0.005 |
| missing40           | Self-CQR           |      0.899 |  0.023 |        0.049 |      0.333 |       0.115 |    0.618 |       0.464 |       0.018 |     0.002 |           0.016 |
| missing40           | TQA-B-CQR          |      0.894 |  0.04  |        0.174 |      0.304 |       0.202 |    0.606 |       0.442 |       0.065 |     0.003 |           0.046 |
| noise15             | ACI-CQR            |      0.871 |  0.029 |        0.103 |      0.407 |       0.086 |    0.913 |       0.66  |       0.041 |     0.004 |           0.083 |
| noise15             | ACI-CQR (MACD)     |      0.874 |  0.026 |        0.055 |      0.404 |       0.046 |    0.913 |       0.663 |       0.03  |     0.001 |           0.008 |
| noise15             | CQR                |      0.857 |  0.044 |        0.329 |      0.419 |       0.308 |    0.919 |       0.638 |       0.126 |     0.002 |           0.03  |
| noise15             | GHCP-CQR           |      0.858 |  0.042 |        0.307 |      0.397 |       0.31  |    0.918 |       0.64  |       0.12  |     0.002 |           0.026 |
| noise15             | HSC-CQR            |      0.881 |  0.019 |        0.018 |      0.406 |       0.026 |    0.91  |       0.679 |       0.014 |     0.001 |           0.006 |
| noise15             | PCS-CQR            |      0.891 |  0.011 |        0.004 |      0.249 |       0.02  |    0.909 |       0.697 |       0.004 |     0.001 |           0     |
| noise15             | PCS-CQR κ=168      |      0.889 |  0.012 |        0.007 |      0.274 |       0.02  |    0.908 |       0.694 |       0.005 |     0.001 |           0.005 |
| noise15             | QR-LGBM            |      0.841 |  0.059 |        0.614 |      0.57  |       0.545 |    0.931 |       0.613 |       0.209 |     0.003 |           0.084 |
| noise15             | QShrink-CQR        |      0.88  |  0.021 |        0.026 |      0.356 |       0.045 |    0.91  |       0.675 |       0.014 |     0     |           0.002 |
| noise15             | QShrink-CQR (MACD) |      0.893 |  0.01  |        0.005 |      0.211 |       0.017 |    0.909 |       0.7   |       0.004 |     0.001 |           0.002 |
| noise15             | SCP-stage          |      0.691 |  0.209 |        1     |      0.877 |       0.993 |    1.098 |       0.444 |       0.925 |     0.013 |           0     |
| noise15             | Self-CP            |      0.906 |  0.019 |        0.024 |      0.099 |       0.071 |    0.931 |       0.731 |       0.007 |     0.001 |           0.008 |
| noise15             | Self-CQR           |      0.902 |  0.01  |        0.001 |      0.082 |       0.009 |    0.915 |       0.725 |       0.003 |     0.001 |           0.002 |
| noise15             | TQA-B-CQR          |      0.853 |  0.047 |        0.393 |      0.452 |       0.368 |    0.923 |       0.63  |       0.148 |     0.001 |           0.026 |
| noise15-history     | ACI-CQR            |      0.955 |  0.059 |        0.008 |      0.062 |       0.018 |    0.694 |       0.618 |       0.014 |     0.003 |           0.004 |
| noise15-history     | ACI-CQR (MACD)     |      0.955 |  0.058 |        0.005 |      0.062 |       0.018 |    0.692 |       0.615 |       0.014 |     0.002 |           0.002 |
| noise15-history     | CQR                |      0.957 |  0.063 |        0.011 |      0.067 |       0.028 |    0.706 |       0.637 |       0.017 |     0.002 |           0.005 |
| noise15-history     | GHCP-CQR           |      0.958 |  0.063 |        0.009 |      0.061 |       0.026 |    0.706 |       0.639 |       0.017 |     0.002 |           0.006 |
| noise15-history     | HSC-CQR            |      0.95  |  0.053 |        0.004 |      0.062 |       0.017 |    0.683 |       0.594 |       0.012 |     0.002 |           0     |
| noise15-history     | PCS-CQR            |      0.944 |  0.046 |        0.003 |      0.053 |       0.025 |    0.672 |       0.572 |       0.011 |     0.003 |           0.002 |
| noise15-history     | PCS-CQR κ=168      |      0.946 |  0.048 |        0.003 |      0.054 |       0.024 |    0.674 |       0.577 |       0.011 |     0.002 |           0.002 |
| noise15-history     | QR-LGBM            |      0.952 |  0.059 |        0.02  |      0.084 |       0.041 |    0.692 |       0.613 |       0.02  |     0.002 |           0.014 |
| noise15-history     | QShrink-CQR        |      0.945 |  0.048 |        0.003 |      0.058 |       0.025 |    0.676 |       0.573 |       0.011 |     0.002 |           0.002 |
| noise15-history     | QShrink-CQR (MACD) |      0.928 |  0.032 |        0.005 |      0.043 |       0.038 |    0.663 |       0.537 |       0.014 |     0.002 |           0.002 |
| noise15-history     | SCP-stage          |      0.842 |  0.105 |        0.406 |      0.401 |       0.387 |    0.681 |       0.444 |       0.32  |     0.002 |           0.005 |
| noise15-history     | Self-CP            |      0.915 |  0.027 |        0.034 |      0.095 |       0.096 |    0.71  |       0.521 |       0.012 |     0.001 |           0.012 |
| noise15-history     | Self-CQR           |      0.909 |  0.02  |        0.016 |      0.113 |       0.065 |    0.664 |       0.507 |       0.033 |     0.002 |           0.004 |
| noise15-history     | TQA-B-CQR          |      0.956 |  0.062 |        0.009 |      0.07  |       0.03  |    0.701 |       0.629 |       0.02  |     0.002 |           0.006 |
| noise5              | ACI-CQR            |      0.886 |  0.019 |        0.07  |      0.236 |       0.086 |    0.604 |       0.436 |       0.042 |     0.003 |           0.049 |
| noise5              | ACI-CQR (MACD)     |      0.888 |  0.017 |        0.042 |      0.233 |       0.059 |    0.604 |       0.437 |       0.034 |     0     |           0.002 |
| noise5              | CQR                |      0.878 |  0.03  |        0.188 |      0.241 |       0.196 |    0.605 |       0.426 |       0.072 |     0.001 |           0.028 |
| noise5              | GHCP-CQR           |      0.88  |  0.029 |        0.169 |      0.231 |       0.196 |    0.605 |       0.428 |       0.072 |     0.001 |           0.016 |
| noise5              | HSC-CQR            |      0.888 |  0.015 |        0.024 |      0.248 |       0.066 |    0.605 |       0.438 |       0.028 |     0.001 |           0.01  |
| noise5              | PCS-CQR            |      0.893 |  0.012 |        0.009 |      0.161 |       0.062 |    0.606 |       0.446 |       0.016 |     0     |           0.005 |
| noise5              | PCS-CQR κ=168      |      0.893 |  0.012 |        0.012 |      0.169 |       0.062 |    0.605 |       0.445 |       0.016 |     0     |           0.008 |
| noise5              | QR-LGBM            |      0.852 |  0.049 |        0.43  |      0.347 |       0.464 |    0.616 |       0.402 |       0.165 |     0.008 |           0.108 |
| noise5              | QShrink-CQR        |      0.889 |  0.016 |        0.029 |      0.202 |       0.071 |    0.604 |       0.44  |       0.033 |     0.001 |           0.012 |
| noise5              | QShrink-CQR (MACD) |      0.894 |  0.012 |        0.012 |      0.144 |       0.05  |    0.607 |       0.447 |       0.012 |     0     |           0.007 |
| noise5              | SCP-stage          |      0.861 |  0.099 |        0.349 |      0.32  |       0.352 |    0.652 |       0.443 |       0.248 |     0.003 |           0.002 |
| noise5              | Self-CP            |      0.907 |  0.024 |        0.038 |      0.113 |       0.13  |    0.678 |       0.484 |       0.014 |     0     |           0.012 |
| noise5              | Self-CQR           |      0.894 |  0.016 |        0.013 |      0.19  |       0.055 |    0.614 |       0.457 |       0.011 |     0.001 |           0.005 |
| noise5              | TQA-B-CQR          |      0.876 |  0.03  |        0.192 |      0.233 |       0.2   |    0.606 |       0.424 |       0.084 |     0.001 |           0.016 |
| outage3d            | ACI-CQR            |      0.893 |  0.023 |        0.072 |      0.245 |       0.083 |    0.562 |       0.386 |       0.043 |     0.004 |           0.037 |
| outage3d            | ACI-CQR (MACD)     |      0.894 |  0.021 |        0.053 |      0.245 |       0.066 |    0.562 |       0.387 |       0.041 |     0     |           0.005 |
| outage3d            | CQR                |      0.887 |  0.039 |        0.209 |      0.254 |       0.204 |    0.56  |       0.382 |       0.082 |     0.002 |           0.034 |
| outage3d            | GHCP-CQR           |      0.89  |  0.039 |        0.192 |      0.237 |       0.206 |    0.559 |       0.384 |       0.075 |     0.002 |           0.034 |
| outage3d            | HSC-CQR            |      0.891 |  0.019 |        0.043 |      0.27  |       0.099 |    0.564 |       0.387 |       0.034 |     0.001 |           0.014 |
| outage3d            | PCS-CQR            |      0.895 |  0.016 |        0.028 |      0.206 |       0.104 |    0.564 |       0.395 |       0.032 |     0.001 |           0.014 |
| outage3d            | PCS-CQR κ=168      |      0.895 |  0.016 |        0.028 |      0.209 |       0.099 |    0.564 |       0.395 |       0.032 |     0.001 |           0.014 |
| outage3d            | QR-LGBM            |      0.855 |  0.052 |        0.419 |      0.381 |       0.426 |    0.57  |       0.357 |       0.132 |     0.008 |           0.119 |
| outage3d            | QShrink-CQR        |      0.895 |  0.022 |        0.054 |      0.228 |       0.088 |    0.562 |       0.389 |       0.037 |     0     |           0.011 |
| outage3d            | QShrink-CQR (MACD) |      0.896 |  0.016 |        0.024 |      0.195 |       0.095 |    0.568 |       0.397 |       0.024 |     0     |           0.007 |
| outage3d            | SCP-stage          |      0.871 |  0.097 |        0.319 |      0.304 |       0.307 |    0.639 |       0.445 |       0.215 |     0.002 |           0.006 |
| outage3d            | Self-CP            |      0.909 |  0.027 |        0.057 |      0.207 |       0.111 |    0.663 |       0.462 |       0.016 |     0.001 |           0.01  |
| outage3d            | Self-CQR           |      0.89  |  0.022 |        0.084 |      0.353 |       0.108 |    0.579 |       0.405 |       0.028 |     0.001 |           0.008 |
| outage3d            | TQA-B-CQR          |      0.891 |  0.039 |        0.186 |      0.236 |       0.191 |    0.56  |       0.383 |       0.072 |     0.001 |           0.029 |
| outage7d            | ACI-CQR            |      0.895 |  0.025 |        0.08  |      0.235 |       0.113 |    0.544 |       0.381 |       0.053 |     0.004 |           0.04  |
| outage7d            | ACI-CQR (MACD)     |      0.896 |  0.022 |        0.061 |      0.235 |       0.091 |    0.543 |       0.383 |       0.045 |     0.001 |           0.006 |
| outage7d            | CQR                |      0.891 |  0.039 |        0.188 |      0.244 |       0.207 |    0.545 |       0.377 |       0.086 |     0.002 |           0.019 |
| outage7d            | GHCP-CQR           |      0.893 |  0.039 |        0.179 |      0.228 |       0.208 |    0.546 |       0.379 |       0.079 |     0.001 |           0.028 |
| outage7d            | HSC-CQR            |      0.893 |  0.02  |        0.054 |      0.264 |       0.112 |    0.546 |       0.385 |       0.046 |     0.001 |           0.008 |
| outage7d            | PCS-CQR            |      0.895 |  0.018 |        0.036 |      0.204 |       0.108 |    0.547 |       0.392 |       0.032 |     0.001 |           0.004 |
| outage7d            | PCS-CQR κ=168      |      0.895 |  0.018 |        0.036 |      0.206 |       0.107 |    0.547 |       0.392 |       0.032 |     0.001 |           0.004 |
| outage7d            | QR-LGBM            |      0.858 |  0.051 |        0.406 |      0.369 |       0.426 |    0.549 |       0.352 |       0.158 |     0.008 |           0.119 |
| outage7d            | QShrink-CQR        |      0.897 |  0.023 |        0.061 |      0.217 |       0.096 |    0.543 |       0.39  |       0.045 |     0     |           0.006 |
| outage7d            | QShrink-CQR (MACD) |      0.897 |  0.018 |        0.03  |      0.191 |       0.095 |    0.548 |       0.393 |       0.029 |     0.001 |           0.002 |
| outage7d            | SCP-stage          |      0.877 |  0.097 |        0.307 |      0.291 |       0.306 |    0.626 |       0.448 |       0.223 |     0.003 |           0.024 |
| outage7d            | Self-CP            |      0.909 |  0.029 |        0.061 |      0.202 |       0.125 |    0.651 |       0.453 |       0.03  |     0.001 |           0.006 |
| outage7d            | Self-CQR           |      0.889 |  0.024 |        0.088 |      0.357 |       0.126 |    0.561 |       0.393 |       0.04  |     0     |           0.013 |
| outage7d            | TQA-B-CQR          |      0.894 |  0.039 |        0.179 |      0.229 |       0.203 |    0.545 |       0.381 |       0.083 |     0.002 |           0.005 |
| shift+40            | ACI-CQR            |      0.881 |  0.025 |        0.117 |      0.242 |       0.097 |    0.664 |       0.412 |       0.209 |     0.006 |           0.084 |
| shift+40            | ACI-CQR (MACD)     |      0.884 |  0.022 |        0.078 |      0.242 |       0.053 |    0.663 |       0.416 |       0.178 |     0.001 |           0.016 |
| shift+40            | CQR                |      0.868 |  0.042 |        0.304 |      0.25  |       0.302 |    0.664 |       0.394 |       0.348 |     0.003 |           0.012 |
| shift+40            | GHCP-CQR           |      0.871 |  0.041 |        0.294 |      0.231 |       0.312 |    0.663 |       0.396 |       0.333 |     0.003 |           0.012 |
| shift+40            | HSC-CQR            |      0.881 |  0.022 |        0.065 |      0.265 |       0.09  |    0.663 |       0.413 |       0.194 |     0.001 |           0.01  |
| shift+40            | PCS-CQR            |      0.886 |  0.017 |        0.028 |      0.2   |       0.054 |    0.665 |       0.423 |       0.157 |     0.001 |           0.008 |
| shift+40            | PCS-CQR κ=168      |      0.886 |  0.017 |        0.028 |      0.204 |       0.057 |    0.664 |       0.423 |       0.157 |     0     |           0.008 |
| shift+40            | QR-LGBM            |      0.841 |  0.061 |        0.532 |      0.372 |       0.487 |    0.673 |       0.37  |       0.547 |     0.009 |           0.112 |
| shift+40            | QShrink-CQR        |      0.884 |  0.022 |        0.078 |      0.216 |       0.092 |    0.662 |       0.417 |       0.187 |     0.001 |           0.019 |
| shift+40            | QShrink-CQR (MACD) |      0.888 |  0.017 |        0.026 |      0.183 |       0.054 |    0.666 |       0.426 |       0.14  |     0.001 |           0.01  |
| shift+40            | SCP-stage          |      0.848 |  0.093 |        0.393 |      0.285 |       0.411 |    0.721 |       0.432 |       0.397 |     0.004 |           0.01  |
| shift+40            | Self-CP            |      0.891 |  0.024 |        0.083 |      0.169 |       0.17  |    0.752 |       0.483 |       0.152 |     0     |           0.004 |
| shift+40            | Self-CQR           |      0.884 |  0.022 |        0.083 |      0.335 |       0.047 |    0.672 |       0.436 |       0.165 |     0.001 |           0.01  |
| shift+40            | TQA-B-CQR          |      0.872 |  0.041 |        0.291 |      0.227 |       0.29  |    0.669 |       0.4   |       0.333 |     0.003 |           0.024 |
| shift+40@d7         | ACI-CQR            |      0.886 |  0.023 |        0.092 |      0.858 |       0.05  |    0.636 |       0.403 |       0.154 |     0.005 |           0.064 |
| shift+40@d7         | ACI-CQR (MACD)     |      0.889 |  0.02  |        0.057 |      0.862 |       0.033 |    0.637 |       0.407 |       0.137 |     0.001 |           0.005 |
| shift+40@d7         | CQR                |      0.872 |  0.04  |        0.283 |      0.852 |       0.195 |    0.634 |       0.388 |       0.275 |     0.003 |           0.044 |
| shift+40@d7         | GHCP-CQR           |      0.874 |  0.039 |        0.267 |      0.838 |       0.195 |    0.634 |       0.39  |       0.258 |     0.002 |           0.039 |
| shift+40@d7         | HSC-CQR            |      0.895 |  0.016 |        0.022 |      0.896 |       0.04  |    0.64  |       0.424 |       0.076 |     0     |           0.002 |
| shift+40@d7         | PCS-CQR            |      0.905 |  0.015 |        0.005 |      0.881 |       0.036 |    0.649 |       0.453 |       0.04  |     0.001 |           0.005 |
| shift+40@d7         | PCS-CQR κ=168      |      0.904 |  0.015 |        0.007 |      0.884 |       0.034 |    0.648 |       0.448 |       0.04  |     0.001 |           0.006 |
| shift+40@d7         | QR-LGBM            |      0.844 |  0.058 |        0.509 |      0.916 |       0.415 |    0.644 |       0.364 |       0.443 |     0.009 |           0.123 |
| shift+40@d7         | QShrink-CQR        |      0.897 |  0.019 |        0.029 |      0.852 |       0.045 |    0.639 |       0.424 |       0.066 |     0     |           0.002 |
| shift+40@d7         | QShrink-CQR (MACD) |      0.908 |  0.016 |        0.005 |      0.877 |       0.033 |    0.65  |       0.46  |       0.025 |     0.001 |           0.002 |
| shift+40@d7         | SCP-stage          |      0.851 |  0.094 |        0.374 |      0.65  |       0.308 |    0.689 |       0.431 |       0.372 |     0.004 |           0.015 |
| shift+40@d7         | Self-CP            |      0.925 |  0.033 |        0.022 |      0.76  |       0.049 |    0.737 |       0.556 |       0.018 |     0.001 |           0.008 |
| shift+40@d7         | Self-CQR           |      0.91  |  0.018 |        0.007 |      0.881 |       0.038 |    0.667 |       0.488 |       0.02  |     0.001 |           0.006 |
| shift+40@d7         | TQA-B-CQR          |      0.875 |  0.039 |        0.266 |      0.855 |       0.191 |    0.637 |       0.392 |       0.269 |     0.002 |           0.028 |
| shift-40            | ACI-CQR            |      0.884 |  0.021 |        0.065 |      0.242 |       0.049 |    0.744 |       0.487 |       0.003 |     0.005 |           0.064 |
| shift-40            | ACI-CQR (MACD)     |      0.887 |  0.019 |        0.036 |      0.242 |       0.028 |    0.745 |       0.49  |       0.003 |     0     |           0.016 |
| shift-40            | CQR                |      0.868 |  0.04  |        0.296 |      0.25  |       0.249 |    0.743 |       0.473 |       0.012 |     0.002 |           0.041 |
| shift-40            | GHCP-CQR           |      0.87  |  0.038 |        0.274 |      0.231 |       0.25  |    0.743 |       0.477 |       0.012 |     0.002 |           0.037 |
| shift-40            | HSC-CQR            |      0.883 |  0.019 |        0.045 |      0.265 |       0.072 |    0.746 |       0.491 |       0.001 |     0.002 |           0.008 |
| shift-40            | PCS-CQR            |      0.889 |  0.016 |        0.03  |      0.2   |       0.057 |    0.748 |       0.499 |       0.001 |     0     |           0.008 |
| shift-40            | PCS-CQR κ=168      |      0.889 |  0.016 |        0.03  |      0.204 |       0.058 |    0.748 |       0.498 |       0.001 |     0     |           0.008 |
| shift-40            | QR-LGBM            |      0.836 |  0.065 |        0.597 |      0.372 |       0.51  |    0.755 |       0.449 |       0.02  |     0.01  |           0.102 |
| shift-40            | QShrink-CQR        |      0.885 |  0.019 |        0.051 |      0.216 |       0.079 |    0.745 |       0.492 |       0.003 |     0.001 |           0.008 |
| shift-40            | QShrink-CQR (MACD) |      0.89  |  0.016 |        0.022 |      0.183 |       0.055 |    0.748 |       0.5   |       0.001 |     0     |           0.005 |
| shift-40            | SCP-stage          |      0.808 |  0.107 |        0.535 |      0.285 |       0.665 |    0.881 |       0.461 |       0.154 |     0.002 |           0.035 |
| shift-40            | Self-CP            |      0.877 |  0.032 |        0.195 |      0.169 |       0.35  |    0.875 |       0.528 |       0.003 |     0.002 |           0.024 |
| shift-40            | Self-CQR           |      0.887 |  0.023 |        0.088 |      0.335 |       0.059 |    0.755 |       0.509 |       0.001 |     0.001 |           0.016 |
| shift-40            | TQA-B-CQR          |      0.88  |  0.036 |        0.228 |      0.227 |       0.154 |    0.749 |       0.485 |       0.011 |     0.002 |           0.026 |
| volatility25        | ACI-CQR            |      0.82  |  0.08  |        0.946 |      0.242 |       0.943 |    1.392 |       0.812 |       0.232 |     0.03  |           0.047 |
| volatility25        | ACI-CQR (MACD)     |      0.836 |  0.064 |        0.937 |      0.242 |       0.914 |    1.468 |       0.949 |       0.123 |     0.002 |           0.035 |
| volatility25        | CQR                |      0.75  |  0.15  |        0.991 |      0.25  |       0.997 |    1.328 |       0.507 |       0.639 |     0.01  |           0.01  |
| volatility25        | GHCP-CQR           |      0.752 |  0.148 |        0.989 |      0.231 |       0.997 |    1.327 |       0.509 |       0.631 |     0.009 |           0.008 |
| volatility25        | HSC-CQR            |      0.806 |  0.094 |        0.942 |      0.265 |       0.967 |    1.194 |       0.586 |       0.324 |     0.006 |           0.002 |
| volatility25        | PCS-CQR            |      0.818 |  0.082 |        0.848 |      0.2   |       0.937 |    1.167 |       0.607 |       0.238 |     0.006 |           0.033 |
| volatility25        | PCS-CQR κ=168      |      0.817 |  0.083 |        0.858 |      0.204 |       0.942 |    1.17  |       0.605 |       0.241 |     0.006 |           0.032 |
| volatility25        | QR-LGBM            |      0.724 |  0.176 |        0.996 |      0.372 |       1     |    1.37  |       0.482 |       0.74  |     0.011 |           0.007 |
| volatility25        | QShrink-CQR        |      0.802 |  0.098 |        0.938 |      0.216 |       0.976 |    1.202 |       0.575 |       0.358 |     0.007 |           0.006 |
| volatility25        | QShrink-CQR (MACD) |      0.82  |  0.08  |        0.831 |      0.183 |       0.928 |    1.165 |       0.607 |       0.227 |     0.007 |           0.023 |
| volatility25        | SCP-stage          |      0.68  |  0.22  |        0.991 |      0.285 |       1     |    1.706 |       0.443 |       0.87  |     0.01  |           0.009 |
| volatility25        | Self-CP            |      0.811 |  0.09  |        0.781 |      0.169 |       0.896 |    1.342 |       0.606 |       0.348 |     0.006 |           0.03  |
| volatility25        | Self-CQR           |      0.821 |  0.079 |        0.758 |      0.335 |       0.887 |    1.164 |       0.628 |       0.227 |     0.007 |           0.051 |
| volatility25        | TQA-B-CQR          |      0.801 |  0.099 |        0.901 |      0.227 |       0.988 |    1.192 |       0.578 |       0.343 |     0.003 |           0.022 |
| weak-forecaster     | ACI-CQR            |      0.896 |  0.034 |        0.138 |      0.24  |       0.138 |    0.587 |       0.423 |       0.088 |     0.008 |           0.065 |
| weak-forecaster     | ACI-CQR (MACD)     |      0.898 |  0.026 |        0.072 |      0.235 |       0.074 |    0.586 |       0.423 |       0.061 |     0.001 |           0.01  |
| weak-forecaster     | CQR                |      0.889 |  0.053 |        0.252 |      0.245 |       0.257 |    0.588 |       0.416 |       0.134 |     0.004 |           0.028 |
| weak-forecaster     | GHCP-CQR           |      0.892 |  0.052 |        0.238 |      0.254 |       0.244 |    0.589 |       0.419 |       0.128 |     0.004 |           0.028 |
| weak-forecaster     | HSC-CQR            |      0.894 |  0.021 |        0.051 |      0.249 |       0.124 |    0.589 |       0.42  |       0.055 |     0.001 |           0.014 |
| weak-forecaster     | PCS-CQR            |      0.898 |  0.017 |        0.028 |      0.166 |       0.112 |    0.588 |       0.424 |       0.036 |     0.001 |           0.014 |
| weak-forecaster     | PCS-CQR κ=168      |      0.898 |  0.019 |        0.036 |      0.202 |       0.117 |    0.586 |       0.425 |       0.041 |     0.001 |           0.021 |
| weak-forecaster     | QR-LGBM            |      0.848 |  0.068 |        0.487 |      0.427 |       0.451 |    0.594 |       0.378 |       0.235 |     0.008 |           0.113 |
| weak-forecaster     | QShrink-CQR        |      0.901 |  0.023 |        0.032 |      0.179 |       0.1   |    0.588 |       0.428 |       0.043 |     0.003 |           0.01  |
| weak-forecaster     | QShrink-CQR (MACD) |      0.899 |  0.018 |        0.028 |      0.155 |       0.115 |    0.591 |       0.425 |       0.033 |     0.001 |           0.014 |
| weak-forecaster     | SCP-stage          |      0.881 |  0.093 |        0.292 |      0.271 |       0.294 |    0.649 |       0.478 |       0.215 |     0.004 |           0.024 |
| weak-forecaster     | Self-CP            |      0.904 |  0.027 |        0.057 |      0.175 |       0.162 |    0.674 |       0.465 |       0.041 |     0.001 |           0.006 |
| weak-forecaster     | Self-CQR           |      0.892 |  0.022 |        0.075 |      0.312 |       0.115 |    0.601 |       0.427 |       0.037 |     0.001 |           0.008 |
| weak-forecaster     | TQA-B-CQR          |      0.894 |  0.049 |        0.225 |      0.236 |       0.24  |    0.584 |       0.421 |       0.115 |     0.003 |           0.026 |

### T_tuning.md

**Selected tuning parameters per run**

| part                           |   pcs_kappa |   pcs_is_kappa |   hsc_cqr_K |   hsc_cqr_kappa |   qshrink_is |   qshrink_macd |   aci_gamma_is |   aci_gamma_macdc |   aci_gamma_cov |   grouped_kappa |
|:-------------------------------|------------:|---------------:|------------:|----------------:|-------------:|---------------:|---------------:|------------------:|----------------:|----------------:|
| loso_BDG2_Bear_s0              |         168 |            336 |          25 |             336 |          672 |            168 |          0     |             0.001 |            0.01 |             168 |
| loso_BDG2_Bear_s1              |         168 |            336 |          50 |             336 |          672 |            168 |          0     |             0     |            0.01 |             168 |
| loso_BDG2_Bear_s2              |         168 |            336 |          25 |             336 |          672 |            168 |          0.001 |             0.001 |            0.01 |             168 |
| loso_BDG2_Bull_s0              |         168 |            336 |          50 |             336 |         1344 |            168 |          0     |             0     |            0.01 |             168 |
| loso_BDG2_Bull_s1              |          96 |            336 |          50 |             336 |         1344 |            336 |          0     |             0.001 |            0.01 |              96 |
| loso_BDG2_Bull_s2              |         168 |            336 |          50 |             336 |          672 |            168 |          0.001 |             0.001 |            0.01 |             168 |
| loso_BDG2_Eagle_s0             |         168 |            336 |          25 |             672 |          672 |            168 |          0.001 |             0.001 |            0.01 |             168 |
| loso_BDG2_Eagle_s1             |         168 |            672 |          50 |             336 |          672 |             96 |          0.001 |             0.001 |            0.01 |             168 |
| loso_BDG2_Eagle_s2             |         168 |            336 |          25 |             336 |          672 |            168 |          0.001 |             0.001 |            0.01 |             168 |
| loso_BDG2_Fox_s0               |         168 |            336 |          25 |             336 |          672 |             96 |          0.001 |             0.001 |            0.01 |             168 |
| loso_BDG2_Fox_s1               |          96 |            336 |          50 |             336 |          336 |             96 |          0     |             0     |            0.01 |             168 |
| loso_BDG2_Fox_s2               |         168 |            336 |          50 |             336 |          336 |             96 |          0     |             0.001 |            0.01 |             168 |
| loso_BDG2_Hog_s0               |         168 |            336 |          50 |             336 |          672 |            168 |          0     |             0.001 |            0.01 |             168 |
| loso_BDG2_Hog_s1               |         168 |            336 |          50 |             336 |         1344 |            168 |          0.001 |             0.001 |            0.01 |             168 |
| loso_BDG2_Hog_s2               |         168 |            336 |          50 |             336 |          672 |            168 |          0.001 |             0.001 |            0.01 |             168 |
| loso_BDG2_Moose_s0             |         168 |            336 |          25 |             336 |          672 |            168 |          0     |             0.001 |            0.01 |             168 |
| loso_BDG2_Moose_s1             |          96 |            336 |          50 |             336 |          672 |             96 |          0     |             0.001 |            0.01 |              96 |
| loso_BDG2_Moose_s2             |         168 |            336 |          50 |             336 |          672 |            168 |          0.001 |             0.001 |            0.01 |             168 |
| loso_BDG2_Peacock_s0           |         168 |            336 |          50 |             336 |          336 |            168 |          0     |             0.001 |            0.01 |             168 |
| loso_BDG2_Peacock_s1           |         168 |            336 |          50 |             336 |          672 |             96 |          0     |             0.001 |            0.01 |             168 |
| loso_BDG2_Peacock_s2           |         168 |            336 |          50 |             336 |          336 |            168 |          0.001 |             0.001 |            0.01 |             168 |
| loso_BDG2_Rat_s0               |          96 |            336 |          25 |             336 |          672 |            168 |          0.001 |             0.001 |            0.01 |              96 |
| loso_BDG2_Rat_s1               |         168 |            336 |          50 |             336 |          672 |            168 |          0.001 |             0.001 |            0.01 |             168 |
| loso_BDG2_Rat_s2               |         168 |            336 |         nan |             336 |          672 |            168 |          0.001 |             0.001 |            0.01 |             168 |
| loso_BDG2_Robin_s0             |         168 |            336 |          25 |             336 |          672 |            168 |          0     |             0.001 |            0.01 |             168 |
| loso_BDG2_Robin_s1             |          96 |            336 |          50 |             336 |          672 |             96 |          0.001 |             0.001 |            0.01 |              96 |
| loso_BDG2_Robin_s2             |         168 |            336 |          50 |             336 |          672 |             96 |          0.001 |             0.001 |            0.01 |             168 |
| loso_BDG2_Wolf_s0              |         168 |            336 |          50 |             336 |          336 |             96 |          0.001 |             0.001 |            0.01 |             168 |
| loso_BDG2_Wolf_s1              |         168 |            336 |          25 |             336 |          672 |             96 |          0.001 |             0.001 |            0.01 |             168 |
| loso_BDG2_Wolf_s2              |         168 |            336 |          50 |             336 |          336 |             96 |          0.001 |             0.001 |            0.01 |             168 |
| main_BDG2_s0_a0.05             |          96 |            336 |          50 |             336 |          336 |             48 |          0     |             0     |            0.01 |              96 |
| main_BDG2_s0_a0.1              |          96 |            336 |         100 |             336 |          672 |             96 |          0.001 |             0.001 |            0.01 |              96 |
| main_BDG2_s0_a0.2              |          96 |            336 |          25 |             336 |          336 |             96 |          0.002 |             0.002 |            0.01 |              96 |
| main_BDG2_s1_a0.05             |          96 |            336 |          50 |             336 |          336 |             48 |          0     |             0     |            0.01 |              96 |
| main_BDG2_s1_a0.1              |         168 |            336 |          50 |             336 |          672 |            168 |          0.001 |             0.001 |            0.01 |             168 |
| main_BDG2_s1_a0.2              |         168 |            336 |          25 |             672 |          672 |            168 |          0.002 |             0.002 |            0.01 |             168 |
| main_BDG2_s2_a0.05             |          96 |            336 |          25 |             336 |          336 |             96 |          0     |             0.001 |            0.01 |              96 |
| main_BDG2_s2_a0.1              |         168 |            336 |          25 |             336 |          672 |            168 |          0     |             0.001 |            0.01 |             168 |
| main_BDG2_s2_a0.2              |         168 |            336 |          25 |             672 |          672 |            168 |          0.002 |             0.002 |            0.01 |             168 |
| main_BDG2_s3_a0.05             |          96 |            336 |          50 |             336 |          672 |             96 |          0     |             0     |            0.01 |              96 |
| main_BDG2_s3_a0.1              |         168 |            336 |          25 |             336 |          336 |             96 |          0     |             0.001 |            0.01 |              96 |
| main_BDG2_s3_a0.2              |         168 |            336 |          50 |             336 |          672 |             96 |          0.001 |             0.002 |            0.01 |              96 |
| main_BDG2_s4_a0.05             |         336 |            336 |         nan |             336 |         1344 |            336 |          0     |             0     |            0.01 |             336 |
| main_BDG2_s4_a0.1              |         168 |            336 |         nan |             336 |         1344 |            168 |          0     |             0.001 |            0.01 |             168 |
| main_BDG2_s4_a0.2              |         168 |            336 |          25 |             336 |         1344 |            168 |          0.002 |             0.002 |            0.01 |             168 |
| main_UCI_s0_a0.05              |          96 |            336 |          25 |             336 |          672 |             96 |          0.001 |             0.001 |            0.01 |             nan |
| main_UCI_s0_a0.1               |          48 |            336 |          25 |             336 |          672 |             48 |          0.002 |             0.002 |            0.01 |             nan |
| main_UCI_s0_a0.2               |          48 |            336 |          10 |             336 |          672 |             96 |          0.002 |             0.002 |            0.01 |             nan |
| main_UCI_s1_a0.05              |          48 |             24 |          25 |              24 |          168 |             24 |          0     |             0     |            0.01 |             nan |
| main_UCI_s1_a0.1               |          96 |            168 |          25 |             168 |          168 |             96 |          0     |             0     |            0.01 |             nan |
| main_UCI_s1_a0.2               |          96 |            168 |          10 |             168 |          336 |            168 |          0.001 |             0.002 |            0.01 |             nan |
| main_UCI_s2_a0.05              |          48 |            168 |          25 |             168 |          336 |             24 |          0     |             0     |            0.01 |             nan |
| main_UCI_s2_a0.1               |         168 |            336 |          50 |             336 |          672 |            168 |          0.001 |             0.001 |            0.01 |             nan |
| main_UCI_s2_a0.2               |          96 |            336 |         100 |             336 |          336 |            168 |          0.002 |             0.002 |            0.01 |             nan |
| main_UCI_s3_a0.05              |          24 |             96 |          25 |              96 |          336 |             24 |          0     |             0     |            0.01 |             nan |
| main_UCI_s3_a0.1               |          48 |            168 |         nan |             168 |          336 |             96 |          0     |             0     |            0.01 |             nan |
| main_UCI_s3_a0.2               |          96 |            168 |          25 |             168 |          336 |            168 |          0.001 |             0.001 |            0.01 |             nan |
| main_UCI_s4_a0.05              |         168 |            672 |          50 |             672 |         1344 |            336 |          0.001 |             0.001 |            0.01 |             nan |
| main_UCI_s4_a0.1               |          96 |            672 |          25 |             672 |         1344 |             96 |          0.001 |             0.002 |            0.01 |             nan |
| main_UCI_s4_a0.2               |          96 |            168 |          25 |             336 |          672 |             96 |          0.002 |             0.005 |            0.01 |             nan |
| pools_BDG2_s0_n10_r0           |          96 |            336 |         nan |             nan |          336 |            168 |          0.001 |             0.002 |            0.01 |              96 |
| pools_BDG2_s0_n10_r1           |          96 |            672 |         nan |             nan |         1344 |            168 |          0     |             0.002 |            0.01 |              96 |
| pools_BDG2_s0_n10_r2           |          96 |            336 |         nan |             nan |          336 |             24 |          0.002 |             0.002 |            0.01 |              96 |
| pools_BDG2_s0_n10_r3           |         168 |            336 |         nan |             nan |          168 |            168 |          0.001 |             0.002 |            0.01 |             168 |
| pools_BDG2_s0_n10_r4           |          96 |            672 |         nan |             nan |         1344 |             96 |          0     |             0.002 |            0.01 |              96 |
| pools_BDG2_s0_n20_r0           |         336 |            672 |         nan |             nan |          336 |            168 |          0.001 |             0.002 |            0.01 |             336 |
| pools_BDG2_s0_n20_r1           |          96 |            336 |         nan |             nan |          672 |             96 |          0.001 |             0.001 |            0.01 |              96 |
| pools_BDG2_s0_n20_r2           |          96 |            168 |         nan |             nan |          336 |             96 |          0.001 |             0.002 |            0.01 |              96 |
| pools_BDG2_s0_n20_r3           |          96 |             96 |         nan |             nan |           48 |            168 |          0.002 |             0.002 |            0.01 |             168 |
| pools_BDG2_s0_n20_r4           |         168 |            672 |         nan |             nan |         1344 |            168 |          0.001 |             0.002 |            0.01 |             168 |
| pools_BDG2_s0_n40_r0           |          96 |            336 |         nan |             nan |          672 |             48 |          0.001 |             0.001 |            0.01 |              96 |
| pools_BDG2_s0_n40_r1           |          96 |            336 |         nan |             nan |         1344 |             96 |          0.001 |             0.002 |            0.01 |              96 |
| pools_BDG2_s0_n40_r2           |          96 |            336 |         nan |             nan |          672 |             96 |          0.001 |             0.001 |            0.01 |              96 |
| pools_BDG2_s0_n40_r3           |         168 |            336 |         nan |             nan |         1344 |            168 |          0.001 |             0.001 |            0.01 |             168 |
| pools_BDG2_s0_n40_r4           |         168 |            336 |         nan |             nan |          672 |             96 |          0.001 |             0.001 |            0.01 |             168 |
| pools_BDG2_s0_n5_r0            |          96 |           1344 |         nan |             nan |         1344 |             96 |          0.005 |             0.005 |            0.01 |              96 |
| pools_BDG2_s0_n5_r1            |          48 |            336 |         nan |             nan |          336 |             24 |          0.002 |             0.002 |            0.01 |             nan |
| pools_BDG2_s0_n5_r2            |          96 |            336 |         nan |             nan |          336 |            168 |          0.002 |             0.002 |            0.01 |             168 |
| pools_BDG2_s0_n5_r3            |          96 |             48 |         nan |             nan |            0 |             96 |          0.001 |             0.001 |            0.01 |              96 |
| pools_BDG2_s0_n5_r4            |         336 |            672 |         nan |             nan |          336 |            336 |          0.002 |             0.002 |            0.01 |             336 |
| pools_BDG2_s1_n10_r0           |          96 |            672 |         nan |             nan |          672 |            168 |          0.001 |             0.002 |            0.01 |              96 |
| pools_BDG2_s1_n10_r1           |          24 |            336 |         nan |             nan |          672 |             24 |          0.001 |             0.001 |            0.01 |              24 |
| pools_BDG2_s1_n10_r2           |          96 |            672 |         nan |             nan |         1344 |             96 |          0.001 |             0.002 |            0.01 |              96 |
| pools_BDG2_s1_n10_r3           |          24 |            672 |         nan |             nan |          672 |             24 |          0.001 |             0.002 |            0.01 |              24 |
| pools_BDG2_s1_n10_r4           |         168 |            168 |         nan |             nan |          336 |             96 |          0.001 |             0.002 |            0.01 |             168 |
| pools_BDG2_s1_n20_r0           |          96 |            336 |         nan |             nan |          336 |             96 |          0.001 |             0.001 |            0.01 |              96 |
| pools_BDG2_s1_n20_r1           |         336 |            672 |         nan |             nan |          672 |            336 |          0.001 |             0.001 |            0.01 |             336 |
| pools_BDG2_s1_n20_r2           |         168 |            672 |         nan |             nan |          672 |            168 |          0.001 |             0.001 |            0.01 |             168 |
| pools_BDG2_s1_n20_r3           |          96 |            672 |         nan |             nan |          672 |            168 |          0.001 |             0.002 |            0.01 |              96 |
| pools_BDG2_s1_n20_r4           |          96 |            168 |         nan |             nan |          336 |            168 |          0.001 |             0.001 |            0.01 |              96 |
| pools_BDG2_s1_n40_r0           |         168 |            336 |         nan |             nan |          336 |            168 |          0.001 |             0.001 |            0.01 |             168 |
| pools_BDG2_s1_n40_r1           |         168 |            336 |         nan |             nan |          336 |            168 |          0.002 |             0.002 |            0.01 |             168 |
| pools_BDG2_s1_n40_r2           |          96 |            336 |         nan |             nan |          672 |             96 |          0.001 |             0.001 |            0.01 |              96 |
| pools_BDG2_s1_n40_r3           |          96 |            336 |         nan |             nan |          336 |             96 |          0.001 |             0.001 |            0.01 |              96 |
| pools_BDG2_s1_n40_r4           |         168 |            672 |         nan |             nan |          672 |            336 |          0.001 |             0.001 |            0.01 |             168 |
| pools_BDG2_s1_n5_r0            |          96 |            336 |         nan |             nan |          336 |             48 |          0.001 |             0.001 |            0.01 |              96 |
| pools_BDG2_s1_n5_r1            |           0 |            168 |         nan |             nan |           96 |              0 |          0.001 |             0.002 |            0.01 |              24 |
| pools_BDG2_s1_n5_r2            |         168 |            inf |         nan |             nan |          336 |            168 |          0.002 |             0.002 |            0.01 |              96 |
| pools_BDG2_s1_n5_r3            |          48 |            672 |         nan |             nan |          672 |             24 |          0     |             0.002 |            0.01 |              48 |
| pools_BDG2_s1_n5_r4            |          24 |             96 |         nan |             nan |           96 |             24 |          0.002 |             0.002 |            0.01 |              24 |
| pools_BDG2_s2_n10_r0           |         168 |            336 |         nan |             nan |          336 |             48 |          0.001 |             0.001 |            0.01 |             168 |
| pools_BDG2_s2_n10_r1           |         336 |            336 |         nan |             nan |          336 |            336 |          0.002 |             0.002 |            0.01 |             168 |
| pools_BDG2_s2_n10_r2           |        1344 |           1344 |         nan |             nan |         1344 |            672 |          0.002 |             0.002 |            0.01 |             672 |
| pools_BDG2_s2_n10_r3           |          96 |            336 |         nan |             nan |          672 |             96 |          0.002 |             0.002 |            0.01 |              96 |
| pools_BDG2_s2_n10_r4           |          96 |            336 |         nan |             nan |          336 |            168 |          0.002 |             0.002 |            0.01 |              48 |
| pools_BDG2_s2_n20_r0           |         168 |            336 |         nan |             nan |          336 |            336 |          0.001 |             0.002 |            0.01 |             168 |
| pools_BDG2_s2_n20_r1           |         672 |            336 |         nan |             nan |          672 |            672 |          0.001 |             0.002 |            0.01 |             672 |
| pools_BDG2_s2_n20_r2           |         336 |            168 |         nan |             nan |          336 |            672 |          0     |             0     |            0.01 |             336 |
| pools_BDG2_s2_n20_r3           |         336 |           1344 |         nan |             nan |         1344 |            336 |          0     |             0.002 |            0.01 |             336 |
| pools_BDG2_s2_n20_r4           |          96 |           1344 |         nan |             nan |         1344 |             96 |          0     |             0.002 |            0.01 |              96 |
| pools_BDG2_s2_n40_r0           |         168 |            168 |         nan |             nan |          336 |            168 |          0     |             0.001 |            0.01 |             168 |
| pools_BDG2_s2_n40_r1           |         336 |            672 |         nan |             nan |          672 |            336 |          0.001 |             0.001 |            0.01 |             336 |
| pools_BDG2_s2_n40_r2           |         336 |            672 |         nan |             nan |          672 |            336 |          0.001 |             0.001 |            0.01 |             168 |
| pools_BDG2_s2_n40_r3           |         336 |           1344 |         nan |             nan |         1344 |            336 |          0.001 |             0.001 |            0.01 |             336 |
| pools_BDG2_s2_n40_r4           |         336 |            336 |         nan |             nan |          672 |            336 |          0.001 |             0.001 |            0.01 |             336 |
| pools_BDG2_s2_n5_r0            |         168 |           1344 |         nan |             nan |         1344 |            168 |          0.001 |             0.002 |            0.01 |             168 |
| pools_BDG2_s2_n5_r1            |         336 |           1344 |         nan |             nan |          672 |            672 |          0     |             0.005 |            0.01 |             168 |
| pools_BDG2_s2_n5_r2            |         336 |            336 |         nan |             nan |          168 |             96 |          0.002 |             0.002 |            0.01 |              48 |
| pools_BDG2_s2_n5_r3            |         168 |            336 |         nan |             nan |          336 |            168 |          0.001 |             0.002 |            0.01 |             168 |
| pools_BDG2_s2_n5_r4            |          96 |            168 |         nan |             nan |          168 |            168 |          0.002 |             0.002 |            0.01 |              96 |
| robust_BDG2_s0_cal10           |          48 |            168 |          25 |             168 |          168 |             48 |          0     |             0.001 |            0.01 |              48 |
| robust_BDG2_s0_cal25           |          96 |            336 |          25 |             336 |          672 |             96 |          0.001 |             0.001 |            0.01 |             168 |
| robust_BDG2_s0_cal50           |          96 |            336 |          50 |             336 |          672 |             96 |          0.001 |             0.001 |            0.01 |              96 |
| robust_BDG2_s0_missing20       |          96 |            336 |         100 |             336 |          672 |             96 |          0.001 |             0.001 |            0.01 |              96 |
| robust_BDG2_s0_missing40       |          96 |            336 |         100 |             336 |          672 |             96 |          0.001 |             0.001 |            0.01 |              96 |
| robust_BDG2_s0_noise15-history |          96 |            336 |         100 |             336 |          672 |             96 |          0.001 |             0.001 |            0.01 |              96 |
| robust_BDG2_s0_noise15         |          96 |            336 |         100 |             336 |          672 |             96 |          0.001 |             0.001 |            0.01 |              96 |
| robust_BDG2_s0_noise5          |          96 |            336 |         100 |             336 |          672 |             96 |          0.001 |             0.001 |            0.01 |              96 |
| robust_BDG2_s0_outage3d        |          96 |            336 |         100 |             336 |          672 |             96 |          0.001 |             0.001 |            0.01 |              96 |
| robust_BDG2_s0_outage7d        |          96 |            336 |         100 |             336 |          672 |             96 |          0.001 |             0.001 |            0.01 |              96 |
| robust_BDG2_s0_shift+40@d7     |          96 |            336 |         100 |             336 |          672 |             96 |          0.001 |             0.001 |            0.01 |              96 |
| robust_BDG2_s0_shift+40        |          96 |            336 |         100 |             336 |          672 |             96 |          0.001 |             0.001 |            0.01 |              96 |
| robust_BDG2_s0_shift-40        |          96 |            336 |         100 |             336 |          672 |             96 |          0.001 |             0.001 |            0.01 |              96 |
| robust_BDG2_s0_tsplit          |          96 |            336 |         100 |             336 |          672 |             96 |          0.001 |             0.001 |            0.01 |              96 |
| robust_BDG2_s0_volatility25    |          96 |            336 |         100 |             336 |          672 |             96 |          0.001 |             0.001 |            0.01 |              96 |
| robust_BDG2_s0_weakmodel       |          96 |            336 |          25 |             336 |          336 |             96 |          0     |             0.001 |            0.01 |              96 |
| robust_BDG2_s1_cal10           |          96 |            168 |          10 |             168 |          168 |             96 |          0     |             0     |            0.01 |              96 |
| robust_BDG2_s1_cal25           |         168 |            336 |          50 |             336 |          672 |            168 |          0.001 |             0.001 |            0.01 |             168 |
| robust_BDG2_s1_cal50           |          96 |            336 |          50 |             336 |          672 |             96 |          0.001 |             0.001 |            0.01 |              96 |
| robust_BDG2_s1_missing20       |         168 |            336 |          50 |             336 |          672 |            168 |          0.001 |             0.001 |            0.01 |             168 |
| robust_BDG2_s1_missing40       |         168 |            336 |          50 |             336 |          672 |            168 |          0.001 |             0.001 |            0.01 |             168 |
| robust_BDG2_s1_noise15-history |         168 |            336 |          50 |             336 |          672 |            168 |          0.001 |             0.001 |            0.01 |             168 |
| robust_BDG2_s1_noise15         |         168 |            336 |          50 |             336 |          672 |            168 |          0.001 |             0.001 |            0.01 |             168 |
| robust_BDG2_s1_noise5          |         168 |            336 |          50 |             336 |          672 |            168 |          0.001 |             0.001 |            0.01 |             168 |
| robust_BDG2_s1_outage3d        |         168 |            336 |          50 |             336 |          672 |            168 |          0.001 |             0.001 |            0.01 |             168 |
| robust_BDG2_s1_outage7d        |         168 |            336 |          50 |             336 |          672 |            168 |          0.001 |             0.001 |            0.01 |             168 |
| robust_BDG2_s1_shift+40@d7     |         168 |            336 |          50 |             336 |          672 |            168 |          0.001 |             0.001 |            0.01 |             168 |
| robust_BDG2_s1_shift+40        |         168 |            336 |          50 |             336 |          672 |            168 |          0.001 |             0.001 |            0.01 |             168 |
| robust_BDG2_s1_shift-40        |         168 |            336 |          50 |             336 |          672 |            168 |          0.001 |             0.001 |            0.01 |             168 |
| robust_BDG2_s1_tsplit          |         168 |            336 |          50 |             336 |          672 |            168 |          0.001 |             0.001 |            0.01 |             168 |
| robust_BDG2_s1_volatility25    |         168 |            336 |          50 |             336 |          672 |            168 |          0.001 |             0.001 |            0.01 |             168 |
| robust_BDG2_s1_weakmodel       |          96 |            168 |          50 |             168 |          168 |             48 |          0     |             0.001 |            0.01 |              96 |
| robust_BDG2_s2_cal10           |         672 |           1344 |          25 |             672 |          672 |            672 |          0.001 |             0.001 |            0.01 |             672 |
| robust_BDG2_s2_cal25           |         168 |            336 |          25 |             336 |          336 |            168 |          0.001 |             0.001 |            0.01 |             168 |
| robust_BDG2_s2_cal50           |         168 |            672 |         100 |             672 |          672 |            168 |          0.001 |             0.001 |            0.01 |             168 |
| robust_BDG2_s2_missing20       |         168 |            336 |          25 |             336 |          672 |            168 |          0     |             0.001 |            0.01 |             168 |
| robust_BDG2_s2_missing40       |         168 |            336 |          25 |             336 |          672 |            168 |          0     |             0.001 |            0.01 |             168 |
| robust_BDG2_s2_noise15-history |         168 |            336 |          25 |             336 |          672 |            168 |          0     |             0.001 |            0.01 |             168 |
| robust_BDG2_s2_noise15         |         168 |            336 |          25 |             336 |          672 |            168 |          0     |             0.001 |            0.01 |             168 |
| robust_BDG2_s2_noise5          |         168 |            336 |          25 |             336 |          672 |            168 |          0     |             0.001 |            0.01 |             168 |
| robust_BDG2_s2_outage3d        |         168 |            336 |          25 |             336 |          672 |            168 |          0     |             0.001 |            0.01 |             168 |
| robust_BDG2_s2_outage7d        |         168 |            336 |          25 |             336 |          672 |            168 |          0     |             0.001 |            0.01 |             168 |
| robust_BDG2_s2_shift+40@d7     |         168 |            336 |          25 |             336 |          672 |            168 |          0     |             0.001 |            0.01 |             168 |
| robust_BDG2_s2_shift+40        |         168 |            336 |          25 |             336 |          672 |            168 |          0     |             0.001 |            0.01 |             168 |
| robust_BDG2_s2_shift-40        |         168 |            336 |          25 |             336 |          672 |            168 |          0     |             0.001 |            0.01 |             168 |
| robust_BDG2_s2_tsplit          |         168 |            336 |          25 |             336 |          672 |            168 |          0     |             0.001 |            0.01 |             168 |
| robust_BDG2_s2_volatility25    |         168 |            336 |          25 |             336 |          672 |            168 |          0     |             0.001 |            0.01 |             168 |
| robust_BDG2_s2_weakmodel       |          96 |            336 |          25 |             336 |          336 |             96 |          0.001 |             0.001 |            0.01 |              96 |
| xds_BDG2toBDG2_s0              |          96 |            336 |          50 |             336 |          672 |            168 |          0.001 |             0.001 |            0.01 |              96 |
| xds_BDG2toBDG2_s1              |         168 |            336 |         nan |             336 |          336 |            168 |          0.001 |             0.001 |            0.01 |             168 |
| xds_BDG2toBDG2_s2              |         168 |            336 |          50 |             336 |          672 |            168 |          0.001 |             0.001 |            0.01 |             168 |
| xds_BDG2toUCI_s0               |          96 |            336 |          50 |             336 |          672 |            168 |          0.001 |             0.001 |            0.01 |             nan |
| xds_BDG2toUCI_s1               |         168 |            336 |         nan |             336 |          336 |            168 |          0.001 |             0.001 |            0.01 |             nan |
| xds_BDG2toUCI_s2               |         168 |            336 |          50 |             336 |          672 |            168 |          0.001 |             0.001 |            0.01 |             nan |
| xds_UCItoBDG2_s0               |          48 |            336 |          25 |             336 |          672 |             48 |          0.002 |             0.002 |            0.01 |             nan |
| xds_UCItoBDG2_s1               |          96 |            168 |          25 |             168 |          168 |             96 |          0     |             0     |            0.01 |             nan |
| xds_UCItoBDG2_s2               |         168 |            336 |          50 |             336 |          672 |            168 |          0.001 |             0.001 |            0.01 |             nan |

### T_tuning_curves.md

**LOBO objectives of PCS-CQR on calibration buildings**

| part              | K   |   kappa |    obj |   macd |   under |
|:------------------|:----|--------:|-------:|-------:|--------:|
| main_BDG2_s0_a0.1 |     |       0 | 0.5907 | 0.0202 |  0.0595 |
| main_BDG2_s0_a0.1 |     |      24 | 0.5855 | 0.0168 |  0.0417 |
| main_BDG2_s0_a0.1 |     |      48 | 0.5832 | 0.0156 |  0.0179 |
| main_BDG2_s0_a0.1 |     |      96 | 0.5809 | 0.015  |  0.0119 |
| main_BDG2_s0_a0.1 |     |     168 | 0.5794 | 0.0153 |  0.0298 |
| main_BDG2_s0_a0.1 |     |     336 | 0.5786 | 0.017  |  0.0238 |
| main_BDG2_s0_a0.1 |     |     672 | 0.579  | 0.0204 |  0.0476 |
| main_BDG2_s0_a0.1 |     |    1344 | 0.5801 | 0.0252 |  0.0833 |
| main_BDG2_s0_a0.1 |     |     inf | 0.5835 | 0.0358 |  0.125  |
| main_BDG2_s1_a0.1 |     |       0 | 0.6339 | 0.0219 |  0.0714 |
| main_BDG2_s1_a0.1 |     |      24 | 0.6287 | 0.0181 |  0.0357 |
| main_BDG2_s1_a0.1 |     |      48 | 0.6266 | 0.0169 |  0.0179 |
| main_BDG2_s1_a0.1 |     |      96 | 0.6244 | 0.0154 |  0.0179 |
| main_BDG2_s1_a0.1 |     |     168 | 0.6231 | 0.0151 |  0.0238 |
| main_BDG2_s1_a0.1 |     |     336 | 0.6225 | 0.0163 |  0.0238 |
| main_BDG2_s1_a0.1 |     |     672 | 0.6229 | 0.0206 |  0.0417 |
| main_BDG2_s1_a0.1 |     |    1344 | 0.6239 | 0.0256 |  0.0774 |
| main_BDG2_s1_a0.1 |     |     inf | 0.6277 | 0.0368 |  0.1726 |
| main_BDG2_s2_a0.1 |     |       0 | 0.5747 | 0.0232 |  0.1131 |
| main_BDG2_s2_a0.1 |     |      24 | 0.5711 | 0.0195 |  0.0833 |
| main_BDG2_s2_a0.1 |     |      48 | 0.5693 | 0.0178 |  0.0595 |
| main_BDG2_s2_a0.1 |     |      96 | 0.5677 | 0.0157 |  0.0476 |
| main_BDG2_s2_a0.1 |     |     168 | 0.5666 | 0.0148 |  0.0417 |
| main_BDG2_s2_a0.1 |     |     336 | 0.5662 | 0.0149 |  0.0357 |
| main_BDG2_s2_a0.1 |     |     672 | 0.5665 | 0.0171 |  0.0357 |
| main_BDG2_s2_a0.1 |     |    1344 | 0.5673 | 0.0204 |  0.0536 |
| main_BDG2_s2_a0.1 |     |     inf | 0.5698 | 0.0292 |  0.0952 |
| main_BDG2_s3_a0.1 |     |       0 | 0.7366 | 0.0215 |  0.0655 |
| main_BDG2_s3_a0.1 |     |      24 | 0.727  | 0.0183 |  0.0417 |
| main_BDG2_s3_a0.1 |     |      48 | 0.7244 | 0.017  |  0.0357 |
| main_BDG2_s3_a0.1 |     |      96 | 0.7202 | 0.016  |  0.0357 |
| main_BDG2_s3_a0.1 |     |     168 | 0.7164 | 0.016  |  0.0298 |
| main_BDG2_s3_a0.1 |     |     336 | 0.7146 | 0.0184 |  0.0298 |
| main_BDG2_s3_a0.1 |     |     672 | 0.7157 | 0.0228 |  0.0536 |
| main_BDG2_s3_a0.1 |     |    1344 | 0.718  | 0.0282 |  0.0833 |
| main_BDG2_s3_a0.1 |     |     inf | 0.7255 | 0.0399 |  0.1548 |
| main_BDG2_s4_a0.1 |     |       0 | 0.7819 | 0.0232 |  0.1012 |
| main_BDG2_s4_a0.1 |     |      24 | 0.7595 | 0.0186 |  0.0417 |
| main_BDG2_s4_a0.1 |     |      48 | 0.7415 | 0.0168 |  0.0298 |
| main_BDG2_s4_a0.1 |     |      96 | 0.7224 | 0.0153 |  0.0179 |
| main_BDG2_s4_a0.1 |     |     168 | 0.7134 | 0.015  |  0.006  |
| main_BDG2_s4_a0.1 |     |     336 | 0.712  | 0.0172 |  0      |
| main_BDG2_s4_a0.1 |     |     672 | 0.7126 | 0.0229 |  0.0298 |
| main_BDG2_s4_a0.1 |     |    1344 | 0.7146 | 0.0292 |  0.0952 |
| main_BDG2_s4_a0.1 |     |     inf | 0.7222 | 0.0438 |  0.1786 |
| main_UCI_s0_a0.1  |     |       0 | 0.5617 | 0.0114 |  0      |
| main_UCI_s0_a0.1  |     |      24 | 0.5549 | 0.0103 |  0      |
| main_UCI_s0_a0.1  |     |      48 | 0.5506 | 0.0102 |  0      |
| main_UCI_s0_a0.1  |     |      96 | 0.5459 | 0.0103 |  0      |
| main_UCI_s0_a0.1  |     |     168 | 0.5428 | 0.0108 |  0      |
| main_UCI_s0_a0.1  |     |     336 | 0.5424 | 0.0138 |  0      |
| main_UCI_s0_a0.1  |     |     672 | 0.5428 | 0.0177 |  0.0476 |
| main_UCI_s0_a0.1  |     |    1344 | 0.5437 | 0.0213 |  0.0476 |
| main_UCI_s0_a0.1  |     |     inf | 0.5464 | 0.0297 |  0.127  |
| main_UCI_s1_a0.1  |     |       0 | 0.8151 | 0.0174 |  0.0476 |
| main_UCI_s1_a0.1  |     |      24 | 0.8106 | 0.015  |  0.0159 |
| main_UCI_s1_a0.1  |     |      48 | 0.8083 | 0.0143 |  0.0159 |
| main_UCI_s1_a0.1  |     |      96 | 0.8073 | 0.0139 |  0.0159 |
| main_UCI_s1_a0.1  |     |     168 | 0.8062 | 0.0145 |  0.0159 |
| main_UCI_s1_a0.1  |     |     336 | 0.8075 | 0.0159 |  0.0159 |
| main_UCI_s1_a0.1  |     |     672 | 0.8102 | 0.0196 |  0.0476 |
| main_UCI_s1_a0.1  |     |    1344 | 0.8142 | 0.0242 |  0.0635 |
| main_UCI_s1_a0.1  |     |     inf | 0.8243 | 0.0364 |  0.1111 |
| main_UCI_s2_a0.1  |     |       0 | 0.5606 | 0.0164 |  0.0159 |
| main_UCI_s2_a0.1  |     |      24 | 0.5566 | 0.0141 |  0.0159 |
| main_UCI_s2_a0.1  |     |      48 | 0.5549 | 0.0133 |  0.0159 |
| main_UCI_s2_a0.1  |     |      96 | 0.5527 | 0.0124 |  0.0159 |
| main_UCI_s2_a0.1  |     |     168 | 0.551  | 0.0118 |  0.0159 |
| main_UCI_s2_a0.1  |     |     336 | 0.5504 | 0.0137 |  0.0159 |
| main_UCI_s2_a0.1  |     |     672 | 0.551  | 0.0181 |  0.0159 |
| main_UCI_s2_a0.1  |     |    1344 | 0.5525 | 0.0228 |  0.0476 |
| main_UCI_s2_a0.1  |     |     inf | 0.5568 | 0.0328 |  0.1111 |
| main_UCI_s3_a0.1  |     |       0 | 0.7724 | 0.014  |  0      |
| main_UCI_s3_a0.1  |     |      24 | 0.7675 | 0.0118 |  0      |
| main_UCI_s3_a0.1  |     |      48 | 0.7641 | 0.0114 |  0      |
| main_UCI_s3_a0.1  |     |      96 | 0.7603 | 0.0115 |  0      |
| main_UCI_s3_a0.1  |     |     168 | 0.7596 | 0.0122 |  0      |
| main_UCI_s3_a0.1  |     |     336 | 0.7603 | 0.0152 |  0.0317 |
| main_UCI_s3_a0.1  |     |     672 | 0.763  | 0.0207 |  0.0635 |
| main_UCI_s3_a0.1  |     |    1344 | 0.7667 | 0.0266 |  0.0952 |
| main_UCI_s3_a0.1  |     |     inf | 0.7755 | 0.0394 |  0.1587 |
| main_UCI_s4_a0.1  |     |       0 | 0.4541 | 0.0126 |  0      |
| main_UCI_s4_a0.1  |     |      24 | 0.4475 | 0.0103 |  0      |
| main_UCI_s4_a0.1  |     |      48 | 0.444  | 0.0097 |  0      |
| main_UCI_s4_a0.1  |     |      96 | 0.4391 | 0.0089 |  0      |
| main_UCI_s4_a0.1  |     |     168 | 0.4361 | 0.0094 |  0      |
| main_UCI_s4_a0.1  |     |     336 | 0.4357 | 0.0109 |  0      |
| main_UCI_s4_a0.1  |     |     672 | 0.4356 | 0.0133 |  0      |
| main_UCI_s4_a0.1  |     |    1344 | 0.4357 | 0.0161 |  0.0317 |
| main_UCI_s4_a0.1  |     |     inf | 0.4367 | 0.0222 |  0.0635 |

### T_weeks_BDG2.md

**Per-building reliability by onboarding week, BDG2**

| Method             |   Under-cov. week 1 |   P10 week 1 |   Under-cov. week 2 |   P10 week 2 |   Under-cov. weeks 3-4 |   P10 weeks 3-4 |   Under-cov. weeks 5-8 |   P10 weeks 5-8 |
|:-------------------|--------------------:|-------------:|--------------------:|-------------:|-----------------------:|----------------:|-----------------------:|----------------:|
| PCS-CQR            |               0.194 |        0.822 |               0.198 |        0.812 |                  0.153 |           0.833 |                  0.11  |           0.848 |
| PCS-CQR κ=168      |               0.197 |        0.821 |               0.198 |        0.811 |                  0.153 |           0.833 |                  0.109 |           0.848 |
| PCS-CQR +stage     |               0.193 |        0.824 |               0.204 |        0.811 |                  0.156 |           0.832 |                  0.108 |           0.849 |
| HSC-CQR            |               0.252 |        0.801 |               0.217 |        0.803 |                  0.176 |           0.83  |                  0.111 |           0.848 |
| QShrink-CQR (MACD) |               0.177 |        0.828 |               0.189 |        0.817 |                  0.145 |           0.835 |                  0.103 |           0.85  |
| Self-CQR           |               0.338 |        0.785 |               0.252 |        0.799 |                  0.174 |           0.827 |                  0.126 |           0.846 |
| ACI-CQR            |               0.238 |        0.794 |               0.23  |        0.794 |                  0.206 |           0.824 |                  0.107 |           0.851 |
| ACI-CQR (MACD)     |               0.237 |        0.796 |               0.225 |        0.799 |                  0.188 |           0.828 |                  0.071 |           0.858 |
| TQA-B-CQR          |               0.232 |        0.802 |               0.244 |        0.794 |                  0.244 |           0.812 |                  0.198 |           0.825 |
| GHCP-CQR           |               0.225 |        0.793 |               0.224 |        0.794 |                  0.219 |           0.809 |                  0.21  |           0.821 |
| CQR                |               0.242 |        0.79  |               0.258 |        0.787 |                  0.255 |           0.802 |                  0.207 |           0.821 |

### T_weeks_UCI.md

**Per-building reliability by onboarding week, UCI**

| Method             |   Under-cov. week 1 |   P10 week 1 |   Under-cov. week 2 |   P10 week 2 |   Under-cov. weeks 3-4 |   P10 weeks 3-4 |   Under-cov. weeks 5-8 |   P10 weeks 5-8 |
|:-------------------|--------------------:|-------------:|--------------------:|-------------:|-----------------------:|----------------:|-----------------------:|----------------:|
| PCS-CQR            |               0.103 |        0.85  |               0.122 |        0.843 |                  0.086 |           0.853 |                  0.044 |           0.86  |
| PCS-CQR κ=168      |               0.12  |        0.841 |               0.114 |        0.847 |                  0.086 |           0.857 |                  0.04  |           0.863 |
| PCS-CQR +stage     |               0.086 |        0.855 |               0.126 |        0.843 |                  0.086 |           0.852 |                  0.042 |           0.861 |
| HSC-CQR            |               0.164 |        0.831 |               0.126 |        0.841 |                  0.101 |           0.852 |                  0.051 |           0.861 |
| QShrink-CQR (MACD) |               0.093 |        0.854 |               0.116 |        0.845 |                  0.091 |           0.854 |                  0.046 |           0.861 |
| Self-CQR           |               0.227 |        0.812 |               0.156 |        0.832 |                  0.135 |           0.845 |                  0.055 |           0.859 |
| ACI-CQR            |               0.149 |        0.83  |               0.143 |        0.84  |                  0.112 |           0.848 |                  0.034 |           0.87  |
| ACI-CQR (MACD)     |               0.149 |        0.83  |               0.139 |        0.844 |                  0.097 |           0.851 |                  0.032 |           0.871 |
| TQA-B-CQR          |               0.147 |        0.83  |               0.152 |        0.833 |                  0.149 |           0.837 |                  0.112 |           0.854 |
| GHCP-CQR           |               0.135 |        0.836 |               0.103 |        0.846 |                  0.105 |           0.848 |                  0.099 |           0.856 |
| CQR                |               0.156 |        0.827 |               0.166 |        0.831 |                  0.156 |           0.832 |                  0.114 |           0.853 |


## 3. Code map (verify claims here)


- src/data/datasets.py — download, cleaning (stuck-meter runs >=24 h, interpolation <=6 h for inputs only,
  obs mask of actually observed hours, UCI DST masking, filters, exclusion flow -> data/processed/*_exclusion.json).
- src/preprocessing/features.py — build(): history-masked, scale-normalised features (Eq. 1 scale);
  descriptor(): load-shape descriptor for the optional kNN prior.
- src/models/forecasters.py — LightGBM point/quantile, MLP Gaussian/quantile (early stopping on validation buildings).
- src/models/calibration.py — grid CDFs; pooled_quantile; neighbours; prior_cdf (incl. grouped LOBO);
  hsc_quantiles (Eq. pcs; kappa=0 fallback); aci_quantiles (conformal level, finite fallback); coverage_objective;
  normalized_IS; ghcp_quantiles; qshrink_quantiles; tqab_quantiles.
- src/training/pipeline.py — split() (random / loso / lso), train_models, onboard_dates, window_predictions
  (scores only observed hours), _select (IS / MACD / MACDc rules), tune_hsc / tune_aci / tune_qshrink,
  run_calibration (all interval methods, timings), common_mask/evaluate.
- src/experiments.py — experiment plan, prepared() caches (incl. disjoint calibration period), perturbations,
  small pools, sensitivity, examples.
- src/evaluation/metrics.py — per-building coverage (overall, per week), width, interval score, exceedance,
  reserve cost.
- src/statistics/analysis.py — seed-level tables, paired comparisons (site sign-flip randomisation tests,
  cluster bootstrap, Holm, Wilcoxon secondary), week/site/pool/tuning/cost tables.
- src/statistics/manuscript_tables.py, error_analysis.py, latency.py; manuscript/values.py (every number in the
  text); manuscript/build_docx.py; tests/test_core.py (15 tests); experiments/PREREGISTRATION.md,
  experiments/DEVIATIONS.md; CHANGELOG.md.
- results/raw/raw_results_<exp>.csv.gz (per building x seed x method), results/statistics.csv, results/run_info.json
  (tuned parameters + tuning tables + timings), results/seed_level_metrics.csv, results/stage_curves.csv.


## 3b. Authors' response to review cycle 1

# Authors' response to review cycle 1

We thank the ten reviewers. All results were recomputed from scratch with the revised code: data re-downloaded
and re-cleaned, 61 experiment jobs, and new protocols. Numbers below come from the revised result files and are
also in the manuscript. Supplementary Table S1 (`experiments/DEVIATIONS.md`) logs every change from the analysis
plan. Items follow `REVIEW/review_01.md`.

## A. Critical

**A1 — Fixed κ=168 beat the LOBO-tuned method; the interval-score objective is flat.** Accepted in full.
LOBO interval-score selection is no longer presented as a contribution. Instead, the paper reports that this
objective is nearly flat in κ (Supplementary tuning curves; Section 5.4) and that it does not target reliability.
We added a reliability-aware LOBO rule (`_select(..., "MACDc")`): among parameter values whose LOBO interval score
is within 2 % of the minimum, it picks the one with the smallest LOBO coverage deviation. For fairness, the rule is
applied to every tuned competitor: PCS, QShrink and ACI. We also report a coverage-only ACI reference. Fixed
pseudo-count versions (PCS-CQR κ=168, QShrink-CQR λ=168) are reported in every protocol. A grouped (leave-site-out)
LOBO variant is reported where the calibration set spans more than two sites. The small-pool failure the reviewers
found is now examined systematically (5–40 calibration buildings × 5 draws × 3 seeds; Table S-pools).
Result: the LOBO interval score varies by only 1.2 % (BDG2) / 1.1 % (UCI) across finite κ and κ=∞ is only 0.9 % worse. The reliability-aware rule selects κ ∈ {96, 168} (BDG2) and {48, 96, 168} (UCI) and halves the under-covered share relative to IS-tuning (BDG2 1.4 % vs 2.9 %; coverage deviation p = 0.014, under-covered share p = 0.16). Fixed κ=168 is statistically indistinguishable (1.5 %), and the text recommends it for small pools, where it is better than the tuned value (5 calibration buildings: 1.7 % vs 2.7 %). Site-grouped LOBO changes nothing.

**A2 — Headline numbers came from the variant the paper called unnecessary.** Accepted. The method is now the
one-parameter layer with a uniform prior and no stage matching, renamed *pseudo-count shrinkage* (PCS, PCS-CQR).
"Hierarchical" was dropped. The similarity (kNN) prior and stage matching appear only in the design ablation, and
the text states where they hurt. Figure 1 was redrawn. The pre-registered HSC/HSC-CQR configuration stays in as a
labelled comparator. Result: PCS-CQR 1.4 % / 0.4 % under-covered (BDG2/UCI) vs HSC-CQR 3.4 % / 1.3 %. +stage changes nothing, +kNN slightly harms, and HSC-CQR has the worst week 1 of the shrinkage variants (25.2 % vs 19.4 %).

**A3 — Pre-registration overstated.** Accepted. "Pre-registered" was replaced by "internal analysis plan fixed
before the full experiments (not externally registered)". The false sentence "All settings were fixed…" was
removed. The new Supplementary Table S1 has 16 entries, each with date, reason and whether target results had been
seen. The planned primary comparison (absolute-score HSC against the planned baselines) is reported in full as the
"preregistered-abs" family, including the finding that it does not beat self-only calibration. Results for PCS-CQR
and for the protocols added in revision are labelled exploratory.

**A4 — No gain in week 1.** Accepted. Every CQR-score strategy is now evaluated per week (weeks 1, 2, 3–4, 5–8;
under-covered share, MACD, P10), and the main table has a week-1 column. The title no longer says "first days".
The abstract, introduction and conclusions state that no strategy repairs week-1 under-coverage. Result: week-1 under-covered share on BDG2 is 24.2 % (CQR), 19.4 % (PCS-CQR) and 33.8 % (Self-CQR), against a sampling floor of 1.7 %. Only coverage-only ACI reaches 8.9 %, with 2.4× wider intervals.

## B. Major

**B1 — Statistics.** All implemented in `src/statistics/analysis.py`:
- BDG2 uses an exact site-cluster sign-flip randomisation test (1024 patterns, p ≥ 0.002) as the primary test,
  with a site-cluster bootstrap for the CIs of the mean and median paired differences. UCI resamples clients.
- The Holm families are defined explicitly: proposed method × protocol × condition × α × metric.
- The tested metrics include the under-covered indicator and the booking-failure indicator.
- LOSO, cross-dataset, disjoint-period, robustness and small-pool comparisons all have tests and seed s.d.
- Building-level Wilcoxon tests are secondary.
- The error analysis is at building level, and its Mann–Whitney test is reported only when n ≥ 10.
- The sentences that contradicted the stored tests were removed, because all text numbers are now generated by
  `manuscript/values.py`.

**B2 — ACI was handicapped.** Accepted. The 500·s cap was replaced by the split-conformal level
⌈(1−α_h)(N+1)⌉/N with a finite fallback (the largest calibration score). The γ grid includes 0. ACI is also tuned
with the reliability-aware rule, and a coverage-only ACI shows what unconstrained coverage-targeting costs.
"ACI adapts slowly" was removed. Result: ACI-CQR (IS) 8.7 %, ACI-CQR (MACD) 4.2 %, ACI-CQR (coverage only) 0.0 % under-covered on BDG2. The last has intervals 2.4× (BDG2) / 1.2× (UCI) as wide as PCS-CQR and a reserve cost of 4.4 % vs 2.1 % of mean load. It always selected the largest γ in the grid (0.01), which the text states.

**B3 — "Most reliable" not supported everywhere; mechanism confounded with tuning.** Accepted:
- Shrinkage strategies (PCS, QShrink) are presented as a near-equivalent family, compared at matched fixed
  pseudo-counts (168) and under the same tuning rule.
- LOSO is now 10 sites × 3 seeds, with a per-site table and a site-balanced summary.
- A conditions table (MS_conditions) shows the under-covered share of every strategy in every protocol and stress
  test, so the best strategy per condition is visible.

Result: QShrink-CQR (MACD) is statistically indistinguishable from PCS-CQR in coverage (BDG2 p = 0.60). LOSO: PCS-CQR 2.4 % vs Self-CQR 7.1 % (p = 0.023) and CQR 24.8 %, below 5 % at every site. The text names the conditions where Self-CQR is as good or better (meter noise in history and truth, early level shift, volatility increase) and the condition where everything fails (volatility increase: ≥ 76 % under-covered for all strategies).

**B4 — Energy-application payoff.** We added two operational metrics computed from the stored intervals and
interpreted as a capacity reservation sized by the upper bound (demand-response baseline or flexibility
commitment):
- booking failures: buildings whose exceedance rate is above α;
- reserve cost: pinball loss of U at level 1−α/2, relative to mean load.

Both are reported in the main tables and tested. We did not build a full market case study; Section 6 discusses
this. Result: booking failures fall from 7.3 % (CQR) to 2.1 % (PCS-CQR) on BDG2 (not significant after Holm with 10 sites, p = 0.070). Reserve cost is unchanged at 2.1 %, while coverage-only ACI costs 4.4 %.

**B5 — Data handling.**
- The evaluation truth is no longer cleaned or interpolated: only hours with an actual observation are scored, via
  an obs mask stored with the data cube.
- UCI daylight-saving artefacts are masked.
- Weather interpolation is limited to 6 h, and only inside the series.
- Timestamps were checked: BDG2 weather is in local time, and the mean diurnal temperature peaks at 14–16 h at
  every site.
- An exclusion-flow table is generated (`data/processed/*_exclusion.json`, used in Section 4.1).
- The site count is corrected to 10.
- Data checksums are pinned in `experiments/data_checksums.txt`.

The quality filter still uses target-year completeness. We did not rerun with a causal filter, because a forecast
cannot be evaluated where truth is missing. The limitations section explains how this excludes very poorly metered
buildings.

**B6 — Length.** Main text cut to ≈8,400 (including the abstract; excluding tables and references) words and 7 (4 figures, 3 tables) display items. The full tables, extra figures and
method details (Supplementary Section S2) moved to the supplement.

**B7 — Literature.**
- Preprints and software records are labelled in the reference list.
- [29] (Jeon 2026, analysis-code record) is described as such, together with what it implements and the fact that
  no results from it are published.
- Ristovska 2026, Hao 2026 and Shi 2026 were re-verified via Crossref (`literature/citation_audit_r1.md`).
- Added Jin et al. 2022, Wang & Hyndman (AcMCP) and Bühlmann 1967, plus a note that BuildingsBench uses the same
  two datasets.
- Contribution 1 was reworded: per-unit evaluation is credited to TQA, Shahid et al. and Rafe & Das. Our
  contribution is its application to building onboarding over time since metering.
- Prior findings are discussed in Section 6.

**B8 — Robustness design.**
- Added stress tests: history-only noise with clean truth, contiguous 3- and 7-day outages, an early (day-7) level
  shift and a volatility increase.
- Post-change weeks are reported separately (w58).
- The CQR family is now also run at α = 0.05 and 0.2.
- Claims are restricted to 56 days after metering.

## C. Moderate / minor
- Wording:
  - The DP motivation is now called a heuristic with a conformal-style correction.
  - The text states explicitly that own scores are not stage-matched.
  - The κ-limit and the score-specificity of stage matching are discussed.
  - TQA-B no longer uses target information.
  - κ=0 is selectable, with the pooled fallback.
  - The γ=0 ≡ pooled equivalence is now true by construction and covered by a unit test.
- Cost:
  - Timings for every strategy (`info.t_method`).
  - Single-building daily-update latency (`results/latency.json`).
  - Medians are reported.
  - Memory per building is stated.
- Leakage tests were extended to h ∈ {1, 7, 14, 28, 56}, including temperature and the descriptor, plus a test that
  the PCS radius uses only past own scores (15 unit tests, all passing).
- The overlap between the calibration period and the training period is tested by the disjoint-period protocol.
  Result: with a disjoint calibration period, PCS-CQR has 1.8 % under-covered vs 18.4 % for CQR, the same pattern as in the main protocol.
- AI use is described under "Research software" (Section 4) and in the declaration.
- Fig 11 (examples) moved to the supplement. Width and P90 relative width are reported. The PyTorch citation was added, and the DeepAR
  attribution and arXiv versions were checked.


## 3c. Deviations from the analysis plan

# Deviations from the analysis plan (Supplementary Table S1)

The analysis plan (experiments/PREREGISTRATION.md, committed 2026-11-15 12:59 UTC in e9ca94d) is an internal,
version-controlled file, not an external registration. Every change after it is listed below. "Target results
seen" says whether results on target buildings (from any run) were available when the change was decided.

| # | Date (UTC) | Change | Reason | Target results seen? |
|---|---|---|---|---|
| 1 | 2026-11-15 | Stuck-meter rule widened to any run of ≥ 24 identical readings; training rows with normalised target > 20 excluded from model fitting | Smoke test (reduced data) showed errors ~80× too large from flat-lined meters at one site | Yes (smoke test, 15 % of training rows) |
| 2 | 2026-11-15 | Self-CQR and ACI-CQR added; HSC-CQR component ablations added | Quick-mode check: self-only calibration a strong competitor; fair test of HSC-CQR needs same-score competitors | Yes (quick mode) |
| 3 | 2026-11-15 | Evaluation on the common set of hours with observed truth and finite intervals | Bug: hours without any possible forecast were counted as misses | No (bug found in code; all results recomputed) |
| 4 | 2026-11-16 | GHCP-CQR, TQA-B-CQR, QShrink-CQR added | Prior-art audit identified these as the closest published mechanisms | Yes (interim full-run results) |
| 5 | 2026-11-16 | "Simple" variants (uniform prior, no stage matching), fixed-κ = 168 h variant, MLP-CQR check added | Interim ablation showed no benefit of the similarity prior or stage matching | Yes |
| 6 | 2026-11-16 | ACI γ grid extended by {0, 1e-4, 2e-4} | Lower grid edge selected in 7 of 10 runs | Yes (selected γ only) |
| 7 | 2026-11-16 | Code-audit fixes (NaN-safe neighbour search, empty-bin prior, grid range, ACI empty-set convention, TQA-B λ-scaling, QShrink grid) | Independent code audit | Yes (all results recomputed) |
| 8 | 2026-11-20 | Recommended layer changed from HSC-CQR (similarity prior + stage matching, κ by LOBO interval score) to PCS-CQR (uniform prior, no stage matching, κ by the reliability-aware LOBO rule) | Review cycle 1: the refinements added nothing and the pre-registered interval-score objective is nearly flat in κ and selected a less reliable κ than a fixed one-week value | Yes (complete v1 results) |
| 9 | 2026-11-20 | Reliability-aware LOBO rule (minimum coverage deviation among parameter values within 2 % of the best LOBO interval score) applied to PCS, QShrink and ACI; unconstrained coverage-only ACI added as reference | Same as 8; applied to all tuned competitors for fairness | Yes |
| 10 | 2026-11-20 | ACI: split-conformal level ⌈(1−α_h)(N+1)⌉/N and finite fallback (largest calibration score) instead of a 500·s radius when α_h ≤ 1/(N+1) | Review: the cap dominated the tuning objective and handicapped ACI | Yes |
| 11 | 2026-11-20 | TQA-B budget scaling from the largest attainable rank instead of the maximum over target buildings; κ = 0 with pooled fallback in the grid | Review: target information used in TQA-B; κ = 0 previously unselectable | Yes |
| 12 | 2026-11-20 | Only actually observed hours are scored (interpolated/masked hours used as inputs only); UCI daylight-saving artefacts masked; weather interpolation limited to 6 h | Review (data and leakage) | Yes |
| 13 | 2026-11-20 | Leave-site-out with 5 site groups and one seed replaced by leave-one-site-out (10 sites × 3 seeds) | Review: site-dependent results, single training run per fold | Yes |
| 14 | 2026-11-20 | Added: disjoint calibration period; history-only noise, contiguous outages, early level shift, volatility increase; small calibration pools (5–40 buildings, 5 draws); CQR-score strategies at 80 % and 95 % | Review (robustness, experimental design) | Yes |
| 15 | 2026-11-20 | Inference: site-level sign-flip randomisation tests (BDG2) instead of building-level Wilcoxon as primary; tests of the under-covered share and booking failures; per-week metrics; operational metrics | Review (statistics): building-level tests ignore clustering in 10 sites | Yes |
| 16 | 2026-11-20 | Headline metric: share of under-covered buildings (an RQ1 metric in the plan) reported first; the planned primary endpoints (interval score and |coverage − 0.9|) are tested and reported for every comparison | The paper's question is per-building reliability; the interval score barely separates strategies | Yes |

Consequences: results for PCS-CQR, the reliability-aware rule and the protocols added in revision are exploratory.
The planned primary comparison (HSC, absolute score, against the planned baselines) is reported in full in the
supplementary tests table (family "preregistered-abs"); its hypothesis is only partly supported (HSC has a lower interval
score than every planned baseline, including self-only calibration, but does not reduce per-building miscalibration
relative to self-only calibration).


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

## Cycle 1 (2026-11-20) — consolidated in REVIEW/review_01.md
Recommendations: 9 Major revision, 1 Minor revision. Top issues: fixed kappa=168 beats LOBO-tuned headline
method (A1); headline numbers from the full kNN/stage variant the paper calls unnecessary (A2); pre-registration
overstated, deviations undisclosed (A3); no week-1 gain (A4); site-clustered inference, ACI cap handicap,
'most reliable' outside main protocol, no operational payoff, data-filter/cleaning issues, length, literature.
Status: addressed in revision 1 (2026-11-21); point-by-point response in REVIEW/response_01.md. Method re-centred
on PCS-CQR with reliability-aware tuning (fixed kappa=168 reported everywhere); deviations table (Supp. Table S1);
week-wise metrics with explicit 'no week-1 repair' claim; site sign-flip tests; ACI fallback fix; LOSO 10x3,
disjoint period, new stress tests, small pools, 80/95 %; operational metrics; observed-hour scoring; ~8.4k words.
Not done: causal (training-period-only) quality filter (discussed as a limitation); full market case study.
