import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date, timedelta
import os
import database
import theme
import i18n

# Load persisted theme at startup
theme.load()

# ── Sort column maps ─────────────────────────────────────────
STUDENT_SORT_MAP = {
    "Name": "name", "Roll No": "roll_no",
    "Department": "department", "Year": "year", "Issue Date": "issue_date",
}
STAFF_SORT_MAP = {
    "Name": "name", "Employee ID": "employee_id",
    "Department": "department", "Designation": "designation", "Issue Date": "issue_date",
}


class DashboardWindow:
    def __init__(self, root, login_time=None, current_user=None):
        self.root = root
        self._login_time = login_time
        self._user = current_user or {"username": "admin", "role": "admin"}
        self._tooltip_win = None
        self._tooltip_row = None
        self._toast_id = None
        self.root.title("ID Card Management System — Dashboard")
        self.root.geometry("1180x720")
        self.root.resizable(True, True)

        # Centre window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth()  // 2) - 590
        y = (self.root.winfo_screenheight() // 2) - 360
        self.root.geometry(f"1180x720+{x}+{y}")

        self._apply_theme()
        self._build_ui()
        self.load_students()

        # Expiry check after UI is ready
        self.root.after(600, self._check_expiry)

    # ── Theme helpers ─────────────────────────────────────────

    def _t(self):
        return theme.get()

    def _apply_theme(self):
        t = self._t()
        self.root.configure(bg=t["DARK_BG"])
        theme.apply_ttk(self.root)

    def _full_redraw(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self._apply_theme()
        self._build_ui()
        self.load_students()

    # ── Toast notification ────────────────────────────────────

    def _toast(self, message, duration=2500):
        """Show a small auto-hiding notification at the bottom of the screen."""
        t = self._t()
        if self._toast_id:
            try:
                self.root.after_cancel(self._toast_id)
            except Exception:
                pass

        toast = tk.Label(self.root, text=f"  ✓  {message}  ",
                         font=theme.FONTS["caption_b"],
                         bg=t["BTN_SUCCESS"], fg="#ffffff",
                         padx=16, pady=6)
        toast.place(relx=0.5, rely=0.96, anchor="center")

        def hide():
            try:
                toast.destroy()
            except Exception:
                pass
        self._toast_id = self.root.after(duration, hide)

    # ── Expiry notification ───────────────────────────────────

    def _check_expiry(self):
        expiring = database.get_expiring_soon(days=30)
        if not expiring:
            return
        lines = [
            f"  • {r['name']} ({r['record_type'].title()}) — {r['department']} | {r['issue_date']}"
            for r in expiring
        ]
        messagebox.showwarning(
            i18n.t("expiry_title"),
            i18n.t("expiry_body", n=len(expiring), items="\n".join(lines)),
        )

    # ══════════════════════════════════════════════════════════
    #  BUILD UI
    # ══════════════════════════════════════════════════════════

    def _build_ui(self):
        t = self._t()
        F = theme.FONTS

        # ── Top bar ───────────────────────────────────────────
        topbar = tk.Frame(self.root, bg=t["PANEL_BG"], pady=8)
        topbar.pack(fill="x")

        # Left: App title + last session (stacked)
        left = tk.Frame(topbar, bg=t["PANEL_BG"])
        left.pack(side="left", padx=14)

        tk.Label(left, text=i18n.t("app_title"),
                 font=F["title"], bg=t["PANEL_BG"], fg=t["TEXT_MAIN"]).pack(anchor="w")

        last_login = database.get_last_login()
        if last_login:
            try:
                dt = datetime.strptime(last_login, "%Y-%m-%d %H:%M:%S")
                last_str = dt.strftime("%d %b %Y, %I:%M %p")
            except Exception:
                last_str = last_login
            tk.Label(left, text=f"Last session: {last_str}",
                     font=F["micro"], bg=t["PANEL_BG"],
                     fg=t["TEXT_HINT"]).pack(anchor="w")

        # Right: Controls (packed right-to-left)

        # 1) Logout button (far right)
        theme.make_btn(topbar, i18n.t("logout"), "BTN_DANGER",
                       command=self.logout, font_key="caption_b",
                       side="right", padx=(4, 14))

        # 2) Separator
        sep1 = tk.Frame(topbar, bg=t["SEPARATOR"], width=1, height=28)
        sep1.pack(side="right", padx=6, pady=4, fill="y")

        # 3) User badge
        role = self._user["role"]
        role_key = f"ROLE_{role.upper()}"
        role_clr = t.get(role_key, t["TEXT_SUB"])
        badge = tk.Frame(topbar, bg=t["PANEL_BG"])
        badge.pack(side="right", padx=4)

        tk.Label(badge, text="●", font=(_family(), 10),
                 bg=t["PANEL_BG"], fg=role_clr).pack(side="left")
        tk.Label(badge, text=f" {self._user['username']}",
                 font=F["caption_b"], bg=t["PANEL_BG"],
                 fg=t["TEXT_MAIN"]).pack(side="left")
        tk.Label(badge, text=f" ({role})",
                 font=F["caption"], bg=t["PANEL_BG"],
                 fg=t["TEXT_SUB"]).pack(side="left")

        # 4) Separator
        sep2 = tk.Frame(topbar, bg=t["SEPARATOR"], width=1, height=28)
        sep2.pack(side="right", padx=6, pady=4, fill="y")

        # 5) Theme toggle
        theme_label = i18n.t("toggle_theme_light") if theme.current_name() == "dark" else i18n.t("toggle_theme")
        theme.make_btn(topbar, theme_label, "BTN_INFO",
                       command=self.toggle_theme, font_key="caption_b",
                       side="right")

        # 6) Language selector
        tk.Label(topbar, text=i18n.t("language"), font=F["caption"],
                 bg=t["PANEL_BG"], fg=t["TEXT_SUB"]).pack(side="right", padx=(8, 2))

        lang_var = tk.StringVar(value={v: k for k, v in i18n.AVAILABLE_LANGS.items()}.get(i18n.get_lang(), "English"))
        lang_cb = ttk.Combobox(topbar, textvariable=lang_var,
                               values=list(i18n.AVAILABLE_LANGS.keys()),
                               state="readonly", width=10, font=F["caption"])
        lang_cb.pack(side="right", padx=4, ipady=2)

        def on_lang_change(event=None):
            chosen = i18n.AVAILABLE_LANGS.get(lang_var.get(), "en")
            i18n.set_lang(chosen)
            self._full_redraw()
        lang_cb.bind("<<ComboboxSelected>>", on_lang_change)

        # ── Admin tools bar (second row — only for admin/operator) ──
        if role in ("admin", "operator"):
            tools_bar = tk.Frame(self.root, bg=t["DARK_BG"], pady=4)
            tools_bar.pack(fill="x")

            tk.Label(tools_bar, text="Tools",
                     font=F["micro"], bg=t["DARK_BG"],
                     fg=t["TEXT_HINT"]).pack(side="left", padx=(14, 8))

            if role == "admin":
                theme.make_btn(tools_bar, "Users", "BTN_PRIMARY",
                               command=self.show_user_manager,
                               font_key="caption_b", icon="👥")
                theme.make_btn(tools_bar, "Backup DB", "BTN_SUCCESS",
                               command=self.do_backup,
                               font_key="caption_b", icon="💾")
                theme.make_btn(tools_bar, "Demo Data", "BTN_WARNING",
                               command=self.generate_demo_data,
                               font_key="caption_b", icon="⚡")

            theme.make_btn(tools_bar, "Audit Log", "BTN_SECONDARY",
                           command=self.show_audit_log,
                           font_key="caption_b", icon="📋")
            theme.make_btn(tools_bar, "Templates", "BTN_INFO",
                           command=self.open_template_editor,
                           font_key="caption_b", icon="🎨")

        # ── Notebook ──────────────────────────────────────────
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=(6, 10))

        self.student_frame   = tk.Frame(self.notebook, bg=t["DARK_BG"])
        self.staff_frame     = tk.Frame(self.notebook, bg=t["DARK_BG"])
        self.notif_frame     = tk.Frame(self.notebook, bg=t["DARK_BG"])
        self.analytics_frame = tk.Frame(self.notebook, bg=t["DARK_BG"])

        # Notification badge count
        expiring = database.get_expiring_soon(days=60)
        notif_label = f"🔔 Notifications ({len(expiring)})" if expiring else "🔔 Notifications"

        self.notebook.add(self.student_frame,   text=i18n.t("tab_students"))
        self.notebook.add(self.staff_frame,     text=i18n.t("tab_staff"))
        self.notebook.add(self.notif_frame,     text=notif_label)
        self.notebook.add(self.analytics_frame, text=i18n.t("tab_analytics"))

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        self._build_tab(self.student_frame, "student")
        self._build_tab(self.staff_frame,   "staff")
        self._build_notifications_tab(self.notif_frame)
        self._build_analytics_tab(self.analytics_frame)

    # ══════════════════════════════════════════════════════════
    #  DATA TAB BUILDER
    # ══════════════════════════════════════════════════════════

    def _build_tab(self, parent, tab_type):
        t = self._t()
        F = theme.FONTS
        sort_map = STUDENT_SORT_MAP if tab_type == "student" else STAFF_SORT_MAP

        # ── Row 1: Search + Filter + Sort ─────────────────────
        row1 = tk.Frame(parent, bg=t["DARK_BG"], pady=8)
        row1.pack(fill="x", padx=12)

        tk.Label(row1, text=i18n.t("search"), font=F["caption_b"],
                 bg=t["DARK_BG"], fg=t["TEXT_SUB"]).pack(side="left")

        search_var = tk.StringVar()
        search_wrap = tk.Frame(row1, bg=t["ENTRY_BORDER"], padx=1, pady=1)
        search_wrap.pack(side="left", padx=(6, 14))
        search_entry = tk.Entry(search_wrap, textvariable=search_var,
                                font=F["body"], width=20,
                                bg=t["ENTRY_BG"], fg=t["TEXT_MAIN"],
                                insertbackground=t["TEXT_MAIN"], relief="flat")
        search_entry.pack(ipady=5, padx=1, pady=1)
        search_entry.bind("<FocusIn>",
                          lambda e: search_wrap.configure(bg=t["ENTRY_FOCUS"]))
        search_entry.bind("<FocusOut>",
                          lambda e: search_wrap.configure(bg=t["ENTRY_BORDER"]))

        tk.Label(row1, text=i18n.t("dept"), font=F["caption_b"],
                 bg=t["DARK_BG"], fg=t["TEXT_SUB"]).pack(side="left")

        dept_var = tk.StringVar(value="All")
        dept_cb = ttk.Combobox(row1, textvariable=dept_var,
                               state="readonly", width=16, font=F["body"])
        dept_cb.pack(side="left", padx=(4, 14), ipady=3)

        tk.Label(row1, text=i18n.t("sort"), font=F["caption_b"],
                 bg=t["DARK_BG"], fg=t["TEXT_SUB"]).pack(side="left")

        sort_var = tk.StringVar(value="Name")
        sort_cb = ttk.Combobox(row1, textvariable=sort_var,
                               values=list(sort_map.keys()),
                               state="readonly", width=12, font=F["body"])
        sort_cb.pack(side="left", padx=(4, 4), ipady=3)

        sort_dir_var = tk.StringVar(value="ASC")
        def toggle_dir():
            sort_dir_var.set("DESC" if sort_dir_var.get() == "ASC" else "ASC")
            dir_btn.config(text=i18n.t("asc") if sort_dir_var.get() == "ASC" else i18n.t("desc"))
            do_search()

        dir_btn = tk.Button(row1, text=i18n.t("asc"), font=F["caption_b"],
                            bg=t["ACCENT"], fg="#ffffff", relief="flat",
                            cursor="hand2", command=toggle_dir)
        dir_btn.pack(side="left", padx=(2, 8), ipady=4, ipadx=6)

        def refresh_depts(event=None):
            depts = database.get_student_departments() if tab_type == "student" else database.get_staff_departments()
            dept_cb["values"] = depts
            if dept_var.get() not in depts:
                dept_var.set("All")

        dept_cb.bind("<ButtonPress>", refresh_depts)

        def do_search(*_):
            q    = search_var.get().strip()
            dept = dept_var.get()
            col  = sort_map.get(sort_var.get(), "name")
            sdir = sort_dir_var.get()
            if tab_type == "student":
                data = database.search_students_filtered(q, dept, col, sdir)
                self._populate_tree(self.student_tree, data, "student")
            else:
                data = database.search_staff_filtered(q, dept, col, sdir)
                self._populate_tree(self.staff_tree, data, "staff")

        search_var.trace_add("write", do_search)
        dept_var.trace_add("write", do_search)
        sort_var.trace_add("write", do_search)
        search_entry.bind("<Escape>", lambda e: search_var.set(""))

        # ── Row 2: Action buttons (role-gated) ────────────────
        row2 = tk.Frame(parent, bg=t["DARK_BG"], pady=4)
        row2.pack(fill="x", padx=12)
        role = self._user["role"]

        # Add / Edit — admin + operator
        if role in ("admin", "operator"):
            theme.make_btn(row2, i18n.t("add"), "BTN_SUCCESS",
                           command=lambda: self.open_add(tab_type),
                           font_key="body")
            theme.make_btn(row2, i18n.t("edit"), "BTN_PRIMARY",
                           command=lambda: self.open_edit(tab_type),
                           font_key="body")

        # Delete — admin only
        if role == "admin":
            theme.make_btn(row2, i18n.t("delete"), "BTN_DANGER",
                           command=lambda: self.delete_record(tab_type),
                           font_key="body")

        # View card — everyone
        theme.make_btn(row2, i18n.t("view_card"), "BTN_INFO",
                       command=lambda: self.view_card(tab_type),
                       font_key="body")

        # Export / Import — admin + operator
        if role in ("admin", "operator"):
            theme.make_btn(row2, i18n.t("export_csv"), "BTN_SUCCESS",
                           command=lambda: self.export_data(tab_type),
                           font_key="body")
            theme.make_btn(row2, i18n.t("import_csv"), "BTN_WARNING",
                           command=lambda: self.import_data(tab_type, do_search),
                           font_key="body")
            theme.make_btn(row2, "🖨️ Batch PDF", "BTN_SECONDARY",
                           command=lambda: self.batch_export(tab_type),
                           font_key="body")

        theme.make_btn(row2, i18n.t("refresh"), "BTN_SECONDARY",
                       command=do_search, font_key="body",
                       side="right")

        # ── Treeview ──────────────────────────────────────────
        tree_frame = tk.Frame(parent, bg=t["DARK_BG"])
        tree_frame.pack(fill="both", expand=True, padx=12, pady=(4, 10))

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        if tab_type == "student":
            cols = ("ID", "Name", "Roll No", "Department", "Year", "Contact", "Issue Date")
            self.student_tree = ttk.Treeview(tree_frame, columns=cols,
                                             show="headings",
                                             yscrollcommand=scrollbar.set)
            tree = self.student_tree
            widths = [44, 170, 100, 150, 70, 120, 110]
        else:
            cols = ("ID", "Name", "Employee ID", "Department", "Designation", "Contact", "Issue Date")
            self.staff_tree = ttk.Treeview(tree_frame, columns=cols,
                                           show="headings",
                                           yscrollcommand=scrollbar.set)
            tree = self.staff_tree
            widths = [44, 170, 110, 150, 130, 120, 110]

        for col, w in zip(cols, widths):
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor="center" if col == "ID" else "w")

        # Validity color tags
        tree.tag_configure("valid",    background="#0a2e1a" if theme.current_name() == "dark" else "#dcfce7",
                           foreground=t["BADGE_VALID"])
        tree.tag_configure("expiring", background="#2a2000" if theme.current_name() == "dark" else "#fef9c3",
                           foreground=t["BADGE_EXPIRING"])
        tree.tag_configure("expired",  background="#2a0a0a" if theme.current_name() == "dark" else "#fecaca",
                           foreground=t["BADGE_EXPIRED"])

        tree.pack(fill="both", expand=True)
        scrollbar.config(command=tree.yview)
        tree.bind("<Double-1>", lambda e: self.view_card(tab_type))

        # Hover tooltip
        self._setup_hover_tooltip(tree, tab_type)

        # Status label
        status_lbl = tk.Label(parent, text="", font=F["caption"],
                              bg=t["DARK_BG"], fg=t["TEXT_SUB"])
        status_lbl.pack(anchor="w", padx=14)

        if tab_type == "student":
            self.student_status = status_lbl
        else:
            self.staff_status = status_lbl

    # ══════════════════════════════════════════════════════════
    #  HOVER TOOLTIP (Feature 07)
    # ══════════════════════════════════════════════════════════

    def _setup_hover_tooltip(self, tree, tab_type):
        def on_motion(event):
            row_id = tree.identify_row(event.y)
            if not row_id:
                self._hide_tooltip()
                return

            if row_id == self._tooltip_row:
                if self._tooltip_win:
                    self._tooltip_win.geometry(f"+{event.x_root + 18}+{event.y_root + 12}")
                return

            self._hide_tooltip()
            self._tooltip_row = row_id

            try:
                rec_id = int(row_id)
            except (ValueError, TypeError):
                return

            if tab_type == "student":
                rec = database.get_student_by_id(rec_id)
            else:
                rec = database.get_staff_by_id(rec_id)
            if not rec:
                return

            t = self._t()
            F = theme.FONTS

            # Shadow layer
            shadow = tk.Toplevel(self.root)
            shadow.overrideredirect(True)
            shadow.attributes("-topmost", True)
            shadow.configure(bg=t["SHADOW"])
            shadow.geometry(f"+{event.x_root + 20}+{event.y_root + 14}")
            shadow.attributes("-alpha", 0.3)

            # Main tooltip
            tip = tk.Toplevel(self.root)
            tip.overrideredirect(True)
            tip.attributes("-topmost", True)
            tip.configure(bg=t["SURFACE"],
                          highlightbackground=t["SEPARATOR"],
                          highlightthickness=1)
            tip.geometry(f"+{event.x_root + 18}+{event.y_root + 12}")

            inner = tk.Frame(tip, bg=t["SURFACE"], padx=12, pady=8)
            inner.pack()

            # Photo thumbnail
            photo_path = rec.get("photo_path", "")
            if photo_path and os.path.exists(photo_path):
                try:
                    from PIL import Image, ImageTk
                    img = Image.open(photo_path).resize((44, 55), Image.LANCZOS)
                    photo_img = ImageTk.PhotoImage(img)
                    photo_lbl = tk.Label(inner, image=photo_img, bg=t["SURFACE"])
                    photo_lbl.image = photo_img
                    photo_lbl.pack(side="left", padx=(0, 10))
                except Exception:
                    pass

            # Info
            info = tk.Frame(inner, bg=t["SURFACE"])
            info.pack(side="left", anchor="n")

            tk.Label(info, text=rec["name"], font=F["body_bold"],
                     bg=t["SURFACE"], fg=t["TEXT_MAIN"]).pack(anchor="w")

            id_text = rec.get("roll_no") or rec.get("employee_id", "")
            tk.Label(info, text=f"{rec['department']}  •  {id_text}",
                     font=F["caption"], bg=t["SURFACE"],
                     fg=t["TEXT_SUB"]).pack(anchor="w")

            # Validity badge
            try:
                issue = datetime.strptime(rec["issue_date"], "%Y-%m-%d").date()
                days_since = (date.today() - issue).days
                if days_since >= 365:
                    badge, color = "EXPIRED", t["BADGE_EXPIRED"]
                elif days_since >= 335:
                    badge, color = "EXPIRING", t["BADGE_EXPIRING"]
                else:
                    badge, color = "VALID", t["BADGE_VALID"]
            except Exception:
                badge, color = "VALID", t["BADGE_VALID"]

            tk.Label(info, text=f"📅 {rec['issue_date']}  •  {badge}",
                     font=F["micro"], bg=t["SURFACE"], fg=color).pack(anchor="w", pady=(3, 0))

            self._tooltip_win = tip
            self._tooltip_shadow = shadow

            # Size shadow to match tip
            tip.update_idletasks()
            w, h = tip.winfo_width(), tip.winfo_height()
            shadow.geometry(f"{w}x{h}")

        def on_leave(event):
            self._hide_tooltip()

        tree.bind("<Motion>", on_motion)
        tree.bind("<Leave>", on_leave)

    def _hide_tooltip(self):
        for attr in ("_tooltip_win", "_tooltip_shadow"):
            w = getattr(self, attr, None)
            if w:
                try:
                    w.destroy()
                except Exception:
                    pass
                setattr(self, attr, None)
        self._tooltip_row = None

    # ══════════════════════════════════════════════════════════
    #  NOTIFICATION CENTER (Feature 06)
    # ══════════════════════════════════════════════════════════

    def _build_notifications_tab(self, parent):
        t = self._t()
        F = theme.FONTS

        # Header
        hdr = tk.Frame(parent, bg=t["PANEL_BG"], pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🔔 Notification Center — Renewal Queue",
                 font=F["title"], bg=t["PANEL_BG"],
                 fg=t["TEXT_MAIN"]).pack(side="left", padx=16)

        theme.make_btn(hdr, "Refresh", "BTN_PRIMARY",
                       command=lambda: self._refresh_notifications(container),
                       font_key="caption_b", icon="🔄",
                       side="right", padx=16)

        # Scrollable container
        canvas = tk.Canvas(parent, bg=t["DARK_BG"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        container = tk.Frame(canvas, bg=t["DARK_BG"])

        container.bind("<Configure>",
                       lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, padx=12, pady=6)
        scrollbar.pack(side="right", fill="y")

        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)

        self._populate_notifications(container)

    def _populate_notifications(self, container):
        t = self._t()
        F = theme.FONTS

        for widget in container.winfo_children():
            widget.destroy()

        records = database.get_expiring_soon(days=60)

        if not records:
            tk.Label(container, text="✅  All ID cards are up to date!",
                     font=F["body"], bg=t["DARK_BG"],
                     fg=t["BADGE_VALID"], pady=40).pack()
            return

        for rec in records:
            try:
                issue = datetime.strptime(rec["issue_date"], "%Y-%m-%d").date()
                days_since = (date.today() - issue).days
                if days_since >= 365:
                    days_over = days_since - 365
                    status, badge_bg = "EXPIRED", t["BADGE_EXPIRED"]
                    days_text = f"Expired {days_over} day{'s' if days_over != 1 else ''} ago"
                elif days_since >= 305:
                    days_left = 365 - days_since
                    status, badge_bg = "EXPIRING", t["BADGE_EXPIRING"]
                    days_text = f"Expires in {days_left} day{'s' if days_left != 1 else ''}"
                else:
                    continue
            except Exception:
                status, badge_bg = "UNKNOWN", t["TEXT_HINT"]
                days_text = ""

            # Card row with left accent border
            row_outer = tk.Frame(container, bg=badge_bg, padx=3, pady=0)
            row_outer.pack(fill="x", padx=8, pady=3)

            row = tk.Frame(row_outer, bg=t["PANEL_BG"], padx=14, pady=10)
            row.pack(fill="x", side="right", expand=True)

            # Left: info
            left = tk.Frame(row, bg=t["PANEL_BG"])
            left.pack(side="left", fill="x", expand=True)

            rec_type = rec.get("record_type", "student").title()
            type_icon = "👩‍🎓" if rec_type == "Student" else "👔"

            tk.Label(left, text=f"{type_icon}  {rec['name']}",
                     font=F["body_bold"], bg=t["PANEL_BG"],
                     fg=t["TEXT_MAIN"]).pack(anchor="w")

            tk.Label(left, text=f"{rec['department']}  •  {rec.get('identifier', '')}  •  Issued {rec['issue_date']}",
                     font=F["caption"], bg=t["PANEL_BG"],
                     fg=t["TEXT_SUB"]).pack(anchor="w")

            tk.Label(left, text=days_text,
                     font=F["caption_b"], bg=t["PANEL_BG"],
                     fg=badge_bg).pack(anchor="w", pady=(2, 0))

            # Right: badge + copy button
            right = tk.Frame(row, bg=t["PANEL_BG"])
            right.pack(side="right")

            tk.Label(right, text=f" {status} ", font=F["micro"],
                     bg=badge_bg, fg="#ffffff", padx=8, pady=2).pack(pady=(0, 4))

            reminder_text = (
                f"Dear {rec['name']},\n\n"
                f"Your ID card issued on {rec['issue_date']} "
                f"{'has expired' if status == 'EXPIRED' else 'is expiring soon'}.\n"
                f"Please visit the administration office for renewal.\n\n"
                f"Department: {rec['department']}\n"
                f"Identifier: {rec.get('identifier', 'N/A')}\n\n"
                f"— Shri Bhagubhai Mafatlal Polytechnic"
            )

            def copy_reminder(text=reminder_text):
                self.root.clipboard_clear()
                self.root.clipboard_append(text)
                self._toast("Reminder copied to clipboard!")

            tk.Button(right, text="📋 Copy", font=F["micro"],
                      bg=t["BTN_SECONDARY"], fg="#ffffff", relief="flat",
                      cursor="hand2", bd=0,
                      command=copy_reminder).pack(ipady=2, ipadx=8)

        tk.Label(container, text=f"Total: {len(records)} card(s) require attention",
                 font=F["caption"], bg=t["DARK_BG"], fg=t["TEXT_SUB"],
                 pady=8).pack()

    def _refresh_notifications(self, container):
        self._populate_notifications(container)
        records = database.get_expiring_soon(days=60)
        label = f"🔔 Notifications ({len(records)})" if records else "🔔 Notifications"
        self.notebook.tab(2, text=label)

    # ══════════════════════════════════════════════════════════
    #  ANALYTICS TAB
    # ══════════════════════════════════════════════════════════

    def _build_analytics_tab(self, parent):
        try:
            import matplotlib
            matplotlib.use("TkAgg")
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        except ImportError:
            tk.Label(parent, text="matplotlib not installed.\nRun: pip install matplotlib",
                     font=theme.FONTS["body"], bg=self._t()["DARK_BG"],
                     fg=self._t()["BADGE_EXPIRED"]).pack(expand=True)
            return

        t = self._t()
        F = theme.FONTS
        is_dark = theme.current_name() == "dark"
        bg_color = t["DARK_BG"]
        panel    = t["PANEL_BG"]
        fg_color = t["TEXT_MAIN"]
        accent   = t["ACCENT"]
        accent2  = t["ACCENT2"]
        mpl_bg   = "#1e293b" if is_dark else "#f1f5f9"
        mpl_face = "#0f172a" if is_dark else "#ffffff"

        # Header bar
        hdr = tk.Frame(parent, bg=panel, pady=8)
        hdr.pack(fill="x")
        tk.Label(hdr, text=i18n.t("analytics_title"),
                 font=F["title"], bg=panel, fg=fg_color).pack(side="left", padx=16)

        refresh_btn = tk.Button(hdr, text=i18n.t("refresh_charts"), font=F["caption_b"],
                                bg=accent, fg="#ffffff", relief="flat", cursor="hand2",
                                command=lambda: self._refresh_analytics(fig, canvas))
        refresh_btn.pack(side="right", padx=16, ipady=4, ipadx=10)

        # Summary stat cards
        stats_frame = tk.Frame(parent, bg=bg_color)
        stats_frame.pack(fill="x", padx=12, pady=(8, 4))

        summary = database.get_analytics_summary()
        cards = [
            ("👩‍🎓 Students",  summary["total_students"], t["BADGE_VALID"]),
            ("👔 Staff",       summary["total_staff"],    t["ACCENT"]),
            ("🏫 Departments", summary["departments"],    t["BTN_INFO"]),
            ("📋 Total IDs",   summary["total"],          t["ACCENT2"]),
        ]
        for label, value, color in cards:
            card = tk.Frame(stats_frame, bg=panel, padx=18, pady=12,
                            highlightbackground=color, highlightthickness=2)
            card.pack(side="left", expand=True, fill="x", padx=6, pady=4)
            tk.Label(card, text=str(value), font=F["display"],
                     bg=panel, fg=color).pack()
            tk.Label(card, text=label, font=F["caption"],
                     bg=panel, fg=fg_color).pack()

        # Matplotlib charts
        chart_frame = tk.Frame(parent, bg=bg_color)
        chart_frame.pack(fill="both", expand=True, padx=12, pady=(4, 8))

        fig = Figure(figsize=(11, 5.5), facecolor=mpl_bg)
        fig.subplots_adjust(left=0.07, right=0.97, top=0.88, bottom=0.18, wspace=0.35)

        self._draw_charts(fig, mpl_bg, mpl_face, fg_color, is_dark)

        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        self._analytics_fig    = fig
        self._analytics_canvas = canvas
        self._analytics_mpl    = (mpl_bg, mpl_face, fg_color, is_dark)

    def _draw_charts(self, fig, mpl_bg, mpl_face, fg_color, is_dark):
        fig.clear()

        palette = ["#3b82f6", "#ef4444", "#22c55e", "#f59e0b", "#6366f1",
                   "#14b8a6", "#f97316", "#8b5cf6", "#ec4899", "#06b6d4"]

        ax1 = fig.add_subplot(1, 3, 1, facecolor=mpl_face)
        ax2 = fig.add_subplot(1, 3, 2, facecolor=mpl_face)
        ax3 = fig.add_subplot(1, 3, 3, facecolor=mpl_face)

        # Chart 1: Students per Dept (Pie)
        s_data = database.get_students_per_department()
        if s_data:
            labels, sizes = zip(*s_data)
            colors = palette[:len(labels)]
            wedges, texts, autotexts = ax1.pie(
                sizes, labels=None, autopct="%1.0f%%",
                colors=colors, startangle=90,
                textprops={"color": fg_color, "fontsize": 8},
                wedgeprops={"linewidth": 1.5, "edgecolor": mpl_bg},
            )
            for at in autotexts:
                at.set_fontsize(7)
            ax1.legend(labels, loc="lower center", bbox_to_anchor=(0.5, -0.22),
                       ncol=2, fontsize=7, frameon=False,
                       labelcolor=fg_color, facecolor="none")
        else:
            ax1.text(0.5, 0.5, i18n.t("no_data"), ha="center", va="center",
                     color=fg_color, fontsize=10)
        ax1.set_title("Students by Dept", color=fg_color, fontsize=10, pad=8)
        ax1.tick_params(colors=fg_color)

        # Chart 2: Staff per Dept (Bar)
        f_data = database.get_staff_per_department()
        if f_data:
            depts, counts = zip(*f_data)
            bars = ax2.barh(depts, counts,
                            color=palette[:len(depts)],
                            edgecolor=mpl_bg, linewidth=0.8)
            ax2.set_xlabel("Count", color=fg_color, fontsize=8)
            ax2.tick_params(colors=fg_color, labelsize=8)
            ax2.spines["top"].set_visible(False)
            ax2.spines["right"].set_visible(False)
            for spine in ["left", "bottom"]:
                ax2.spines[spine].set_color(fg_color)
            for bar, val in zip(bars, counts):
                ax2.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
                         str(val), va="center", color=fg_color, fontsize=8)
        else:
            ax2.text(0.5, 0.5, i18n.t("no_data"), ha="center", va="center",
                     color=fg_color, fontsize=10)
            ax2.set_axis_off()
        ax2.set_title("Staff by Dept", color=fg_color, fontsize=10, pad=8)
        ax2.set_facecolor(mpl_face)
        for label in ax2.get_yticklabels():
            label.set_color(fg_color)

        # Chart 3: Monthly Issuance
        monthly = database.get_monthly_issuance(12)
        labels3  = [m[0][5:] for m in monthly]
        students = [m[1]     for m in monthly]
        staff_   = [m[2]     for m in monthly]

        x = range(len(labels3))
        ax3.bar(x, students, label="Students", color="#22c55e", edgecolor=mpl_bg, linewidth=0.5)
        ax3.bar(x, staff_,   label="Staff",    color="#3b82f6", bottom=students,
                edgecolor=mpl_bg, linewidth=0.5)
        ax3.set_xticks(list(x))
        ax3.set_xticklabels(labels3, rotation=45, ha="right",
                            fontsize=7, color=fg_color)
        ax3.set_ylabel("Cards Issued", color=fg_color, fontsize=8)
        ax3.tick_params(colors=fg_color, labelsize=7)
        ax3.legend(fontsize=7, frameon=False, labelcolor=fg_color, facecolor="none")
        for spine in ["top", "right"]:
            ax3.spines[spine].set_visible(False)
        for spine in ["left", "bottom"]:
            ax3.spines[spine].set_color(fg_color)
        ax3.set_title("Monthly Issuance (12 mo)", color=fg_color, fontsize=10, pad=8)
        ax3.set_facecolor(mpl_face)

    def _refresh_analytics(self, fig, canvas):
        t = self._t()
        is_dark  = theme.current_name() == "dark"
        mpl_bg   = "#1e293b" if is_dark else "#f1f5f9"
        mpl_face = "#0f172a" if is_dark else "#ffffff"
        self._draw_charts(fig, mpl_bg, mpl_face, t["TEXT_MAIN"], is_dark)
        canvas.draw()

    # ══════════════════════════════════════════════════════════
    #  DATA LOADING
    # ══════════════════════════════════════════════════════════

    def _populate_tree(self, tree, data, tab_type):
        tree.delete(*tree.get_children())
        today = date.today()
        for rec in data:
            try:
                issue = datetime.strptime(rec["issue_date"], "%Y-%m-%d").date()
                days_since = (today - issue).days
                if days_since >= 365:
                    validity_tag = "expired"
                elif days_since >= 335:
                    validity_tag = "expiring"
                else:
                    validity_tag = "valid"
            except Exception:
                validity_tag = "valid"

            if tab_type == "student":
                tree.insert("", "end", iid=rec["id"], tags=(validity_tag,), values=(
                    rec["id"], rec["name"], rec["roll_no"],
                    rec["department"], rec["year"],
                    rec.get("contact", ""), rec["issue_date"]
                ))
            else:
                tree.insert("", "end", iid=rec["id"], tags=(validity_tag,), values=(
                    rec["id"], rec["name"], rec["employee_id"],
                    rec["department"], rec["designation"],
                    rec.get("contact", ""), rec["issue_date"]
                ))
        count = len(data)
        s = "s" if count != 1 else ""
        label_text = i18n.t("records_found", n=count, s=s)
        if tab_type == "student":
            self.student_status.config(text=label_text)
        else:
            self.staff_status.config(text=label_text)

    def load_students(self):
        data = database.get_all_students()
        self._populate_tree(self.student_tree, data, "student")

    def load_staff(self):
        data = database.get_all_staff()
        self._populate_tree(self.staff_tree, data, "staff")

    def on_tab_change(self, event):
        tab = self.notebook.index(self.notebook.select())
        if tab == 0:
            self.load_students()
        elif tab == 1:
            self.load_staff()

    # ══════════════════════════════════════════════════════════
    #  CRUD ACTIONS
    # ══════════════════════════════════════════════════════════

    def _get_selected_id(self, tab_type):
        tree = self.student_tree if tab_type == "student" else self.staff_tree
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", i18n.t("no_selection"))
            return None
        return int(selected[0])

    def open_add(self, tab_type):
        from ui_forms import RecordForm
        RecordForm(self.root, tab_type, mode="add", record=None,
                   on_save=self.load_students if tab_type == "student" else self.load_staff)

    def open_edit(self, tab_type):
        record_id = self._get_selected_id(tab_type)
        if record_id is None:
            return
        record = database.get_student_by_id(record_id) if tab_type == "student" \
            else database.get_staff_by_id(record_id)
        from ui_forms import RecordForm
        RecordForm(self.root, tab_type, mode="edit", record=record,
                   on_save=self.load_students if tab_type == "student" else self.load_staff)

    def delete_record(self, tab_type):
        record_id = self._get_selected_id(tab_type)
        if record_id is None:
            return
        tree = self.student_tree if tab_type == "student" else self.staff_tree
        name = tree.item(record_id, "values")[1]
        if not messagebox.askyesno("Confirm Delete", i18n.t("confirm_del", name=name)):
            return
        fn = database.delete_student if tab_type == "student" else database.delete_staff
        success, msg = fn(record_id)
        if success:
            (self.load_students if tab_type == "student" else self.load_staff)()
            messagebox.showinfo(i18n.t("deleted"), msg)
        else:
            messagebox.showerror(i18n.t("error"), msg)

    def view_card(self, tab_type):
        record_id = self._get_selected_id(tab_type)
        if record_id is None:
            return
        record = database.get_student_by_id(record_id) if tab_type == "student" \
            else database.get_staff_by_id(record_id)
        from ui_card import CardPreviewWindow
        CardPreviewWindow(self.root, tab_type, record)

    # ── Export / Import ───────────────────────────────────────

    def export_data(self, tab_type):
        filepath = filedialog.asksaveasfilename(
            title=f"Export {tab_type.title()} Records",
            defaultextension=".csv",
            initialfile=f"{tab_type}s_export.csv",
            filetypes=[
                ("CSV Files", "*.csv"),
                ("Excel Files", "*.xlsx"),
                ("All Files", "*.*"),
            ],
        )
        if not filepath:
            return
        if filepath.lower().endswith(".xlsx"):
            fn = database.export_students_xlsx if tab_type == "student" else database.export_staff_xlsx
        else:
            fn = database.export_students_csv if tab_type == "student" else database.export_staff_csv
        ok, msg = fn(filepath)
        (messagebox.showinfo if ok else messagebox.showerror)("Export", msg)

    def import_data(self, tab_type, refresh_fn):
        filepath = filedialog.askopenfilename(
            title=f"Import {tab_type.title()} Records",
            filetypes=[
                ("CSV Files", "*.csv"),
                ("Excel Files", "*.xlsx"),
                ("All Files", "*.*"),
            ],
        )
        if not filepath:
            return
        if filepath.lower().endswith(".xlsx"):
            fn = database.import_students_xlsx if tab_type == "student" else database.import_staff_xlsx
        else:
            fn = database.import_students_csv if tab_type == "student" else database.import_staff_csv
        ok, msg = fn(filepath)
        if ok:
            messagebox.showinfo("Import Complete", msg)
            refresh_fn()
        else:
            messagebox.showerror("Import Failed", msg)

    # ── Batch PDF Export ──────────────────────────────────────

    def batch_export(self, tab_type):
        if tab_type == "student":
            records = database.get_all_students()
        else:
            records = database.get_all_staff()
        if not records:
            messagebox.showwarning("No Records", "There are no records to export.")
            return
        filepath = filedialog.asksaveasfilename(
            title=f"Batch Export {tab_type.title()} ID Cards",
            defaultextension=".pdf",
            initialfile=f"{tab_type}s_batch_cards.pdf",
            filetypes=[("PDF Document", "*.pdf"), ("All Files", "*.*")],
        )
        if not filepath:
            return
        self.root.config(cursor="watch")
        self.root.update()
        from ui_card import batch_export_pdf
        ok, msg = batch_export_pdf(records, tab_type, filepath)
        self.root.config(cursor="")
        if ok:
            messagebox.showinfo("Batch Export", msg)
        else:
            messagebox.showerror("Batch Export Failed", msg)

    # ── Demo Data ─────────────────────────────────────────────

    def generate_demo_data(self):
        if not messagebox.askyesno(
            "Generate Demo Data",
            "This will insert ~30 student and ~10 staff fake records "
            "for demonstration purposes.\n\n"
            "Existing records will NOT be deleted.\n\n"
            "Continue?"
        ):
            return
        self.root.config(cursor="watch")
        self.root.update()
        ok, msg = database.generate_demo_data(n_students=30, n_staff=10)
        self.root.config(cursor="")
        if ok:
            messagebox.showinfo("Demo Data", msg)
            self.load_students()
        else:
            messagebox.showerror("Demo Data Failed", msg)

    # ── Backup ────────────────────────────────────────────────

    def do_backup(self):
        backup_dir = filedialog.askdirectory(title="Choose Backup Folder")
        if not backup_dir:
            return
        ok, msg, _ = database.backup_database(backup_dir)
        if ok:
            messagebox.showinfo(i18n.t("backup_title"), msg)
        else:
            messagebox.showerror("Backup Failed", msg)

    # ── Theme toggle ──────────────────────────────────────────

    def toggle_theme(self):
        theme.toggle()
        self._full_redraw()

    # ── Audit Log ─────────────────────────────────────────────

    def show_audit_log(self):
        t = self._t()
        F = theme.FONTS
        win = tk.Toplevel(self.root)
        win.title("Audit Log")
        win.geometry("920x500")
        win.configure(bg=t["DARK_BG"])
        win.resizable(True, True)

        win.update_idletasks()
        x = (win.winfo_screenwidth()  // 2) - 460
        y = (win.winfo_screenheight() // 2) - 250
        win.geometry(f"920x500+{x}+{y}")

        tk.Label(win, text=i18n.t("audit_title"),
                 font=F["title"],
                 bg=t["DARK_BG"], fg=t["TEXT_MAIN"]).pack(pady=(12, 6))

        cols   = ("Timestamp", "Action", "Type", "Record ID", "Details")
        widths = [160, 100, 80, 80, 400]

        frame = tk.Frame(win, bg=t["DARK_BG"])
        frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        sy = ttk.Scrollbar(frame, orient="vertical")
        sy.pack(side="right", fill="y")
        sx = ttk.Scrollbar(frame, orient="horizontal")
        sx.pack(side="bottom", fill="x")

        tree = ttk.Treeview(frame, columns=cols, show="headings",
                            yscrollcommand=sy.set, xscrollcommand=sx.set)
        for col, w in zip(cols, widths):
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor="w")
        tree.pack(fill="both", expand=True)
        sy.config(command=tree.yview)
        sx.config(command=tree.xview)

        logs = database.get_audit_logs(200)
        for log in logs:
            tree.insert("", "end", values=(
                log["timestamp"], log["action"], log["record_type"],
                log.get("record_id", ""), log.get("details", ""),
            ))

        n = len(logs)
        y_word = "y" if n == 1 else "ies"
        tk.Label(win, text=i18n.t("audit_footer", n=n, y=y_word),
                 font=F["caption"], bg=t["DARK_BG"], fg=t["TEXT_SUB"]
                 ).pack(anchor="w", padx=14, pady=(0, 6))

    # ── Template Editor ───────────────────────────────────────

    def open_template_editor(self):
        try:
            from template_editor import TemplateEditorWindow
            TemplateEditorWindow(self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open template editor: {e}")

    # ── User Manager ──────────────────────────────────────────

    def show_user_manager(self):
        t = self._t()
        F = theme.FONTS
        win = tk.Toplevel(self.root)
        win.title("User Management")
        win.configure(bg=t["DARK_BG"])
        win.resizable(True, True)
        win.minsize(480, 420)

        # Center on screen
        sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
        ww, wh = min(700, sw - 80), min(580, sh - 80)
        win.geometry(f"{ww}x{wh}+{(sw - ww) // 2}+{(sh - wh) // 2}")
        win.grab_set()

        # ── Main grid: header(0), table(1 expand), actions(2), divider(3), form(4) ──
        win.grid_rowconfigure(1, weight=1)
        win.grid_columnconfigure(0, weight=1)

        # ── Row 0: Header ──
        hdr = tk.Frame(win, bg=t["ACCENT"], pady=10)
        hdr.grid(row=0, column=0, sticky="ew")
        tk.Label(hdr, text="👥  User Management",
                 font=F["title"], bg=t["ACCENT"], fg="#ffffff"
                 ).pack(side="left", padx=14)
        count_lbl = tk.Label(hdr, text="", font=F["caption"],
                             bg=t["ACCENT"], fg="#dbeafe")
        count_lbl.pack(side="right", padx=14)

        # ── Row 1: Table (expands) ──
        tree_wrap = tk.Frame(win, bg=t["DARK_BG"])
        tree_wrap.grid(row=1, column=0, sticky="nsew", padx=10, pady=(6, 0))
        tree_wrap.grid_rowconfigure(0, weight=1)
        tree_wrap.grid_columnconfigure(0, weight=1)

        cols = ("ID", "Username", "Role", "Created")
        tree = ttk.Treeview(tree_wrap, columns=cols, show="headings", height=6)
        for col, w, stretch in zip(cols, [40, 140, 90, 160], [False, True, False, True]):
            tree.heading(col, text=col)
            tree.column(col, width=w, minwidth=w, anchor="center", stretch=stretch)
        tree.grid(row=0, column=0, sticky="nsew")

        sy = ttk.Scrollbar(tree_wrap, orient="vertical", command=tree.yview)
        sy.grid(row=0, column=1, sticky="ns")
        tree.configure(yscrollcommand=sy.set)

        def refresh_users():
            tree.delete(*tree.get_children())
            users = database.get_all_users()
            for u in users:
                tree.insert("", "end", iid=u["id"], values=(
                    u["id"], u["username"], u["role"], u["created_at"]
                ))
            count_lbl.config(text=f"{len(users)} user(s)")

        refresh_users()

        # ── Row 2: Action buttons ──
        action_bar = tk.Frame(win, bg=t["DARK_BG"])
        action_bar.grid(row=2, column=0, sticky="ew", padx=10, pady=6)

        def do_delete():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("No Selection",
                                       "Select a user to delete.", parent=win)
                return
            uid = int(sel[0])
            vals = tree.item(uid, "values")
            uname = vals[1]
            if not messagebox.askyesno("Confirm Delete",
                                       f"Delete user '{uname}'?", parent=win):
                return
            ok, msg = database.delete_user(uid, self._user["username"])
            if ok:
                messagebox.showinfo("Deleted", msg, parent=win)
                refresh_users()
            else:
                messagebox.showerror("Error", msg, parent=win)

        def do_change_role():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("No Selection",
                                       "Select a user to change role.", parent=win)
                return
            uid = int(sel[0])
            vals = tree.item(uid, "values")
            uname, cur_role = vals[1], vals[2]

            rw = tk.Toplevel(win)
            rw.title(f"Change Role — {uname}")
            rw.geometry("300x170")
            rw.configure(bg=t["DARK_BG"])
            rw.resizable(False, False)
            rw.grab_set()
            rw.update_idletasks()
            rw.geometry(f"+{(sw)//2 - 150}+{(sh)//2 - 85}")

            tk.Label(rw, text=f"Change role for '{uname}'",
                     font=F["body_bold"], bg=t["DARK_BG"],
                     fg=t["TEXT_MAIN"]).pack(pady=(14, 2))
            tk.Label(rw, text=f"Current: {cur_role}", font=F["caption"],
                     bg=t["DARK_BG"], fg=t["TEXT_SUB"]).pack(pady=(0, 10))

            nrv = tk.StringVar(value=cur_role)
            ttk.Combobox(rw, textvariable=nrv,
                         values=["admin", "operator", "viewer"],
                         state="readonly", width=14, font=F["body"]
                         ).pack(ipady=2)

            def apply_role():
                nr = nrv.get()
                if nr == cur_role:
                    rw.destroy()
                    return
                ok, msg = database.update_user_role(uid, nr,
                                                     self._user["username"])
                if ok:
                    messagebox.showinfo("Updated", msg, parent=rw)
                    rw.destroy()
                    refresh_users()
                else:
                    messagebox.showerror("Error", msg, parent=rw)

            br = tk.Frame(rw, bg=t["DARK_BG"])
            br.pack(pady=10)
            tk.Button(br, text="Apply", font=F["body_bold"],
                      bg=t["BTN_PRIMARY"], fg="#ffffff",
                      activebackground=t["ACCENT"], activeforeground="#ffffff",
                      relief="flat", cursor="hand2", bd=0,
                      command=apply_role).pack(side="left", ipadx=14, ipady=4, padx=4)
            tk.Button(br, text="Cancel", font=F["body"],
                      bg=t["BTN_SECONDARY"], fg="#ffffff",
                      relief="flat", cursor="hand2", bd=0,
                      command=rw.destroy).pack(side="left", ipadx=10, ipady=4, padx=4)

        tk.Button(action_bar, text="🗑️  Delete User", font=F["caption_b"],
                  bg=t["BTN_DANGER"], fg="#ffffff",
                  activebackground="#b91c1c", activeforeground="#ffffff",
                  relief="flat", cursor="hand2", bd=0,
                  command=do_delete).pack(side="left", ipadx=10, ipady=4, padx=(0, 6))
        tk.Button(action_bar, text="🔄  Change Role", font=F["caption_b"],
                  bg=t["BTN_INFO"], fg="#ffffff",
                  activebackground="#0369a1", activeforeground="#ffffff",
                  relief="flat", cursor="hand2", bd=0,
                  command=do_change_role).pack(side="left", ipadx=10, ipady=4)

        # ── Row 3: Divider ──
        tk.Frame(win, bg=t["SEPARATOR"], height=1).grid(
            row=3, column=0, sticky="ew", padx=10, pady=2)

        # ── Row 4: Add User Form (grid-based, responsive) ──
        form = tk.Frame(win, bg=t["PANEL_BG"], padx=14, pady=12)
        form.grid(row=4, column=0, sticky="ew", padx=10, pady=(0, 10))
        # 5 columns: label, input, label, input, button
        form.grid_columnconfigure(1, weight=1)
        form.grid_columnconfigure(3, weight=1)

        tk.Label(form, text="➕  Add New User", font=F["body_bold"],
                 bg=t["PANEL_BG"], fg=t["TEXT_MAIN"]
                 ).grid(row=0, column=0, columnspan=5, sticky="w", pady=(0, 10))

        # Username label + entry
        tk.Label(form, text="Username", font=F["caption_b"],
                 bg=t["PANEL_BG"], fg=t["TEXT_SUB"]
                 ).grid(row=1, column=0, sticky="w", padx=(0, 6))
        u_var = tk.StringVar()
        u_entry = tk.Entry(form, textvariable=u_var, font=F["body"],
                           bg=t["ENTRY_BG"], fg=t["TEXT_MAIN"],
                           insertbackground=t["TEXT_MAIN"], relief="flat",
                           highlightthickness=1,
                           highlightbackground=t["ENTRY_BORDER"],
                           highlightcolor=t["ACCENT"])
        u_entry.grid(row=1, column=1, sticky="ew", padx=(0, 12), ipady=5)

        # Password label + entry
        tk.Label(form, text="Password", font=F["caption_b"],
                 bg=t["PANEL_BG"], fg=t["TEXT_SUB"]
                 ).grid(row=1, column=2, sticky="w", padx=(0, 6))
        p_var = tk.StringVar()
        tk.Entry(form, textvariable=p_var, show="●", font=F["body"],
                 bg=t["ENTRY_BG"], fg=t["TEXT_MAIN"],
                 insertbackground=t["TEXT_MAIN"], relief="flat",
                 highlightthickness=1,
                 highlightbackground=t["ENTRY_BORDER"],
                 highlightcolor=t["ACCENT"]
                 ).grid(row=1, column=3, sticky="ew", padx=(0, 12), ipady=5)

        # Role label + combo + Add button (row 2)
        tk.Label(form, text="Role", font=F["caption_b"],
                 bg=t["PANEL_BG"], fg=t["TEXT_SUB"]
                 ).grid(row=2, column=0, sticky="w", padx=(0, 6), pady=(10, 0))
        role_var = tk.StringVar(value="viewer")
        ttk.Combobox(form, textvariable=role_var,
                     values=["admin", "operator", "viewer"],
                     state="readonly", width=12, font=F["body"]
                     ).grid(row=2, column=1, sticky="w", pady=(10, 0), ipady=2)

        def do_add():
            username = u_var.get().strip()
            password = p_var.get().strip()
            role = role_var.get()
            if not username or not password:
                messagebox.showwarning("Missing Fields",
                                       "Please enter both username and password.",
                                       parent=win)
                return
            ok, msg = database.add_user(username, password, role)
            if ok:
                messagebox.showinfo("User Added", msg, parent=win)
                u_var.set("")
                p_var.set("")
                role_var.set("viewer")
                refresh_users()
            else:
                messagebox.showerror("Error", msg, parent=win)

        tk.Button(form, text="➕  Add User", font=F["body_bold"],
                  bg=t["BTN_SUCCESS"], fg="#ffffff",
                  activebackground="#16a34a", activeforeground="#ffffff",
                  relief="flat", cursor="hand2", bd=0,
                  command=do_add
                  ).grid(row=2, column=3, sticky="e", pady=(10, 0),
                         ipady=5, ipadx=16)

    # ── Logout ────────────────────────────────────────────────

    def logout(self):
        if messagebox.askyesno("Logout", i18n.t("logout_confirm")):
            if self._login_time:
                duration_secs = int((datetime.now() - self._login_time).total_seconds())
                mins, secs = divmod(duration_secs, 60)
                database.log_action(
                    "LOGOUT", "user",
                    details=f"username={self._user['username']}, session_duration={mins}m {secs}s"
                )
            self.root.destroy()
            import main
            main.main()


def _family():
    return theme.FONTS["body"][0]
