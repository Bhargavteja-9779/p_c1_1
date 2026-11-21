## DRAFT 2.4 Calibration strategies (new parts)

**Recency-weighted shrinkage.** Own scores observed $d$ days before the forecast receive weight $\rho^{d-1}$ ($\rho = 0.95$ per day, half-life ≈ 13.5 days, fixed a priori), and $n_{b,h}$ in Eq. (5) is replaced by the effective number $\sum_i \rho^{d_i-1}$. With $\rho = 1$, Eq. (5) is recovered. Recency weighting limits the influence of scores that no longer describe the building, e.g. after a change of occupancy or operation, in the spirit of non-exchangeable conformal prediction with decaying weights [43].

**Stage-wise studentised conformal calibration (SSC).** A building's error *scale* can be estimated from far fewer own scores than its 90 % tail quantile. SSC therefore normalises each score by a running estimate of the building's own error scale and calibrates the normalised scores across buildings at the *same* onboarding stage. With $a_{b,h,j}=|y_{b,t,j}-\hat y_{b,t,j}|/s_{b,h}$ the normalised absolute residual,

$$
r_{b,h}=\frac{1}{\sigma_0}\cdot\frac{\kappa_s\,\sigma_0+\sum_{h'<h}\sum_j a_{b,h',j}}{\kappa_s+n_{b,h}},\qquad
\tilde e_{b,h,j}=\frac{e^{\mathrm{cqr}}_{b,h,j}}{r_{b,h}},\qquad\qquad (7)
$$

where $\sigma_0$ is the mean normalised absolute residual of the calibration buildings and $\kappa_s=24$ (one day of hourly residuals, fixed a priori). $r_{b,h}$ uses only stages before $h$, so it is known when the forecast is issued. At each stage $h$, the radius $\tilde q_h$ is the $(1-\alpha)$ quantile of the building-weighted mixture

$$
\tilde F_h(e)=\frac{1}{M+1}\Big[\sum_{c=1}^{M}\hat F_{c,h}(e)+\mathbb 1\{e\ge+\infty\}\Big],\qquad\qquad (8)
$$

in which every calibration building $c$ contributes the empirical distribution of its 24 studentised scores at stage $h$, and the new building contributes a point mass at $+\infty$. This is the hierarchical conformal prediction (HCP) weighting of Lee, Barber and Willett [24] applied per onboarding stage; unlike the closely related "pooling CDFs" rule of Dunn et al. [23], whose guarantee is asymptotic, it has a finite-sample guarantee. The interval is $[\hat y^{\mathrm{lo}}-\tilde q_h\,r_{b,h}\,s_{b,h},\;\hat y^{\mathrm{hi}}+\tilde q_h\,r_{b,h}\,s_{b,h}]$.

*Proposition 1 (stage-wise validity across new buildings).* Suppose the onboarding trajectories of the $M$ calibration buildings and of the new building are exchangeable, and $\sigma_0$, $\kappa_s$ and the forecaster are fixed. Then, for every stage $h$, $\Pr\{y_{b,t,J}\in C_{b,h,J}\}\ge 1-\alpha$, where $J$ is an hour drawn uniformly from the new building's valid hours at stage $h$ and the probability is over buildings and $J$.
*Proof sketch.* $\tilde e_{b,h,\cdot}$ is the same measurable function of each building's own trajectory up to stage $h$, so the $M+1$ vectors of stage-$h$ studentised scores are exchangeable across buildings. Applying an independent uniform random permutation to the hours within each building makes them exchangeable within buildings as well, while leaving Eq. (8) unchanged and making $J$ the first permuted hour. The data are then hierarchically exchangeable, and Theorem 1 of Lee et al. [24] gives coverage $\ge 1-\alpha$. ∎
The proposition guarantees coverage *on average over new buildings at each onboarding day*, from day 1 on, which no shrinkage estimator with $0<\kappa<\infty$ does. It does not guarantee per-building coverage, which is impossible distribution-free [44]. In our protocol, calibration and target buildings are onboarded in different years, and $\sigma_0$ is estimated from the calibration buildings (leave-one-out for calibration buildings), so the assumption holds only approximately; reliability is therefore assessed empirically. **HSC-SSC** applies the shrinkage of Eq. (5) to the studentised scores, combining the stage-wise scale adaptation with own-quantile shrinkage.

## DRAFT 2.5 Selection objective
The pseudo-count (and λ for QShrink, γ for ACI) is selected by leave-one-building-out on calibration buildings with one of two objectives: the mean normalised interval score (IS objective) or the mean absolute per-building coverage deviation (coverage objective; ties broken by the interval score). The coverage objective matches the reliability target of Section 2.1 but ignores sharpness. Online level control (ACI) can drive per-building coverage to nominal with a large step size, but its intervals then alternate between very wide and very narrow. Every strategy is therefore judged jointly on reliability and sharpness (Section 4.2, Fig. X).

## DRAFT 3.4 Operational evaluation: day-ahead capacity headroom
Consider an operator (aggregator, energy manager or DSO) that offers, for each building and hour, a day-ahead capacity headroom $H=\bar P-U$ below a contracted limit $\bar P$, for example to host flexible EV-charging or heat-pump load. The upper interval bound $U$ is used as the planning load, and the offer earns revenue in proportion to $H$. Whenever the realised load exceeds $U$, the operator pays a penalty proportional to the violation $(y-U)_+$. Up to a constant, the relative cost per building is
$$
\mathrm{cost}_b(\rho)=\frac{\overline{U}+\rho\,\overline{(y-U)_+}}{\bar y_b},\qquad\qquad (9)
$$
the upper half of the interval score with penalty ratio $\rho$. The 90 % central interval places $U$ at the 95 % quantile, which is cost-optimal for $\rho=20$. We report $\rho\in\{10,20,40\}$, together with the share of *under-protected* buildings, i.e. those whose upper bound is exceeded in more than 10 % of hours (twice the nominal 5 %). This operational outcome makes the consequence of per-building unreliability concrete: a few under-protected buildings generate most of the penalty exposure.
