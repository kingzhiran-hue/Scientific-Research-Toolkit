# Third-party licensing and notice requirements

Reviewed: 12 October 2026. Scope: imports, installation requirements, installed-package license metadata and source provenance for this source-only toolkit. The original toolkit code is [MIT-licensed](LICENSE), copyright (c) 2026 Jie Jin. Upstream components retain their own authorship and licenses.

## Code and packaging boundary

No copied third-party library implementation, dependency binary, bundled font or embedded dependency distribution was identified in the source tree. The code implements documented algorithms independently; separate reference packages are called by tests. Dependencies are downloaded/installed separately. This file is an inventory and compliance guide, not a substitute for upstream LICENSE/COPYING/NOTICE files if upstream material is redistributed.

## Inventory

| Component | Tested version / requirement | Use | License | Notices and conditions if redistributed or combined |
|---|---|---|---|---|
| Python | 3.12.14 | Interpreter | PSF license | Preserve the distribution's PSF and component license/copyright notices. |
| NumPy | 2.3.5 | Runtime calibration/pixel arrays | BSD-3-Clause | Retain copyright, conditions and disclaimer; observe nonendorsement clause; preserve additional binary-component notices. |
| Pillow | 12.3.0 | Runtime images/overlays | MIT-CMU | Retain upstream copyright/permission/disclaimer and third-party component notices; respect the restriction on using the rights holder's name in advertising without permission. |
| jsonlite | 2.0.0 | R runtime JSON | MIT + file LICENSE | Preserve the package-specific copyright from its LICENSE along with the MIT terms and any embedded component notices. |
| R and its base/recommended packages | 4.6.0 | Interpreter, grid/grDevices/stats/utils/tools | GPL-2 / GPL-3; component-specific terms | Preserve the R distribution's COPYING/COPYRIGHT and component notices; meet applicable source and redistribution requirements. Independently written scripts are not automatically relicensed merely by running the interpreter. |
| metafor | 5.0-1 | Independent reference tests | GPL >=2 | Retain upstream notices and license; comply with applicable GPL terms for distribution/combined works. |
| metadat | 1.6-0 | Reference dependency | GPL >=2 | Retain upstream notices/license and applicable GPL corresponding-source requirements. |
| Matrix | 1.7-5 | Reference dependency | GPL >=2 or file LICENCE, as recorded in DESCRIPTION | Preserve the complete distribution LICENCE and component notices; do not assume every embedded component has identical terms. |
| numDeriv | 2016.8-1.1 | Reference dependency | GPL-2 | Retain upstream notices/license and applicable GPL terms. |
| mathjaxr | 2.0-0 | Reference dependency | GPL-3 | Preserve GPL and bundled MathJax/component notices; check package license files before bundling. |
| pbapply | 1.7-4 | Reference dependency | GPL >=2 | Retain upstream notices/license and applicable GPL terms. |
| digest | 0.6.39 | Reference dependency | GPL >=2 | Preserve GPL and embedded hashing-code notices. |
| nlme | 3.1-169 | Recommended R dependency | GPL >=2 | Retain upstream notices/license and applicable GPL terms. |
| lattice | 0.22-9 | Recommended R dependency | GPL >=2 | Retain upstream notices/license and applicable GPL terms. |
| remotes | Optional installer | R installation | GPL-2 | Retain upstream notices/license if the utility is redistributed. |
| setuptools | >=68 | Optional Python build backend | MIT | Retain upstream copyright/permission/disclaimer and vendored component notices if bundled. |
| PyMuPDF / MuPDF | PyMuPDF 1.28.2 | Optional PDF validation/rendering tests | AGPL-3.0 or Artifex commercial license | Preserve upstream COPYING/notices; comply with AGPL corresponding-source and applicable network-interaction terms for covered works, or obtain an appropriate commercial license. The toolkit MIT license grants no commercial PyMuPDF license. |

## Compatibility conclusion

**Source-only MIT configuration: compatible with dependency-specific conditions.** No vendored third-party notices were removed or replaced. The permissive MIT terms allow the original toolkit material to be included in a GPL/AGPL-compliant combined work; recipients must still retain the MIT notice for that material. A covered combined distribution is not an MIT-only distribution. Do not infer that separately installed or optional dependencies have no license obligations. If redistributing dependencies, retain their actual package LICENSE/COPYING/NOTICE files and meet source, modification and other applicable requirements. Commercial PyMuPDF use outside AGPL compliance requires separate authorization from Artifex.

## Upstream references

- [MIT standard license](https://opensource.org/license/mit)
- [NumPy license and binary-component notices](https://numpy.org/doc/stable/license.html)
- [Pillow license](https://pillow.readthedocs.io/en/stable/about.html#license)
- [Python license](https://docs.python.org/3/license.html)
- [R licensing](https://www.r-project.org/Licenses/)
- [jsonlite package](https://cran.r-project.org/package=jsonlite)
- [metafor package](https://cran.r-project.org/package=metafor)
- [PyMuPDF license and copyright](https://pymupdf.readthedocs.io/en/latest/about.html#license-and-copyright)
- [setuptools license](https://github.com/pypa/setuptools/blob/main/LICENSE)

For the remaining R packages, use the package-specific DESCRIPTION and LICENSE/LICENCE/COPYING files from the exact installed version listed in [dependencies](docs/dependencies.md). Current upstream webpages may describe a newer version.
