# Methodology {#sec:method}

## Problem setting and notation

Let $y_{b,t,j}\ge 0$ denote the metered electricity use (kWh) of building $b$ on day $t$ and hour $j\in\{0,\dots,23\}$. Building $b$ is metered from day $t_{0,b}$ onward. At the end of day $t_{0,b}+h-1$, after $h$ days of the building's own history have been observed, a day-ahead forecast is issued for the 24 hours of day $t=t_{0,b}+h$; we call $h$ the *onboarding stage*. For a miscoverage level $\alpha$ (main analysis: $\alpha=0.1$), the goal is an interval $C_{b,h,j}=[L_{b,h,j},U_{b,h,j}]$ such that, **for every individual building**, the share of hours with $y_{b,t,j}\in C_{b,h,j}$ is close to $1-\alpha$ from the first days after metering starts, while the intervals remain as narrow as possible. The empirical target is therefore the distribution of per-building coverage across buildings, not only its mean.

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

where the "+1" is a point mass at $+\infty$ that represents the not-yet-observed test score, as in weighted split conformal prediction [@tibshirani2019; @barber2023]. With $\rho=1$, the building's own scores receive the weight $n_{b,h}/(\kappa+n_{b,h}+1)$. This is the classical credibility (empirical-Bayes) form [@hong2023cred], recently used to shrink site- or group-specific conformal calibration towards a pooled one [@shahid2026; @rafe2026] and, with a fixed pseudo-count, to mix donor and local scores for new solar stations [@jeon2026]. It is also the posterior mean of the building's score distribution under a Dirichlet-process prior with base measure $F^{\mathrm{pop}}$ and concentration $\kappa$ [@ferguson1973; @zhang2024bayes]. Two limits recover familiar methods: $\kappa\to\infty$ gives pooled split conformal prediction, and $\kappa=0$ gives split conformal prediction on the building's own scores, which is undefined until enough own scores exist. The pseudo-count has a direct operational reading: it is the number of hourly own scores that the population is worth.

Recency weighting ($\rho<1$) is motivated by onboarding itself. Errors in the first days are produced by a forecaster that has seen almost no history of the building, and newly enrolled buildings can change their operation after enrolment. Old own scores then describe a building that no longer exists, and they are down-weighted in the same spirit as non-exchangeable conformal prediction [@barber2023]. A side effect is that the effective sample size $n^{\rho}_{b,h}$ is bounded by $1/(1-\rho)$, so the population distribution keeps a minimum weight $\kappa/(\kappa+1/(1-\rho)+1)$ throughout. The decay factor $\rho=0.95$ per day (half-life ≈ 13.5 days) was fixed before any result was seen (Section [-@sec:design]); Section [-@sec:frontier] reports $\rho\in\{0.8,0.9,0.95,1\}$.

**Selection of the pseudo-count.** $\kappa$ is selected on the calibration buildings only, by leave-one-building-out: each calibration building in turn plays the role of a new building, with the population distribution built from the remaining calibration buildings. The selection objective is the target property itself, namely the mean absolute deviation of the per-building coverage from $1-\alpha$ over the onboarding window (ties broken by the interval score of Eq. ([-@eq:is])), from the grid $\kappa\in\{0,24,48,96,168,336,672,1344,\infty\}$ hours. The study's original protocol selected $\kappa$ by the interval score instead. That objective is reported as a variant, and its systematic preference for larger $\kappa$ (Section [-@sec:ablation]) is why the coverage objective is used. Target buildings are never used for any choice.

**Examined refinements.** Three further elements were tested and are reported as variants (Section [-@sec:ablation]). The first two are *onboarding-stage matching* (the population distribution built from calibration scores at a similar onboarding stage, in bins $\{1\},\{2\},\{3\},\{4..6\},\{7..13\},\{14..27\},\{28..56\}$) and a *similarity-localised population distribution* (the $K$ calibration buildings closest to the new building in a load-shape descriptor; Supplementary Section S2). The third is *stage-wise studentisation*. Each CQR score is divided by the building's running error-scale ratio

$$
r_{b,h}=\frac{\kappa_s\,\sigma_0+\sum_{h'<h}\sum_j a_{b,h',j}}{\sigma_0\,(\kappa_s+n_{b,h})},\qquad a_{b,h,j}=\frac{|y_{b,t,j}-\hat y_{b,t,j}|}{s_{b,h}},
$$ {#eq:ssc}

with $\sigma_0$ the mean normalised absolute residual of the calibration buildings and $\kappa_s=24$ fixed a priori. At each exact stage $h$ the radius is the $(1-\alpha)$ quantile of the mixture in which each calibration building contributes the empirical distribution of its studentised scores at stage $h$ with weight $1/(M+1)$ and the new building a point mass $1/(M+1)$ at $+\infty$. This is the hierarchical conformal prediction (HCP) weighting of Lee, Barber and Willett [@lee2023hier], applied per stage; the "pooling CDFs" rule of [@dunn2023] is closely related but has only an asymptotic guarantee. The interval is $[\hat y^{\mathrm{lo}}-\tilde q_h r_{b,h}s_{b,h},\,\hat y^{\mathrm{hi}}+\tilde q_h r_{b,h}s_{b,h}]$ (SSC-CQR), and HSC-SSC-CQR applies the shrinkage of Eq. ([-@eq:hsc]) to the studentised scores.

*Proposition 1 (stage-wise validity across new buildings).* If the onboarding trajectories of the $M$ calibration buildings and of the new building are exchangeable and $\sigma_0$, $\kappa_s$ and the forecaster are fixed, then for every stage $h$, $\Pr\{y_{b,t,J}\in C_{b,h,J}\}\ge 1-\alpha$, where $J$ is an hour drawn uniformly from the new building's valid hours at stage $h$ and the probability is over buildings and $J$.

*Proof.* The studentised score is the same measurable function of each building's own trajectory up to stage $h$, so the $M+1$ vectors of stage-$h$ studentised scores are exchangeable across buildings. An independent uniform random permutation of the hours within each building makes them exchangeable within buildings as well, leaves the mixture unchanged and makes $J$ the first permuted hour. The data are then hierarchically exchangeable, and Theorem 1 of [@lee2023hier] gives coverage at least $1-\alpha$. ∎

The proposition guarantees coverage on average over new buildings at every onboarding day, from the first day on, which no shrinkage estimator with $0<\kappa<\infty$ does. It does not guarantee coverage for an individual building, which is impossible without distributional assumptions [@lin2022cptd]. The results show that this distinction matters in practice (Section [-@sec:ablation]).

**Validity of the shrinkage layer.** For a fixed $\kappa\in(0,\infty)$, Eq. ([-@eq:hsc]) does not inherit the finite-sample guarantee of split conformal prediction: neither the building's own past scores nor the calibration scores are exchangeable with its future scores, because forecast quality changes with $h$ and loads are autocorrelated. The layer is a principled, tunable interpolation between two conformal limits, and its reliability is established empirically below, including under distribution shift.

**Computation.** Score distributions are stored as cumulative counts on a fixed grid of 4000 asinh-spaced points between $-10$ and $500$ (in units of $s$; relative spacing ≈ 0.5 %). Mixture quantiles then reduce to a vectorised search; grid quantiles are rounded upwards for all methods alike, and whether an own-score quantile exists is decided from the number of own scores. The calibration store holds one cumulative-count vector per calibration building.
