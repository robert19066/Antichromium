# 🌐 AntiChromium Browser
[![icon.png](https://i.postimg.cc/kXTT7x10/icon.png)](https://postimg.cc/ZCy8cyhH)

> *we are all tired of chromium and firefox based browsers aren't we? If you use this light boi, your RAM will thank you <3 and ughh, pyqt is based on chrome sooo UGHH i have been caught lmao* - me

AntiChromium(formerly BlahBlah Broswer) is a lightweight, heavily customisable desktop browser built with **Python + PyQt6 + QtWebEngine**. It was born out of frustration with Chromium's monopoly on browser aesthetics and a desire to actually *own* your browser experience — down to every color and font. Make it **your** broswer.

---

## ✨ Features

### 🎨 Theming System
- **8 built-in themes**
    - B L A K(darker than my soul at 3am)
    - W H I T(brighter than discord light mode)
    - Dracula(perfect for productivity)
    - Win7 Nostalgia(ah trows me to the good days)
    - Liquid Glass(apple increasingly knocking on my door harder and harder)
    - Molten Chrome(Nothing is more molten than my RAM when Chrome gulps it down its mouth while Ai Overview is loading.)
    - Punk(RAINBOWS #nohomo )
    - GradientZ(OOOooOOh GRADIENTS OOOH)
    - Terminal(sudo rm -rf / --no-preserve-root. run this to unlock true digital freedom - wipe everything :D)
    - RandomME(generates a compleatly new theme every time its selected)
- **Full theme editor** — pick every single color with a visual color picker, live preview before saving
- **Import / Export** themes as JSON — share your themes with others or back them up so you can share them :O.
- **User themes** persist between sessions in `~/.blahblah_browser/themes/`

### 🗂 Tab Management
- **Horizontal tabs** (classic) or **Vertical tabs** — switchable at any time from settings
- Tab **fade-in animation** on open
- Right-click to close tabs in vertical mode
- Keyboard shortcuts: `Ctrl+T` new tab, `Ctrl+W` close tab

### 🔍 Navigation
- Smart URL bar — detects URLs vs search queries automatically
- Animated **glow effect** on the URL bar when focused (color matches your active theme) waah so cool so glow!
- Animated **progress bar** during page load so NICEEE!
- Find in page (`Ctrl+F`) with previous/next navigation

### 📐 Other
- **Zoom controls** (`Ctrl+` / `Ctrl-` / `Ctrl+0`) with live % display in settings
- **Smooth scroll** injection via JavaScript makes the page scroll smoother than butter.
- **JavaScript toggle** — disable JS globally across all tabs. why would you do that tho.
- **Bookmark sidebar** — slides in/out, double-click to navigate, add new bookmarks from settings. who uses bookmarks in the big 26 twin...
- **Keyboard shortcuts** for everything. yeah.
- `faulthandler` enabled — crashes print a real traceback instead of silently dying and letting you lose your mindstream of consciousness tabs. no more "Aw, Snap!" nonsense. t r a n s p a r e n c y    i s    k e y.

---

## 🖥 Requirements

| Dependency | Version |
|---|---|
| Python | 3.10+ |
| PyQt6(the damn library it uses for the ui) | latest |
| PyQt6-WebEngine(the web renderer) | latest |

```bash
pip install PyQt6 PyQt6-WebEngine
```
or just run installdeps.sh if ur on Unix. it also makes venv for you so you don't have to worry about it. how nice of me.
---

## 🚀 Running

```bash
git clone https://github.com/yourname/antichromium
cd antichromium
chmod +x installdeps.sh
./installdeps.sh
chmod +x start.sh 
./start.sh         
```

Or with the included launch script:
```bash
chmod +x start.sh
./start.sh
```

---

## 📁 Project Structure

```
antichromium/
├── main.py          wow I REALLY WONDER WHAT MAIN.PY DOES...
├── classes.py       housess all resources and custom widgets
|-- themes.py        contains all the built in themes and theme loading/saving logic
├── icon.png         i wonder what icon.png is for... hmmm 
├── start.sh and installdeps.sh  launch and setup scripts        
└── README.md       the file you are currently reading, contains all the info about the project and how to use it. BUT IF YOU ARE NOT A DUM DUM, YOU WILL PROBABLY FIGURE IT OUT BY JUST RUNNING installdeps.sh AND start.sh WITHOUT READING THIS README.md BECAUSE IT'S ALL PRETTY STRAIGHTFORWARD. BUT IF YOU ARE A DUM DUM, THEN THIS README.md IS HERE TO HELP YOU UNDERSTAND HOW TO USE THE BROWSER AND ALL ITS COOL FEATURES.
```

---
# How2Use - dumdum tutorial for dummies who can't figure out how to use the browser without reading this README.md
## 🎨 Creating a Custom Theme

1. Open **Settings (⚙)** → click **✏ Edit** to edit the current theme, or **＋ New** to start fresh
2. Pick colors for every UI element using the color pickers
3. Hit **👁 Preview** to see it applied live without saving
4. Hit **💾 Save** to store it permanently — it will appear in the theme dropdown
5. Use **📤 Export JSON** to save the file anywhere to share it

### Theme JSON format

```json
{
  "name": "My Theme",
  "win_bg": "#0f0f0f",
  "bg": "#0f0f0f",
  "surface": "#1a1a1a",
  "fg": "#f0f0f0",
  "border": "#2a2a2a",
  "hover": "#222222",
  "selection": "#333333",
  "accent": "#ff6ac1",
  "accent_fg": "#000000",
  "accent_hover": "#dd50a8",
  "btn": "#1e1e1e",
  "btn_fg": "#f0f0f0",
  "btn_border": "1px solid #2a2a2a",
  "btn_hover": "#282828",
  "btn_press": "#111111",
  "tab_bg": "#141414",
  "tab_fg": "#666666",
  "tab_sel": "#0f0f0f",
  "tab_sel_fg": "#f0f0f0",
  "prog_bg": "#1e1e1e",
  "glow": "#ff6ac1",
  "font": "'Segoe UI', Arial, sans-serif",
  "extra": ""
}
```

The `extra` field accepts raw Qt stylesheet CSS for anything not covered by the standard fields.

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl+T` | New tab |
| `Ctrl+W` | Close current tab |
| `Ctrl+R` / `F5` | Reload |
| `Ctrl+L` | Focus URL bar |
| `Ctrl+F` | Find in page |
| `Alt+←` | Back |
| `Alt+→` | Forward |
| `Ctrl++` | Zoom in |
| `Ctrl+-` | Zoom out |
| `Ctrl+0` | Reset zoom |

---

## 🛣 Roadmap

- [ ] Per-tab zoom memory
- [ ] Download manager
- [ ] Browser history viewer
- [ ] Extension/userscript support
- [ ] Custom CSS injection per site
- [ ] More glass-style themes (Mica, Acrylic)
- [ ] Theme marketplace / sharing

---

# 🤝 Contributing

Pull requests VERRY welcome. If you make a cool theme, feel free to open a PR to add it to the built-in list.

---

## 📜 License

MIT — do whatever you want with it but don't blame me if it breaks or causes your computer to catch on fire or something(idk how you can set your pc on fire using a browser...exept you run it from a chromebook). I am not responsible for any spontainous combustion of ram caused by NOT using this software. NOT use at your own risk.

---

*PS: tell google i like chrome but its lowk buns man like it gulps ram like i gulp butter*
