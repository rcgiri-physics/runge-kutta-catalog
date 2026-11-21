"""Write SOURCES.md: one card per method that was compared with its first published source.

Each card gives the reference (with a DOI or an archived link where one exists), how the comparison was made,
how many library copies were compared and how closely they agree, any copy that differs, and the tableau.
Run after any change to the data:  python scripts/render_sources.py
"""
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
methods = [json.loads(l) for l in open(ROOT / "data/methods.jsonl", encoding="utf-8")]
tables = {t["id"]: t for t in (json.loads(l) for l in open(ROOT / "data/tables.jsonl", encoding="utf-8"))}

HW2 = "Hairer and Wanner, *Solving Ordinary Differential Equations II*, 2nd ed. (Springer, 1996), Sect. IV.5"
DEF = "Built from the definition (collocation: nodes are the roots of the defining polynomial, " \
      "a_ij and b_j are integrals of the Lagrange polynomials), in 50-digit arithmetic, as in " + HW2 + "."
VERNER = "[Verner's coefficient files](https://web.archive.org/web/20260519035415/https://www.sfu.ca/~jverner/) " \
         "(J. H. Verner, Simon Fraser University; archived copy)"
FEAGIN = "[Feagin's coefficient files](https://web.archive.org/web/20190206083535/http://sce.uhcl.edu:80/rungekutta/) " \
         "(T. Feagin, University of Houston-Clear Lake; 60 digits; archived copy)"

# reference key (as recorded in data/tables.jsonl) -> (reference in Markdown, how the comparison was made)
REFS = {
    "Euler": ("L. Euler, *Institutionum calculi integralis*, vol. 1 (1768)", "The method's definition: y1 = y0 + h f(t0, y0)."),
    "explicit midpoint": ("C. Runge, Ueber die numerische Auflösung von Differentialgleichungen, *Math. Ann.* 46 (1895) 167-178, "
                          "[doi:10.1007/BF01446807](https://doi.org/10.1007/BF01446807)", "Built from the method's definition."),
    "Heun 2 / SSPRK22": ("K. Heun, Neue Methoden zur approximativen Integration der Differentialgleichungen einer unabhängigen "
                         "Veränderlichen, *Z. Math. Phys.* 45 (1900) 23-38; as SSPRK(2,2): C.-W. Shu and S. Osher, *J. Comput. "
                         "Phys.* 77 (1988) 439-471, [doi:10.1016/0021-9991(88)90177-5](https://doi.org/10.1016/0021-9991(88)90177-5)",
                         "Built from the definition; the SSP form converted to a Butcher table."),
    "Heun 3": ("K. Heun, *Z. Math. Phys.* 45 (1900) 23-38", "Built from the method's definition."),
    "Kutta 3": ("W. Kutta, Beitrag zur näherungsweisen Integration totaler Differentialgleichungen, *Z. Math. Phys.* 46 (1901) "
                "435-453", "Built from the method's definition."),
    "RK4 classical": ("W. Kutta, *Z. Math. Phys.* 46 (1901) 435-453", "Built from the method's definition."),
    "3/8 rule": ("W. Kutta, *Z. Math. Phys.* 46 (1901) 435-453", "Built from the method's definition."),
    "SSPRK33": ("C.-W. Shu and S. Osher, Efficient implementation of essentially non-oscillatory shock-capturing schemes, "
                "*J. Comput. Phys.* 77 (1988) 439-471, [doi:10.1016/0021-9991(88)90177-5](https://doi.org/10.1016/0021-9991(88)90177-5)",
                "The Shu-Osher form converted to a Butcher table."),
    "Gill": ("S. Gill, A process for the step-by-step integration of differential equations in an automatic digital computing "
             "machine, *Proc. Camb. Phil. Soc.* 47 (1951) 96-108, [doi:10.1017/S0305004100026414](https://doi.org/10.1017/S0305004100026414)",
             "Gill's choice of the free parameter (sqrt 2) in the 4-stage family with c = (0, 1/2, 1/2, 1)."),
    "Gauss": ("J. C. Butcher, Implicit Runge-Kutta processes, *Math. Comp.* 18 (1964) 50-64, "
              "[doi:10.1090/S0025-5718-1964-0159424-9](https://doi.org/10.1090/S0025-5718-1964-0159424-9)", DEF),
    "RadauIIA": ("B. L. Ehle, On Padé approximations to the exponential function and A-stable methods for the numerical "
                 "solution of initial value problems, Research Report CSRR 2010, University of Waterloo (1969)", DEF),
    "LobattoIIIA": ("B. L. Ehle, Research Report CSRR 2010, University of Waterloo (1969)", DEF),
    "LobattoIIIC": ("F. H. Chipman, A-stable Runge-Kutta processes, *BIT* 11 (1971) 384-388, "
                    "[doi:10.1007/BF01939406](https://doi.org/10.1007/BF01939406)",
                    "Lobatto nodes and weights, a_i1 = b_1, and the simplifying condition C(s-1), as in " + HW2 + "."),
    "Ralston": ("A. Ralston, Runge-Kutta methods with minimum error bounds, *Math. Comp.* 16 (1962) 431-437, "
                "[doi:10.1090/S0025-5718-1962-0150954-0](https://doi.org/10.1090/S0025-5718-1962-0150954-0)",
                "The paper's minimum-error-bound nodes; the remaining coefficients follow from the order conditions. "
                "The paper itself was read page by page."),
    "SSPRK(10,4)": ("D. I. Ketcheson, Highly efficient strong stability-preserving Runge-Kutta methods with low-storage "
                    "implementations, *SIAM J. Sci. Comput.* 30 (2008) 2113-2136, "
                    "[doi:10.1137/07070485X](https://doi.org/10.1137/07070485X)",
                    "The paper's low-storage algorithm (Sect. 6.1), converted to a Butcher table stage by stage."),
    "SSPRK(4,3)": ("J. F. B. M. Kraaijevanger, Contractivity of Runge-Kutta methods, *BIT* 31 (1991) 482-528, "
                   "[doi:10.1007/BF01933264](https://doi.org/10.1007/BF01933264)",
                   "The optimal 4-stage method written as four forward-Euler steps (as in Ketcheson 2008), converted to a Butcher table."),
    "DOPRI5": ("J. R. Dormand and P. J. Prince, A family of embedded Runge-Kutta formulae, *J. Comput. Appl. Math.* 6 (1980) "
               "19-26, [doi:10.1016/0771-050X(80)90013-3](https://doi.org/10.1016/0771-050X(80)90013-3)",
               "Compared with the table in E. Hairer's own `dopri5.f` (the authors' code)."),
    "Fehlberg 1969": ("E. Fehlberg, Low-order classical Runge-Kutta formulas with stepsize control and their application to some "
                      "heat transfer problems, NASA TR R-315 (1969), Table III, "
                      "[ntrs.nasa.gov/citations/19690021375](https://ntrs.nasa.gov/citations/19690021375)",
                      "Transcribed from Table III (formula 2, p. 13) and checked against the order conditions before use. "
                      "Fehlberg's c is the 4th-order weight vector and c-hat the 5th; libraries propagate either one, and both count as a match."),
    "Fehlberg 1968": ("E. Fehlberg, Classical fifth-, sixth-, seventh-, and eighth-order Runge-Kutta formulas with stepsize "
                      "control, NASA TR R-287 (1968), Table X, "
                      "[ntrs.nasa.gov/citations/19680027281](https://ntrs.nasa.gov/citations/19680027281)",
                      "Transcribed from Table X (RK7(8), p. 65) and checked against the order conditions before use. "
                      "Libraries propagate the 7th- or the 8th-order weights; both count as a match."),
    "Tsitouras 5(4)": ("Ch. Tsitouras, Runge-Kutta pairs of order 5(4) satisfying only the first column simplifying "
                       "assumption, *Comput. Math. Appl.* 62 (2011) 770-775, "
                       "[doi:10.1016/j.camwa.2011.06.002](https://doi.org/10.1016/j.camwa.2011.06.002); "
                       "[preprint, archived 2012](https://web.archive.org/web/20121114221354/http://users.ntua.gr:80/tsitoura/RK54_new_v2.pdf)",
                       "Compared with Table 1 of the preprint (16 significant digits), with a_i1 = c_i - sum_j a_ij as the paper states. "
                       "The preprint prints the error weight b-hat_7 with the wrong sign ([ERRATA.md](ERRATA.md)); every library has it right."),
    "Verner": (VERNER, "Compared with the coefficient file of the same stage count and nodes, entry by entry."),
    "Feagin": (FEAGIN, "Compared with Feagin's 60-digit file of the same stage count, entry by entry."),
}


SHORT = {"Euler": "Euler (1768)", "explicit midpoint": "Runge (1895)", "Heun 2 / SSPRK22": "Heun (1900)",
         "Heun 3": "Heun (1900)", "Kutta 3": "Kutta (1901)", "RK4 classical": "Kutta (1901)", "3/8 rule": "Kutta (1901)",
         "SSPRK33": "Shu and Osher (1988)", "Gill": "Gill (1951)", "Gauss": "Butcher (1964)", "RadauIIA": "Ehle (1969)",
         "LobattoIIIA": "Ehle (1969)", "LobattoIIIC": "Chipman (1971)", "Ralston": "Ralston (1962)",
         "SSPRK(10,4)": "Ketcheson (2008)", "SSPRK(4,3)": "Kraaijevanger (1991)", "DOPRI5": "Dormand and Prince (1980)",
         "Fehlberg 1969": "Fehlberg (1969)", "Fehlberg 1968": "Fehlberg (1968)", "Tsitouras 5(4)": "Tsitouras (2011)",
         "Verner": "Verner's files", "Feagin": "Feagin's files"}


def ref_of(key):
    if key.startswith("Verner file"):
        return "Verner", key.removeprefix("Verner file ")
    if key.startswith("Feagin file"):
        return "Feagin", None
    for k in REFS:
        if key == k or key.startswith(k):
            return k, None
    return key, None


def frac(s):
    return str(s)  # never shortened: the tableau must be copyable


def tableau(co):
    A, b, c, bh = co["A"], co["b"], co.get("c"), co.get("bhat")
    s = len(b)
    c = c or ["?"] * s
    rows = [[frac(c[i])] + [frac(A[i][j]) if j < len(A[i]) else "0" for j in range(s)] for i in range(s)]
    rows.append([""] + [frac(x) for x in b])
    if bh:
        rows.append(["(embedded)"] + [frac(x) for x in bh])
    w = [max(len(r[k]) for r in rows) for k in range(s + 1)]
    out = []
    for i, r in enumerate(rows):
        if i == s:
            out.append("-" * (w[0] + 1) + "+" + "-" * (sum(w[1:]) + 2 * s))
        out.append(r[0].rjust(w[0]) + " | " + "  ".join(x.rjust(w[k + 1]) for k, x in enumerate(r[1:])))
    return "\n".join(out)


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


# gather per display name: every copy, which reference it was compared with, and the result
cards = defaultdict(lambda: {"order": None, "stages": None, "groups": [], "refs": defaultdict(list), "unchecked": 0,
                             "differ": []})
for m in methods:
    if not any(x for x in (m["first_source"] or [])):
        continue
    cd = cards[m["name"]]
    cd["order"], cd["stages"] = m["order"], m["stages"]
    cd["groups"].append(m)
for m in methods:  # copies with the same display name in groups without a source match, e.g. a reported defect
    if m["name"] in cards and m not in cards[m["name"]]["groups"]:
        cards[m["name"]]["groups"].append(m)
for name, cd in cards.items():
    for m in cd["groups"]:
        for tid in m["table_ids"]:
            t = tables[tid]
            fs = t["first_source"] or []
            if not fs:
                cd["unchecked"] += 1
            for x in fs:
                (cd["refs"][x["reference"]] if x["agrees"] else cd["differ"]).append((t, x))

out = ["# First published sources\n",
       "Each card is one method that was compared with its first published source: the paper or report, the author's own "
       "coefficient file or code, or a construction from the definition in a standard text. A card says how the "
       "comparison was made, how many library copies were compared and how closely they agree, which copies differ, "
       "and gives the tableau. *Largest difference* is the largest absolute difference between a library copy and the "
       "reference over A, b, c and the embedded weights; values near 1e-15 come from printed decimals, values near "
       "1e-50 from 50-digit arithmetic.\n",
       "Generated by `scripts/render_sources.py` from `data/`; do not edit by hand.\n",
       "## Summary\n",
       "| Method | Order | Stages | Reference | Copies compared | Agree | Largest difference |",
       "|---|---|---|---|---|---|---|"]
body = []
order = sorted(cards.items(), key=lambda kv: (kv[1]["order"] or 0, kv[1]["stages"] or 0, kv[0].lower()))
for name, cd in order:
    n_ok = sum(len(v) for v in cd["refs"].values())
    n_bad = len(cd["differ"])
    dmax = max((x["largest_difference"] or 0) for v in cd["refs"].values() for _, x in v) if n_ok else 0
    keys = sorted({ref_of(k)[0] for k in cd["refs"]})
    short = "; ".join(SHORT[k] for k in keys if k in SHORT)
    out.append(f"| [{name}](#{slug(name)}) | {cd['order']} | {cd['stages']} | {short} | {n_ok + n_bad} | "
               f"{n_ok}{'' if not n_bad else f' ({n_bad} differ)'} | {dmax:.0e} |".replace("0e+00", "0"))

    body.append(f"\n## {name}\n")
    body.append(f"Order {cd['order']}, {cd['stages']} stages.\n")
    for k in keys:
        if k in REFS:
            body.append(f"- **Reference:** {REFS[k][0]}")
            body.append(f"- **How compared:** {REFS[k][1]}")
    files = sorted({ref_of(k)[1] for k in cd["refs"] if ref_of(k)[1]})
    if files:
        body.append("- **Files:** " + ", ".join(f"`{f}`" for f in files))
    copies = sorted({(t["library"], str(t["method"])) for v in cd["refs"].values() for t, _ in v})
    body.append(f"- **Library copies that agree ({n_ok}, largest difference {dmax:.1e}):** "
                + "; ".join(f"{lib} `{meth}`" for lib, meth in copies))
    if n_bad:
        body.append("- **Copies that differ:** " + "; ".join(
            f"{t['library']} `{t['method']}` (largest difference {x['largest_difference']:.2g}; "
            f"{'confirmed by the maintainers, ' if (t.get('review') or {}).get('confirmed_at') else ''}see [ERRATA.md](ERRATA.md))"
            for t, x in cd["differ"]))
    if cd["unchecked"]:
        body.append(f"- **Not compared individually:** {cd['unchecked']} further copies with the same coefficients "
                    "(same group in `data/methods.jsonl`).")
    agreeing = [m for m in cd["groups"] if m["first_source"]] or cd["groups"]
    best = next((m for m in agreeing if m["exact"]), None) or \
        max(agreeing, key=lambda m: sum(len(str(x)) for row in m["coefficients"]["A"] for x in row))  # most digits
    if best["stages"] <= 7:
        body.append(f"\nTableau ({'exact' if best['exact'] else 'as printed in ' + tables[best['table_ids'][0]]['library']}; "
                    f"c | A, then b{', then the embedded weights' if best['coefficients'].get('bhat') else ''}):\n")
        body.append("```text\n" + tableau(best["coefficients"]) + "\n```")
    else:
        body.append(f"\nThe tableau ({best['stages']} stages) is in `data/methods.jsonl` "
                    f"(table ids {', '.join(best['table_ids'][:3])}).")

(ROOT / "SOURCES.md").write_text("\n".join(out + body) + "\n", encoding="utf-8", newline="\n")
print(f"wrote SOURCES.md: {len(cards)} methods")
