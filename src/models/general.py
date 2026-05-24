"""
Non-Markovian and infinite-server queue model calculators.
Uses the Pollaczek-Khinchine (P-K) mean value formula for M/G/1 variants.
"""

import math


def calcular_md1(lam, mu):
    """M/D/1 — deterministic service time"""
    rho = lam / mu
    if rho >= 1:
        return None, f"Sistema inestable: ρ = {rho:.4f} ≥ 1"
    ES  = 1 / mu
    ES2 = ES**2  # deterministic: variance = 0
    Lq  = math.ceil((lam**2 * ES2) / (2 * (1 - rho)))
    L   = math.ceil(rho + Lq)
    Wq  = Lq / lam
    W   = Wq + ES
    P0  = 1 - rho
    Pn  = lambda n: (1 - rho) * rho**n
    return {
        "modelo": "M/D/1",
        "rho": rho, "P0": P0, "L": L, "Lq": Lq,
        "W": W, "Wq": Wq, "lambda_ef": lam,
        "Pn_func": Pn,
        "extra": {"Coef. variación²": "0 (determinístico)",
                  "Lq vs M/M/1": "Lq(M/D/1) = Lq(M/M/1)/2"}
    }, None


def calcular_mg1(lam, mu, cv):
    """M/G/1 — Pollaczek-Khinchine, general service"""
    rho = lam / mu
    if rho >= 1:
        return None, f"Sistema inestable: ρ = {rho:.4f} ≥ 1"
    ES  = 1 / mu
    ES2 = (cv**2 + 1) / mu**2  # E[S²] = Var[S] + E[S]²
    Lq  = math.ceil((lam**2 * ES2) / (2 * (1 - rho)))
    L   = math.ceil(rho + Lq)
    Wq  = Lq / lam
    W   = Wq + ES
    P0  = 1 - rho
    Pn  = lambda n: (1 - rho) * rho**n
    return {
        "modelo": "M/G/1",
        "rho": rho, "P0": P0, "L": L, "Lq": Lq,
        "W": W, "Wq": Wq, "lambda_ef": lam,
        "Pn_func": Pn,
        "extra": {"Coef. variación (CV)": f"{cv:.4f}",
                  "E[S]": f"{ES:.6f}", "E[S²]": f"{ES2:.6f}"}
    }, None


def calcular_mek1(lam, mu, k):
    """M/Ek/1 — Erlang-k service (special case of M/G/1)"""
    rho = lam / mu
    if rho >= 1:
        return None, f"Sistema inestable: ρ = {rho:.4f} ≥ 1"
    cv  = 1 / math.sqrt(k)
    ES  = 1 / mu
    ES2 = (1 / k + 1) / mu**2
    Lq  = math.ceil((lam**2 * ES2) / (2 * (1 - rho)))
    L   = math.ceil(rho + Lq)
    Wq  = Lq / lam
    W   = Wq + ES
    P0  = 1 - rho
    Pn  = lambda n: (1 - rho) * rho**n
    return {
        "modelo": f"M/Ek/1 (k={k})",
        "rho": rho, "P0": P0, "L": L, "Lq": Lq,
        "W": W, "Wq": Wq, "lambda_ef": lam,
        "Pn_func": Pn,
        "extra": {"Etapas Erlang k": k,
                  "CV = 1/√k": f"{cv:.6f}"}
    }, None


def calcular_mminf(lam, mu):
    """M/M/∞ — infinite servers (no queue ever forms)"""
    rho = lam / mu
    P0  = math.exp(-rho)
    Pn  = lambda n: math.exp(-rho) * rho**n / math.factorial(n)
    L   = math.ceil(rho)
    Lq  = 0.0
    W   = 1 / mu
    Wq  = 0.0
    return {
        "modelo": "M/M/∞",
        "rho": rho, "P0": P0, "L": L, "Lq": Lq,
        "W": W, "Wq": Wq, "lambda_ef": lam,
        "Pn_func": Pn,
        "extra": {"Distribución N": "Poisson(λ/μ)",
                  "Cola": "Nunca se forma"}
    }, None
