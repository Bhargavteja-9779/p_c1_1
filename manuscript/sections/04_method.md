# Method {#sec:method}

## Problem setting and notation

Let $y_{b,t,j}\ge 0$ denote the metered electricity use (kWh) of building $b$ on day $t$ and hour $j\in\{0,\dots,23\}$. Building $b$ is metered from day $t_{0,b}$ onward. At the end of day $t_{0,b}+h-1$, after $h$ days of the building's own history have been observed, a day-ahead forecast is issued for the 24 hours of day $t=t_{0,b}+h$; we call $h$ the *onboarding stage*. For a miscoverage level $\alpha$ (main analysis: $\alpha=0.1$), the goal is an interval $C_{b,h,j}=[L_{b,h,j},U_{b,h,j}]$ such that, **for every individual building**, the share of hours with $y_{b,t,j}\in C_{b,h,j}$ is close to $1-\alpha$ from the first days after metering starts, while the intervals remain as narrow as possible. The empirical target is therefore the distribution of per-building coverage across buildings, not only its mean.

Three disjoint sets of buildings are available (Section [-@sec:setup]): *training* buildings for the global forecaster, *calibration* buildings whose (simulated) onboarding windows provide nonconformity scores, and *target* buildings, which are metered in a later period and on which all methods are evaluated.

## Scale-normalised global forecaster

Buildings differ in mean load by four orders of magnitude (Fig. [-@fig:data]). Every load-derived quantity is therefore expressed relative to the scale

$$
s_{b,h}=\frac{1}{24\,m_h}\sum_{k=1}^{m_h}\sum_{j=0}^{23} y_{b,\,t-k,\,j},\qquad m_h=\min(h,7),
$$ {#eq:scale}

which uses only the last $m_h$ observed days. A single model $f$ is trained on the training buildings to predict $y_{b,t,j}/s_{b,h}$ from calendar variables, the normalised loads of the previous 1, 2, 7 and 14 days (missing if $h$ is smaller), normalised daily statistics and hour-of-day/day-type profiles computed over at most the last 28 observed days, the day-to-day variability of the normalised profile, the history length $\min(h,28)$, and, for BDG2, outdoor air temperature (Table [-@tbl:features]). During training, the history length of every sample is drawn uniformly from $\{1,\dots,28\}$ and all features are masked accordingly, so the model learns to forecast from short histories. The point forecast is $\hat y_{b,t,j}=s_{b,h}\,f(\mathbf x_{b,t,j})$; quantile models $f^{\mathrm{lo}},f^{\mathrm{hi}}$ (levels $\alpha/2$ and $1-\alpha/2$) are trained in the same way with the pinball loss [@koenker1978].

<<TABLE:MS_features|tbl:features>>

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

## Hierarchical shrinkage conformal calibration (HSC)

Fig. [-@fig:method] summarises the calibration layer.

![Calibration layer for newly metered buildings. A global forecaster is trained on scale-normalised loads of training buildings; calibration buildings provide nonconformity scores per onboarding stage; for a new building, a population prior (optionally stage-matched and similarity-localised) is shrunk toward the building's own accumulating scores with pseudo-count κ; κ and K are chosen by leave-one-building-out on calibration buildings only.](figures/Fig1_method.png){#fig:method}


Split conformal prediction [@vovk2005; @lei2018] would set $q$ to the $\lceil(1-\alpha)(N+1)\rceil$-th smallest of $N$ pooled calibration scores. This gives coverage that is valid on average over exchangeable test points. It cannot adapt to an individual building whose errors are systematically larger or smaller than average, which is precisely the situation of a building that has just been metered. HSC combines three elements.

**(i) Onboarding-stage matching.** Forecast errors depend on how much history is available. Calibration scores are therefore grouped into stage bins $\mathcal B\in\{\{1\},\{2\},\{3\},\{4..6\},\{7..13\},\{14..27\},\{28..56\}\}$, and a forecast at stage $h$ is calibrated with scores from the bin $\mathcal B(h)$ containing $h$.

**(ii) Similarity-localised population prior.** From its most recent $\min(h,28)$ observed days, each building is summarised by a descriptor $\mathbf z_{b,h}$: its mean daily load profile divided by its mean load (24 values), the mean absolute day-to-day change of that normalised profile, and the logarithm of the mean load. These quantities are computed in the same way for calibration buildings at the same stage. With $\mathcal N_K(b,h)$ the $K$ calibration buildings closest to $\mathbf z_{b,h}$ (Euclidean distance after standardisation), the prior score distribution is

$$
F^{\mathrm{prior}}_{b,h}(e)=\frac{1}{K}\sum_{c\in\mathcal N_K(b,h)}\hat F_{c,\mathcal B(h)}(e),
$$ {#eq:prior}

where $\hat F_{c,\mathcal B}$ is the empirical distribution function of the scores of calibration building $c$ in stage bin $\mathcal B$. Buildings without any valid score in $\mathcal B$ are left out of the average, and buildings whose descriptor is undefined (no valid data in the descriptor window) are never selected as neighbours. With $K$ equal to the number of calibration buildings, the prior is the unweighted (building-weighted) population average.

**(iii) Shrinkage toward the building's own scores.** By the time the stage-$h$ forecast is issued, the building's own scores from stages $1,\dots,h-1$ have been observed: $n_{b,h}=24(h-1)$ values $e_{b,1},\dots,e_{b,n_{b,h}}$ (fewer if data are missing). HSC uses the mixture distribution

$$
\tilde F_{b,h}(e)=\frac{\kappa\,F^{\mathrm{prior}}_{b,h}(e)+\sum_{i=1}^{n_{b,h}}\mathbb 1\{e_{b,i}\le e\}}{\kappa+n_{b,h}+1},\qquad
q_{b,h}=\inf\{e:\tilde F_{b,h}(e)\ge 1-\alpha\},
$$ {#eq:hsc}

where the "+1" in the denominator is a point mass at $+\infty$ that represents the not-yet-observed test score, as in (weighted) split conformal prediction [@tibshirani2019]. The building's own scores thus receive the weight $n_{b,h}/(\kappa+n_{b,h}+1)$, the classical credibility (empirical-Bayes) form [@hong2023cred] that has recently also been used to shrink site- or group-specific conformal calibration towards a pooled one [@shahid2026; @rafe2026] and, with a fixed pseudo-count, to mix donor and local scores for new solar stations [@jeon2026]. Equation ([-@eq:hsc]) is the posterior mean of the building's score distribution under a Dirichlet-process prior with base measure $F^{\mathrm{prior}}_{b,h}$ and concentration $\kappa$ [@ferguson1973], with the test point appended; the same prior-regularised form has been analysed for online conformal prediction with an uninformative base measure [@zhang2024bayes]. The pseudo-count $\kappa$ (in hours of scores) has a direct interpretation: after $\kappa/24$ days, the building's own errors carry as much weight as the population prior. Two limits recover familiar methods. $\kappa\to\infty$ gives the (localised, stage-matched) population split-conformal quantile, with the usual finite-sample correction applied in that case. $\kappa=0$ gives split conformal prediction on the building's own past scores, which is undefined (infinite) until enough own scores exist. HSC interpolates between the two as data accumulate.

**Selection of $\kappa$ and $K$.** Both are selected on the calibration buildings only, by leave-one-building-out. Each calibration building in turn plays the role of a new building, with the prior built from the remaining calibration buildings. The pair minimising the interval score of Eq. ([-@eq:is]) — computed per hour, divided by the scale $s_{b,h}$ and averaged over all calibration building-hours of all stages — is chosen from $\kappa\in\{0,24,48,96,168,336,672,1344,\infty\}$ and $K\in\{10,25,50,100,\text{all}\}$. Target buildings are never used for any choice.

**Computation.** Score distributions are stored as cumulative counts on a fixed grid of 4000 asinh-spaced points between $-10$ and $500$ (in units of $s$; relative spacing ≈ 0.5 %). Mixture quantiles in Eq. ([-@eq:hsc]) then reduce to a vectorised search; the grid quantile is rounded upwards (conservatively) for all methods alike, and a quantile above the grid range is capped at $500\,s_{b,h}$ (a conservative stand-in for an unbounded radius). Whether an own-score quantile exists ($\lceil(1-\alpha)(n+1)\rceil\le n$) is decided from the number of own scores. The calibration store holds one cumulative-count vector per calibration building and stage bin, plus the descriptors.

**Validity.** For a fixed $\kappa\in(0,\infty)$, Eq. ([-@eq:hsc]) does not inherit the finite-sample marginal guarantee of split conformal prediction: neither the target's own past scores nor the calibration scores are exchangeable with its future scores, because the forecast quality changes with $h$ and load is autocorrelated. HSC should therefore be read as a principled, tunable interpolation between two conformal limits. Its reliability is assessed empirically below, including under distribution shift, rather than claimed theoretically.
