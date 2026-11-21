"""Re-check every table in data/rosenbrock.jsonl with physverify.

For each Rosenbrock table (standard form: (I - h gamma_ii J) k_i = h f(y + sum_j alpha_ij k_j) + h J sum_{j<i}
gamma_ij k_j, y1 = y + sum b_i k_i), the order with the exact Jacobian, the order as a W-method (any matrix in
place of J), and the embedded order are recomputed with physverify.butcher.rosenbrock_residuals and compared with
the record. Each recorded order must hold and, below 6 (the highest order checked), the next one must fail.

    pip install -r requirements.txt
    python scripts/verify_rosenbrock.py
"""
import json
import sys
from pathlib import Path

from physverify.butcher import rosenbrock_residuals

ROOT = Path(__file__).resolve().parent.parent
TOL, CAP = 1e-8, 6


def order(al, G, w, wm=False):
    r = rosenbrock_residuals(al, G, w, CAP, w_method=wm)
    p = 0
    while p < CAP and r[p + 1] <= TOL:
        p += 1
    return p


bad = 0
rows = [json.loads(l) for l in open(ROOT / "data/rosenbrock.jsonl", encoding="utf-8")]
for t in rows:
    got = {"order_exact_jacobian": order(t["alpha"], t["gamma"], t["b"]),
           "order_w_method": order(t["alpha"], t["gamma"], t["b"], True),
           "embedded_order": None if t["embedded"] is None else order(t["alpha"], t["gamma"], t["embedded"])}
    diff = {k: (t[k], v) for k, v in got.items() if t[k] != v}
    if t["claim"] and t["claim"].get("order") is not None and got["order_exact_jacobian"] < t["claim"]["order"]:
        diff["claim"] = (t["claim"]["order"], got["order_exact_jacobian"])
    if diff:
        bad += 1
        print(f"NOT REPRODUCED {t['id']} {t['library']} {t['method']}: {diff}")
print(f"{len(rows) - bad} reproduced, {bad} not reproduced of {len(rows)} Rosenbrock tables")
sys.exit(1 if bad else 0)
