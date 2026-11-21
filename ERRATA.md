# Errata

## Errors in published sources

- **Tsitouras 5(4)**, preprint of Tsitouras (2011), Comput. Math. Appl. 62:770-775, Table 1 (archived copy of 2012). The error weight b̂₇ is printed as +1/66. With +1/66 the error weights do not sum to 0 and b − b̂ fails order 1; with −1/66, b − b̂ has order 4 (residuals below 1.5e-15). Every library copy uses −1/66, so the libraries are right. Stepanov (2022, arXiv:2108.12590, caption of Table 4) notes the same. The journal version was not checked.
- **PEP(4,2,5)**, Barrios de León, Ketcheson and Ranocha, arXiv:2407.15365v2, Appendix A, eq. (31). The nodes are printed as c = (0, 1/10, 19/20, 37/63), but the row sums of the printed A are (0, 1/10, 37/63, 19/20), and b·c = 1/2 holds only with the row sums. The third and fourth nodes are swapped in the paper; Irksome copied it (see below).

## Library defects confirmed by the maintainers

| Library | Table | Defect | Effect | Report |
|---|---|---|---|---|
| OrdinaryDiffEq.jl (and the same table in DiffEqDevTools.jl) | Feagin12 | node c₂ = 2, should be 0.2 (Feagin's file) | order 1 on problems where f depends on t | [#5001](https://github.com/SciML/OrdinaryDiffEq.jl/issues/5001), fixed in [PR #5002](https://github.com/SciML/OrdinaryDiffEq.jl/pull/5002) |
| Irksome | PEPRK(4, 2, 5) | c₃ and c₄ swapped, as in the paper | time-dependent forcing sampled at the wrong times | [#293](https://github.com/firedrakeproject/Irksome/issues/293); already fixed on main |

Earlier, [qmat #23](https://github.com/Parallel-in-Time/qmat/issues/23) (order labels one too high) and [#25](https://github.com/Parallel-in-Time/qmat/issues/25) (RK21 weights) were confirmed and fixed. Neither shows as a failing table here: #23 was fixed before the version read, and #25 is about agreement with the cited paper, not the order.

Other defects found in this census have been reported to their libraries and are waiting for a reply. They are not listed, and their tables are not in `data/`, until the maintainers confirm them; 24 table rows in 10 libraries are held back for this reason.

## Failures that are not defects

A table can fail a check on purpose. These are in the data with their labels:

| Table | Why it fails a check | Label |
|---|---|---|
| Lobatto IIIB (DiffEqDevTools.jl, Trilinos Tempus), Radau IA 1 stage (Trilinos Tempus) | the stage times c differ from the row sums of A by construction (Hairer and Wanner II, IV.5); the order holds | by design |
| Irksome RadauIIA(1), BackwardEuler, GaussLegendre(1) | one stage, so the embedded weights computed by the library are zero and the embedded order is 0 | by design |
| rklib rks5 and rk8_10 | Shanks's approximate formulas: fewer stages than the order needs, so the conditions hold only approximately (Shanks 1966) | approximate order by design |
| OrdinaryDiffEq.jl Anas5 | order 5 only when the parameter w matches the problem's frequency; order 4 otherwise, as the documentation says | by design |
| OrdinaryDiffEq.jl SIR54 | order 5 only for quadratic right-hand sides (the trees with f‴ are not satisfied), as designed | by design |
| Irksome GaussLegendre(5) | an A-stability false alarm from round-off in physverify 0.8.0, fixed in 0.9.0 | tool false alarm |
| DiffEqDevTools.jl LobattoIIID2 | the stage times c = (0, 1) differ from the row sums of A, (1, 0); the order holds, and whether this layout matches the source is open | question (source layout) |
