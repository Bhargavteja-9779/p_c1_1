# Experimental setup {#sec:setup}

## Data

**BDG2.** The Building Data Genome Project 2 [@miller2020bdg2] provides two years (2016–2017) of hourly meter data from non-residential buildings on university and public campuses in North America and Europe, together with site weather and building metadata. It is the dataset of the ASHRAE Great Energy Predictor III competition [@miller2020gepiii]. We use the cleaned electricity meters, site air temperature and the primary-space-usage attribute.

**UCI.** The ElectricityLoadDiagrams20112014 dataset [@trindade2015] contains 15-min consumption of {{n_uci_raw}} Portuguese electricity clients (2011–2014). We aggregate it to hourly energy and use 2012–2014, because most clients have no data in 2011. It has no weather or metadata and represents a different country, customer mix and metering infrastructure. We use it to test generality and transfer.

**Quality rules** (applied identically to all methods and fixed before the main experiments): runs of at least 24 identical consecutive readings (meter outage or stuck meter) are treated as missing; gaps of at most 6 h are linearly interpolated; a building is retained if at most 5 % of its hours are missing in every period used and its mean load is at least 1 kWh/h. This leaves **{{n_bdg2}} BDG2 buildings at {{n_sites}} sites** and **{{n_uci}} UCI clients** (Fig. [-@fig:data]). Training rows whose normalised target exceeds 20 (meter restarts after near-zero history) are excluded from model fitting only.

## Protocols and leakage control

*Random-building protocol (main).* For each of five pre-specified seeds, buildings are randomly partitioned into training (50 %, of which one tenth is held out as building-disjoint validation data for early stopping), calibration (20 %) and target (30 %) sets. The forecaster and all calibration scores use only the training period (BDG2: 2016; UCI: 2012–2013). Each calibration building is "onboarded" at a random date in the training period. Each target building is onboarded at a random date in the later period (BDG2: 2017; UCI: 2014), drawn among windows with at least 80 % valid hours. Every building is followed for 56 day-ahead forecasts ($h=1,\dots,56$). Features at stage $h$ use only the $h$ days after $t_{0,b}$ (verified by unit tests that perturb all data outside this window). Target buildings, their period and their data are therefore never seen by the forecaster, the calibration scores, or any hyper-parameter selection.

*Leave-site-out (BDG2).* The 12 sites are grouped into five folds of similar size. All buildings of a fold are targets; the remaining buildings are split 70/30 into training and calibration sets. This tests transfer to unseen campuses, climates and operators.

*Cross-dataset.* Models and calibration scores from one dataset are applied to the target buildings of the other (BDG2→UCI and UCI→BDG2), without weather features, which UCI lacks. A BDG2→BDG2 run without weather serves as the within-dataset reference (three seeds each).

## Compared methods

All conformal-type methods share the same forecaster, scores, grid and stage bins; they differ only in how the radius $q_{b,h}$ is obtained.

* **Naive+SCP** (classical): seasonal-naive forecast (same hour one week earlier if $h\ge7$, else the previous day) with stage-matched split conformal intervals.
* **Raw-SCP**: split conformal prediction on unnormalised absolute residuals (kWh).
* **SCP**: split conformal on normalised absolute scores pooled over all stages [@lei2018].
* **SCP-stage**: as SCP, with stage-bin matching (the score-weighted analogue of HSC with $\kappa=\infty$, $K=$ all, whose prior weights buildings equally).
* **Mondrian-usage** (BDG2): SCP-stage computed separately per primary-usage class (classes with at least 10 calibration buildings), a group-conditional (Mondrian) variant [@vovk2005].
* **Self-CP**: split conformal on the building's own past scores ($\kappa=0$), falling back to SCP-stage until enough own scores exist.
* **ACI** [@gibbs2021]: adaptive conformal inference on top of the SCP-stage distribution, $\alpha_{h+1}=\alpha_h+\gamma\sum_j(\alpha-\mathrm{err}_{h,j})$, with $\gamma$ chosen by leave-one-building-out on calibration buildings from $\{0,10^{-4},2\!\times\!10^{-4},5\!\times\!10^{-4},10^{-3},2\!\times\!10^{-3},5\!\times\!10^{-3},10^{-2}\}$ (the three smallest values were added after a code audit showed that the pre-registered grid's lower edge was selected in most runs; $\gamma=0$ recovers the pooled method). When $\alpha_h$ leaves $[0,1]$, the radius is set to the largest grid value ($\alpha_h\le 0$) or to the smallest observed score ($\alpha_h\ge1$, empty-set convention).
* **QR-LGBM**: direct LightGBM quantile regression [@ke2017; @koenker1978].
* **CQR** [@romano2019]: QR-LGBM conformalised with stage-matched pooled CQR scores.
* **MLP-Gauss**: a global multilayer perceptron (256-256-128, ReLU) with a Gaussian output trained by negative log-likelihood, a deep probabilistic baseline in the spirit of DeepAR's likelihood training [@salinas2020].
* **MLP-QR**: the same network trained with the pinball loss for the two quantiles [@wang2019pinball].
* **Self-CQR** and **ACI-CQR**: self-only calibration and ACI applied to the CQR scores (same quantile models as CQR).
* **TQA-B-CQR** [@lin2022tqa]: temporal quantile adjustment ("budgeting" variant) on the CQR scores. The building's exponentially decayed mean own score (decay 0.8 per day, normalised by the weight sum, days before the forecast only) is ranked among the calibration buildings' decayed means at the same stage; the rank $r=|\{j:\bar e_j<\bar e_b\}|/(N+1)$ is mapped to the queried level $1-a$ with $a=\alpha-\lambda g^B(r)$, $g^B(r)=C(r-(1-\alpha))$ for $r<1-\alpha$ and $r-(1-\alpha)$ otherwise, $C=\alpha^2/(1-\alpha)^2$, $\lambda\le1$ chosen per stage so that $a\ge0.01$, and the quantile is taken over the pooled scores together with a point at $+\infty$, as in the original method; the paper's TQA-E variant is an ACI-type update and is represented by ACI-CQR.
* **GHCP-CQR**: the calibration step of generalised hierarchical conformal prediction [@mallick2026], adapted to our setting: with $M$ calibration buildings, every calibration building receives total weight $1/(M+1)$ spread over its scores (pooled over all onboarding stages, since GHCP has no notion of stages), and the new building receives the same group share, spread over its observed own scores and a point mass at $+\infty$ for its not-yet-observed scores. Deviations from the original: the surrogate group size is the median number of scores per calibration building (≈1344 in all runs) instead of a randomly drawn donor, and no observations are set aside to fit a local predictor, because our global forecaster already conditions on the building's own history (omitting this step most likely favours GHCP-CQR). GHCP's finite-sample guarantee relies on within-group exchangeability, which hourly loads violate.
* **QShrink-CQR** (regularised Mondrian [@rafe2026]): quantile-level shrinkage $q=w\,q^{\mathrm{own}}+(1-w)\,q^{\mathrm{pool}}$ with $w=n_{b,h}/(n_{b,h}+\lambda)$, $q^{\mathrm{own}}$ the split-conformal quantile of the own scores (w = 0 while undefined) and $q^{\mathrm{pool}}$ the CQR radius; $\lambda$ is selected by leave-one-building-out from the same grid as $\kappa$, including $\lambda=0$ (own quantile whenever it exists) and $\lambda=\infty$ (pooled CQR radius).
* **HSC** and **HSC-CQR**: Eq. ([-@eq:hsc]) with all three elements (stage matching, similarity prior, shrinkage) applied to absolute and CQR scores; **HSC simple** and **HSC-CQR simple**: the same with a uniform prior ($K$ = all) and without stage matching, i.e. a single pseudo-count shrinkage towards the pooled score distribution; **HSC-CQR fixed-κ**: HSC-CQR simple with the pseudo-count fixed at one week of hourly scores ($\kappa=168$) instead of being selected — a donor–local mixture with fixed pseudo-count as in [@jeon2026].
* **CQR (MLP)** and **HSC-CQR (MLP)**: CQR and HSC-CQR simple on the quantiles of the MLP quantile model, to check that the calibration layer is not specific to LightGBM.

The neural networks use the same features (missing values set to zero with missingness indicators, standardised), Adam (learning rate $10^{-3}$, batch 4096), at most 12 epochs, and early stopping on the validation buildings (patience 3). LightGBM uses 63 leaves, learning rate 0.05, at least 200 samples per leaf, 0.8 feature and bagging fractions, L2 regularisation 1, and early stopping (50 rounds) on the validation buildings. These are conventional settings, applied identically to point and quantile models. No method was tuned on target buildings.

## Metrics and statistical analysis

For target building $b$ with valid hourly observations over its 56-day window, we compute coverage $\mathrm{cov}_b$, relative width $\overline{U-L}/\bar y_b$, and the relative interval (Winkler) score [@winkler1972; @gneiting2007]

$$
\mathrm{IS}_b=\frac{1}{\bar y_b}\,\overline{(U-L)+\tfrac{2}{\alpha}(L-y)_+ +\tfrac{2}{\alpha}(y-U)_+},
$$ {#eq:is}

a proper score that rewards narrow intervals and penalises misses in proportion to their size. Across buildings we report the mean coverage; the **mean absolute coverage deviation** $\mathrm{MACD}=\mathrm{mean}_b|\mathrm{cov}_b-(1-\alpha)|$; the **under-covered share**, i.e. the share of buildings with $\mathrm{cov}_b<1-\alpha-0.05$; the 10th percentile of $\mathrm{cov}_b$; and the medians of relative width and $\mathrm{IS}_b$. The medians are used because a few buildings with erratic loads dominate means. Means are reported in the supplementary tables. Point accuracy is reported as CV(RMSE) [@ashrae14].

The unit of statistical analysis is the target building. A building's metrics are averaged over the seeds in which it was a target, and HSC variants are compared with each baseline by two-sided Wilcoxon signed-rank tests [@wilcoxon1945] on paired per-building values of $\mathrm{IS}_b$ and $|\mathrm{cov}_b-(1-\alpha)|$. $p$-values are Holm-adjusted [@holm1979] within each family of comparisons. Effect sizes are matched-pairs rank-biserial correlations [@kerby2014], positive when HSC is better. 95 % confidence intervals of the mean paired difference come from a cluster bootstrap over sites for BDG2 (buildings at a site share weather and operation) and over buildings for UCI (2000 resamples). Seed-level results are reported as mean ± standard deviation over seeds. All settings were fixed in a pre-registration file before any full experiment was run.
