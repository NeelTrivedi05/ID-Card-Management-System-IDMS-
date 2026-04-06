import tkinter as tk
from tkinter import messagebox
import os

try:
    from PIL import Image, ImageTk, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

DARK_BG  = "#1a1a2e"
PANEL_BG = "#16213e"
ACCENT   = "#0f3460"
ACCENT2  = "#e94560"

# ── Card dimensions (pixels) ──────────────────────────────────
CARD_W = 380
CARD_H = 230

class CardPreviewWindow:
    def __init__(self, parent, tab_type, record):
        self.parent   = parent
        self.tab_type = tab_type
        self.record   = record

        self.win = tk.Toplevel(parent)
        self.win.title(f"ID Card Preview — {record['name']}")
        self.win.geometry("500x420")
        self.win.configure(bg=DARK_BG)
        self.win.resizable(False, False)
        self.win.grab_set()

        # Centre
        self.win.update_idletasks()
        x = (self.win.winfo_screenwidth()  // 2) - 250
        y = (self.win.winfo_screenheight() // 2) - 210
        self.win.geometry(f"500x420+{x}+{y}")

        self._build_ui()

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self.win, bg=PANEL_BG, pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text="ID Card Preview",
                 font=("Arial", 13, "bold"),
                 bg=PANEL_BG, fg="white").pack()
        tk.Label(hdr, text="This is how the card will look",
                 font=("Arial", 9), bg=PANEL_BG, fg="#a0aec0").pack()

        # Canvas area (centred)
        canvas_frame = tk.Frame(self.win, bg=DARK_BG, pady=20)
        canvas_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(canvas_frame,
                                width=CARD_W + 20,
                                height=CARD_H + 20,
                                bg=DARK_BG,
                                highlightthickness=0)
        self.canvas.pack(anchor="center")

        # Draw the card
        self._draw_card()

        # Bottom buttons
        btn_frame = tk.Frame(self.win, bg=DARK_BG, pady=10)
        btn_frame.pack(fill="x", padx=20)

        tk.Button(btn_frame, text="Close",
                  font=("Arial", 10), bg=ACCENT2, fg="white",
                  relief="flat", cursor="hand2",
                  command=self.win.destroy
                  ).pack(side="right", ipady=6, ipadx=16)

    # ── Draw card on canvas ───────────────────────────────────

    def _draw_card(self):
        c  = self.canvas
        r  = self.record
        ox = 10   # offset x (shadow/padding)
        oy = 10   # offset y

        # ── Shadow ───────────────────────────────────────────
        c.create_rectangle(ox + 4, oy + 4,
                           ox + CARD_W + 4, oy + CARD_H + 4,
                           fill="#111122", outline="")

        # ── Card background ───────────────────────────────────
        c.create_rectangle(ox, oy, ox + CARD_W, oy + CARD_H,
                           fill="#1e2a4a", outline="#3a4a7a", width=2)

        # ── Left accent strip ─────────────────────────────────
        c.create_rectangle(ox, oy, ox + 10, oy + CARD_H,
                           fill="#e94560", outline="")

        # ── Header band ───────────────────────────────────────
        c.create_rectangle(ox + 10, oy, ox + CARD_W, oy + 52,
                           fill="#0f3460", outline="")

        # College name
        c.create_text(ox + 200, oy + 16,
                      text="SHRI BHAGUBHAI MAFATLAL POLYTECHNIC",
                      font=("Arial", 8, "bold"), fill="white", anchor="center")
        c.create_text(ox + 200, oy + 30,
                      text="Computer Engineering Department",
                      font=("Arial", 7), fill="#a0c4ff", anchor="center")

        # Card type badge
        badge_text = "STUDENT ID CARD" if self.tab_type == "student" else "STAFF ID CARD"
        c.create_rectangle(ox + 130, oy + 38, ox + 270, oy + 54,
                           fill="#e94560", outline="")
        c.create_text(ox + 200, oy + 46,
                      text=badge_text,
                      font=("Arial", 7, "bold"), fill="white", anchor="center")

        # ── Photo area ────────────────────────────────────────
        photo_x = ox + 20
        photo_y = oy + 62
        photo_w = 80
        photo_h = 96

        self._draw_photo(c, photo_x, photo_y, photo_w, photo_h)

        # ── Info area ─────────────────────────────────────────
        info_x = ox + 115
        info_y = oy + 66

        name = r.get("name", "N/A")
        c.create_text(info_x, info_y,
                      text=name,
                      font=("Arial", 12, "bold"), fill="white", anchor="nw")

        # Divider
        c.create_line(info_x, info_y + 18, ox + CARD_W - 12, info_y + 18,
                      fill="#e94560", width=1)

        # Fields differ by type
        if self.tab_type == "student":
            fields = [
                ("Roll No",   r.get("roll_no",    "N/A")),
                ("Dept",      r.get("department", "N/A")),
                ("Year",      r.get("year",       "N/A")),
                ("Contact",   r.get("contact",    "—")),
            ]
        else:
            fields = [
                ("Emp ID",    r.get("employee_id",  "N/A")),
                ("Dept",      r.get("department",   "N/A")),
                ("Post",      r.get("designation",  "N/A")),
                ("Contact",   r.get("contact",      "—")),
            ]

        line_y = info_y + 26
        for label, value in fields:
            c.create_text(info_x, line_y,
                          text=f"{label}:",
                          font=("Arial", 8), fill="#a0aec0", anchor="nw")
            # Truncate long values
            val_str = str(value)[:28] if value else "—"
            c.create_text(info_x + 55, line_y,
                          text=val_str,
                          font=("Arial", 8, "bold"), fill="white", anchor="nw")
            line_y += 18

        # ── Footer bar ────────────────────────────────────────
        footer_y = oy + CARD_H - 28
        c.create_rectangle(ox + 10, footer_y, ox + CARD_W, oy + CARD_H,
                           fill="#0a1a30", outline="")

        issue = r.get("issue_date", "N/A")
        c.create_text(ox + 20, footer_y + 14,
                      text=f"Issued: {issue}",
                      font=("Arial", 7), fill="#a0aec0", anchor="w")

        c.create_text(ox + CARD_W - 15, footer_y + 14,
                      text="SVKM's SBMP",
                      font=("Arial", 7, "bold"), fill="#a0c4ff", anchor="e")

        # ── Barcode placeholder ───────────────────────────────
        bar_x = ox + 20
        bar_y = oy + 168
        for i in range(28):
            bar_color = "#e94560" if i % 3 == 0 else "#ffffff"
            bar_width = 2 if i % 5 == 0 else 1
            c.create_rectangle(bar_x + i * 3, bar_y,
                               bar_x + i * 3 + bar_width, bar_y + 18,
                               fill=bar_color, outline="")

    def _draw_photo(self, canvas, x, y, w, h):
        photo_path = self.record.get("photo_path", "")

        if PIL_AVAILABLE and photo_path and os.path.exists(photo_path):
            try:
                img = Image.open(photo_path).convert("RGB")
                img = img.resize((w, h), Image.LANCZOS)
                self._photo_img = ImageTk.PhotoImage(img)
                canvas.create_image(x, y, anchor="nw", image=self._photo_img)
                # Border around photo
                canvas.create_rectangle(x, y, x + w, y + h,
                                        outline="#e94560", width=2, fill="")
                return
            except Exception:
                pass

        # Fallback: placeholder box
        canvas.create_rectangle(x, y, x + w, y + h,
                                fill="#0f2040", outline="#3a4a7a", width=1)
        canvas.create_text(x + w // 2, y + h // 2 - 10,
                           text="👤", font=("Arial", 24), fill="#3a4a7a")
        canvas.create_text(x + w // 2, y + h // 2 + 16,
                           text="No Photo", font=("Arial", 7), fill="#3a4a7a")
