import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import shutil
import os
from datetime import date
import database
import theme as _theme

# ── Theme accessors ──
def _c(key):
    return _theme.get()[key]

def _t():
    return _theme.get()

F = _theme.FONTS  # shortcut

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
        self.tab_type = tab_type
        self.mode     = mode
        self.record   = record
        self.on_save  = on_save
        self.photo_path = record.get("photo_path", "") if record else ""

        title_map = {
            ("student", "add"):  "Add New Student",
            ("student", "edit"): "Edit Student Record",
            ("staff",   "add"):  "Add New Staff Member",
            ("staff",   "edit"): "Edit Staff Record",
        }

        t = _t()

        self.win = tk.Toplevel(parent)
        self.win.title(title_map[(tab_type, mode)])
        self.win.geometry("500x600")
        self.win.configure(bg=t["DARK_BG"])
        self.win.resizable(False, False)
        self.win.grab_set()

        # Centre
        self.win.update_idletasks()
        x = (self.win.winfo_screenwidth()  // 2) - 250
        y = (self.win.winfo_screenheight() // 2) - 300
        self.win.geometry(f"500x600+{x}+{y}")

        self._build_form()
        if mode == "edit" and record:
            self._populate_fields()

    # ── Build the form ────────────────────────────────────────

    def _build_form(self):
        t = _t()

        # Header
        hdr = tk.Frame(self.win, bg=t["ACCENT"], pady=14)
        hdr.pack(fill="x")
        title_text = ("Add" if self.mode == "add" else "Edit") + \
                     (" Student" if self.tab_type == "student" else " Staff")
        tk.Label(hdr, text=title_text, font=F["title"],
                 bg=t["ACCENT"], fg="#ffffff").pack()

        # Scrollable body
        canvas = tk.Canvas(self.win, bg=t["DARK_BG"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.win, orient="vertical", command=canvas.yview)
        self.body = tk.Frame(canvas, bg=t["DARK_BG"], padx=34, pady=14)

        self.body.bind("<Configure>",
                       lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_win = canvas.create_window((0, 0), window=self.body, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Stretch body to canvas width
        def _on_canvas_configure(event):
            canvas.itemconfig(canvas_win, width=event.width)
        canvas.bind("<Configure>", _on_canvas_configure)

        # Mousewheel scroll
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.vars = {}

        if self.tab_type == "student":
            self._field("Full Name",    "name",    required=True)
            self._field("Roll Number",  "roll_no", required=True)
            self._dropdown("Department", "department", DEPARTMENTS_CSE, required=True)
            self._dropdown("Year",       "year",       STUDENT_YEARS,   required=True)
            self._field("Contact Number", "contact")
            self._field("Email",          "email")
        else:
            self._field("Full Name",    "name",        required=True)
            self._field("Employee ID",  "employee_id", required=True)
            self._dropdown("Department", "department", DEPARTMENTS_CSE, required=True)
            self._dropdown("Designation","designation", DESIGNATIONS,   required=True)
            self._field("Contact Number", "contact")
            self._field("Email",          "email")

        self._date_field("Issue Date",  "issue_date", required=True)
        self._photo_field()

        # ── Divider ──
        tk.Frame(self.body, bg=t["SEPARATOR"], height=1).pack(fill="x", pady=(16, 10))

        # ── Buttons ──
        btn_frame = tk.Frame(self.body, bg=t["DARK_BG"])
        btn_frame.pack(fill="x")

        tk.Button(btn_frame, text="💾  Save Record",
                  font=F["body_bold"], bg=t["BTN_SUCCESS"], fg="#ffffff",
                  activebackground="#16a34a", activeforeground="#ffffff",
                  relief="flat", cursor="hand2", bd=0,
                  command=self.save).pack(side="left", expand=True,
                                          fill="x", padx=(0, 6), ipady=10)
        tk.Button(btn_frame, text="Cancel",
                  font=F["body"], bg=t["BTN_SECONDARY"], fg="#ffffff",
                  activebackground="#64748b", activeforeground="#ffffff",
                  relief="flat", cursor="hand2", bd=0,
                  command=self.win.destroy).pack(side="left", expand=True,
                                                  fill="x", ipady=10)

    # ── Reusable field builders ───────────────────────────────

    def _label(self, text, required=False):
        t = _t()
        row = tk.Frame(self.body, bg=t["DARK_BG"])
        row.pack(anchor="w", pady=(10, 2))

        tk.Label(row, text=text, font=F["caption_b"],
                 bg=t["DARK_BG"], fg=t["TEXT_SUB"]).pack(side="left")

        if required:
            tk.Label(row, text=" *", font=F["caption_b"],
                     bg=t["DARK_BG"], fg=t["BADGE_EXPIRED"]).pack(side="left")

    def _field(self, label, key, required=False):
        t = _t()
        self._label(label, required)

        wrap = tk.Frame(self.body, bg=t["ENTRY_BORDER"], padx=1, pady=1)
        wrap.pack(fill="x")

        var = tk.StringVar()
        entry = tk.Entry(wrap, textvariable=var, font=F["body"],
                         bg=t["ENTRY_BG"], fg=t["TEXT_MAIN"],
                         insertbackground=t["TEXT_MAIN"],
                         relief="flat")
        entry.pack(fill="x", ipady=7, padx=1, pady=1)

        # Focus ring
        entry.bind("<FocusIn>",
                   lambda e, w=wrap: w.configure(bg=t["ENTRY_FOCUS"]))
        entry.bind("<FocusOut>",
                   lambda e, w=wrap: w.configure(bg=t["ENTRY_BORDER"]))

        self.vars[key] = var

    def _dropdown(self, label, key, options, required=False):
        t = _t()
        self._label(label, required)

        wrap = tk.Frame(self.body, bg=t["ENTRY_BORDER"], padx=1, pady=1)
        wrap.pack(fill="x")

        var = tk.StringVar(value=options[0])
        cb = ttk.Combobox(wrap, textvariable=var,
                          values=options, state="readonly",
                          font=F["body"])
        cb.pack(fill="x", ipady=4, padx=1, pady=1)
        self.vars[key] = var

    def _date_field(self, label, key, required=False):
        t = _t()
        self._label(label, required)

        wrap = tk.Frame(self.body, bg=t["ENTRY_BORDER"], padx=1, pady=1)
        wrap.pack(fill="x")

        var = tk.StringVar(value=date.today().strftime("%d-%m-%Y"))
        entry = tk.Entry(wrap, textvariable=var, font=F["body"],
                         bg=t["ENTRY_BG"], fg=t["TEXT_MAIN"],
                         insertbackground=t["TEXT_MAIN"],
                         relief="flat")
        entry.pack(fill="x", ipady=7, padx=1, pady=1)

        entry.bind("<FocusIn>",
                   lambda e, w=wrap: w.configure(bg=t["ENTRY_FOCUS"]))
        entry.bind("<FocusOut>",
                   lambda e, w=wrap: w.configure(bg=t["ENTRY_BORDER"]))

        tk.Label(self.body, text="📅  Format: DD-MM-YYYY", font=F["micro"],
                 bg=t["DARK_BG"], fg=t["TEXT_HINT"]).pack(anchor="w", pady=(2, 0))

        self.vars[key] = var

    def _photo_field(self):
        t = _t()
        self._label("Photo")

        # Photo row with thumbnail preview
        row = tk.Frame(self.body, bg=t["DARK_BG"])
        row.pack(fill="x", pady=(2, 0))

        # Thumbnail preview (initially hidden)
        self.photo_thumb = tk.Label(row, bg=t["DARK_BG"], width=5, height=3)
        self.photo_thumb.pack(side="left", padx=(0, 8))

        self.photo_label = tk.Label(row, text="No photo selected",
                                    font=F["caption"], bg=t["DARK_BG"],
                                    fg=t["TEXT_HINT"], wraplength=240, anchor="w")
        self.photo_label.pack(side="left", fill="x", expand=True)

        tk.Button(row, text="📷  Browse",
                  font=F["caption_b"], bg=t["ACCENT"], fg="#ffffff",
                  activebackground=t["ACCENT_HOVER"],
                  relief="flat", cursor="hand2", bd=0,
                  command=self.browse_photo).pack(side="right", ipady=5, ipadx=10)

        # If editing and photo exists, show thumbnail
        if self.photo_path and os.path.exists(self.photo_path):
            self._update_photo_thumb(self.photo_path)

    def _update_photo_thumb(self, path):
        """Show a small thumbnail preview of the selected photo."""
        try:
            from PIL import Image, ImageTk
            img = Image.open(path).resize((40, 50), Image.LANCZOS)
            photo_img = ImageTk.PhotoImage(img)
            self.photo_thumb.configure(image=photo_img)
            self.photo_thumb.image = photo_img
        except Exception:
            pass

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
            self.photo_label.config(text=os.path.basename(photo), fg=_c("BADGE_VALID"))
            self._update_photo_thumb(photo)

    # ── Photo browse ──────────────────────────────────────────

    def validate_photo_face(self, path):
        try:
            import cv2
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            face_cascade = cv2.CascadeClassifier(cascade_path)
            img = cv2.imread(path)
            if img is None:
                return False
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4)
            return len(faces) > 0
        except Exception as e:
            print(f"Face validation error: {e}")
            return True

    def browse_photo(self):
        path = filedialog.askopenfilename(
            title="Select Photo",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )
        if path:
            if not self.validate_photo_face(path):
                messagebox.showerror("Invalid Photo",
                    "No clear human face detected in the selected photo.\n"
                    "Please choose a valid photo containing a face.")
                return

            # Feature 05: Open crop dialog
            try:
                from photo_crop import PhotoCropDialog
                crop_dlg = PhotoCropDialog(self.win, path, output_dir=PHOTOS_DIR)
                self.win.wait_window(crop_dlg.win)

                if crop_dlg.result_path:
                    self.photo_path = crop_dlg.result_path
                    self.photo_label.config(
                        text=os.path.basename(crop_dlg.result_path),
                        fg=_c("BADGE_VALID"),
                    )
                    self._update_photo_thumb(crop_dlg.result_path)
                    return
            except Exception as e:
                print(f"Crop dialog error (falling back to raw copy): {e}")

            # Fallback: direct copy
            filename  = os.path.basename(path)
            dest_path = os.path.join(PHOTOS_DIR, filename)
            try:
                shutil.copy2(path, dest_path)
                self.photo_path = dest_path
                self.photo_label.config(text=filename, fg=_c("BADGE_VALID"))
                self._update_photo_thumb(dest_path)
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
