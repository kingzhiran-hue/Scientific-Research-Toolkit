# Dependency inventory

Actual versions used for the acceptance runs (Windows x64):

| Component | Tested version | Role | License reported by installed distribution |
|---|---|---|---|
| Python | 3.12.14 | Digitizer, command runner, tests | Python Software Foundation license |
| NumPy | 2.3.5 | Calibration and pixel arrays | BSD-3-Clause; binary distributions have additional component notices |
| Pillow | 12.3.0 | Image reading and overlays | MIT-CMU; distribution includes component notices |
| PyMuPDF | 1.28.2 | Optional development-only PDF validation/rendering | AGPL-3.0 or Artifex commercial license |
| R | 4.6.0 | Statistical and drawing engine | GPL-2/GPL-3 |
| jsonlite | 2.0.0 | Runtime JSON read/write | MIT + file LICENSE |
| metafor | 5.0-1 | Separate reference calculations in tests | GPL >=2 |
| metadat | 1.6-0 | Reference software dependency | GPL >=2 |
| Matrix | 1.7-5 | Reference software dependency | GPL >=2 plus distribution LICENCE |
| numDeriv | 2016.8-1.1 | Reference software dependency | GPL-2 |
| mathjaxr | 2.0-0 | Reference software dependency | GPL-3 |
| pbapply | 1.7-4 | Reference software dependency | GPL >=2 |
| digest | 0.6.39 | Reference software dependency | GPL >=2 |
| nlme | 3.1-169 | Recommended R dependency | GPL >=2 |
| lattice | 0.22-9 | Recommended R dependency | GPL >=2 |
| remotes | Optional installation utility | Installs archived R package versions if needed | GPL-2 |
| setuptools | Build requirement >=68 | Optional Python package installation | MIT |

R base/recommended grid, grDevices, stats, utils and tools are used directly. The installed `packageVersion()` representation may replace hyphens with dots; the table uses DESCRIPTION versions. `environment/check.R` prints actual installed package versions.

Core Python requirements and development PDF tooling are separated in requirements.txt and requirements-dev.txt. These versions were installed into a new virtual environment for the independent test. The R acceptance run used a separate library containing installed software distributions, with every tested package's loaded location verified. It reused the same host R engine; it was not a test of a new operating system or a fresh compiler installation.

The optional archived-version R installer can require Rtools/compiler support for source packages. It was exercised in the independent library with already provisioned exact versions. Automatic download-and-compilation of every archived package on a brand-new computer was not separately validated. No dependency binary or third-party package source is included in the candidate ZIP.

Dependency licensing remains separate from the pending toolkit license. [NumPy license](https://numpy.org/doc/stable/license.html), [Pillow distribution license](https://pillow.readthedocs.io/en/stable/about.html#license), and [PyMuPDF licensing](https://pymupdf.readthedocs.io/en/latest/about.html#license-and-copyright) provide the corresponding upstream information. Package DESCRIPTION metadata supplies the R license inventory.
