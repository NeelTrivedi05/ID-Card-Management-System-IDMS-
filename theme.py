"""
theme.py — Centralized Design System for IDMS.

Provides:
  - FONTS       : 7-level type scale (Segoe UI / system fallback)
  - THEMES      : Dark + Light palettes with semantic color roles
  - apply_ttk() : Style all ttk widgets to match the active theme
  - make_btn()  : Consistent button factory used across the app
"""
import json
import os
import tkinter as tk
from tkinter import ttk

THEME_FILE = "theme.json"

# ── Typography ────────────────────────────────────────────────
# Segoe UI ships with Windows 10/11.  Falls back gracefully.

_FAMILY = "Segoe UI"

FONTS = {
    "display":   (_FAMILY, 18, "bold"),
    "title":     (_FAMILY, 13, "bold"),
    "heading":   (_FAMILY, 12, "bold"),
    "body":      (_FAMILY, 11),
    "body_bold": (_FAMILY, 11, "bold"),
    "caption":   (_FAMILY, 9),
    "caption_b": (_FAMILY, 9, "bold"),
    "micro":     (_FAMILY, 8),
}

# ── Theme palettes ───────────────────────────────────────────

THEMES = {
    "dark": {
        # ── Surface colors ──
        "DARK_BG":       "#0f172a",       # deepest background
        "PANEL_BG":      "#1e293b",       # cards, panels, topbar
        "SURFACE":       "#334155",       # elevated surfaces (tooltip, dropdown)
        "ENTRY_BG":      "#1e293b",       # input field background
        "ENTRY_BORDER":  "#475569",       # input border (idle)
        "ENTRY_FOCUS":   "#3b82f6",       # input border (focused)
        # ── Brand ──
        "ACCENT":        "#3b82f6",       # blue — primary actions
        "ACCENT2":       "#ef4444",       # red — danger / brand accent
        "ACCENT_HOVER":  "#2563eb",       # hover state for ACCENT
        # ── Text ──
        "TEXT_MAIN":     "#f1f5f9",       # primary text
        "TEXT_SUB":      "#94a3b8",       # secondary / muted text
        "TEXT_HINT":     "#64748b",       # placeholder, hint text
        # ── Treeview ──
        "TREE_ROW_ODD":  "#1e293b",
        "TREE_ROW_EVEN": "#0f172a",
        "TREE_SELECTED": "#1d4ed8",
        # ── Semantic button colors ──
        "BTN_PRIMARY":   "#3b82f6",       # Add, Save, main action
        "BTN_SUCCESS":   "#22c55e",       # Confirm, positive
        "BTN_DANGER":    "#ef4444",       # Delete, Logout
        "BTN_WARNING":   "#f59e0b",       # Import, Demo Data
        "BTN_SECONDARY": "#475569",       # Close, Cancel, Refresh
        "BTN_INFO":      "#6366f1",       # View, Templates
        # ── Status badges ──
        "BADGE_VALID":    "#22c55e",
        "BADGE_EXPIRING": "#eab308",
        "BADGE_EXPIRED":  "#ef4444",
        # ── Role badge colors ──
        "ROLE_ADMIN":    "#ef4444",
        "ROLE_OPERATOR": "#f59e0b",
        "ROLE_VIEWER":   "#3b82f6",
        # ── Misc ──
        "SEPARATOR":     "#334155",
        "SHADOW":        "#020617",
    },
    "light": {
        # ── Surface colors ──
        "DARK_BG":       "#f1f5f9",
        "PANEL_BG":      "#ffffff",
        "SURFACE":       "#e2e8f0",
        "ENTRY_BG":      "#f8fafc",
        "ENTRY_BORDER":  "#cbd5e1",
        "ENTRY_FOCUS":   "#3b82f6",
        # ── Brand ──
        "ACCENT":        "#2563eb",
        "ACCENT2":       "#dc2626",
        "ACCENT_HOVER":  "#1d4ed8",
        # ── Text ──
        "TEXT_MAIN":     "#0f172a",
        "TEXT_SUB":      "#64748b",
        "TEXT_HINT":     "#94a3b8",
        # ── Treeview ──
        "TREE_ROW_ODD":  "#f8fafc",
        "TREE_ROW_EVEN": "#e2e8f0",
        "TREE_SELECTED": "#2563eb",
        # ── Semantic button colors ──
        "BTN_PRIMARY":   "#2563eb",
        "BTN_SUCCESS":   "#16a34a",
        "BTN_DANGER":    "#dc2626",
        "BTN_WARNING":   "#d97706",
        "BTN_SECONDARY": "#64748b",
        "BTN_INFO":      "#4f46e5",
        # ── Status badges ──
        "BADGE_VALID":    "#16a34a",
        "BADGE_EXPIRING": "#ca8a04",
        "BADGE_EXPIRED":  "#dc2626",
        # ── Role badge colors ──
        "ROLE_ADMIN":    "#dc2626",
        "ROLE_OPERATOR": "#d97706",
        "ROLE_VIEWER":   "#2563eb",
        # ── Misc ──
        "SEPARATOR":     "#e2e8f0",
        "SHADOW":        "#94a3b8",
    },
}

# ── Active state (module-level singleton) ─────────────────────
_current = "dark"


def load():
    """Load theme preference from theme.json (defaults to dark)."""
    global _current
    if os.path.exists(THEME_FILE):
        try:
            with open(THEME_FILE) as f:
                data = json.load(f)
                if data.get("theme") in THEMES:
                    _current = data["theme"]
        except Exception:
            pass
    return _current


def save(name: str):
    """Persist the chosen theme to theme.json."""
    global _current
    if name in THEMES:
        _current = name
        try:
            with open(THEME_FILE, "w") as f:
                json.dump({"theme": name}, f)
        except Exception:
            pass


def get() -> dict:
    """Return the active palette dict."""
    return THEMES[_current]


def current_name() -> str:
    return _current


def toggle():
    """Switch between dark ↔ light and persist."""
    new = "light" if _current == "dark" else "dark"
    save(new)
    return new


def apply_ttk(root):
    """Re-apply ttk widget styles to match the current theme."""
    t = get()
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure("Treeview",
                    background=t["PANEL_BG"],
                    foreground=t["TEXT_MAIN"],
                    fieldbackground=t["PANEL_BG"],
                    rowheight=32,
                    font=FONTS["body"])
    style.configure("Treeview.Heading",
                    background=t["ACCENT"],
                    foreground="#ffffff",
                    font=FONTS["body_bold"],
                    relief="flat",
                    padding=[8, 6])
    style.map("Treeview",
              background=[("selected", t["TREE_SELECTED"])],
              foreground=[("selected", "#ffffff")])

    style.configure("TNotebook",      background=t["DARK_BG"], borderwidth=0)
    style.configure("TNotebook.Tab",  background=t["PANEL_BG"],
                    foreground=t["TEXT_SUB"], padding=[18, 8],
                    font=FONTS["body_bold"])
    style.map("TNotebook.Tab",
              background=[("selected", t["ACCENT"])],
              foreground=[("selected", "#ffffff")])

    style.configure("TCombobox",
                    fieldbackground=t["ENTRY_BG"],
                    background=t["ENTRY_BG"],
                    foreground=t["TEXT_MAIN"],
                    selectbackground=t["ACCENT"],
                    selectforeground="#ffffff",
                    padding=[6, 4])

    style.configure("Vertical.TScrollbar", background=t["PANEL_BG"],
                    troughcolor=t["DARK_BG"], borderwidth=0)
    style.configure("Horizontal.TScrollbar", background=t["PANEL_BG"],
                    troughcolor=t["DARK_BG"], borderwidth=0)


# ── Button factory ────────────────────────────────────────────

def make_btn(parent, text, color_key="BTN_PRIMARY", command=None,
             font_key="body", icon=None, **pack_opts):
    """
    Create a styled tk.Button using theme colors.

    Parameters
    ----------
    parent    : parent widget
    text      : button label (can include emoji)
    color_key : key in the theme dict (e.g. "BTN_DANGER")
    command   : callback
    font_key  : key in FONTS dict
    icon      : optional prefix emoji (prepended to text)
    **pack_opts : forwarded to .pack()

    Returns the Button widget (already packed).
    """
    t = get()
    display_text = f"{icon} {text}" if icon else text
    bg = t.get(color_key, t["BTN_PRIMARY"])

    # Derive a darker hover shade from the actual button color
    hover_bg = _darken_hex(bg, 0.18)

    btn = tk.Button(
        parent, text=display_text,
        font=FONTS.get(font_key, FONTS["body"]),
        bg=bg, fg="#ffffff",
        activebackground=hover_bg,
        activeforeground="#ffffff",
        relief="flat", cursor="hand2",
        bd=0, highlightthickness=0,
        command=command,
    )

    # Default pack options
    defaults = {"side": "left", "padx": 3, "ipady": 5, "ipadx": 10}
    defaults.update(pack_opts)
    btn.pack(**defaults)
    return btn



def _darken_hex(hex_color: str, amount: float = 0.15) -> str:
    """Return a hex color darkened by `amount` (0-1)."""
    try:
        h = hex_color.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        factor = 1.0 - amount
        r, g, b = int(r * factor), int(g * factor), int(b * factor)
        return f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        return hex_color


# Load preference at import time
load()
