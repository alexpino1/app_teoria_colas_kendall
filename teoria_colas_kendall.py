"""
Teoría de Colas - Notación de Kendall
Aplicación de escritorio completa con todas las variantes A/B/c/K/N/D
Modelos: M/M/1, M/M/c, M/M/1/K, M/M/c/K, M/M/1/K/K (cerrado),
         M/D/1, M/G/1, M/Ek/1, M/M/∞
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math
import threading
from _pydecimal import ROUND_UP

# ─── Intentar importar matplotlib ───────────────────────────────────────────
try:
    import matplotlib
    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import numpy as np
    MATPLOTLIB_OK = True
except ImportError:
    MATPLOTLIB_OK = False

# ════════════════════════════════════════════════════════════════
#  PALETA Y CONSTANTES
# ════════════════════════════════════════════════════════════════
BG         = "#0D1117"
CARD       = "#161B22"
ACCENT     = "#238636"
ACCENT2    = "#1F6FEB"
TEXT       = "#E6EDF3"
TEXT_DIM   = "#8B949E"
BORDER     = "#30363D"
RED        = "#DA3633"
YELLOW     = "#D29922"
GREEN      = "#3FB950"
PURPLE     = "#8957E5"
CYAN       = "#39D353"
FONT_TITLE = ("Consolas", 22, "bold")
FONT_HEAD  = ("Consolas", 13, "bold")
FONT_LABEL = ("Consolas", 11)
FONT_ENTRY = ("Consolas", 12)
FONT_RESULT= ("Consolas", 12)
FONT_SMALL = ("Consolas", 10)


# ════════════════════════════════════════════════════════════════
#  MOTOR DE CÁLCULO — todas las variantes
# ════════════════════════════════════════════════════════════════

def _erlang_c(a, c):
    """Erlang-C: P(esperar) para M/M/c"""
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
    Cw  = _erlang_c(a, c)          # Erlang C
    Lq  = math.ceil(Cw * rho / (1 - rho))
    Wq  = Lq / lam
    W   = Wq + 1/mu
    L   = math.ceil(lam * W)
    def Pn(n):
        if n < c:
            return P0 * a**n / math.factorial(n)
        return P0 * a**n / (math.factorial(c) * c**(n-c))
    return {
        "modelo": f"M/M/{c}",
        "rho": rho, "P0": P0, "L": L, "Lq": Lq,
        "W": W, "Wq": Wq, "lambda_ef": lam,
        "Pn_func": Pn,
        "extra": {"Erlang-C (P_espera)": f"{Cw:.6f}", "Servidores c": c}
    }, None


def calcular_mm1k(lam, mu, K):
    """M/M/1/K — capacidad finita"""
    rho = lam / mu
    if abs(rho - 1) < 1e-12:
        P0 = 1 / (K + 1)
    else:
        P0 = (1 - rho) / (1 - rho**(K+1))
    Pn_f  = lambda n: P0 * rho**n if n <= K else 0
    PK    = Pn_f(K)
    lam_e = lam * (1 - PK)
    L     = math.ceil(sum(n * Pn_f(n) for n in range(K+1)))
    Lq    = math.ceil(sum((n-1) * Pn_f(n) for n in range(1, K+1)))
    W     = L  / lam_e  if lam_e > 0 else 0
    Wq    = Lq / lam_e  if lam_e > 0 else 0
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
    """M/M/c/K — c servidores, capacidad K"""
    if K < c:
        return None, "K debe ser ≥ c"
    a   = lam / mu
    rho = a / c
    # Calcular P0
    s1 = sum(a**n / math.factorial(n) for n in range(c))
    s2 = sum(a**n / (math.factorial(c) * c**(n-c)) for n in range(c, K+1))
    P0 = 1 / (s1 + s2)
    def Pn_f(n):
        if n < 0 or n > K: return 0
        if n < c: return P0 * a**n / math.factorial(n)
        return P0 * a**n / (math.factorial(c) * c**(n-c))
    PK    = Pn_f(K)
    lam_e = lam * (1 - PK)
    L     = math.ceil(sum(n * Pn_f(n) for n in range(K+1)))
    Lq    = math.ceil(sum((n-c) * Pn_f(n) for n in range(c, K+1)))
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
    """M/M/1/K/K — población finita (modelo cerrado)"""
    # λ individual = lam, estado n: tasa llegada = (K-n)*lam
    def tasa_lam(n): return max(K - n, 0) * lam
    # P0
    coef = [math.factorial(K) / math.factorial(K-n) * (lam/mu)**n / math.factorial(n)
            if n <= K else 0 for n in range(K+1)]
    # usar fórmula directa
    rho = lam / mu
    vals = [math.comb(K, n) * rho**n for n in range(K+1)]
    total = sum(vals)
    Pn_f = lambda n: vals[n]/total if 0 <= n <= K else 0
    P0   = Pn_f(0)
    lam_e= sum(tasa_lam(n) * Pn_f(n) for n in range(K+1))
    L    = math.ceil(sum(n * Pn_f(n) for n in range(K+1)))
    Lq   = math.ceil(sum((n-1) * Pn_f(n) for n in range(1, K+1)))
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


def calcular_md1(lam, mu):
    """M/D/1 — servicio determinístico"""
    rho = lam / mu
    if rho >= 1:
        return None, f"Sistema inestable: ρ = {rho:.4f} ≥ 1"
    # Pollaczek-Khinchine: E[S]=1/mu, E[S²]=1/mu² (determinístico → var=0)
    ES  = 1/mu
    ES2 = ES**2      # determinístico: sin varianza
    Lq  = math.ceil((lam**2 * ES2) / (2*(1-rho)))
    L   = math.ceil(rho + Lq)
    Wq  = Lq / lam
    W   = Wq + ES
    P0  = 1 - rho
    Pn  = lambda n: (1-rho)*rho**n  # aproximación M/D/1
    return {
        "modelo": "M/D/1",
        "rho": rho, "P0": P0, "L": L, "Lq": Lq,
        "W": W, "Wq": Wq, "lambda_ef": lam,
        "Pn_func": Pn,
        "extra": {"Coef. variación²": "0 (determinístico)",
                  "Lq vs M/M/1": "Lq(M/D/1) = Lq(M/M/1)/2"}
    }, None


def calcular_mg1(lam, mu, cv):
    """M/G/1 — Pollaczek-Khinchine, servicio general"""
    rho = lam / mu
    if rho >= 1:
        return None, f"Sistema inestable: ρ = {rho:.4f} ≥ 1"
    ES  = 1/mu
    ES2 = (cv**2 + 1) / mu**2    # E[S²] = Var[S] + E[S]² = cv²/mu² + 1/mu²
    Lq  = math.ceil((lam**2 * ES2) / (2*(1-rho)))
    L   = math.ceil(rho + Lq)
    Wq  = Lq / lam
    W   = Wq + ES
    P0  = 1 - rho
    Pn  = lambda n: (1-rho)*rho**n
    return {
        "modelo": "M/G/1",
        "rho": rho, "P0": P0, "L": L, "Lq": Lq,
        "W": W, "Wq": Wq, "lambda_ef": lam,
        "Pn_func": Pn,
        "extra": {"Coef. variación (CV)": f"{cv:.4f}",
                  "E[S]": f"{ES:.6f}", "E[S²]": f"{ES2:.6f}"}
    }, None


def calcular_mek1(lam, mu, k):
    """M/Ek/1 — Erlang-k service (caso especial de M/G/1)"""
    rho = lam / mu
    if rho >= 1:
        return None, f"Sistema inestable: ρ = {rho:.4f} ≥ 1"
    cv  = 1 / math.sqrt(k)       # CV de Erlang-k
    ES  = 1/mu
    ES2 = (1/k + 1) / mu**2
    Lq  = math.ceil((lam**2 * ES2) / (2*(1-rho)))
    L   = math.ceil(rho + Lq)
    Wq  = Lq / lam
    W   = Wq + ES
    P0  = 1 - rho
    Pn  = lambda n: (1-rho)*rho**n
    return {
        "modelo": f"M/Ek/1 (k={k})",
        "rho": rho, "P0": P0, "L": L, "Lq": Lq,
        "W": W, "Wq": Wq, "lambda_ef": lam,
        "Pn_func": Pn,
        "extra": {"Etapas Erlang k": k,
                  "CV = 1/√k": f"{cv:.6f}"}
    }, None


def calcular_mminf(lam, mu):
    """M/M/∞ — servidores infinitos (sin cola)"""
    rho = lam / mu   # carga media
    P0  = math.exp(-rho)
    Pn  = lambda n: math.exp(-rho) * rho**n / math.factorial(n)
    L   = math.ceil(rho)          # E[N] = λ/μ
    Lq  = 0.0          # nunca hay cola
    W   = 1/mu
    Wq  = 0.0
    return {
        "modelo": "M/M/∞",
        "rho": rho, "P0": P0, "L": L, "Lq": Lq,
        "W": W, "Wq": Wq, "lambda_ef": lam,
        "Pn_func": Pn,
        "extra": {"Distribución N": "Poisson(λ/μ)",
                  "Cola": "Nunca se forma"}
    }, None


# ════════════════════════════════════════════════════════════════
#  CONFIGURACIÓN DE CADA MODELO (nombre, parámetros, función)
# ════════════════════════════════════════════════════════════════
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


# ════════════════════════════════════════════════════════════════
#  APLICACIÓN TKINTER
# ════════════════════════════════════════════════════════════════

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Teoría de Colas — Notación de Kendall")
        self.configure(bg=BG)
        self.geometry("1280x820")
        self.minsize(960, 680)
        self.resizable(True, True)
        self._resultado = None
        
        # Pre-inicializar atributos que se crean en _build_right
        # para evitar AttributeError si _build_left los referencia antes
        self._lbl_modelo  = None
        self._lbl_kendall = None
        self._lbl_detalle = None
        self._build_ui()

    # ── UI principal ──────────────────────────────────────────
    def _build_ui(self):
        # ── Header ──────────────────────────────────────────
        hdr = tk.Frame(self, bg=BG, pady=14)
        hdr.pack(fill="x", padx=24)
        tk.Label(hdr, text=" TEORÍA DE COLAS ", font=FONT_TITLE,
                 bg=BG, fg=ACCENT).pack(side="left")
        tk.Label(hdr, text="Notación de Kendall  ",
                 font=FONT_LABEL, bg=BG, fg=TEXT_DIM).pack(side="left", padx=18)

        sep = tk.Frame(self, bg=BORDER, height=1)
        sep.pack(fill="x", padx=0)

        # ── Body layout ──────────────────────────────────────
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=18, pady=12)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        # Panel izquierdo (selector + parámetros) — se crea el frame pero
        # _select_model se llama DESPUÉS de _build_right para que los labels existan
        left = tk.Frame(body, bg=CARD, bd=0, relief="flat",
                        highlightthickness=1, highlightbackground=BORDER)
        left.grid(row=0, column=0, sticky="nsew", padx=(0,10))
        left.configure(width=310)
        left.pack_propagate(False)

        # Panel derecho (resultados + gráfica) — se construye PRIMERO
        right = tk.Frame(body, bg=BG)
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)
        self._build_right(right)

        # Ahora sí construimos el panel izquierdo (que llama a _select_model internamente)
        self._build_left(left)

    # ── Panel izquierdo ───────────────────────────────────────
    def _build_left(self, parent):
        # Título sección
        tk.Label(parent, text="MODELO", font=FONT_HEAD,
                 bg=CARD, fg=ACCENT, pady=14).pack(fill="x", padx=18)
        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x")

        # Lista de modelos
        lf = tk.Frame(parent, bg=CARD)
        lf.pack(fill="x", padx=10, pady=10)
        self._model_var = tk.StringVar(value=list(MODELOS.keys())[0])
        self._model_btns = {}
        for nombre in MODELOS:
            btn = tk.Button(
                lf, text=nombre, font=FONT_LABEL,
                bg=CARD, fg=TEXT, bd=0, cursor="hand2",
                activebackground=ACCENT2, activeforeground=TEXT,
                anchor="w", padx=12, pady=6,
                command=lambda n=nombre: self._select_model(n)
            )
            btn.pack(fill="x", pady=1)
            self._model_btns[nombre] = btn

        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x")

        # Área de parámetros — creada ANTES de llamar a _select_model
        tk.Label(parent, text="PARÁMETROS", font=FONT_HEAD,
                 bg=CARD, fg=ACCENT2, pady=10).pack(fill="x", padx=18)

        self._params_frame = tk.Frame(parent, bg=CARD)
        self._params_frame.pack(fill="x", padx=14, pady=4)

        # Botón calcular
        tk.Button(
            parent, text="▶  CALCULAR", font=FONT_HEAD,
            bg=ACCENT, fg=TEXT, bd=0, cursor="hand2",
            activebackground="#2EA043", activeforeground=TEXT,
            pady=10, command=self._calcular
        ).pack(fill="x", padx=14, pady=14)

        # Botón limpiar
        tk.Button(
            parent, text="✕  Limpiar", font=FONT_SMALL,
            bg=CARD, fg=TEXT_DIM, bd=0, cursor="hand2",
            activebackground=BORDER, activeforeground=TEXT,
            pady=6, command=self._limpiar
        ).pack(fill="x", padx=14)

        # _select_model AL FINAL: cuando _params_frame y los labels del panel
        # derecho ya están creados
        self._select_model(list(MODELOS.keys())[0])

    # ── Panel derecho ─────────────────────────────────────────
    def _build_right(self, parent):
        # Descripción modelo
        self._desc_frame = tk.Frame(parent, bg=CARD,
                                    highlightthickness=1, highlightbackground=BORDER)
        self._desc_frame.grid(row=0, column=0, sticky="ew", pady=(0,10))
        self._lbl_modelo    = tk.Label(self._desc_frame, text="", font=FONT_HEAD,
                                       bg=CARD, fg=TEXT, anchor="w", padx=16, pady=8)
        self._lbl_modelo.pack(fill="x")
        self._lbl_kendall   = tk.Label(self._desc_frame, text="", font=FONT_SMALL,
                                       bg=CARD, fg=ACCENT2, anchor="w", padx=16)
        self._lbl_kendall.pack(fill="x")
        self._lbl_detalle   = tk.Label(self._desc_frame, text="", font=FONT_SMALL,
                                       bg=CARD, fg=TEXT_DIM, anchor="w", padx=16, pady=6)
        self._lbl_detalle.pack(fill="x")

        # Notebook resultados / gráfica
        nb_frame = tk.Frame(parent, bg=BG)
        nb_frame.grid(row=1, column=0, sticky="nsew")
        nb_frame.rowconfigure(0, weight=1)
        nb_frame.columnconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Dark.TNotebook", background=BG, borderwidth=0)
        style.configure("Dark.TNotebook.Tab", background=CARD, foreground=TEXT_DIM,
                        font=FONT_LABEL, padding=[14, 6])
        style.map("Dark.TNotebook.Tab",
                  background=[("selected", ACCENT2)],
                  foreground=[("selected", TEXT)])

        self._nb = ttk.Notebook(nb_frame, style="Dark.TNotebook")
        self._nb.pack(fill="both", expand=True)

        # Tab 1: Resultados
        res_tab = tk.Frame(self._nb, bg=BG)
        self._nb.add(res_tab, text="  Resultados  ")
        self._build_results_tab(res_tab)

        # Tab 2: Gráfica Pn
        self._graf_tab = tk.Frame(self._nb, bg=BG)
        self._nb.add(self._graf_tab, text="  Gráfica Pn  ")
        self._build_graph_tab(self._graf_tab)

        # Tab 3: Comparativa
        self._comp_tab = tk.Frame(self._nb, bg=BG)
        self._nb.add(self._comp_tab, text="  Comparativa  ")
        self._build_comp_tab(self._comp_tab)

    def _build_results_tab(self, parent):
        canvas = tk.Canvas(parent, bg=BG, highlightthickness=0)
        sb = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(canvas, bg=BG)
        win_id = canvas.create_window((0,0), window=inner, anchor="nw")
        def _on_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(win_id, width=e.width)
        canvas.bind("<Configure>", _on_configure)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        self._res_inner = inner
        # tarjetas métricas
        self._metric_cards = {}
        metrics = [
            ("rho", "ρ  Factor de utilización", ACCENT),
            ("P0",  "P₀  Probabilidad sistema vacío", ACCENT2),
            ("L",   "L   Clientes promedio en sistema", PURPLE),
            ("Lq",  "Lq  Clientes promedio en cola", YELLOW),
            ("W",   "W   Tiempo promedio en sistema", GREEN),
            ("Wq",  "Wq  Tiempo promedio en cola", RED),
            ("lambda_ef", "λef  Tasa efectiva de llegada", CYAN),
        ]
        for key, label, color in metrics:
            card = self._make_metric_card(inner, label, "—", color)
            card.pack(fill="x", padx=16, pady=5)
            self._metric_cards[key] = card

        # Extras
        tk.Frame(inner, bg=BORDER, height=1).pack(fill="x", padx=16, pady=8)
        self._extra_frame = tk.Frame(inner, bg=BG)
        self._extra_frame.pack(fill="x", padx=16)

        # Tabla Pn
        tk.Frame(inner, bg=BORDER, height=1).pack(fill="x", padx=16, pady=8)
        tk.Label(inner, text="Probabilidades  P(n)", font=FONT_HEAD,
                 bg=BG, fg=TEXT, anchor="w").pack(fill="x", padx=16)
        self._pn_frame = tk.Frame(inner, bg=BG)
        self._pn_frame.pack(fill="x", padx=16, pady=6)

    def _make_metric_card(self, parent, label, value, color):
        card = tk.Frame(parent, bg=CARD,
                        highlightthickness=1, highlightbackground=BORDER)
        tk.Frame(card, bg=color, width=4).pack(side="left", fill="y")
        info = tk.Frame(card, bg=CARD, padx=14, pady=10)
        info.pack(side="left", fill="both", expand=True)
        tk.Label(info, text=label, font=FONT_SMALL, bg=CARD, fg=TEXT_DIM,
                 anchor="w").pack(fill="x")
        val_lbl = tk.Label(info, text=value, font=("Consolas", 18, "bold"),
                           bg=CARD, fg=color, anchor="w")
        val_lbl.pack(fill="x")
        card._val_lbl = val_lbl
        return card

    def _build_graph_tab(self, parent):
        if not MATPLOTLIB_OK:
            tk.Label(parent, text="matplotlib no disponible.\nInstala: pip install matplotlib numpy",
                     font=FONT_LABEL, bg=BG, fg=RED).pack(expand=True)
            return
        self._fig, self._ax = plt.subplots(figsize=(7,4), facecolor=BG)
        self._ax.set_facecolor(CARD)
        self._canvas_mpl = FigureCanvasTkAgg(self._fig, master=parent)
        self._canvas_mpl.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def _build_comp_tab(self, parent):
        tk.Label(parent, text="Comparativa de métricas entre modelos calculados",
                 font=FONT_SMALL, bg=BG, fg=TEXT_DIM).pack(pady=8)
        cols = ("Modelo", "ρ", "L", "Lq", "W", "Wq", "P0")
        style = ttk.Style()
        style.configure("Dark.Treeview", background=CARD, foreground=TEXT,
                        fieldbackground=CARD, rowheight=28, font=FONT_SMALL,
                        borderwidth=0)
        style.configure("Dark.Treeview.Heading", background=BORDER, foreground=TEXT,
                        font=("Consolas",11,"bold"))
        style.map("Dark.Treeview", background=[("selected", ACCENT2)])
        self._tree = ttk.Treeview(parent, columns=cols, show="headings",
                                  style="Dark.Treeview", height=12)
        for c in cols:
            self._tree.heading(c, text=c)
            self._tree.column(c, width=100, anchor="center")
        self._tree.column("Modelo", width=140, anchor="w")
        sb = ttk.Scrollbar(parent, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y", padx=(0,10), pady=(0,10))
        self._tree.pack(fill="both", expand=True, padx=(10,0), pady=(0,10))
        tk.Button(parent, text="Limpiar historial", font=FONT_SMALL,
                  bg=CARD, fg=TEXT_DIM, bd=0, cursor="hand2",
                  command=lambda: [self._tree.delete(i) for i in self._tree.get_children()]
                  ).pack(pady=4)

    # ── Interacción ──────────────────────────────────────────
    def _select_model(self, nombre):
        self._model_var.set(nombre)
        # Resaltar botón seleccionado
        for n, btn in self._model_btns.items():
            btn.configure(bg=ACCENT2 if n == nombre else CARD,
                          fg=TEXT)
        # Actualizar descripción (guardia por si los labels aún no existen)
        m = MODELOS[nombre]
        if self._lbl_modelo:
            self._lbl_modelo.configure(text=f"  {nombre}  —  {m['desc']}")
        if self._lbl_kendall:
            self._lbl_kendall.configure(text=f"  Kendall: ")#{m['kendall']}
        if self._lbl_detalle:
            self._lbl_detalle.configure(text=f"  {m['detalle']}")
        # Reconstruir parámetros
        for w in self._params_frame.winfo_children():
            w.destroy()
        self._entries = {}
        for item in m["params"]:
            label, key = item[0], item[1]
            row = tk.Frame(self._params_frame, bg=CARD)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label, font=FONT_SMALL, bg=CARD,
                     fg=TEXT_DIM, anchor="w").pack(fill="x")
            e = tk.Entry(row, font=FONT_ENTRY, bg=BG, fg=TEXT,
                         insertbackground=TEXT, relief="flat",
                         highlightthickness=1, highlightbackground=BORDER,
                         highlightcolor=ACCENT2)
            e.pack(fill="x", ipady=6)
            self._entries[key] = e

    def _calcular(self):
        nombre = self._model_var.get()
        m = MODELOS[nombre]
        params = {}
        try:
            for item in m["params"]:
                label, key = item[0], item[1]
                tipo = item[2] if len(item) > 2 else "float"
                raw = self._entries[key].get().strip().replace(",",".")
                params[key] = int(raw) if tipo == "int" else float(raw)
        except ValueError:
            messagebox.showerror("Error de entrada",
                                 "Verifica que todos los campos sean numéricos.")
            return

        resultado, error = m["fn"](params)
        if error:
            messagebox.showerror("Error de cálculo", error)
            return

        self._resultado = resultado
        self._mostrar_resultados(resultado)

    def _mostrar_resultados(self, r):
        # Métricas principales
        fmt = lambda v: f"{v:.6f}"
        self._metric_cards["rho"]._val_lbl.configure(text=f"{r['rho']:.4f}")
        self._metric_cards["P0"]._val_lbl.configure(text=fmt(r["P0"]))
        self._metric_cards["L"]._val_lbl.configure(text=fmt(r["L"]))
        self._metric_cards["Lq"]._val_lbl.configure(text=fmt(r["Lq"]))
        self._metric_cards["W"]._val_lbl.configure(text=fmt(r["W"]))
        self._metric_cards["Wq"]._val_lbl.configure(text=fmt(r["Wq"]))
        self._metric_cards["lambda_ef"]._val_lbl.configure(text=fmt(r["lambda_ef"]))

        # Extras
        for w in self._extra_frame.winfo_children():
            w.destroy()
        if r.get("extra"):
            for k, v in r["extra"].items():
                if isinstance(k, str) and not callable(v):
                    row = tk.Frame(self._extra_frame, bg=BG)
                    row.pack(fill="x", pady=1)
                    tk.Label(row, text=f"{k}:", font=FONT_SMALL, bg=BG,
                             fg=TEXT_DIM, width=28, anchor="w").pack(side="left")
                    tk.Label(row, text=str(v), font=FONT_SMALL, bg=BG,
                             fg=CYAN, anchor="w").pack(side="left")

        # Tabla Pn
        for w in self._pn_frame.winfo_children():
            w.destroy()
        Pn = r.get("Pn_func")
        if Pn:
            N = 15
            header = tk.Frame(self._pn_frame, bg=BORDER)
            header.pack(fill="x")
            for txt, w in [("n", 4), ("P(n)", 14), ("P(N≤n)", 14), ("Barra", 20)]:
                tk.Label(header, text=txt, font=("Consolas",10,"bold"),
                         bg=BORDER, fg=TEXT, width=w, anchor="w").pack(side="left", padx=4, pady=3)
            acum = 0
            for n in range(N+1):
                p = min(Pn(n), 1.0)
                acum = min(acum + p, 1.0)
                bar = "█" * int(p * 30)
                row = tk.Frame(self._pn_frame, bg=CARD if n%2==0 else BG)
                row.pack(fill="x")
                for txt, w in [(str(n), 4), (f"{p:.6f}", 14),
                               (f"{acum:.6f}", 14), (bar, 20)]:
                    tk.Label(row, text=txt, font=FONT_SMALL,
                             bg=row["bg"], fg=ACCENT if n==0 else TEXT,
                             width=w, anchor="w").pack(side="left", padx=4, pady=2)

        # Actualizar gráfica
        self._actualizar_grafica(r)

        # Agregar a comparativa
        self._tree.insert("", "end", values=(
            r["modelo"],
            f"{r['rho']:.4f}", f"{r['L']:.4f}", f"{r['Lq']:.4f}",
            f"{r['W']:.4f}", f"{r['Wq']:.4f}", f"{r['P0']:.4f}"
        ))

    def _actualizar_grafica(self, r):
        if not MATPLOTLIB_OK:
            return
        Pn = r.get("Pn_func")
        if not Pn:
            return
        self._ax.clear()
        N = 20
        ns = list(range(N+1))
        ps = [min(Pn(n), 1.0) for n in ns]
        colors = [ACCENT if n == 0 else ACCENT2 for n in ns]
        bars = self._ax.bar(ns, ps, color=colors, edgecolor=BORDER, linewidth=0.5)
        self._ax.set_facecolor(CARD)
        self._ax.set_title(f"Distribución P(n)  —  {r['modelo']}",
                           color=TEXT, fontsize=11, pad=10)
        self._ax.set_xlabel("n  (número de clientes)", color=TEXT_DIM, fontsize=9)
        self._ax.set_ylabel("P(n)", color=TEXT_DIM, fontsize=9)
        self._ax.tick_params(colors=TEXT_DIM, labelsize=8)
        for spine in self._ax.spines.values():
            spine.set_edgecolor(BORDER)
        self._ax.axhline(y=r["P0"], color=ACCENT, linestyle="--",
                         linewidth=0.8, alpha=0.7, label=f"P₀={r['P0']:.4f}")
        self._ax.legend(facecolor=CARD, edgecolor=BORDER,
                        labelcolor=TEXT, fontsize=8)
        self._fig.patch.set_facecolor(BG)
        self._fig.tight_layout()
        self._canvas_mpl.draw()

    def _limpiar(self):
        for card in self._metric_cards.values():
            card._val_lbl.configure(text="—")
        for w in self._extra_frame.winfo_children():
            w.destroy()
        for w in self._pn_frame.winfo_children():
            w.destroy()
        if MATPLOTLIB_OK:
            self._ax.clear()
            self._canvas_mpl.draw()
        for e in self._entries.values():
            e.delete(0, "end")


# ════════════════════════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = App()
    app.mainloop()
