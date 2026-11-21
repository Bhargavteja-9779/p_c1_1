# Method {#sec:method}

## Problem setting and notation

Let $y_{b,t,j}\ge 0$ denote the metered electricity use (kWh) of building $b$ on day $t$ and hour $j\in\{0,\dots,23\}$. Building $b$ is metered from day $t_{0,b}$ onward. After $h$ days of its own history have been observed, a day-ahead forecast is issued for the 24 hours of day $t=t_{0,b}+h$; we call $h$ the *onboarding stage*. For a miscoverage level $\alpha$ (main analysis $\alpha=0.1$), the goal is an interval $C_{b,h,j}=[L_{b,h,j},U_{b,h,j}]$ whose coverage is close to $1-\alpha$ **for every individual building**, while the intervals remain as narrow as possible. The empirical target is therefore the distribution of per-building coverage across buildings, not only its mean. Three disjoint sets of buildings are used (Section [-@sec:setup]): *training* buildings for the global forecaster, *calibration* buildings whose simulated onboarding windows provide nonconformity scores, and *target* buildings, metered in a later period, on which all methods are evaluated.

## Scale-normalised global forecaster

Buildings differ in mean load by four orders of magnitude (Supplementary Fig. S1). Every load-derived quantity is therefore expressed relative to the scale

$$
s_{b,h}=\frac{1}{24\,m_h}\sum_{k=1}^{m_h}\sum_{j=0}^{23} y_{b,\,t-k,\,j},\qquad m_h=\min(h,7),
$$ {#eq:scale}

which uses only the last $m_h$ observed days. A single LightGBM model [@ke2017] is trained on the training buildings to predict $y_{b,t,j}/s_{b,h}$ from calendar variables, normalised loads of the previous 1, 2, 7 and 14 days (missing if $h$ is smaller), normalised daily statistics and hour-of-day/day-type profiles over at most the last 28 observed days, the day-to-day variability of the normalised profile, the history length $\min(h,28)$ and, for BDG2, outdoor air temperature (Supplementary Table S2). During training the history length of each sample is drawn uniformly from $\{1,\dots,28\}$ and all features are masked accordingly, so the model learns to forecast from short histories. Quantile models $f^{\mathrm{lo}},f^{\mathrm{hi}}$ (levels $\alpha/2$, $1-\alpha/2$) are trained in the same way with the pinball loss [@koenker1978], giving $\hat y^{\mathrm{lo}}_{b,t,j}=s_{b,h}f^{\mathrm{lo}}(\mathbf x_{b,t,j})$ and $\hat y^{\mathrm{hi}}_{b,t,j}$.

## Nonconformity scores

The main score is the conformalised-quantile-regression (CQR) score [@romano2019], normalised by the scale:

$$
e_{b,h,j}=\frac{\max\{\hat y^{\mathrm{lo}}_{b,t,j}-y_{b,t,j},\; y_{b,t,j}-\hat y^{\mathrm{hi}}_{b,t,j}\}}{s_{b,h}},\qquad
C_{b,h,j}=\big[\hat y^{\mathrm{lo}}_{b,t,j}-q_{b,h}\,s_{b,h},\;\hat y^{\mathrm{hi}}_{b,t,j}+q_{b,h}\,s_{b,h}\big].
$$ {#eq:scores}

The normalisation makes scores of buildings of different size comparable, and therefore poolable. All calibration strategies compared in this paper use the same scores and differ only in how the radius $q_{b,h}$ is obtained. The absolute residual $|y-\hat y|/s$ of a point forecast is used as a secondary score. Only hours whose reading was actually observed (not interpolated or masked by the quality rules) contribute scores.

## Pseudo-count shrinkage of the score distribution (PCS)

Fig. [-@fig:method] summarises the calibration layer.

![Calibration layer for newly metered buildings (PCS-CQR). A global quantile forecaster is trained on scale-normalised loads of training buildings; calibration buildings provide CQR nonconformity scores; for a new building, the pooled score distribution of the calibration buildings is shrunk toward the building's own accumulating scores with pseudo-count κ, which is chosen by leave-one-building-out on calibration buildings only.](figures/Fig1_method.png){#fig:method}

Pooled split conformal prediction [@vovk2005; @lei2018] sets $q$ to the $\lceil(1-\alpha)(N+1)\rceil$-th smallest of the $N$ pooled calibration scores. This guarantees coverage on average over exchangeable test points but cannot adapt to a building whose errors are systematically larger or smaller than average — the situation of a building that has just been metered. When the stage-$h$ forecast is issued, the building's own scores from days $1,\dots,h-1$ are available: $n_{b,h}\le 24(h-1)$ values $e_{b,1},\dots,e_{b,n_{b,h}}$. PCS uses the mixture distribution

$$
\tilde F_{b,h}(e)=\frac{\kappa\,F^{\mathrm{pop}}(e)+\sum_{i=1}^{n_{b,h}}\mathbb 1\{e_{b,i}\le e\}}{\kappa+n_{b,h}+1},\qquad
q_{b,h}=\inf\{e:\tilde F_{b,h}(e)\ge 1-\alpha\},
$$ {#eq:pcs}

where $F^{\mathrm{pop}}=M^{-1}\sum_{c=1}^{M}\hat F_c$ is the average of the empirical score distributions of the $M$ calibration buildings, and the "+1" in the denominator is a point mass at $+\infty$ for the not-yet-observed test score, as in weighted split conformal prediction [@tibshirani2019]. The building's own scores receive the credibility weight $n_{b,h}/(\kappa+n_{b,h}+1)$ [@buhlmann1967], so after $\kappa/24$ days they carry as much weight as the population. The mixture numerator is the predictive distribution of a Dirichlet-process model with base measure $F^{\mathrm{pop}}$ and concentration $\kappa$ [@ferguson1973]; Eq. ([-@eq:pcs]) adds the conformal-style point at infinity and should be read as a Dirichlet-process-motivated heuristic, not as a posterior. The same form appears in prior-regularised online conformal prediction [@zhang2024bayes], in credibility-type shrinkage of site- or group-specific conformal calibration [@shahid2026; @rafe2026] and, with a fixed pseudo-count, as a donor–local mixture for newly commissioned solar stations [@jeon2026]; we do not claim the mechanism as new. As $\kappa\to\infty$, Eq. ([-@eq:pcs]) tends to the building-weighted population quantile, which is used with the usual finite-sample correction at $\kappa=\infty$ (the correction is not applied for large finite $\kappa$). $\kappa=0$ is split conformal prediction on the building's own past scores, used — like the Self-CQR baseline — with a pooled fallback until enough own scores exist.

**Selection of κ.** $\kappa$ is selected on calibration buildings only, by leave-one-building-out (LOBO): each calibration building in turn plays the role of a new building, with $F^{\mathrm{pop}}$ built from the remaining calibration buildings, and the 56-day onboarding window is replayed. For each $\kappa\in\{0,24,48,96,168,336,672,1344,\infty\}$ two objectives are computed over the pseudo-targets: the mean interval score (Eq. [-@eq:is], divided by $s$) and the mean absolute deviation of their window coverage from $1-\alpha$. The pre-registered rule minimised the interval score. Because this objective is almost flat in $\kappa$ (Section [-@sec:results]) and does not target per-building reliability, PCS uses a **reliability-aware rule**: among the values of $\kappa$ whose LOBO interval score is within 2 % of the minimum, choose the one with the smallest LOBO coverage deviation (ties broken by the interval score). The 2 % tolerance keeps the sharpness loss below the seed-to-seed variability of the interval score. The same rule is applied to the tuning parameters of the competing strategies (Section [-@sec:setup]).

**Optional refinements (tested, not recommended).** The pre-registered design, called **HSC** (absolute score) and **HSC-CQR** (CQR score) below, added two building-specific refinements to Eq. ([-@eq:pcs]) and selected $\kappa$ by the interval score. (i) *Onboarding-stage matching*: the prior uses only calibration scores from the same stage bin $\{1\},\{2\},\{3\},\{4..6\},\{7..13\},\{14..27\},\{28..56\}$ as $h$. (ii) *Similarity-localised prior*: $F^{\mathrm{pop}}$ is replaced by the average over the $K$ calibration buildings nearest to the new building in a descriptor of its last $\min(h,28)$ days (24 values of the normalised mean daily profile, its mean absolute day-to-day change and the log mean load; standardised Euclidean distance), with $K\in\{10,25,50,100,\text{all}\}$ selected jointly with $\kappa$. Section [-@sec:results] shows that neither refinement improves reliability, so the recommended layer is the one-parameter form of Eq. ([-@eq:pcs]).

**Computation and state.** Score distributions are stored as cumulative counts on a fixed grid of 4000 asinh-spaced points between $-10$ and $500$ (in units of $s$; relative spacing about 0.5 %), and the grid quantile is rounded upwards for all methods alike. A deployed PCS layer stores one shared vector $F^{\mathrm{pop}}$ and, per building, one running count vector of its own scores (16 kB as int32; alternatively the at most $24h$ raw scores). The daily update adds 24 scores and recomputes one quantile.

**Validity.** For finite $\kappa>0$, Eq. ([-@eq:pcs]) does not inherit the finite-sample guarantee of split conformal prediction: neither the building's own past scores nor the calibration scores are exchangeable with its future scores, because forecast quality changes with $h$, the own scores pool all earlier stages, and load is autocorrelated. Its per-building reliability is therefore assessed empirically, including under distribution shift.
