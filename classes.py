from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QListWidget, QLabel, QComboBox, QCheckBox, QFrame, QSizePolicy,
    QDialog, QFormLayout, QScrollArea, QFileDialog, QMessageBox,
    QGraphicsDropShadowEffect, QGraphicsOpacityEffect, QStackedWidget,
    QTextEdit, QListWidgetItem, QAbstractItemView
)
from PyQt6.QtCore import (
    QPropertyAnimation, QEasingCurve, QAbstractAnimation,
    QSequentialAnimationGroup, Qt, pyqtSignal, QSize
)
from PyQt6.QtGui import QFont, QColor, QCursor

from themes import (
    BUILTIN_THEMES, EDITABLE_KEYS, build_stylesheet,
    generate_random_theme, save_theme, load_theme, list_user_themes, _t
)

# ── Glow URL bar ──────────────────────────────────────────────────────────────
class GlowURLBar(QLineEdit):
    def __init__(self, *a):
        super().__init__(*a)
        self._fx = QGraphicsDropShadowEffect()
        self._fx.setBlurRadius(0); self._fx.setOffset(0, 0)
        self._fx.setColor(QColor("#6c63ff"))
        self.setGraphicsEffect(self._fx)
        self._pa = QPropertyAnimation(self._fx, b"blurRadius")
        self._pa.setDuration(220)
        self._pa.setEasingCurve(QEasingCurve.Type.OutCubic)

    def set_glow(self, c): self._fx.setColor(QColor(c))

    def focusInEvent(self, e):
        super().focusInEvent(e)
        self._pa.stop()
        self._pa.setStartValue(self._fx.blurRadius())
        self._pa.setEndValue(22); self._pa.start()

    def focusOutEvent(self, e):
        super().focusOutEvent(e)
        self._pa.stop()
        self._pa.setStartValue(self._fx.blurRadius())
        self._pa.setEndValue(0); self._pa.start()

# ── Ripple / pulse button ─────────────────────────────────────────────────────
class RippleButton(QPushButton):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._seq = None

    def mousePressEvent(self, e):
        w = self.width()
        self._seq = QSequentialAnimationGroup(self)
        for s, end, ms in [(w, max(w-6, 20), 70), (max(w-6, 20), w, 120)]:
            a = QPropertyAnimation(self, b"minimumWidth"); a.setDuration(ms)
            a.setStartValue(s); a.setEndValue(end)
            self._seq.addAnimation(a)
        self._seq.start()
        super().mousePressEvent(e)

# ── Sliding panel base ────────────────────────────────────────────────────────
class SlidingPanel(QFrame):
    def __init__(self, target_width=260, parent=None):
        super().__init__(parent)
        self._tw   = target_width
        self._anim = None
        self.setMaximumWidth(0)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

    def _run(self, target):
        self._anim = QPropertyAnimation(self, b"maximumWidth")
        self._anim.setDuration(300)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutQuart)
        self._anim.setStartValue(self.maximumWidth())
        self._anim.setEndValue(target)
        self._anim.start()

    def open(self):    self._run(self._tw)
    def close(self):   self._run(0)
    def toggle(self):  self.close() if self.maximumWidth() > 10 else self.open()
    def is_open(self): return self.maximumWidth() > 10

# ── Bookmark bar ──────────────────────────────────────────────────────────────
class BookmarkBar(SlidingPanel):
    def __init__(self, parent=None):
        super().__init__(target_width=210, parent=parent)
        self.setObjectName("lpanel")
        self._list = QListWidget()
        self._list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        lay = QVBoxLayout(self); lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self._list)
        for u in ["https://github.com", "https://reddit.com",
                  "https://youtube.com", "https://wikipedia.org"]:
            self._list.addItem(u)

    def add(self, url):           self._list.addItem(url)
    def on_double_click(self, fn): self._list.itemDoubleClicked.connect(fn)

# ── Settings panel ────────────────────────────────────────────────────────────
class SettingsPanel(SlidingPanel):
    def __init__(self, parent=None):
        super().__init__(target_width=272, parent=parent)
        self.setObjectName("panel")

        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        inner = QWidget()
        lay   = QVBoxLayout(inner); lay.setContentsMargins(14, 14, 14, 14); lay.setSpacing(10)

        def section(txt):
            lb = QLabel(txt); lb.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            lay.addWidget(lb)

        # Theme
        section("🎨  Theme")
        self.theme_combo = QComboBox()
        self._refresh_theme_list()
        lay.addWidget(self.theme_combo)

        th_row = QHBoxLayout()
        self.btn_theme_edit   = RippleButton("✏ Edit")
        self.btn_theme_new    = RippleButton("＋ New")
        self.btn_theme_import = RippleButton("↓ Import")
        for b in (self.btn_theme_edit, self.btn_theme_new, self.btn_theme_import):
            b.setFixedHeight(28); th_row.addWidget(b)
        lay.addLayout(th_row)

        # Layout
        section("🗂  Tab Layout")
        self.vertical_tabs = QCheckBox("Vertical tab bar")
        lay.addWidget(self.vertical_tabs)


        # Homepage
        section("🏠  Homepage")
        self.hp_edit = QLineEdit("https://google.com")
        lay.addWidget(self.hp_edit)

        # Options
        self.js_check    = QCheckBox("JavaScript"); self.js_check.setChecked(True)
        self.smooth_scr  = QCheckBox("Smooth scroll");  self.smooth_scr.setChecked(True)
        

        # Zoom
        section("🔍  Page Zoom")
        zrow = QHBoxLayout()
        self.btn_zm   = RippleButton("−"); self.btn_zm.setFixedWidth(36)
        self.zoom_lbl = QLabel("100%")
        self.zoom_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.btn_zp   = RippleButton("+"); self.btn_zp.setFixedWidth(36)
        self.btn_zr   = RippleButton("↺"); self.btn_zr.setFixedWidth(36)
        for w in (self.btn_zm, self.zoom_lbl, self.btn_zp, self.btn_zr): zrow.addWidget(w)
        lay.addLayout(zrow)

        # Bookmark
        section("★  Add Bookmark")
        self.bm_input = QLineEdit(); self.bm_input.setPlaceholderText("URL + Enter")
        lay.addWidget(self.bm_input)

        section(" ⚠️  Known bugs:")
        for b in ["Some websites may not reload when a new theme is selected. FIX: Refresh the page.",
                  "Dark mode is not fully implemented and may cause visual glitches. FIX: well, its...not..there so yeah the fix is doing nothing :D",]:
            lb = QLabel("• " + b); lb.setWordWrap(True)
            lay.addWidget(lb)

        lay.addStretch()
        scroll.setWidget(inner)
        outer = QVBoxLayout(self); outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _refresh_theme_list(self):
        self.theme_combo.blockSignals(True)
        cur = self.theme_combo.currentText()
        self.theme_combo.clear()
        self.theme_combo.addItems(list(BUILTIN_THEMES.keys()) + ["RandomME"] +
                                  [name for name, _ in list_user_themes()])
        idx = self.theme_combo.findText(cur)
        if idx >= 0: self.theme_combo.setCurrentIndex(idx)
        self.theme_combo.blockSignals(False)

# ── Color picker button ───────────────────────────────────────────────────────
class ColorBtn(QPushButton):
    colorChanged = pyqtSignal(str)

    def __init__(self, color="#ffffff", parent=None):
        super().__init__(parent)
        self._c = color
        self.setFixedSize(52, 26)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._refresh()
        self.clicked.connect(self._pick)

    def _refresh(self):
        self.setStyleSheet(f"background:{self._c};border:1.5px solid #888;border-radius:5px;")
        self.setToolTip(self._c)

    def _pick(self):
        from PyQt6.QtWidgets import QColorDialog
        c = QColorDialog.getColor(QColor(self._c), self, "Pick Color")
        if c.isValid():
            self._c = c.name()
            self._refresh()
            self.colorChanged.emit(self._c)

    def color(self): return self._c
    def setColor(self, c): self._c = c; self._refresh()

# ── Theme editor dialog ───────────────────────────────────────────────────────
class ThemeEditorDialog(QDialog):
    themeChanged = pyqtSignal(dict)

    LABELS = {
        "win_bg": "Window background", "bg": "Widget background",
        "surface": "Surface / panels", "fg": "Foreground text",
        "border": "Borders", "hover": "Hover bg",
        "selection": "Text selection", "accent": "Accent",
        "accent_fg": "Text on accent", "accent_hover": "Accent hover",
        "btn": "Button bg", "btn_fg": "Button text",
        "btn_hover": "Button hover", "btn_press": "Button press",
        "tab_bg": "Tab bg", "tab_fg": "Tab text",
        "tab_sel": "Selected tab", "tab_sel_fg": "Selected tab text",
        "prog_bg": "Progress bg", "glow": "URL glow",
    }

    def __init__(self, theme: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Theme Editor"); self.resize(480, 580)
        self._theme = dict(theme)
        self._btns  = {}

        lay = QVBoxLayout(self); lay.setSpacing(8)

        # Name
        row = QHBoxLayout()
        row.addWidget(QLabel("Theme name:"))
        self.name_edit = QLineEdit(theme.get("name", "My Theme"))
        row.addWidget(self.name_edit)
        lay.addLayout(row)

        # Color grid
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        inner  = QWidget(); form = QFormLayout(inner); form.setSpacing(6)

        for key in EDITABLE_KEYS:
            lbl = self.LABELS.get(key, key)
            btn = ColorBtn(theme.get(key, "#888888"))
            btn.colorChanged.connect(lambda c, k=key: self._on_color(k, c))
            self._btns[key] = btn
            form.addRow(lbl + ":", btn)

        # Font
        form.addRow("Font family:", QLabel(""))
        self.font_edit = QLineEdit(theme.get("font", "'Segoe UI', Arial, sans-serif"))
        form.addRow("", self.font_edit)

        # Extra CSS
        form.addRow("Extra CSS:", QLabel(""))
        self.extra_edit = QTextEdit(); self.extra_edit.setFixedHeight(80)
        self.extra_edit.setPlainText(theme.get("extra", ""))
        form.addRow("", self.extra_edit)

        scroll.setWidget(inner); lay.addWidget(scroll)

        # Buttons
        brow = QHBoxLayout()
        self.btn_preview = RippleButton("👁 Preview");  self.btn_preview.setObjectName("accent")
        self.btn_save    = RippleButton("💾 Save")
        self.btn_export  = RippleButton("📤 Export JSON")
        self.btn_import  = RippleButton("📥 Import JSON")
        self.btn_cancel  = RippleButton("Cancel")
        for b in (self.btn_preview, self.btn_save, self.btn_export,
                  self.btn_import, self.btn_cancel):
            brow.addWidget(b)
        lay.addLayout(brow)

        self.btn_preview.clicked.connect(self._preview)
        self.btn_save.clicked.connect(self._save)
        self.btn_export.clicked.connect(self._export)
        self.btn_import.clicked.connect(self._import)
        self.btn_cancel.clicked.connect(self.reject)

    def _on_color(self, key, val):
        self._theme[key] = val

    def _current_theme(self) -> dict:
        t = dict(self._theme)
        t["font"]  = self.font_edit.text()
        t["extra"] = self.extra_edit.toPlainText()
        return t

    def _preview(self):
        self.themeChanged.emit(self._current_theme())

    def _save(self):
        name = self.name_edit.text().strip() or "My Theme"
        save_theme(self._current_theme(), name)
        QMessageBox.information(self, "Saved", f"Theme '{name}' saved!")
        self.themeChanged.emit(self._current_theme())
        self.accept()

    def _export(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export theme", "", "JSON (*.json)")
        if path:
            import json; from pathlib import Path
            out = dict(self._current_theme()); out["name"] = self.name_edit.text()
            Path(path).write_text(json.dumps(out, indent=2))

    def _import(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import theme", "", "JSON (*.json)")
        if path:
            t = load_theme(path)
            self._theme = t
            for key, btn in self._btns.items():
                btn.setColor(t.get(key, "#888"))
            self.font_edit.setText(t.get("font", "'Segoe UI', Arial, sans-serif"))
            self.extra_edit.setPlainText(t.get("extra", ""))

# ── Vertical tab widget ───────────────────────────────────────────────────────
class VerticalTabWidget(QWidget):
    tabCloseRequested = pyqtSignal(int)
    currentChanged    = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QHBoxLayout(self); lay.setContentsMargins(0, 0, 0, 0); lay.setSpacing(0)

        self._tab_bar = QListWidget()
        self._tab_bar.setObjectName("lpanel")
        self._tab_bar.setFixedWidth(180)
        self._tab_bar.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._tab_bar.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._tab_bar.customContextMenuRequested.connect(self._ctx_menu)

        self._stack = QStackedWidget()
        lay.addWidget(self._tab_bar); lay.addWidget(self._stack, 1)
        self._tab_bar.currentRowChanged.connect(self._on_row)

    def _on_row(self, i):
        if i >= 0: self._stack.setCurrentIndex(i); self.currentChanged.emit(i)

    def _ctx_menu(self, pos):
        from PyQt6.QtWidgets import QMenu
        item = self._tab_bar.itemAt(pos)
        if not item: return
        row = self._tab_bar.row(item)
        menu = QMenu(self)
        menu.addAction("Close tab", lambda: self.tabCloseRequested.emit(row))
        menu.exec(self._tab_bar.mapToGlobal(pos))

    def addTab(self, widget, title):
        self._tab_bar.addItem(title)
        self._stack.addWidget(widget)
        i = self._stack.count() - 1
        self._tab_bar.setCurrentRow(i)
        return i

    def removeTab(self, i):
        self._tab_bar.takeItem(i)
        w = self._stack.widget(i)
        self._stack.removeWidget(w)
        if w: w.deleteLater()

    def setCurrentIndex(self, i): self._tab_bar.setCurrentRow(i)
    def currentIndex(self):       return self._tab_bar.currentRow()
    def count(self):               return self._stack.count()
    def widget(self, i):           return self._stack.widget(i)
    def setTabsClosable(self, _):  pass  # handled via context menu

    def setTabText(self, i, text):
        if 0 <= i < self._tab_bar.count():
            item = self._tab_bar.item(i)
            # truncate long titles
            item.setText((text[:22] + "…") if len(text) > 25 else text)

    def indexOf(self, widget):
        for i in range(self._stack.count()):
            if self._stack.widget(i) is widget: return i
        return -1