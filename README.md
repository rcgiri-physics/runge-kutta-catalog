# runge-kutta-catalog

**Runge–Kutta Butcher tableaux with original sources, order checks, and errata.**

Runge–Kutta coefficients are copied by hand from papers into code, and from code into more code. One wrong digit can lower a method's order without any visible sign: adaptive step control shrinks the step until the error looks fine, and a test on y′ = λy cannot see a wrong stage time. This catalogue shows where each table came from, how the library copies differ, and what was checked.

**823 tableaux from 34 open-source libraries**, each read at a pinned version and checked against the order conditions. 40 methods were compared with their first published source.

## Where to start

- **[START_HERE.md](START_HERE.md):** five widely used methods (classical RK4, Dormand–Prince 5(4), Tsitouras 5(4), SSPRK(3,3), Radau IIA) with a copyable tableau, the original reference and when you would use each.
- **[SOURCES.md](SOURCES.md):** the 40 methods compared with their first published source. Each card gives the reference with a DOI or archived link, how the comparison was made, how many library copies agree and how closely, and the tableau.
- **[ERRATA.md](ERRATA.md):** errors found in published sources and in libraries, and failures that are not defects.
- **[CATALOGUE.md](CATALOGUE.md):** every table, grouped by coefficients, with its order, stage order and the libraries that carry it.
- **[ROSENBROCK.md](ROSENBROCK.md):** 88 Rosenbrock and W-method tables from 10 libraries, with the order for the exact Jacobian, the order as a W-method (any approximate Jacobian), the embedded order, R(inf) and A-stability, each linked to its source file at a pinned commit.
- **[examples/convergence.py](examples/convergence.py):** runs the five start-here methods on y′ = y cos t, and shows a confirmed library defect (Feagin 12 with c₂ = 2) turning a 12th-order method into a first-order one on y′ = t.

## The counts, and how they relate

| | Count |
|---|---|
| Tables read from the libraries | 847 |
| Held back: defects reported but not yet confirmed by the maintainers | 24 (in 10 libraries) |
| **Tables published here** | **823** |
| Coefficient groups (tables whose A, b, c and embedded weights agree to 12 significant digits) | 362 |
| Distinct method names among them | 319 |
| Methods compared with their first published source | 40 |
| Tables with a NodePy second opinion (all agree) | 680 |

The same method can fall into several groups: a float copy and an exact copy differ beyond 12 digits, and some libraries add an embedded pair or an extra stage. The group count is therefore not a count of distinct methods. Of the 847 tables read, 791 satisfy the order their library states, 39 do not, 16 state no order and 1 is truncated in the code. Each failure was reviewed by hand; more than half are defects, the rest are by design, approximate by construction or open (see [ERRATA.md](ERRATA.md)). Held-back tables are added once the maintainers confirm.

Most defects show only when f depends on t, or only in the error estimate. **If you test an integrator, include a problem with explicit time dependence**, such as y′ = y cos t.

These counts describe this sample of libraries, chosen by availability. They are not an error rate for numerical software.

## Checking it yourself

```bash
pip install -r requirements.txt     # physverify, mpmath, numpy, pinned
python scripts/verify.py            # every table, double precision
python scripts/verify.py --precise --max-stages 13   # 50-digit residuals against the archive
python scripts/verify_rosenbrock.py # Rosenbrock tables: exact-Jacobian, W-method and embedded orders
python examples/convergence.py
```

`verify.py` evaluates each table from the strings printed in the library and checks, with `physverify.butcher.check_tableau`, that the recorded order holds, that the next order fails (below order 14, the highest checked), and that the library's own claim gives the recorded verdict. `--precise` recomputes the order-condition residuals over every rooted tree in 50-digit arithmetic and compares them with the archive. [scripts/example_source_to_record.py](scripts/example_source_to_record.py) shows how one record was made, reading SciPy's RK45 from the installed library. Reading the other 33 libraries and the comparisons with first sources were done in the census and are recorded per table, not re-run here. CI runs all of this on every push and weekly. Details: [METHOD.md](METHOD.md).

## Files

| File | Content |
|---|---|
| `data/tables.jsonl` | one line per table: library, version, file, line, coefficients as printed and exact, the library's claim, the verdict, 50-digit residuals, NodePy's order, first-source comparison |
| `data/methods.jsonl` | one line per coefficient group: display name, all names used, order, coefficients, libraries, references |
| `data/summary.json` | the counts above |
| `data/rosenbrock.jsonl` | one line per Rosenbrock table: library, commit and link to the source file, alpha, Gamma, b, embedded weights, orders, R(inf), A-stability margin |
| `scripts/` | `verify.py`, `verify_rosenbrock.py`, the page generators (`render.py`, `render_sources.py`, `render_start.py`, `render_rosenbrock.py`) and the SciPy example |

## Rosenbrock and W-methods

`data/rosenbrock.jsonl` holds 88 Rosenbrock tables from OrdinaryDiffEq.jl, Hairer's RODAS, PETSc, KPP, NCAR MICM, MESA, EarthSciIntegrator, Deneb, PyFR and OpenFOAM, in the standard (alpha, Gamma, b) form. Each record links to the library file at the commit read. `python scripts/verify_rosenbrock.py` recomputes the order with the exact Jacobian, the order as a W-method and the embedded order: all 88 reproduce, and all 37 order claims stored with a table are met. Three methods are compared with their first published source (`scripts/rosenbrock_sources.py`): ROS3P with Lang and Verwer (2001), 4 copies agree to 3.3e-16; RODAS with Hairer's own code, 7 copies agree to 3.6e-14; ROS2 with Verwer, Spee, Blom and Hundsdorfer (1999), 8 copies agree to 2.2e-16. Copies are found by their coefficients, which shows, for example, that OpenFOAM's `rodas34` is Hairer's RODAS and PETSc's `TSROSW2P` is ROS2. Not yet included: tables from libraries with reported but unconfirmed defects, first-source comparisons for the other Rosenbrock methods, and dense output.

## Other families

The census also covered IMEX coupling, dense output, symplectic splitting and linear multistep methods. Those results are summarised on the [physverify census page](https://rcgiri-physics.github.io/physverify/census/); their data will be added here later.

## Citing and licence

Cite as in [CITATION.cff](CITATION.cff); a Zenodo DOI will be added with the first public release. The data (`data/` and the generated pages) is under [CC BY 4.0](LICENSE-DATA), the scripts under the [MIT licence](LICENSE). Coefficients are as published by the libraries and their sources; each table records where it was read.

Corrections are welcome: if a table, a name or a reference here is wrong, please open an issue.
