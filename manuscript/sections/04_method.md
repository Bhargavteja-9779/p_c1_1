# Methodology {#sec:method}

## Problem setting and notation

Let $y_{b,t,j}\ge 0$ denote the metered electricity use (kWh) of building $b$ on day $t$ and hour $j\in\{0,\dots,23\}$. Building $b$ is metered from day $t_{0,b}$ onward. At the end of day $t_{0,b}+h-1$, after $h$ days of the building's own history have been observed, a day-ahead forecast is issued for the 24 hours of day $t=t_{0,b}+h$; we call $h$ the *onboarding stage*. We assume that all 24 hours of day $t-1$ are observed when the forecast is issued; because day-ahead nominations usually close around noon of $t-1$ and meter data may arrive late, a variant in which the building's own scores reach the calibration layer one day later is also evaluated (Section [-@sec:design]). For a miscoverage level $\alpha$ (main analysis: $\alpha=0.1$), the goal is an interval $C_{b,h,j}=[L_{b,h,j},U_{b,h,j}]$ such that, **for every individual building**, the share of hours with $y_{b,t,j}\in C_{b,h,j}$ is close to $1-\alpha$ from the first days after metering starts, while the intervals remain as narrow as possible. The empirical target is therefore the distribution of per-building coverage across buildings, not only its mean.

Three disjoint sets of buildings are available (Section [-@sec:setup]): *training* buildings for the global forecaster, *calibration* buildings whose (simulated) onboarding windows provide nonconformity scores, and *target* buildings, which are metered in a later period and on which all methods are evaluated.

## Scale-normalised global forecaster

Buildings differ in mean load by four orders of magnitude (Fig. [-@fig:data]). Every load-derived quantity is therefore expressed relative to the scale

$$
s_{b,h}=\frac{1}{24\,m_h}\sum_{k=1}^{m_h}\sum_{j=0}^{23} y_{b,\,t-k,\,j},\qquad m_h=\min(h,7),
$$ {#eq:scale}

which uses only the last $m_h$ observed days. A single model $f$ is trained on the training buildings to predict $y_{b,t,j}/s_{b,h}$ from calendar variables, the normalised loads of the previous 1, 2, 7 and 14 days (missing if $h$ is smaller), normalised daily statistics and hour-of-day/day-type profiles computed over at most the last 28 observed days, the day-to-day variability of the normalised profile, the history length $\min(h,28)$, and, for BDG2, outdoor air temperature (Supplementary Table S1). During training, the history length of every sample is drawn uniformly from $\{1,\dots,28\}$ and all features are masked accordingly, so the model learns to forecast from short histories. The point forecast is $\hat y_{b,t,j}=s_{b,h}\,f(\mathbf x_{b,t,j})$; quantile models $f^{\mathrm{lo}},f^{\mathrm{hi}}$ (levels $\alpha/2$ and $1-\alpha/2$) are trained in the same way with the pinball loss [@koenker1978].

## Nonconformity scores

We use two normalised scores: the absolute residual and the conformalised-quantile-regression (CQR) score [@romano2019]:

$$
e^{\mathrm{abs}}_{b,h,j}=\frac{|y_{b,t,j}-\hat y_{b,t,j}|}{s_{b,h}},\qquad
e^{\mathrm{cqr}}_{b,h,j}=\frac{\max\{\hat y^{\mathrm{lo}}_{b,t,j}-y_{b,t,j},\; y_{b,t,j}-\hat y^{\mathrm{hi}}_{b,t,j}\}}{s_{b,h}} .
$$ {#eq:scores}

Given a radius $q_{b,h}$ (in units of $s_{b,h}$), the interval is

$$
C_{b,h,j}=\big[\hat y^{\mathrm{lo}}_{b,t,j}-q_{b,h}\,s_{b,h},\;\hat y^{\mathrm{hi}}_{b,t,j}+q_{b,h}\,s_{b,h}\big],
$$ {#eq:interval}

with $\hat y^{\mathrm{lo}}=\hat y^{\mathrm{hi}}=\hat y$ for the absolute score. Division by $s_{b,h}$ is what makes scores from buildings of different size comparable and therefore poolable.

## Recency-weighted shrinkage conformal calibration {#sec:layer}

Fig. [-@fig:method] summarises the calibration layer. Split conformal prediction [@vovk2005; @lei2018] sets $q$ to the $\lceil(1-\alpha)(N+1)\rceil$-th smallest of $N$ pooled calibration scores. This is valid on average over exchangeable test points but cannot adapt to an individual building whose errors are systematically larger or smaller than average, which is precisely the situation of a newly metered building. Calibration on the building's own scores alone removes this bias but replaces it with variance: with a few dozen hourly scores, an empirical 90 % quantile is a noisy estimate. The layer trades the two off explicitly.

![Calibration layer for newly metered buildings. A global forecaster is trained on scale-normalised loads of training buildings. Calibration buildings, onboarded in the training period, provide CQR nonconformity scores that form the population score distribution. For a new building, the population distribution is mixed with the building's own past scores, which are down-weighted with their age (factor ρ per day), through a pseudo-count κ selected by leave-one-building-out on the per-building coverage of calibration buildings.](figures/Fig1_method.png){#fig:method}

**Population score distribution.** Let $\hat F_c$ be the empirical distribution function of the scores of calibration building $c$ over its onboarding window. The population distribution is the building-weighted average $F^{\mathrm{pop}}(e)=\frac1M\sum_{c=1}^{M}\hat F_c(e)$ over the $M$ calibration buildings, so that every building, not every hour, counts equally.

**Recency-weighted shrinkage.** When the stage-$h$ forecast is issued, the building's own scores from stages $1,\dots,h-1$ are known. A score observed on stage $h'$ receives the weight $w_{h,h'}=\rho^{\,h-1-h'}$, so the most recent day has weight one and older days are down-weighted by a factor $\rho$ per day. With $n^{\rho}_{b,h}=\sum_{i}w_{h,h'(i)}$ the effective number of own scores, the layer uses the mixture distribution

$$
\tilde F_{b,h}(e)=\frac{\kappa\,F^{\mathrm{pop}}(e)+\sum_{i}w_{h,h'(i)}\,\mathbb 1\{e_{b,i}\le e\}}{\kappa+n^{\rho}_{b,h}+1},\qquad
q_{b,h}=\inf\{e:\tilde F_{b,h}(e)\ge 1-\alpha\},
$$ {#eq:hsc}

where the "+1" is a point mass at $+\infty$ that represents the not-yet-observed test score, as in weighted split conformal prediction [@tibshirani2019; @barber2023]. With $\rho=1$, the building's own scores receive the weight $n_{b,h}/(\kappa+n_{b,h}+1)$. This is the classical credibility form of experience rating [@buhlmann1967] and of empirical-Bayes shrinkage [@efron1973]; it has been linked to conformal prediction [@hong2023cred] and recently used to shrink site- or group-specific conformal calibration towards a pooled one, with the pseudo-count chosen by leave-one-site-out on per-site violations [@shahid2026] or fixed [@rafe2026]; a donor–local score mixture for new solar stations is implemented in a software record (cf. [@jeon2026]). For $\rho=1$ and without the point mass, the mixture is also the posterior mean of the building's score distribution under a Dirichlet-process prior with base measure $F^{\mathrm{pop}}$ and concentration $\kappa$ [@ferguson1973]; with $\rho<1$ this reading no longer holds. The layer is therefore an adaptation of known components, and what this study contributes is its evaluation for onboarding (Section [-@sec:intro]). As $\kappa\to\infty$ the radius becomes the split-conformal quantile of the building-weighted, stage-agnostic population distribution, which differs from the score-weighted, stage-matched CQR baseline (both are reported); $\kappa=0$ gives split conformal prediction on the building's own scores, which is undefined until enough own scores exist. The pseudo-count has a direct operational reading: it is the number of hourly own scores that the population is worth.

Recency weighting ($\rho<1$) is motivated by onboarding itself. Errors in the first days are produced by a forecaster that has seen almost no history of the building, and newly enrolled buildings can change their operation after enrolment. Old own scores then describe a building that no longer exists, and they are down-weighted in the same spirit as non-exchangeable conformal prediction [@barber2023]. Because each day adds up to 24 hourly scores, the effective sample size is bounded by $n^{\rho}_{b,h}\le 24/(1-\rho)=480$ hourly scores for $\rho=0.95$, so the population distribution keeps a minimum weight $\kappa/(\kappa+480+1)$ (for example 9 % at $\kappa=48$ h). The decay factor $\rho=0.95$ per day (half-life ≈ 13.5 days) was fixed in the protocol addendum, which was written after a pilot evaluation and before the final runs (Section [-@sec:design]); it was not tuned, and Section [-@sec:frontier] shows that other values ($\rho\in\{0.8,0.9,1\}$) lie at different points of the same frontier.

**Selection of the pseudo-count.** $\kappa$ is selected on the calibration buildings only, by leave-one-building-out (LOBO): each calibration building in turn plays the role of a new building, with the population distribution built from the remaining calibration buildings. Following the leave-one-unit-out principle of [@shahid2026], the objective is the target property: the mean absolute deviation of the per-building coverage from $1-\alpha$ over the onboarding window (LOBO-MACD). Because this objective alone rewards forcing coverage at any cost in width, it is minimised subject to a sharpness constraint: the LOBO interval score (Eq. ([-@eq:is])) may exceed that of the family's pooled limit ($\kappa=\infty$) by at most 2 %; if no value qualifies, the sharpest value is taken. The grid is $\kappa\in\{0,6,12,24,48,96,168,336,672,1344,\infty\}$ hours, and selections at the grid edges are reported. Exactly the same constrained objective tunes every parametrised competitor (quantile shrinkage $\lambda$, ACI step size $\gamma$; Section [-@sec:design]). The original protocol selected $\kappa$ by the interval score; that variant is reported as well. Target buildings are never used for any choice.

**Examined refinements.** Three further elements were tested and are reported as variants (Section [-@sec:ablation]). The first two are *onboarding-stage matching* (the population distribution built from calibration scores at a similar onboarding stage, in bins $\{1\},\{2\},\{3\},\{4..6\},\{7..13\},\{14..27\},\{28..56\}$) and a *similarity-localised population distribution* (the $K$ calibration buildings closest to the new building in a load-shape descriptor; Supplementary Section S2). The third is *stage-wise studentisation*. Each CQR score is divided by the building's running error-scale ratio

$$
r_{b,h}=\frac{\kappa_s\,\sigma_0+\sum_{h'<h}\sum_j a_{b,h',j}}{\sigma_0\,(\kappa_s+n_{b,h})},\qquad a_{b,h,j}=\frac{|y_{b,t,j}-\hat y_{b,t,j}|}{s_{b,h}},
$$ {#eq:ssc}

with $\sigma_0$ the mean normalised absolute residual of the forecaster on the validation buildings (disjoint from calibration and target buildings, so that the studentised score is the same function of each building's data) and $\kappa_s=24$ fixed a priori. At each exact stage $h$ the radius is the $(1-\alpha)$ quantile of the mixture in which each calibration building contributes the empirical distribution of its studentised scores at stage $h$ with weight $1/(M+1)$ and the new building a point mass $1/(M+1)$ at $+\infty$. This is the hierarchical conformal prediction (HCP) weighting of Lee, Barber and Willett ([@lee2023hier], arXiv v4), applied per stage; the "pooling CDFs" rule of [@dunn2023] is closely related but has only an asymptotic guarantee. The interval is $[\hat y^{\mathrm{lo}}-\tilde q_h r_{b,h}s_{b,h},\,\hat y^{\mathrm{hi}}+\tilde q_h r_{b,h}s_{b,h}]$ (SSC-CQR), and HSC-SSC-CQR applies the shrinkage of Eq. ([-@eq:hsc]) to the studentised scores.

*Corollary 1 (of Theorem 1 in [@lee2023hier]; stage-wise validity across new buildings).* If the onboarding trajectories of the $M$ calibration buildings and of the new building are exchangeable and $\sigma_0$, $\kappa_s$ and the forecaster are fixed, then for every stage $h$, $\Pr\{y_{b,t,J}\in C_{b,h,J}\}\ge 1-\alpha$, where $J$ is an hour drawn uniformly from the new building's valid hours at stage $h$ and the probability is over buildings and $J$.

*Proof.* The studentised score is the same measurable function of each building's own trajectory up to stage $h$, so the $M+1$ vectors of stage-$h$ studentised scores are exchangeable across buildings. An independent uniform random permutation of the hours within each building makes them exchangeable within buildings as well, leaves the mixture unchanged and makes $J$ the first permuted hour. The data are then hierarchically exchangeable, and Theorem 1 of [@lee2023hier] gives coverage at least $1-\alpha$. ∎

The corollary concerns coverage on average over new buildings at each onboarding day. Its premise of exchangeability between calibration and target trajectories does not hold in the evaluated protocol, where target buildings are onboarded in a later period than calibration buildings, so it motivates SSC-CQR but gives no guarantee here; its stage-wise coverage is reported empirically (Supplementary Table S22). It does not concern individual buildings: distribution-free longitudinal validity for a single series under arbitrary dependence is impossible [@lin2022cptd], whereas area-conditional validity is attainable when each unit has exchangeable data of its own, as in the small-area method of [@bersson2024], which shrinks only the interval width; in onboarding, a building has too few own scores in its first week for such a construction.

**Validity of the shrinkage layer.** For a fixed $\kappa\in(0,\infty)$, Eq. ([-@eq:hsc]) does not inherit the finite-sample guarantee of split conformal prediction: neither the building's own past scores nor the calibration scores are exchangeable with its future scores, because forecast quality changes with $h$ and loads are autocorrelated. The layer is a tunable interpolation between pooled and own-score calibration, and its reliability is assessed empirically below, including under distribution shift.

**Computation.** Score distributions are stored as cumulative counts on a fixed grid of 4000 asinh-spaced points between $-10$ and $500$ (in units of $s$; relative spacing ≈ 0.5 %). Mixture quantiles then reduce to a vectorised search; grid quantiles are rounded upwards for all methods alike, and whether an own-score quantile exists is decided from the number of own scores. Tuning holds one cumulative-count vector per calibration building and stage; deployment needs only the population vector and, per building, one decayed count vector (4000 numbers), updated once a day:

> **Daily update for building $b$** (cost linear in the grid size). (i) Bin the 24 new scores of day $h-1$ on the grid and accumulate them into counts $c$; (ii) state $\leftarrow\rho\cdot$state $+\,c$; (iii) $\tilde F\leftarrow(\kappa F^{\mathrm{pop}}+\text{state})/(\kappa+\text{state}_{\max}+1)$; (iv) $q_{b,h}\leftarrow$ first grid point with $\tilde F\ge 1-\alpha$; (v) issue Eq. ([-@eq:interval]).
