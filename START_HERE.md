# Start here

Five widely used methods, each with its tableau, its first published source and when you would reach for it. Every tableau below is generated from `data/` (by `scripts/render_start.py`): it is the library copy that was compared with the method's source, exact where the library stores exact values. Strings like '1/6' are exact rationals; evaluate them in your own precision. `examples/convergence.py` runs all five on y' = y cos t.


## Classical RK4 (Kutta 1901)

Order 4, 4 stages, explicit.

**When to use it.** Fixed-step integration of non-stiff problems when simplicity matters more than efficiency. It has no error estimate, so the step size is yours to choose and check.

**Source.** W. Kutta, *Z. Math. Phys.* 46 (1901) 435-453. Compared copies: see [SOURCES.md](SOURCES.md#classical-rk4-kutta-1901).

**Tableau** (exact; from Assimulo `RungeKutta4 (as coded)`, one of 23 copies in this group that match the source):

```python
c = ['0', '1/2', '1/2', '1']
A = [['0', '0', '0', '0'], ['1/2', '0', '0', '0'], ['0', '1/2', '0', '0'], ['0', '0', '1', '0']]
b = ['1/6', '1/3', '1/3', '1/6']
```
Check it yourself: `physverify.butcher.check_tableau(A, b, c, claimed=4)` after converting the strings to numbers.

## Dormand-Prince 5(4)

Order 5, 7 stages, explicit.

**When to use it.** Adaptive steps for non-stiff problems at moderate tolerances. It is the pair behind SciPy's `RK45` and MATLAB's `ode45`; the 5th-order solution is propagated and the 4th-order one estimates the error.

**Source.** J. R. Dormand and P. J. Prince, *J. Comput. Appl. Math.* 6 (1980) 19-26, [doi:10.1016/0771-050X(80)90013-3](https://doi.org/10.1016/0771-050X(80)90013-3). Compared copies: see [SOURCES.md](SOURCES.md#dormand-prince-5-4).

**Tableau** (exact; from NodePy `DP5`, one of 12 copies in this group that match the source):

```python
c = ['0', '1/5', '3/10', '4/5', '8/9', '1', '1']
A = [['0', '0', '0', '0', '0', '0', '0'], ['1/5', '0', '0', '0', '0', '0', '0'], ['3/40', '9/40', '0', '0', '0', '0', '0'], ['44/45', '-56/15', '32/9', '0', '0', '0', '0'], ['19372/6561', '-25360/2187', '64448/6561', '-212/729', '0', '0', '0'], ['9017/3168', '-355/33', '46732/5247', '49/176', '-5103/18656', '0', '0'], ['35/384', '0', '500/1113', '125/192', '-2187/6784', '11/84', '0']]
b = ['35/384', '0', '500/1113', '125/192', '-2187/6784', '11/84', '0']
b_embedded = ['5179/57600', '0', '7571/16695', '393/640', '-92097/339200', '187/2100', '1/40']
```
Check it yourself: `physverify.butcher.check_tableau(A, b, c, claimed=5)` after converting the strings to numbers.

## Tsitouras 5(4)

Order 5, 7 stages, explicit.

**When to use it.** An alternative adaptive 5(4) pair for non-stiff problems, built with only the first-column simplifying assumption; `Tsit5` in Julia's OrdinaryDiffEq.jl. The coefficients are decimals, given here with all printed digits.

**Source.** Ch. Tsitouras, *Comput. Math. Appl.* 62 (2011) 770-775, [doi:10.1016/j.camwa.2011.06.002](https://doi.org/10.1016/j.camwa.2011.06.002). Note the erratum on the preprint's error weights in [ERRATA.md](ERRATA.md). Compared copies: see [SOURCES.md](SOURCES.md#tsitouras-5-4).

**Tableau** (decimals as printed; from Rust diffsol `tsit45 (as coded)`, one of 4 copies in this group that match the source):

```python
c = ['0', '0.161', '0.327', '0.9', '0.9800255409045097', '1', '1']
A = [['0', '0', '0', '0', '0', '0', '0'], ['(0.161)-(+0)', '0', '0', '0', '0', '0', '0'], ['(0.327)-((0.335480655492357)+0)', '0.335480655492357', '0', '0', '0', '0', '0'], ['(0.9)-((-6.359448489975075)+(4.362295432869581)+0)', '-6.359448489975075', '4.362295432869581', '0', '0', '0', '0'], ['(0.9800255409045097)-((-11.74888356406283)+(7.495539342889836)+(-0.09249506636175525)+0)', '-11.74888356406283', '7.495539342889836', '-0.09249506636175525', '0', '0', '0'], ['(1)-((-12.92096931784711)+(8.159367898576159)+(-0.071584973281401)+(-0.02826905039406838)+0)', '-12.92096931784711', '8.159367898576159', '-0.071584973281401', '-0.02826905039406838', '0', '0'], ['0.09646076681806523', '0.01', '0.4798896504144996', '1.379008574103742', '-3.290069515436081', '2.324710524099774', '0']]
b = ['0.09646076681806523', '0.01', '0.4798896504144996', '1.379008574103742', '-3.290069515436081', '2.324710524099774', '0']
b_embedded = ['(0.09646076681806523)-(-0.001780011052225777)', '(0.01)-(-0.0008164344596567469)', '(0.4798896504144996)-(0.007880878010261995)', '(1.379008574103742)-(-0.1447110071732629)', '(-3.290069515436081)-(0.5823571654525552)', '(2.324710524099774)-(-0.45808210592918697)', '(0)-(0.015151515151515152)']
```
Check it yourself: `physverify.butcher.check_tableau(A, b, c, claimed=5)` after converting the strings to numbers.

## SSPRK(3,3)

Order 3, 3 stages, explicit.

**When to use it.** Method-of-lines time stepping for hyperbolic PDEs with a TVD or limited spatial discretisation: it keeps the strong-stability property of forward Euler under the same step-size limit (SSP coefficient 1).

**Source.** C.-W. Shu and S. Osher, *J. Comput. Phys.* 77 (1988) 439-471, [doi:10.1016/0021-9991(88)90177-5](https://doi.org/10.1016/0021-9991(88)90177-5). Compared copies: see [SOURCES.md](SOURCES.md#ssprk-3-3).

**Tableau** (decimals as printed; from qmat `RK33`, one of 11 copies in this group that match the source):

```python
c = ['0.0', '1.0', '0.5']
A = [['0.0', '0.0', '0.0'], ['1.0', '0.0', '0.0'], ['0.25', '0.25', '0.0']]
b = ['0.16666666666666666', '0.16666666666666666', '0.6666666666666666']
```
Check it yourself: `physverify.butcher.check_tableau(A, b, c, claimed=3)` after converting the strings to numbers.

## Radau IIA, 3 stages

Order 5, 3 stages, implicit, stage order 3.

**When to use it.** Stiff problems and index-1 DAEs: implicit, L-stable, order 5, stage order 3. It is the method in Hairer and Wanner's `radau5` code. Each step solves a nonlinear system of 3 stages.

**Source.** B. L. Ehle, Research Report CSRR 2010, University of Waterloo (1969); construction as in Hairer and Wanner, *Solving Ordinary Differential Equations II*, Sect. IV.5. Compared copies: see [SOURCES.md](SOURCES.md#radau-iia-3-stages).

**Tableau** (exact; from NodePy `RadauIIA3`, one of 3 copies in this group that match the source):

```python
c = ['2/5 - sqrt(6)/10', 'sqrt(6)/10 + 2/5', '1']
A = [['11/45 - 7*sqrt(6)/360', '37/225 - 169*sqrt(6)/1800', '-2/225 + sqrt(6)/75'], ['37/225 + 169*sqrt(6)/1800', '7*sqrt(6)/360 + 11/45', '-sqrt(6)/75 - 2/225'], ['4/9 - sqrt(6)/36', 'sqrt(6)/36 + 4/9', '1/9']]
b = ['4/9 - sqrt(6)/36', 'sqrt(6)/36 + 4/9', '1/9']
```
Check it yourself: `physverify.butcher.check_tableau(A, b, c, claimed=5)` after converting the strings to numbers.
