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
        "printed_check": float(printed_check), "check_label": "the transcription against the paper's Table 5.1",
    }


def standard_from_transformed(g, A, C, m, mh):
    """Hairer's transformed form back to the standard form: Gamma = (diag(1/gamma) - C)^-1, alpha = A Gamma,
    b = m Gamma (Hairer and Wanner II, Sect. IV.7)."""
    s = len(m)
    Cm, Am = mpmath.matrix(s, s), mpmath.matrix(s, s)
    for i in range(s):
        for j in range(i):
            Cm[i, j], Am[i, j] = C[i][j], A[i][j]
    G = (mpmath.diag([1 / g] * s) - Cm) ** -1
    al, b, e = Am * G, mpmath.matrix([m]) * G, mpmath.matrix([mh]) * G
    return ([[al[i, j] for j in range(s)] for i in range(s)], [[G[i, j] for j in range(s)] for i in range(s)],
            [b[j] for j in range(s)], [e[j] for j in range(s)])


def rodas():
    """E. Hairer's own code rodas.f, subroutine ROCOE, METH = 1 (RODAS of Hairer and Wanner II, Sects. IV.7 and VI.3), archived
    copy of www.unige.ch/~hairer/prog/stiff/rodas.f (2026-03-17). Transformed form, 16 digits as printed."""
    F = lambda x: M(x.replace("D", "e"))  # noqa: E731  (Fortran D exponents)
    g = F("0.2500000000000000D+00")
    a = {"21": "0.1544000000000000D+01", "31": "0.9466785280815826D+00", "32": "0.2557011698983284D+00",
         "41": "0.3314825187068521D+01", "42": "0.2896124015972201D+01", "43": "0.9986419139977817D+00",
         "51": "0.1221224509226641D+01", "52": "0.6019134481288629D+01", "53": "0.1253708332932087D+02",
         "54": "-0.6878860361058950D+00"}
    c = {"21": "-0.5668800000000000D+01", "31": "-0.2430093356833875D+01", "32": "-0.2063599157091915D+00",
         "41": "-0.1073529058151375D+00", "42": "-0.9594562251023355D+01", "43": "-0.2047028614809616D+02",
         "51": "0.7496443313967647D+01", "52": "-0.1024680431464352D+02", "53": "-0.3399990352819905D+02",
         "54": "0.1170890893206160D+02", "61": "0.8083246795921522D+01", "62": "-0.7981132988064893D+01",
         "63": "-0.3152159432874371D+02", "64": "0.1631930543123136D+02", "65": "-0.6058818238834054D+01"}
    times_printed = [M(0), F("0.386D0"), F("0.21D0"), F("0.63D0"), M(1), M(1)]   # C2, C3, C4; stages 5 and 6 at t + h
    d_printed = [F("0.2500000000000000D+00"), F("-0.1043000000000000D+00"), F("0.1035000000000000D+00"),
                 F("-0.3620000000000023D-01"), M(0), M(0)]                          # D1 to D4 (gamma_i)
    s = 6
    A = [[M(0)] * s for _ in range(s)]
    C = [[M(0)] * s for _ in range(s)]
    for k, v in a.items():
        A[int(k[0]) - 1][int(k[1]) - 1] = F(v)
    A[5][:4] = A[4][:4]   # stage 6: a6j = (a51, ..., a54, 1)
    A[5][4] = M(1)
    for k, v in c.items():
        C[int(k[0]) - 1][int(k[1]) - 1] = F(v)
    m = A[4][:4] + [M(1), M(1)]    # stiffly accurate: the solution is stage 6
    mh = A[4][:4] + [M(1), M(0)]   # the embedded solution is stage 5
    alpha, gamma, b, emb = standard_from_transformed(g, A, C, m, mh)
    times = [mpmath.fsum(r) for r in alpha]
    tweights = [mpmath.fsum(r) for r in gamma]
    check = max(max(abs(x - y) for x, y in zip(times, times_printed)), max(abs(x - y) for x, y in zip(tweights, d_printed)))
    return {
        "name": "RODAS (Hairer and Wanner)",
        "reference": "E. Hairer's own code `rodas.f`, subroutine ROCOE, METH = 1 ([archived copy of "
                     "www.unige.ch/~hairer/prog/stiff/rodas.f, 2026-03-17](https://web.archive.org/web/20260317131158/"
                     "https://www.unige.ch/~hairer/prog/stiff/rodas.f)); the method is described in E. Hairer and G. "
                     "Wanner, *Solving Ordinary Differential Equations II*, 2nd ed. (Springer, 1996), Sects. IV.7 and VI.3 (as the code's header says)",
        "how": "The 16-digit coefficients of ROCOE METH = 1 (transformed form with gamma = 0.25; the method is stiffly "
               "accurate, so b is row 6 of A and the embedded weights row 5), converted to the standard form in "
               "50-digit arithmetic. ROCOE in the archived author's file is identical, line for line, to the copy "
               "shipped with Assimulo.",
        "alpha": alpha, "gamma": gamma, "b": b, "embedded": emb, "times": times_printed, "time_weights": d_printed,
        "printed_check": float(check),
        "check_label": "the file's own stage times (C2, C3, C4) and time-derivative weights (D1 to D4) against the row "
                       "sums of alpha and Gamma",
    }


def ros2():
    """J. G. Verwer, E. J. Spee, J. G. Blom and W. Hundsdorfer, SIAM J. Sci. Comput. 20 (1999) 1456-1480,
    eqs. (3.2)-(3.4), pp. 1460-1461."""
    g = 1 + 1 / mpmath.sqrt(2)           # gamma_+ = 1 + 1/sqrt(2), p. 1461
    b2 = M(1) / 2                        # b2 = 1/2, p. 1460
    alpha = [[M(0), M(0)], [1 / (2 * b2), M(0)]]  # alpha21 = 1/(2 b2)
    gamma = [[g, M(0)], [-g / b2, g]]             # gamma21 = -gamma/b2
    b = [1 - b2, b2]                              # b1 = 1 - b2
    R = lambda z: (1 + (1 - 2 * g) * z + (M(1) / 2 - 2 * g + g * g) * z * z) / (1 - g * z) ** 2  # noqa: E731  (3.3)
    Am = mpmath.matrix([[alpha[i][j] + gamma[i][j] for j in range(2)] for i in range(2)])

    def Rc(z):  # the stability function computed from the transcription: 1 + z b^T (I - z(alpha + Gamma))^-1 1
        x = mpmath.lu_solve(mpmath.eye(2) - z * Am, mpmath.matrix([1, 1]))
        return 1 + z * (b[0] * x[0] + b[1] * x[1])
    check = max(abs(R(z) - Rc(z)) for z in (M(-1), M(-10), M("0.5"), mpmath.mpc(0, 3), M(-1000)))
    return {
        "name": "ROS2",
        "reference": "J. G. Verwer, E. J. Spee, J. G. Blom and W. Hundsdorfer, A second-order Rosenbrock method applied "
                     "to photochemical dispersion problems, *SIAM J. Sci. Comput.* 20 (1999) 1456-1480, "
                     "[doi:10.1137/S1064827597326651](https://doi.org/10.1137/S1064827597326651); "
                     "[CWI copy](https://ir.cwi.nl/pub/1252/1252D.pdf)",
        "how": "The two-stage family of eq. (3.2) with b2 = 1/2 and gamma = 1 + 1/sqrt(2) (pp. 1460-1461): b = (1/2, 1/2), "
               "alpha21 = 1/(2 b2) = 1, gamma21 = -gamma/b2 = -2 gamma, in 50-digit arithmetic. The paper notes the "
               "method is second order for any matrix in place of the Jacobian (a W-method). It defines no embedded "
               "weights, so only the main coefficients are compared.",
        "alpha": alpha, "gamma": gamma, "b": b, "embedded": None, "times": [M(0), M(1)], "time_weights": None,
        "printed_check": float(check), "check_label": "the paper's stability function (3.3) against the transcription",
    }


SOURCES = [ros3p(), rodas(), ros2()]


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
    if t.get("embedded") is not None and src.get("embedded") is not None:
        de = max(abs(M(x) - M(y)) for x, y in zip(t["embedded"], src["embedded"]))
    return float(d), (None if de is None else float(de))


def comparisons():
    rows = [json.loads(l) for l in open(ROOT / "data/rosenbrock.jsonl", encoding="utf-8")]
    out = []
    for src in SOURCES:
        copies = []
        for t in rows:
            if t["stages"] != len(src["b"]):
                continue
            d, de = diff(t, src)
            if d < 1e-8:  # a copy of this method (same coefficients to 1e-8), whatever the library calls it
                copies.append({"library": t["library"], "method": t["method"], "url": t["source"]["url"],
                               "diff": d, "embedded_diff": de})
        out.append((src, copies))
    return out


if __name__ == "__main__":
    import sys
    bad = []
    for src, copies in comparisons():
        if src["printed_check"] > 1e-14:
            bad.append(f"{src['name']}: the check of the transcription fails")
        for c in copies:
            if c["diff"] > 1e-12 or (c["embedded_diff"] or 0) > 1e-12:
                bad.append(f"{src['name']}: {c['library']} differs from the source")
        print(f"{src['name']}: {src['check_label']}: {src['printed_check']:.1e}")
        for c in copies:
            print(f"   {c['library']:<20} {c['method']:<8} main {c['diff']:.1e}   embedded "
                  f"{'-' if c['embedded_diff'] is None else format(c['embedded_diff'], '.1e')}")
    if bad:
        sys.exit("; ".join(bad))
