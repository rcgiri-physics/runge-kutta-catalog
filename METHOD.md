# Method

## Reading the tables

Each library was read at a pinned version, recorded in every row of `data/tables.jsonl` (`version`, `file`, `line`). Python libraries were imported or parsed from source; Julia, C, C++, Fortran, Java and Rust libraries were parsed from source. The coefficients are stored exactly as printed (`coefficients_as_printed`) and, where every entry is rational or a closed form, in exact form (`coefficients_exact`). The library's own claim (order, embedded order, and where it is stated) is in `claim`.

The libraries were chosen by availability: widely used ODE libraries in Python, Julia, C/C++, Fortran, Java and Rust, plus some smaller projects found by searching for common method names. They are not a random sample.

## Checks

- **Order conditions.** `physverify.butcher.check_tableau` checks the claimed order, the embedded order, the stage times against the row sums of A, and the stability claims. The residuals of the order conditions were also computed to 50 digits up to order 14 (`residuals_50_digit`); `computed_order` is the highest order whose conditions hold.
- **Second opinion.** NodePy 1.0.1 recomputed the order of the 680 tables that passed by 2026-11-16, with its own rooted-tree code. All 680 agree. NodePy was not run on tables added later, on embedded weights, or on failing tables.
- **First sources.** Where the original was available, the library copies were compared with the method's first published source: the paper or report (Fehlberg 1968 and 1969, Ralston 1962, Ketcheson 2008, Kraaijevanger 1991, Tsitouras 2011), the author's own coefficient files (Verner, Feagin), the author's code (Hairer's dopri5.f), or a construction from the definition in a standard text (Gauss, Radau IIA, Lobatto IIIA and IIIC collocation methods; Euler, Runge, Heun and Kutta methods). Each check compares a table with the closest reference of the same size, so a large difference means a different method; only matches are listed in [SOURCES.md](SOURCES.md).
- **Review of failures.** Every failing table was read by eye against its source, rechecked in exact or 50-digit arithmetic, and, where possible, run in a convergence study in the library's own language (Julia, Fortran, Java, C). The label is in `review.label`.

## Grouping into methods

Tables are grouped into a method when A, b, c and the embedded weights agree to 12 significant digits. A float copy and an exact copy of the same method can land in different groups when one has fewer digits; both are listed. The method's display name is the reference name where a first-source check matched, otherwise the name most libraries use.

## What is not covered

- Only the tables, not the code that applies them. A correct table can be used by a step function with a bug (for example, a stage evaluated at the wrong time). Some of those cases were checked separately in the census and are on the [physverify census page](https://rcgiri-physics.github.io/physverify/census/).
- Dense output, Rosenbrock, IMEX coupling, symplectic and multistep coefficients are not in this dataset yet.
- A few sources could not be obtained (paywalled or offline), so those methods have no first-source check.

## Rebuilding

The data files are generated from the census working files, which are not public; `scripts/render.py` regenerates the Markdown pages from `data/`, and `scripts/verify.py` re-checks every table.
