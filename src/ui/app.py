import tkinter as tk
from tkinter import ttk, messagebox

from src.constants import (
    BG, CARD, ACCENT, ACCENT2, TEXT, TEXT_DIM, BORDER,
    RED, YELLOW, GREEN, PURPLE, CYAN,
    FONT_TITLE, FONT_HEAD, FONT_LABEL, FONT_ENTRY, FONT_SMALL,
)
from src.models.registry import MODELOS

try:
    from version import VERSION_STR, APP_TITLE
except ImportError:
    VERSION_STR = "1.0.0"
    APP_TITLE = "Teoría de Colas - Notación de Kendall"

try:
    import matplotlib
    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import numpy as np
    MATPLOTLIB_OK = True
except ImportError:
    MATPLOTLIB_OK = False


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_TITLE} v{VERSION_STR}")
        self.configure(bg=BG)
        self.geometry("1280x820")
        self.minsize(960, 680)
        self.resizable(True, True)
        self._resultado = None

        self._lbl_modelo  = None
        self._lbl_kendall = None
        self._lbl_detalle = None
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _on_closing(self):
        if MATPLOTLIB_OK:
            try:
                plt.close("all")
            except Exception:
                pass
        self.quit()
        self.destroy()
        import sys
        sys.exit(0)

    # ── Main layout ───────────────────────────────────────────────
    def _build_ui(self):
        hdr = tk.Frame(self, bg=BG, pady=14)
        hdr.pack(fill="x", padx=24)
        tk.Label(hdr, text=" TEORÍA DE COLAS ", font=FONT_TITLE,
                 bg=BG, fg=ACCENT).pack(side="left")
        tk.Label(hdr, text=f"Notación de Kendall v{VERSION_STR}  ",
                 font=FONT_LABEL, bg=BG, fg=TEXT_DIM).pack(side="left", padx=18)

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=18, pady=12)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        left = tk.Frame(body, bg=CARD, bd=0, relief="flat",
                        highlightthickness=1, highlightbackground=BORDER)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left.configure(width=310)
        left.pack_propagate(False)

        right = tk.Frame(body, bg=BG)
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)
        self._build_right(right)

        self._build_left(left)

    # ── Left panel ────────────────────────────────────────────────
    def _build_left(self, parent):
        tk.Label(parent, text="MODELO", font=FONT_HEAD,
                 bg=CARD, fg=ACCENT, pady=14).pack(fill="x", padx=18)
        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x")

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

        tk.Label(parent, text="PARÁMETROS", font=FONT_HEAD,
                 bg=CARD, fg=ACCENT2, pady=10).pack(fill="x", padx=18)

        self._params_frame = tk.Frame(parent, bg=CARD)
        self._params_frame.pack(fill="x", padx=14, pady=4)

        tk.Button(
            parent, text="CALCULAR", font=FONT_HEAD,
            bg=ACCENT, fg=TEXT, bd=0, cursor="hand2",
            activebackground="#2EA043", activeforeground=TEXT,
            pady=10, command=self._calcular
        ).pack(fill="x", padx=14, pady=14)

        tk.Button(
            parent, text="Limpiar", font=FONT_SMALL,
            bg=CARD, fg=TEXT_DIM, bd=0, cursor="hand2",
            activebackground=BORDER, activeforeground=TEXT,
            pady=6, command=self._limpiar
        ).pack(fill="x", padx=14)

        self._select_model(list(MODELOS.keys())[0])

    # ── Right panel ───────────────────────────────────────────────
    def _build_right(self, parent):
        self._desc_frame = tk.Frame(parent, bg=CARD,
                                    highlightthickness=1, highlightbackground=BORDER)
        self._desc_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self._lbl_modelo = tk.Label(self._desc_frame, text="", font=FONT_HEAD,
                                    bg=CARD, fg=TEXT, anchor="w", padx=16, pady=8)
        self._lbl_modelo.pack(fill="x")
        self._lbl_kendall = tk.Label(self._desc_frame, text="", font=FONT_SMALL,
                                     bg=CARD, fg=ACCENT2, anchor="w", padx=16)
        self._lbl_kendall.pack(fill="x")
        self._lbl_detalle = tk.Label(self._desc_frame, text="", font=FONT_SMALL,
                                     bg=CARD, fg=TEXT_DIM, anchor="w", padx=16, pady=6)
        self._lbl_detalle.pack(fill="x")

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

        res_tab = tk.Frame(self._nb, bg=BG)
        self._nb.add(res_tab, text="  Resultados  ")
        self._build_results_tab(res_tab)

        self._graf_tab = tk.Frame(self._nb, bg=BG)
        self._nb.add(self._graf_tab, text="  Gráfica Pn  ")
        self._build_graph_tab(self._graf_tab)

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
        win_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(win_id, width=e.width)

        canvas.bind("<Configure>", _on_configure)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        self._res_inner = inner

        self._metric_cards = {}
        metrics = [
            ("rho",       "ρ  Factor de utilización",          ACCENT),
            ("P0",        "P₀  Probabilidad sistema vacío",     ACCENT2),
            ("L",         "L   Clientes promedio en sistema",   PURPLE),
            ("Lq",        "Lq  Clientes promedio en cola",      YELLOW),
            ("W",         "W   Tiempo promedio en sistema",     GREEN),
            ("Wq",        "Wq  Tiempo promedio en cola",        RED),
            ("lambda_ef", "λef  Tasa efectiva de llegada",      CYAN),
        ]
        for key, label, color in metrics:
            card = self._make_metric_card(inner, label, "—", color)
            card.pack(fill="x", padx=16, pady=5)
            self._metric_cards[key] = card

        tk.Frame(inner, bg=BORDER, height=1).pack(fill="x", padx=16, pady=8)
        self._extra_frame = tk.Frame(inner, bg=BG)
        self._extra_frame.pack(fill="x", padx=16)

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
            tk.Label(parent,
                     text="matplotlib no disponible.\nInstala: pip install matplotlib numpy",
                     font=FONT_LABEL, bg=BG, fg=RED).pack(expand=True)
            return
        self._fig, self._ax = plt.subplots(figsize=(7, 4), facecolor=BG)
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
                        font=("Consolas", 11, "bold"))
        style.map("Dark.Treeview", background=[("selected", ACCENT2)])
        self._tree = ttk.Treeview(parent, columns=cols, show="headings",
                                  style="Dark.Treeview", height=12)
        for c in cols:
            self._tree.heading(c, text=c)
            self._tree.column(c, width=100, anchor="center")
        self._tree.column("Modelo", width=140, anchor="w")
        sb = ttk.Scrollbar(parent, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y", padx=(0, 10), pady=(0, 10))
        self._tree.pack(fill="both", expand=True, padx=(10, 0), pady=(0, 10))
        tk.Button(parent, text="Limpiar historial", font=FONT_SMALL,
                  bg=CARD, fg=TEXT_DIM, bd=0, cursor="hand2",
                  command=lambda: [self._tree.delete(i) for i in self._tree.get_children()]
                  ).pack(pady=4)

    # ── Interaction ───────────────────────────────────────────────
    def _select_model(self, nombre):
        self._model_var.set(nombre)
        for n, btn in self._model_btns.items():
            btn.configure(bg=ACCENT2 if n == nombre else CARD, fg=TEXT)
        m = MODELOS[nombre]
        if self._lbl_modelo:
            self._lbl_modelo.configure(text=f"  {nombre}  —  {m['desc']}")
        if self._lbl_kendall:
            self._lbl_kendall.configure(text=f"  Kendall: {m['kendall']}")
        if self._lbl_detalle:
            self._lbl_detalle.configure(text=f"  {m['detalle']}")
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
                raw = self._entries[key].get().strip().replace(",", ".")
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
        fmt = lambda v: f"{v:.6f}"
        self._metric_cards["rho"]._val_lbl.configure(text=f"{r['rho']:.4f}")
        self._metric_cards["P0"]._val_lbl.configure(text=fmt(r["P0"]))
        self._metric_cards["L"]._val_lbl.configure(text=fmt(r["L"]))
        self._metric_cards["Lq"]._val_lbl.configure(text=fmt(r["Lq"]))
        self._metric_cards["W"]._val_lbl.configure(text=fmt(r["W"]))
        self._metric_cards["Wq"]._val_lbl.configure(text=fmt(r["Wq"]))
        self._metric_cards["lambda_ef"]._val_lbl.configure(text=fmt(r["lambda_ef"]))

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

        for w in self._pn_frame.winfo_children():
            w.destroy()
        Pn = r.get("Pn_func")
        if Pn:
            N = 15
            header = tk.Frame(self._pn_frame, bg=BORDER)
            header.pack(fill="x")
            for txt, w in [("n", 4), ("P(n)", 14), ("P(N≤n)", 14), ("Barra", 20)]:
                tk.Label(header, text=txt, font=("Consolas", 10, "bold"),
                         bg=BORDER, fg=TEXT, width=w, anchor="w").pack(side="left", padx=4, pady=3)
            acum = 0
            for n in range(N + 1):
                p = min(Pn(n), 1.0)
                acum = min(acum + p, 1.0)
                bar = "█" * int(p * 30)
                row = tk.Frame(self._pn_frame, bg=CARD if n % 2 == 0 else BG)
                row.pack(fill="x")
                for txt, w in [(str(n), 4), (f"{p:.6f}", 14),
                               (f"{acum:.6f}", 14), (bar, 20)]:
                    tk.Label(row, text=txt, font=FONT_SMALL,
                             bg=row["bg"], fg=ACCENT if n == 0 else TEXT,
                             width=w, anchor="w").pack(side="left", padx=4, pady=2)

        self._actualizar_grafica(r)

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
        N  = 20
        ns = list(range(N + 1))
        ps = [min(Pn(n), 1.0) for n in ns]
        colors = [ACCENT if n == 0 else ACCENT2 for n in ns]
        self._ax.bar(ns, ps, color=colors, edgecolor=BORDER, linewidth=0.5)
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
        self._ax.legend(facecolor=CARD, edgecolor=BORDER, labelcolor=TEXT, fontsize=8)
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
