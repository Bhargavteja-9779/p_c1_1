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
* **SCP-stage**: as SCP, with stage-bin matching (HSC with $\kappa=\infty$, $K=$ all).
* **Mondrian-usage** (BDG2): SCP-stage computed separately per primary-usage class (classes with at least 10 calibration buildings), a group-conditional (Mondrian) variant [@vovk2005].
* **Self-CP**: split conformal on the building's own past scores ($\kappa=0$), falling back to SCP-stage until enough own scores exist.
* **ACI** [@gibbs2021]: adaptive conformal inference on top of the SCP-stage distribution, $\alpha_{h+1}=\alpha_h+\gamma\sum_j(\alpha-\mathrm{err}_{h,j})$, with $\gamma$ chosen by leave-one-building-out on calibration buildings from $\{5\!\times\!10^{-4},10^{-3},2\!\times\!10^{-3},5\!\times\!10^{-3},10^{-2}\}$.
* **QR-LGBM**: direct LightGBM quantile regression [@ke2017; @koenker1978].
* **CQR** [@romano2019]: QR-LGBM conformalised with stage-matched pooled CQR scores.
* **MLP-Gauss**: a global multilayer perceptron (256-256-128, ReLU) with a Gaussian output trained by negative log-likelihood, a deep probabilistic baseline in the spirit of DeepAR's likelihood training [@salinas2020].
* **MLP-QR**: the same network trained with the pinball loss for the two quantiles [@wang2019pinball].
* **HSC** and **HSC-CQR** (proposed): Eq. ([-@eq:hsc]) applied to absolute and CQR scores, respectively.

The neural networks use the same features (missing values set to zero with missingness indicators, standardised), Adam (learning rate $10^{-3}$, batch 4096), at most 12 epochs, and early stopping on the validation buildings (patience 3). LightGBM uses 63 leaves, learning rate 0.05, at least 200 samples per leaf, 0.8 feature and bagging fractions, L2 regularisation 1, and early stopping (50 rounds) on the validation buildings. These are conventional settings, applied identically to point and quantile models. No method was tuned on target buildings.

## Metrics and statistical analysis

For target building $b$ with valid hourly observations over its 56-day window, we compute coverage $\mathrm{cov}_b$, relative width $\overline{U-L}/\bar y_b$, and the relative interval (Winkler) score [@winkler1972; @gneiting2007]

$$
\mathrm{IS}_b=\frac{1}{\bar y_b}\,\overline{(U-L)+\tfrac{2}{\alpha}(L-y)_+ +\tfrac{2}{\alpha}(y-U)_+},
$$ {#eq:is}

a proper score that rewards narrow intervals and penalises misses in proportion to their size. Across buildings we report the mean coverage; the **mean absolute coverage deviation** $\mathrm{MACD}=\mathrm{mean}_b|\mathrm{cov}_b-(1-\alpha)|$; the **under-covered share**, i.e. the share of buildings with $\mathrm{cov}_b<1-\alpha-0.05$; the 10th percentile of $\mathrm{cov}_b$; and the medians of relative width and $\mathrm{IS}_b$. The medians are used because a few buildings with erratic loads dominate means. Means are reported in the supplementary tables. Point accuracy is reported as CV(RMSE) [@ashrae14].

The unit of statistical analysis is the target building. A building's metrics are averaged over the seeds in which it was a target, and HSC variants are compared with each baseline by two-sided Wilcoxon signed-rank tests [@wilcoxon1945] on paired per-building values of $\mathrm{IS}_b$ and $|\mathrm{cov}_b-(1-\alpha)|$. $p$-values are Holm-adjusted [@holm1979] within each family of comparisons. Effect sizes are matched-pairs rank-biserial correlations [@kerby2014], positive when HSC is better. 95 % confidence intervals of the mean paired difference come from a cluster bootstrap over sites for BDG2 (buildings at a site share weather and operation) and over buildings for UCI (2000 resamples). Seed-level results are reported as mean ± standard deviation over seeds. All settings were fixed in a pre-registration file before any full experiment was run.
