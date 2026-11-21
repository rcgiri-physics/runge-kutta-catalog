# rk-tables — Runge–Kutta tables from open-source ODE libraries, checked

Runge–Kutta coefficients are copied by hand from papers into code, and from code into more code. One wrong digit can lower a method's order without any visible sign: adaptive step control shrinks the step until the error looks fine, and a test on y′ = λy cannot see a wrong stage time.

This repository holds **823 Butcher tables read from 34 open-source libraries** at pinned versions, each checked against the order conditions, and grouped into **362 methods**. Use it to:

- **find the coefficients of a method** with their verified order, stage order and the libraries that carry them ([CATALOGUE.md](CATALOGUE.md));
- **see which methods were compared with their first published source** (paper, author's file or construction from the definition) and how closely the library copies agree ([SOURCES.md](SOURCES.md));
- **check a table you have** against the order conditions with [physverify](https://github.com/rcgiri-physics/physverify) (`physverify.butcher.check_tableau`), or compare it with the copies here;
- **read the errors found**, in published sources and in libraries ([ERRATA.md](ERRATA.md)).

## What is here

| File | Content |
|---|---|
| [CATALOGUE.md](CATALOGUE.md) | every method: name, stages, order, stage order, what it was checked against, which libraries carry it |
| [SOURCES.md](SOURCES.md) | 40 methods compared with their first published source, with the largest difference over all library copies |
| [ERRATA.md](ERRATA.md) | errors in published sources, defects confirmed by library maintainers, and failures that are not defects |
| [METHOD.md](METHOD.md) | how the tables were read and checked, and what was not covered |
| `data/tables.jsonl` | one line per library table: library, version, file, line, coefficients as printed and in exact form, the library's claim, the verdict, 50-digit residuals, the NodePy second opinion and the first-source comparison |
| `data/methods.jsonl` | one line per method: names, order, coefficients, libraries, references |
| `data/summary.json` | the counts |
| `scripts/verify.py` | re-checks every table with physverify: `pip install physverify mpmath`, then `python scripts/verify.py` |

## Results in brief (counts for these libraries only)

- Of the 847 tables read, 791 satisfy the order their library states, 39 do not, 16 state no order and 1 is truncated in the code.
- Each failure was reviewed by hand against its source, with an exact recheck and, where possible, a convergence run. More than half are defects; the others are by design (for example Lobatto IIIB, whose stage times differ from the row sums on purpose), approximate by construction, or open.
- 24 defect rows from 10 libraries are not published here yet: their maintainers have not confirmed them. They are counted above and will be added as replies arrive.
- Most defects show only when f depends on t, or only in the error estimate. **If you test an integrator, include a problem with explicit time dependence**, such as y′ = y cos t.
- NodePy recomputed the order of the 680 tables that passed by 2026-11-16 and agreed on all 680.

These counts describe this sample of libraries, chosen by availability. They are not an error rate for numerical software.

## Reproducing the checks

```bash
pip install physverify mpmath
python scripts/verify.py
# 823 reproduced, 0 not reproduced, 0 skipped (no order recorded) of 823 tables
```

For each table the script evaluates the coefficients as printed in the library, confirms the recorded order with `physverify.butcher.check_tableau`, and checks that the library's own claim gives the recorded verdict.

## Other families

The same census covered Rosenbrock and W-methods, IMEX coupling, dense output, symplectic splitting and linear multistep methods. Those results are summarised on the [physverify census page](https://rcgiri-physics.github.io/physverify/census/); their data will be added here later.

## Citing and licence

Cite as in [CITATION.cff](CITATION.cff). The data (`data/`, and the generated Markdown files) is under [CC BY 4.0](LICENSE-DATA); the scripts are under the [MIT licence](LICENSE). Coefficients are as published by the libraries and their sources; each table records where it was read.

Corrections are welcome: if a table, a name or a reference here is wrong, please open an issue.
