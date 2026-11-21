"""First published sources for Rosenbrock methods, transcribed from the papers, and their comparison with the
library copies in data/rosenbrock.jsonl. Used by render_rosenbrock.py; run on its own to print the comparisons:

    python scripts/rosenbrock_sources.py

Every source is given in the standard form of data/rosenbrock.jsonl (alpha strictly lower triangular, gamma lower
triangular with the diagonal, b, embedded), with 50-digit arithmetic, plus the stage times alpha_i = sum_j alpha_ij
and the weights of the time derivative gamma_i = sum_j gamma_ij where the paper states them. Where a paper also
prints a table, the transcription is checked against it first.
"""
import json
from pathlib import Path

import mpmath

mpmath.mp.dps = 50
ROOT = Path(__file__).resolve().parent.parent
M = mpmath.mpf


def transformed(alpha, gamma, b, emb):
    """Hairer's transformed form: A = alpha Gamma^-1, C = diag(1/gamma_ii) - Gamma^-1, m = b Gamma^-1."""
    s = len(b)
    G = mpmath.matrix(gamma)
    Gi = G ** -1
    A = mpmath.matrix(alpha) * Gi
    C = mpmath.diag([1 / G[i, i] for i in range(s)]) - Gi
    m = (mpmath.matrix([b]) * Gi)
    mh = (mpmath.matrix([emb]) * Gi)
    return A, C, m, mh


def ros3p():
    """J. Lang and J. Verwer, ROS3P - an accurate third-order Rosenbrock solver designed for parabolic problems,
    BIT 41 (2001) 731-738, Sect. 5 (p. 734-735) and Table 5.1 (p. 735)."""
    g = M(1) / 2 + mpmath.sqrt(3) / 6          # gamma_+ = 1/2 + sqrt(3)/6, p. 734
    alpha = [[0, 0, 0], [1, 0, 0], [1, 0, 0]]   # alpha21 = alpha31 = 1, alpha32 = 0, p. 734
    gamma = [[g, 0, 0], [-1, g, 0], [-g, M(1) / 2 - 2 * g, g]]  # gamma21 = -1 (p. 734); gamma31 = -g, gamma32 = 1/2 - 2g (p. 735)
    b = [M(2) / 3, 0, M(1) / 3]                 # b = (2/3, 0, 1/3), p. 735
    emb = [M(1) / 3, M(1) / 3, M(1) / 3]        # b-hat = (1/3, 1/3, 1/3), p. 735
    times = [0, 1, 1]                           # alpha_i, Table 5.1
    tweights = [g, g - 1, M(1) / 2 - 2 * g]     # gamma_i = sum_j gamma_ij, Table 5.1
    table51 = {  # Table 5.1 as printed (transformed form), to check the transcription above
        "a21": "1.267949192431123e+00", "a31": "1.267949192431123e+00", "a32": "0.000000000000000e+00",
        "c21": "-1.607695154586736e+00", "c31": "-3.464101615137755e+00", "c32": "-1.732050807568877e+00",
        "m1": "2.000000000000000e+00", "m2": "5.773502691896258e-01", "m3": "4.226497308103742e-01",
        "mh1": "2.113248654051871e+00", "mh2": "1.000000000000000e+00", "mh3": "4.226497308103742e-01",
        "gamma": "7.886751345948129e-01", "gamma2": "-2.113248654051871e-01", "gamma3": "-1.077350269189626e+00",
    }
    A, C, m, mh = transformed(alpha, gamma, b, emb)
    ours = {"a21": A[1, 0], "a31": A[2, 0], "a32": A[2, 1], "c21": C[1, 0], "c31": C[2, 0], "c32": C[2, 1],
            "m1": m[0], "m2": m[1], "m3": m[2], "mh1": mh[0], "mh2": mh[1], "mh3": mh[2],
            "gamma": g, "gamma2": tweights[1], "gamma3": tweights[2]}
    printed_check = max(abs(ours[k] - M(v)) for k, v in table51.items())
    return {
        "name": "ROS3P",
        "reference": "J. Lang and J. Verwer, ROS3P - an accurate third-order Rosenbrock solver designed for parabolic "
                     "problems, *BIT* 41 (2001) 731-738, [doi:10.1023/A:1021900219772](https://doi.org/10.1023/A:1021900219772); "
                     "[CWI copy](https://ir.cwi.nl/pub/1102/1102D.pdf)",
        "how": "The closed form of Sect. 5 (gamma = 1/2 + sqrt(3)/6, alpha21 = alpha31 = 1, alpha32 = 0, gamma21 = -1, "
               "gamma31 = -gamma, gamma32 = 1/2 - 2 gamma, b = (2/3, 0, 1/3), b-hat = (1/3, 1/3, 1/3)), in 50-digit "
               "arithmetic. The transcription was first checked against the paper's own Table 5.1 (transformed form, "
               "16 digits).",
        "alpha": alpha, "gamma": gamma, "b": b, "embedded": emb, "times": times, "time_weights": tweights,
        "printed_check": float(printed_check),
        "match": lambda t: t["method"].upper().replace("_", "") in ("ROS3P",),
    }


SOURCES = [ros3p()]


def diff(t, src):
    """Largest absolute difference between a library copy and the source, over alpha, gamma and b (and the embedded
    weights when both have them)."""
    d = 0
    for k in ("alpha", "gamma"):
        for i, row in enumerate(src[k]):
            for j, v in enumerate(row):
                d = max(d, abs(M(t[k][i][j]) - M(v)))
    d = max(d, max(abs(M(x) - M(y)) for x, y in zip(t["b"], src["b"])))
    de = None
    if t.get("embedded") is not None:
        de = max(abs(M(x) - M(y)) for x, y in zip(t["embedded"], src["embedded"]))
    return float(d), (None if de is None else float(de))


def comparisons():
    rows = [json.loads(l) for l in open(ROOT / "data/rosenbrock.jsonl", encoding="utf-8")]
    out = []
    for src in SOURCES:
        copies = []
        for t in rows:
            if src["match"](t) and t["stages"] == len(src["b"]):
                d, de = diff(t, src)
                copies.append({"library": t["library"], "method": t["method"], "url": t["source"]["url"],
                               "diff": d, "embedded_diff": de})
        out.append((src, copies))
    return out


if __name__ == "__main__":
    import sys
    bad = []
    for src, copies in comparisons():
        if src["printed_check"] > 1e-14:
            bad.append(f"{src['name']}: transcription differs from the paper's table")
        for c in copies:
            if c["diff"] > 1e-12 or (c["embedded_diff"] or 0) > 1e-12:
                bad.append(f"{src['name']}: {c['library']} differs from the source")
        print(f"{src['name']}: transcription vs the paper's printed table: {src['printed_check']:.1e}")
        for c in copies:
            print(f"   {c['library']:<20} {c['method']:<8} main {c['diff']:.1e}   embedded "
                  f"{'-' if c['embedded_diff'] is None else format(c['embedded_diff'], '.1e')}")
    if bad:
        sys.exit("; ".join(bad))
