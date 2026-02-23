import sys, traceback, faulthandler
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QProgressBar, QSizePolicy, QGraphicsOpacityEffect, QTabWidget
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings, QWebEnginePage
from PyQt6.QtCore import QUrl, QPropertyAnimation, QEasingCurve, QAbstractAnimation, QTimer
from PyQt6.QtGui import QFont, QKeySequence, QShortcut, QColor
from PyQt6.QtGui import QIcon
from themes import (
    BUILTIN_THEMES, build_stylesheet, generate_random_theme,
    load_theme, list_user_themes, INJECT_DARK, REMOVE_DARK, SMOOTH_JS
)
from classes import (
    GlowURLBar, RippleButton, BookmarkBar, SettingsPanel,
    VerticalTabWidget, ThemeEditorDialog
)

ENGINES = {
    "Google":    "https://www.google.com/search?q={}",
    "Bing":      "https://www.bing.com/search?q={}",
    "DuckDuckGo":"https://duckduckgo.com/?q={}",
    "Brave":     "https://search.brave.com/search?q={}",
    "Yahoo":     "https://search.yahoo.com/search?p={}",
}

class CustomBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Antichromium")
        self.setWindowIcon(QIcon("icon.png"))
        self.resize(1340, 860)
        self._dark_web  = False
        self._zoom      = 1.0
        self._cur_theme = {}
        # hold animation refs so GC doesn't kill them
        self._t_in = self._t_out = self._ov = self._ov_fx = None

        self.central = QWidget(); self.setCentralWidget(self.central)
        root = QVBoxLayout(self.central)
        root.setContentsMargins(10, 10, 10, 6); root.setSpacing(5)

        # ── Panels first (avoids AttributeError on connect) ───────────────────
        self.sett   = SettingsPanel()
        self.bm_bar = BookmarkBar()

        # Settings signals
        self.sett.theme_combo.currentTextChanged.connect(self._apply_theme)
        self.sett.vertical_tabs.stateChanged.connect(self._toggle_vtabs)
        self.sett.js_check.stateChanged.connect(self._toggle_js)
        self.sett.smooth_scr.stateChanged.connect(self._toggle_smooth)
        self.sett.bm_input.returnPressed.connect(self._add_bookmark)
        self.sett.btn_zm.clicked.connect(self._zoom_out)
        self.sett.btn_zp.clicked.connect(self._zoom_in)
        self.sett.btn_zr.clicked.connect(self._zoom_reset)
        self.sett.btn_theme_edit.clicked.connect(self._open_theme_editor)
        self.sett.btn_theme_new.clicked.connect(self._new_theme)
        self.sett.btn_theme_import.clicked.connect(self._import_theme)
        self.bm_bar.on_double_click(lambda item: self._cv().setUrl(QUrl(item.text())))

        # ── Nav bar ───────────────────────────────────────────────────────────
        nav = QHBoxLayout(); nav.setSpacing(5)

        def rb(lbl, tip="", obj=""):
            b = RippleButton(lbl); b.setToolTip(tip)
            if obj: b.setObjectName(obj)
            return b

        self.btn_bm   = rb("☰",     "Bookmarks")
        self.btn_back = rb("◀",     "Back  (Alt+←)")
        self.btn_fwd  = rb("▶",     "Forward  (Alt+→)")
        self.btn_ref  = rb("↻",     "Reload  (F5)")
        self.url_bar  = GlowURLBar()
        self.url_bar.setPlaceholderText("Search or type a URL…")
        self.btn_tab  = rb("＋ Tab","New tab  (Ctrl+T)", "accent")
        self.btn_find = rb("🔍",    "Find in page  (Ctrl+F)")
        self.btn_sett = rb("⚙",     "Settings")

        self.btn_bm.clicked.connect(self.bm_bar.toggle)
        self.btn_back.clicked.connect(lambda: self._cv().back())
        self.btn_fwd.clicked.connect(lambda: self._cv().forward())
        self.btn_ref.clicked.connect(lambda: self._cv().reload())
        self.url_bar.returnPressed.connect(self._navigate)
        self.btn_tab.clicked.connect(self._new_tab)
        self.btn_find.clicked.connect(self._toggle_find)
        self.btn_sett.clicked.connect(self.sett.toggle)

        for w in (self.btn_bm, self.btn_back, self.btn_fwd, self.btn_ref,
                  self.url_bar, self.btn_tab, self.btn_find, self.btn_sett):
            nav.addWidget(w)
        self.url_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        root.addLayout(nav)

        # ── Find bar ──────────────────────────────────────────────────────────
        self._find_row = QWidget(); self._find_row.setVisible(False)
        fr = QHBoxLayout(self._find_row)
        fr.setContentsMargins(0, 0, 0, 0); fr.setSpacing(5)
        self._find_edit  = GlowURLBar()
        self._find_edit.setPlaceholderText("Find in page…")
        self._find_edit.setMaximumWidth(300)
        self._find_prev  = rb("↑", "Prev match")
        self._find_next  = rb("↓", "Next match")
        self._find_close = rb("✕", "Close")
        self._find_edit.textChanged.connect(self._do_find)
        self._find_prev.clicked.connect(lambda: self._do_find(backward=True))
        self._find_next.clicked.connect(self._do_find)
        self._find_close.clicked.connect(self._toggle_find)
        for w in (self._find_edit, self._find_prev, self._find_next, self._find_close):
            fr.addWidget(w)
        fr.addStretch()
        root.addWidget(self._find_row)

        # ── Progress bar ──────────────────────────────────────────────────────
        self.prog = QProgressBar()
        self.prog.setRange(0, 100); self.prog.setValue(0)
        self.prog.setTextVisible(False); self.prog.setFixedHeight(4)
        root.addWidget(self.prog)

        # ── Body ──────────────────────────────────────────────────────────────
        self.body_lay = QHBoxLayout(); self.body_lay.setSpacing(0)

        # Tab widget (starts as horizontal QTabWidget)
        self._vtab_mode = False
        self.tabs = self._make_htabs()

        self.body_lay.addWidget(self.bm_bar)
        self.body_lay.addWidget(self.tabs, 1)
        self.body_lay.addWidget(self.sett)
        root.addLayout(self.body_lay, 1)

        # ── Status bar ────────────────────────────────────────────────────────
        self.status = QLabel("Ready  ◦  BlahBlah Browser")
        self.status.setFixedHeight(17)
        f = self.status.font(); f.setPointSize(9); self.status.setFont(f)
        root.addWidget(self.status)

        # ── Shortcuts ─────────────────────────────────────────────────────────
        def sc(key, fn): QShortcut(QKeySequence(key), self).activated.connect(fn)
        sc("Ctrl+T",    self._new_tab)
        sc("Ctrl+W",    lambda: self._close_tab(self.tabs.currentIndex()))
        sc("Ctrl+R",    lambda: self._cv().reload())
        sc("F5",        lambda: self._cv().reload())
        sc("Ctrl+L",    lambda: (self.url_bar.setFocus(), self.url_bar.selectAll()))
        sc("Ctrl+F",    self._toggle_find)
        sc("Alt+Left",  lambda: self._cv().back())
        sc("Alt+Right", lambda: self._cv().forward())
        sc("Ctrl++",    self._zoom_in)
        sc("Ctrl+-",    self._zoom_out)
        sc("Ctrl+0",    self._zoom_reset)

        # ── Init ──────────────────────────────────────────────────────────────
        self.sett.theme_combo.blockSignals(True)
        self.sett.theme_combo.setCurrentText("Dracula")
        self.sett.theme_combo.blockSignals(False)
        self._apply_theme("Dracula", animate=False)
        self._add_new_tab(QUrl(self.sett.hp_edit.text()), "Home")

    # ── Tab widget factory ────────────────────────────────────────────────────
    def _make_htabs(self):
        t = QTabWidget()
        t.setTabsClosable(True)
        t.tabCloseRequested.connect(self._close_tab)
        t.currentChanged.connect(self._on_tab_changed)
        return t

    def _make_vtabs(self):
        t = VerticalTabWidget()
        t.tabCloseRequested.connect(self._close_tab)
        t.currentChanged.connect(self._on_tab_changed)
        return t

    def _toggle_vtabs(self, state):
        # Migrate all tabs to new widget type
        old    = self.tabs
        views  = [old.widget(i) for i in range(old.count())]
        titles = [old.tabText(i) if hasattr(old, "tabText") else
                  (old._tab_bar.item(i).text() if hasattr(old, "_tab_bar") else "Tab")
                  for i in range(old.count())]
        cur = old.currentIndex()

        self.body_lay.removeWidget(old)
        old.hide(); old.setParent(None)

        self._vtab_mode = bool(state)
        self.tabs = self._make_vtabs() if self._vtab_mode else self._make_htabs()

        for v, title in zip(views, titles):
            self.tabs.addTab(v, title)
        self.tabs.setCurrentIndex(cur)

        self.body_lay.insertWidget(1, self.tabs, 1)

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _cv(self) -> QWebEngineView:
        return self.tabs.widget(self.tabs.currentIndex())

    def _add_new_tab(self, qurl: QUrl, label="New Tab"):
        v = QWebEngineView()
        v.setUrl(qurl)
        v.urlChanged.connect(lambda u, _v=v: self._on_url(_v, u))
        v.titleChanged.connect(lambda t, _v=v: self._on_title(_v, t))
        v.loadStarted.connect(lambda _v=v: self._on_start(_v))
        v.loadProgress.connect(lambda p, _v=v: self._on_prog(_v, p))
        v.loadFinished.connect(lambda ok, _v=v: self._on_fin(_v, ok))

        i = self.tabs.addTab(v, label)
        self.tabs.setCurrentIndex(i)

        # Fade-in animation
        fx = QGraphicsOpacityEffect(); v.setGraphicsEffect(fx); fx.setOpacity(0)
        a = QPropertyAnimation(fx, b"opacity"); a.setDuration(320)
        a.setStartValue(0.0); a.setEndValue(1.0)
        a.setEasingCurve(QEasingCurve.Type.OutCubic)
        a.finished.connect(lambda: v.setGraphicsEffect(None))
        a.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)

        if self._dark_web:
            QTimer.singleShot(900, lambda _v=v: _v.page().runJavaScript(INJECT_DARK))

    def _new_tab(self):
        self._add_new_tab(QUrl(self.sett.hp_edit.text()), "New Tab")

    def _close_tab(self, i):
        if self.tabs.count() > 1:
            self.tabs.removeTab(i)

    def _navigate(self):
        q = self.url_bar.text().strip()
        if not q: return
        if "." in q and " " not in q:
            url = QUrl(q if q.startswith("http") else "https://" + q)
        else:
            eng = self.sett.engine_combo.currentText()
            url = QUrl(ENGINES[eng].format(q.replace(" ", "+")))
        self._cv().setUrl(url)

    # ── Tab slots ─────────────────────────────────────────────────────────────
    def _on_url(self, v, url):
        if v is self._cv(): self.url_bar.setText(url.toString())
        if self._dark_web:
            QTimer.singleShot(700, lambda: v.page().runJavaScript(INJECT_DARK))
        if self.sett.smooth_scr.isChecked():
            QTimer.singleShot(800, lambda: v.page().runJavaScript(SMOOTH_JS))

    def _on_title(self, v, t):
        i = self.tabs.indexOf(v)
        if i != -1:
            short = (t[:22] + "…") if len(t) > 25 else t or "New Tab"
            self.tabs.setTabText(i, short)

    def _on_start(self, v):
        if v is self._cv(): self._anim_prog(0); self.status.setText("Loading…")

    def _on_prog(self, v, p):
        if v is self._cv(): self._anim_prog(p)

    def _on_fin(self, v, ok):
        if v is self._cv():
            self._anim_prog(100)
            self.status.setText("✓  Done" if ok else "✗  Load failed")
            QTimer.singleShot(900, lambda: self._anim_prog(0))
        if self._dark_web: v.page().runJavaScript(INJECT_DARK)
        if self.sett.smooth_scr.isChecked(): v.page().runJavaScript(SMOOTH_JS)

    def _on_tab_changed(self, i):
        if i >= 0 and (v := self.tabs.widget(i)):
            self.url_bar.setText(v.url().toString())

    # ── Progress animation ────────────────────────────────────────────────────
    def _anim_prog(self, val):
        a = QPropertyAnimation(self.prog, b"value", self)
        a.setDuration(260); a.setEasingCurve(QEasingCurve.Type.OutCubic)
        a.setStartValue(self.prog.value()); a.setEndValue(val)
        a.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)

    # ── Theme switching ───────────────────────────────────────────────────────
    def _apply_theme(self, name, animate=True):
        if name == "RandomME":
            theme = generate_random_theme()
        elif name in BUILTIN_THEMES:
            theme = BUILTIN_THEMES[name]
        else:
            # user theme
            user = dict(list_user_themes())
            if name in user:
                theme = load_theme(user[name])
            else:
                return
        self._cur_theme = theme
        ss = build_stylesheet(theme)
        glow = theme.get("glow", "#6c63ff")

        if not animate:
            self.setStyleSheet(ss)
            self.url_bar.set_glow(glow)
            return

        # Cross-fade overlay (all refs on self to beat GC)
        self._ov = QLabel(self.central)
        self._ov.setStyleSheet("background:#000;")
        self._ov.resize(self.central.size())
        self._ov.show(); self._ov.raise_()

        self._ov_fx = QGraphicsOpacityEffect()
        self._ov.setGraphicsEffect(self._ov_fx)
        self._ov_fx.setOpacity(0)

        self._t_in = QPropertyAnimation(self._ov_fx, b"opacity")
        self._t_in.setDuration(110)
        self._t_in.setStartValue(0.0); self._t_in.setEndValue(1.0)
        self._t_in.setEasingCurve(QEasingCurve.Type.OutQuad)

        self._t_out = QPropertyAnimation(self._ov_fx, b"opacity")
        self._t_out.setDuration(210)
        self._t_out.setStartValue(1.0); self._t_out.setEndValue(0.0)
        self._t_out.setEasingCurve(QEasingCurve.Type.OutQuad)

        def _reveal():
            self.setStyleSheet(ss)
            self.url_bar.set_glow(glow)
            self._t_out.finished.connect(self._ov.deleteLater)
            self._t_out.start()

        self._t_in.finished.connect(_reveal)
        self._t_in.start()

    # ── Theme editor ──────────────────────────────────────────────────────────
    def _open_theme_editor(self):
        name = self.sett.theme_combo.currentText()
        theme = (BUILTIN_THEMES.get(name) or self._cur_theme or
                 list(BUILTIN_THEMES.values())[0])
        dlg = ThemeEditorDialog(dict(theme), self)
        dlg.themeChanged.connect(self._on_editor_preview)
        dlg.exec()
        self.sett._refresh_theme_list()

    def _on_editor_preview(self, theme):
        self._cur_theme = theme
        self.setStyleSheet(build_stylesheet(theme))
        self.url_bar.set_glow(theme.get("glow", "#6c63ff"))

    def _new_theme(self):
        from themes import generate_random_theme
        dlg = ThemeEditorDialog(generate_random_theme("New Theme"), self)
        dlg.themeChanged.connect(self._on_editor_preview)
        dlg.exec()
        self.sett._refresh_theme_list()

    def _import_theme(self):
        from PyQt6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(self, "Import theme", "", "JSON (*.json)")
        if path:
            theme = load_theme(path)
            from themes import save_theme; import json; from pathlib import Path
            name = json.loads(Path(path).read_text()).get("name", "Imported")
            save_theme(theme, name)
            self.sett._refresh_theme_list()
            self._apply_theme(name)

    # ── Settings actions ──────────────────────────────────────────────────────
    def _toggle_dark_web(self, state):
        self._dark_web = bool(state)
        js = INJECT_DARK if self._dark_web else REMOVE_DARK
        for i in range(self.tabs.count()):
            self.tabs.widget(i).page().runJavaScript(js)

    def _toggle_js(self, state):
        for i in range(self.tabs.count()):
            self.tabs.widget(i).settings().setAttribute(
                QWebEngineSettings.WebAttribute.JavascriptEnabled, bool(state))

    def _toggle_smooth(self, state):
        if state: self._cv().page().runJavaScript(SMOOTH_JS)

    def _add_bookmark(self):
        url = self.sett.bm_input.text().strip()
        if url: self.bm_bar.add(url); self.sett.bm_input.clear()

    # ── Find ──────────────────────────────────────────────────────────────────
    def _toggle_find(self):
        vis = not self._find_row.isVisible()
        self._find_row.setVisible(vis)
        if vis:  self._find_edit.setFocus()
        else:    self._cv().findText("")

    def _do_find(self, text=None, backward=False):
        q    = self._find_edit.text() if text is None else text
        flag = (QWebEnginePage.FindFlag.FindBackward if backward
                else QWebEnginePage.FindFlag(0))
        self._cv().findText(q, flag)

    # ── Zoom ──────────────────────────────────────────────────────────────────
    def _set_zoom(self, z):
        self._zoom = round(max(0.25, min(z, 3.0)), 1)
        self._cv().setZoomFactor(self._zoom)
        self.sett.zoom_lbl.setText(f"{int(self._zoom * 100)}%")

    def _zoom_in(self):    self._set_zoom(self._zoom + 0.1)
    def _zoom_out(self):   self._set_zoom(self._zoom - 0.1)
    def _zoom_reset(self): self._set_zoom(1.0)


# ── Entry ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    faulthandler.enable()
    sys.excepthook = lambda cls, exc, tb: (
        traceback.print_exception(cls, exc, tb), sys.exit(1))

    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 11))
    w = CustomBrowser(); w.show()
    sys.exit(app.exec())