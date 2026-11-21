"""Re-check every table in data/tables.jsonl with physverify.

For each table, the coefficients are evaluated from the strings as printed in the library (50 digits with
mpmath, then rounded to double precision), and physverify.butcher.check_tableau is asked whether the order
recorded in the dataset holds. A table whose recorded order is confirmed counts as reproduced.

    pip install physverify mpmath
    python scripts/verify.py            # all tables
    python scripts/verify.py --id 901d03665ed6
"""
import argparse, ast, json, sys
from pathlib import Path

import mpmath
from physverify.butcher import check_tableau

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


def check(t):
    co = t["coefficients_as_printed"]
    order = t["verdict"]["computed_order"]
    if not order:
        return None, "no order recorded"
    A, b, c = floats(co["A"]), floats(co["b"]), floats(co.get("c"))
    # 1. the order the dataset records holds
    res = check_tableau(A, b, c, claimed=order, max_order=order)
    order_ok = res.status == "PASS" or f"order {order} confirmed" in res.message
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
    args = ap.parse_args()
    tables = [json.loads(l) for l in open(ROOT / "data/tables.jsonl", encoding="utf-8")]
    if args.id:
        tables = [t for t in tables if t["id"] == args.id]
    n_ok = n_bad = n_skip = 0
    for t in tables:
        try:
            ok, msg = check(t)
        except Exception as e:  # report, do not hide
            ok, msg = False, f"error: {e}"
        if ok is None:
            n_skip += 1
        elif ok:
            n_ok += 1
        else:
            n_bad += 1
            print(f"NOT REPRODUCED {t['id']} {t['library']} {t['method']}: {msg}")
    print(f"{n_ok} reproduced, {n_bad} not reproduced, {n_skip} skipped (no order recorded) of {len(tables)} tables")
    sys.exit(1 if n_bad else 0)


if __name__ == "__main__":
    main()
