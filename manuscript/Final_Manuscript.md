---
title: "Reliable day-ahead load intervals for newly metered buildings: shrinkage conformal calibration evaluated building by building"
---

**Authors:** P N Bhargav Teja^a,\*^, [Second Author]^b^

^a^ [Department, Institution, City, Country] · ^b^ [Department, Institution, City, Country]

\* Corresponding author: P N Bhargav Teja. E-mail: [corresponding author e-mail]

# Highlights

- Pooled conformal intervals leave many newly metered buildings under-covered
- Shrinkage toward each building's own scores removes most of this excess
- Under-covered buildings fall from 15.2% to 0.2% at equivalent interval score
- First-week reliability reaches the level of a perfectly calibrated building
- Weekly coverage stays noisy; tested on 1,358 buildings and clients

# Abstract

Demand response, flexibility offers and measurement-and-verification need day-ahead load intervals for individual buildings, often from the first days after a building is metered. Interval methods are usually judged by coverage pooled over many buildings, which can hide buildings whose intervals are systematically too narrow. We evaluate how calibration strategies serve newly metered buildings one by one, under a building- and period-disjoint protocol on 1,042 buildings at 14 sites (Building Data Genome 2) and 316 Portuguese electricity clients. Pooled, self-only, adaptive, temporal, hierarchical and shrinkage conformal calibration are applied to the same quantile forecasts and tuned by one leave-one-building-out rule. Pooled conformalised quantile regression left 15.2% (BDG2) and 12.3% (UCI) of new buildings with coverage more than five points below the 90 % target over their first eight weeks. Shrinking each building's calibration toward its own recency-weighted scores reduced these shares to 0.2% and 0.0% at an equivalent median interval score, and brought first-week under-coverage to the level of a perfectly calibrated building (16.6% versus 22.0% for the pooled baseline on BDG2). Quantile shrinkage performed almost as well; online level control matched it only in a narrow parameter band. Gains held on unseen sites, after cross-country transfer and under fourteen stress conditions. Weekly coverage of single buildings remained noisy for every strategy. In day-ahead capacity-headroom offers, shrinkage left average cost unchanged but removed most systematically under-protected buildings, at 0.037 ms per building-day.

**Keywords:** probabilistic load forecasting; conformal prediction; cold start; building energy; demand response; prediction intervals


# 1. Introduction

## 1.1 Background and motivation

Buildings account for a large share of electricity demand, and their flexible loads are increasingly enrolled in demand response, flexibility markets and on-site renewable integration [1]. These applications act on day-ahead statements of the form "tomorrow's hourly load of *this* building will lie between $L$ and $U$ with probability $1-\alpha$". Demand-response baselines and their settlement, day-ahead capacity and flexibility offers, measurement and verification [2] and anomaly alarms all depend on such intervals. Probabilistic load forecasting has therefore become a central topic in energy forecasting [3,4], and recent studies in this journal have developed expressive probabilistic models for loads, renewables and multi-energy systems [5–7].

Intervals are needed most when a building has just been connected to a monitoring, aggregation or demand-response platform, which is exactly when the least building-specific data exist. Aggregators onboard buildings continuously, and an interval that is too narrow for an individual building exposes the operator to penalties and false alarms for that building, regardless of how well the intervals perform on average over the portfolio. Two properties are therefore required at the same time. The intervals must be *reliable building by building*, not only on average, and they must be reliable *from the first days* after metering starts, without months of building-specific history.

## 1.2 Related work

*Forecasting with little building-specific data.* Data-driven building forecasting traditionally needs months to years of history per building [8]. Transfer learning, federated learning and global or pretrained models now provide useful point forecasts for buildings with little history [9–13], and large pretrained models report zero-shot probabilistic forecasts for unseen buildings [14]. A recent cross-building study found that split-conformal intervals under-cover unseen buildings on average and recommended recalibration before deployment [15]. These studies evaluate point accuracy or *pooled* interval metrics; whether the intervals are reliable for *each* new building, and from which day on, has not been examined.

*Conformal calibration in energy forecasting.* Conformal prediction gives distribution-free intervals around any forecaster [16–18], with conformalised quantile regression (CQR) as a strong default [19]. It is increasingly used for loads, prices and renewables, for example in day-ahead and intraday power markets [20], with adaptive conformal inference (ACI) [21], local online conformal prediction for power-load intervals [22] and context-aware calibration for renewable forecasts [23]. Its guarantee is *marginal*: averaged over exchangeable test points. For a fleet of new buildings, a marginal guarantee is compatible with intervals that are much too narrow for volatile buildings and too wide for regular ones, while pooled coverage looks perfect. An early comparison of interval methods across load profiles already observed that reliability differs between profiles [24].

*Unit-level and temporal calibration.* The statistics literature offers several remedies, each developed under different assumptions. Group-wise (Mondrian) calibration [16] needs enough calibration data per group, and conditional or class-conditional calibration targets pre-specified groups [25,26]. Online methods adapt the miscoverage level or the quantile of a single series, such as ACI and its aggregated, dynamically tuned and strongly adaptive variants [27–30] and conformal PID control [31], or weight recent scores more heavily under drift, such as non-exchangeable conformal prediction [32]. For panels of series, temporal quantile adjustment (TQA) targets per-series (longitudinal) coverage and shows that distribution-free longitudinal validity is impossible in general [33,34]. Several lines address *new units* directly. Few-shot conformal prediction borrows calibration from exchangeable auxiliary tasks for a new task with few labels [35]; hierarchical conformal prediction gives coverage for a *new group* drawn from the same population [36,37]; generalised hierarchical conformal prediction (GHCP) uses a new group's first observations [38]; federated conformal prediction pools calibration across clients [39]; and small-area conformal prediction borrows strength across areas while keeping area-conditional coverage [40,41]. Posterior conformal prediction adapts to clusters of units with similar score distributions [42], and group-weighted and macro-coverage conformal prediction target coverage averaged over groups rather than hours [43,44], which is the building-weighted population distribution used below. Credibility-type shrinkage of a unit's own calibration towards a pooled one, the classical credibility form [45–48], has recently been proposed for federated sites, with the pseudo-count selected by leave-one-site-out on per-site violations [49], for survey subgroups [50] as a Bayesian prior in online quantile tracking for a single series [51] and as a cold-start prior whose weight decays over time [52]; a donor–local score mixture for newly commissioned solar stations is available as a software record [53].

## 1.3 Research gaps and contributions

Three gaps follow from this literature.

1. **No building-level evaluation of interval reliability during onboarding.** Energy studies report pooled coverage; how many newly metered buildings receive unreliable intervals, in which weeks and with which operational consequences, is unknown.
2. **No evidence on which calibration mechanism suits onboarding.** The candidate mechanisms (online level control, temporal quantile adjustment, hierarchical pooling, quantile- or score-level shrinkage) have been developed for different settings (single series, exchangeable groups, federated sites) and have not been compared on the same forecaster, scores and protocol for a population of new buildings whose forecast errors change as their history grows.
3. **No evidence on the attainable reliability–sharpness trade-off over time.** It is unknown how far per-building reliability can be improved without wider intervals, in the first week versus later weeks, and how much of the remaining weekly under-coverage is sampling noise.

This study addresses these gaps with the following contributions.

1. **Evaluation framework for onboarding.** We operationalise *per-building interval reliability during onboarding*, with outcome measures that operators can act on: the share of under-covered buildings over the onboarding window, in each week and in the worst week, a method-independent sampling-noise reference for these shares that respects day-to-day dependence, and the share of buildings whose upper bound is exceeded twice as often as stated. We evaluate them under a building- and period-disjoint protocol on two public datasets with 1,358 buildings and clients, with leave-site-out and cross-country transfer and stress tests.
2. **A head-to-head comparison under one tuning rule.** Under one protocol, forecaster and score, we compare pooled split conformal and CQR, Mondrian, self-only, ACI, TQA, GHCP-style pooling, quantile shrinkage and score shrinkage, with and without recency weighting of the building's own scores. Every parametrised strategy is tuned by the same leave-one-building-out rule on calibration buildings (per-building coverage subject to a sharpness constraint), and the recommended configuration is chosen by a nested rule that never ranks on the evaluation set it is reported on.
3. **The reliability–sharpness frontier.** We map every strategy over its full parameter range at three nominal levels to show which ones are reliable without loss of sharpness, in which weeks, and with which tail behaviour. The calibration layer we recommend adapts known components (credibility shrinkage of score distributions, recency weights, a pseudo-count tuned for per-unit coverage [49]) to onboarding; it is closed-form and runs on top of any interval forecaster.
4. **Operational and weekly evidence.** We quantify the effect on day-ahead capacity-headroom offers, show how much of the weekly under-coverage of single buildings remains after calibration relative to an oracle reference, and identify which design elements matter, including two that do not (building-similarity priors and onboarding-stage matching) and one that fails in the tails (studentising scores by a running scale estimate).

The rest of the paper presents the methodology (Section 2), the data and experimental design (Section 3), the results (Section 4) and their implications and limitations (Section 5). Section 6 concludes.


# 2. Methodology

## 2.1 Problem setting and notation

Let $y_{b,t,j}\ge 0$ denote the metered electricity use (kWh) of building $b$ on day $t$ and hour $j\in\{0,\dots,23\}$. Building $b$ is metered from day $t_{0,b}$ onward. At the end of day $t_{0,b}+h-1$, after $h$ days of the building's own history have been observed, a day-ahead forecast is issued for the 24 hours of day $t=t_{0,b}+h$; we call $h$ the *onboarding stage*. We assume that all 24 hours of day $t-1$ are observed when the forecast is issued; because day-ahead nominations usually close around noon of $t-1$ and meter data may arrive late, a variant in which the building's own scores reach the calibration layer one day later is also evaluated (Section 3.6). For a miscoverage level $\alpha$ (main analysis: $\alpha=0.1$), the goal is an interval $C_{b,h,j}=[L_{b,h,j},U_{b,h,j}]$ such that, **for every individual building**, the share of hours with $y_{b,t,j}\in C_{b,h,j}$ is close to $1-\alpha$ from the first days after metering starts, while the intervals remain as narrow as possible. The empirical target is therefore the distribution of per-building coverage across buildings, not only its mean.

Three disjoint sets of buildings are available (Section 3): *training* buildings for the global forecaster, *calibration* buildings whose (simulated) onboarding windows provide nonconformity scores, and *target* buildings, which are metered in a later period and on which all methods are evaluated.

## 2.2 Scale-normalised global forecaster

Buildings differ in mean load by four orders of magnitude (Fig. 2). Every load-derived quantity is therefore expressed relative to the scale

$$
s_{b,h}=\frac{1}{24\,m_h}\sum_{k=1}^{m_h}\sum_{j=0}^{23} y_{b,\,t-k,\,j},\qquad m_h=\min(h,7),\qquad\qquad (1)
$$

which uses only the last $m_h$ observed days. A single model $f$ is trained on the training buildings to predict $y_{b,t,j}/s_{b,h}$ from calendar variables, the normalised loads of the previous 1, 2, 7 and 14 days (missing if $h$ is smaller), normalised daily statistics and hour-of-day/day-type profiles computed over at most the last 28 observed days, the day-to-day variability of the normalised profile, the history length $\min(h,28)$, and, for BDG2, outdoor air temperature (Supplementary Table S1). During training, the history length of every sample is drawn uniformly from $\{1,\dots,28\}$ and all features are masked accordingly, so the model learns to forecast from short histories. The point forecast is $\hat y_{b,t,j}=s_{b,h}\,f(\mathbf x_{b,t,j})$; quantile models $f^{\mathrm{lo}},f^{\mathrm{hi}}$ (levels $\alpha/2$ and $1-\alpha/2$) are trained in the same way with the pinball loss [54].

## 2.3 Nonconformity scores

We use two normalised scores: the absolute residual and the conformalised-quantile-regression (CQR) score [19]:

$$
e^{\mathrm{abs}}_{b,h,j}=\frac{|y_{b,t,j}-\hat y_{b,t,j}|}{s_{b,h}},\qquad
e^{\mathrm{cqr}}_{b,h,j}=\frac{\max\{\hat y^{\mathrm{lo}}_{b,t,j}-y_{b,t,j},\; y_{b,t,j}-\hat y^{\mathrm{hi}}_{b,t,j}\}}{s_{b,h}} .\qquad\qquad (2)
$$

Given a radius $q_{b,h}$ (in units of $s_{b,h}$), the interval is

$$
C_{b,h,j}=\big[\hat y^{\mathrm{lo}}_{b,t,j}-q_{b,h}\,s_{b,h},\;\hat y^{\mathrm{hi}}_{b,t,j}+q_{b,h}\,s_{b,h}\big],\qquad\qquad (3)
$$

with $\hat y^{\mathrm{lo}}=\hat y^{\mathrm{hi}}=\hat y$ for the absolute score. Division by $s_{b,h}$ is what makes scores from buildings of different size comparable and therefore poolable.

## 2.4 Recency-weighted shrinkage conformal calibration

Fig. 1 summarises the calibration layer. Split conformal prediction [16,17] sets $q$ to the $\lceil(1-\alpha)(N+1)\rceil$-th smallest of $N$ pooled calibration scores. This is valid on average over exchangeable test points but cannot adapt to an individual building whose errors are systematically larger or smaller than average, which is precisely the situation of a newly metered building. Calibration on the building's own scores alone removes this bias but replaces it with variance: with a few dozen hourly scores, an empirical 90 % quantile is a noisy estimate. The layer trades the two off explicitly.

![**Fig. 1.** Calibration layer for newly metered buildings. A global forecaster is trained on scale-normalised loads of training buildings. Calibration buildings, onboarded in the training period, provide CQR nonconformity scores that form the population score distribution. For a new building, the population distribution is mixed with the building's own past scores, which are down-weighted with their age (factor ρ per day), through a pseudo-count κ selected by leave-one-building-out on the per-building coverage of calibration buildings.](figures/Fig1_method.png){width=16.5cm}

**Population score distribution.** Let $\hat F_c$ be the empirical distribution function of the scores of calibration building $c$ over its onboarding window. The population distribution is the building-weighted average $F^{\mathrm{pop}}(e)=\frac1M\sum_{c=1}^{M}\hat F_c(e)$ over the $M$ calibration buildings, so that every building, not every hour, counts equally.

**Recency-weighted shrinkage.** When the stage-$h$ forecast is issued, the building's own scores from stages $1,\dots,h-1$ are known. A score observed on stage $h'$ receives the weight $w_{h,h'}=\rho^{\,h-1-h'}$, so the most recent day has weight one and older days are down-weighted by a factor $\rho$ per day. With $n^{\rho}_{b,h}=\sum_{i}w_{h,h'(i)}$ the effective number of own scores, the layer uses the mixture distribution

$$
\tilde F_{b,h}(e)=\frac{\kappa\,F^{\mathrm{pop}}(e)+\sum_{i}w_{h,h'(i)}\,\mathbb 1\{e_{b,i}\le e\}}{\kappa+n^{\rho}_{b,h}+1},\qquad
q_{b,h}=\inf\{e:\tilde F_{b,h}(e)\ge 1-\alpha\},\qquad\qquad (4)
$$

where the "+1" is a point mass at $+\infty$ that represents the not-yet-observed test score, as in weighted split conformal prediction [32,55]. With $\rho=1$, the building's own scores receive the weight $n_{b,h}/(\kappa+n_{b,h}+1)$. This is the classical credibility form of experience rating [45] and of empirical-Bayes shrinkage [46]; it has been linked to conformal prediction [48] and recently used to shrink site- or group-specific conformal calibration towards a pooled one, with the pseudo-count chosen by leave-one-site-out on per-site violations [49] or fixed [50]; a donor–local score mixture for new solar stations is implemented in a software record (cf. [53]). For $\rho=1$ and without the point mass, the mixture is also the posterior mean of the building's score distribution under a Dirichlet-process prior with base measure $F^{\mathrm{pop}}$ and concentration $\kappa$ [56]; with $\rho<1$ this reading no longer holds. The layer is therefore an adaptation of known components, and what this study contributes is its evaluation for onboarding (Section 1). As $\kappa\to\infty$ the radius becomes the split-conformal quantile of the building-weighted, stage-agnostic population distribution, which differs from the score-weighted, stage-matched CQR baseline (both are reported); $\kappa=0$ gives split conformal prediction on the building's own scores, which is undefined until enough own scores exist. The pseudo-count has a direct operational reading: it is the number of hourly own scores that the population is worth.

Recency weighting ($\rho<1$) is motivated by onboarding itself. Errors in the first days are produced by a forecaster that has seen almost no history of the building, and newly enrolled buildings can change their operation after enrolment. Old own scores then describe a building that no longer exists, and they are down-weighted in the same spirit as non-exchangeable conformal prediction [32]. Because each day adds up to 24 hourly scores, the effective sample size is bounded by $n^{\rho}_{b,h}\le 24/(1-\rho)=480$ hourly scores for $\rho=0.95$, so the population distribution keeps a minimum weight $\kappa/(\kappa+480+1)$ (for example 9 % at $\kappa=48$ h). The decay factor $\rho=0.95$ per day (half-life ≈ 13.5 days) was fixed in the protocol addendum, which was written after a pilot evaluation and before the final runs (Section 3.6); it was not tuned, and Section 4.4 shows that other values ($\rho\in\{0.8,0.9,1\}$) lie at different points of the same frontier.

**Selection of the pseudo-count.** $\kappa$ is selected on the calibration buildings only, by leave-one-building-out (LOBO): each calibration building in turn plays the role of a new building, with the population distribution built from the remaining calibration buildings. Following the leave-one-unit-out principle of [49], the objective is the target property: the mean absolute deviation of the per-building coverage from $1-\alpha$ over the onboarding window (LOBO-MACD). Because this objective alone rewards forcing coverage at any cost in width, it is minimised subject to a sharpness constraint: the LOBO interval score (Eq. (6)) may exceed that of the family's pooled limit ($\kappa=\infty$) by at most 2 %; if no value qualifies, the sharpest value is taken. The grid is $\kappa\in\{0,6,12,24,48,96,168,336,672,1344,\infty\}$ hours, and selections at the grid edges are reported. Exactly the same constrained objective tunes every parametrised competitor (quantile shrinkage $\lambda$, ACI step size $\gamma$; Section 3.6). The original protocol selected $\kappa$ by the interval score; that variant is reported as well. Target buildings are never used for any choice.

**Examined refinements.** Three further elements were tested and are reported as variants (Section 4.5). The first two are *onboarding-stage matching* (the population distribution built from calibration scores at a similar onboarding stage, in bins $\{1\},\{2\},\{3\},\{4..6\},\{7..13\},\{14..27\},\{28..56\}$) and a *similarity-localised population distribution* (the $K$ calibration buildings closest to the new building in a load-shape descriptor; Supplementary Section S2). The third is *stage-wise studentisation*. Each CQR score is divided by the building's running error-scale ratio

$$
r_{b,h}=\frac{\kappa_s\,\sigma_0+\sum_{h'<h}\sum_j a_{b,h',j}}{\sigma_0\,(\kappa_s+n_{b,h})},\qquad a_{b,h,j}=\frac{|y_{b,t,j}-\hat y_{b,t,j}|}{s_{b,h}},\qquad\qquad (5)
$$

with $\sigma_0$ the mean normalised absolute residual of the forecaster on the validation buildings (disjoint from calibration and target buildings, so that the studentised score is the same function of each building's data) and $\kappa_s=24$ fixed a priori. At each exact stage $h$ the radius is the $(1-\alpha)$ quantile of the mixture in which each calibration building contributes the empirical distribution of its studentised scores at stage $h$ with weight $1/(M+1)$ and the new building a point mass $1/(M+1)$ at $+\infty$. This is the hierarchical conformal prediction (HCP) weighting of Lee, Barber and Willett ([37], arXiv v4), applied per stage; the "pooling CDFs" rule of [36] is closely related but has only an asymptotic guarantee. The interval is $[\hat y^{\mathrm{lo}}-\tilde q_h r_{b,h}s_{b,h},\,\hat y^{\mathrm{hi}}+\tilde q_h r_{b,h}s_{b,h}]$ (SSC-CQR), and HSC-SSC-CQR applies the shrinkage of Eq. (4) to the studentised scores.

*Corollary 1 (of Theorem 1 in [37]; stage-wise validity across new buildings).* If the onboarding trajectories of the $M$ calibration buildings and of the new building are exchangeable and $\sigma_0$, $\kappa_s$ and the forecaster are fixed, then for every stage $h$, $\Pr\{y_{b,t,J}\in C_{b,h,J}\}\ge 1-\alpha$, where $J$ is an hour drawn uniformly from the new building's valid hours at stage $h$ and the probability is over buildings and $J$.

*Proof.* The studentised score is the same measurable function of each building's own trajectory up to stage $h$, so the $M+1$ vectors of stage-$h$ studentised scores are exchangeable across buildings. An independent uniform random permutation of the hours within each building makes them exchangeable within buildings as well, leaves the mixture unchanged and makes $J$ the first permuted hour. The data are then hierarchically exchangeable, and Theorem 1 of [37] gives coverage at least $1-\alpha$. ∎

The corollary concerns coverage on average over new buildings at each onboarding day. Its premise of exchangeability between calibration and target trajectories does not hold in the evaluated protocol, where target buildings are onboarded in a later period than calibration buildings, so it motivates SSC-CQR but gives no guarantee here; its stage-wise coverage is reported empirically (Supplementary Table S22). It does not concern individual buildings: distribution-free longitudinal validity for a single series under arbitrary dependence is impossible [34], whereas area-conditional validity is attainable when each unit has exchangeable data of its own, as in the small-area method of [40], which shrinks only the interval width; in onboarding, a building has too few own scores in its first week for such a construction.

**Validity of the shrinkage layer.** For a fixed $\kappa\in(0,\infty)$, Eq. (4) does not inherit the finite-sample guarantee of split conformal prediction: neither the building's own past scores nor the calibration scores are exchangeable with its future scores, because forecast quality changes with $h$ and loads are autocorrelated. The layer is a tunable interpolation between pooled and own-score calibration, and its reliability is assessed empirically below, including under distribution shift.

**Computation.** Score distributions are stored as cumulative counts on a fixed grid of 4000 asinh-spaced points between $-10$ and $500$ (in units of $s$; relative spacing ≈ 0.5 %). Mixture quantiles then reduce to a vectorised search; grid quantiles are rounded upwards for all methods alike, and whether an own-score quantile exists is decided from the number of own scores. Tuning holds one cumulative-count vector per calibration building and stage; deployment needs only the population vector and, per building, one decayed count vector (4000 numbers), updated once a day:

> **Daily update for building $b$** (cost linear in the grid size). (i) Bin the 24 new scores of day $h-1$ on the grid and accumulate them into counts $c$; (ii) state $\leftarrow\rho\cdot$state $+\,c$; (iii) $\tilde F\leftarrow(\kappa F^{\mathrm{pop}}+\text{state})/(\kappa+\text{state}_{\max}+1)$; (iv) $q_{b,h}\leftarrow$ first grid point with $\tilde F\ge 1-\alpha$; (v) issue Eq. (3).


# 3. Data and experimental design

## 3.1 Data

**BDG2.** The Building Data Genome Project 2 [57] provides two years (2016–2017) of hourly meter data from non-residential buildings on university and public campuses in North America and Europe, together with site weather and building metadata. It is the dataset of the ASHRAE Great Energy Predictor III competition [58]. We use the cleaned electricity meters, site air temperature and the primary-space-usage attribute.

**UCI.** The ElectricityLoadDiagrams20112014 dataset [59] contains 15-min consumption of 370 Portuguese electricity clients (2011–2014). We aggregate it to hourly energy and use 2012–2014, because most clients have no data in 2011. It has no weather or metadata and represents a different country, customer mix and metering infrastructure. We use it to test generality and transfer.

**Quality rules** (applied identically to all methods): runs of at least 24 identical consecutive readings (meter outage or stuck meter) are treated as missing, and no load value is imputed, so missing hours are excluded from features and metrics alike. On UCI, the two daylight-saving transition hours per year are masked. Eligibility is decided on the training and calibration period only, with no look-ahead: a building is retained if at most 5 % of its hours in that period are missing outside short gaps of at most 6 h and its mean load is at least 1 kWh/h. This leaves **1042 BDG2 buildings at 14 sites** and **316 UCI clients** (Fig. 2). A target building enters the evaluation if it has an onboarding window with at least 80 % valid hours; the few that do not are dropped and counted. Air temperature gaps of at most 6 h are interpolated. Training rows whose normalised target exceeds 20 (meter restarts after near-zero history) are excluded from model fitting only.

![**Fig. 2.** Data after the quality filter: (a) primary space usage of the BDG2 buildings; (b) distribution of mean hourly load of BDG2 buildings and UCI clients (log scale).](figures/Fig2_data.png){width=16.5cm}

## 3.2 Protocols and leakage control

*Random-building protocol (main).* For each of five pre-specified seeds, buildings are randomly partitioned into training (50 %, of which one tenth is held out as building-disjoint validation data for early stopping), calibration (20 %) and target (30 %) sets. The forecaster and all calibration scores use only the training period (BDG2: 2016; UCI: 2012–2013). Each calibration building is "onboarded" at a random date in the training period. Each target building is onboarded at a random date in the later period (BDG2: 2017; UCI: 2014), drawn among windows with at least 80 % valid hours. Every building is followed for 56 day-ahead forecasts ($h=1,\dots,56$). Features at stage $h$ use only the $h$ days after $t_{0,b}$ (verified by unit tests that perturb all data outside this window). Target buildings, their period and their data are therefore never seen by the forecaster, the calibration scores, or any hyper-parameter selection.

*Leave-site-out (BDG2).* The 14 sites are grouped into five folds of similar size. All buildings of a fold are targets; the remaining buildings are split 70/30 into training and calibration sets. This tests transfer to unseen campuses, climates and operators.

*Cross-dataset.* Models and calibration scores from one dataset are applied to the target buildings of the other (BDG2→UCI and UCI→BDG2), without weather features, which UCI lacks. A BDG2→BDG2 run without weather serves as the within-dataset reference (three seeds each).

*Stress tests (BDG2, three seeds).* Additive Gaussian meter noise with a standard deviation of 5 % or 15 % of the building's mean load (clipped at zero), random missing hours (20 % and 40 %) and abrupt level shifts of +40 % and −40 % at day 28 are applied to the new buildings' onboarding windows (history and truth). Calibration pools are reduced to 10 %, 25 % and 50 % of the calibration buildings, and a weak forecaster is trained on 10 % of the training buildings.

## 3.3 Compared methods

All conformal-type strategies use the same LightGBM quantile models, the same CQR scores (Eq. 2), the same score grid and the same calibration buildings; they differ only in how the radius $q_{b,h}$ is obtained. Every tuned parameter is selected by leave-one-building-out on calibration buildings, and the parameter grids are equally fine. Implementation details and deviations from the original methods are given in Supplementary Section S3.

* *Pooled:* **CQR** [19] (stage-matched pooled CQR scores); **SCP** and **SCP-stage** (split conformal on normalised absolute residuals [17], without and with stage matching); **Raw-SCP** (unnormalised residuals); **Mondrian-usage** (BDG2; per primary-usage class [16]); and **Naive+SCP** (seasonal-naive forecast).
* *Self-calibration:* **Self-CQR**, split conformal on the building's own past scores, falling back to pooled CQR until an own quantile exists.
* *Online level control:* **ACI-CQR** [27], $\alpha_{h+1}=\alpha_h+\gamma\sum_j(\alpha-\mathrm{err}_{h,j})$ on the pooled CQR distribution, with $\gamma\in\{0,10^{-4},2\cdot10^{-4},5\cdot10^{-4},10^{-3},2\cdot10^{-3},5\cdot10^{-3},10^{-2}\}$; a level $\alpha_h\le0$ is mapped to the largest observed calibration score.
* *Temporal and hierarchical pooling:* **TQA-B-CQR** [33] (budgeted temporal quantile adjustment; the budget scale is set from calibration buildings) and **GHCP-CQR** [38] (the new building receives the weight of one calibration building).
* *Shrinkage:* **QShrink-CQR**, quantile-level shrinkage $q=w\,q^{\mathrm{own}}+(1-w)\,q^{\mathrm{pool}}$ with $w=n_{b,h}/(n_{b,h}+\lambda)$ ("regularised Mondrian" [50]); **HSC-CQR fixed-κ**, score shrinkage with a fixed pseudo-count of one week ($\kappa=168$ h), i.e. a donor–local mixture as in [53]; **QShrink-CQR recency** and **Self-CQR recency** (quantile shrinkage and self-calibration with the same recency weights as the layer; Self-CQR recency falls back to pooled CQR until the weighted own quantile is defined); and the proposed **HSC-CQR recency** (Eq. 4).
* *Variants of the layer (Section 4.5):* **HSC-CQR simple** ($\rho=1$, $\kappa$ by the interval score), **HSC-CQR simple (cov)** ($\rho=1$, $\kappa$ by the coverage objective), **HSC-CQR** (with stage matching and similarity-localised distribution), **HSC-CQR -shrink** ($\kappa=\infty$), **SSC-CQR** and **HSC-SSC-CQR** (Eq. 5).
* *Direct probabilistic models:* **QR-LGBM** (LightGBM quantile regression [54,60]), **MLP-QR** (a 256-256-128 multilayer perceptron with pinball loss [61]) and **MLP-Gauss** (the same network with a Gaussian likelihood, in the spirit of [62]); **CQR (MLP)** and **HSC-CQR (MLP)** apply the calibration to the MLP quantiles.

For fairness, ACI-CQR and QShrink-CQR are run both with the interval-score objective and with the coverage objective used for the proposed layer (suffix "(cov)"). All strategies are additionally evaluated over their full parameter grids on the target buildings (for transparency only, never for selection; Section 4.4). LightGBM (63 leaves, learning rate 0.05, at least 200 samples per leaf, 0.8 feature and bagging fractions, L2 regularisation 1) and the MLPs (Adam, learning rate $10^{-3}$, batch 4096, at most 12 epochs) use early stopping on building-disjoint validation buildings. These are conventional settings, identical for all calibration strategies.

## 3.4 Outcome measures

For target building $b$ with valid hourly observations over its 56-day window, we compute coverage $\mathrm{cov}_b$, relative width $\overline{U-L}/\bar y_b$ and the relative interval (Winkler) score [63,64]

$$
\mathrm{IS}_b=\frac{1}{\bar y_b}\,\overline{(U-L)+\tfrac{2}{\alpha}(L-y)_+ +\tfrac{2}{\alpha}(y-U)_+},\qquad\qquad (6)
$$

a proper score that rewards narrow intervals and penalises misses in proportion to their size.

*Reliability.* The primary reliability outcome is the **under-covered share**: the share of buildings with $\mathrm{cov}_b<1-\alpha-0.05$ (for 90 % intervals, coverage below 0.85), over the window and over the first week (days 1–7). We also report the 10th percentile of $\mathrm{cov}_b$ and the mean absolute coverage deviation $\mathrm{MACD}=\mathrm{mean}_b|\mathrm{cov}_b-(1-\alpha)|$. We also report the 10th percentile of $\mathrm{cov}_b$, the under-covered share in each week of weeks 2–8 (mean over weeks), and the share of buildings with at least one week below 0.80. Per-building coverage is itself an estimate, and misses are serially dependent. As a method-independent reference, we simulate for every building an *oracle* that is perfectly calibrated but has the observed dependence of misses: the building's daily miss indicators under pooled CQR are re-centred at $\alpha$ and resampled with a 7-day moving-block bootstrap over its valid days. The share of oracle buildings that fall below the threshold is the reference for each metric; excess over it is reported with a site-cluster bootstrap confidence interval (BDG2) or a building bootstrap (UCI).

*Sharpness.* The median and the mean over buildings of the relative interval score, and the 99th percentile and maximum of the width ratio to pooled CQR for the same building and seed (tails).

*Operational consequence.* Consider an operator that offers, for every building and hour, a day-ahead capacity headroom $\bar P-U$ below a contracted limit $\bar P$, for example to host flexible EV-charging or heat-pump load, and pays a penalty proportional to the violation $(y-U)_+$ whenever the realised load exceeds the planned upper bound $U$. Up to a constant, the relative cost of a building is

$$
\mathrm{cost}_b(\rho_p)=\frac{\overline{U}+\rho_p\,\overline{(y-U)_+}}{\bar y_b}.\qquad\qquad (7)
$$

The upper bound of a calibrated central 90 % interval is the cost-optimal plan for the penalty ratio $\rho_p=20$, because the optimal plan is the $(1-1/\rho_p)$ quantile. We report $\rho_p\in\{10,20,40\}$, and the share of **under-protected** buildings, whose upper bound is exceeded in more than 10 % of the hours (twice the nominal 5 %).

## 3.5 Statistical analysis

The unit of analysis is the target building; a building's metrics are averaged over the seeds in which it was a target. One confirmatory family was declared: the recommended configuration against pooled CQR, QShrink-CQR (cov), ACI-CQR (cov) and Self-CQR, on the under-covered share over the window and in the first week and on the relative interval score, on both datasets (24 comparisons, Holm-adjusted [65]). Differences in under-covered shares are tested with paired McNemar tests and reported with 95 % bootstrap confidence intervals that resample sites (BDG2) or buildings (UCI), because buildings at one site share weather and operation. Interval scores are compared by Wilcoxon signed-rank tests [66] on log ratios, with a two one-sided test (TOST) for equivalence within a 2 % margin. All other comparisons are exploratory and labelled as such. Standard deviations over seeds describe split variability, not estimation uncertainty.

## 3.6 Protocol, pre-registration and deviations

The splits, seeds, metrics, baselines and the interval-score tuning objective were fixed in an internal analysis protocol before any full experiment was run (released with the code). After a pilot evaluation, an addendum was written and committed to the repository *before* the corresponding experiments were run. It added the coverage objective (applied to the proposed layer, ACI and QShrink alike), recency weighting with $\rho=0.95$, stage-wise studentisation, the operational outcomes and the noise reference, and it fixed the rule for the recommended configuration. That rule selects the strategy with the lowest under-covered share, averaged over both datasets, among those whose median interval score is at most 2 % above that of pooled CQR on both datasets. Every parametrised strategy (pseudo-counts $\kappa$ and $\lambda$, ACI step size $\gamma$) is tuned by the same constrained leave-one-building-out rule on calibration buildings: minimise MACD subject to an interval score at most 2 % above that of pooled CQR, over grids that include $\kappa,\lambda\in\{6,12,\dots,1344\}$ h and $\gamma\le 0.05$; grid-edge selections are reported. To avoid ranking on the data the result is reported on, the recommended configuration is selected on BDG2 and confirmed on UCI, on unseen sites and in both cross-dataset directions (nested selection); bootstrap selection frequencies are reported. The decay factor $\rho=0.95$ was set in the addendum and not tuned. Two further variants address deployment questions: own scores used one day later (delay 1d; the forecast for day $h$ uses own scores up to day $h-2$, for gate closures before the end of day $h-1$), and a radius capped at the pooled 99 % score quantile (capped). Further deviations, for example the extension of the ACI grid after a code audit, are listed in Supplementary Section S4.


# 4. Results

All shares in this section use one unit, the building: a building's metrics are averaged over the seeds in which it was a target (0.2% thus means that this share of the 837 BDG2 target buildings is under-covered). "Under-covered" means coverage below 0.85 at the 90 % target. The *oracle reference* is the share expected for a building whose intervals are perfectly calibrated but whose misses have the observed day-to-day dependence (Section 3.6); it is the same for every method.

## 4.1 Pooled calibration leaves many new buildings unreliable

The global LightGBM forecaster reaches a median CV(RMSE) of 0.137 on new BDG2 buildings over their first 56 forecast days (seasonal naive: 0.199; MLP: 0.139) and 0.087 on UCI clients (naive 0.120; MLP 0.087). The question is whether the intervals of such a forecaster can be trusted building by building.

They cannot when calibration is pooled (Table 1). Conformalised quantile regression (CQR) leaves 15.2% of the BDG2 buildings and 12.3% of the UCI clients under-covered over the 56-day window, against an oracle reference of 1.9% and 0.6%. Its mean coverage is nevertheless close to nominal (0.895 on BDG2). Direct quantile regression with a neural network does not solve the problem (MLP-QR: 18.6% on BDG2), and the Gaussian MLP lowers it (3.3%) only by over-covering on average (0.938) at a median interval score of 0.643 instead of 0.557. Part of the pooled excess is a uniform level offset between the calibration period and the target period (+0.0047 in coverage on BDG2); removing it would lower the CQR share by only 1.4 percentage points, so most of the excess is genuine heterogeneity between buildings. Pooled under-coverage is concentrated in buildings that are hard to forecast (Spearman correlation of coverage with CV(RMSE): -0.60 on BDG2), and it is not a borderline effect: 14.2% of the BDG2 buildings miss the target by more than five points (Fig. 3).

**Table 1.** Per-building reliability and sharpness (random-building protocol, nominal 90 %; unit = building, metrics averaged over the seeds in which it is a target: 837 BDG2 buildings, 270 UCI clients). Under-cov.: share of buildings with coverage < 0.85 over the 56-day window, in the first week, and per week in weeks 2–8 (mean over weeks); Any wk < 0.80: share with at least one week below 0.80. Oracle reference: share expected for a building that is perfectly calibrated but has the observed serial dependence of misses (7-day moving-block bootstrap of miss indicators re-centred at 0.90; method-independent). Rel. IS: interval score divided by the building's mean load (median and mean over buildings). Width ratio: interval width relative to pooled CQR for the same building and seed (99th percentile / maximum). All strategies use the same LightGBM quantile models and CQR scores; '(cov)': parameter selected by the constrained leave-one-building-out objective; 'delay 1d': own scores used one day later.

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


![**Fig. 3.** Empirical distribution of per-building coverage over the 56-day onboarding window (all target buildings of all five seeds; dashed: nominal 0.90; dotted: 0.85).](figures/Fig4_coverage_cdf.png){width=16.5cm}

## 4.2 Building-adaptive calibration over the onboarding window

All strategies in Table 1 use the same quantile models and CQR scores; they differ only in how a new building's own scores enter the calibration, and every parametrised strategy was tuned by the same constrained leave-one-building-out rule on calibration buildings. The recommended configuration, recency-weighted score shrinkage (HSC-CQR recency), was chosen by the nested rule of Section 3.6 on BDG2 and ranked first in each confirmation setting (UCI, unseen sites, both cross-dataset directions); it was selected in 99.7% of bootstrap resamples of the selection.

Over the window, the layer leaves 0.2% of the BDG2 buildings and 0.0% of the UCI clients under-covered, below the oracle reference. In the confirmatory comparison with pooled CQR (Supplementary Table S16), the paired difference is -15.0 percentage points on BDG2 (95 % site-cluster bootstrap CI [-21.5, -9.0]; 238 buildings move from under-covered to covered, 1 the other way; Holm-adjusted p < 0.001) and -12.3 points on UCI (CI [-16.1, -8.6]). The median relative interval score is equivalent to pooled CQR's within a 2 % margin on both datasets (TOST; ratio +0.01%, CI [-0.09%, +0.08%] on BDG2).

The gain is a property of the *shrinkage family*, not of one member. Quantile shrinkage with recency (QShrink-CQR recency: 0.6% and 0.0%) and without it (QShrink-CQR (cov): 1.5% and 0.1%), score shrinkage without recency (1.1%) and with a fixed one-week pseudo-count (1.0%) all remove most of the pooled excess. Against QShrink-CQR (cov), the recommended layer is better over the window on BDG2 (-1.4 points, CI [-2.2, -0.5], p < 0.001) but not on UCI (p = 1.000), and the two are tied in the first week on both datasets. Online level control tuned by the same constrained rule (ACI-CQR (cov): 2.6% and 1.7%) and self-calibration with recency (Self-CQR recency: 1.7%) are close behind over the window. Strategies that never give the new building more weight than one reference building or bound their adjustment by design, GHCP-style pooling (14.3%) and temporal quantile adjustment (15.0%), stay close to pooled CQR: they secure validity across buildings but cannot correct a building whose errors are systematically larger than average.

The window gains survive a more conservative information set. With the building's own scores used one day later than in the main protocol (delay 1d, i.e. day $h$ uses scores up to day $h-2$), the layer leaves 0.4% (BDG2) and 0.1% (UCI) under-covered. They also hold for a different forecaster: on the MLP quantile models, the layer reduces the share from 12.8% to 0.5% (BDG2) and from 9.5% to 0.2% (UCI).

## 4.3 Weekly reliability: what the window metric hides

A window metric averages over eight weeks, and an operator who settles weekly sees something else (Fig. 4). In the first week, pooled CQR leaves 22.0% (BDG2) and 15.2% (UCI) of the buildings under-covered. The recommended layer reduces this to 16.6% and 7.0% (confirmatory differences -5.4 and -8.2 points, CIs [-8.0, -2.5] and [-12.2, -4.3]), which is at the oracle reference for one week of data (17.3% and 12.8%). Quantile shrinkage achieves the same first week (16.5%, 7.3%); online level control does not (20.9%, 14.5%), and self-calibration is worst (34.2% on BDG2) because a few dozen own scores give noisy quantiles.

From the second week on, the picture is less favourable for every strategy. On BDG2, 19.8% of the buildings are under-covered in an average week of weeks 2–8, against 23.6% with pooled CQR and an oracle reference of 17.3%. The excess over the reference is +2.5 points (CI [1.5, 3.3]) for the layer and +6.3 points for CQR. On UCI, the layer is at the reference (+0.4 points, CI [-0.7, 1.4]). Over eight weeks, 43.9% of the BDG2 buildings have at least one week below 0.80 (CQR 51.2%). Week-to-week coverage of a single building is inherently noisy: the oracle building itself has some week below 0.85 with probability 72.8%. The calibration layer therefore removes *systematic* per-building under-coverage, which is what the window metric measures, but weekly reliability on BDG2 remains a few points worse than ideal for all strategies studied.

![**Fig. 4.** Share of buildings whose coverage in a given week after metering started is below 0.85 (main protocol, five seeds). Dotted: oracle reference, i.e. the share expected for perfectly calibrated intervals with the observed serial dependence of misses (7-day moving-block bootstrap).](figures/Fig_weekly.png){width=16.5cm}

## 4.4 The reliability–sharpness frontier

Fig. 5 maps every strategy family over its full parameter grid on the target buildings. It serves transparency only; no selection was made on target buildings. Over the window (panels a, b), shrinkage with or without recency, quantile shrinkage and ACI at a suitable step size ($\gamma$ = 0.002: 0.3% on BDG2) all bring the under-covered share close to zero without loss of sharpness. Two differences remain. First, ACI does so only in a narrow band of step sizes: at $\gamma$ = 0.005 the median interval score rises by +27% on BDG2, at $\gamma$ = 0.01 by +258%, while the shrinkage families degrade gracefully over almost two orders of magnitude of $\kappa$. Second, in the first week (panels c, d), no ACI step size that preserves sharpness brings the BDG2 share below 20.9%, whereas score shrinkage reaches 15.5% at $\kappa$ = 48 h.

The first-week gain comes from a small pseudo-count, not from recency. At equal $\kappa$ = 48 h, the first-week share on BDG2 is 15.2% with recency ($\rho$ = 0.95) and 15.6% without it. Recency acts later in the window, where pre-change and early scores would otherwise dominate the building's own contribution: at $\kappa$ = 48 h, the window share is 0.1% with and 2.3% without recency. The decay factor was fixed at 0.95 per day and not tuned; $\rho$ = 0.8 lies on a slightly better point of the frontier (0.1% at $\kappa$ = 24 h). Leave-one-building-out selected $\kappa$ = 168, 48, 96 h on BDG2 and 24, 48 h on UCI across seeds.

![**Fig. 5.** Reliability–sharpness frontier. Each line is a calibration family evaluated over its full parameter grid on the target buildings (mean over five seeds): score shrinkage with own-score decay ρ ∈ {1, 0.95, 0.9, 0.8} per day over κ, quantile shrinkage over λ, and ACI over γ. x: change of the median relative interval score versus pooled CQR; y: under-covered buildings over the 56-day window (a, b) and in the first week (c, d). Lower left is better. κ = λ = 0 (own scores only) are omitted because the radius is undefined in the first days.](figures/Fig_frontier.png){width=16.5cm}

## 4.5 Which design elements matter

Fig. 6 isolates the design elements. *Shrinkage* is indispensable: the same layer with $\kappa=\infty$ (HSC-CQR recency κ=∞) behaves like pooled CQR (15.5%). *The selection objective* matters next. Selected by the interval score, which is almost flat in $\kappa$, the layer without recency used $\kappa$ = 336 h and left 1.9% under-covered; selected by the constrained coverage objective it used 168, 96 h (1.1%). *Recency* then lowers the remaining window share (Section 4.4).

Three refinements do not help. A similarity-localised population distribution with onboarding-stage matching (HSC-CQR: 2.7%) adds nothing over the stage-agnostic simple variant; after scale normalisation and history-aware features, the remaining differences between buildings' score distributions appear to be driven by events rather than by load shape. Stage-wise studentisation alone (SSC-CQR: 10.0%) leaves many buildings under-covered: its stage-wise guarantee is a statement about the average over new buildings, not about each building, and it does not even hold here because the calibration and target periods differ (Section 2). Combined with shrinkage (HSC-SSC-CQR), studentisation is competitive in medians (0.8%; first week 14.7%) but fails in the tails: a few buildings with a large running scale receive intervals up to 87.9 times as wide as pooled CQR's, and its mean interval score is +22.4% above CQR's.

![**Fig. 6.** Design elements of the calibration layer: share of under-covered buildings over the window (a) and in the first week (b), mean ± s.d. over five seeds. From left: proposed layer (recency, coverage objective); with stage-wise studentisation; without recency (coverage objective); fixed κ = 168 h; without recency (interval-score objective); with stage matching and similarity prior (interval-score objective); without shrinkage (κ = ∞); own scores only (κ = 0); pooled CQR.](figures/Fig6_ablation.png){width=16.5cm}

## 4.6 Sharpness tails

Equal medians do not imply equal tails. The recommended layer's mean relative interval score is +1.8% above pooled CQR's on BDG2 (-0.1% on UCI), its 99th-percentile width ratio is 1.43, and 2 building-seed units receive intervals more than five times as wide as CQR's (maximum 6.5×). They arise because the building's own scores enter the radius directly: a few extreme own scores widen the interval until recency weighting down-weights them. Capping the radius at the pooled 99 % score quantile (HSC-CQR recency (capped)) removes them (maximum width ratio 1.5×, mean interval score -1.0% vs CQR) at a window share of 0.4% instead of 0.2%. Quantile shrinkage (8.8×), ACI (14.6×) and self-calibration (31.0×) have larger extremes. We recommend the capped variant for deployment.

## 4.7 Robustness and generalisation

Table 2 stresses the strategies on BDG2. In all fourteen conditions, the recommended layer keeps the window share below 1 %, and it is significantly lower than ACI-CQR (cov) in thirteen and than QShrink-CQR (cov) in ten of them (paired McNemar tests). Pooled calibration from clean calibration buildings breaks down when the new buildings' meters are noisy (29.5% under-covered at 15 % noise), drift (26.8% under a ramp) or shift in level; the layer is largely unaffected because the building's own scores enter the mixture. Two stresses remain hard for every strategy. A level shift in the first two weeks raises first-week under-coverage to about 40 % for all methods, and a gradual ramp leaves about a fifth of the buildings under-protected (upper bound exceeded in more than 10 % of hours) even with the layer, because a ramp biases the point forecast faster than any calibration of a fixed-width radius can follow.

**Table 2.** Stress tests on BDG2 (3 seeds; unit = building). Columns 2–5: share of buildings (%) with coverage < 0.85 over the 56-day window (HSC-CQR recency: mean ± s.d. over seeds, the s.d. reflecting split variability); * = paired McNemar test against HSC-CQR recency, p < 0.05. Wk 1: under-covered share in the first week. Under-prot.: share of buildings whose upper bound is exceeded in more than 10 % of hours (nominal 5 %). Perturbations are applied to the target buildings only.

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


On campuses that contributed no training or calibration building (leave-site-out), 0.4% of the buildings are under-covered with the layer (QShrink-CQR (cov) 1.7%; CQR 21.4%). With models and calibration scores from BDG2 applied to Portuguese UCI clients, the share is 0.0% (CQR 3.5%). The opposite direction is much harder: a model and calibration population from UCI clients, without weather information, leave 39.0% of the BDG2 buildings under-covered with CQR and 1.3% with the layer, which then rests mainly on the building's own scores. At the 95 % level the ordering is unchanged (0.1% vs 12.7% on BDG2). At the 80 % level, the selection rule picks online level control (ACI-CQR (cov): 0.5% on BDG2 vs 3.3% for the layer): with wider miss probabilities, the binary feedback of ACI carries enough information to correct a building within days (Supplementary Tables S6–S9).

## 4.8 Operational consequences and computational cost

Table 3 translates the intervals into day-ahead capacity-headroom offers planned on the upper bound. With pooled CQR, 7.7% of the BDG2 buildings and 2.7% of the UCI clients have their upper bound exceeded more than twice as often as stated; with the recommended layer, 2.3% and 0.2%. The *average* cost changes little (+1.2%, +0.3% and -1.1% on BDG2 for penalty ratios of 10, 20 and 40), and the mean cost of the worst decile of buildings changes by +2.1%. The layer does not make the portfolio cheaper. It redistributes the planning margin from regular buildings, which pooled calibration over-protects, to volatile buildings, which it under-protects, so that far fewer buildings systematically violate their stated reliability. Whether this has monetary value depends on whether contracts or settlement are building-specific; with a portfolio-level linear penalty, as in this cost model, it has none.

**Table 3.** Operational consequence: day-ahead capacity-headroom offers planned on the upper bound (Eq. 7). Upper exceed.: mean share of hours above the upper bound (nominal 5 %); Under-prot.: share of buildings with more than 10 % exceedance; Cost Δ: change of the mean relative cost (planning load + ρ_p × violation) versus pooled CQR for penalty ratios ρ_p (ρ_p = 20 is cost-optimal for a calibrated 95 % upper bound); mean ± s.d. over seeds.

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


The online step of the layer (binning the new score and recomputing the radius) takes 0.037 ms per building-day on one CPU core, against 4.54 ms for the LightGBM inference itself. The state per building is 16 kB; the deployment prior is a fixed score histogram; leave-one-building-out selection of $\kappa$ takes 1.8 s on BDG2 and needs 93 MB. Cost per building-day is constant in the number of buildings and in onboarding time.

## 4.9 Where the layer still fails

With pooled CQR, a building's coverage falls with its forecast difficulty (Spearman correlation between per-building coverage and CV(RMSE): -0.60 on BDG2, -0.57 on UCI); with the proposed layer the correlation is -0.22 and 0.01 (Fig. 7a). Across usage classes with at least 30 building × seed units, the largest reduction of the absolute coverage deviation is observed for 'Entertainment/public assembly' and the smallest for 'Lodging/residential' (Fig. 7b). Of the 1507 BDG2 building × seed units, 2 remain under-covered. On UCI, 0 of 475 units remain under-covered. Fig. 8 shows the intervals for two pre-specified buildings: the one at the 10th percentile and the one at the median of per-building CQR coverage.

![**Fig. 7.** Error analysis on BDG2: (a) per-building coverage versus point-forecast CV(RMSE) of the building (log scale) for pooled CQR and the proposed layer; (b) mean coverage by primary usage (usage classes with at least 30 building × seed units).](figures/Fig10_error_analysis.png){width=16.5cm}

![**Fig. 8.** Day-ahead 90 % intervals for two pre-specified BDG2 buildings during their first 10 forecast days (seed 0): the building at the 10th percentile (a) and at the median (b) of per-building CQR coverage. Markers show observations outside the respective interval.](figures/Fig11_examples.png){width=16.5cm}


# 5. Discussion

## 5.1 Why pooled calibration fails per building, and what repairs it

A global forecaster normalised by building scale produces scores that are comparable *on average* across buildings, but not identically distributed. Some buildings have regular schedules and small errors; others have irregular occupancy, plug loads or weather sensitivity that the first days of data cannot reveal. A pooled quantile is a compromise that over-covers the former and under-covers the latter. In our data, pooled CQR coverage falls with forecast difficulty (Spearman correlation with CV(RMSE): -0.60 on BDG2), much less so with the recommended layer (-0.22).

The results point to one mechanism and two choices. The mechanism is *shrinkage toward the building's own scores*: every strategy that lets the new building's scores gain weight as they accumulate removes most of the pooled excess over the onboarding window, whether it mixes score distributions or quantiles. We therefore read the result as a property of the shrinkage family, in line with credibility theory [45,47], rather than as a new mechanism. The first choice is the *selection objective*. The interval score is almost flat in the pseudo-count and gives little guidance; selecting it for per-building coverage under a sharpness constraint, as [49] did for site-level violations, selects small pseudo-counts of one to seven days of hourly scores, and these are what improve the first week. The second choice is *recency weighting*, which keeps early and pre-change scores from dominating the building's own contribution later in the window and under level shifts or drift.

Online level control (ACI) is a different kind of mechanism: it reacts to misses rather than to scores. At 90 % it can match the window-level reliability of shrinkage only in a narrow band of step sizes, and in the first week the binary miss signal carries too little information to correct a poor starting point. At 80 %, where misses are twice as frequent, the feedback is informative enough and ACI was the selected strategy. Hierarchical pooling (GHCP-style) and temporal quantile adjustment secure validity across buildings or bound their adjustment by design. These are sound choices for exchangeable groups, but they cannot correct a building whose errors are systematically larger than average.

The stage-wise studentised variant illustrates a distinction that is easy to overlook. Its coverage guarantee, averaged over new buildings at every onboarding day (a corollary of [37]), is the strongest formal property among the methods studied, yet it leaves many individual buildings under-covered, and the change between calibration and target periods voids even that guarantee here. A per-building target needs per-building information, and no population-level guarantee can substitute for it [34].

## 5.2 Practical implications

For aggregators, utilities and demand-response platforms that onboard buildings continuously, the results support a simple operating rule: calibrate the intervals of a global forecaster with CQR scores of previously onboarded buildings, mix in each new building's own scores with a forgetting factor of about 0.95 per day, select the pseudo-count by leave-one-building-out on per-building coverage of previously onboarded buildings under a sharpness constraint, and cap the radius at a high pooled quantile. Three consequences follow.

1. **No systematically unreliable buildings, but no weekly guarantee.** Over the first eight weeks, the share of buildings whose intervals are systematically too narrow falls from 15.2% to 0.4% (BDG2, capped layer), and first-week unreliability falls to the level of a perfectly calibrated building. Week-to-week coverage of any single building remains noisy, and on BDG2 about one building in five is below 0.85 in a given week, a few points more than an ideal calibration would produce. Applications that settle building by building over weeks, such as demand-response baselines, flexibility offers and anomaly alarms, should therefore budget for weekly fluctuation even with well-calibrated intervals. Measurement-and-verification practice relies on long baseline periods [2]; the layer provides usable day-ahead uncertainty well before such baselines exist.
2. **Risk redistribution, not cost reduction.** Average headroom cost is essentially unchanged, but the planning margin is reassigned from regular to volatile buildings, and buildings whose stated reliability is violated systematically become rare. This matters where contracts, settlement rules or customer trust are building-specific; under a purely portfolio-level linear penalty it has no monetary value.
3. **Negligible cost and easy integration.** The layer is closed-form, adds 0.037 ms per building-day to a forecast that itself takes 4.54 ms, keeps 16 kB of state per building, needs one parameter selected in seconds, works on top of different forecasters (LightGBM and MLP quantiles here) and needs no metadata about the new building.

## 5.3 Limitations and future work

1. **No finite-sample guarantee for the recommended layer.** Its reliability is established empirically, across two datasets, unseen sites, cross-country transfer and fourteen stress conditions. Distribution-free per-building validity is impossible in general [34]. Combining shrinkage with a formal per-building safeguard is an open problem.
2. **Weekly reliability.** On BDG2, weekly under-coverage in weeks 2–8 remains +2.5 points above the oracle reference (CI [1.5, 3.3]) for the recommended layer and is above it for every strategy studied. Level shifts in the first two weeks and gradual ramps remain hard for all strategies.
3. **Information set and simulated onboarding.** The main protocol uses all hours of the previous day; the one-day-delayed variant shows that window reliability is retained but first-week under-coverage rises by two to three points. Onboarding dates were sampled within existing meter histories, BDG2 experiments use observed temperature as a stand-in for weather forecasts, and the calibration period precedes the target period by one year, which introduces a small uniform coverage offset.
4. **Data coverage.** BDG2 consists mostly of campus buildings in North America and Europe, and UCI has no metadata. Residential portfolios, industrial sites, other climates and sub-hourly resolutions remain to be tested.
5. **Baselines.** Large pretrained probabilistic forecasters [14] were not run because of the CPU-only budget; the GHCP and TQA baselines are adaptations of methods designed for other settings (Supplementary Section S3), and Bayesian area-conditional methods such as FAB [40] were not run because a building has too few own scores in its first week.
6. **Fixed decay factor.** The forgetting factor was fixed at 0.95 per day; the frontier shows that 0.8 is slightly better on BDG2. Selecting it jointly with the pseudo-count was not studied.
7. **Decision model.** The capacity-headroom case is deliberately simple. Building-level contractual penalties, market-specific settlement, correlated errors across buildings and portfolio-level bids are natural extensions.

# 6. Conclusion

Day-ahead load intervals are needed from the first days after a building is metered, and they must be reliable for each building, not only on average. Across 1,358 buildings and clients from two public datasets, pooled conformalised quantile regression left 15.2% (BDG2) and 12.3% (UCI) of new buildings systematically under-covered over their first eight weeks, although its mean coverage was close to nominal. Shrinking each building's calibration toward its own accumulating scores, with the pseudo-count selected for per-building coverage under a sharpness constraint, removed nearly all of this excess (0.2% and 0.0% with the recommended recency-weighted layer) at an equivalent median interval score, and brought first-week reliability to the level of a perfectly calibrated building. Quantile shrinkage performed almost as well; the result is a property of the shrinkage family. Online level control matched it over the window only in a narrow band of step sizes, and not in the first week at 90 %. The gains held on unseen sites, after cross-country transfer, with a delayed information set, for a neural forecaster and under fourteen stress conditions. Two caveats bound the claim: weekly coverage of single buildings remains noisy and, on BDG2, a few points worse than ideal for every strategy, and the recommended layer needs a radius cap to avoid rare very wide intervals. For operators, the layer does not reduce average cost; it removes systematically under-protected buildings at negligible computational cost.


# CRediT authorship contribution statement

**P N Bhargav Teja:** Conceptualization, Methodology, Software, Validation, Formal analysis, Investigation, Data curation, Writing – original draft, Writing – review & editing, Visualization. **[Second Author]:** Supervision.

# Declaration of competing interest

The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

# Declaration of generative AI and AI-assisted technologies in the manuscript preparation process

During the preparation of this work the authors used Claude (Anthropic) to assist with literature screening, code development, running the experiments, and drafting and editing the text. All reported numbers are generated automatically from the released code and result files. After using this tool, the authors reviewed and edited the content as needed and take full responsibility for the content of the published article.

# Data and code availability

Both datasets are public. BDG2 (CC-BY-4.0) is available at https://github.com/buds-lab/building-data-genome-project-2 [57], and ElectricityLoadDiagrams20112014 (CC-BY-4.0) at https://doi.org/10.24432/C58C86 [59]. The complete code (data download and cleaning, models, the calibration layer, all baselines, experiments, statistics, figures, tables and this manuscript's numbers) is provided as supplementary material and will be released in a public repository [repository URL to be inserted upon acceptance]. `python run_all.py --mode full` reproduces all results.

# 7. Funding

This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors.

# References

1. Li H, Wang Z, Hong T, Piette MA. Energy flexibility of residential buildings: A systematic review of characterization and quantification methods and applications. Adv Appl Energy 2021;3:100054. https://doi.org/10.1016/j.adapen.2021.100054.
2. ASHRAE. Guideline 14-2014: Measurement of energy, demand, and water savings. Atlanta, GA: ASHRAE; 2014.
3. Hong T, Fan S. Probabilistic electric load forecasting: A tutorial review. Int J Forecast 2016;32:914–38. https://doi.org/10.1016/j.ijforecast.2015.11.011.
4. Hong T, Pinson P, Fan S, Zareipour H, Troccoli A, Hyndman RJ. Probabilistic energy forecasting: Global Energy Forecasting Competition 2014 and beyond. Int J Forecast 2016;32:896–913. https://doi.org/10.1016/j.ijforecast.2016.02.001.
5. Guo H, Huang B, Wang J. Probabilistic load forecasting for integrated energy systems using attentive quantile regression temporal convolutional network. Adv Appl Energy 2024;14:100165. https://doi.org/10.1016/j.adapen.2024.100165.
6. Nie Y, Zelikman E, Scott A, Paletta Q, Brandt A. SkyGPT: Probabilistic ultra-short-term solar forecasting using synthetic sky images from physics-constrained VideoGPT. Adv Appl Energy 2024;14:100172. https://doi.org/10.1016/j.adapen.2024.100172.
7. Lindberg O, Lingfors D, Arnqvist J, van der Meer D, Munkhammar J. Day-ahead probabilistic forecasting at a co-located wind and solar power park in Sweden: Trading and forecast verification. Adv Appl Energy 2023;9:100120. https://doi.org/10.1016/j.adapen.2022.100120.
8. Amasyali K, El-Gohary NM. A review of data-driven building energy consumption prediction studies. Renew Sustain Energy Rev 2018;81:1192–205. https://doi.org/10.1016/j.rser.2017.04.095.
9. Ribeiro M, Grolinger K, ElYamany HF, Higashino WA, Capretz MAM. Transfer learning with seasonal and trend adjustment for cross-building energy forecasting. Energy Build 2018;165:352–63. https://doi.org/10.1016/j.enbuild.2018.01.034.
10. Fan C, Sun Y, Xiao F, Ma J, Lee D, Wang J, et al. Statistical investigations of transfer learning-based methodology for short-term building energy predictions. Appl Energy 2020;262:114499. https://doi.org/10.1016/j.apenergy.2020.114499.
11. Pinto G, Wang Z, Roy A, Hong T, Capozzoli A. Transfer learning for smart buildings: A critical review of algorithms, applications, and future perspectives. Adv Appl Energy 2022;5:100084. https://doi.org/10.1016/j.adapen.2022.100084.
12. Gao J, Chen Y, Hu W, Zhang D. An adaptive deep-learning load forecasting framework by integrating transformer and domain knowledge. Adv Appl Energy 2023;10:100142. https://doi.org/10.1016/j.adapen.2023.100142.
13. Ristovska T, González-Vidal A, Skarmeta AF, Kovatcheva E, Gotsev L. Federated transfer learning for cold-start building energy prediction under data scarcity and privacy constraints. Energy AI 2026;25:100815. https://doi.org/10.1016/j.egyai.2026.100815.
14. Emami P, Sahu A, Graf P. BuildingsBench: A large-scale dataset of 900K buildings and benchmark for short-term load forecasting. In: Advances in Neural Information Processing Systems 36 (NeurIPS 2023), Datasets and Benchmarks Track; 2023.
15. Hao Y, Yang J, Ji Z. Evaluating the reliability of cross-building load forecasting under distribution shift and sensor missingness. Appl Sci 2026;16:7984. https://doi.org/10.3390/app16167984.
16. Vovk V, Gammerman A, Shafer G. Algorithmic learning in a random world. New York: Springer; 2005. https://doi.org/10.1007/b106715.
17. Lei J, G'Sell M, Rinaldo A, Tibshirani RJ, Wasserman L. Distribution-free predictive inference for regression. J Am Stat Assoc 2018;113:1094–111. https://doi.org/10.1080/01621459.2017.1307116.
18. Angelopoulos AN, Bates S. Conformal prediction: A gentle introduction. Found Trends Mach Learn 2023;16:494–591. https://doi.org/10.1561/2200000101.
19. Romano Y, Patterson E, Candès E. Conformalized quantile regression. In: Advances in Neural Information Processing Systems 32 (NeurIPS 2019); 2019.
20. Kath C, Ziel F. Conformal prediction interval estimation and applications to day-ahead and intraday power markets. Int J Forecast 2021;37:777–99. https://doi.org/10.1016/j.ijforecast.2020.09.006.
21. Suresh V, Swain A, Revathi BS, Guerrero JM. Mamba based adaptive conformal inference for probabilistic short-term load forecasting. Knowl Based Syst 2025;328:114222. https://doi.org/10.1016/j.knosys.2025.114222.
22. Shi L, Shen Z, Lyu T. Local online conformal prediction for power load forecasting intervals. Electr Power Syst Res 2026;261:113412. https://doi.org/10.1016/j.epsr.2026.113412.
23. Moradi A, Tanneau M, Zandehshahvar R, Van Hentenryck P. Enhanced renewable energy forecasting using context-aware conformal prediction. arXiv:2510.15780 [Preprint]; 2025. https://doi.org/10.48550/arXiv.2510.15780.
24. Almeida V, Gama J. Prediction intervals for electric load forecast: Evaluation for different profiles. In: 2015 18th International Conference on Intelligent System Application to Power Systems (ISAP); 2015. https://doi.org/10.1109/isap.2015.7325539.
25. Gibbs I, Cherian JJ, Candès EJ. Conformal prediction with conditional guarantees. J R Stat Soc Series B Stat Methodol 2025;87:1100–26. https://doi.org/10.1093/jrsssb/qkaf008.
26. Ding T, Angelopoulos AN, Bates S, Jordan MI, Tibshirani RJ. Class-conditional conformal prediction with many classes. In: Advances in Neural Information Processing Systems 36 (NeurIPS 2023); 2023.
27. Gibbs I, Candès E. Adaptive conformal inference under distribution shift. In: Advances in Neural Information Processing Systems 34 (NeurIPS 2021); 2021.
28. Zaffran M, Féron O, Goude Y, Josse J, Dieuleveut A. Adaptive conformal predictions for time series. In: Proceedings of the 39th International Conference on Machine Learning, PMLR 162; 2022, p. 25834–66.
29. Gibbs I, Candès EJ. Conformal inference for online prediction with arbitrary distribution shifts. J Mach Learn Res 2024;25(162):1–36. https://www.jmlr.org/papers/v25/22-1218.html.
30. Bhatnagar A, Wang H, Xiong C, Bai Y. Improved online conformal prediction via strongly adaptive online learning. In: Proceedings of the 40th International Conference on Machine Learning, PMLR 202; 2023, p. 2337–63.
31. Angelopoulos AN, Candès EJ, Tibshirani RJ. Conformal PID control for time series prediction. In: Advances in Neural Information Processing Systems 36 (NeurIPS 2023); 2023. https://arxiv.org/abs/2307.16895.
32. Barber RF, Candès EJ, Ramdas A, Tibshirani RJ. Conformal prediction beyond exchangeability. Ann Stat 2023;51:816–45. https://doi.org/10.1214/23-AOS2276.
33. Lin Z, Trivedi S, Sun J. Conformal prediction with temporal quantile adjustments. In: Advances in Neural Information Processing Systems 35 (NeurIPS 2022); 2022.
34. Lin Z, Trivedi S, Sun J. Conformal prediction intervals with temporal dependence. Trans Mach Learn Res 2022. https://doi.org/10.48550/arXiv.2205.12940.
35. Fisch A, Schuster T, Jaakkola T, Barzilay R. Few-shot conformal prediction with auxiliary tasks. In: Proceedings of the 38th International Conference on Machine Learning, PMLR 139; 2021, p. 3329–39.
36. Dunn R, Wasserman L, Ramdas A. Distribution-free prediction sets for two-layer hierarchical models. J Am Stat Assoc 2023;118:2491–502. https://doi.org/10.1080/01621459.2022.2060112.
37. Lee Y, Barber RF, Willett R. Distribution-free inference with hierarchical data. arXiv:2306.06342 [Preprint]; 2023. https://doi.org/10.48550/arXiv.2306.06342.
38. Mallick S, Tchetgen Tchetgen E, Dobriban E, Lee Y. Generalized hierarchical conformal prediction. arXiv:2608.15500 [Preprint]; 2026. https://doi.org/10.48550/arXiv.2608.15500.
39. Lu C, Yu Y, Karimireddy SP, Jordan MI, Raskar R. Federated conformal predictors for distributed uncertainty quantification. In: Proceedings of the 40th International Conference on Machine Learning, PMLR 202; 2023, p. 22942–64.
40. Bersson E, Hoff PD. Optimal conformal prediction for small areas. J Surv Stat Methodol 2024;12:1464–88. https://doi.org/10.1093/jssam/smae010.
41. Hoff P. Bayes-optimal prediction with frequentist coverage control. Bernoulli 2023;29:901–28. https://doi.org/10.3150/22-BEJ1484.
42. Zhang Y, Candès EJ. Posterior conformal prediction. arXiv:2409.19712 [Preprint]; 2024. https://doi.org/10.48550/arXiv.2409.19712.
43. Bhattacharyya A, Barber RF. Group-weighted conformal prediction. arXiv:2401.17452 [Preprint]; 2024. https://doi.org/10.48550/arXiv.2401.17452.
44. Bhattacharyya A, Ding T, Barber RF. Conformal prediction with macro-coverage guarantees. arXiv:2606.28598 [Preprint]; 2026. https://doi.org/10.48550/arXiv.2606.28598.
45. Bühlmann H. Experience rating and credibility. ASTIN Bull 1967;4:199–207. https://doi.org/10.1017/S0515036100008989.
46. Efron B, Morris C. Stein's estimation rule and its competitors—An empirical Bayes approach. J Am Stat Assoc 1973;68:117–30. https://doi.org/10.2307/2284155.
47. Bühlmann H, Gisler A. A course in credibility theory and its applications. Berlin: Springer; 2005. https://doi.org/10.1007/3-540-29273-X.
48. Hong L. Conformal prediction credibility intervals. N Am Actuar J 2023;27:675–88. https://doi.org/10.1080/10920277.2022.2123364.
49. Shahid NF. When average calibration fails: Site-conditional federated conformal risk control. arXiv:2606.20115 [Preprint]; 2026. https://doi.org/10.48550/arXiv.2606.20115.
50. Rafe A, Das S. Socio-conformal calibration in complex survey data: Marginal validity is not enough for subgroup reliability. arXiv:2605.05562 [Preprint]; 2026. https://doi.org/10.48550/arXiv.2605.05562.
51. Zhang Z, Lu Z, Yang H. The benefit of being Bayesian in online conformal prediction. arXiv:2410.02561 [Preprint]; 2024. https://doi.org/10.48550/arXiv.2410.02561.
52. Fang YH, Lee CY. Optimal spatio-temporal decoupling for Bayesian conformal prediction. arXiv:2605.00432 [Preprint]; 2026. https://doi.org/10.48550/arXiv.2605.00432.
53. Jeon B. coldstart-conformal-solar: Analysis code for auditing cold-start conformal prediction intervals of solar irradiance forecasts at unseen stations (v1.2) [software]. Zenodo; 2026. https://doi.org/10.5281/zenodo.24002627.
54. Koenker R, Bassett G. Regression quantiles. Econometrica 1978;46:33–50. https://doi.org/10.2307/1913643.
55. Tibshirani RJ, Barber RF, Candès E, Ramdas A. Conformal prediction under covariate shift. In: Advances in Neural Information Processing Systems 32 (NeurIPS 2019); 2019.
56. Ferguson TS. A Bayesian analysis of some nonparametric problems. Ann Stat 1973;1:209–30. https://doi.org/10.1214/aos/1176342360.
57. Miller C, Kathirgamanathan A, Picchetti B, Arjunan P, Park JY, Nagy Z, et al. The Building Data Genome Project 2, energy meter data from the ASHRAE Great Energy Predictor III competition. Sci Data 2020;7:368. https://doi.org/10.1038/s41597-020-00712-x.
58. Miller C, Arjunan P, Kathirgamanathan A, Fu C, Roth J, Park JY, et al. The ASHRAE Great Energy Predictor III competition: Overview and results. Sci Technol Built Environ 2020;26:1427–47. https://doi.org/10.1080/23744731.2020.1795514.
59. Trindade A. ElectricityLoadDiagrams20112014 [dataset]. UCI Machine Learning Repository; 2015. https://doi.org/10.24432/C58C86.
60. Ke G, Meng Q, Finley T, Wang T, Chen W, Ma W, et al. LightGBM: A highly efficient gradient boosting decision tree. In: Advances in Neural Information Processing Systems 30 (NIPS 2017); 2017.
61. Wang Y, Gan D, Sun M, Zhang N, Lu Z, Kang C. Probabilistic individual load forecasting using pinball loss guided LSTM. Appl Energy 2019;235:10–20. https://doi.org/10.1016/j.apenergy.2018.10.078.
62. Salinas D, Flunkert V, Gasthaus J, Januschowski T. DeepAR: Probabilistic forecasting with autoregressive recurrent networks. Int J Forecast 2020;36:1181–91. https://doi.org/10.1016/j.ijforecast.2019.07.001.
63. Winkler RL. A decision-theoretic approach to interval estimation. J Am Stat Assoc 1972;67:187–91. https://doi.org/10.1080/01621459.1972.10481224.
64. Gneiting T, Raftery AE. Strictly proper scoring rules, prediction, and estimation. J Am Stat Assoc 2007;102:359–78. https://doi.org/10.1198/016214506000001437.
65. Holm S. A simple sequentially rejective multiple test procedure. Scand J Stat 1979;6:65–70.
66. Wilcoxon F. Individual comparisons by ranking methods. Biometrics Bull 1945;1:80–3. https://doi.org/10.2307/3001968.
