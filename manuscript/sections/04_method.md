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

## Score-shrinkage conformal calibration (SSC)

Fig. [-@fig:method] summarises the calibration layer.

![Calibration layer for newly metered buildings. A global forecaster is trained on scale-normalised loads of training buildings; calibration buildings provide a pooled nonconformity-score distribution; for a new building, this pooled distribution is mixed with the building's own accumulating scores with a single pseudo-count κ, chosen by leave-one-building-out on calibration buildings with a per-building reliability objective. Two optional refinements (stage-matched and similarity-localised priors) were tested and are not part of the recommended layer.](figures/Fig1_method.png){#fig:method}

Split conformal prediction [@vovk2005; @lei2018] sets $q$ to the $\lceil(1-\alpha)(N+1)\rceil$-th smallest of $N$ pooled calibration scores. Its coverage is valid on average over exchangeable test points, but it cannot adapt to an individual building whose errors are systematically larger or smaller than average — precisely the situation of a building that has just been metered. Calibrating on the building's own past scores alone adapts, but is undefined or erratic while few scores exist. The layer studied here combines the two with one parameter.

**Mixture of pooled and own scores.** By the time the stage-$h$ forecast is issued, the building's own scores from stages $1,\dots,h-1$ have been observed: $n_{b,h}\le 24(h-1)$ values $e_{b,1},\dots,e_{b,n_{b,h}}$ (fewer if readings are missing). With $F^{\mathrm{pop}}$ the building-weighted average of the empirical score distributions of the calibration buildings, SSC uses

$$
\tilde F_{b,h}(e)=\frac{\kappa\,F^{\mathrm{pop}}(e)+\sum_{i=1}^{n_{b,h}}\mathbb 1\{e_{b,i}\le e\}}{\kappa+n_{b,h}+1},\qquad
q_{b,h}=\inf\{e:\tilde F_{b,h}(e)\ge 1-\alpha\},
$$ {#eq:hsc}

where the "+1" in the denominator is a point mass at $+\infty$ for the not-yet-observed test score, as in (weighted) split conformal prediction [@tibshirani2019]. The building's own scores thus receive the weight $n_{b,h}/(\kappa+n_{b,h}+1)$, the classical credibility form of experience rating [@buhlmann1967] and of empirical-Bayes shrinkage [@efron1973]. The same form has recently been used to shrink site- or group-specific conformal calibration towards a pooled one [@shahid2026; @rafe2026] and, with a fixed pseudo-count and distance-weighted donors, to mix donor and local scores for newly commissioned solar-irradiance stations ([@jeon2026], a software record accompanying a manuscript under review); a prior-regularised quantile of the same type has been analysed for online conformal prediction [@zhang2024bayes]. The mechanism is therefore not new; what we study is whether, how and from when it makes day-ahead load intervals reliable for each newly metered building, compared with the alternatives of Section [-@sec:related]. Without the point mass, the mixture is the posterior mean of the building's score distribution under a Dirichlet-process prior with base measure $F^{\mathrm{pop}}$ and concentration $\kappa$ [@ferguson1973]; we use this reading only as motivation. The pseudo-count $\kappa$ (in hours of scores) has a direct interpretation: after $\kappa/24$ days the building's own errors carry as much weight as the population. As $\kappa\to\infty$ the radius becomes the pooled split-conformal quantile (with the usual finite-sample correction applied in that case); with $\kappa=0$ it becomes the split-conformal quantile of the building's own past scores, which is undefined until enough own scores exist. Under the onboarding protocol neither end carries a finite-sample guarantee (see *Validity*), so these are limits of form, not of coverage.

**Selection of $\kappa$.** $\kappa$ is selected on the calibration buildings only, by leave-one-building-out (LOBO): each calibration building in turn plays the role of a new building, with $F^{\mathrm{pop}}$ built from the remaining calibration buildings and the building's own scores accumulating over its onboarding window. Because the goal is per-building reliability without giving up sharpness, the selection rule is the *sharpest reliable setting*: among the values of $\kappa$ for which at most 5 % of the pseudo-targets are clearly under-covered (coverage below $1-\alpha-0.05$, the under-coverage criterion of Section [-@sec:setup]), the one with the smallest scale-normalised interval score (Eq. [-@eq:is]) is chosen; if no value qualifies, the one with the smallest under-covered share. The grid is $\kappa\in\{0,24,48,96,168,336,672,1344,\infty\}$. This rule replaces the pre-registered interval-score objective, which in the first submission traded per-building reliability for sharpness (Section [-@sec:prereg]); a pure coverage-deviation objective was also considered and rejected on a first one-seed check because it rewards forcing each building's coverage to the nominal value at any cost in width (it selected the largest ACI step size, with 55 % wider intervals). The interval-score-tuned layer and a fixed one-week value $\kappa=168$ h (introduced as an ablation before the final runs of the first submission) are reported alongside. Target buildings are never used for any choice.

**Refinements tested as ablations.** The pre-registered design added two building-specific refinements to $F^{\mathrm{pop}}$. (i) *Onboarding-stage matching*: calibration scores are grouped into stage bins $\mathcal B\in\{\{1\},\{2\},\{3\},\{4..6\},\{7..13\},\{14..27\},\{28..56\}\}$ and a stage-$h$ forecast uses only the bin containing $h$ (the building's own scores are pooled over its past stages). (ii) *Similarity-localised prior*: $F^{\mathrm{pop}}$ is replaced by the average over the $K$ calibration buildings closest to a load-shape descriptor (normalised mean daily profile, mean absolute day-to-day change, log mean load; computed from the last $\min(h,28)$ days; Euclidean distance after standardisation; buildings without valid scores in the bin or with undefined descriptors are excluded), with $K\in\{10,25,50,100,\text{all}\}$ selected jointly with $\kappa$ by LOBO on the interval score. This design is closely related to localised conformal prediction [@guan2023]. Section [-@sec:results] shows that neither refinement improves reliability; the recommended layer is the one-parameter mixture above.

**Computation.** Score distributions are stored as cumulative counts on a fixed grid of 4000 asinh-spaced points between $-10$ and $500$ (in units of $s$; relative spacing ≈ 0.5 %). Mixture quantiles in Eq. ([-@eq:hsc]) then reduce to a vectorised search; the grid quantile is rounded upwards (conservatively) for all methods alike, and a quantile above the grid range is capped at $500\,s_{b,h}$. Whether an own-score quantile exists ($\lceil(1-\alpha)(n+1)\rceil\le n$) is decided from the number of own scores. A negative CQR radius larger than half the quantile spread would invert the interval; for every method such hours receive the degenerate interval at the midpoint (their number is reported). A deployment stores one pooled cumulative-count vector and, per building, its own counts; a daily update adds 24 scores and recomputes one quantile.

**Validity.** For a fixed $\kappa\in(0,\infty)$, Eq. ([-@eq:hsc]) does not inherit the finite-sample marginal guarantee of split conformal prediction: neither the target's own past scores nor the calibration scores are exchangeable with its future scores, because forecast quality changes with $h$ and load is autocorrelated; building-level guarantees for new groups require other constructions [@dunn2023; @lee2023hier]. The layer should therefore be read as a principled, tunable interpolation, and its reliability is assessed empirically below, including under distribution shift.
