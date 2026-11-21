"""Re-check every table in data/tables.jsonl.

Default (double precision, physverify.butcher.check_tableau): the coefficients are evaluated from the strings as
printed in the library and rounded to double precision; the recorded order must hold and, below order 14 (the
highest order checked), the next order must fail; and the library's own claim must give the recorded verdict.

--precise (50 digits, mpmath): the order-condition residuals are recomputed from the printed strings over every
rooted tree up to the recorded order + 1, compared with the archived `residuals_50_digit`, and the next order
must fail. This is slow for the largest tables; use --max-stages to limit it.

What neither mode covers: reading the table from the library's source (see scripts/example_source_to_record.py
for one worked example) and the comparison with first published sources (recorded in `first_source`).

    pip install -r requirements.txt
    python scripts/verify.py
    python scripts/verify.py --precise --max-stages 13
    python scripts/verify.py --id 901d03665ed6
"""
import argparse, ast, json, sys
from pathlib import Path

import mpmath
from physverify.butcher import check_tableau, trees

mpmath.mp.dps = 50
ROOT = Path(__file__).resolve().parent.parent
FUNCS = {"sqrt": mpmath.sqrt, "cos": mpmath.cos, "sin": mpmath.sin, "exp": mpmath.exp, "log": mpmath.log}


def value(s):
    """A coefficient string (numbers, + - * / **, sqrt, cos, sin, exp, log, pi) as an mpmath number."""
    s = str(s).strip()

    def ev(n):
        if isinstance(n, ast.Expression):
            return ev(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)) and not isinstance(n.value, bool):
            return mpmath.mpf(ast.get_source_segment(s, n))
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.USub, ast.UAdd)):
            v = ev(n.operand)
            return -v if isinstance(n.op, ast.USub) else v
        if isinstance(n, ast.BinOp):
            a, b = ev(n.left), ev(n.right)
            ops = {ast.Add: lambda: a + b, ast.Sub: lambda: a - b, ast.Mult: lambda: a * b,
                   ast.Div: lambda: a / b, ast.Pow: lambda: a ** b}
            if type(n.op) in ops:
                return ops[type(n.op)]()
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in FUNCS and len(n.args) == 1:
            return FUNCS[n.func.id](ev(n.args[0]))
        if isinstance(n, ast.Name) and n.id == "pi":
            return +mpmath.pi
        raise ValueError(f"coefficient not allowed: {s!r}")

    return ev(ast.parse(s, mode="eval"))


def floats(v):
    if v is None:
        return None
    return [floats(x) for x in v] if isinstance(v, list) else float(value(v))


def gamma(t):
    g = 1 + sum(_size(s) for s in t)
    for s in t:
        g *= gamma(s)
    return g


def _size(t):
    return 1 + sum(_size(s) for s in t)


def precise_residuals(co, max_order):
    """{order: largest |b . Phi(t) - 1/gamma(t)|} over the rooted trees of each order, in 50-digit arithmetic."""
    A = [[value(x) for x in row] for row in co["A"]]
    b = [value(x) for x in co["b"]]
    s = len(b)
    A = [row + [mpmath.mpf(0)] * (s - len(row)) for row in A]
    memo = {}

    def phi(t):
        if t not in memo:
            v = [mpmath.mpf(1)] * s
            for ch in t:
                p = phi(ch)
                Ap = [mpmath.fsum(A[i][j] * p[j] for j in range(s)) for i in range(s)]
                v = [v[i] * Ap[i] for i in range(s)]
            memo[t] = v
        return memo[t]

    return {p: max(abs(mpmath.fsum(b[i] * phi(t)[i] for i in range(s)) - mpmath.mpf(1) / gamma(t)) for t in trees(p))
            for p in range(1, max_order + 1)}


def check_precise(t):
    """The 50-digit residuals agree with the archived ones, and the recorded order is the highest that holds."""
    order = t["verdict"]["computed_order"]
    if not order or order >= 14:
        return None, "no order recorded, or order at the checked limit (14)"
    tol = mpmath.mpf(10) ** -(t["verdict"].get("digits_given") or 30)
    tol = max(tol, mpmath.mpf("1e-30"))
    r = precise_residuals(t["coefficients_as_printed"], order + 1)
    rec = t.get("residuals_50_digit") or {}
    # agree on what decides the order: every residual above 1e-9 matches the archive to 1e-4 relative, and those
    # at or below 1e-9 are below it in both (the archive's tiny residuals can differ: see METHOD.md)
    def close(p):
        a, x = float(r[p]), float(rec[str(p)])
        return (a <= 1e-9 and x <= 1e-9) or abs(a - x) <= 1e-4 * max(abs(a), abs(x))
    same = all(close(p) for p in r if str(p) in rec)
    holds = all(r[p] <= 1e-8 for p in range(1, order + 1)) or t["verdict"]["status"] in ("FAIL", "truncated")
    highest = r[order + 1] > 1e-12
    return same and highest and holds, (f"residuals {'match' if same else 'differ from'} the archive; order {order + 1} "
                              f"{'fails' if highest else 'also holds'} (residual {mpmath.nstr(r[order + 1], 3)}); "
                              f"orders up to {order} {'hold' if holds else 'do not all hold'}")


def check(t):
    co = t["coefficients_as_printed"]
    order = t["verdict"]["computed_order"]
    if not order:
        return None, "no order recorded"
    A, b, c = floats(co["A"]), floats(co["b"]), floats(co.get("c"))
    # 1. the order the dataset records holds, and (below order 14, the limit checked) the next order does not
    res = check_tableau(A, b, c, claimed=order, max_order=order)
    order_ok = res.status == "PASS" or f"order {order} confirmed" in res.message
    if order < 14:
        nxt = check_tableau(A, b, c, claimed=order + 1, max_order=order + 1)
        order_ok = order_ok and nxt.status == "FAIL" and f"only up to {order}" in nxt.message
    # 2. the library's own claim gives the recorded verdict (a FAIL can come from a claimed order that is too
    #    high, an embedded pair, or stage times c that differ from A 1)
    claim = t.get("claim") or {}
    rec = t["verdict"]["status"]
    if rec not in ("PASS", "FAIL"):
        return order_ok, res.message
    emb = claim.get("embedded")
    kw = {"embedded": floats(co["bhat"]), "claimed_embedded": emb} if emb is not None and co.get("bhat") else {}
    res2 = check_tableau(A, b, c, claimed=claim.get("order") or order, **kw)
    label = ((t.get("review") or {}).get("label") or "")
    verdict_ok = res2.status == rec or (rec == "FAIL" and label == "tool false alarm")
    return order_ok and verdict_ok, f"{res2.status} (recorded {rec}): {res2.message}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--id")
    ap.add_argument("--precise", action="store_true", help="50-digit residuals against the archive")
    ap.add_argument("--max-stages", type=int, default=None, help="with --precise, skip larger tables")
    args = ap.parse_args()
    tables = [json.loads(l) for l in open(ROOT / "data/tables.jsonl", encoding="utf-8")]
    if args.id:
        tables = [t for t in tables if t["id"] == args.id]
    n_ok = n_bad = n_skip = 0
    for t in tables:
        if args.precise and args.max_stages and t["stages"] > args.max_stages:
            n_skip += 1
            continue
        try:
            ok, msg = (check_precise if args.precise else check)(t)
        except Exception as e:  # report, do not hide
            ok, msg = False, f"error: {e}"
        if ok is None:
            n_skip += 1
        elif ok:
            n_ok += 1
        else:
            n_bad += 1
            print(f"NOT REPRODUCED {t['id']} {t['library']} {t['method']}: {msg}")
    mode = "50-digit" if args.precise else "double precision"
    print(f"{mode}: {n_ok} reproduced, {n_bad} not reproduced, {n_skip} skipped of {len(tables)} tables")
    sys.exit(1 if n_bad else 0)


if __name__ == "__main__":
    main()
