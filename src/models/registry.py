"""
MODELOS registry: maps each Kendall notation name to its metadata,
parameter definitions, and calculator function.
"""

from .markovian import (
    calcular_mm1,
    calcular_mmc,
    calcular_mm1k,
    calcular_mmck,
    calcular_mm1kk,
)
from .general import (
    calcular_md1,
    calcular_mg1,
    calcular_mek1,
    calcular_mminf,
)

MODELOS = {
    "M/M/1": {
        "desc": "Un servidor · Poisson · Exponencial · Capacidad ∞",
        "params": [
            ("λ  (tasa llegada)", "lambda"),
            ("μ  (tasa servicio)", "mu"),
        ],
        "fn": lambda p: calcular_mm1(p["lambda"], p["mu"]),
        "kendall": "A/B/c/K/N/D",
        "detalle": "M / M / 1 / ∞ / ∞ / FCFS",
    },
    "M/M/c": {
        "desc": "c servidores paralelos · Poisson · Exponencial",
        "params": [
            ("λ  (tasa llegada)", "lambda"),
            ("μ  (tasa servicio por servidor)", "mu"),
            ("c  (número de servidores)", "c", "int"),
        ],
        "fn": lambda p: calcular_mmc(p["lambda"], p["mu"], int(p["c"])),
        "kendall": "M / M / c / ∞ / ∞ / FCFS",
        "detalle": "Erlang-C",
    },
    "M/M/1/K": {
        "desc": "Un servidor · capacidad máxima K (pérdidas)",
        "params": [
            ("λ  (tasa llegada)", "lambda"),
            ("μ  (tasa servicio)", "mu"),
            ("K  (capacidad del sistema)", "K", "int"),
        ],
        "fn": lambda p: calcular_mm1k(p["lambda"], p["mu"], int(p["K"])),
        "kendall": "M / M / 1 / K / ∞ / FCFS",
        "detalle": "Clientes rechazados si sistema lleno",
    },
    "M/M/c/K": {
        "desc": "c servidores · capacidad máxima K",
        "params": [
            ("λ  (tasa llegada)", "lambda"),
            ("μ  (tasa servicio)", "mu"),
            ("c  (servidores)", "c", "int"),
            ("K  (capacidad total  ≥ c)", "K", "int"),
        ],
        "fn": lambda p: calcular_mmck(p["lambda"], p["mu"], int(p["c"]), int(p["K"])),
        "kendall": "M / M / c / K / ∞ / FCFS",
        "detalle": "Extensión general con pérdidas",
    },
    "M/M/1/K/K": {
        "desc": "Población finita K · un servidor (modelo cerrado)",
        "params": [
            ("λ  (tasa llegada individual)", "lambda"),
            ("μ  (tasa servicio)", "mu"),
            ("K  (tamaño de la población)", "K", "int"),
        ],
        "fn": lambda p: calcular_mm1kk(p["lambda"], p["mu"], int(p["K"])),
        "kendall": "M / M / 1 / K / K / FCFS",
        "detalle": "Fuente finita — máquinas en reparación",
    },
    "M/D/1": {
        "desc": "Un servidor · servicio determinístico (tiempo fijo)",
        "params": [
            ("λ  (tasa llegada)", "lambda"),
            ("μ  (tasa servicio  1/tiempo_fijo)", "mu"),
        ],
        "fn": lambda p: calcular_md1(p["lambda"], p["mu"]),
        "kendall": "M / D / 1 / ∞ / ∞ / FCFS",
        "detalle": "P-K: Lq = ρ²/2(1-ρ)",
    },
    "M/G/1": {
        "desc": "Un servidor · servicio general (Pollaczek-Khinchine)",
        "params": [
            ("λ  (tasa llegada)", "lambda"),
            ("μ  (tasa servicio media)", "mu"),
            ("CV (coef. variación del servicio)", "cv"),
        ],
        "fn": lambda p: calcular_mg1(p["lambda"], p["mu"], p["cv"]),
        "kendall": "M / G / 1 / ∞ / ∞ / FCFS",
        "detalle": "CV=0→M/D/1, CV=1→M/M/1, CV>1→hiper-exp",
    },
    "M/Ek/1": {
        "desc": "Un servidor · servicio Erlang-k etapas",
        "params": [
            ("λ  (tasa llegada)", "lambda"),
            ("μ  (tasa servicio media)", "mu"),
            ("k  (etapas Erlang  k≥1)", "k", "int"),
        ],
        "fn": lambda p: calcular_mek1(p["lambda"], p["mu"], int(p["k"])),
        "kendall": "M / Ek / 1 / ∞ / ∞ / FCFS",
        "detalle": "k=1→M/M/1, k→∞→M/D/1",
    },
    "M/M/∞": {
        "desc": "Servidores infinitos · sin espera posible",
        "params": [
            ("λ  (tasa llegada)", "lambda"),
            ("μ  (tasa servicio)", "mu"),
        ],
        "fn": lambda p: calcular_mminf(p["lambda"], p["mu"]),
        "kendall": "M / M / ∞ / ∞ / ∞ / FCFS",
        "detalle": "Modelo de auto-servicio / telefonía sin bloqueo",
    },
}
