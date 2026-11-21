"""One worked example of how a record in data/tables.jsonl was made: SciPy's RK45, read from the installed library.

The census read each library at a pinned version. Here SciPy's Dormand-Prince table is read the same way
(imported, not copied by hand), compared entry by entry with record b0aa23deaf18, and checked with physverify.
The record was made from SciPy 1.18.1; another version may differ if SciPy changed the table.

    pip install -r requirements.txt scipy
    python scripts/example_source_to_record.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import scipy
from physverify.butcher import check_tableau
from scipy.integrate._ivp.rk import RK45

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from verify import floats  # noqa: E402

rec = next(json.loads(l) for l in open(ROOT / "data/tables.jsonl", encoding="utf-8")
           if json.loads(l)["id"] == "b0aa23deaf18")
co = rec["coefficients_as_printed"]

# 1. read the table from the library: SciPy stores A (s x s), B (weights), C (nodes) and E (b - embedded, FSAL stage)
A_lib, b_lib, c_lib = np.array(RK45.A), np.array(RK45.B), np.array(RK45.C)
A_lib = np.pad(A_lib, ((0, 0), (0, len(b_lib) - A_lib.shape[1])))  # SciPy stores A with s - 1 columns
print(f"SciPy {scipy.__version__}; record read from SciPy {rec['version']}, {rec['file']}, line {rec['line']}")

# 2. compare with the record
A_rec = np.array(floats(co["A"]), dtype=float)
A_rec = np.pad(A_rec, ((0, 0), (0, len(b_lib) - A_rec.shape[1])))
diff = max(np.abs(A_lib - A_rec[:len(b_lib), :len(b_lib)]).max(), np.abs(b_lib - np.array(floats(co["b"]))).max(),
           np.abs(c_lib - np.array(floats(co["c"]))).max())
print(f"largest difference between the installed table and the record: {diff:.1e}")

# 3. check the claim the library makes (order 5) from the coefficients alone
res = check_tableau(A_lib, b_lib, c_lib, claimed=RK45.order)
print(f"physverify: {res.status}: {res.message}")
print(f"recorded verdict: {rec['verdict']['status']}, order {rec['verdict']['computed_order']}")
