import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import json
import os
import theme as _theme


class TemplateEditorWindow:
    def __init__(self, parent):
        self.parent = parent
        t = _theme.get()
        F = _theme.FONTS

        self.win = tk.Toplevel(parent)
        self.win.title("Template Editor")
        self.win.geometry("520x680")
        self.win.configure(bg=t["DARK_BG"])
        self.win.grab_set()

        # Centre
        self.win.update_idletasks()
        x = (self.win.winfo_screenwidth()  // 2) - 260
        y = (self.win.winfo_screenheight() // 2) - 340
        self.win.geometry(f"520x680+{x}+{y}")

        self.template_data = {
            "current_template": "Default",
            "templates": {
                "Default": {
                    "card_w": 450, "card_h": 280,
                    "bg_color": "#1e293b", "outline_color": "#475569",
                    "accent_color": "#3b82f6",
                    "header_bg": "#0f172a", "footer_bg": "#0f172a",
                    "text_primary": "#f1f5f9", "text_secondary": "#94a3b8",
                    "text_accent": "#93c5fd",
                    "college_text": "SHRI BHAGUBHAI MAFATLAL POLYTECHNIC",
                    "college_subtext": "Computer Engineering Department",
                    "photo_rect": {"x": 24, "y": 72, "w": 96, "h": 116},
                    "info_start": {"x": 136, "y": 78},
                    "barcode_start": {"x": 24, "y": 200}
                }
            }
        }

        self.entries = {}

        self.load_templates()
        self._build_ui()
        self.load_current_template()

    def load_templates(self):
        if os.path.exists("templates.json"):
            try:
                with open("templates.json", "r") as f:
                    data = json.load(f)
                    self.template_data.update(data)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load templates: {e}")

    def save_templates(self):
        self.save_current_template()
        try:
            with open("templates.json", "w") as f:
                json.dump(self.template_data, f, indent=2)
            messagebox.showinfo("Saved", "Template saved successfully!")
            self.win.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save templates: {e}")

    def load_current_template(self):
        current = self.template_data.get("current_template", "Default")
        tmpl = self.template_data["templates"].get(current, {})

        for key, val in tmpl.items():
            if isinstance(val, dict):
                for sub_key, sub_val in val.items():
                    entry_id = f"{key}_{sub_key}"
                    if entry_id in self.entries:
                        self.entries[entry_id].delete(0, tk.END)
                        self.entries[entry_id].insert(0, str(sub_val))
            else:
                if key in self.entries:
                    self.entries[key].delete(0, tk.END)
                    self.entries[key].insert(0, str(val))

    def save_current_template(self):
        current = self.template_data.get("current_template", "Default")
        tmpl = self.template_data["templates"].setdefault(current, {})

        for key, entry in self.entries.items():
            val = entry.get().strip()
            if val == "":
                continue
            if "_" in key and key.split("_")[0] in ["photo_rect", "info_start", "barcode_start"]:
                main_key, sub_key = key.split("_", 1)
                if main_key not in tmpl or not isinstance(tmpl[main_key], dict):
                    tmpl[main_key] = {}
                try:
                    tmpl[main_key][sub_key] = int(val)
                except ValueError:
                    tmpl[main_key][sub_key] = val
            else:
                try:
                    tmpl[key] = int(val)
                except ValueError:
                    tmpl[key] = val

    def pick_color(self, key):
        current_color = self.entries[key].get() or "#ffffff"
        color = colorchooser.askcolor(initialcolor=current_color, title="Select Color")
        if color[1]:
            self.entries[key].delete(0, tk.END)
            self.entries[key].insert(0, color[1])

    def reset_to_default(self):
        default_tmpl = {
            "card_w": 450, "card_h": 280,
            "bg_color": "#1e293b", "outline_color": "#475569",
            "accent_color": "#3b82f6",
            "header_bg": "#0f172a", "footer_bg": "#0f172a",
            "text_primary": "#f1f5f9", "text_secondary": "#94a3b8",
            "text_accent": "#93c5fd",
            "college_text": "SHRI BHAGUBHAI MAFATLAL POLYTECHNIC",
            "college_subtext": "Computer Engineering Department",
            "photo_rect": {"x": 24, "y": 72, "w": 96, "h": 116},
            "info_start": {"x": 136, "y": 78},
            "barcode_start": {"x": 24, "y": 200}
        }
        current = self.template_data.get("current_template", "Default")
        self.template_data["templates"][current] = default_tmpl
        self.load_current_template()

    def _build_ui(self):
        t = _theme.get()
        F = _theme.FONTS

        # Header
        hdr = tk.Frame(self.win, bg=t["ACCENT"], pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🎨  Template Editor", font=F["title"],
                 bg=t["ACCENT"], fg="#ffffff").pack()

        # Scrollable form
        canvas = tk.Canvas(self.win, bg=t["DARK_BG"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.win, orient="vertical", command=canvas.yview)
        form_container = tk.Frame(canvas, bg=t["DARK_BG"])

        form_container.bind("<Configure>",
                            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_win = canvas.create_window((0, 0), window=form_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Stretch form_container to canvas width
        def _on_canvas_configure(event):
            canvas.itemconfig(canvas_win, width=event.width)
        canvas.bind("<Configure>", _on_canvas_configure)

        # Mousewheel scroll
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        form_frame = tk.Frame(form_container, bg=t["DARK_BG"], padx=24, pady=10)
        form_frame.pack(fill="both", expand=True)

        row = 0

        def add_section(title):
            nonlocal row
            tk.Label(form_frame, text=title, font=F["body_bold"],
                     bg=t["DARK_BG"], fg=t["TEXT_MAIN"]).grid(
                row=row, column=0, columnspan=3, sticky="w", pady=(14, 6))
            # Separator
            sep = tk.Frame(form_frame, bg=t["SEPARATOR"], height=1)
            sep.grid(row=row + 1, column=0, columnspan=3, sticky="ew", pady=(0, 4))
            row += 2

        def add_field(label_text, key, is_color=False):
            nonlocal row
            tk.Label(form_frame, text=label_text, font=F["caption"],
                     bg=t["DARK_BG"], fg=t["TEXT_SUB"]).grid(
                row=row, column=0, sticky="w", pady=4)

            ent = tk.Entry(form_frame, font=F["body"], width=26,
                           bg=t["ENTRY_BG"], fg=t["TEXT_MAIN"],
                           insertbackground=t["TEXT_MAIN"],
                           relief="flat",
                           highlightthickness=1,
                           highlightbackground=t["ENTRY_BORDER"])
            ent.grid(row=row, column=1, sticky="w", pady=4, padx=6)
            self.entries[key] = ent

            if is_color:
                tk.Button(form_frame, text="🎨", font=F["caption"],
                          command=lambda k=key: self.pick_color(k),
                          bg=t["BTN_INFO"], fg="#ffffff",
                          relief="flat", cursor="hand2", bd=0).grid(
                    row=row, column=2, padx=4)
            row += 1

        add_section("Institution Text")
        add_field("College Name:", "college_text")
        add_field("College Subtext:", "college_subtext")

        add_section("Colors")
        add_field("Background:", "bg_color", True)
        add_field("Accent:", "accent_color", True)
        add_field("Header BG:", "header_bg", True)
        add_field("Footer BG:", "footer_bg", True)
        add_field("Primary Text:", "text_primary", True)
        add_field("Secondary Text:", "text_secondary", True)

        add_section("Layout Positions (X / Y)")
        add_field("Photo X:", "photo_rect_x")
        add_field("Photo Y:", "photo_rect_y")
        add_field("Info Block X:", "info_start_x")
        add_field("Info Block Y:", "info_start_y")
        add_field("Barcode X:", "barcode_start_x")
        add_field("Barcode Y:", "barcode_start_y")

        # Bottom buttons
        btn_frame = tk.Frame(self.win, bg=t["DARK_BG"], pady=10)
        btn_frame.pack(fill="x", padx=24)

        _theme.make_btn(btn_frame, "Close", "BTN_SECONDARY",
                        command=self.win.destroy, side="right")
        _theme.make_btn(btn_frame, "Save Template", "BTN_SUCCESS",
                        command=self.save_templates, icon="💾", side="right")
        _theme.make_btn(btn_frame, "Preview Card", "BTN_PRIMARY",
                        command=self.preview_card, icon="👁", side="left")
        _theme.make_btn(btn_frame, "Reset Default", "BTN_WARNING",
                        command=self.reset_to_default, side="left")

    def preview_card(self):
        self.save_current_template()
        try:
            with open("templates.json", "w") as f:
                json.dump(self.template_data, f, indent=2)
        except Exception:
            pass

        record = {
            "name": "Jane Doe",
            "employee_id": "EMP123",
            "department": "Computer Science",
            "designation": "Professor",
            "issue_date": "2024-05-10"
        }
        from ui_card import CardPreviewWindow
        CardPreviewWindow(self.win, "staff", record)
