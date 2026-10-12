# Scientific Research Toolkit

Version **0.1.0 — independent repository candidate**. Licensed under the [MIT License](LICENSE).

Three independently callable modules provide semi-manual scientific bar-chart digitization, independent continuous-outcome meta-analysis, and configurable scientific figures. **All supplied inputs, diagrams, measurements and example results are Synthetic data**, invented expressly for software development. They are not anonymized research data or findings from a real review.

## Scope

| Module | Language | Supports |
|---|---|---|
| Scientific Figure Digitizer | Python | Candidate positions, user-confirmed points, linear/log/segmented calibration, asymmetric error endpoints, overlays, CSV/JSON and a local point editor |
| General Meta-analysis Toolkit | R | MD/Hedges g, SD/SEM inputs, direct effects/variances, REML/PM/DL, unmodified HKSJ, Riley-type PI, leave-one-out and structured subsets |
| Scientific Figure Generator | R | Eight figure types, supplied statistics only, PDF/SVG/PNG, configurable appearance and displayed elements |

This is not a universal automatic image reader. Automatic proposals are intended for isolated filled bars on a light background; the user must verify panel, group, axes and error caps. Complex pictures require manual points or may be unsuitable. SD/SEM and sample sizes are never inferred from image appearance. The meta-analysis module supports **independent two-group continuous outcomes**; shared controls, correlated outcomes, multilevel models, networks, RNA-seq and single-cell analyses are not implemented.

## Installation

Work from this repository's root. Install Python 3.11 or newer and R separately; the actually tested versions are in [dependencies](docs/dependencies.md). The following commands use `python` and `Rscript` from your PATH.

```sh
python -m venv .venv
```

Activate `.venv` (`.venv\Scripts\Activate.ps1` on Windows; `source .venv/bin/activate` on POSIX), then:

```sh
python -m pip install -r requirements.txt
Rscript --vanilla environment/install.R
```

For numerical/reference and rendered-PDF tests, also install:

```sh
python -m pip install -r requirements-dev.txt
```

Core Python dependencies are NumPy and Pillow. R runtime requires jsonlite; metafor and its dependencies are used for independent numerical tests. Rendering uses R's Cairo devices. `environment/install.R` installs the specified R package versions from CRAN archives; Internet access is required when packages are missing. Exact archived source versions that need compilation require the matching Rtools on Windows or a compiler toolchain on other systems. On an unsupported R version, install compatible packages explicitly and repeat the tests. This release has been tested on Windows only; no cross-platform validation claim is made.

Optional Python installation (`python -m pip install . --no-deps`) installs the `scientific-digitizer` entry point and Python API. The R modules and unified runner remain source files in this repository.

## Run the synthetic demonstration and tests

```sh
python toolkit.py examples
python toolkit.py demo
python toolkit.py test
python toolkit.py all
```

`all` regenerates invented fixtures, runs all three modules and executes tests. `test` generates prerequisites if demonstration outputs do not exist. Results are written beneath `outputs/`, which is excluded from the public candidate ZIP. To locate R explicitly, set `RSCRIPT` or use `python toolkit.py --rscript "path/to/Rscript" all`. No access to any prior research directory is required.

## Module commands

### A. Digitize user-confirmed points

```sh
python toolkit.py digitize propose --image examples/synthetic_data/bracket.png --region 80 90 830 560 --baseline 530 --out outputs/digitizer/candidates.json
python toolkit.py digitize measure --image examples/synthetic_data/linear.png --config examples/synthetic_data/linear_points.json --out outputs/digitizer/linear
python toolkit.py digitize gui --image examples/synthetic_data/linear.png --config examples/synthetic_data/linear_points.json --out outputs/gui_demo --port 8767
```

For the editor, open `http://127.0.0.1:8767/` locally. Select a group and coordinate field, click the source image, inspect and update its JSON, explicitly confirm each group, then Save. Stop the server with Ctrl+C. The editor binds only to localhost and sends no information to an external service. Console editing is also available by adding `--interactive` to `measure`.

Manual configuration examples cover linear, negative, nonzero-baseline, log and broken axes. Outputs: `measurements.csv`, `measurements.json`, `confirmed_coordinates.json`, `overlay.png`. Candidate proposals are unconfirmed and are **not** a ready-to-use measurement configuration. See [digitizer instructions](docs/digitizer.md).

### B. Analyze independent continuous comparisons

```sh
python toolkit.py meta --input examples/synthetic_data/groups.csv --out outputs/meta --measure MD --config examples/synthetic_data/analysis_config.json
python toolkit.py meta --input examples/synthetic_data/groups.csv --out outputs/meta_g --measure Hedges_g
python toolkit.py meta --input examples/synthetic_data/effects.csv --input-type effects --out outputs/meta_effects --measure MD
```

Use `--method PM` or `--method DL` to change the primary heterogeneity estimator. Output parameters explicitly identify the choice. `results.json`, `effects.csv`, `specifications.csv` and `leave_one_out.csv` preserve inputs/derived statistics. A one-effect input has no pooled inference; two effects have no Riley PI. Numerical conventions and input templates: [meta-analysis](docs/meta_analysis.md).

### C. Draw supplied results

```sh
python toolkit.py plot --type forest --input outputs/meta/effects.csv --results outputs/meta/results.json --out outputs/figures/forest --config examples/synthetic_data/plot_config.json
python toolkit.py plot --type sensitivity --input outputs/meta/specifications.csv --out outputs/figures/sensitivity --config examples/synthetic_data/plot_config.json
python toolkit.py plot --type loo --input outputs/meta/leave_one_out.csv --out outputs/figures/loo --config examples/synthetic_data/plot_config.json
python toolkit.py plot --type rob-summary --input examples/synthetic_data/risk_of_bias.csv --out outputs/figures/rob-summary --config examples/synthetic_data/plot_config.json
python toolkit.py plot --type rob-matrix --input examples/synthetic_data/risk_of_bias.csv --out outputs/figures/rob-matrix --config examples/synthetic_data/plot_config.json
python toolkit.py plot --type evidence --input examples/synthetic_data/evidence.csv --out outputs/figures/evidence --config examples/synthetic_data/plot_config.json
python toolkit.py plot --type prisma --input examples/synthetic_data/selection_counts.json --out outputs/figures/prisma --config examples/synthetic_data/plot_config.json
python toolkit.py plot --type comparison --input outputs/meta/specifications.csv --out outputs/figures/comparison --config examples/synthetic_data/plot_config.json
```

Each command produces PDF, SVG and PNG. The plotting module does not estimate new effects or change judgments. See [plotting](docs/plotting.md) for schemas and appearance options, including hiding CI/PI/I2 or legends.

## Evidence of implementation

See the [synthetic example gallery](docs/examples.md), [test report](docs/test_report.md), [privacy scan](docs/privacy_scan_report.md), [isolation report](docs/isolation_report.md), and [algorithm provenance](docs/provenance.md). Tests use hand calculations and separate reference software; they do not use real research inputs. Numerical equality cannot guarantee suitable study selection or correct user attribution. Users retain responsibility for their source interpretation, units, independence and methods.

## License, citation and publication

The toolkit's original source code, documentation and synthetic examples are licensed under the [MIT License](LICENSE), copyright (c) 2026 Jie Jin. Retain the copyright and full license notice when redistributing copies or substantial portions. Software is supplied without warranty under the license terms. [CITATION.cff](CITATION.cff) identifies Jie Jin as the software author; no unconfirmed contact details or identifiers are included.

Dependencies retain their own licenses. See [third-party notices](THIRD_PARTY_NOTICES.md), [licensing guidance](docs/licensing.md) and the [dependency inventory](docs/dependencies.md), including GPL-licensed R reference packages and optional AGPL/commercial PyMuPDF test tooling. The MIT grant does not relicense those dependencies or waive their requirements when used in combined software. The [upload preparation guide](docs/upload_preparation.md) covers source-only publication. No repository account was connected and no public upload was performed.

Short Chinese guide: [中文使用说明](docs/usage_zh.md).
