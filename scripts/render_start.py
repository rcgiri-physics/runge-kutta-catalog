"""Write START_HERE.md and data/start_here.json: five method cards generated from data/ (no coefficient typed by
hand). Each card uses the library copy that was compared with the method's first published source, exact where
possible, else the copy with the most digits.  python scripts/render_start.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
methods = [json.loads(l) for l in open(ROOT / "data/methods.jsonl", encoding="utf-8")]
tables = {t["id"]: t for t in (json.loads(l) for l in open(ROOT / "data/tables.jsonl", encoding="utf-8"))}

CARDS = [
    ("Classical RK4 (Kutta 1901)", "Classical RK4 (Kutta 1901)",
     "Fixed-step integration of non-stiff problems when simplicity matters more than efficiency. It has no error "
     "estimate, so the step size is yours to choose and check.",
     "W. Kutta, *Z. Math. Phys.* 46 (1901) 435-453."),
    ("Dormand-Prince 5(4)", "Dormand-Prince 5(4)",
     "Adaptive steps for non-stiff problems at moderate tolerances. It is the pair behind SciPy's `RK45` and "
     "MATLAB's `ode45`; the 5th-order solution is propagated and the 4th-order one estimates the error.",
     "J. R. Dormand and P. J. Prince, *J. Comput. Appl. Math.* 6 (1980) 19-26, "
     "[doi:10.1016/0771-050X(80)90013-3](https://doi.org/10.1016/0771-050X(80)90013-3)."),
    ("Tsitouras 5(4)", "Tsitouras 5(4)",
     "An alternative adaptive 5(4) pair for non-stiff problems, built with only the first-column simplifying "
     "assumption; `Tsit5` in Julia's OrdinaryDiffEq.jl. The coefficients are decimals, given here with all printed digits.",
     "Ch. Tsitouras, *Comput. Math. Appl.* 62 (2011) 770-775, "
     "[doi:10.1016/j.camwa.2011.06.002](https://doi.org/10.1016/j.camwa.2011.06.002). Note the erratum on the "
     "preprint's error weights in [ERRATA.md](ERRATA.md)."),
    ("SSPRK(3,3)", "SSPRK(3,3)",
     "Method-of-lines time stepping for hyperbolic PDEs with a TVD or limited spatial discretisation: it keeps the "
     "strong-stability property of forward Euler under the same step-size limit (SSP coefficient 1).",
     "C.-W. Shu and S. Osher, *J. Comput. Phys.* 77 (1988) 439-471, "
     "[doi:10.1016/0021-9991(88)90177-5](https://doi.org/10.1016/0021-9991(88)90177-5)."),
    ("Radau IIA, 3 stages", "Radau IIA, 3 stages",
     "Stiff problems and index-1 DAEs: implicit, L-stable, order 5, stage order 3. It is the method in Hairer and "
     "Wanner's `radau5` code. Each step solves a nonlinear system of 3 stages.",
     "B. L. Ehle, Research Report CSRR 2010, University of Waterloo (1969); construction as in Hairer and Wanner, "
     "*Solving Ordinary Differential Equations II*, Sect. IV.5."),
]


def slug(s):
    import re
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def pick(name):
    groups = [m for m in methods if m["name"] == name and m["first_source"]]
    exact = [m for m in groups if m["exact"]]
    best = exact[0] if exact else max(groups, key=lambda m: sum(len(str(x)) for r in m["coefficients"]["A"] for x in r))
    tid = next(i for i in best["table_ids"] if any(x["agrees"] for x in tables[i]["first_source"] or []))
    return best, tables[tid]


def py(v):
    return "[" + ", ".join(py(x) if isinstance(x, list) else ("'" + str(x) + "'") for x in v) + "]"


out = ["# Start here\n",
       "Five widely used methods, each with its tableau, its first published source and when you would reach for it. "
       "Every tableau below is generated from `data/` (by `scripts/render_start.py`): it is the library copy that was "
       "compared with the method's source, exact where the library stores exact values. Strings like '1/6' are exact "
       "rationals; evaluate them in your own precision. `examples/convergence.py` runs all five on y' = y cos t.\n"]
cards = []
for title, name, when, ref in CARDS:
    m, t = pick(name)
    co = m["coefficients"]
    cards.append({"name": title, "table_id": t["id"], "order": m["order"]})
    agreeing = sum(1 for tid in m["table_ids"] if any(x["agrees"] for x in tables[tid]["first_source"] or []))
    out.append(f"\n## {title}\n")
    out.append(f"Order {m['order']}, {m['stages']} stages{', explicit' if not m['implicit'] else ', implicit'}"
               f"{', stage order ' + str(m['stage_order']) if m['implicit'] else ''}.\n")
    out.append(f"**When to use it.** {when}\n")
    out.append(f"**Source.** {ref} Compared copies: see [SOURCES.md](SOURCES.md#{slug(name)}).\n")
    out.append(f"**Tableau** ({'exact' if m['exact'] else 'decimals as printed'}; from {t['library']} `{t['method']}`, "
               f"one of {agreeing} copies in this group that match the source):\n")
    out.append("```python\n" + f"c = {py(co['c'])}\nA = {py(co['A'])}\nb = {py(co['b'])}"
               + (f"\nb_embedded = {py(co['bhat'])}" if co.get("bhat") else "") + "\n```")
    out.append("Check it yourself: `physverify.butcher.check_tableau(A, b, c, claimed="
               f"{m['order']})` after converting the strings to numbers.")

(ROOT / "START_HERE.md").write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
json.dump(cards, open(ROOT / "data/start_here.json", "w", encoding="utf-8", newline="\n"), indent=1)
print("wrote START_HERE.md and data/start_here.json")
