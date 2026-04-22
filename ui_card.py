import tkinter as tk
from tkinter import messagebox, filedialog
import os
import json
import theme as _theme

try:
    from PIL import Image, ImageTk, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import qrcode
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

# ── Card dimensions ──────────────────────────────────────────
CARD_W = 450
CARD_H = 280

# ── Fonts helper for PIL ─────────────────────────────────────

def _get_font(size, bold=False):
    """Try loading Segoe UI, fallback to Arial, then default."""
    if bold:
        names = ["segoeuib.ttf", "arialbd.ttf"]
    else:
        names = ["segoeui.ttf", "arial.ttf"]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _resolve_template():
    """Load template from templates.json, merged over defaults."""
    template = {
        "card_w": CARD_W, "card_h": CARD_H,
        "bg_color": "#1e293b", "outline_color": "#475569", "accent_color": "#3b82f6",
        "header_bg": "#0f172a", "footer_bg": "#0f172a",
        "text_primary": "#f1f5f9", "text_secondary": "#94a3b8", "text_accent": "#93c5fd",
        "college_text": "SHRI BHAGUBHAI MAFATLAL POLYTECHNIC",
        "college_subtext": "Computer Engineering Department",
        "photo_rect": {"x": 24, "y": 72, "w": 96, "h": 116},
        "info_start": {"x": 136, "y": 78},
        "barcode_start": {"x": 24, "y": 200}
    }
    try:
        if os.path.exists("templates.json"):
            with open("templates.json", "r") as f:
                data = json.load(f)
                tmpl_name = data.get("current_template", "Default")
                saved = data.get("templates", {}).get(tmpl_name, {})
                for key, val in saved.items():
                    if val != "" and val is not None:
                        template[key] = val
    except Exception:
        pass
    return template


class CardPreviewWindow:
    def __init__(self, parent, tab_type, record):
        self.parent   = parent
        self.tab_type = tab_type
        self.record   = record

        t = _theme.get()
        F = _theme.FONTS

        self.win = tk.Toplevel(parent)
        self.win.title(f"ID Card Preview — {record['name']}")
        self.win.geometry("560x480")
        self.win.configure(bg=t["DARK_BG"])
        self.win.resizable(False, False)
        self.win.grab_set()

        # Centre
        self.win.update_idletasks()
        x = (self.win.winfo_screenwidth()  // 2) - 280
        y = (self.win.winfo_screenheight() // 2) - 240
        self.win.geometry(f"560x480+{x}+{y}")

        self._build_ui()

    def _build_ui(self):
        t = _theme.get()
        F = _theme.FONTS

        # Header
        hdr = tk.Frame(self.win, bg=t["ACCENT"], pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text="ID Card Preview", font=F["title"],
                 bg=t["ACCENT"], fg="#ffffff").pack()
        tk.Label(hdr, text="This is how the card will look",
                 font=F["caption"], bg=t["ACCENT"], fg="#dbeafe").pack()

        # Canvas area
        canvas_frame = tk.Frame(self.win, bg=t["DARK_BG"], pady=16)
        canvas_frame.pack(fill="both", expand=True)

        template = _resolve_template()
        cw = template.get("card_w", CARD_W)
        ch = template.get("card_h", CARD_H)

        self.canvas = tk.Canvas(canvas_frame,
                                width=cw + 24,
                                height=ch + 24,
                                bg=t["DARK_BG"],
                                highlightthickness=0)
        self.canvas.pack(anchor="center")

        self._draw_card(template)

        # Bottom buttons
        btn_frame = tk.Frame(self.win, bg=t["DARK_BG"], pady=10)
        btn_frame.pack(fill="x", padx=24)

        _theme.make_btn(btn_frame, "Close", "BTN_SECONDARY",
                        command=self.win.destroy, font_key="body",
                        side="right")

        if PIL_AVAILABLE:
            _theme.make_btn(btn_frame, "Export PDF", "BTN_SUCCESS",
                            command=self.export_pdf, font_key="body",
                            icon="📄", side="right", padx=8)

    # ── Draw card on canvas ───────────────────────────────────

    def _draw_card(self, template=None):
        c  = self.canvas
        r  = self.record
        ox = 12   # offset
        oy = 12

        if template is None:
            template = _resolve_template()

        cw = template.get("card_w", CARD_W)
        ch = template.get("card_h", CARD_H)

        # Shadow
        c.create_rectangle(ox + 5, oy + 5, ox + cw + 5, oy + ch + 5,
                           fill="#020617", outline="")

        # Card background
        c.create_rectangle(ox, oy, ox + cw, oy + ch,
                           fill=template["bg_color"],
                           outline=template["outline_color"], width=2)

        # Left accent strip
        c.create_rectangle(ox, oy, ox + 10, oy + ch,
                           fill=template["accent_color"], outline="")

        # Header band
        c.create_rectangle(ox + 10, oy, ox + cw, oy + 60,
                           fill=template["header_bg"], outline="")

        # College name
        c.create_text(ox + (cw // 2) + 5, oy + 20,
                      text=template["college_text"],
                      font=("Segoe UI", 10, "bold"),
                      fill=template["text_primary"], anchor="center")
        c.create_text(ox + (cw // 2) + 5, oy + 36,
                      text=template["college_subtext"],
                      font=("Segoe UI", 8),
                      fill=template["text_accent"], anchor="center")

        # Card type badge
        badge_text = "STUDENT ID CARD" if self.tab_type == "student" else "STAFF ID CARD"
        badge_w = 130
        badge_cx = ox + (cw // 2) + 5
        c.create_rectangle(badge_cx - badge_w // 2, oy + 46,
                           badge_cx + badge_w // 2, oy + 62,
                           fill=template["accent_color"], outline="")
        c.create_text(badge_cx, oy + 54,
                      text=badge_text,
                      font=("Segoe UI", 8, "bold"),
                      fill=template["text_primary"], anchor="center")

        # Photo area
        prect = template["photo_rect"]
        photo_x = ox + prect["x"]
        photo_y = oy + prect["y"]
        photo_w = prect["w"]
        photo_h = prect["h"]
        self._draw_photo(c, photo_x, photo_y, photo_w, photo_h, template["accent_color"])

        # Info area
        istart = template["info_start"]
        info_x = ox + istart["x"]
        info_y = oy + istart["y"]

        name = r.get("name", "N/A")
        c.create_text(info_x, info_y,
                      text=name,
                      font=("Segoe UI", 14, "bold"),
                      fill=template["text_primary"], anchor="nw")

        # Divider
        c.create_line(info_x, info_y + 22, ox + cw - 16, info_y + 22,
                      fill=template["accent_color"], width=1)

        # Fields
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

        line_y = info_y + 30
        for label, value in fields:
            c.create_text(info_x, line_y,
                          text=f"{label}:",
                          font=("Segoe UI", 9),
                          fill=template["text_secondary"], anchor="nw")
            val_str = str(value)[:32] if value else "—"
            c.create_text(info_x + 65, line_y,
                          text=val_str,
                          font=("Segoe UI", 9, "bold"),
                          fill=template["text_primary"], anchor="nw")
            line_y += 22

        # Footer bar
        footer_y = oy + ch - 32
        c.create_rectangle(ox + 10, footer_y, ox + cw, oy + ch,
                           fill=template["footer_bg"], outline="")

        issue = r.get("issue_date", "N/A")
        c.create_text(ox + 24, footer_y + 16,
                      text=f"Issued: {issue}",
                      font=("Segoe UI", 8),
                      fill=template["text_secondary"], anchor="w")
        c.create_text(ox + cw - 16, footer_y + 16,
                      text="SVKM's SBMP",
                      font=("Segoe UI", 8, "bold"),
                      fill=template["text_accent"], anchor="e")

        # QR Code
        bstart = template["barcode_start"]
        bar_x = ox + bstart["x"]
        bar_y = oy + bstart["y"]

        if QR_AVAILABLE and PIL_AVAILABLE:
            qr_pil = self._generate_qr_pil(size=64)
            if qr_pil:
                self._qr_tk = ImageTk.PhotoImage(qr_pil)
                c.create_image(bar_x, bar_y, anchor="nw", image=self._qr_tk)
                c.create_text(bar_x + 32, bar_y + 68,
                              text="Scan to verify",
                              font=("Segoe UI", 6),
                              fill=template["text_secondary"], anchor="center")
            else:
                self._draw_fallback_barcode(c, bar_x, bar_y, template)
        else:
            self._draw_fallback_barcode(c, bar_x, bar_y, template)

    def _draw_fallback_barcode(self, c, bar_x, bar_y, template):
        for i in range(30):
            bar_color = template["accent_color"] if i % 3 == 0 else "#ffffff"
            bar_width = 2 if i % 5 == 0 else 1
            c.create_rectangle(bar_x + i * 3, bar_y,
                               bar_x + i * 3 + bar_width, bar_y + 22,
                               fill=bar_color, outline="")

    def _draw_photo(self, canvas, x, y, w, h, border_color="#3b82f6"):
        photo_path = self.record.get("photo_path", "")

        if PIL_AVAILABLE and photo_path and os.path.exists(photo_path):
            try:
                img = Image.open(photo_path).convert("RGB")
                img = img.resize((w, h), Image.LANCZOS)
                self._photo_img = ImageTk.PhotoImage(img)
                canvas.image = self._photo_img
                canvas.create_image(x, y, anchor="nw", image=self._photo_img)
                canvas.create_rectangle(x, y, x + w, y + h,
                                        outline=border_color, width=2, fill="")
                return
            except Exception:
                pass

        # Fallback: silhouette placeholder
        canvas.create_rectangle(x, y, x + w, y + h,
                                fill="#1e293b", outline="#475569", width=1)
        canvas.create_text(x + w // 2, y + h // 2 - 12,
                           text="👤", font=("Segoe UI", 28), fill="#475569")
        canvas.create_text(x + w // 2, y + h // 2 + 20,
                           text="No Photo", font=("Segoe UI", 8), fill="#475569")

    # ── QR Code ───────────────────────────────────────────────

    def _qr_data_string(self):
        r = self.record
        if self.tab_type == "student":
            return (
                f"NAME: {r.get('name', 'N/A')} | "
                f"ROLL: {r.get('roll_no', 'N/A')} | "
                f"DEPT: {r.get('department', 'N/A')} | "
                f"YEAR: {r.get('year', 'N/A')} | "
                f"ISSUED: {r.get('issue_date', 'N/A')}"
            )
        else:
            return (
                f"NAME: {r.get('name', 'N/A')} | "
                f"EMP: {r.get('employee_id', 'N/A')} | "
                f"DEPT: {r.get('department', 'N/A')} | "
                f"POST: {r.get('designation', 'N/A')} | "
                f"ISSUED: {r.get('issue_date', 'N/A')}"
            )

    def _generate_qr_pil(self, size):
        if not (QR_AVAILABLE and PIL_AVAILABLE):
            return None
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=2, border=1,
            )
            qr.add_data(self._qr_data_string())
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="#f1f5f9", back_color="#1e293b")
            return qr_img.resize((size, size), Image.LANCZOS)
        except Exception:
            return None

    # ── PIL image generation (for PDF) ────────────────────────

    def _generate_image(self):
        r = self.record
        template = _resolve_template()
        cw = template.get("card_w", CARD_W)
        ch = template.get("card_h", CARD_H)

        img = Image.new("RGB", (cw, ch), template["bg_color"])
        d = ImageDraw.Draw(img)

        # Accent strip
        d.rectangle([0, 0, 10, ch], fill=template["accent_color"])
        # Header
        d.rectangle([10, 0, cw, 60], fill=template["header_bg"])

        f_college = _get_font(13, True)
        f_sub     = _get_font(11, False)
        f_sub_b   = _get_font(11, True)
        f_name    = _get_font(18, True)
        f_label   = _get_font(12, False)
        f_value   = _get_font(12, True)
        f_small   = _get_font(10, False)
        f_small_b = _get_font(10, True)

        # College name
        d.text((cw // 2, 20), template["college_text"], font=f_college,
               fill=template["text_primary"], anchor="mm")
        d.text((cw // 2, 36), template["college_subtext"], font=f_sub,
               fill=template["text_accent"], anchor="mm")

        # Badge
        badge_text = "STUDENT ID CARD" if self.tab_type == "student" else "STAFF ID CARD"
        d.rectangle([cw // 2 - 70, 46, cw // 2 + 70, 62], fill=template["accent_color"])
        d.text((cw // 2, 54), badge_text, font=f_sub_b,
               fill=template["text_primary"], anchor="mm")

        # Photo
        prect = template["photo_rect"]
        px, py, pw, ph = prect["x"], prect["y"], prect["w"], prect["h"]
        photo_path = r.get("photo_path", "")
        if photo_path and os.path.exists(photo_path):
            try:
                p_img = Image.open(photo_path).convert("RGB")
                p_img = p_img.resize((pw, ph), Image.LANCZOS)
                img.paste(p_img, (px, py))
            except Exception:
                pass
        d.rectangle([px, py, px + pw, py + ph], outline=template["accent_color"], width=2)

        # Info
        istart = template["info_start"]
        ix, iy = istart["x"], istart["y"]

        name = r.get("name", "N/A")
        d.text((ix, iy), name, font=f_name, fill=template["text_primary"], anchor="la")
        d.line([ix, iy + 22, cw - 16, iy + 22], fill=template["accent_color"], width=1)

        if self.tab_type == "student":
            fields = [
                ("Roll No", r.get("roll_no", "N/A")),
                ("Dept",    r.get("department", "N/A")),
                ("Year",    r.get("year", "N/A")),
                ("Contact", r.get("contact", "—")),
            ]
        else:
            fields = [
                ("Emp ID",  r.get("employee_id", "N/A")),
                ("Dept",    r.get("department", "N/A")),
                ("Post",    r.get("designation", "N/A")),
                ("Contact", r.get("contact", "—")),
            ]

        ly = iy + 30
        for lbl, val in fields:
            d.text((ix, ly), f"{lbl}:", font=f_label,
                   fill=template["text_secondary"], anchor="la")
            val_str = str(val)[:32] if val else "—"
            d.text((ix + 65, ly), val_str, font=f_value,
                   fill=template["text_primary"], anchor="la")
            ly += 22

        # Footer
        fy = ch - 32
        d.rectangle([10, fy, cw, ch], fill=template["footer_bg"])
        issue = r.get("issue_date", "N/A")
        d.text((24, fy + 16), f"Issued: {issue}", font=f_small,
               fill=template["text_secondary"], anchor="lm")
        d.text((cw - 16, fy + 16), "SVKM's SBMP", font=f_small_b,
               fill=template["text_accent"], anchor="rm")

        # QR Code
        bx, by = template["barcode_start"]["x"], template["barcode_start"]["y"]
        qr_pil = self._generate_qr_pil(size=64)
        if qr_pil:
            img.paste(qr_pil, (bx, by))
            d.text((bx + 32, by + 68), "Scan to verify",
                   font=f_small, fill=template["text_secondary"], anchor="mm")
        else:
            for i in range(30):
                bc = template["accent_color"] if i % 3 == 0 else "#ffffff"
                bw = 2 if i % 5 == 0 else 1
                d.rectangle([bx + i * 3, by, bx + i * 3 + bw, by + 22], fill=bc)

        return img

    def export_pdf(self):
        if not PIL_AVAILABLE:
            messagebox.showerror("Error", "Pillow is not installed. Run: pip install Pillow")
            return

        name = self.record.get("name", "card").replace(" ", "_").lower()
        filepath = filedialog.asksaveasfilename(
            title="Export ID Card",
            defaultextension=".pdf",
            initialfile=f"{name}_id.pdf",
            filetypes=[("PDF Document", "*.pdf"), ("PNG Image", "*.png"), ("All Files", "*.*")]
        )
        if not filepath:
            return

        img = self._generate_image()
        try:
            if filepath.lower().endswith(".pdf"):
                img.save(filepath, "PDF", resolution=100.0)
            else:
                img.save(filepath)
            messagebox.showinfo("Success", f"ID Card exported to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Export Failed", str(e))


# ══════════════════════════════════════════════════════════════
#  BATCH EXPORT
# ══════════════════════════════════════════════════════════════

def batch_export_pdf(records, tab_type, filepath):
    if not PIL_AVAILABLE:
        return False, "Pillow is not installed. Run: pip install Pillow"
    if not records:
        return False, "No records to export."

    try:
        A4_W, A4_H = 2480, 3508
        MARGIN_TOP = 200
        CARD_GAP  = 120

        pages = []

        card_images = []
        for rec in records:
            helper = _BatchCardHelper(tab_type, rec)
            card_images.append(helper.generate_image())

        sample_w, sample_h = card_images[0].size
        scale_factor = min((A4_W - 400) / sample_w, 1200 / sample_h)
        card_disp_w = int(sample_w * scale_factor)
        card_disp_h = int(sample_h * scale_factor)
        center_x = (A4_W - card_disp_w) // 2

        for i in range(0, len(card_images), 2):
            page = Image.new("RGB", (A4_W, A4_H), "#ffffff")
            draw = ImageDraw.Draw(page)

            hdr_font = _get_font(48, True)
            sub_font = _get_font(32, False)

            draw.text((A4_W // 2, 80), "SHRI BHAGUBHAI MAFATLAL POLYTECHNIC",
                      font=hdr_font, fill="#0f172a", anchor="mm")
            draw.text((A4_W // 2, 130),
                      f"{'Student' if tab_type == 'student' else 'Staff'} ID Cards — Batch Export",
                      font=sub_font, fill="#64748b", anchor="mm")
            draw.line([(200, 160), (A4_W - 200, 160)], fill="#3b82f6", width=3)

            # Card 1
            card1 = card_images[i].resize((card_disp_w, card_disp_h), Image.LANCZOS)
            y1 = MARGIN_TOP + 50
            page.paste(card1, (center_x, y1))
            draw.text((center_x, y1 - 20),
                      f"#{i + 1}  —  {records[i].get('name', 'N/A')}",
                      font=sub_font, fill="#334155", anchor="la")

            # Card 2
            if i + 1 < len(card_images):
                card2 = card_images[i + 1].resize((card_disp_w, card_disp_h), Image.LANCZOS)
                y2 = y1 + card_disp_h + CARD_GAP
                page.paste(card2, (center_x, y2))
                draw.text((center_x, y2 - 20),
                          f"#{i + 2}  —  {records[i + 1].get('name', 'N/A')}",
                          font=sub_font, fill="#334155", anchor="la")

            page_num = (i // 2) + 1
            total_pages = (len(card_images) + 1) // 2
            draw.text((A4_W // 2, A4_H - 80),
                      f"Page {page_num} of {total_pages}",
                      font=sub_font, fill="#94a3b8", anchor="mm")

            pages.append(page)

        if len(pages) == 1:
            pages[0].save(filepath, "PDF", resolution=300.0)
        else:
            pages[0].save(filepath, "PDF", resolution=300.0,
                          save_all=True, append_images=pages[1:])

        return True, (
            f"Batch PDF exported successfully!\n\n"
            f"  📄 Cards: {len(card_images)}\n"
            f"  📃 Pages: {len(pages)}\n"
            f"  📁 File: {filepath}"
        )
    except Exception as e:
        return False, f"Batch export failed: {str(e)}"


class _BatchCardHelper:
    """Lightweight helper for batch image generation without tkinter."""

    def __init__(self, tab_type, record):
        self.tab_type = tab_type
        self.record = record

    def _qr_data_string(self):
        r = self.record
        if self.tab_type == "student":
            return (
                f"NAME: {r.get('name', 'N/A')} | "
                f"ROLL: {r.get('roll_no', 'N/A')} | "
                f"DEPT: {r.get('department', 'N/A')} | "
                f"YEAR: {r.get('year', 'N/A')} | "
                f"ISSUED: {r.get('issue_date', 'N/A')}"
            )
        else:
            return (
                f"NAME: {r.get('name', 'N/A')} | "
                f"EMP: {r.get('employee_id', 'N/A')} | "
                f"DEPT: {r.get('department', 'N/A')} | "
                f"POST: {r.get('designation', 'N/A')} | "
                f"ISSUED: {r.get('issue_date', 'N/A')}"
            )

    def _generate_qr_pil(self, size):
        if not (QR_AVAILABLE and PIL_AVAILABLE):
            return None
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=2, border=1,
            )
            qr.add_data(self._qr_data_string())
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="#f1f5f9", back_color="#1e293b")
            return qr_img.resize((size, size), Image.LANCZOS)
        except Exception:
            return None

    def generate_image(self):
        r = self.record
        template = _resolve_template()
        cw = template.get("card_w", CARD_W)
        ch = template.get("card_h", CARD_H)

        img = Image.new("RGB", (cw, ch), template["bg_color"])
        d = ImageDraw.Draw(img)

        d.rectangle([0, 0, 10, ch], fill=template["accent_color"])
        d.rectangle([10, 0, cw, 60], fill=template["header_bg"])

        f_college = _get_font(13, True)
        f_sub     = _get_font(11, False)
        f_sub_b   = _get_font(11, True)
        f_name    = _get_font(18, True)
        f_label   = _get_font(12, False)
        f_value   = _get_font(12, True)
        f_small   = _get_font(10, False)
        f_small_b = _get_font(10, True)

        d.text((cw // 2, 20), template["college_text"], font=f_college,
               fill=template["text_primary"], anchor="mm")
        d.text((cw // 2, 36), template["college_subtext"], font=f_sub,
               fill=template["text_accent"], anchor="mm")

        badge_text = "STUDENT ID CARD" if self.tab_type == "student" else "STAFF ID CARD"
        d.rectangle([cw // 2 - 70, 46, cw // 2 + 70, 62], fill=template["accent_color"])
        d.text((cw // 2, 54), badge_text, font=f_sub_b,
               fill=template["text_primary"], anchor="mm")

        prect = template["photo_rect"]
        px, py, pw, ph = prect["x"], prect["y"], prect["w"], prect["h"]
        photo_path = r.get("photo_path", "")
        if photo_path and os.path.exists(photo_path):
            try:
                p_img = Image.open(photo_path).convert("RGB")
                p_img = p_img.resize((pw, ph), Image.LANCZOS)
                img.paste(p_img, (px, py))
            except Exception:
                pass
        d.rectangle([px, py, px + pw, py + ph], outline=template["accent_color"], width=2)

        istart = template["info_start"]
        ix, iy = istart["x"], istart["y"]

        name = r.get("name", "N/A")
        d.text((ix, iy), name, font=f_name, fill=template["text_primary"], anchor="la")
        d.line([ix, iy + 22, cw - 16, iy + 22], fill=template["accent_color"], width=1)

        if self.tab_type == "student":
            fields = [
                ("Roll No", r.get("roll_no", "N/A")),
                ("Dept",    r.get("department", "N/A")),
                ("Year",    r.get("year", "N/A")),
                ("Contact", r.get("contact", "—")),
            ]
        else:
            fields = [
                ("Emp ID",  r.get("employee_id", "N/A")),
                ("Dept",    r.get("department", "N/A")),
                ("Post",    r.get("designation", "N/A")),
                ("Contact", r.get("contact", "—")),
            ]

        ly = iy + 30
        for lbl, val in fields:
            d.text((ix, ly), f"{lbl}:", font=f_label,
                   fill=template["text_secondary"], anchor="la")
            val_str = str(val)[:32] if val else "—"
            d.text((ix + 65, ly), val_str, font=f_value,
                   fill=template["text_primary"], anchor="la")
            ly += 22

        fy = ch - 32
        d.rectangle([10, fy, cw, ch], fill=template["footer_bg"])
        issue = r.get("issue_date", "N/A")
        d.text((24, fy + 16), f"Issued: {issue}", font=f_small,
               fill=template["text_secondary"], anchor="lm")
        d.text((cw - 16, fy + 16), "SVKM's SBMP", font=f_small_b,
               fill=template["text_accent"], anchor="rm")

        bx, by = template["barcode_start"]["x"], template["barcode_start"]["y"]
        qr_pil = self._generate_qr_pil(size=64)
        if qr_pil:
            img.paste(qr_pil, (bx, by))
            d.text((bx + 32, by + 68), "Scan to verify",
                   font=f_small, fill=template["text_secondary"], anchor="mm")
        else:
            for i in range(30):
                bc = template["accent_color"] if i % 3 == 0 else "#ffffff"
                bw = 2 if i % 5 == 0 else 1
                d.rectangle([bx + i * 3, by, bx + i * 3 + bw, by + 22], fill=bc)

        return img
