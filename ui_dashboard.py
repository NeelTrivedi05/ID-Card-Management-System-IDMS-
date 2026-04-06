import tkinter as tk
from tkinter import ttk, messagebox
import database

DARK_BG   = "#1a1a2e"
PANEL_BG  = "#16213e"
ACCENT    = "#0f3460"
ACCENT2   = "#e94560"
TEXT_MAIN = "#ffffff"
TEXT_SUB  = "#a0aec0"

class DashboardWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("ID Card Management System — Dashboard")
        self.root.geometry("950x620")
        self.root.configure(bg=DARK_BG)
        self.root.resizable(True, True)

        # Centre window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth()  // 2) - 475
        y = (self.root.winfo_screenheight() // 2) - 310
        self.root.geometry(f"950x620+{x}+{y}")

        self._style_treeview()
        self._build_ui()
        self.load_students()

    def _style_treeview(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background=PANEL_BG,
                        foreground=TEXT_MAIN,
                        fieldbackground=PANEL_BG,
                        rowheight=28,
                        font=("Arial", 10))
        style.configure("Treeview.Heading",
                        background=ACCENT,
                        foreground=TEXT_MAIN,
                        font=("Arial", 10, "bold"),
                        relief="flat")
        style.map("Treeview",
                  background=[("selected", ACCENT2)],
                  foreground=[("selected", TEXT_MAIN)])
        style.configure("TNotebook",        background=DARK_BG, borderwidth=0)
        style.configure("TNotebook.Tab",    background=PANEL_BG,
                        foreground=TEXT_SUB, padding=[16, 8],
                        font=("Arial", 10))
        style.map("TNotebook.Tab",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", TEXT_MAIN)])

    def _build_ui(self):
        # ── Top bar ─────────────────────────────────────────
        topbar = tk.Frame(self.root, bg=PANEL_BG, pady=10)
        topbar.pack(fill="x")

        tk.Label(topbar, text="🪪  ID Card Management System",
                 font=("Arial", 14, "bold"),
                 bg=PANEL_BG, fg=TEXT_MAIN).pack(side="left", padx=16)

        tk.Button(topbar, text="Logout", font=("Arial", 9),
                  bg=ACCENT2, fg=TEXT_MAIN, relief="flat",
                  activebackground="#c73652", cursor="hand2",
                  command=self.logout).pack(side="right", padx=16, ipady=4, ipadx=8)

        # ── Notebook tabs ────────────────────────────────────
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.student_frame = tk.Frame(self.notebook, bg=DARK_BG)
        self.staff_frame   = tk.Frame(self.notebook, bg=DARK_BG)
        self.notebook.add(self.student_frame, text="  Students  ")
        self.notebook.add(self.staff_frame,   text="  Staff  ")

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        self._build_tab(self.student_frame, "student")
        self._build_tab(self.staff_frame,   "staff")

    def _build_tab(self, parent, tab_type):
        # ── Search + action bar ──────────────────────────────
        bar = tk.Frame(parent, bg=DARK_BG, pady=8)
        bar.pack(fill="x", padx=10)

        tk.Label(bar, text="Search:", font=("Arial", 10),
                 bg=DARK_BG, fg=TEXT_SUB).pack(side="left")

        search_var = tk.StringVar()
        search_entry = tk.Entry(bar, textvariable=search_var,
                                font=("Arial", 10), width=28,
                                bg=PANEL_BG, fg=TEXT_MAIN,
                                insertbackground="white", relief="flat")
        search_entry.pack(side="left", ipady=5, padx=(6, 4))

        def do_search(*_):
            q = search_var.get().strip()
            if tab_type == "student":
                data = database.search_students(q) if q else database.get_all_students()
                self._populate_tree(self.student_tree, data, "student")
            else:
                data = database.search_staff(q) if q else database.get_all_staff()
                self._populate_tree(self.staff_tree, data, "staff")

        search_var.trace_add("write", do_search)
        search_entry.bind("<Escape>", lambda e: search_var.set(""))

        tk.Button(bar, text="+ Add",
                  font=("Arial", 10), bg="#2ecc71", fg="white",
                  relief="flat", cursor="hand2",
                  command=lambda: self.open_add(tab_type)
                  ).pack(side="left", padx=4, ipady=4, ipadx=8)

        tk.Button(bar, text="✏ Edit",
                  font=("Arial", 10), bg=ACCENT, fg="white",
                  relief="flat", cursor="hand2",
                  command=lambda: self.open_edit(tab_type)
                  ).pack(side="left", padx=4, ipady=4, ipadx=8)

        tk.Button(bar, text="🗑 Delete",
                  font=("Arial", 10), bg=ACCENT2, fg="white",
                  relief="flat", cursor="hand2",
                  command=lambda: self.delete_record(tab_type)
                  ).pack(side="left", padx=4, ipady=4, ipadx=8)

        tk.Button(bar, text="👁 View Card",
                  font=("Arial", 10), bg="#8e44ad", fg="white",
                  relief="flat", cursor="hand2",
                  command=lambda: self.view_card(tab_type)
                  ).pack(side="left", padx=4, ipady=4, ipadx=8)

        tk.Button(bar, text="↻ Refresh",
                  font=("Arial", 10), bg="#555", fg="white",
                  relief="flat", cursor="hand2",
                  command=lambda: do_search()
                  ).pack(side="right", padx=4, ipady=4, ipadx=8)

        # ── Treeview ─────────────────────────────────────────
        tree_frame = tk.Frame(parent, bg=DARK_BG)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        if tab_type == "student":
            cols = ("ID", "Name", "Roll No", "Department", "Year", "Contact", "Issue Date")
            self.student_tree = ttk.Treeview(tree_frame, columns=cols,
                                             show="headings",
                                             yscrollcommand=scrollbar.set)
            tree = self.student_tree
            widths = [40, 160, 90, 140, 60, 110, 100]
        else:
            cols = ("ID", "Name", "Employee ID", "Department", "Designation", "Contact", "Issue Date")
            self.staff_tree = ttk.Treeview(tree_frame, columns=cols,
                                           show="headings",
                                           yscrollcommand=scrollbar.set)
            tree = self.staff_tree
            widths = [40, 160, 100, 140, 120, 110, 100]

        for col, w in zip(cols, widths):
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor="center" if col == "ID" else "w")

        tree.pack(fill="both", expand=True)
        scrollbar.config(command=tree.yview)

        # Double-click to view card
        tree.bind("<Double-1>", lambda e: self.view_card(tab_type))

        # Status label
        if tab_type == "student":
            self.student_status = tk.Label(parent, text="", font=("Arial", 9),
                                           bg=DARK_BG, fg=TEXT_SUB)
            self.student_status.pack(anchor="w", padx=14)
        else:
            self.staff_status = tk.Label(parent, text="", font=("Arial", 9),
                                         bg=DARK_BG, fg=TEXT_SUB)
            self.staff_status.pack(anchor="w", padx=14)

    # ── Data loading ─────────────────────────────────────────

    def _populate_tree(self, tree, data, tab_type):
        tree.delete(*tree.get_children())
        for rec in data:
            if tab_type == "student":
                tree.insert("", "end", iid=rec["id"], values=(
                    rec["id"], rec["name"], rec["roll_no"],
                    rec["department"], rec["year"],
                    rec.get("contact", ""), rec["issue_date"]
                ))
            else:
                tree.insert("", "end", iid=rec["id"], values=(
                    rec["id"], rec["name"], rec["employee_id"],
                    rec["department"], rec["designation"],
                    rec.get("contact", ""), rec["issue_date"]
                ))
        count = len(data)
        label_text = f"{count} record{'s' if count != 1 else ''} found"
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
        else:
            self.load_staff()

    # ── Get selected record ───────────────────────────────────

    def _get_selected_id(self, tab_type):
        tree = self.student_tree if tab_type == "student" else self.staff_tree
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a record first.")
            return None
        return int(selected[0])

    # ── Actions ───────────────────────────────────────────────

    def open_add(self, tab_type):
        from ui_forms import RecordForm
        RecordForm(self.root, tab_type, mode="add", record=None,
                   on_save=self.load_students if tab_type == "student" else self.load_staff)

    def open_edit(self, tab_type):
        record_id = self._get_selected_id(tab_type)
        if record_id is None:
            return
        if tab_type == "student":
            record = database.get_student_by_id(record_id)
        else:
            record = database.get_staff_by_id(record_id)

        from ui_forms import RecordForm
        RecordForm(self.root, tab_type, mode="edit", record=record,
                   on_save=self.load_students if tab_type == "student" else self.load_staff)

    def delete_record(self, tab_type):
        record_id = self._get_selected_id(tab_type)
        if record_id is None:
            return

        tree = self.student_tree if tab_type == "student" else self.staff_tree
        values = tree.item(record_id, "values")
        name = values[1]

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete:\n\n{name}\n\nThis cannot be undone."
        )
        if not confirm:
            return

        if tab_type == "student":
            success, msg = database.delete_student(record_id)
            if success:
                self.load_students()
        else:
            success, msg = database.delete_staff(record_id)
            if success:
                self.load_staff()

        if success:
            messagebox.showinfo("Deleted", msg)
        else:
            messagebox.showerror("Error", msg)

    def view_card(self, tab_type):
        record_id = self._get_selected_id(tab_type)
        if record_id is None:
            return
        if tab_type == "student":
            record = database.get_student_by_id(record_id)
        else:
            record = database.get_staff_by_id(record_id)

        from ui_card import CardPreviewWindow
        CardPreviewWindow(self.root, tab_type, record)

    def logout(self):
        confirm = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if confirm:
            self.root.destroy()
            import main
            main.main()
