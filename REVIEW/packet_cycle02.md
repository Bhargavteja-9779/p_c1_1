# Review packet — cycle 2
Repository root: /home/user/p_c1_1 (read-only for reviewers).

## 1. Manuscript (as built; all numbers filled from results files)

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

### T_alpha0.05_UCI.md

**UCI, nominal 95%**

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

### T_alpha0.2_BDG2.md

**BDG2, nominal 80%**

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

### T_alpha0.2_UCI.md

**UCI, nominal 80%**

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

### T_efficiency.md

**Computational cost (4 CPU cores)**

| part              |   train_total_s |   lgb_train_s |   mlp_train_s |   n_train_rows |   lgb_pred_ms_per_target_day |   hsc_tune_s |   hsc_apply_ms_per_target_day |   scp_s |   calibration_total_s |   hsc_store_MB |   hsc_cov_tune_s |   ssc_apply_ms_per_target_day |
|:------------------|----------------:|--------------:|--------------:|---------------:|-----------------------------:|-------------:|------------------------------:|--------:|----------------------:|---------------:|-----------------:|------------------------------:|
| main_BDG2_s0_a0.1 |        220.986  |      100.803  |      118.42   |        1318757 |                       0.2328 |      23.1937 |                        0.3246 |  0.4349 |              202.113  |        19.7944 |           1.3801 |                        0.0197 |
| main_BDG2_s1_a0.1 |        206.121  |      119.893  |       84.3989 |        1322913 |                       1.2394 |      25.7847 |                        0.3052 |  0.2967 |              184.842  |        19.7944 |           1.3993 |                        0.0193 |
| main_BDG2_s2_a0.1 |        383.78   |      264.78   |      117.19   |        1320185 |                       0.1101 |      24.1234 |                        0.3036 |  0.2324 |              197.936  |        19.7944 |           1.6272 |                        0.0248 |
| main_BDG2_s3_a0.1 |        858.693  |      755.455  |      101.391  |        1318589 |                       0.9428 |      27.2327 |                        0.1794 |  0.3612 |              175.056  |        19.7944 |           1.349  |                        0.0159 |
| main_BDG2_s4_a0.1 |        195.939  |      110.469  |       83.5954 |        1317922 |                       1.573  |      26.4748 |                        0.3544 |  0.3706 |              184.629  |        19.7944 |           1.6374 |                        0.019  |
| main_UCI_s0_a0.1  |       2411.89   |     2352.48   |       58.3863 |         992746 |                       0.0986 |       6.9857 |                        0.0658 |  0.1122 |               55.3212 |         7.4229 |           0.5219 |                        0.0155 |
| main_UCI_s1_a0.1  |         81.9074 |       30.965  |       49.4367 |         998092 |                       0.0851 |       6.0261 |                        0.0692 |  0.1044 |               44.5693 |         7.4229 |           0.5946 |                        0.0201 |
| main_UCI_s2_a0.1  |        119.531  |       50.2771 |       67.94   |         994452 |                       0.0443 |       5.7307 |                        0.2041 |  0.1077 |               54.544  |         7.4229 |           0.527  |                        0.0223 |
| main_UCI_s3_a0.1  |         93.1492 |       26.2627 |       65.4251 |         994891 |                       0.0754 |       6.2338 |                        0.069  |  0.0865 |               51.7172 |         7.4229 |           0.5289 |                        0.0206 |
| main_UCI_s4_a0.1  |        125.304  |       53.7684 |       70.1733 |         995880 |                       0.0963 |       6.0314 |                        0.0699 |  0.1358 |               51.0595 |         7.4229 |           0.4138 |                        0.0248 |

### T_gen_BDG2toBDG2_nw.md

**Generalisation: BDG2->BDG2 (no weather)**

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

### T_gen_BDG2toUCI_nw.md

**Generalisation: BDG2->UCI (no weather)**

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

### T_gen_UCItoBDG2_nw.md

**Generalisation: UCI->BDG2 (no weather)**

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

### T_gen_leave-site-out.md

**Generalisation: leave-site-out**

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

### T_main_BDG2.md

**Main results, BDG2, 90 % nominal, mean ± s.d. over seeds**

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

### T_main_UCI.md

**Main results, UCI, 90 % nominal, mean ± s.d. over seeds**

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

### T_robustness.md

**Robustness (BDG2, mean over seeds)**

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

## Cycle 1 (Reviewer 1, general; REVIEW/review_01.md) — resolved in manuscript v2
| Issue | Resolution |
|---|---|
| No week-1 gain | Pre-registered recency weighting + coverage objective (Addendum A); week-1 under-covered share now reported (BDG2 23.8 % → 13.7 %, UCI 16.0 % → 5.9 %); weekly figure with noise reference |
| Fixed κ beat tuned κ (objective mismatch) | Coverage objective for HSC, QShrink and ACI alike; frontier over all parameter grids |
| Pre-registration overstated | Reworded as internal protocol + committed addendum; deviations in Supplementary S4 |
| Missing baselines (scale-normalised, recency) | SSC-CQR, HSC-SSC-CQR (with Proposition 1, HCP-based), recency variant |
| No applied significance | Capacity-headroom cost (ρ = 10/20/40) and under-protected share; result: average cost unchanged, risk redistributed (reported as such) |
| Noise floor / clustering | Day-block SE per building; under-share noise reference; site-level tests (Table S5) |
| ACI grid cap; TQA-B target batch | Fixed (finite surrogate; λ from calibration buildings; unit test) |
| Selective stress reporting | Table 2 reports all key strategies per condition; exceptions stated (α = 0.2 ACI, HSC-SSC in two conditions) |
| Length/structure vs journal | v2 restructured to AAE pattern (literature/aae_fulltext_benchmark.md) |
