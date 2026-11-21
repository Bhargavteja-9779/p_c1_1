---
title: "Trustworthy day-ahead load intervals for newly metered buildings via recency-weighted shrinkage conformal calibration"
---

**Authors:** [Author 1]^a,\*^, [Author 2]^b^

^a^ [Department, Institution, City, Country] · ^b^ [Department, Institution, City, Country]

\* Corresponding author. E-mail: [corresponding.author@institution]

# Highlights

- Pooled conformal intervals leave many newly metered buildings under-covered
- Recency-weighted shrinkage calibrates intervals building by building
- Under-covered new buildings fall from 18.7% to 0.4% at unchanged interval score
- The layer also reduces first-week unreliability, unlike online level control
- Tested on 1,157 buildings, unseen sites, cross-country transfer and stress tests

# Abstract

Demand response, flexibility offers and measurement-and-verification need day-ahead load intervals for individual buildings, often from the first days after a building is metered. Interval methods are usually judged by coverage pooled over many buildings, which can hide buildings whose intervals are systematically too narrow. We propose a recency-weighted shrinkage conformal calibration layer that mixes each new building's exponentially down-weighted nonconformity scores with the score distribution of previously onboarded buildings, with a pseudo-count selected by leave-one-building-out for per-building coverage. Under a building- and period-disjoint protocol on 842 buildings at 10 sites (Building Data Genome 2) and 315 Portuguese electricity clients, we compare it with pooled, self-only, adaptive, temporal, hierarchical and quantile-shrinkage conformal calibration and with direct probabilistic forecasters. Pooled conformalised quantile regression left 18.7% (BDG2) and 9.5% (UCI) of new buildings with coverage more than five points below the 90 % target; the proposed layer reduced these shares to 0.4% and 0.0%, the level expected from sampling noise, with first-week shares falling from 23.8% to 13.7% and from 16.0% to 5.9%, at an interval score within +0.9% of the pooled baseline. Gains held on unseen sites, after cross-country transfer and under noise, missing data, level shifts and small calibration pools. Online level control matched window-level reliability only in a narrow parameter band and not in the first week. In day-ahead capacity-headroom offers, the layer left average cost unchanged but removed systematically under-protected buildings, at 0.015 ms per building-day.

**Keywords:** probabilistic load forecasting; conformal prediction; cold start; building energy; demand response; prediction intervals


# 1. Introduction

## 1.1 Background and motivation

Buildings account for a large share of electricity demand, and their flexible loads are increasingly enrolled in demand response, flexibility markets and on-site renewable integration [1]. These applications act on day-ahead statements of the form "tomorrow's hourly load of *this* building will lie between $L$ and $U$ with probability $1-\alpha$". Demand-response baselines and their settlement, day-ahead capacity and flexibility offers, measurement and verification [2] and anomaly alarms all depend on such intervals. Probabilistic load forecasting has therefore become a central topic in energy forecasting [3,4], and recent studies in this journal have developed expressive probabilistic models for loads, renewables and multi-energy systems [5–7].

Intervals are needed most when a building has just been connected to a monitoring, aggregation or demand-response platform, which is exactly when the least building-specific data exist. Aggregators onboard buildings continuously, and an interval that is too narrow for an individual building exposes the operator to penalties and false alarms for that building, regardless of how well the intervals perform on average over the portfolio. Two properties are therefore required at the same time. The intervals must be *reliable building by building*, not only on average, and they must be reliable *from the first days* after metering starts, without months of building-specific history.

## 1.2 Related work

*Forecasting with little building-specific data.* Data-driven building forecasting traditionally needs months to years of history per building [8]. Transfer learning, federated learning and global or pretrained models now provide useful point forecasts for buildings with little history [9–13], and large pretrained models report zero-shot probabilistic forecasts for unseen buildings [14]. A recent cross-building study found that split-conformal intervals under-cover unseen buildings on average and recommended recalibration before deployment [15]. These studies evaluate point accuracy or *pooled* interval metrics; whether the intervals are reliable for *each* new building, and from which day on, has not been examined.

*Conformal calibration in energy forecasting.* Conformal prediction gives distribution-free intervals around any forecaster [16–18], with conformalised quantile regression (CQR) as a strong default [19]. It is increasingly used for loads and renewables, for example with adaptive conformal inference (ACI) [20], local online conformal prediction for power-load intervals [21] and context-aware calibration for renewable forecasts [22]. Its guarantee is *marginal*: averaged over exchangeable test points. For a fleet of new buildings, a marginal guarantee is compatible with intervals that are much too narrow for volatile buildings and too wide for regular ones, while pooled coverage looks perfect. An early comparison of interval methods across load profiles already observed that reliability differs between profiles [23].

*Unit-level and temporal calibration.* The statistics literature offers several remedies, each developed under different assumptions. Group-wise (Mondrian) calibration [16] needs enough calibration data per group, and conditional or class-conditional calibration targets pre-specified groups [24,25]. Online methods adapt the miscoverage level of a single series, such as ACI and its aggregated variants [26,27], or weight recent scores more heavily under drift, such as non-exchangeable conformal prediction [28]. For panels of series, temporal quantile adjustment (TQA) targets per-series (longitudinal) coverage and shows that distribution-free longitudinal validity is impossible in general [29,30]. Hierarchical conformal prediction gives coverage for a *new group* drawn from the same population [31,32], and generalised hierarchical conformal prediction (GHCP) uses a new group's first observations [33]. Finally, credibility-type shrinkage of a unit's own calibration towards a pooled one has recently been proposed for federated sites [34], survey subgroups [35], online conformal prediction with a Bayesian prior [36] and newly commissioned solar stations, with a fixed pseudo-count [37]; the credibility form itself is classical [38].

## 1.3 Research gaps and contributions

Three gaps follow from this literature.

1. **No building-level evaluation of interval reliability during onboarding.** Energy studies report pooled coverage; how many newly metered buildings receive unreliable intervals, in which weeks and with which operational consequences, is unknown.
2. **No evidence on which calibration mechanism suits onboarding.** The candidate mechanisms (online level control, temporal quantile adjustment, hierarchical pooling, quantile- or score-level shrinkage) have not been compared on the same forecaster, scores and protocol, and none was designed for a population of new units whose forecast errors change as their history grows.
3. **No calibration rule that is reliable both per building and in the first week.** Pooling cannot adapt to an individual building; self-calibration is noisy in the first days; and the parameters that control the transition between the two have so far been fixed by hand or tuned for sharpness.

This study addresses these gaps with the following contributions.

1. **Problem formulation and protocol.** We formalise *per-building interval reliability during onboarding*, with outcome measures that operators can act on: the share of under-covered buildings over the onboarding window and in each week, a sampling-noise reference for these shares, and the share of buildings whose upper bound is exceeded twice as often as stated. We evaluate them under a building- and period-disjoint protocol on two public datasets with 1,157 buildings and clients, with leave-site-out and cross-country transfer and stress tests.
2. **A recency-weighted shrinkage calibration layer.** We propose a closed-form layer that mixes a building's exponentially down-weighted own nonconformity scores with the population's score distribution through a pseudo-count, with the pseudo-count selected by leave-one-building-out on the per-building coverage of calibration buildings. It runs on top of any interval forecaster.
3. **A head-to-head comparison and the reliability–sharpness frontier.** Under one protocol, forecaster and score, we compare pooled split conformal and CQR, Mondrian, self-only, ACI, TQA, GHCP-style pooling, quantile shrinkage and score shrinkage, each tuned in the same way, together with direct quantile-regression and deep probabilistic baselines. We map every strategy over its full parameter range to show which ones are reliable without loss of sharpness, and in which weeks.
4. **Operational evidence.** We quantify the effect on day-ahead capacity-headroom offers and show which design elements matter, including two that do not (building-similarity priors and onboarding-stage matching) and one that fails in the tails (studentising scores by a running scale estimate).

The rest of the paper presents the methodology (Section 2), the data and experimental design (Section 3), the results (Section 4) and their implications and limitations (Section 5). Section 6 concludes.


# 2. Methodology

## 2.1 Problem setting and notation

Let $y_{b,t,j}\ge 0$ denote the metered electricity use (kWh) of building $b$ on day $t$ and hour $j\in\{0,\dots,23\}$. Building $b$ is metered from day $t_{0,b}$ onward. At the end of day $t_{0,b}+h-1$, after $h$ days of the building's own history have been observed, a day-ahead forecast is issued for the 24 hours of day $t=t_{0,b}+h$; we call $h$ the *onboarding stage*. For a miscoverage level $\alpha$ (main analysis: $\alpha=0.1$), the goal is an interval $C_{b,h,j}=[L_{b,h,j},U_{b,h,j}]$ such that, **for every individual building**, the share of hours with $y_{b,t,j}\in C_{b,h,j}$ is close to $1-\alpha$ from the first days after metering starts, while the intervals remain as narrow as possible. The empirical target is therefore the distribution of per-building coverage across buildings, not only its mean.

Three disjoint sets of buildings are available (Section 3): *training* buildings for the global forecaster, *calibration* buildings whose (simulated) onboarding windows provide nonconformity scores, and *target* buildings, which are metered in a later period and on which all methods are evaluated.

## 2.2 Scale-normalised global forecaster

Buildings differ in mean load by four orders of magnitude (Fig. 2). Every load-derived quantity is therefore expressed relative to the scale

$$
s_{b,h}=\frac{1}{24\,m_h}\sum_{k=1}^{m_h}\sum_{j=0}^{23} y_{b,\,t-k,\,j},\qquad m_h=\min(h,7),\qquad\qquad (1)
$$

which uses only the last $m_h$ observed days. A single model $f$ is trained on the training buildings to predict $y_{b,t,j}/s_{b,h}$ from calendar variables, the normalised loads of the previous 1, 2, 7 and 14 days (missing if $h$ is smaller), normalised daily statistics and hour-of-day/day-type profiles computed over at most the last 28 observed days, the day-to-day variability of the normalised profile, the history length $\min(h,28)$, and, for BDG2, outdoor air temperature (Supplementary Table S1). During training, the history length of every sample is drawn uniformly from $\{1,\dots,28\}$ and all features are masked accordingly, so the model learns to forecast from short histories. The point forecast is $\hat y_{b,t,j}=s_{b,h}\,f(\mathbf x_{b,t,j})$; quantile models $f^{\mathrm{lo}},f^{\mathrm{hi}}$ (levels $\alpha/2$ and $1-\alpha/2$) are trained in the same way with the pinball loss [39].

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

where the "+1" is a point mass at $+\infty$ that represents the not-yet-observed test score, as in weighted split conformal prediction [28,40]. With $\rho=1$, the building's own scores receive the weight $n_{b,h}/(\kappa+n_{b,h}+1)$. This is the classical credibility (empirical-Bayes) form [38], recently used to shrink site- or group-specific conformal calibration towards a pooled one [34,35] and, with a fixed pseudo-count, to mix donor and local scores for new solar stations [37]. It is also the posterior mean of the building's score distribution under a Dirichlet-process prior with base measure $F^{\mathrm{pop}}$ and concentration $\kappa$ [36,41]. Two limits recover familiar methods: $\kappa\to\infty$ gives pooled split conformal prediction, and $\kappa=0$ gives split conformal prediction on the building's own scores, which is undefined until enough own scores exist. The pseudo-count has a direct operational reading: it is the number of hourly own scores that the population is worth.

Recency weighting ($\rho<1$) is motivated by onboarding itself. Errors in the first days are produced by a forecaster that has seen almost no history of the building, and newly enrolled buildings can change their operation after enrolment. Old own scores then describe a building that no longer exists, and they are down-weighted in the same spirit as non-exchangeable conformal prediction [28]. A side effect is that the effective sample size $n^{\rho}_{b,h}$ is bounded by $1/(1-\rho)$, so the population distribution keeps a minimum weight $\kappa/(\kappa+1/(1-\rho)+1)$ throughout. The decay factor $\rho=0.95$ per day (half-life ≈ 13.5 days) was fixed before any result was seen (Section 3.6); Section 4.3 reports $\rho\in\{0.8,0.9,0.95,1\}$.

**Selection of the pseudo-count.** $\kappa$ is selected on the calibration buildings only, by leave-one-building-out: each calibration building in turn plays the role of a new building, with the population distribution built from the remaining calibration buildings. The selection objective is the target property itself, namely the mean absolute deviation of the per-building coverage from $1-\alpha$ over the onboarding window (ties broken by the interval score of Eq. (6)), from the grid $\kappa\in\{0,24,48,96,168,336,672,1344,\infty\}$ hours. The study's original protocol selected $\kappa$ by the interval score instead. That objective is reported as a variant, and its systematic preference for larger $\kappa$ (Section 4.4) is why the coverage objective is used. Target buildings are never used for any choice.

**Examined refinements.** Three further elements were tested and are reported as variants (Section 4.4). The first two are *onboarding-stage matching* (the population distribution built from calibration scores at a similar onboarding stage, in bins $\{1\},\{2\},\{3\},\{4..6\},\{7..13\},\{14..27\},\{28..56\}$) and a *similarity-localised population distribution* (the $K$ calibration buildings closest to the new building in a load-shape descriptor; Supplementary Section S2). The third is *stage-wise studentisation*. Each CQR score is divided by the building's running error-scale ratio

$$
r_{b,h}=\frac{\kappa_s\,\sigma_0+\sum_{h'<h}\sum_j a_{b,h',j}}{\sigma_0\,(\kappa_s+n_{b,h})},\qquad a_{b,h,j}=\frac{|y_{b,t,j}-\hat y_{b,t,j}|}{s_{b,h}},\qquad\qquad (5)
$$

with $\sigma_0$ the mean normalised absolute residual of the calibration buildings and $\kappa_s=24$ fixed a priori. At each exact stage $h$ the radius is the $(1-\alpha)$ quantile of the mixture in which each calibration building contributes the empirical distribution of its studentised scores at stage $h$ with weight $1/(M+1)$ and the new building a point mass $1/(M+1)$ at $+\infty$. This is the hierarchical conformal prediction (HCP) weighting of Lee, Barber and Willett [32], applied per stage; the "pooling CDFs" rule of [31] is closely related but has only an asymptotic guarantee. The interval is $[\hat y^{\mathrm{lo}}-\tilde q_h r_{b,h}s_{b,h},\,\hat y^{\mathrm{hi}}+\tilde q_h r_{b,h}s_{b,h}]$ (SSC-CQR), and HSC-SSC-CQR applies the shrinkage of Eq. (4) to the studentised scores.

*Proposition 1 (stage-wise validity across new buildings).* If the onboarding trajectories of the $M$ calibration buildings and of the new building are exchangeable and $\sigma_0$, $\kappa_s$ and the forecaster are fixed, then for every stage $h$, $\Pr\{y_{b,t,J}\in C_{b,h,J}\}\ge 1-\alpha$, where $J$ is an hour drawn uniformly from the new building's valid hours at stage $h$ and the probability is over buildings and $J$.

*Proof.* The studentised score is the same measurable function of each building's own trajectory up to stage $h$, so the $M+1$ vectors of stage-$h$ studentised scores are exchangeable across buildings. An independent uniform random permutation of the hours within each building makes them exchangeable within buildings as well, leaves the mixture unchanged and makes $J$ the first permuted hour. The data are then hierarchically exchangeable, and Theorem 1 of [32] gives coverage at least $1-\alpha$. ∎

The proposition guarantees coverage on average over new buildings at every onboarding day, from the first day on, which no shrinkage estimator with $0<\kappa<\infty$ does. It does not guarantee coverage for an individual building, which is impossible without distributional assumptions [30]. The results show that this distinction matters in practice (Section 4.4).

**Validity of the shrinkage layer.** For a fixed $\kappa\in(0,\infty)$, Eq. (4) does not inherit the finite-sample guarantee of split conformal prediction: neither the building's own past scores nor the calibration scores are exchangeable with its future scores, because forecast quality changes with $h$ and loads are autocorrelated. The layer is a principled, tunable interpolation between two conformal limits, and its reliability is established empirically below, including under distribution shift.

**Computation.** Score distributions are stored as cumulative counts on a fixed grid of 4000 asinh-spaced points between $-10$ and $500$ (in units of $s$; relative spacing ≈ 0.5 %). Mixture quantiles then reduce to a vectorised search; grid quantiles are rounded upwards for all methods alike, and whether an own-score quantile exists is decided from the number of own scores. The calibration store holds one cumulative-count vector per calibration building.


# 3. Data and experimental design

## 3.1 Data

**BDG2.** The Building Data Genome Project 2 [42] provides two years (2016–2017) of hourly meter data from non-residential buildings on university and public campuses in North America and Europe, together with site weather and building metadata. It is the dataset of the ASHRAE Great Energy Predictor III competition [43]. We use the cleaned electricity meters, site air temperature and the primary-space-usage attribute.

**UCI.** The ElectricityLoadDiagrams20112014 dataset [44] contains 15-min consumption of 370 Portuguese electricity clients (2011–2014). We aggregate it to hourly energy and use 2012–2014, because most clients have no data in 2011. It has no weather or metadata and represents a different country, customer mix and metering infrastructure. We use it to test generality and transfer.

**Quality rules** (applied identically to all methods and fixed before the main experiments): runs of at least 24 identical consecutive readings (meter outage or stuck meter) are treated as missing; gaps of at most 6 h are linearly interpolated; a building is retained if at most 5 % of its hours are missing in every period used and its mean load is at least 1 kWh/h. This leaves **842 BDG2 buildings at 10 sites** and **315 UCI clients** (Fig. 2). Training rows whose normalised target exceeds 20 (meter restarts after near-zero history) are excluded from model fitting only.

![**Fig. 2.** Data after the quality filter: (a) primary space usage of the BDG2 buildings; (b) distribution of mean hourly load of BDG2 buildings and UCI clients (log scale).](figures/Fig2_data.png){width=16.5cm}

## 3.2 Protocols and leakage control

*Random-building protocol (main).* For each of five pre-specified seeds, buildings are randomly partitioned into training (50 %, of which one tenth is held out as building-disjoint validation data for early stopping), calibration (20 %) and target (30 %) sets. The forecaster and all calibration scores use only the training period (BDG2: 2016; UCI: 2012–2013). Each calibration building is "onboarded" at a random date in the training period. Each target building is onboarded at a random date in the later period (BDG2: 2017; UCI: 2014), drawn among windows with at least 80 % valid hours. Every building is followed for 56 day-ahead forecasts ($h=1,\dots,56$). Features at stage $h$ use only the $h$ days after $t_{0,b}$ (verified by unit tests that perturb all data outside this window). Target buildings, their period and their data are therefore never seen by the forecaster, the calibration scores, or any hyper-parameter selection.

*Leave-site-out (BDG2).* The 10 sites are grouped into five folds of similar size. All buildings of a fold are targets; the remaining buildings are split 70/30 into training and calibration sets. This tests transfer to unseen campuses, climates and operators.

*Cross-dataset.* Models and calibration scores from one dataset are applied to the target buildings of the other (BDG2→UCI and UCI→BDG2), without weather features, which UCI lacks. A BDG2→BDG2 run without weather serves as the within-dataset reference (three seeds each).

*Stress tests (BDG2, three seeds).* Additive Gaussian meter noise with a standard deviation of 5 % or 15 % of the building's mean load (clipped at zero), random missing hours (20 % and 40 %) and abrupt level shifts of +40 % and −40 % at day 28 are applied to the new buildings' onboarding windows (history and truth). Calibration pools are reduced to 10 %, 25 % and 50 % of the calibration buildings, and a weak forecaster is trained on 10 % of the training buildings.

## 3.3 Compared methods

All conformal-type strategies use the same LightGBM quantile models, the same CQR scores (Eq. 2), the same score grid and the same calibration buildings; they differ only in how the radius $q_{b,h}$ is obtained. Every tuned parameter is selected by leave-one-building-out on calibration buildings, and the parameter grids are equally fine. Implementation details and deviations from the original methods are given in Supplementary Section S3.

* *Pooled:* **CQR** [19] (stage-matched pooled CQR scores); **SCP** and **SCP-stage** (split conformal on normalised absolute residuals [17], without and with stage matching); **Raw-SCP** (unnormalised residuals); **Mondrian-usage** (BDG2; per primary-usage class [16]); and **Naive+SCP** (seasonal-naive forecast).
* *Self-calibration:* **Self-CQR**, split conformal on the building's own past scores, falling back to pooled CQR until an own quantile exists.
* *Online level control:* **ACI-CQR** [26], $\alpha_{h+1}=\alpha_h+\gamma\sum_j(\alpha-\mathrm{err}_{h,j})$ on the pooled CQR distribution, with $\gamma\in\{0,10^{-4},2\cdot10^{-4},5\cdot10^{-4},10^{-3},2\cdot10^{-3},5\cdot10^{-3},10^{-2}\}$; a level $\alpha_h\le0$ is mapped to the largest observed calibration score.
* *Temporal and hierarchical pooling:* **TQA-B-CQR** [29] (budgeted temporal quantile adjustment; the budget scale is set from calibration buildings) and **GHCP-CQR** [33] (the new building receives the weight of one calibration building).
* *Shrinkage:* **QShrink-CQR**, quantile-level shrinkage $q=w\,q^{\mathrm{own}}+(1-w)\,q^{\mathrm{pool}}$ with $w=n_{b,h}/(n_{b,h}+\lambda)$ ("regularised Mondrian" [35]); **HSC-CQR fixed-κ**, score shrinkage with a fixed pseudo-count of one week ($\kappa=168$ h), i.e. a donor–local mixture as in [37]; and the proposed **HSC-CQR recency** (Eq. 4).
* *Variants of the layer (Section 4.4):* **HSC-CQR simple** ($\rho=1$, $\kappa$ by the interval score), **HSC-CQR simple (cov)** ($\rho=1$, $\kappa$ by the coverage objective), **HSC-CQR** (with stage matching and similarity-localised distribution), **HSC-CQR -shrink** ($\kappa=\infty$), **SSC-CQR** and **HSC-SSC-CQR** (Eq. 5).
* *Direct probabilistic models:* **QR-LGBM** (LightGBM quantile regression [39,45]), **MLP-QR** (a 256-256-128 multilayer perceptron with pinball loss [46]) and **MLP-Gauss** (the same network with a Gaussian likelihood, in the spirit of [47]); **CQR (MLP)** and **HSC-CQR (MLP)** apply the calibration to the MLP quantiles.

For fairness, ACI-CQR and QShrink-CQR are run both with the interval-score objective and with the coverage objective used for the proposed layer (suffix "(cov)"). All strategies are additionally evaluated over their full parameter grids on the target buildings (for transparency only, never for selection; Section 4.3). LightGBM (63 leaves, learning rate 0.05, at least 200 samples per leaf, 0.8 feature and bagging fractions, L2 regularisation 1) and the MLPs (Adam, learning rate $10^{-3}$, batch 4096, at most 12 epochs) use early stopping on building-disjoint validation buildings. These are conventional settings, identical for all calibration strategies.

## 3.4 Outcome measures

For target building $b$ with valid hourly observations over its 56-day window, we compute coverage $\mathrm{cov}_b$, relative width $\overline{U-L}/\bar y_b$ and the relative interval (Winkler) score [48,49]

$$
\mathrm{IS}_b=\frac{1}{\bar y_b}\,\overline{(U-L)+\tfrac{2}{\alpha}(L-y)_+ +\tfrac{2}{\alpha}(y-U)_+},\qquad\qquad (6)
$$

a proper score that rewards narrow intervals and penalises misses in proportion to their size.

*Reliability.* The primary reliability outcome is the **under-covered share**: the share of buildings with $\mathrm{cov}_b<1-\alpha-0.05$ (for 90 % intervals, coverage below 0.85), over the window and over the first week (days 1–7). We also report the 10th percentile of $\mathrm{cov}_b$ and the mean absolute coverage deviation $\mathrm{MACD}=\mathrm{mean}_b|\mathrm{cov}_b-(1-\alpha)|$. Per-building coverage is itself an estimate, so we compute, for every building, the standard error of its coverage from its daily coverage values (day blocks preserve the dependence of misses within a day). Under a normal approximation, a perfectly calibrated building would fall below the 0.85 threshold with probability $\Phi(-0.05/\mathrm{SE}_b)$. The average of this probability over buildings is the share of under-covered buildings expected from sampling noise alone, and it is reported as a reference.

*Sharpness.* The median over buildings of the relative interval score and width (medians, because a few erratic buildings dominate means).

*Operational consequence.* Consider an operator that offers, for every building and hour, a day-ahead capacity headroom $\bar P-U$ below a contracted limit $\bar P$, for example to host flexible EV-charging or heat-pump load, and pays a penalty proportional to the violation $(y-U)_+$ whenever the realised load exceeds the planned upper bound $U$. Up to a constant, the relative cost of a building is

$$
\mathrm{cost}_b(\rho_p)=\frac{\overline{U}+\rho_p\,\overline{(y-U)_+}}{\bar y_b}.\qquad\qquad (7)
$$

The upper bound of a calibrated central 90 % interval is the cost-optimal plan for the penalty ratio $\rho_p=20$, because the optimal plan is the $(1-1/\rho_p)$ quantile. We report $\rho_p\in\{10,20,40\}$, and the share of **under-protected** buildings, whose upper bound is exceeded in more than 10 % of the hours (twice the nominal 5 %).

## 3.5 Statistical analysis

The unit of analysis is the target building. A building's metrics are averaged over the seeds in which it was a target, and strategies are compared by two-sided Wilcoxon signed-rank tests [50] on paired per-building values of the absolute coverage deviation over the window and in the first week and of the interval score. $p$-values are Holm-adjusted [51] within each family of comparisons; effect sizes are matched-pairs rank-biserial correlations [52]. Because BDG2 buildings at one site share weather and operation, we additionally test the site means of the paired differences (Wilcoxon over the ten sites) and repeat the building-level test without the largest site. Seed-level results are reported as mean ± standard deviation over seeds.

## 3.6 Protocol, pre-registration and deviations

The splits, seeds, metrics, baselines and the interval-score tuning objective were fixed in an internal analysis protocol before any full experiment was run (released with the code). After a first round of internal review, an addendum was written and committed to the repository *before* the corresponding experiments were run. It added the coverage objective (applied to the proposed layer, ACI and QShrink alike), recency weighting with $\rho=0.95$, stage-wise studentisation, the operational outcomes and the noise reference, and it fixed the rule for the recommended configuration. That rule selects the strategy with the lowest under-covered share, averaged over both datasets, among those whose median interval score is at most 2 % above that of pooled CQR on both datasets. The rule selected HSC-CQR recency. Further deviations, for example the extension of the ACI grid to small step sizes after a code audit, are listed in Supplementary Section S4.


# 4. Results

## 4.1 Pooled calibration leaves many new buildings unreliable

The global LightGBM forecaster reaches a median CV(RMSE) of 0.136 on new BDG2 buildings over their first 56 forecast days (seasonal naive: 0.197; MLP: 0.137) and 0.089 on UCI clients (naive 0.120; MLP 0.087). The forecasters are therefore reasonable; the question is whether their intervals can be trusted building by building.

Table 1 shows that they cannot when calibration is pooled. Conformalised quantile regression (CQR) attains a mean per-building coverage of 0.891 on BDG2, close to the 0.90 target, yet 18.7% of the new buildings have coverage below 0.85, and the 10th percentile of per-building coverage is 0.831. On UCI the share is 9.5%. Direct quantile regression with a neural network (MLP-QR: 20.6% on BDG2) does not solve the problem, and the Gaussian MLP lowers under-coverage (5.6%) only by over-covering on average (0.924) with a median interval score 0.604 instead of 0.564. If every building were perfectly calibrated, sampling noise alone would leave about 1.6% (BDG2) and 0.4% (UCI) of the buildings below 0.85 over the window. Pooled calibration therefore produces more than ten times as many unreliable buildings as sampling noise would. Fig. 3 shows the long lower tails of the per-building coverage distributions.

**Table 1.** Per-building reliability and sharpness of the calibration strategies (random-building protocol, nominal 90 %, 5 seeds; all strategies except MLP-QR/MLP-Gauss use the same LightGBM quantile models and CQR scores). Coverage: mean per-building coverage over the 56-day onboarding window; Under-cov.: share of buildings with coverage < 0.85 (over the window and in the first week); P10: 10th percentile of per-building coverage; Under-prot.: share of buildings whose upper bound is exceeded in more than 10 % of hours (nominal 5 %); Rel. IS: median over buildings of the interval score divided by the building's mean load. Mean ± s.d. over seeds. '(cov)': parameter selected with the per-building coverage objective.

| Data   | Method               | Coverage      | Under-cov. (%)   | Under-cov. wk 1 (%)   | P10 cov.      | Under-prot. (%)   | Rel. IS       |
|:-------|:---------------------|:--------------|:-----------------|:----------------------|:--------------|:------------------|:--------------|
| BDG2   | HSC-CQR recency      | 0.896 ± 0.001 | 0.4 ± 0.3        | 13.7 ± 1.4            | 0.878 ± 0.001 | 1.3 ± 0.2         | 0.570 ± 0.020 |
| BDG2   | HSC-SSC-CQR          | 0.898 ± 0.001 | 0.9 ± 0.9        | 13.1 ± 1.6            | 0.876 ± 0.001 | 1.1 ± 0.3         | 0.571 ± 0.020 |
| BDG2   | SSC-CQR              | 0.899 ± 0.004 | 9.7 ± 1.0        | 20.6 ± 2.6            | 0.852 ± 0.003 | 4.7 ± 1.4         | 0.565 ± 0.022 |
| BDG2   | HSC-CQR simple (cov) | 0.895 ± 0.001 | 1.9 ± 0.8        | 19.4 ± 2.1            | 0.872 ± 0.001 | 2.2 ± 0.6         | 0.567 ± 0.022 |
| BDG2   | HSC-CQR              | 0.891 ± 0.003 | 3.4 ± 0.8        | 24.5 ± 4.2            | 0.864 ± 0.003 | 3.4 ± 1.1         | 0.564 ± 0.024 |
| BDG2   | QShrink-CQR (cov)    | 0.896 ± 0.001 | 1.5 ± 0.8        | 17.2 ± 2.6            | 0.873 ± 0.002 | 1.5 ± 0.6         | 0.567 ± 0.021 |
| BDG2   | QShrink-CQR          | 0.897 ± 0.002 | 4.1 ± 1.6        | 21.5 ± 2.1            | 0.862 ± 0.003 | 3.2 ± 0.9         | 0.562 ± 0.024 |
| BDG2   | Self-CQR             | 0.889 ± 0.002 | 6.1 ± 1.7        | 33.7 ± 1.7            | 0.857 ± 0.003 | 2.3 ± 0.7         | 0.575 ± 0.018 |
| BDG2   | ACI-CQR              | 0.894 ± 0.003 | 8.0 ± 3.7        | 23.8 ± 2.2            | 0.855 ± 0.008 | 3.9 ± 2.2         | 0.563 ± 0.025 |
| BDG2   | ACI-CQR (cov)        | 0.900 ± 0.000 | 0.0 ± 0.0        | 9.1 ± 1.7             | 0.894 ± 0.001 | 0.1 ± 0.2         | 1.110 ± 0.194 |
| BDG2   | TQA-B-CQR            | 0.894 ± 0.003 | 17.0 ± 1.5       | 22.4 ± 1.7            | 0.836 ± 0.002 | 6.2 ± 1.5         | 0.567 ± 0.023 |
| BDG2   | GHCP-CQR             | 0.894 ± 0.004 | 16.8 ± 1.0       | 22.0 ± 1.7            | 0.834 ± 0.003 | 6.2 ± 1.3         | 0.565 ± 0.023 |
| BDG2   | CQR                  | 0.891 ± 0.004 | 18.7 ± 1.8       | 23.8 ± 2.1            | 0.831 ± 0.003 | 6.8 ± 1.3         | 0.564 ± 0.023 |
| BDG2   | MLP-QR               | 0.885 ± 0.010 | 20.6 ± 6.2       | 27.0 ± 6.6            | 0.826 ± 0.015 | 7.9 ± 4.7         | 0.571 ± 0.021 |
| BDG2   | MLP-Gauss            | 0.924 ± 0.009 | 5.6 ± 3.3        | 10.0 ± 5.1            | 0.867 ± 0.013 | 5.4 ± 2.4         | 0.604 ± 0.036 |
| UCI    | HSC-CQR recency      | 0.901 ± 0.002 | 0.0 ± 0.0        | 5.9 ± 1.9             | 0.886 ± 0.003 | 0.2 ± 0.5         | 0.369 ± 0.014 |
| UCI    | HSC-SSC-CQR          | 0.903 ± 0.003 | 0.0 ± 0.0        | 6.7 ± 2.3             | 0.884 ± 0.005 | 0.2 ± 0.5         | 0.368 ± 0.014 |
| UCI    | SSC-CQR              | 0.914 ± 0.006 | 2.5 ± 1.8        | 11.2 ± 2.6            | 0.877 ± 0.011 | 1.3 ± 0.9         | 0.369 ± 0.015 |
| UCI    | HSC-CQR simple (cov) | 0.900 ± 0.002 | 0.2 ± 0.5        | 8.2 ± 1.7             | 0.880 ± 0.005 | 0.4 ± 0.6         | 0.367 ± 0.015 |
| UCI    | HSC-CQR              | 0.898 ± 0.003 | 0.6 ± 0.9        | 17.5 ± 3.8            | 0.878 ± 0.005 | 0.8 ± 0.5         | 0.368 ± 0.016 |
| UCI    | QShrink-CQR (cov)    | 0.901 ± 0.003 | 0.2 ± 0.5        | 9.5 ± 3.3             | 0.882 ± 0.004 | 0.2 ± 0.5         | 0.368 ± 0.015 |
| UCI    | QShrink-CQR          | 0.902 ± 0.005 | 1.7 ± 2.4        | 14.5 ± 3.4            | 0.879 ± 0.011 | 0.6 ± 0.6         | 0.367 ± 0.015 |
| UCI    | Self-CQR             | 0.896 ± 0.002 | 1.3 ± 1.9        | 23.2 ± 5.5            | 0.871 ± 0.002 | 0.6 ± 0.6         | 0.372 ± 0.014 |
| UCI    | ACI-CQR              | 0.903 ± 0.005 | 3.6 ± 3.1        | 15.4 ± 3.4            | 0.871 ± 0.011 | 0.6 ± 0.6         | 0.366 ± 0.015 |
| UCI    | ACI-CQR (cov)        | 0.901 ± 0.001 | 0.0 ± 0.0        | 5.3 ± 3.0             | 0.895 ± 0.001 | 0.0 ± 0.0         | 0.431 ± 0.037 |
| UCI    | TQA-B-CQR            | 0.900 ± 0.007 | 9.1 ± 4.1        | 14.3 ± 3.4            | 0.857 ± 0.014 | 2.1 ± 1.3         | 0.368 ± 0.013 |
| UCI    | GHCP-CQR             | 0.906 ± 0.010 | 7.8 ± 3.6        | 13.1 ± 3.5            | 0.864 ± 0.016 | 1.1 ± 0.7         | 0.369 ± 0.016 |
| UCI    | CQR                  | 0.899 ± 0.011 | 9.5 ± 4.3        | 16.0 ± 3.8            | 0.856 ± 0.016 | 2.5 ± 1.2         | 0.368 ± 0.015 |
| UCI    | MLP-QR               | 0.889 ± 0.013 | 13.3 ± 8.6       | 20.0 ± 4.7            | 0.849 ± 0.022 | 2.1 ± 2.0         | 0.379 ± 0.017 |
| UCI    | MLP-Gauss            | 0.927 ± 0.005 | 2.5 ± 1.6        | 8.2 ± 5.4             | 0.885 ± 0.011 | 2.5 ± 1.9         | 0.394 ± 0.017 |


![**Fig. 3.** Empirical distribution of per-building coverage over the 56-day onboarding window (all target buildings of all five seeds; dashed: nominal 0.90; dotted: 0.85).](figures/Fig4_coverage_cdf.png){width=16.5cm}

## 4.2 Building-adaptive calibration strategies compared

All strategies in this subsection use the same quantile models and CQR scores; they differ only in how a new building's own scores enter the calibration. The recency-weighted shrinkage layer (HSC-CQR recency) leaves 0.4% of the BDG2 buildings and 0.0% of the UCI clients under-covered, which is within the sampling-noise reference of 1.2% and 0.3%. The 10th percentile of per-building coverage rises from 0.831 to 0.878 (BDG2). Its median interval score differs from pooled CQR by +0.9% (BDG2) and +0.3% (UCI). Paired per building, the layer reduces the absolute coverage deviation for 90% of the BDG2 buildings (rank-biserial $r$ = 0.93, Holm-adjusted $p$ < 0.001) and 86% of the UCI clients, while the interval scores are statistically indistinguishable from CQR's (Holm-adjusted $p$ = 1.000 on BDG2 and = 1.000 on UCI). On BDG2, every reliability comparison in this section is also significant when the ten site means are tested ($p \le$ 0.006) and when the largest site is excluded (Supplementary Table S5).

The competing mechanisms behave as their designs suggest (Table 1). *Self-calibration* (Self-CQR) is reliable later in the window but leaves 33.7% of the BDG2 buildings under-covered in the first week, when a few dozen own scores yield noisy quantiles. *Temporal quantile adjustment* (TQA-B-CQR: 17.0%) and *GHCP-style pooling* (GHCP-CQR: 16.8%) remain close to pooled CQR. TQA bounds its adjustment by design, and GHCP never gives the new building more weight than one reference building, which secures marginal validity across buildings but cannot correct a building whose errors are systematically larger than average. *Quantile shrinkage* is the closest competitor. Tuned with the same coverage objective (QShrink-CQR (cov)), it leaves 1.5% and 0.2% under-covered. The proposed layer has the smaller coverage deviation for 77% of the BDG2 buildings ($p$ < 0.001), at a slightly higher interval score (better for 32% of the buildings). *Online level control* (ACI-CQR) tuned for the interval score selects small step sizes and leaves 8.0% of the BDG2 buildings under-covered. Tuned for coverage, it selects the largest step size of the grid ($\gamma$ = 0.01) and reaches nominal coverage for almost every building, but its median interval score nearly doubles (1.110 vs 0.564). Its intervals alternate between very wide and very narrow as the level is pushed up and down. Under the pre-specified sharpness constraint (Section 3.6), this variant is not eligible.

## 4.3 Onboarding dynamics and the reliability–sharpness frontier

Fig. 4 resolves reliability by week. In the first week, pooled CQR leaves 23.8% (BDG2) and 16.0% (UCI) of the buildings under-covered. ACI-CQR does not change this (23.8% and 15.4%), and the shrinkage layer without recency improves it only partly (19.4% and 8.2%). The recency-weighted layer reduces these shares to 13.7% and 5.9%. From the second week on it stays close to the level expected for perfectly calibrated intervals (18.7% on BDG2 for weekly coverage, which is noisier than coverage over the window), while pooled calibration stays several points above that level in every week.

![**Fig. 4.** Share of buildings whose coverage in a given week after metering started is below 0.85 (main protocol, five seeds). Dotted: share expected from sampling noise if every building were perfectly calibrated (normal approximation with each building's day-block standard error, weekly scale).](figures/Fig_weekly.png){width=16.5cm}

Fig. 5 maps every strategy family over its full parameter grid on the target buildings. This is for transparency only; nothing was selected on target buildings. Over the whole window, the families reach similar endpoints (panels a, b). Shrinkage with or without recency, quantile shrinkage and ACI at a well-chosen step size ($\gamma$ = 0.002: 0.1% under-covered on BDG2) can all bring the under-covered share close to zero without loss of sharpness. Two differences remain. First, ACI attains this only in a narrow band of step sizes. One grid step further ($\gamma$ = 0.005), the median interval score rises by +8% on BDG2, and at $\gamma$ = 0.01 by +97%. The shrinkage families degrade gracefully over almost two orders of magnitude of $\kappa$. Second, and decisive for onboarding, the families differ in the first week (panels c, d). No ACI step size that preserves sharpness brings the first-week share below 22.7% on BDG2, whereas the recency-weighted shrinkage family reaches 13.7% at $\kappa$ = 48 h. Leave-one-building-out selection chose $\kappa$ = 48 h on BDG2 and 24, 48 h on UCI.

![**Fig. 5.** Reliability–sharpness frontier. Each line is a calibration family evaluated over its full parameter grid on the target buildings (mean over five seeds): score shrinkage with own-score decay ρ ∈ {1, 0.95, 0.9, 0.8} per day over κ, quantile shrinkage over λ, and ACI over γ. x: change of the median relative interval score versus pooled CQR; y: under-covered buildings over the 56-day window (a, b) and in the first week (c, d). Lower left is better. κ = λ = 0 (own scores only) are omitted because the radius is undefined in the first days.](figures/Fig_frontier.png){width=16.5cm}

## 4.4 Which design elements matter

Fig. 6 isolates the elements of the layer. *Shrinkage* is indispensable: without it ($\kappa=\infty$), 21.7% of the BDG2 buildings remain under-covered. *The selection objective* matters next. Selected by the interval score, the pseudo-count of the layer without recency was 336 h on BDG2 (HSC-CQR simple: 2.9% under-covered); selected by per-building coverage it was 168, 96 h (1.9%). The interval score is almost flat in $\kappa$ (Fig. 5), so it gives little guidance on per-building reliability. *Recency weighting* then reduces the remaining under-coverage from 1.9% to 0.4% (BDG2) and acts above all in the first week (13.7% vs 19.4% on BDG2; 5.9% vs 8.2% on UCI). Compared with a fixed one-week pseudo-count without recency, the donor–local mixture of [37] (HSC-CQR fixed-κ: 1.9%), the proposed layer reduces the coverage deviation for 77% of the BDG2 buildings ($p$ < 0.001) at a slightly higher interval score.

Three refinements do not help. The similarity-localised population distribution and onboarding-stage matching (HSC-CQR: 3.4%) add nothing over the stage-agnostic simple variant. After normalisation by scale and conditioning of the forecaster on history-derived features, the remaining between-building differences in score distributions appear to be driven by events rather than by load shape, and the forecaster already knows how much history it has. Stage-wise studentisation alone (SSC-CQR) leaves 9.7% of the BDG2 buildings under-covered despite its stage-wise guarantee across buildings (Proposition 1). Coverage averaged over new buildings at every day does not imply coverage for each building. Combined with shrinkage (HSC-SSC-CQR), studentisation matches the proposed layer in median terms (0.9%), but a few buildings with a large running error scale receive extremely wide intervals. Its *mean* capacity-headroom cost is +61.1% above CQR's (Table 3), a tail failure that the medians hide.

![**Fig. 6.** Design elements of the calibration layer: share of under-covered buildings over the window (a) and in the first week (b), mean ± s.d. over five seeds. From left: proposed layer (recency, coverage objective); with stage-wise studentisation; without recency (coverage objective); fixed κ = 168 h; without recency (interval-score objective); with stage matching and similarity prior (interval-score objective); without shrinkage (κ = ∞); own scores only (κ = 0); pooled CQR.](figures/Fig6_ablation.png){width=16.5cm}

## 4.5 Robustness and generalisation

Table 2 stresses the strategies. Among the strategies in Table 2, the recency-weighted layer has the lowest under-covered share in every condition (with ties for self-calibration at 15 % meter noise and for quantile shrinkage in the BDG2 → UCI transfer), and its median interval score stays within ±1.5 % of pooled CQR's. Only the studentised variant HSC-SSC-CQR, which has the tail failure described above, is lower in two conditions (1.3% with the smallest calibration pool and 0.0% at 15 % noise). Pooled calibration from clean calibration buildings breaks down when the new buildings' meters are noisy (CQR: 30.7% under-covered at 15 % noise). The layer is unaffected (0.1%) because the building's own, noisy scores enter the mixture. Abrupt level changes of ±40 % at day 28 are the hardest stress for shrinkage without recency, because pre-change scores remain in the calibration. Recency weighting limits their influence (0.8% and 1.2% under-covered, versus 2.8% and 3.0% without recency). A very small calibration pool (16 buildings) raises the share to 2.5%, and a forecaster trained on 10 % of the training buildings to 0.7% (CQR: 25.0%).

**Table 2.** Robustness and generalisation: share of under-covered buildings (%, coverage < 0.85 over the 56-day window), mean over runs (stress tests: 3 seeds on BDG2; unseen sites: 5 folds; cross-dataset: 3 seeds, no weather features). Last column: change of the median relative interval score of HSC-CQR recency versus pooled CQR. MLP-QR is not available for the weak-forecaster condition ('–').

| Condition                    |   Runs |   HSC-CQR recency |   QShrink-CQR (cov) |   HSC-CQR simple (cov) |   ACI-CQR |   Self-CQR |   CQR | MLP-QR   |   Δ rel. IS vs CQR (%) |
|:-----------------------------|-------:|------------------:|--------------------:|-----------------------:|----------:|-----------:|------:|:---------|-----------------------:|
| Meter noise 5 %              |      3 |               0.1 |                 1.1 |                    0.9 |       8.3 |        1.8 |  16.9 | 19.2     |                    0   |
| Meter noise 15 %             |      3 |               0.1 |                 0.5 |                    0.4 |      10.4 |        0.1 |  30.7 | 26.4     |                   -1.3 |
| Missing hours 20 %           |      3 |               0.7 |                 1.7 |                    1.8 |       9.9 |        5.9 |  17.5 | 33.5     |                    0.7 |
| Missing hours 40 %           |      3 |               0.9 |                 2.2 |                    2.4 |      12   |        5.5 |  16.9 | 47.0     |                   -0.3 |
| Level shift +40 % (day 28)   |      3 |               0.8 |                 2   |                    2.8 |      16.3 |        7.9 |  30.3 | 31.4     |                    1.4 |
| Level shift −40 % (day 28)   |      3 |               1.2 |                 2.4 |                    3   |      10.9 |        8.6 |  28.6 | 19.5     |                    0.6 |
| Calibration pool 10 %        |      3 |               2.5 |                 2.8 |                    4.5 |      10.1 |        7   |  21.6 | 19.6     |                   -0.1 |
| Calibration pool 25 %        |      3 |               0.5 |                 1.6 |                    1.8 |       3   |        6.6 |  17.5 | 19.6     |                    1.5 |
| Weak forecaster              |      3 |               0.7 |                 2.8 |                    2.8 |       7.1 |        7.6 |  25   | –        |                   -0.2 |
| Unseen sites (BDG2, 5 folds) |      5 |               0.4 |                 1.7 |                    1.4 |       8.4 |        6.3 |  21.8 | 25.0     |                   -0.4 |
| BDG2 → BDG2, no weather      |      3 |               0.1 |                 0.9 |                    1.3 |       4.2 |        7.4 |  17.4 | 12.6     |                    0.6 |
| BDG2 → UCI (Portugal)        |      3 |               0   |                 0   |                    0.4 |       1.1 |        2.1 |   5.6 | 3.2      |                   -0.1 |
| UCI → BDG2                   |      3 |               1.2 |                 3.3 |                    3.2 |      20.9 |        6.9 |  41.8 | 43.2     |                   -1.3 |


On campuses from which no training or calibration building comes (leave-site-out), 0.4% of the buildings are under-covered (CQR 21.8%). With models and calibration scores from BDG2 applied to Portuguese UCI clients, the share is 0.0% (CQR 5.6%). The opposite direction is much harder: a model and calibration population from UCI clients, without weather information, leave 41.8% of the BDG2 buildings under-covered with CQR and 1.2% with the layer. Under such transfer the population distribution is a poor prior and the gain rests mainly on the building's own scores, but the layer still outperforms self-calibration (6.9%), which suffers in the first week. Results at nominal 95 % and 80 % show the same ordering, with one exception: at 80 % on BDG2, ACI-CQR leaves fewer buildings under-covered (1.3%) than the layer (3.2%) (Supplementary Tables S6–S9).

## 4.6 Operational consequences and computational cost

Table 3 translates the intervals into day-ahead capacity-headroom offers planned on the upper bound. With pooled CQR, 6.8% of the BDG2 buildings and 2.5% of the UCI clients have their upper bound exceeded more than twice as often as stated. With the recency-weighted layer, these shares fall to 1.3% and 0.2%. The *average* cost changes little: +1.8%, +0.8% and -0.8% on BDG2 for penalty ratios of 10, 20 and 40 (UCI: +0.5%, -0.1%, -1.2%). The layer does not make the portfolio cheaper on average. It redistributes risk: the planning margin moves from regular buildings, which pooled calibration over-protects, to volatile buildings, which it under-protects, so that no building systematically violates its stated reliability. The higher the penalty for violations, the more this pays off. Aggressive online level control (ACI-CQR (cov)) achieves even fewer under-protected buildings, but at +31.2% higher cost on BDG2.

**Table 3.** Operational consequence: day-ahead capacity-headroom offers planned on the upper bound (Eq. 9). Upper exceed.: mean share of hours above the upper bound (nominal 5 %); Under-prot.: share of buildings with more than 10 % exceedance; Cost Δ: change of the mean relative cost (planning load + ρ × violation) versus pooled CQR for penalty ratios ρ (ρ = 20 is cost-optimal for a calibrated 95 % upper bound); mean ± s.d. over seeds.

| Data   | Method               | Upper exceed. (%)   | Under-prot. (%)   | Cost Δ ρ=10 (%)   | Cost Δ ρ=20 (%)   | Cost Δ ρ=40 (%)   |
|:-------|:---------------------|:--------------------|:------------------|:------------------|:------------------|:------------------|
| BDG2   | HSC-CQR recency      | 5.1 ± 0.2           | 1.3 ± 0.2         | +1.8 ± 1.5        | +0.8 ± 1.4        | -0.8 ± 1.3        |
| BDG2   | HSC-SSC-CQR          | 5.0 ± 0.2           | 1.1 ± 0.3         | +66.7 ± 123.1     | +61.1 ± 114.5     | +52.1 ± 100.5     |
| BDG2   | SSC-CQR              | 5.0 ± 0.3           | 4.7 ± 1.4         | +0.4 ± 0.2        | -0.1 ± 0.1        | -0.9 ± 0.2        |
| BDG2   | HSC-CQR simple (cov) | 5.2 ± 0.2           | 2.2 ± 0.6         | +0.7 ± 0.5        | -0.0 ± 0.5        | -1.2 ± 0.5        |
| BDG2   | HSC-CQR              | 5.3 ± 0.3           | 3.4 ± 1.1         | +0.1 ± 0.0        | -0.3 ± 0.1        | -1.1 ± 0.2        |
| BDG2   | QShrink-CQR (cov)    | 5.1 ± 0.2           | 1.5 ± 0.6         | +1.3 ± 0.9        | +0.5 ± 0.8        | -1.0 ± 0.6        |
| BDG2   | QShrink-CQR          | 5.1 ± 0.2           | 3.2 ± 0.9         | +0.4 ± 0.2        | -0.1 ± 0.1        | -1.0 ± 0.2        |
| BDG2   | Self-CQR             | 5.3 ± 0.2           | 2.3 ± 0.7         | +2.8 ± 2.1        | +1.7 ± 1.9        | -0.0 ± 1.7        |
| BDG2   | ACI-CQR              | 5.2 ± 0.3           | 3.9 ± 2.2         | +0.2 ± 0.3        | -0.1 ± 0.2        | -0.5 ± 0.1        |
| BDG2   | ACI-CQR (cov)        | 4.8 ± 0.2           | 0.1 ± 0.2         | +34.9 ± 6.9       | +31.2 ± 6.4       | +25.1 ± 5.7       |
| BDG2   | TQA-B-CQR            | 5.1 ± 0.3           | 6.2 ± 1.5         | +0.2 ± 0.1        | +0.1 ± 0.1        | -0.3 ± 0.1        |
| BDG2   | GHCP-CQR             | 5.1 ± 0.3           | 6.2 ± 1.3         | +0.1 ± 0.0        | -0.0 ± 0.0        | -0.1 ± 0.0        |
| BDG2   | CQR                  | 5.3 ± 0.3           | 6.8 ± 1.3         | +0.0 ± 0.0        | +0.0 ± 0.0        | +0.0 ± 0.0        |
| BDG2   | MLP-QR               | 5.6 ± 0.7           | 7.9 ± 4.7         | +0.0 ± 0.4        | -0.1 ± 0.5        | -0.3 ± 1.4        |
| BDG2   | MLP-Gauss            | 4.3 ± 0.5           | 5.4 ± 2.4         | +5.2 ± 3.2        | +4.1 ± 2.9        | +2.3 ± 2.9        |
| UCI    | HSC-CQR recency      | 5.0 ± 0.2           | 0.2 ± 0.5         | +0.5 ± 0.4        | -0.1 ± 0.4        | -1.2 ± 0.9        |
| UCI    | HSC-SSC-CQR          | 4.9 ± 0.1           | 0.2 ± 0.5         | +2.5 ± 4.3        | +1.7 ± 4.2        | +0.4 ± 4.1        |
| UCI    | SSC-CQR              | 4.4 ± 0.2           | 1.3 ± 0.9         | +0.3 ± 0.2        | -0.2 ± 0.3        | -1.0 ± 0.6        |
| UCI    | HSC-CQR simple (cov) | 5.0 ± 0.2           | 0.4 ± 0.6         | +0.3 ± 0.3        | -0.2 ± 0.4        | -1.0 ± 0.7        |
| UCI    | HSC-CQR              | 5.1 ± 0.3           | 0.8 ± 0.5         | +0.0 ± 0.1        | -0.2 ± 0.2        | -0.6 ± 0.4        |
| UCI    | QShrink-CQR (cov)    | 5.0 ± 0.2           | 0.2 ± 0.5         | +0.4 ± 0.4        | -0.2 ± 0.5        | -1.1 ± 0.8        |
| UCI    | QShrink-CQR          | 4.9 ± 0.2           | 0.6 ± 0.6         | +0.1 ± 0.1        | -0.2 ± 0.2        | -0.7 ± 0.4        |
| UCI    | Self-CQR             | 5.1 ± 0.2           | 0.6 ± 0.6         | +0.8 ± 0.6        | +0.2 ± 0.6        | -0.9 ± 1.0        |
| UCI    | ACI-CQR              | 4.9 ± 0.1           | 0.6 ± 0.6         | +0.2 ± 0.6        | +0.0 ± 0.6        | -0.4 ± 0.9        |
| UCI    | ACI-CQR (cov)        | 4.9 ± 0.2           | 0.0 ± 0.0         | +18.9 ± 16.7      | +17.2 ± 16.4      | +14.1 ± 15.7      |
| UCI    | TQA-B-CQR            | 4.8 ± 0.1           | 2.1 ± 1.3         | +0.0 ± 0.1        | -0.1 ± 0.1        | -0.2 ± 0.3        |
| UCI    | GHCP-CQR             | 4.6 ± 0.2           | 1.1 ± 0.7         | +0.1 ± 0.0        | +0.0 ± 0.0        | -0.2 ± 0.0        |
| UCI    | CQR                  | 4.8 ± 0.2           | 2.5 ± 1.2         | +0.0 ± 0.0        | +0.0 ± 0.0        | +0.0 ± 0.0        |
| UCI    | MLP-QR               | 4.7 ± 0.9           | 2.1 ± 2.0         | -0.5 ± 0.8        | -0.9 ± 1.7        | -1.4 ± 3.7        |
| UCI    | MLP-Gauss            | 4.5 ± 0.6           | 2.5 ± 1.9         | +0.7 ± 1.0        | +0.1 ± 1.8        | -1.0 ± 3.5        |


Once the scores are stored, the layer adds 0.015 ms per building-day on one CPU core (BDG2; pooled CQR: 0.0005 ms). The calibration store needs 18.8 MB for about 170 calibration buildings, and leave-one-building-out selection of $\kappa$ takes 1.0 s. Both are negligible next to training the three LightGBM models (56 s on four cores) and allow portfolio-scale deployment.

## 4.7 Where the layer still fails

With pooled CQR, a building's coverage falls with its forecast difficulty (Spearman correlation between per-building coverage and CV(RMSE): -0.65 on BDG2, -0.55 on UCI); with the proposed layer the correlation is -0.06 and -0.02 (Fig. 7a). Across usage classes with at least 30 building × seed units, the largest reduction of the absolute coverage deviation is observed for 'Public services' and the smallest for 'Lodging/residential' (Fig. 7b). Of the 1265 BDG2 building × seed units, 5 remain under-covered; their median within-window level change |log(mean load weeks 5–8 / weeks 1–4)| is 0.251 versus 0.054 for the others (Mann–Whitney p = 0.071), and their first-week volatility is 0.012 versus 0.113 (p = 0.005). With so few failures, these comparisons are not conclusive. On UCI, 0 of 475 units remain under-covered. Fig. 8 shows the intervals for two pre-specified buildings: the one at the 10th percentile and the one at the median of per-building CQR coverage.

![**Fig. 7.** Error analysis on BDG2: (a) per-building coverage versus point-forecast CV(RMSE) of the building (log scale) for pooled CQR and the proposed layer; (b) mean coverage by primary usage (usage classes with at least 30 building × seed units).](figures/Fig10_error_analysis.png){width=16.5cm}

![**Fig. 8.** Day-ahead 90 % intervals for two pre-specified BDG2 buildings during their first 10 forecast days (seed 0): the building at the 10th percentile (a) and at the median (b) of per-building CQR coverage. Markers show observations outside the respective interval.](figures/Fig11_examples.png){width=16.5cm}


# 5. Discussion

## 5.1 Why pooled calibration fails per building, and what makes the layer work

A global forecaster normalised by building scale produces scores that are comparable *on average* across buildings, but not identically distributed. Some buildings have regular schedules and small errors; others have irregular occupancy, plug loads or weather sensitivity that the first days of data cannot reveal. A pooled quantile is a compromise that over-covers the former and under-covers the latter. In our data, pooled CQR coverage falls with forecast difficulty (Spearman correlation with CV(RMSE): -0.65 on BDG2), whereas with the recency-weighted layer coverage is almost independent of it (-0.06). Reliability is no longer something that only easy buildings receive.

The results identify three ingredients. The first is shrinkage of the score *distribution* towards the building's own scores. Mixing distributions, rather than quantiles, lets the first own scores shift the whole tail gradually. The second is a pseudo-count selected for the quantity that matters. The interval score is almost flat in $\kappa$ and therefore gives little guidance, whereas per-building coverage on calibration buildings selected 48 h (BDG2) and 24, 48 h (UCI), i.e. one to two days of hourly scores, for the recency-weighted layer. The third is recency weighting. It keeps the population prior active in the background (the effective number of own scores is bounded by $1/(1-\rho)$) and lets the most recent errors dominate the building's own contribution, which helps both in the first week and after abrupt changes. Online level control can match the window-level reliability of this layer at a well-chosen step size, but only in a narrow band of step sizes, and it cannot repair the first week. Its feedback signal, the binary miss indicator, carries too little information when the starting point is poor. Hierarchical pooling (GHCP) and temporal quantile adjustment secure validity across buildings or bound their adjustment by design. These are sound choices for exchangeable groups, but they cannot correct a building whose errors are systematically larger than average.

The stage-wise studentised variant illustrates a distinction that is easy to overlook. Its guarantee of coverage on average over new buildings at every onboarding day (Proposition 1) is the strongest formal property among the methods studied, yet it leaves many individual buildings under-covered. A per-building target needs per-building information, and no population-level guarantee can substitute for it [30].

## 5.2 Practical implications

For aggregators, utilities and demand-response platforms that onboard buildings continuously, the results support a simple operating rule: calibrate the intervals of a global forecaster with CQR scores of previously onboarded buildings, mix in each new building's own scores with an exponential forgetting factor of about 0.95 per day, and select the pseudo-count by leave-one-building-out on the per-building coverage of previously onboarded buildings. This rule has three practical consequences.

1. **Reliability from the first weeks.** The share of new buildings with clearly unreliable intervals falls to the level expected from sampling noise from the second week on, and the first-week share falls from 23.8% to 13.7% (BDG2) and from 16.0% to 5.9% (UCI). Applications that rely on intervals at enrolment, such as demand-response baselines, flexibility offers and anomaly alarms, can therefore use them weeks earlier than under self-calibration. Measurement-and-verification practice typically relies on long baseline periods [2], and the layer provides reliable day-ahead uncertainty well before such baselines exist.
2. **Risk redistribution, not cost reduction.** Average headroom cost is essentially unchanged, but the planning margin is reassigned from regular to volatile buildings, and under-protected buildings, those whose stated reliability is violated systematically, almost disappear. Where contracts, settlement rules or customer trust are building-specific, this is the relevant improvement.
3. **Negligible cost and easy integration.** The layer is closed-form, needs one parameter selected in seconds, adds well under a millisecond per building-day and works on top of different forecasters (LightGBM and MLP quantiles here), including pretrained forecasting models. It needs no metadata about the new building.

## 5.3 Limitations and future work

1. **No finite-sample guarantee for the recommended layer.** Its reliability is established empirically, across two datasets, unseen sites, cross-country transfer and stress tests. Distribution-free per-building validity is impossible in general [30], and the stage-wise guarantee of Proposition 1 does not translate into per-building reliability. Combining shrinkage with a formal per-building safeguard is an open problem.
2. **The first week remains the hardest period.** 13.7% of the BDG2 buildings are still under-covered over their first week. Until own data accumulate, every strategy can only be as reliable as the information available, which suggests using metadata or pretrained-model uncertainty in the population distribution.
3. **Simulated onboarding and observed weather.** Onboarding dates were sampled within existing meter histories, and BDG2 experiments use observed temperature as a stand-in for weather forecasts. Real enrolment can coincide with commissioning problems that our level-shift tests only approximate. The experiments without weather show the same ordering.
4. **Data coverage.** BDG2 consists mostly of campus buildings in North America and Europe, and UCI has no metadata. Residential portfolios, industrial sites, other climates and sub-hourly resolutions remain to be tested.
5. **Baselines.** Large pretrained probabilistic forecasters [14] were not run because of the CPU-only budget, and the GHCP and TQA baselines are adaptations of methods designed for other settings (Supplementary Section S3).
6. **Fixed decay factor.** The forgetting factor was fixed a priori at 0.95 per day. The frontier analysis shows that 0.8–0.95 perform similarly, but selecting it jointly with the pseudo-count was not studied.
7. **Decision model.** The capacity-headroom case is deliberately simple. Market-specific settlement rules, correlated errors across buildings in a portfolio and the joint calibration of many buildings' intervals for portfolio-level bids are natural extensions.

# 6. Conclusion

Day-ahead load intervals are needed from the first days after a building is metered, and they must be reliable for each building, not only on average. Across 1,157 buildings and clients from two public datasets, pooled conformal and quantile-regression intervals left a substantial share of new buildings under-covered although their average coverage was close to nominal. A recency-weighted shrinkage of the nonconformity-score distribution towards each building's own scores, with the pseudo-count selected for per-building coverage, reduced the share of under-covered new buildings from 18.7% to 0.4% (BDG2) and from 9.5% to 0.0% (UCI), within the level expected from sampling noise. It reduced first-week unreliability from 23.8% to 13.7% (BDG2) and from 16.0% to 5.9% (UCI), at an interval score within +0.9% of pooled CQR. The improvement held on unseen sites, after cross-country transfer, under meter noise, missing data, abrupt level changes, small calibration pools and a weak forecaster, and for a neural quantile model. Online level control and quantile shrinkage reach similar window-level reliability only at well-chosen parameters and do not repair the first week. Similarity priors and onboarding-stage matching are unnecessary. A stage-wise population guarantee does not imply per-building reliability. For operators, the layer does not reduce average cost; it removes systematically under-protected buildings at negligible computational cost. Future work should add formal per-building safeguards, use metadata or pretrained-model uncertainty for the first days, and extend the decision analysis to portfolio-level flexibility bids.


# CRediT authorship contribution statement

**[Author 1]:** Conceptualization, Methodology, Software, Formal analysis, Investigation, Data curation, Writing – original draft, Visualization. **[Author 2]:** Supervision, Writing – review & editing. *(To be completed by the authors.)*

# Declaration of competing interest

The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

# Declaration of generative AI and AI-assisted technologies in the manuscript preparation process

During the preparation of this work the author(s) used Claude (Anthropic) in order to support literature screening, software development, running the experiments and drafting the text. Every reported number is generated automatically from the released code and result files. After using this tool/service, the author(s) reviewed and edited the content as needed and take(s) full responsibility for the content of the publication. *(Authors: verify that this statement matches your actual use and the journal's current policy.)*

# Data and code availability

Both datasets are public. BDG2 (CC-BY-4.0) is available at https://github.com/buds-lab/building-data-genome-project-2 [42], and ElectricityLoadDiagrams20112014 (CC-BY-4.0) at https://doi.org/10.24432/C58C86 [44]. The complete code (data download and cleaning, models, the calibration layer, all baselines, experiments, statistics, figures, tables and this manuscript's numbers) is provided as supplementary material and will be released in a public repository [repository URL to be inserted upon acceptance]. `python run_all.py --mode full` reproduces all results.

# Acknowledgements

*(To be completed by the authors; no specific funding was received for this work unless stated here.)*

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
20. Suresh V, Swain A, Revathi BS, Guerrero JM. Mamba based adaptive conformal inference for probabilistic short-term load forecasting. Knowl Based Syst 2025;328:114222. https://doi.org/10.1016/j.knosys.2025.114222.
21. Shi L, Shen Z, Lyu T. Local online conformal prediction for power load forecasting intervals. Electr Power Syst Res 2026;261:113412. https://doi.org/10.1016/j.epsr.2026.113412.
22. Moradi A, Tanneau M, Zandehshahvar R, Van Hentenryck P. Enhanced renewable energy forecasting using context-aware conformal prediction. arXiv:2510.15780 [Preprint]; 2025. https://doi.org/10.48550/arXiv.2510.15780.
23. Almeida V, Gama J. Prediction intervals for electric load forecast: Evaluation for different profiles. In: 2015 18th International Conference on Intelligent System Application to Power Systems (ISAP); 2015. https://doi.org/10.1109/isap.2015.7325539.
24. Gibbs I, Cherian JJ, Candès EJ. Conformal prediction with conditional guarantees. J R Stat Soc Series B Stat Methodol 2025;87:1100–26. https://doi.org/10.1093/jrsssb/qkaf008.
25. Ding T, Angelopoulos AN, Bates S, Jordan MI, Tibshirani RJ. Class-conditional conformal prediction with many classes. In: Advances in Neural Information Processing Systems 36 (NeurIPS 2023); 2023.
26. Gibbs I, Candès E. Adaptive conformal inference under distribution shift. In: Advances in Neural Information Processing Systems 34 (NeurIPS 2021); 2021.
27. Zaffran M, Féron O, Goude Y, Josse J, Dieuleveut A. Adaptive conformal predictions for time series. In: Proceedings of the 39th International Conference on Machine Learning, PMLR 162; 2022, p. 25834–66.
28. Barber RF, Candès EJ, Ramdas A, Tibshirani RJ. Conformal prediction beyond exchangeability. Ann Stat 2023;51:816–45. https://doi.org/10.1214/23-AOS2276.
29. Lin Z, Trivedi S, Sun J. Conformal prediction with temporal quantile adjustments. In: Advances in Neural Information Processing Systems 35 (NeurIPS 2022); 2022.
30. Lin Z, Trivedi S, Sun J. Conformal prediction intervals with temporal dependence. Trans Mach Learn Res 2022. https://doi.org/10.48550/arXiv.2205.12940.
31. Dunn R, Wasserman L, Ramdas A. Distribution-free prediction sets for two-layer hierarchical models. J Am Stat Assoc 2023;118:2491–502. https://doi.org/10.1080/01621459.2022.2060112.
32. Lee Y, Barber RF, Willett R. Distribution-free inference with hierarchical data. arXiv:2306.06342 [Preprint]; 2023. https://doi.org/10.48550/arXiv.2306.06342.
33. Mallick S, Tchetgen Tchetgen E, Dobriban E, Lee Y. Generalized hierarchical conformal prediction. arXiv:2608.15500 [Preprint]; 2026. https://doi.org/10.48550/arXiv.2608.15500.
34. Shahid NF. When average calibration fails: Site-conditional federated conformal risk control. arXiv:2606.20115 [Preprint]; 2026. https://doi.org/10.48550/arXiv.2606.20115.
35. Rafe A, Das S. Socio-conformal calibration in complex survey data: Marginal validity is not enough for subgroup reliability. arXiv:2605.05562 [Preprint]; 2026. https://doi.org/10.48550/arXiv.2605.05562.
36. Zhang Z, Lu Z, Yang H. The benefit of being Bayesian in online conformal prediction. arXiv:2410.02561 [Preprint]; 2024. https://doi.org/10.48550/arXiv.2410.02561.
37. Jeon B. coldstart-conformal-solar: Analysis code for auditing cold-start conformal prediction intervals of solar irradiance forecasts at unseen stations (v1.2) [software]. Zenodo; 2026. https://doi.org/10.5281/zenodo.24002627.
38. Hong L. Conformal prediction credibility intervals. N Am Actuar J 2023;27:675–88. https://doi.org/10.1080/10920277.2022.2123364.
39. Koenker R, Bassett G. Regression quantiles. Econometrica 1978;46:33–50. https://doi.org/10.2307/1913643.
40. Tibshirani RJ, Barber RF, Candès E, Ramdas A. Conformal prediction under covariate shift. In: Advances in Neural Information Processing Systems 32 (NeurIPS 2019); 2019.
41. Ferguson TS. A Bayesian analysis of some nonparametric problems. Ann Stat 1973;1:209–30. https://doi.org/10.1214/aos/1176342360.
42. Miller C, Kathirgamanathan A, Picchetti B, Arjunan P, Park JY, Nagy Z, et al. The Building Data Genome Project 2, energy meter data from the ASHRAE Great Energy Predictor III competition. Sci Data 2020;7:368. https://doi.org/10.1038/s41597-020-00712-x.
43. Miller C, Arjunan P, Kathirgamanathan A, Fu C, Roth J, Park JY, et al. The ASHRAE Great Energy Predictor III competition: Overview and results. Sci Technol Built Environ 2020;26:1427–47. https://doi.org/10.1080/23744731.2020.1795514.
44. Trindade A. ElectricityLoadDiagrams20112014 [dataset]. UCI Machine Learning Repository; 2015. https://doi.org/10.24432/C58C86.
45. Ke G, Meng Q, Finley T, Wang T, Chen W, Ma W, et al. LightGBM: A highly efficient gradient boosting decision tree. In: Advances in Neural Information Processing Systems 30 (NIPS 2017); 2017.
46. Wang Y, Gan D, Sun M, Zhang N, Lu Z, Kang C. Probabilistic individual load forecasting using pinball loss guided LSTM. Appl Energy 2019;235:10–20. https://doi.org/10.1016/j.apenergy.2018.10.078.
47. Salinas D, Flunkert V, Gasthaus J, Januschowski T. DeepAR: Probabilistic forecasting with autoregressive recurrent networks. Int J Forecast 2020;36:1181–91. https://doi.org/10.1016/j.ijforecast.2019.07.001.
48. Winkler RL. A decision-theoretic approach to interval estimation. J Am Stat Assoc 1972;67:187–91. https://doi.org/10.1080/01621459.1972.10481224.
49. Gneiting T, Raftery AE. Strictly proper scoring rules, prediction, and estimation. J Am Stat Assoc 2007;102:359–78. https://doi.org/10.1198/016214506000001437.
50. Wilcoxon F. Individual comparisons by ranking methods. Biometrics Bull 1945;1:80–3. https://doi.org/10.2307/3001968.
51. Holm S. A simple sequentially rejective multiple test procedure. Scand J Stat 1979;6:65–70.
52. Kerby DS. The simple difference formula: An approach to teaching nonparametric correlation. Compr Psychol 2014;3:11.IT.3.1. https://doi.org/10.2466/11.IT.3.1.
