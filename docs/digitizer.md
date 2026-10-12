# Scientific Figure Digitizer

## Workflow and attribution

1. Supply your own readable PNG, JPG or TIFF. Use the original resolution where possible.
2. Define the exact panel as `plot_region: [x_min, y_min, x_max, y_max]`. Coordinates are in the supplied image, top-left origin; y increases downward. Cropping or resizing requires recalibration; the software never silently transfers points between images.
3. Obtain tick values, group identities, error type and n from reliable source information. Candidate detection does not read labels or infer these facts.
4. Add at least two measured ticks per axis segment. More ticks permit residual checks. Confirm every bar top and upper/lower cap manually.
5. Inspect the output overlay and back-check converted means/endpoints against ticks. Keep the coordinate JSON with the measurement output.

The local point editor and console editor modify user-selected coordinates. They do not approve scientific attribution. The server binds `127.0.0.1`, serves only the selected image/configuration, checks foreign Origin headers on saves, and should be stopped when finished.

## Configuration

Use the working templates in `examples/synthetic_data/*_points.json`. Each segment has `id`, `scale` (`linear` or `log10`), ticks `pixel_y`/`value`, `pixel_range`, and an optional `max_residual` on the fitted scale (default 0.02 times the tick-value span on that scale). Each group has an id, x, `bar_y`, `upper_y`, `lower_y`, segment identifiers where needed, `variance_type`, `n`, and `confirmed: true`. Values cannot lie outside the calibrated span or selected panel. The existing templates are an authoritative schema example.

`SD`, `SEM`, `CI`, `OTHER`, and `NR` are allowed labels. n is a positive integer or null. Labels/n are user inputs, never image predictions. CI/OTHER/NR errors must not be passed directly to the SD/SEM meta-analysis input. Missing upper or lower endpoints remain missing. Upper and lower magnitudes are retained separately; asymmetric errors are never averaged or treated as a symmetric SD.

## Calibration

For a linear segment, least-squares calibration fits `value = intercept + slope * pixel_y`. For a log segment, it fits `log10(value) = intercept + slope * pixel_y`, then transforms each mean and cap separately by `10^prediction`. All log ticks must be positive. Residuals are reported on the fitted linear or log10 scale with the configured threshold relative to the tick span.

For a broken axis, segments must have nonoverlapping pixel ranges. Points in the break or outside all calibrated spans are rejected. When a bar and error cap occupy different valid segments, their separately transformed values can be subtracted; ordinary interpolation across the break is prohibited. Tick monotonicity, uniqueness and finite values are checked.

`error_upper = value_upper - mean`; `error_lower = mean - value_lower`. Endpoint order must be physically consistent. On a log axis, equal pixel offsets generally produce unequal numerical magnitudes. A two-tick calibration fits exactly and cannot reveal a misread tick; user verification remains essential.

## Candidate detection and limits

Projection-based axis/tick proposals identify dark ink and connected filled bar bodies. Cap proposals require a supporting central stem; broad bracket lines are rejected. These heuristics are tested on invented simple charts, not validated on all published figures. Outlined, stacked, overlapping, low-contrast, three-dimensional, compressed, perspective-distorted or heavily annotated charts generally need manual coordinates; unsuitable sources should not be measured. A failed proposal may be replaced with manual points, provided the source remains reliably measurable.

The software reports calibration residuals, source image basename/SHA256 and coordinates, but does not quantify all source-resolution or human-point uncertainty. An overlay is an aid to review, not proof that the chosen panel/group is correct.

## Python API

```python
import json
from digitizer import AxisCalibration, digitize
config = json.load(open('examples/synthetic_data/linear_points.json'))
result = digitize('examples/synthetic_data/linear.png', config, 'outputs/api_digitizer')
```

Import `propose` from `digitizer.detection` for candidate generation. The exact callable signatures are in the module source. Outputs are new files; do not choose an output directory containing inputs you wish to preserve.
