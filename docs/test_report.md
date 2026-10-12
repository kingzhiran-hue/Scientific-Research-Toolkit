# Actual implementation and acceptance tests

## Result

ALL_TESTS_PASS=YES
INDEPENDENT_ENVIRONMENT_TEST=PASS

Executed on Windows x64 using Python 3.12.14 and R 4.6.0. All supplied data and diagrams are invented. The final independent run completed **25 commands with exit code 0**. This includes the standalone test command in an initially empty-output workspace, the exact module commands documented in README, optional package installation/entry point, console editing, Python/R API examples and opening the final generated figures.

| Suite | Actual result |
|---|---|
| Digitizer | 19 unittest tests passed |
| Continuous-outcome meta-analysis | 44 checks passed |
| Plotting | 34 checks passed |
| File validation | Eight PDF/SVG/600-DPI PNG sets opened/parsed; PDF text and numerical content checked |
| Independent output comparison | 26/26 deterministic statistical/measurement files matched byte-for-byte |
| Visual review | Eight rendered main examples plus long-label and single-effect cases inspected; no clipping or evident layout faults in these examples |
| Local browser interface | Clicked points invalidate confirmation; unconfirmed save rejected; original invented configuration restored and three confirmed groups saved successfully |

## Independent numerical references

MD/variance, SEM conversion and the default approximate-J g/df variance were checked using separate hand formulas. Exact-J/LS g was checked against metafor::escalc. REML, PM and DL tau2/point estimates/HK SE/CI/p/weights were checked against metafor::rma.uni(test='knha'). Q-based I2 and Riley PI were checked with explicit independent calculations using reference model outputs; the reference software's default PI was not substituted. Each leave-one-out fit was separately checked against metafor. Tests also cover q<1 without a variance floor, k=1/k=2, zero-residual inference, missing/invalid inputs, shared controls, dependence and extreme numeric ranges.

The tests are inspectable source files, not success declarations from running the same calculation twice.

## Independence and scope

A new workspace received only generic code and invented fixtures, without outputs. A fresh Python virtual environment installed the listed dependencies. Ten R packages loaded from a separate software library, verified individually. The same Windows host and R engine were used; this is **not** a new operating-system or cross-platform test. R software distributions were provisioned by copying installed package distributions, not by copying any previous research project dependency directory. The archived-version installer was executed with the exact packages already present; a fresh compiler/download workflow remains untested.

Initial checks exposed UTF-8 R library loading and missing transitive reference dependencies; the library bootstrap and complete dependency list were corrected, and the final clean run passed. Existing host startup locale warnings were nonfatal; no numerical/test failure was accepted as a pass.

`test_report.json` records sanitized actual commands, dependency-independent source/input SHA256, output SHA256, suite results and exact output comparisons. Vector file metadata timestamps can vary; numerical/measurement outputs were compared exactly. The tests do not establish empirical accuracy on every published chart, scientific appropriateness of user inputs, or full reproduction of any prior review.
