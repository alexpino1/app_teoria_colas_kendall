"""
PAPI COLAS — Teoría de Colas (PyQt6)
Editorial magazine aesthetic · Negro · Crema · Magenta
"""

import math
import os

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QLineEdit, QTabWidget,
    QScrollArea, QFrame, QSizePolicy, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPainter, QPen, QFontMetrics, QIcon

from src.models.registry import MODELOS

try:
    from version import VERSION_STR
except ImportError:
    VERSION_STR = "2.0"

import sys

def get_resource_path(relative_path):
    """Obtiene la ruta absoluta a un recurso, funciona en dev y en PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base_path, relative_path)

try:
    import matplotlib
    matplotlib.use("QtAgg")
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
    from matplotlib.figure import Figure
    MATPLOTLIB_OK = True
except Exception:
    MATPLOTLIB_OK = False

# ─── Design tokens ───────────────────────────────────────────────────────────
PAPER  = "#f0e7d8"
PAPER2 = "#e3d6c0"
INK    = "#14110f"
INK_S  = "#2b2724"
HOT    = "#ff2e6e"
GOLD   = "#d4a437"
MUTE   = "#8b827a"

F_DISP = "Impact"
F_SER  = "Georgia"
F_MONO = "Consolas"
F_SANS = "Segoe UI"

N_MAX = 25


# ─── Helpers ─────────────────────────────────────────────────────────────────
def _fmt(v, d=4):
    if v is None:
        return "—"
    try:
        f = float(v)
        if not math.isfinite(f):
            return "∞"
        return f"{f:.{d}f}"
    except Exception:
        return "—"


def _pn_list(result):
    fn = result.get("Pn_func")
    if not callable(fn):
        return []
    out = []
    for i in range(N_MAX + 1):
        try:
            out.append(min(float(fn(i)), 1.0))
        except Exception:
            out.append(0.0)
    return out


def _qlabel(text, size=10, bold=False, italic=False, color=INK, family=F_MONO):
    w = QLabel(text)
    f = QFont(family, size)
    if bold:
        f.setWeight(QFont.Weight.Bold)
    if italic:
        f.setItalic(True)
    w.setFont(f)
    w.setStyleSheet(f"color: {color}; background: transparent;")
    return w


# ─── Marquee ─────────────────────────────────────────────────────────────────
_MSEGS = [
    "  Teoría de Colas  ", "  Notación de Kendall  ",
    "  M/M/1 · M/M/c · M/D/1 · M/G/1 · M/Ek/1 · M/M/∞  ",
    "  Papi Colas Edition  ", "  ρ = λ/μ  ",
    "  Little's Law: L = λW  ", "  Pollaczek-Khinchine  ",
]


class Marquee(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._font = QFont(F_DISP, 16)
        self._off = 0
        fm = QFontMetrics(self._font)
        star_w = fm.horizontalAdvance("★")
        text_w = sum(fm.horizontalAdvance(s) for s in _MSEGS)
        self._full_w = text_w + star_w * len(_MSEGS)
        self.setFixedHeight(52)
        t = QTimer(self, interval=20)
        t.timeout.connect(self._tick)
        t.start()

    def _tick(self):
        self._off -= 2
        if self._off < -self._full_w:
            self._off = 0
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        p.fillRect(self.rect(), QColor(INK))
        p.setPen(QPen(QColor(HOT), 1))
        p.drawLine(0, 0, self.width(), 0)
        p.setFont(self._font)
        fm = p.fontMetrics()
        y = (self.height() + fm.ascent() - fm.descent()) // 2 + 2
        x = self._off
        while x < self.width():
            dx = x
            for seg in _MSEGS:
                p.setPen(QColor(PAPER2))
                p.drawText(int(dx), y, seg)
                dx += fm.horizontalAdvance(seg)
                p.setPen(QColor(HOT))
                p.drawText(int(dx), y, "★")
                dx += fm.horizontalAdvance("★")
            x += self._full_w
        p.end()


# ─── Masthead bar ────────────────────────────────────────────────────────────
class MastheadBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(52)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Content row
        content = QWidget()
        content.setStyleSheet(f"background-color: {INK};")
        row = QHBoxLayout(content)
        row.setContentsMargins(200, 0, 200, 0)
        row.setSpacing(32)

        brand = QLabel()
        brand.setTextFormat(Qt.TextFormat.RichText)
        brand.setStyleSheet(f"background-color: {INK};")
        brand.setText(
            f'<span style="font-family:{F_DISP}; font-size:20px; '
            f'color:{HOT}; letter-spacing:4px;">PAPI COLAS</span>'
        )
        row.addWidget(brand)

        rule = QFrame()
        rule.setFrameShape(QFrame.Shape.HLine)
        rule.setStyleSheet(f"background: {PAPER2}; border: none; max-height:1px;")
        row.addWidget(rule, stretch=1)

        ver = _qlabel(f"NOTACIÓN DE KENDALL · v{VERSION_STR}", 10, color=HOT)
        ver.setStyleSheet(f"color: {HOT}; background-color: {INK};")
        row.addWidget(ver)

        outer.addWidget(content, stretch=1)

        # Bottom border as a full-width widget — always on top of content
        border = QFrame()
        border.setFixedHeight(2)
        border.setStyleSheet(f"background-color: {HOT}; border: none;")
        outer.addWidget(border)

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(INK))
        p.end()


# ─── Rail (left dark panel) ──────────────────────────────────────────────────
class RailPanel(QWidget):
    """Model selector + parameter inputs + action buttons."""

    model_selected = pyqtSignal(str)
    calc_clicked   = pyqtSignal()
    clear_clicked  = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            f"background-color: {INK}; border-right: 1px solid {HOT};"
        )
        self.setMinimumWidth(220)
        self.setMaximumWidth(310)

        self._model_name = list(MODELOS.keys())[0]
        self._model_btns: dict[str, QPushButton] = {}
        self._entries:    dict[str, QLineEdit]   = {}
        self._params_container: QWidget | None   = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(
            f"QScrollArea {{ background: {INK}; border: none; }}"
            f"QScrollBar:vertical {{ background: {INK_S}; width:6px; }}"
            f"QScrollBar::handle:vertical {{ background: {MUTE}; border-radius:3px; }}"
        )
        outer.addWidget(scroll)

        inner = QWidget()
        inner.setStyleSheet(f"background: {INK};")
        scroll.setWidget(inner)

        self._lay = QVBoxLayout(inner)
        self._lay.setContentsMargins(26, 28, 26, 28)
        self._lay.setSpacing(0)

        self._build_model_section()
        self._lay.addSpacing(24)
        self._build_params_section()
        self._lay.addSpacing(20)
        self._build_actions()
        self._lay.addStretch()

        self._select_model(self._model_name)

    # ── Section header
    def _sec_hdr(self, text):
        lbl = QLabel(text)
        lbl.setFont(QFont(F_MONO, 10))
        lbl.setStyleSheet(
            f"color: {HOT}; background: transparent; "
            f"letter-spacing: 3px; margin-bottom: 12px;"
        )
        return lbl

    # ── Model buttons section
    def _build_model_section(self):
        self._lay.addWidget(self._sec_hdr("★  MODELO"))
        grid = QGridLayout()
        grid.setSpacing(6)
        names = list(MODELOS.keys())
        for i, name in enumerate(names):
            btn = QPushButton(name)
            btn.setFont(QFont(F_MONO, 11))
            btn.setStyleSheet(self._btn_style(False))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, n=name: self._select_model(n))
            btn.setFixedHeight(40)
            grid.addWidget(btn, i // 2, i % 2)
            self._model_btns[name] = btn
        self._lay.addLayout(grid)

    def _btn_style(self, active: bool) -> str:
        if active:
            return (
                f"QPushButton {{ background: {HOT}; color: {INK}; "
                f"border: 1px solid {HOT}; font-family: {F_MONO}; "
                f"font-weight: bold; padding: 8px; }}"
            )
        return (
            f"QPushButton {{ background: transparent; "
            f"color: {PAPER}; border: 1px solid rgba(240,231,216,0.2); "
            f"font-family: {F_MONO}; padding: 8px; }}"
            f"QPushButton:hover {{ border-color: {HOT}; color: {HOT}; }}"
        )

    # ── Params section
    def _build_params_section(self):
        self._lay.addWidget(self._sec_hdr("★  PARÁMETROS"))
        self._params_container = QWidget()
        self._params_container.setStyleSheet(f"background: {INK};")
        self._params_lay = QVBoxLayout(self._params_container)
        self._params_lay.setContentsMargins(0, 0, 0, 0)
        self._params_lay.setSpacing(16)
        self._lay.addWidget(self._params_container)

    # ── Actions
    def _build_actions(self):
        calc_btn = QPushButton("✦  CALCULAR")
        calc_btn.setFont(QFont(F_DISP, 13))
        calc_btn.setFixedHeight(52)
        calc_btn.setStyleSheet(
            f"QPushButton {{ background: {HOT}; color: {INK}; border: none; "
            f"letter-spacing: 3px; }}"
            f"QPushButton:hover {{ background: #fff; }}"
        )
        calc_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        calc_btn.clicked.connect(self.calc_clicked)
        self._lay.addWidget(calc_btn)

        self._lay.addSpacing(8)

        clr_btn = QPushButton("Limpiar")
        clr_btn.setFont(QFont(F_MONO, 11))
        clr_btn.setFixedHeight(38)
        clr_btn.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {MUTE}; "
            f"border: 1px solid rgba(240,231,216,0.2); }}"
            f"QPushButton:hover {{ border-color: {HOT}; color: {HOT}; }}"
        )
        clr_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clr_btn.clicked.connect(self.clear_clicked)
        self._lay.addWidget(clr_btn)

    # ── Model selection
    def _select_model(self, name: str):
        self._model_name = name
        for n, btn in self._model_btns.items():
            btn.setStyleSheet(self._btn_style(n == name))

        for i in reversed(range(self._params_lay.count())):
            w = self._params_lay.itemAt(i).widget()
            if w:
                w.setParent(None)

        self._entries.clear()
        m = MODELOS[name]
        for item in m["params"]:
            label_text, key = item[0], item[1]
            row = QWidget()
            row.setStyleSheet(f"background: {INK};")
            rl = QVBoxLayout(row)
            rl.setContentsMargins(0, 0, 0, 0)
            rl.setSpacing(4)

            lbl = QLabel(label_text.strip())
            lbl.setFont(QFont(F_MONO, 9))
            lbl.setStyleSheet(
                f"color: {PAPER2}; background: transparent; "
                f"letter-spacing: 1px;"
            )
            rl.addWidget(lbl)

            entry = QLineEdit()
            entry.setFont(QFont(F_DISP, 22))
            entry.setStyleSheet(
                f"QLineEdit {{ background: transparent; color: {PAPER}; "
                f"border: none; border-bottom: 1px solid {PAPER2}; "
                f"padding-bottom: 4px; }}"
                f"QLineEdit:focus {{ border-bottom: 2px solid {HOT}; }}"
            )
            self._entries[key] = entry
            rl.addWidget(entry)

            self._params_lay.addWidget(row)

        self.model_selected.emit(name)

    def get_params(self) -> tuple[dict, str | None]:
        m = MODELOS[self._model_name]
        params = {}
        for item in m["params"]:
            label_text, key = item[0], item[1]
            tipo = item[2] if len(item) > 2 else "float"
            raw = self._entries[key].get() if hasattr(self._entries[key], "get") \
                  else self._entries[key].text().strip().replace(",", ".")
            if not raw:
                return {}, f"El campo '{label_text.strip()}' está vacío."
            try:
                params[key] = int(raw) if tipo == "int" else float(raw)
            except ValueError:
                return {}, f"'{raw}' no es un número válido en '{label_text.strip()}'."
        return params, None

    def clear_entries(self):
        for e in self._entries.values():
            e.clear()

    @property
    def current_model(self) -> str:
        return self._model_name


# ─── Portrait placeholder ────────────────────────────────────────────────────
class PortraitArea(QWidget):
    """Dark gradient area that shows the model number in large serif italic."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._num = "01"
        self._tag = "M/M/1"
        self.setMinimumHeight(280)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

    def set_model(self, index: int, label: str):
        self._num = f"{index:02d}"
        self._tag = label
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        # Dark gradient background
        grad = p.drawRect  # placeholder; use fillRect with solid color
        p.fillRect(self.rect(), QColor(INK_S))

        # Large number watermark
        f_big = QFont(F_SER, 160)
        f_big.setItalic(True)
        f_big.setWeight(QFont.Weight.Black)
        p.setFont(f_big)
        p.setPen(QColor(HOT))
        fm = QFontMetrics(f_big)
        num_w = fm.horizontalAdvance(f"N°{self._num}")
        p.drawText(
            self.width() - num_w - 10, fm.ascent() - 20, f"N°{self._num}"
        )

        # Overlay gradient (bottom fade)
        p.fillRect(
            0, self.height() - 80, self.width(), 80,
            QColor(10, 9, 8, 150)
        )

        # Tag label (bottom left)
        f_tag = QFont(F_MONO, 10)
        p.setFont(f_tag)
        p.setPen(QColor(INK))
        tag_rect_h = 28
        p.fillRect(14, self.height() - 14 - tag_rect_h,
                   QFontMetrics(f_tag).horizontalAdvance(f"Featured · {self._tag}") + 20,
                   tag_rect_h, QColor(HOT))
        p.drawText(
            24, self.height() - 14 - tag_rect_h + 18,
            f"Featured · {self._tag}"
        )
        p.end()


# ─── Stage (center panel) ────────────────────────────────────────────────────
class StagePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {PAPER};")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(40, 36, 40, 24)
        lay.setSpacing(0)

        # Stage top bar
        top = QHBoxLayout()
        self._lbl_kicker = _qlabel("● Cover Story", 10, color=INK_S)
        self._lbl_edition = _qlabel("Edición · M/M/1", 10, color=INK_S)
        top.addWidget(self._lbl_kicker)
        top.addStretch()
        top.addWidget(self._lbl_edition)
        lay.addLayout(top)
        lay.addSpacing(14)

        # Headline
        self._headline = QLabel()
        self._headline.setTextFormat(Qt.TextFormat.RichText)
        self._headline.setWordWrap(True)
        self._headline.setFont(QFont(F_SER, 64))
        self._headline.setStyleSheet(
            f"color: {INK}; background: transparent; line-height: 0.88;"
        )
        lay.addWidget(self._headline)
        lay.addSpacing(22)

        # Portrait
        self._portrait = PortraitArea()
        lay.addWidget(self._portrait, stretch=1)
        lay.addSpacing(14)

        # Kendall strip
        strip_line = QFrame()
        strip_line.setFrameShape(QFrame.Shape.HLine)
        strip_line.setStyleSheet(f"background: {INK}; border: none; max-height:1px;")
        lay.addWidget(strip_line)
        lay.addSpacing(10)

        strip_row = QHBoxLayout()
        self._lbl_kendall_label = _qlabel("Notación de Kendall", 11, color=INK_S)
        self._lbl_kendall_value = _qlabel("M/M/1/∞/∞/FCFS", 11, bold=True, color=HOT)
        strip_row.addWidget(self._lbl_kendall_label)
        strip_row.addStretch()
        strip_row.addWidget(self._lbl_kendall_value)
        lay.addLayout(strip_row)

        self.update_model("M/M/1", 0)

    _KICKERS = {
        "M/M/1":   ("Cover Story",       "Un servidor,<br><i style='color:{h}'>mil corazones.</i>"),
        "M/M/c":   ("Tour Mundial",       "Equipo de<br><i style='color:{h}'><b>c</b> servidores.</i>"),
        "M/D/1":   ("Determinista",        "Tiempo fijo,<br><i style='color:{h}'>swing exacto.</i>"),
        "M/G/1":   ("Servicio General",    "Una varianza<br><i style='color:{h}'>que enamora.</i>"),
        "M/Ek/1":  ("Erlang",              "k fases,<br><i style='color:{h}'>un solo flow.</i>"),
        "M/M/∞":   ("Sin Límite",          "Servidores<br><i style='color:{h}'>infinitos.</i>"),
    }

    def update_model(self, model_name: str, model_index: int):
        kicker, headline_tpl = self._KICKERS.get(
            model_name,
            ("Modelo", f"<i style='color:{HOT}'>{model_name}</i>")
        )
        headline_html = headline_tpl.format(h=HOT)
        m = MODELOS[model_name]

        self._lbl_kicker.setText(f"●  {kicker}")
        self._lbl_edition.setText(f"Edición · {model_name}")
        self._headline.setText(
            f'<span style="font-family:{F_SER}; font-size:64px; '
            f'font-weight:900; font-style:italic; color:{INK};">'
            f'{headline_html}</span>'
            f'<br><span style="font-family:{F_SANS}; font-size:14px; '
            f'font-weight:900; color:{INK_S}; letter-spacing:3px;">'
            f'{m["desc"].upper()}</span>'
        )
        self._portrait.set_model(model_index + 1, model_name)
        self._lbl_kendall_value.setText(m.get("detalle", m.get("kendall", "")))


# ─── Feature (right dark panel) ──────────────────────────────────────────────
class FeaturePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(200)
        self.setMaximumWidth(300)
        self.setStyleSheet(f"background-color: {INK}; color: #ffffff;")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(26, 28, 26, 28)
        lay.setSpacing(0)

        eyebrow = _qlabel("★  MÉTRICA DEL MOMENTO", 9, color=HOT)
        eyebrow.setStyleSheet(f"color: {HOT}; background-color: {INK};")
        lay.addWidget(eyebrow)
        lay.addSpacing(14)

        # Big ρ value — RichText so inline color is immune to Qt cascade
        self._big_val = QLabel()
        self._big_val.setTextFormat(Qt.TextFormat.RichText)
        self._big_val.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self._big_val.setStyleSheet(f"background-color: {INK};")
        self._set_big("—")
        lay.addWidget(self._big_val)

        rho_tag = _qlabel("ρ  (factor de utilización)", 10, color=HOT)
        rho_tag.setStyleSheet(f"color: {HOT}; background-color: {INK};")
        lay.addWidget(rho_tag)
        lay.addSpacing(12)

        # Blurb — also RichText for reliable color
        self._blurb = QLabel()
        self._blurb.setTextFormat(Qt.TextFormat.RichText)
        self._blurb.setWordWrap(True)
        self._blurb.setStyleSheet(f"background-color: {INK};")
        self._set_blurb("Ingresa los parámetros<br>y dale a Calcular.")
        lay.addWidget(self._blurb)
        lay.addSpacing(22)

        # Divider
        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setStyleSheet(f"background: rgba(240,231,216,0.18); border: none; max-height:1px;")
        lay.addWidget(div)
        lay.addSpacing(18)

        # Ticker grid
        self._tick_grid = QGridLayout()
        self._tick_grid.setSpacing(14)
        tick_defs = [
            ("L · sistema", "L",   True),
            ("Lq · cola",   "Lq",  False),
            ("W",           "W",   False),
            ("Wq",          "Wq",  False),
            ("P₀",          "P0",  False),
            ("λef",         "lef", False),
        ]
        self._tick_vals: dict[str, QLabel] = {}
        for i, (lbl_txt, key, hot) in enumerate(tick_defs):
            cell = QWidget()
            cell.setStyleSheet(f"background: {INK};")
            cl = QVBoxLayout(cell)
            cl.setContentsMargins(0, 0, 0, 0)
            cl.setSpacing(2)
            lbl = _qlabel(lbl_txt, 9, color=MUTE)
            lbl.setStyleSheet(f"color: {MUTE}; background: transparent; letter-spacing: 1px;")
            val = QLabel("—")
            val.setFont(QFont(F_DISP, 20))
            val.setStyleSheet(
                f"color: {HOT if hot else PAPER}; background: transparent;"
            )
            cl.addWidget(lbl)
            cl.addWidget(val)
            self._tick_vals[key] = val
            self._tick_grid.addWidget(cell, i // 2, i % 2)

        lay.addLayout(self._tick_grid)
        lay.addStretch()

        # Unstable warning (hidden by default)
        self._warn = QLabel("⚠  ρ ≥ 1 — Sistema inestable.\nLa cola crece sin límite.")
        self._warn.setFont(QFont(F_MONO, 10))
        self._warn.setStyleSheet(
            f"background: {HOT}; color: {INK}; padding: 10px; "
            f"border-radius: 0px; line-height: 1.4;"
        )
        self._warn.setWordWrap(True)
        self._warn.hide()
        lay.addWidget(self._warn)

    # paintEvent guarantees INK background regardless of Qt stylesheet cascade
    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(INK))
        p.end()

    def _set_big(self, text: str):
        self._big_val.setText(
            f'<span style="font-family:{F_SER}; font-size:78px; '
            f'font-style:italic; font-weight:900; color:#ffffff;">{text}</span>'
        )

    def _set_blurb(self, html: str):
        self._blurb.setText(
            f'<span style="font-family:{F_SER}; font-size:13px; '
            f'font-style:italic; color:#d6cfc4;">{html}</span>'
        )

    def update_result(self, result: dict | None):
        if result is None:
            self._set_big("—")
            self._set_blurb("Ingresa los parámetros<br>y dale a Calcular.")
            for lbl in self._tick_vals.values():
                lbl.setText("—")
            self._warn.hide()
            return

        rho = result.get("rho", 0)
        self._set_big(_fmt(rho, 2))

        pct = min(100, rho * 100) if math.isfinite(rho) else None
        if result.get("unstable"):
            blurb = "El sistema se sobresatura.<br>Necesitas más servidores<br>o servir más rápido."
        elif pct is not None and pct < 50:
            blurb = f"Servidor relajado,<br>trabajando al {pct:.0f}%<br>de su capacidad."
        elif pct is not None and pct < 80:
            blurb = f"Servidor en ritmo:<br>{pct:.0f}% ocupado,<br>fila controlable."
        elif pct is not None:
            blurb = f"Servidor al límite<br>({pct:.0f}%). Cualquier<br>pico colapsa la cola."
        else:
            blurb = "—"

        self._set_blurb(blurb)
        self._tick_vals["L"].setText(_fmt(result.get("L"), 3))
        self._tick_vals["Lq"].setText(_fmt(result.get("Lq"), 3))
        self._tick_vals["W"].setText(_fmt(result.get("W"), 3))
        self._tick_vals["Wq"].setText(_fmt(result.get("Wq"), 3))
        self._tick_vals["P0"].setText(_fmt(result.get("P0"), 4))
        self._tick_vals["lef"].setText(_fmt(result.get("lambda_ef"), 3))

        if result.get("unstable"):
            self._warn.show()
        else:
            self._warn.hide()


# ─── Cover (3-column layout) ─────────────────────────────────────────────────
class CoverWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {PAPER};")

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.rail    = RailPanel()
        self.stage   = StagePanel()
        self.feature = FeaturePanel()

        lay.addWidget(self.rail,    stretch=105)
        lay.addWidget(self.stage,   stretch=140)
        lay.addWidget(self.feature, stretch=95)


# ─── Metric card (results tab) ───────────────────────────────────────────────
class MetricCard(QFrame):
    def __init__(self, sym: str, label: str, help_text: str = "",
                 accent=False, dark=False, parent=None):
        super().__init__(parent)
        bg = INK if dark else PAPER
        self.setStyleSheet(
            f"background: {bg};"
            f"border-top: 2px solid {HOT if dark else INK};"
        )
        self.setMinimumHeight(80)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 8, 10, 8)
        lay.setSpacing(2)

        lbl_row = QLabel()
        lbl_row.setTextFormat(Qt.TextFormat.RichText)
        lbl_row.setText(
            f'<span style="font-family:{F_SER}; font-style:italic; '
            f'font-size:12px; color:{HOT};">{sym} </span>'
            f'<span style="font-family:{F_MONO}; font-size:9px; '
            f'letter-spacing:2px; color:{"" + PAPER2 if dark else INK_S};">'
            f'{label.upper()}</span>'
        )
        lay.addWidget(lbl_row)

        num_color = HOT if accent else (PAPER if dark else INK)
        self._val = QLabel("—")
        _f_val = QFont(F_SER, 26)
        _f_val.setItalic(True)
        _f_val.setWeight(QFont.Weight.Black)
        self._val.setFont(_f_val)
        self._val.setStyleSheet(f"color: {num_color}; background: transparent;")
        lay.addWidget(self._val)

    def set_value(self, v: str):
        self._val.setText(v)


# ─── P(n) probability table ──────────────────────────────────────────────────
class PnTableWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {PAPER};")
        self._lay = QVBoxLayout(self)
        self._lay.setContentsMargins(0, 0, 0, 0)
        self._lay.setSpacing(0)

    def load(self, pn: list[float]):
        for i in reversed(range(self._lay.count())):
            item = self._lay.itemAt(i)
            if item and item.widget():
                item.widget().setParent(None)

        if not pn:
            return

        # Header
        hdr = QWidget()
        hdr.setStyleSheet(f"background: {PAPER2};")
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(14, 8, 14, 8)
        for txt, w_pct in [("n", 8), ("P(n)", 20), ("P(N≤n)", 20), ("Barra", 52)]:
            lh = QLabel(txt.upper())
            lh.setFont(QFont(F_MONO, 9))
            lh.setStyleSheet(f"color: {INK_S}; background: transparent; letter-spacing: 2px;")
            lh.setFixedWidth(int(self.width() * w_pct / 100) if self.width() > 0 else 80)
            hl.addWidget(lh)
        self._lay.addWidget(hdr)

        cum = 0.0
        max_p = max(pn) if pn else 1.0
        if max_p == 0:
            max_p = 1.0

        for n, p in enumerate(pn[:16]):
            cum = min(cum + p, 1.0)
            row = QWidget()
            row.setStyleSheet(f"background: {PAPER2 if n % 2 == 0 else PAPER};")
            rl = QHBoxLayout(row)
            rl.setContentsMargins(14, 8, 14, 8)
            rl.setSpacing(0)

            def _cell(txt, color=INK, w=80):
                lbl = QLabel(txt)
                lbl.setFont(QFont(F_MONO, 11))
                lbl.setStyleSheet(f"color: {color}; background: transparent;")
                lbl.setMinimumWidth(w)
                return lbl

            rl.addWidget(_cell(str(n), HOT, 50))
            rl.addWidget(_cell(f"{p:.6f}", INK, 110))
            rl.addWidget(_cell(f"{cum:.6f}", INK, 110))

            # Bar
            bar_container = QWidget()
            bar_container.setStyleSheet("background: transparent;")
            bar_container.setFixedHeight(14)
            bar_container.setMinimumWidth(100)

            bar_pct = p / max_p

            class BarWidget(QWidget):
                def __init__(self, pct, parent=None):
                    super().__init__(parent)
                    self._pct = pct
                    self.setFixedHeight(14)
                def paintEvent(self, _):
                    pp = QPainter(self)
                    pp.fillRect(self.rect(), QColor(PAPER2))
                    w = int(self.width() * self._pct)
                    pp.fillRect(0, 0, w, self.height(), QColor(HOT))
                    pp.end()

            bw = BarWidget(bar_pct)
            bw.setMinimumWidth(80)
            rl.addWidget(bw, stretch=1)
            rl.addSpacing(14)

            self._lay.addWidget(row)


# ─── Results tab ─────────────────────────────────────────────────────────────
class ResultsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {PAPER};")

        self._lay = QVBoxLayout(self)
        self._lay.setContentsMargins(0, 0, 0, 0)
        self._lay.setSpacing(0)

        cards_data = [
            ("ρ",   "Factor de utilización",  "", True,  False),
            ("P₀",  "Prob. sistema vacío",    "", False, False),
            ("L",   "Clientes en sistema",    "", False, True),
            ("Lq",  "Clientes en cola",       "", False, False),
            ("W",   "Tiempo en sistema",      "", False, False),
            ("Wq",  "Tiempo en cola",         "", True,  False),
            ("λef", "Tasa efectiva",          "", False, False),
            ("P_K", "Prob. rechazo / carga",  "", False, True),
        ]

        self._cards: dict[str, MetricCard] = {}
        grid_widget = QWidget()
        grid_widget.setStyleSheet(f"background: {PAPER};")
        grid = QGridLayout(grid_widget)
        grid.setSpacing(4)
        grid.setContentsMargins(0, 0, 0, 0)

        keys = ["rho", "P0", "L", "Lq", "W", "Wq", "lef", "PK"]
        for i, (sym, lbl, hlp, acc, drk) in enumerate(cards_data):
            card = MetricCard(sym, lbl, hlp, accent=acc, dark=drk)
            grid.addWidget(card, i // 4, i % 4)
            self._cards[keys[i]] = card

        self._lay.addWidget(grid_widget)
        self._lay.addStretch()

        # P(n) table kept as attribute for update_result but not shown here
        self._pn_table = PnTableWidget()

        self._empty = QLabel("Dale a Calcular para ver el espectáculo.")
        _f_emp = QFont(F_SER, 18)
        _f_emp.setItalic(True)
        self._empty.setFont(_f_emp)
        self._empty.setStyleSheet(
            f"color: {INK_S}; border: 1px dashed {INK}; "
            f"padding: 40px; background: {PAPER};"
        )
        self._empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lay.insertWidget(0, self._empty)
        grid_widget.hide()

        self._grid_widget = grid_widget

    def update_result(self, result: dict | None):
        if result is None:
            self._empty.show()
            self._grid_widget.hide()
            for c in self._cards.values():
                c.set_value("—")
            self._pn_table.load([])
            return

        self._empty.hide()
        self._grid_widget.show()

        self._cards["rho"].set_value(_fmt(result.get("rho"), 4))
        self._cards["P0"].set_value(_fmt(result.get("P0"), 4))
        self._cards["L"].set_value(_fmt(result.get("L"), 3))
        self._cards["Lq"].set_value(_fmt(result.get("Lq"), 3))
        self._cards["W"].set_value(_fmt(result.get("W"), 3))
        self._cards["Wq"].set_value(_fmt(result.get("Wq"), 3))
        self._cards["lef"].set_value(_fmt(result.get("lambda_ef"), 3))

        pk = result.get("PK")
        self._cards["PK"].set_value(_fmt(pk, 4) if pk is not None else _fmt(result.get("rho"), 4))

        pn = _pn_list(result)
        self._pn_table.load(pn)


# ─── Chart tab ───────────────────────────────────────────────────────────────
class ChartTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {PAPER};")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        if not MATPLOTLIB_OK:
            lbl = QLabel("matplotlib no disponible.\nInstala: pip install matplotlib numpy")
            lbl.setFont(QFont(F_MONO, 12))
            lbl.setStyleSheet(f"color: {HOT}; padding: 40px; background: {INK};")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lay.addWidget(lbl)
            self._canvas = None
            return

        wrap = QWidget()
        wrap.setStyleSheet(f"background: {INK};")
        wl = QVBoxLayout(wrap)
        wl.setContentsMargins(36, 32, 36, 28)
        wl.setSpacing(0)

        head_row = QHBoxLayout()
        self._chart_title = QLabel("P(n) · Distribución")
        _f_ct = QFont(F_SER, 28)
        _f_ct.setItalic(True)
        _f_ct.setWeight(QFont.Weight.Black)
        self._chart_title.setFont(_f_ct)
        self._chart_title.setStyleSheet(f"color: {PAPER}; background: transparent;")
        self._chart_meta = _qlabel("M/M/1 · ρ = —", 11, color=HOT)
        head_row.addWidget(self._chart_title)
        head_row.addStretch()
        head_row.addWidget(self._chart_meta)
        wl.addLayout(head_row)
        wl.addSpacing(18)

        self._fig = Figure(figsize=(10, 4), facecolor=INK)
        self._ax = self._fig.add_subplot(111)
        self._ax.set_facecolor(INK_S)
        self._canvas = FigureCanvasQTAgg(self._fig)
        self._canvas.setStyleSheet(f"background: {INK};")
        wl.addWidget(self._canvas)

        caption = QLabel(
            '"El estado vacío (P₀) marca el ritmo. Cada barra es la probabilidad '
            'de encontrar exactamente n clientes simultáneos en el sistema."'
        )
        caption.setFont(QFont(F_SER, 13))
        caption.setStyleSheet(
            f"color: {PAPER2}; background: transparent; font-style: italic; "
            f"padding-top: 14px; border-top: 1px solid rgba(240,231,216,0.15);"
        )
        caption.setWordWrap(True)
        wl.addSpacing(14)
        wl.addWidget(caption)

        lay.addWidget(wrap)

        self._empty = QLabel("Calcula primero para graficar.")
        _f_ce = QFont(F_SER, 22)
        _f_ce.setItalic(True)
        self._empty.setFont(_f_ce)
        self._empty.setStyleSheet(
            f"color: {INK_S}; border: 1px dashed {INK}; "
            f"padding: 80px; background: {PAPER};"
        )
        self._empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.insertWidget(0, self._empty)
        wrap.hide()
        self._wrap = wrap

    def update_result(self, result: dict | None, model_name: str = ""):
        if not MATPLOTLIB_OK or self._canvas is None:
            return
        if result is None:
            self._empty.show()
            self._wrap.hide()
            return

        pn = _pn_list(result)
        if not pn:
            self._empty.show()
            self._wrap.hide()
            return

        self._empty.hide()
        self._wrap.show()

        self._chart_title.setText("P(n) · Distribución")
        self._chart_meta.setText(f"{model_name} · ρ = {_fmt(result.get('rho'), 3)}")

        self._ax.clear()
        self._ax.set_facecolor(INK_S)
        colors = [GOLD if i == 0 else HOT for i in range(len(pn))]
        self._ax.bar(range(len(pn)), pn, color=colors, edgecolor="none", width=0.7)

        p0 = result.get("P0")
        max_p = max(pn) if pn else 1
        if p0 and math.isfinite(p0) and max_p > 0:
            self._ax.axhline(y=p0, color=GOLD, linestyle="--",
                             linewidth=1.2, alpha=0.8, label=f"P₀ = {p0:.4f}")
            self._ax.legend(facecolor=INK, edgecolor=INK_S,
                           labelcolor=PAPER2, fontsize=9)

        self._ax.set_title(f"Distribución P(n) — {model_name}",
                          color=PAPER, fontsize=11, pad=10)
        self._ax.set_xlabel("n  (número de clientes)", color=PAPER2, fontsize=9)
        self._ax.set_ylabel("P(n)", color=PAPER2, fontsize=9)
        self._ax.tick_params(colors=PAPER2, labelsize=8)
        for spine in self._ax.spines.values():
            spine.set_edgecolor(INK_S)
        self._fig.patch.set_facecolor(INK)
        self._fig.tight_layout()
        self._canvas.draw()


# ─── Compare tab ─────────────────────────────────────────────────────────────
class CompareTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {PAPER};")
        self._saved: list[dict] = []

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # Header row
        head = QWidget()
        head.setStyleSheet(f"background: {PAPER};")
        hl = QHBoxLayout(head)
        hl.setContentsMargins(0, 0, 0, 18)

        title = QLabel()
        title.setTextFormat(Qt.TextFormat.RichText)
        title.setText(
            f'<span style="font-family:{F_SER}; font-style:italic; '
            f'font-weight:900; font-size:36px; color:{INK};">La </span>'
            f'<span style="font-family:{F_SER}; font-style:italic; '
            f'font-weight:900; font-size:36px; color:{HOT};">Comparativa</span>'
        )
        hl.addWidget(title)
        hl.addStretch()

        clr_btn = QPushButton("VACIAR")
        clr_btn.setFont(QFont(F_MONO, 10))
        clr_btn.setStyleSheet(
            f"QPushButton {{ background: {INK}; color: {PAPER}; border: none; "
            f"padding: 10px 14px; letter-spacing: 2px; }}"
            f"QPushButton:hover {{ background: {HOT}; color: {INK}; }}"
        )
        clr_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clr_btn.clicked.connect(self._clear_all)
        hl.addWidget(clr_btn)

        lay.addWidget(head)

        # Table
        cols = ["Modelo", "Parámetros", "ρ", "L", "Lq", "W", "Wq", "P₀", ""]
        self._table = QTableWidget(0, len(cols))
        self._table.setHorizontalHeaderLabels(cols)
        self._table.setStyleSheet(
            f"QTableWidget {{ background: {PAPER}; border: none; "
            f"gridline-color: rgba(20,17,15,0.12); font-family: {F_MONO}; font-size: 13px; }}"
            f"QTableWidget::item {{ padding: 14px; border-bottom: 1px solid rgba(20,17,15,0.12); }}"
            f"QTableWidget::item:selected {{ background: rgba(255,46,110,0.12); }}"
            f"QHeaderView::section {{ background: {PAPER2}; color: {INK_S}; "
            f"font-family: {F_MONO}; font-size: 10px; padding: 10px 14px; "
            f"border: none; border-bottom: 1px solid rgba(20,17,15,0.18); letter-spacing: 2px; }}"
        )
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(False)
        self._table.verticalHeader().hide()
        hdr = self._table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        for i in range(2, 8):
            hdr.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)
        self._table.setRowHeight(0, 50)

        self._empty_lbl = QLabel(
            "Calcula varios modelos para guardarlos aquí\ny compararlos lado a lado."
        )
        _f_cmp = QFont(F_SER, 18)
        _f_cmp.setItalic(True)
        self._empty_lbl.setFont(_f_cmp)
        self._empty_lbl.setStyleSheet(
            f"color: {INK_S}; border: 1px dashed {INK}; "
            f"padding: 60px; background: {PAPER};"
        )
        self._empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lay.addWidget(self._empty_lbl)
        lay.addWidget(self._table)
        self._table.hide()

    def add_result(self, model_name: str, params: dict, result: dict):
        key = (model_name, str(sorted(params.items())))
        for s in self._saved:
            if s["key"] == key:
                return
        idx = len(self._saved)
        self._saved.append({"key": key, "model": model_name, "params": params, "result": result})
        self._empty_lbl.hide()
        self._table.show()
        self._table.insertRow(idx)
        self._fill_row(idx)
        self._table.setRowHeight(idx, 44)

    def _fill_row(self, i: int):
        s = self._saved[i]
        r = s["result"]
        pr = s["params"]
        par_txt = (f"λ={pr.get('lambda','')}, μ={pr.get('mu','')}"
                   + (f", c={pr['c']}" if "c" in pr else "")
                   + (f", K={pr['K']}" if "K" in pr else "")
                   + (f", k={pr['k']}" if "k" in pr else ""))

        def _item(text, color=None):
            it = QTableWidgetItem(str(text))
            it.setForeground(QColor(color if color else INK))
            return it

        self._table.setItem(i, 0, _item(s["model"]))
        self._table.setItem(i, 1, _item(par_txt))
        for j, col_key in enumerate(["rho", "L", "Lq", "W", "Wq", "P0"]):
            self._table.setItem(i, j + 2, _item(_fmt(r.get(col_key), 4),
                                                HOT if col_key == "rho" else INK))

        del_btn = QPushButton("✕")
        del_btn.setFont(QFont(F_MONO, 11))
        del_btn.setStyleSheet(
            f"QPushButton {{ background: transparent; color: {MUTE}; border: none; }}"
            f"QPushButton:hover {{ color: {HOT}; }}"
        )
        del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        del_btn.clicked.connect(lambda _, idx=i: self._remove_row(idx))
        self._table.setCellWidget(i, 8, del_btn)

    def _clear_all(self):
        self._saved.clear()
        self._table.setRowCount(0)
        self._table.hide()
        self._empty_lbl.show()

    def _remove_row(self, idx: int):
        if 0 <= idx < len(self._saved):
            self._saved.pop(idx)
            self._rebuild_table()

    def _rebuild_table(self):
        self._table.setRowCount(0)
        if not self._saved:
            self._table.hide()
            self._empty_lbl.show()
            return
        self._empty_lbl.hide()
        self._table.show()
        for i in range(len(self._saved)):
            self._table.insertRow(i)
            self._fill_row(i)
            self._table.setRowHeight(i, 44)


# ─── Spread (tabs below the cover) ───────────────────────────────────────────
class SpreadSection(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            f"background: {PAPER}; border-top: 6px solid {INK};"
        )

        lay = QVBoxLayout(self)
        lay.setContentsMargins(40, 40, 40, 60)
        lay.setSpacing(0)

        self._tabs = QTabWidget()
        self._tabs.setStyleSheet(
            f"QTabWidget::pane {{ border: none; background: {PAPER}; }}"
            f"QTabBar::tab {{"
            f"  background: transparent; border: none;"
            f"  border-bottom: 4px solid transparent;"
            f"  padding: 14px 20px;"
            f"  font-family: {F_DISP}; font-size: 12px; letter-spacing: 2px;"
            f"  color: {INK_S}; margin-bottom: -2px;"
            f"}}"
            f"QTabBar::tab:selected {{"
            f"  color: {INK}; border-bottom: 4px solid {HOT};"
            f"}}"
            f"QTabBar::tab:hover {{ color: {INK}; }}"
            f"QTabWidget > QTabBar {{"
            f"  border-bottom: 2px solid {INK};"
            f"}}"
        )

        self.results_tab = ResultsTab()
        self.chart_tab   = ChartTab()
        self.compare_tab = CompareTab()

        self._tabs.addTab(self.results_tab, "01  RESULTADOS")
        self._tabs.addTab(self.chart_tab,   "02  GRÁFICA P(n)")
        self._tabs.addTab(self.compare_tab, "03  COMPARATIVA")

        lay.addWidget(self._tabs)


# ─── Main window ─────────────────────────────────────────────────────────────
class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"PAPI COLAS · Teoría de Colas · v{VERSION_STR}")
        self.resize(1280, 820)
        self.setMinimumSize(960, 680)

        # Cargar el icono de la ventana de PyQt6
        icon_path = get_resource_path(os.path.join("assets", "icon.png"))
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        root = QWidget()
        self.setCentralWidget(root)
        root.setStyleSheet(f"background: {PAPER};")

        vlay = QVBoxLayout(root)
        vlay.setContentsMargins(0, 0, 0, 0)
        vlay.setSpacing(0)

        # Masthead (fixed top bar)
        self._mast = MastheadBar()
        vlay.addWidget(self._mast)

        # Scroll area for cover + spread
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(
            f"QScrollArea {{ background: {PAPER}; border: none; }}"
            f"QScrollBar:vertical {{ background: {PAPER2}; width: 10px; }}"
            f"QScrollBar::handle:vertical {{ background: {MUTE}; border-radius: 5px; }}"
        )
        vlay.addWidget(scroll, stretch=1)

        body = QWidget()
        body.setStyleSheet(f"background: {PAPER};")
        scroll.setWidget(body)

        blay = QVBoxLayout(body)
        blay.setContentsMargins(0, 0, 0, 0)
        blay.setSpacing(0)

        # Cover
        self._cover = CoverWidget()
        self._cover.setMinimumHeight(540)
        blay.addWidget(self._cover)

        # Spread
        self._spread = SpreadSection()
        self._spread.setMinimumHeight(500)
        blay.addWidget(self._spread)

        # Marquee (fixed bottom bar)
        self._marquee = Marquee()
        vlay.addWidget(self._marquee)

        # Wire up signals
        rail = self._cover.rail
        rail.model_selected.connect(self._on_model_selected)
        rail.calc_clicked.connect(self._on_calc)
        rail.clear_clicked.connect(self._on_clear)

        # Initialize first model display
        first = list(MODELOS.keys())[0]
        self._cover.stage.update_model(first, 0)

        self._result: dict | None = None

    def _on_model_selected(self, name: str):
        idx = list(MODELOS.keys()).index(name)
        self._cover.stage.update_model(name, idx)

    def _on_calc(self):
        rail = self._cover.rail
        params, err = rail.get_params()
        if err:
            QMessageBox.critical(self, "Error de entrada", err)
            return

        model_name = rail.current_model
        m = MODELOS[model_name]
        result, calc_err = m["fn"](params)

        if calc_err:
            QMessageBox.critical(self, "Error de cálculo", calc_err)
            return

        self._result = result
        self._cover.feature.update_result(result)
        self._spread.results_tab.update_result(result)
        self._spread.chart_tab.update_result(result, model_name)

        # For models with 'c' servers, auto-add c=1..c to compare so the user
        # sees all server-count scenarios side by side without pressing Calcular
        # multiple times.
        c_val = int(params.get("c", 1)) if "c" in params else 1
        if c_val > 1:
            for ci in range(1, c_val):
                sub = {**params, "c": ci}
                sub_result, sub_err = m["fn"](sub)
                if not sub_err:
                    self._spread.compare_tab.add_result(model_name, sub, sub_result)
        self._spread.compare_tab.add_result(model_name, params, result)

    def _on_clear(self):
        self._result = None
        self._cover.rail.clear_entries()
        self._cover.feature.update_result(None)
        self._spread.results_tab.update_result(None)
        self._spread.chart_tab.update_result(None)
