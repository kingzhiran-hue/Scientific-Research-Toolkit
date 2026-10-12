# Scientific Figure Generator

Run the eight working examples listed in README, or `python toolkit.py demo` for all of them. This module draws input statistics without fitting models or changing supplied labels/judgments.

## Input schemas

| Figure | Fields |
|---|---|
| forest | `id`, `yi`, `ci_low`, `ci_high`; optional `results.json` from meta module for pooled result |
| sensitivity, loo, comparison | `analysis` or `label`, `estimate`, `ci_low`, `ci_high`; optional `pi_low`, `pi_high` |
| rob-summary, rob-matrix | long-form `study`, `domain`, `judgment` in LOW/UNCLEAR/HIGH/NR |
| evidence | wide-form unique `id`, then observation-coded measure columns |
| prisma | JSON: identified, duplicates, screened, title_excluded, sought, not_retrieved, assessed, fulltext_excluded, included |

For effect plots, a paired missing CI means unavailable inference; infinite or reversed intervals are rejected. Individual effect CIs are provided inputs, normally normal-theory intervals, not incorrectly relabeled HK CIs. Pooled intervals use the selected analysis method. A k=1 result is labeled a single effect, not a pooled estimate.

Evidence codes: UP, DOWN, NO_CHANGE, QUALITATIVE_UP, QUALITATIVE_DOWN, NR. Codes are observed directions supplied by the user, not predefined beneficial directions. Qualitative/NR cells stay explicit; no mediation, causal claim or effect correlation is inferred.

RoB summary bar percentages use reported domain assessments; missing matrix cells display NR. The plotting module is not an RoB assessment tool. The PRISMA-style figure checks arithmetic but implements a simple single-stream records/reports layout, not every official PRISMA variant. Database-specific branches, study/report families and exclusion reason lists must be reported separately if needed; supplied counts are not validated against real screening logs.

## Configurable appearance

`plot_config.json` is a working configuration. Supported fields: `title`, `xlab`, `font`, `font_size`, `width` and `height` in inches, `dpi`, `primary` and `secondary` colors, `formats` (pdf/svg/png), `show_CI`, `show_PI`, `show_I2`, and `legend` (boolean).

`legend_labels` optionally overrides `CI`, `PI`, LOW/UNCLEAR/HIGH/NR, `evidence`, or `prisma` text. `rob_colors` can supply named colors for all four risk categories. The point editor has separate image controls and does not use these R settings.

`show_I2` affects the pooled forest annotation; the software does not invent I2 for figures whose input lacks it. `show_CI`/`show_PI` affect interval displays and their legends. Width/height, font availability and label length require user inspection. Cairo PDF and SVG are vector; PNG is raster at the requested DPI. All formats use the same draw function. Device files can contain different metadata timestamps even when the numeric content is identical.

## R API

```r
source('plotting/core.R')
z <- read.csv('outputs/meta/specifications.csv')
z$label <- z$analysis
interval_plot(z, 'outputs/api_comparison', list(title='Synthetic comparison'))
```

Other functions: `rob_plot(z,stem,cfg,matrix=FALSE)`, `evidence_plot(z,stem,cfg)`, `prisma_plot(counts,stem,cfg)`. Modules have no private project dependency. Every included example is invented and reproducible.
