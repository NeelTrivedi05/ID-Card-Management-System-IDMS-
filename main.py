import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import database
import theme

# Load persisted theme at startup
theme.load()


class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("IDMS — Login")
        self.root.geometry("460x520")
        self.root.resizable(False, False)

        t = theme.get()
        self.root.configure(bg=t["DARK_BG"])

        # Centre the window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth()  // 2) - 230
        y = (self.root.winfo_screenheight() // 2) - 260
        self.root.geometry(f"460x520+{x}+{y}")

        self._build_ui()

    def _build_ui(self):
        t = theme.get()
        F = theme.FONTS

        # ── Header band ─────────────────────────────────────
        header = tk.Frame(self.root, bg=t["ACCENT"], height=160)
        header.pack(fill="x")
        header.pack_propagate(False)

        # Monogram circle
        circle_frame = tk.Frame(header, bg=t["ACCENT"])
        circle_frame.pack(expand=True)

        # Styled app icon
        tk.Label(circle_frame, text="🪪", font=(_family(), 36),
                 bg=t["ACCENT"], fg="#ffffff").pack(pady=(20, 4))

        tk.Label(circle_frame, text="ID Card Management System",
                 font=F["title"], bg=t["ACCENT"], fg="#ffffff").pack()

        tk.Label(circle_frame, text="Shri Bhagubhai Mafatlal Polytechnic",
                 font=F["caption"], bg=t["ACCENT"], fg="#dbeafe").pack(pady=(2, 12))

        # ── Form area ────────────────────────────────────────
        form_bg = t["PANEL_BG"]
        form = tk.Frame(self.root, bg=form_bg, padx=50, pady=30)
        form.pack(fill="both", expand=True)

        # Welcome text
        tk.Label(form, text="Welcome back",
                 font=F["heading"], bg=form_bg, fg=t["TEXT_MAIN"]).pack(anchor="w")
        tk.Label(form, text="Sign in to your account",
                 font=F["caption"], bg=form_bg, fg=t["TEXT_SUB"]).pack(anchor="w", pady=(0, 20))

        # ── Username field ──
        tk.Label(form, text="Username", font=F["caption_b"],
                 bg=form_bg, fg=t["TEXT_SUB"]).pack(anchor="w")

        user_frame = tk.Frame(form, bg=t["ENTRY_BORDER"], highlightthickness=0,
                              padx=1, pady=1)
        user_frame.pack(fill="x", pady=(4, 14))

        self.username_var = tk.StringVar()
        self.user_entry = tk.Entry(user_frame, textvariable=self.username_var,
                                    font=F["body"], relief="flat",
                                    bg=t["ENTRY_BG"], fg=t["TEXT_MAIN"],
                                    insertbackground=t["TEXT_MAIN"])
        self.user_entry.pack(fill="x", ipady=8, padx=1, pady=1)
        self.user_entry.focus()

        # Focus ring bindings
        self.user_entry.bind("<FocusIn>",
                             lambda e: user_frame.configure(bg=t["ENTRY_FOCUS"]))
        self.user_entry.bind("<FocusOut>",
                             lambda e: user_frame.configure(bg=t["ENTRY_BORDER"]))

        # ── Password field ──
        tk.Label(form, text="Password", font=F["caption_b"],
                 bg=form_bg, fg=t["TEXT_SUB"]).pack(anchor="w")

        pass_outer = tk.Frame(form, bg=t["ENTRY_BORDER"], padx=1, pady=1)
        pass_outer.pack(fill="x", pady=(4, 6))

        pass_inner = tk.Frame(pass_outer, bg=t["ENTRY_BG"])
        pass_inner.pack(fill="x", padx=1, pady=1)

        self.password_var = tk.StringVar()
        self.pass_entry = tk.Entry(pass_inner, textvariable=self.password_var,
                                    show="●", font=F["body"], relief="flat",
                                    bg=t["ENTRY_BG"], fg=t["TEXT_MAIN"],
                                    insertbackground=t["TEXT_MAIN"])
        self.pass_entry.pack(side="left", fill="x", expand=True, ipady=8)

        # Eye toggle
        self._show_pass = False
        self.eye_btn = tk.Label(pass_inner, text="👁", font=F["body"],
                                bg=t["ENTRY_BG"], fg=t["TEXT_HINT"],
                                cursor="hand2", padx=8)
        self.eye_btn.pack(side="right")
        self.eye_btn.bind("<Button-1>", self._toggle_password)

        # Focus ring
        self.pass_entry.bind("<FocusIn>",
                             lambda e: pass_outer.configure(bg=t["ENTRY_FOCUS"]))
        self.pass_entry.bind("<FocusOut>",
                             lambda e: pass_outer.configure(bg=t["ENTRY_BORDER"]))

        # ── Login button ──
        login_btn = tk.Button(form, text="Sign In", font=F["body_bold"],
                              bg=t["ACCENT"], fg="#ffffff", relief="flat",
                              activebackground=t["ACCENT_HOVER"],
                              activeforeground="#ffffff",
                              cursor="hand2", bd=0,
                              command=self.attempt_login)
        login_btn.pack(fill="x", ipady=10, pady=(16, 10))

        # Credential hint
        tk.Label(form, text="Default credentials:  admin / admin123",
                 font=F["micro"], bg=form_bg, fg=t["TEXT_HINT"]).pack()

        # Bind Enter key
        self.root.bind("<Return>", lambda e: self.attempt_login())

    def _toggle_password(self, event=None):
        self._show_pass = not self._show_pass
        self.pass_entry.config(show="" if self._show_pass else "●")
        self.eye_btn.config(text="🙈" if self._show_pass else "👁")

    def attempt_login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if not username or not password:
            messagebox.showwarning("Missing Fields",
                                   "Please enter both username and password.")
            return

        # Database-backed authentication (Feature 04)
        ok, result = database.authenticate_user(username, password)

        if ok:
            login_time = datetime.now()
            database.log_action("LOGIN", "user",
                                details=f"username={username}, role={result['role']}")
            self.root.destroy()
            self._open_dashboard(login_time, current_user=result)
        else:
            messagebox.showerror("Login Failed",
                                 f"{result}\n\nDefault: admin / admin123")

    def _open_dashboard(self, login_time=None, current_user=None):
        from ui_dashboard import DashboardWindow
        root = tk.Tk()
        DashboardWindow(root, login_time=login_time, current_user=current_user)
        root.mainloop()


def _family():
    """Return the theme font family."""
    return theme.FONTS["body"][0]


def main():
    database.initialize_db()
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
