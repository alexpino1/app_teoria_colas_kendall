"""
M/M/* queue model calculators (Markovian arrivals and service).
"""

import math


def _erlang_c(a, c):
    """Erlang-C: P(wait) for M/M/c"""
    rho = a / c
    num = (a**c / math.factorial(c)) * (1 / (1 - rho))
    den = sum(a**n / math.factorial(n) for n in range(c)) + num
    return num / den


def _p0_mmc(a, c):
    rho = a / c
    s = sum(a**n / math.factorial(n) for n in range(c))
    s += (a**c / math.factorial(c)) * (1 / (1 - rho))
    return 1 / s


def calcular_mm1(lam, mu):
    """M/M/1"""
    rho = lam / mu
    if rho >= 1:
        return None, f"Sistema inestable: ρ = {rho:.4f} ≥ 1"
    P0 = 1 - rho
    Lq = math.ceil(rho**2 / (1 - rho))
    L  = math.ceil(rho / (1 - rho))
    Wq = Lq / lam
    W  = L  / lam
    Pn = lambda n: P0 * rho**n
    return {
        "modelo": "M/M/1",
        "rho": rho, "P0": P0, "L": L, "Lq": Lq,
        "W": W, "Wq": Wq, "lambda_ef": lam,
        "Pn_func": Pn,
        "extra": {}
    }, None


def calcular_mmc(lam, mu, c):
    """M/M/c"""
    a   = lam / mu
    rho = a / c
    if rho >= 1:
        return None, f"Sistema inestable: ρ = {rho:.4f} ≥ 1"
    P0  = _p0_mmc(a, c)
    Cw  = _erlang_c(a, c)
    Lq  = math.ceil(Cw * rho / (1 - rho))
    Wq  = Lq / lam
    W   = Wq + 1 / mu
    L   = math.ceil(lam * W)
    def Pn(n):
        if n < c:
            return P0 * a**n / math.factorial(n)
        return P0 * a**n / (math.factorial(c) * c**(n - c))
    return {
        "modelo": f"M/M/{c}",
        "rho": rho, "P0": P0, "L": L, "Lq": Lq,
        "W": W, "Wq": Wq, "lambda_ef": lam,
        "Pn_func": Pn,
        "extra": {"Erlang-C (P_espera)": f"{Cw:.6f}", "Servidores c": c}
    }, None


def calcular_mm1k(lam, mu, K):
    """M/M/1/K — finite capacity"""
    rho = lam / mu
    if abs(rho - 1) < 1e-12:
        P0 = 1 / (K + 1)
    else:
        P0 = (1 - rho) / (1 - rho**(K + 1))
    Pn_f  = lambda n: P0 * rho**n if n <= K else 0
    PK    = Pn_f(K)
    lam_e = lam * (1 - PK)
    L     = math.ceil(sum(n * Pn_f(n) for n in range(K + 1)))
    Lq    = math.ceil(sum((n - 1) * Pn_f(n) for n in range(1, K + 1)))
    W     = L  / lam_e if lam_e > 0 else 0
    Wq    = Lq / lam_e if lam_e > 0 else 0
    return {
        "modelo": f"M/M/1/{K}",
        "rho": rho, "P0": P0, "L": L, "Lq": Lq,
        "W": W, "Wq": Wq, "lambda_ef": lam_e,
        "Pn_func": Pn_f,
        "extra": {f"P(rechazo) P_{K}": f"{PK:.6f}",
                  "λ efectiva": f"{lam_e:.6f}",
                  "Capacidad K": K}
    }, None


def calcular_mmck(lam, mu, c, K):
    """M/M/c/K — c servers, capacity K"""
    if K < c:
        return None, "K debe ser ≥ c"
    a   = lam / mu
    rho = a / c
    s1  = sum(a**n / math.factorial(n) for n in range(c))
    s2  = sum(a**n / (math.factorial(c) * c**(n - c)) for n in range(c, K + 1))
    P0  = 1 / (s1 + s2)
    def Pn_f(n):
        if n < 0 or n > K: return 0
        if n < c: return P0 * a**n / math.factorial(n)
        return P0 * a**n / (math.factorial(c) * c**(n - c))
    PK    = Pn_f(K)
    lam_e = lam * (1 - PK)
    L     = math.ceil(sum(n * Pn_f(n) for n in range(K + 1)))
    Lq    = math.ceil(sum((n - c) * Pn_f(n) for n in range(c, K + 1)))
    W     = L  / lam_e if lam_e > 0 else 0
    Wq    = Lq / lam_e if lam_e > 0 else 0
    return {
        "modelo": f"M/M/{c}/{K}",
        "rho": rho, "P0": P0, "L": L, "Lq": Lq,
        "W": W, "Wq": Wq, "lambda_ef": lam_e,
        "Pn_func": Pn_f,
        "extra": {f"P(rechazo) P_{K}": f"{PK:.6f}",
                  "λ efectiva": f"{lam_e:.6f}",
                  "Servidores c": c, "Capacidad K": K}
    }, None


def calcular_mm1kk(lam, mu, K):
    """M/M/1/K/K — finite population (closed model)"""
    def tasa_lam(n): return max(K - n, 0) * lam
    rho  = lam / mu
    vals = [math.comb(K, n) * rho**n for n in range(K + 1)]
    total = sum(vals)
    Pn_f = lambda n: vals[n] / total if 0 <= n <= K else 0
    P0   = Pn_f(0)
    lam_e = sum(tasa_lam(n) * Pn_f(n) for n in range(K + 1))
    L    = math.ceil(sum(n * Pn_f(n) for n in range(K + 1)))
    Lq   = math.ceil(sum((n - 1) * Pn_f(n) for n in range(1, K + 1)))
    W    = L  / lam_e if lam_e > 0 else 0
    Wq   = Lq / lam_e if lam_e > 0 else 0
    rho_ef = lam_e / mu
    return {
        "modelo": f"M/M/1/{K}/{K}",
        "rho": rho_ef, "P0": P0, "L": L, "Lq": Lq,
        "W": W, "Wq": Wq, "lambda_ef": lam_e,
        "Pn_func": Pn_f,
        "extra": {"Población N": K, "λ_ef": f"{lam_e:.6f}"}
    }, None
