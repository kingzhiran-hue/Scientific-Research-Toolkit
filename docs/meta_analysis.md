# General Meta-analysis Toolkit

## Required input and assumptions

Each row is an independent comparison. Always provide unique `id`, unique `independence_id`, and `independent=TRUE`. An independence id represents the animal/participant cohort, not merely a different outcome name. Optional `shared_control` and `control_id` identify known control reuse. Repeated cohorts, a FALSE independence flag or shared/reused controls are rejected. The software cannot detect undeclared dependence from numbers; users must verify cohort structure. Split-control, multilevel, correlated-effect and network methods are not provided.

### Group summaries

Required fields: `mean_t`, `mean_c`, `error_t`, `error_c`, `error_type_t`, `error_type_c`, `n_t`, `n_c`. Error types must explicitly be SD or SEM; n must be an integer >=2. Numeric fields must be finite, errors nonnegative and resulting sampling variances positive. `unit` is required for MD and must be a single known compatible unit. No automatic unit conversion is performed. `construct`, if supplied, must be the same across all rows; equivalent labels alone do not establish scientific commensurability.

### Direct effects

Use `--input-type effects`; provide `yi` and positive `vi`, or positive `se` with `vi=se^2`. If both are supplied they must agree. `effect_measure`, if present, must match the selected MD/Hedges_g. MD still requires units. n is not necessary to analyze supplied effects; the total N is then unknown. If group n fields are supplied, both must be valid. A user may use different raw units for g only after establishing the same outcome construct and orientation.

The example CSVs are complete invented templates. Do not infer missing n, SD or SEM from p values or significance stars.

## Effect-size conventions

Convert SEM to SD by `SD = SEM * sqrt(n)` independently for each group.

MD: `yi = mean_t - mean_c`; `vi = SD_t^2/n_t + SD_c^2/n_c`.

For g, let `df = n_t+n_c-2`, `N=n_t+n_c`, and `sp^2=((n_t-1)SD_t^2+(n_c-1)SD_c^2)/df`.

The default is the explicit approximation `J=1-3/(4df-1)`, `g=J*(mean_t-mean_c)/sp`, with approximate variance `vi=N/(n_t*n_c)+g^2/(2df)`. These conventions are intentionally reported; they are not asserted to equal every software default.

Optional `--g-correction exact --g-variance LS` uses `J=Gamma(df/2)/(sqrt(df/2)*Gamma((df-1)/2))` and denominator N instead of df in the second variance term. This alternative is tested against `metafor::escalc(measure='SMD', vtype='LS')`. All combinations are recorded, and neither correction nor variance choice is silently substituted. Very small samples merit special methodological review; approximations can differ appreciably.

## Random-effects estimation and inference

For heterogeneity variance `tau2`, weights are `wi=1/(vi+tau2)` and `mu=sum(wi*yi)/sum(wi)`.

REML solves `sum(wi^2*(yi-mu)^2) = sum(wi)-sum(wi^2)/sum(wi)`, with the variance constrained to >=0. PM solves `sum(wi*(yi-mu)^2)=k-1`. DL uses `max(0,(Q-(k-1))/(sum(1/vi)-sum((1/vi)^2)/sum(1/vi)))`. Root-based methods use deterministic numerical bracketing and tolerance.

**Unmodified Hartung–Knapp:** `q=sum(wi*(yi-mu)^2)/(k-1)`, `V_HK=q/sum(wi)`, `SE_HK=sqrt(V_HK)`. The confidence interval is `mu ± t_(1-alpha/2,k-1)*SE_HK`; the two-sided p value uses the same t distribution. There is no `max(1,q)` adjustment. q<1 is retained. With zero residual variance, HK inference is degenerate: the output says so and does not supply a misleading p value.

**Riley-type prediction interval:** `mu ± t_(1-alpha/2,k-2)*sqrt(tau2+V_HK)`. The PI combines between-study variance and uncertainty in the mean, with df k−2. This is an explicitly chosen approximation, not the default PI obtained merely by calling reference software. In particular, metafor's default prediction degrees of freedom can differ. At k<3 the PI is not estimable; at k=1 there is no pooled inference. Small-k prediction is intrinsically uncertain.

Fixed-effect weights `1/vi` define Cochran Q. `I2=max(0,1-(k-1)/Q)*100`, with I2=0 when Q=0. This is the Q-based definition, which can differ from a tau2-based definition. Q df/p, HK df/p, tau2, weights, N when known, CI, PI and all method choices are exported.

## Sensitivity and subsets

The primary selected estimator, PM, DL and leave-one-out results are exported. `analysis_config.json` demonstrates named `subsets` with `where` conditions (`field`, `operator`, `value`) and optional `exclude=true`. Operators: eq, ne, in, lt, le, gt, ge. Conditions combine by AND; a value list can implement OR within one field using `in`. Missing filter values and unknown fields/operators fail explicitly. Empty subsets are reported as not estimable, not fitted by force. No arbitrary R code is evaluated from a configuration.

Results do not establish a favorable effect direction; users determine clinical/scientific interpretation. N sums independent group sizes when available and is not a reconstructed total for repeated cohorts.

## R API

```r
source('meta_analysis/core.R')
z <- read.csv('examples/synthetic_data/groups.csv')
e <- effect_sizes(z, measure='MD')
a <- fit_meta(e, method='REML', level=.95)
```

## Method/reference documentation

The independent reference checks use [metafor model documentation](https://wviechtb.github.io/metafor/reference/rma.uni.html), [effect-size conventions](https://wviechtb.github.io/metafor/reference/escalc.html), and [prediction documentation](https://wviechtb.github.io/metafor/reference/predict.rma.html). These pages explain HKSJ and alternative variance/PI conventions. The formulas above, rather than unstated package defaults, define this implementation. This toolkit supplies methods; it does not reproduce any previous study's full workflow.
