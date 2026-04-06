import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import shutil
import os
from datetime import date
import database

DARK_BG   = "#1a1a2e"
PANEL_BG  = "#16213e"
ACCENT    = "#0f3460"
ACCENT2   = "#e94560"
TEXT_MAIN = "#ffffff"
TEXT_SUB  = "#a0aec0"

PHOTOS_DIR = "photos"
os.makedirs(PHOTOS_DIR, exist_ok=True)

STUDENT_YEARS   = ["First Year", "Second Year", "Third Year"]
DEPARTMENTS_CSE = ["Computer Engineering", "Information Technology",
                   "Electronics", "Mechanical", "Civil", "Electrical"]
DESIGNATIONS    = ["Lecturer", "Senior Lecturer", "HOD",
                   "Lab Assistant", "Clerk", "Principal", "Other"]


class RecordForm:
    def __init__(self, parent, tab_type, mode, record, on_save):
        self.parent   = parent
        self.tab_type = tab_type   # "student" or "staff"
        self.mode     = mode       # "add" or "edit"
        self.record   = record
        self.on_save  = on_save
        self.photo_path = record.get("photo_path", "") if record else ""

        title_map = {
            ("student", "add"):  "Add New Student",
            ("student", "edit"): "Edit Student Record",
            ("staff",   "add"):  "Add New Staff Member",
            ("staff",   "edit"): "Edit Staff Record",
        }

        self.win = tk.Toplevel(parent)
        self.win.title(title_map[(tab_type, mode)])
        self.win.geometry("480x560")
        self.win.configure(bg=DARK_BG)
        self.win.resizable(False, False)
        self.win.grab_set()

        # Centre
        self.win.update_idletasks()
        x = (self.win.winfo_screenwidth()  // 2) - 240
        y = (self.win.winfo_screenheight() // 2) - 280
        self.win.geometry(f"480x560+{x}+{y}")

        self._build_form()
        if mode == "edit" and record:
            self._populate_fields()

    # ── Build the form ────────────────────────────────────────

    def _build_form(self):
        # Header
        hdr = tk.Frame(self.win, bg=PANEL_BG, pady=12)
        hdr.pack(fill="x")
        title_text = ("Add" if self.mode == "add" else "Edit") + \
                     (" Student" if self.tab_type == "student" else " Staff")
        tk.Label(hdr, text=title_text, font=("Arial", 13, "bold"),
                 bg=PANEL_BG, fg=TEXT_MAIN).pack()

        # Scrollable body
        canvas = tk.Canvas(self.win, bg=DARK_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.win, orient="vertical", command=canvas.yview)
        self.body = tk.Frame(canvas, bg=DARK_BG, padx=30, pady=10)

        self.body.bind("<Configure>",
                       lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.body, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.vars = {}

        if self.tab_type == "student":
            self._field("Full Name *",       "name")
            self._field("Roll Number *",     "roll_no")
            self._dropdown("Department *",   "department", DEPARTMENTS_CSE)
            self._dropdown("Year *",         "year",       STUDENT_YEARS)
            self._field("Contact Number",    "contact")
            self._field("Email",             "email")
        else:
            self._field("Full Name *",       "name")
            self._field("Employee ID *",     "employee_id")
            self._dropdown("Department *",   "department", DEPARTMENTS_CSE)
            self._dropdown("Designation *",  "designation", DESIGNATIONS)
            self._field("Contact Number",    "contact")
            self._field("Email",             "email")

        self._date_field("Issue Date *",     "issue_date")
        self._photo_field()

        # Buttons
        btn_frame = tk.Frame(self.body, bg=DARK_BG, pady=10)
        btn_frame.pack(fill="x")

        tk.Button(btn_frame, text="Save",
                  font=("Arial", 11, "bold"), bg="#2ecc71", fg="white",
                  relief="flat", cursor="hand2",
                  command=self.save).pack(side="left", expand=True,
                                          fill="x", padx=(0, 6), ipady=8)
        tk.Button(btn_frame, text="Cancel",
                  font=("Arial", 11), bg=ACCENT2, fg="white",
                  relief="flat", cursor="hand2",
                  command=self.win.destroy).pack(side="left", expand=True,
                                                  fill="x", ipady=8)

    def _label(self, text):
        tk.Label(self.body, text=text, font=("Arial", 9),
                 bg=DARK_BG, fg=TEXT_SUB).pack(anchor="w", pady=(8, 1))

    def _field(self, label, key):
        self._label(label)
        var = tk.StringVar()
        tk.Entry(self.body, textvariable=var, font=("Arial", 10),
                 bg=PANEL_BG, fg=TEXT_MAIN, insertbackground="white",
                 relief="flat").pack(fill="x", ipady=6)
        self.vars[key] = var

    def _dropdown(self, label, key, options):
        self._label(label)
        var = tk.StringVar(value=options[0])
        cb = ttk.Combobox(self.body, textvariable=var,
                          values=options, state="readonly",
                          font=("Arial", 10))
        cb.pack(fill="x", ipady=4)
        self.vars[key] = var

    def _date_field(self, label, key):
        self._label(label)
        var = tk.StringVar(value=date.today().strftime("%d-%m-%Y"))
        tk.Entry(self.body, textvariable=var, font=("Arial", 10),
                 bg=PANEL_BG, fg=TEXT_MAIN, insertbackground="white",
                 relief="flat").pack(fill="x", ipady=6)
        tk.Label(self.body, text="Format: DD-MM-YYYY", font=("Arial", 8),
                 bg=DARK_BG, fg="#666").pack(anchor="w")
        self.vars[key] = var

    def _photo_field(self):
        self._label("Photo")
        row = tk.Frame(self.body, bg=DARK_BG)
        row.pack(fill="x", pady=(2, 0))

        self.photo_label = tk.Label(row, text="No photo selected",
                                    font=("Arial", 9), bg=DARK_BG, fg=TEXT_SUB,
                                    wraplength=280, anchor="w")
        self.photo_label.pack(side="left", fill="x", expand=True)

        tk.Button(row, text="Browse",
                  font=("Arial", 9), bg=ACCENT, fg="white",
                  relief="flat", cursor="hand2",
                  command=self.browse_photo).pack(side="right", ipady=4, ipadx=8)

    # ── Populate for edit mode ────────────────────────────────

    def _populate_fields(self):
        r = self.record
        field_map = {
            "name":        r.get("name", ""),
            "roll_no":     r.get("roll_no", ""),
            "employee_id": r.get("employee_id", ""),
            "department":  r.get("department", ""),
            "year":        r.get("year", ""),
            "designation": r.get("designation", ""),
            "contact":     r.get("contact", ""),
            "email":       r.get("email", ""),
            "issue_date":  r.get("issue_date", ""),
        }
        for key, val in field_map.items():
            if key in self.vars and val:
                self.vars[key].set(val)

        photo = r.get("photo_path", "")
        if photo and os.path.exists(photo):
            self.photo_path = photo
            self.photo_label.config(text=os.path.basename(photo))

    # ── Photo browse ──────────────────────────────────────────

    def browse_photo(self):
        path = filedialog.askopenfilename(
            title="Select Photo",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )
        if path:
            filename  = os.path.basename(path)
            dest_path = os.path.join(PHOTOS_DIR, filename)
            try:
                shutil.copy2(path, dest_path)
                self.photo_path = dest_path
                self.photo_label.config(text=filename, fg="#2ecc71")
            except Exception as e:
                messagebox.showerror("Photo Error", str(e))

    # ── Validation ────────────────────────────────────────────

    def _get(self, key):
        return self.vars[key].get().strip() if key in self.vars else ""

    def _validate(self):
        name = self._get("name")
        if not name:
            messagebox.showwarning("Validation", "Full Name is required.")
            return False

        if self.tab_type == "student":
            if not self._get("roll_no"):
                messagebox.showwarning("Validation", "Roll Number is required.")
                return False
        else:
            if not self._get("employee_id"):
                messagebox.showwarning("Validation", "Employee ID is required.")
                return False

        if not self._get("issue_date"):
            messagebox.showwarning("Validation", "Issue Date is required.")
            return False

        return True

    # ── Save ──────────────────────────────────────────────────

    def save(self):
        if not self._validate():
            return

        if self.tab_type == "student":
            args = (
                self._get("name"),
                self._get("roll_no"),
                self._get("department"),
                self._get("year"),
                self._get("contact"),
                self._get("email"),
                self.photo_path,
                self._get("issue_date"),
            )
            if self.mode == "add":
                success, msg = database.add_student(*args)
            else:
                success, msg = database.update_student(self.record["id"], *args)
        else:
            args = (
                self._get("name"),
                self._get("employee_id"),
                self._get("department"),
                self._get("designation"),
                self._get("contact"),
                self._get("email"),
                self.photo_path,
                self._get("issue_date"),
            )
            if self.mode == "add":
                success, msg = database.add_staff(*args)
            else:
                success, msg = database.update_staff(self.record["id"], *args)

        if success:
            messagebox.showinfo("Success", msg)
            self.win.destroy()
            self.on_save()
        else:
            messagebox.showerror("Error", msg)
