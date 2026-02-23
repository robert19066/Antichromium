import json, random, colorsys
from pathlib import Path

USER_DIR = Path.home() / ".blahblah_browser" / "themes"
USER_DIR.mkdir(parents=True, exist_ok=True)

INJECT_DARK = ("(function(){if(document.getElementById('__bb__'))return;"
               "var s=document.createElement('style');s.id='__bb__';"
               "s.textContent='html{filter:invert(90%)hue-rotate(180deg)!important}"
               "img,video,canvas,picture{filter:invert(100%)hue-rotate(180deg)!important}';"
               "document.documentElement.appendChild(s)})();")
REMOVE_DARK  = "(function(){var s=document.getElementById('__bb__');if(s)s.remove()})();"
SMOOTH_JS    = ("document.documentElement.style.scrollBehavior='smooth';"
                "document.body.style.scrollBehavior='smooth';")

# ── Stylesheet template ───────────────────────────────────────────────────────
_SS = """
* {{ font-family: {font}; }}
QMainWindow  {{ background: {win_bg}; }}
QWidget      {{ background: {bg}; color: {fg}; }}
QDialog      {{ background: {bg}; color: {fg}; }}

QLineEdit {{
    background: {surface}; color: {fg};
    border: 1.5px solid {border}; border-radius: 14px;
    padding: 8px 16px; selection-background-color: {selection};
}}
QLineEdit:focus {{ border-color: {accent}; }}

QPushButton {{
    background: {btn}; color: {btn_fg};
    border: {btn_border}; border-radius: 9px;
    padding: 7px 14px; font-weight: 600; min-width: 28px;
}}
QPushButton:hover   {{ background: {btn_hover}; }}
QPushButton:pressed {{ background: {btn_press}; }}
QPushButton#accent {{
    background: {accent}; color: {accent_fg};
    border: none; border-radius: 9px; padding: 7px 16px; font-weight: 700;
}}
QPushButton#accent:hover  {{ background: {accent_hover}; }}
QPushButton#danger        {{ background: #c0392b; color:#fff; border:none; border-radius:9px; }}
QPushButton#danger:hover  {{ background: #e74c3c; }}
QPushButton#flat {{
    background: transparent; border: none; color: {fg};
    padding: 2px 4px; font-weight: normal; min-width: 16px;
}}
QPushButton#flat:hover {{ background: {hover}; border-radius: 6px; }}

QTabWidget::pane {{ border: none; background: {bg}; }}
QTabBar          {{ background: transparent; }}
QTabBar::tab {{
    background: {tab_bg}; color: {tab_fg};
    padding: 9px 18px; margin-right: 3px;
    border-top-left-radius: 9px; border-top-right-radius: 9px;
}}
QTabBar::tab:selected {{ background: {tab_sel}; color: {tab_sel_fg}; font-weight: bold; }}
QTabBar::tab:hover:!selected {{ background: {btn_hover}; }}
QTabBar::tab:left {{
    border-top-left-radius: 9px; border-bottom-left-radius: 9px;
    border-top-right-radius: 0; border-bottom-right-radius: 0;
    margin-right: 0; margin-bottom: 3px; padding: 12px 10px;
    min-width: 140px; text-align: left;
}}

QListWidget {{
    background: {surface}; color: {fg};
    border: none; border-right: 2px solid {border}; padding: 4px;
}}
QListWidget::item {{ padding: 7px 10px; border-radius: 6px; }}
QListWidget::item:hover    {{ background: {hover}; }}
QListWidget::item:selected {{ background: {accent}; color: {accent_fg}; border-radius: 6px; }}

QProgressBar {{ max-height: 4px; border: none; border-radius: 2px; background: {prog_bg}; }}
QProgressBar::chunk {{ background: {accent}; border-radius: 2px; }}

QLabel   {{ color: {fg}; background: transparent; }}
QComboBox {{
    background: {surface}; color: {fg};
    border: 1.5px solid {border}; border-radius: 8px; padding: 5px 10px;
}}
QComboBox::drop-down {{ border: none; width: 18px; }}
QComboBox QAbstractItemView {{
    background: {surface}; color: {fg}; border: 1px solid {border};
    selection-background-color: {accent}; selection-color: {accent_fg};
}}
QCheckBox {{ color: {fg}; spacing: 7px; }}
QCheckBox::indicator {{
    width: 16px; height: 16px; border-radius: 4px;
    border: 1.5px solid {border}; background: {surface};
}}
QCheckBox::indicator:checked {{ background: {accent}; border-color: {accent}; }}
QFrame#panel  {{ background: {surface}; border-left:  2px solid {border}; }}
QFrame#lpanel {{ background: {surface}; border-right: 2px solid {border}; }}
QScrollBar:vertical {{
    background: {bg}; width: 7px; border-radius: 3px; margin: 0;
}}
QScrollBar::handle:vertical {{ background: {border}; border-radius: 3px; min-height: 20px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QTextEdit {{
    background: {surface}; color: {fg};
    border: 1.5px solid {border}; border-radius: 8px;
    padding: 6px; font-family: 'Courier New', monospace; font-size: 12px;
}}
QSlider::groove:horizontal {{ background: {prog_bg}; height: 4px; border-radius: 2px; }}
QSlider::handle:horizontal {{
    background: {accent}; width: 14px; height: 14px;
    margin: -5px 0; border-radius: 7px;
}}
QSlider::sub-page:horizontal {{ background: {accent}; border-radius: 2px; }}
QSplitter::handle {{ background: {border}; }}

{extra}
"""

def build_stylesheet(t: dict) -> str:
    return _SS.format(**{
        "font":         t.get("font", "'Segoe UI', Arial, sans-serif"),
        "win_bg":       t["win_bg"],
        "bg":           t["bg"],
        "fg":           t["fg"],
        "surface":      t["surface"],
        "border":       t["border"],
        "hover":        t["hover"],
        "selection":    t["selection"],
        "accent":       t["accent"],
        "accent_fg":    t["accent_fg"],
        "accent_hover": t["accent_hover"],
        "btn":          t["btn"],
        "btn_fg":       t["btn_fg"],
        "btn_border":   t["btn_border"],
        "btn_hover":    t["btn_hover"],
        "btn_press":    t["btn_press"],
        "tab_bg":       t["tab_bg"],
        "tab_fg":       t["tab_fg"],
        "tab_sel":      t["tab_sel"],
        "tab_sel_fg":   t["tab_sel_fg"],
        "prog_bg":      t["prog_bg"],
        "extra":        t.get("extra", ""),
    })

def _t(**kw) -> dict:
    return {"font": "'Segoe UI', Arial, sans-serif", "extra": "", "glow": "#6c63ff", **kw}

# ── Built-in themes ───────────────────────────────────────────────────────────
BUILTIN_THEMES: dict[str, dict] = {

  "B L A K": _t(
    win_bg="#000", bg="#000", surface="#0d0d0d", fg="#e0e0e0",
    border="#1e1e1e", hover="#141414", selection="#2a2a2a",
    accent="#ffffff", accent_fg="#000", accent_hover="#cccccc",
    btn="#111", btn_fg="#e0e0e0", btn_border="1px solid #222",
    btn_hover="#1c1c1c", btn_press="#080808",
    tab_bg="#090909", tab_fg="#555", tab_sel="#000", tab_sel_fg="#fff",
    prog_bg="#111", glow="#ffffff",
  ),

  "W H I T": _t(
    win_bg="#ffffff", bg="#ffffff", surface="#f5f5f5", fg="#111111",
    border="#e0e0e0", hover="#ebebeb", selection="#d0d0d0",
    accent="#111111", accent_fg="#ffffff", accent_hover="#333333",
    btn="#eeeeee", btn_fg="#111", btn_border="1px solid #e0e0e0",
    btn_hover="#e4e4e4", btn_press="#d8d8d8",
    tab_bg="#f0f0f0", tab_fg="#888", tab_sel="#ffffff", tab_sel_fg="#111",
    prog_bg="#e0e0e0", glow="#555555",
  ),

  "Dracula": _t(
    win_bg="#282a36", bg="#282a36", surface="#21222c", fg="#f8f8f2",
    border="#44475a", hover="#44475a", selection="#44475a",
    accent="#bd93f9", accent_fg="#282a36", accent_hover="#9c71e3",
    btn="#44475a", btn_fg="#f8f8f2", btn_border="none",
    btn_hover="#6272a4", btn_press="#373848",
    tab_bg="#21222c", tab_fg="#6272a4", tab_sel="#282a36", tab_sel_fg="#f8f8f2",
    prog_bg="#44475a", glow="#bd93f9",
    extra="""
    QPushButton#accent { background:#ff79c6; color:#282a36; }
    QPushButton#accent:hover { background:#e060ad; }
    QProgressBar::chunk { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #bd93f9, stop:1 #ff79c6); }
    QTabBar::tab:selected { color:#ff79c6; border-bottom: 2px solid #ff79c6; }
    QListWidget::item:selected { background:#bd93f9; color:#282a36; }
    """,
  ),

  "Win7 Nostalgia": _t(
    win_bg="qlineargradient(x1:0,y1:0,x2:0,y2:1,"
           "stop:0 #d6eeff, stop:0.18 #a8d8f8, stop:0.45 #6ab8f0,"
           "stop:0.46 #4aa8e8, stop:0.72 #82c8f5, stop:1 #c0e8ff)",
    bg="qlineargradient(x1:0,y1:0,x2:0,y2:1,"
       "stop:0 #e8f4ff, stop:0.5 #c2dff5, stop:1 #daeeff)",
    surface="qlineargradient(x1:0,y1:0,x2:0,y2:1,"
            "stop:0 rgba(255,255,255,0.82), stop:0.48 rgba(210,235,255,0.70),"
            "stop:0.49 rgba(180,218,248,0.75), stop:1 rgba(220,240,255,0.78))",
    fg="#0a2a4a", border="rgba(100,170,230,0.55)",
    hover="rgba(180,220,255,0.55)", selection="rgba(90,160,230,0.35)",
    accent="qlineargradient(x1:0,y1:0,x2:0,y2:1,"
           "stop:0 #7ad4ff, stop:0.45 #28a8f0, stop:0.46 #1090e0, stop:1 #60c8ff)",
    accent_fg="#ffffff", accent_hover="#1a90d8",
    btn="qlineargradient(x1:0,y1:0,x2:0,y2:1,"
        "stop:0 rgba(255,255,255,0.90), stop:0.48 rgba(200,230,255,0.80),"
        "stop:0.49 rgba(160,210,248,0.85), stop:1 rgba(210,235,255,0.88))",
    btn_fg="#0a2a4a", btn_border="1px solid rgba(100,170,230,0.60)",
    btn_hover="qlineargradient(x1:0,y1:0,x2:0,y2:1,"
              "stop:0 rgba(255,255,255,0.98), stop:0.48 rgba(220,240,255,0.90),"
              "stop:0.49 rgba(180,222,252,0.92), stop:1 rgba(225,242,255,0.95))",
    btn_press="qlineargradient(x1:0,y1:0,x2:0,y2:1,"
              "stop:0 rgba(160,210,248,0.90), stop:1 rgba(200,232,255,0.85))",
    tab_bg="qlineargradient(x1:0,y1:0,x2:0,y2:1,"
           "stop:0 rgba(255,255,255,0.65), stop:1 rgba(190,225,255,0.55))",
    tab_fg="#3a6080",
    tab_sel="qlineargradient(x1:0,y1:0,x2:0,y2:1,"
            "stop:0 rgba(255,255,255,0.95), stop:0.48 rgba(225,242,255,0.90),"
            "stop:0.49 rgba(185,222,252,0.92), stop:1 rgba(230,245,255,0.95))",
    tab_sel_fg="#0a2a4a",
    prog_bg="rgba(160,210,240,0.40)", glow="#28a8f0",
    extra="""
    QFrame#panel, QFrame#lpanel {
        background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
            stop:0 rgba(255,255,255,0.78), stop:0.5 rgba(205,232,252,0.72),
            stop:1 rgba(220,240,255,0.75));
        border: 1px solid rgba(120,180,230,0.55);
    }
    QLineEdit {
        background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
            stop:0 rgba(255,255,255,0.88), stop:1 rgba(215,238,255,0.80));
        border: 1.5px solid rgba(100,170,230,0.60);
    }
    QListWidget {
        background: rgba(230,244,255,0.60);
        border-right: 1px solid rgba(120,180,230,0.50);
    }
    QComboBox {
        background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
            stop:0 rgba(255,255,255,0.88), stop:1 rgba(215,238,255,0.80));
    }
    QProgressBar::chunk {
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
            stop:0 #7ad4ff, stop:0.5 #28a8f0, stop:1 #60c8ff);
    }
    QTabBar::tab:selected { border-bottom: 2px solid #28a8f0; }
    """,
  ),

  "Liquid Glass": _t(
    win_bg="qlineargradient(x1:0,y1:0,x2:1,y2:1,"
           "stop:0 #0a0a0a, stop:0.5 #111118, stop:1 #080810)",
    bg="transparent", surface="rgba(255,255,255,0.04)", fg="rgba(255,255,255,0.88)",
    border="rgba(255,255,255,0.10)", hover="rgba(255,255,255,0.07)",
    selection="rgba(255,255,255,0.14)",
    accent="rgba(255,255,255,0.85)", accent_fg="#000000",
    accent_hover="rgba(255,255,255,0.95)",
    btn="rgba(255,255,255,0.06)", btn_fg="rgba(255,255,255,0.85)",
    btn_border="1px solid rgba(255,255,255,0.10)",
    btn_hover="rgba(255,255,255,0.11)", btn_press="rgba(255,255,255,0.03)",
    tab_bg="rgba(255,255,255,0.04)", tab_fg="rgba(255,255,255,0.35)",
    tab_sel="rgba(255,255,255,0.09)", tab_sel_fg="rgba(255,255,255,0.90)",
    prog_bg="rgba(255,255,255,0.06)", glow="rgba(255,255,255,0.6)",
    extra="""
    QFrame#panel, QFrame#lpanel {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
    }
    QLineEdit {
        background: rgba(255,255,255,0.05);
        border: 1.5px solid rgba(255,255,255,0.10);
    }
    QListWidget {
        background: transparent;
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    QComboBox  { background: rgba(255,255,255,0.05); }
    QTextEdit  { background: rgba(255,255,255,0.05); }
    QTabBar::tab:selected { border-bottom: 1px solid rgba(255,255,255,0.30); }
    QProgressBar::chunk { background: rgba(255,255,255,0.70); }
    QPushButton#accent {
        background: rgba(255,255,255,0.85);
        color: #000;
        border: none;
    }
    QPushButton#accent:hover { background: rgba(255,255,255,0.95); }
    """,
  ),

  "Molten Chrome": _t(
    win_bg="qlineargradient(x1:0,y1:0,x2:0,y2:1,"
           "stop:0 #1e1e1e, stop:0.5 #141414, stop:1 #1a1a1a)",
    bg="#141414", surface="qlineargradient(x1:0,y1:0,x2:0,y2:1,"
    "stop:0 #2e2e2e, stop:0.5 #222, stop:1 #282828)",
    fg="#d8d8d8", border="#484848", hover="#303030", selection="#404040",
    accent="qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #e8e8e8,stop:1 #a0a0a0)",
    accent_fg="#111", accent_hover="#c8c8c8",
    btn="qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #484848,stop:0.5 #303030,stop:1 #3a3a3a)",
    btn_fg="#d8d8d8", btn_border="1px solid #585858",
    btn_hover="qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #585858,stop:1 #404040)",
    btn_press="qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #202020,stop:1 #303030)",
    tab_bg="qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #303030,stop:1 #222)",
    tab_fg="#888", tab_sel="#141414", tab_sel_fg="#e0e0e0",
    prog_bg="#282828", glow="#c0c0c0",
    extra="""
    QPushButton#accent {
        background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
            stop:0 #f0f0f0, stop:0.5 #b8b8b8, stop:1 #d8d8d8);
        color: #111; border: 1px solid #888; border-radius: 9px;
    }
    QProgressBar::chunk {
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
            stop:0 #e8e8e8, stop:0.5 #a8a8a8, stop:1 #d0d0d0);
    }
    """,
  ),

  "Punk": _t(
    win_bg="#000", bg="#000", surface="#080808", fg="#ffffff",
    border="#220011", hover="#110008", selection="#330022",
    accent="#ff0055", accent_fg="#ffffff", accent_hover="#cc0044",
    btn="qlineargradient(x1:0,y1:0,x2:1,y2:0,"
        "stop:0 #ff003c,stop:0.2 #ff8800,stop:0.4 #ffee00,"
        "stop:0.6 #00ff88,stop:0.8 #0099ff,stop:1 #cc00ff)",
    btn_fg="#ffffff", btn_border="none",
    btn_hover="qlineargradient(x1:0,y1:0,x2:1,y2:0,"
              "stop:0 #ff3366,stop:0.2 #ffaa00,stop:0.4 #ffff33,"
              "stop:0.6 #33ffaa,stop:0.8 #33bbff,stop:1 #ee33ff)",
    btn_press="qlineargradient(x1:0,y1:0,x2:1,y2:0,"
              "stop:0 #cc002a,stop:0.5 #009944,stop:1 #8800cc)",
    tab_bg="#080808", tab_fg="#555",
    tab_sel="qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #ff003c,stop:1 #cc00ff)",
    tab_sel_fg="#fff",
    prog_bg="#110008", glow="#ff0055",
    extra="""
    QPushButton#accent {
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
            stop:0 #ff003c, stop:1 #cc00ff);
        color: white; font-weight: bold;
    }
    QProgressBar::chunk {
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
            stop:0 #ff003c, stop:0.5 #00ff88, stop:1 #cc00ff);
    }
    """,
  ),

  "GradientZ": _t(
    win_bg="qlineargradient(x1:0,y1:0,x2:1,y2:1,"
           "stop:0 #0f0c29, stop:0.45 #302b63, stop:1 #1a1040)",
    bg="transparent", surface="rgba(80,50,160,0.18)", fg="#e8d8ff",
    border="rgba(160,100,255,0.35)", hover="rgba(110,80,200,0.22)",
    selection="rgba(180,100,255,0.40)",
    accent="qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #f953c6,stop:1 #b91d73)",
    accent_fg="#ffffff", accent_hover="#d840a0",
    btn="qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #4a5be8,stop:1 #6a3aaa)",
    btn_fg="#e8d8ff", btn_border="none",
    btn_hover="qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #6070ff,stop:1 #8050cc)",
    btn_press="qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #2a3ab0,stop:1 #4a2080)",
    tab_bg="rgba(60,40,120,0.22)", tab_fg="rgba(200,170,255,0.65)",
    tab_sel="rgba(80,50,180,0.40)", tab_sel_fg="#e8d8ff",
    prog_bg="rgba(60,40,100,0.30)", glow="#f953c6",
    extra="""
    QFrame#panel, QFrame#lpanel {
        background: rgba(60,35,130,0.20);
        border: 1px solid rgba(160,100,255,0.32);
    }
    QLineEdit { background: rgba(70,45,150,0.20); }
    QListWidget { background: rgba(60,40,120,0.18);
                  border-right: 1px solid rgba(160,100,255,0.30); }
    QProgressBar::chunk {
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
            stop:0 #f953c6, stop:1 #667eea);
    }
    """,
  ),

  "Terminal": _t(
    win_bg="#000000",
    bg="#000000", surface="#050505", fg="#39ff14",
    border="#0a3300", hover="#061a00", selection="#0d4400",
    accent="#39ff14", accent_fg="#000000", accent_hover="#20cc00",
    btn="#051000", btn_fg="#39ff14", btn_border="1px solid #0a3300",
    btn_hover="#0a2200", btn_press="#030a00",
    tab_bg="#030a00", tab_fg="#1a6600", tab_sel="#000", tab_sel_fg="#39ff14",
    prog_bg="#051000", glow="#39ff14",
    font="'Courier New', 'Lucida Console', monospace",
    extra="""
    QMainWindow {
        background: #000;
        background-image: repeating-linear-gradient(
            0deg, transparent, transparent 3px,
            rgba(0,20,0,0.18) 3px, rgba(0,20,0,0.18) 4px);
    }
    QLineEdit, QTextEdit, QComboBox { font-family: 'Courier New', monospace; }
    QPushButton { font-family: 'Courier New', monospace; letter-spacing: 1px; }
    QPushButton#accent { background: #39ff14; color: #000; font-weight: bold; }
    QPushButton#accent:hover { background: #20cc00; }
    QProgressBar::chunk { background: #39ff14; }
    QTabBar::tab:selected { color: #39ff14; border-bottom: 2px solid #39ff14; }
    """,
  ),
}

# ── Random theme generator ────────────────────────────────────────────────────
def generate_random_theme(name="RandomME") -> dict:
    def hsl(h, s, l) -> str:
        r, g, b = colorsys.hls_to_rgb(h % 1.0, l, s)
        return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

    h      = random.random()
    h_acc  = (h + 0.45 + random.random() * 0.2) % 1.0
    dark   = random.random() > 0.25

    if dark:
        bg      = hsl(h, 0.15, 0.07 + random.random() * 0.05)
        surf    = hsl(h, 0.18, 0.12 + random.random() * 0.05)
        fg      = hsl(h, 0.20, 0.86 + random.random() * 0.10)
        border  = hsl(h, 0.22, 0.20 + random.random() * 0.08)
        hover   = hsl(h, 0.20, 0.17 + random.random() * 0.07)
        btn     = hsl(h, 0.18, 0.15 + random.random() * 0.07)
        tab_fg  = hsl(h, 0.15, 0.48)
    else:
        bg      = hsl(h, 0.06, 0.94 + random.random() * 0.05)
        surf    = hsl(h, 0.08, 0.90)
        fg      = hsl(h, 0.20, 0.10 + random.random() * 0.08)
        border  = hsl(h, 0.10, 0.76)
        hover   = hsl(h, 0.10, 0.85)
        btn     = hsl(h, 0.08, 0.86)
        tab_fg  = hsl(h, 0.12, 0.52)

    al       = 0.55 + random.random() * 0.15
    acc      = hsl(h_acc, 0.75 + random.random() * 0.25, al)
    acc_hov  = hsl(h_acc, 0.75, max(0.0, al - 0.12))
    acc_fg   = "#000000" if al > 0.55 else "#ffffff"
    sel      = hsl(h_acc, 0.40, 0.30 if dark else 0.72)

    return _t(
        win_bg=bg, bg=bg, surface=surf, fg=fg,
        border=border, hover=hover, selection=sel,
        accent=acc, accent_fg=acc_fg, accent_hover=acc_hov,
        btn=btn, btn_fg=fg, btn_border=f"1px solid {border}",
        btn_hover=hover, btn_press=border,
        tab_bg=surf, tab_fg=tab_fg, tab_sel=hover, tab_sel_fg=fg,
        prog_bg=border, glow=acc,
    )

# ── Persistence ───────────────────────────────────────────────────────────────
EDITABLE_KEYS = [
    "win_bg","bg","surface","fg","border","hover","selection",
    "accent","accent_fg","accent_hover",
    "btn","btn_fg","btn_hover","btn_press",
    "tab_bg","tab_fg","tab_sel","tab_sel_fg","prog_bg","glow",
]

def save_theme(theme: dict, name: str) -> Path:
    safe = "".join(c if c.isalnum() or c in " _-" else "_" for c in name)
    path = USER_DIR / f"{safe}.json"
    out  = {k: theme.get(k, "") for k in EDITABLE_KEYS}
    out["name"]  = name
    out["font"]  = theme.get("font", "'Segoe UI', Arial, sans-serif")
    out["extra"] = theme.get("extra", "")
    path.write_text(json.dumps(out, indent=2))
    return path

def load_theme(path) -> dict:
    data = json.loads(Path(path).read_text())
    return _t(**{k: data[k] for k in data if k != "name"})

def list_user_themes() -> list[tuple[str, Path]]:
    return [(p.stem, p) for p in sorted(USER_DIR.glob("*.json"))]