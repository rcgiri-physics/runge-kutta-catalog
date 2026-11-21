"""Use a table from the catalogue, and see why the stage times matter.

1. Five methods from START_HERE.md solve y' = y cos t, y(0) = 1 (exact solution exp(sin t)) with fixed steps, and
   physverify checks that the error falls at each method's order. Because f depends on t, a wrong stage time
   would show here; it would not show on y' = lambda y.
2. The Feagin 12 table as archived from OrdinaryDiffEq.jl (node c2 = 2 instead of 0.2, confirmed and fixed
   upstream) solves y' = t, y(0) = 0, whose exact value at t = 1 is 1/2. Halving the step halves the error:
   first order. With c2 = 0.2 the error drops to round-off.

    pip install -r requirements.txt
    python examples/convergence.py
"""
import json
import sys
from pathlib import Path

import numpy as np
from physverify import check_order

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from verify import floats  # noqa: E402  (evaluates the coefficient strings as printed)

TABLES = {json.loads(l)["id"]: json.loads(l) for l in open(ROOT / "data/tables.jsonl", encoding="utf-8")}


def table(tid):
    co = TABLES[tid]["coefficients_as_printed"]
    A, b = np.array(floats(co["A"]), dtype=float), np.array(floats(co["b"]), dtype=float)
    s = len(b)
    A = np.pad(A, ((0, 0), (0, s - A.shape[1])))
    c = np.array(floats(co["c"]), dtype=float) if co.get("c") else A.sum(axis=1)
    return A, b, c


def solve_linear(A, b, c, a, g, t_end, n):
    """Fixed-step Runge-Kutta for y' = a(t) y + g(t); the stage equations are linear, so explicit and implicit
    tables are handled alike: (I - h diag(a(t + c h)) A) K = a(t + c h) y + g(t + c h)."""
    h, y, t = t_end / n, 1.0 if g is None else 0.0, 0.0
    for _ in range(n):
        ts = t + c * h
        at = a(ts)
        gt = np.zeros_like(ts) if g is None else g(ts)
        K = np.linalg.solve(np.eye(len(b)) - h * at[:, None] * A, at * y + gt)
        y, t = y + h * b @ K, t + h
    return y


start = json.load(open(ROOT / "data/start_here.json", encoding="utf-8"))  # written by scripts/render_start.py

print("1. y' = y cos t, y(0) = 1, exact y(2) = exp(sin 2)")
for card in start:
    A, b, c = table(card["table_id"])
    ns = [8, 16, 32, 64] if card["order"] <= 4 else [4, 8, 16, 32]
    errs = [abs(solve_linear(A, b, c, np.cos, None, 2.0, n) - np.exp(np.sin(2.0))) for n in ns]
    res = check_order([2.0 / n for n in ns], errs, expected=card["order"])
    print(f"   {card['name']:<24} {res.status:<5} {res.message}")

print("\n2. y' = t, y(0) = 0, exact y(1) = 1/2, with the archived Feagin 12 table (c2 = 2)")
fid = next(t["id"] for t in TABLES.values() if t["library"] == "OrdinaryDiffEq.jl" and t["method"] == "Feagin12"
           and (t.get("review") or {}).get("confirmed_at"))
A, b, c = table(fid)
zero = lambda ts: np.zeros_like(ts)  # noqa: E731
for label, cc in (("as archived, c2 = 2  ", c), ("corrected, c2 = 0.2  ", np.where(np.isclose(c, 2.0), 0.2, c))):
    errs = [abs(solve_linear(A, b, cc, zero, lambda ts: ts, 1.0, n) - 0.5) for n in (4, 8, 16)]
    print(f"   {label} errors at 4, 8, 16 steps: " + ", ".join(f"{e:.1e}" for e in errs))
