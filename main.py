import tkinter as tk
from tkinter import messagebox
import database

# ── Hardcoded admin credentials (simple for SLA project) ────
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("ID Card Management System — Login")
        self.root.geometry("420x340")
        self.root.resizable(False, False)
        self.root.configure(bg="#1a1a2e")

        # Centre the window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth()  // 2) - 210
        y = (self.root.winfo_screenheight() // 2) - 170
        self.root.geometry(f"420x340+{x}+{y}")

        self._build_ui()

    def _build_ui(self):
        # ── Header ──────────────────────────────────────────
        header = tk.Frame(self.root, bg="#16213e", pady=18)
        header.pack(fill="x")

        tk.Label(header, text="🪪", font=("Arial", 30),
                 bg="#16213e", fg="white").pack()
        tk.Label(header, text="ID Card Management System",
                 font=("Arial", 14, "bold"), bg="#16213e", fg="white").pack()
        tk.Label(header, text="Shri Bhagubhai Mafatlal Polytechnic",
                 font=("Arial", 9), bg="#16213e", fg="#a0aec0").pack()

        # ── Login form ──────────────────────────────────────
        form = tk.Frame(self.root, bg="#1a1a2e", padx=40, pady=20)
        form.pack(fill="both", expand=True)

        tk.Label(form, text="Username", font=("Arial", 10),
                 bg="#1a1a2e", fg="#a0aec0").pack(anchor="w")
        self.username_var = tk.StringVar()
        username_entry = tk.Entry(form, textvariable=self.username_var,
                                  font=("Arial", 11), relief="flat",
                                  bg="#16213e", fg="white",
                                  insertbackground="white")
        username_entry.pack(fill="x", ipady=6, pady=(2, 12))
        username_entry.focus()

        tk.Label(form, text="Password", font=("Arial", 10),
                 bg="#1a1a2e", fg="#a0aec0").pack(anchor="w")
        self.password_var = tk.StringVar()
        tk.Entry(form, textvariable=self.password_var, show="*",
                 font=("Arial", 11), relief="flat",
                 bg="#16213e", fg="white",
                 insertbackground="white").pack(fill="x", ipady=6, pady=(2, 18))

        tk.Button(form, text="Login", font=("Arial", 11, "bold"),
                  bg="#0f3460", fg="white", relief="flat",
                  activebackground="#e94560", activeforeground="white",
                  cursor="hand2", command=self.attempt_login
                  ).pack(fill="x", ipady=8)

        # Bind Enter key to login
        self.root.bind("<Return>", lambda e: self.attempt_login())

    def attempt_login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if not username or not password:
            messagebox.showwarning("Missing Fields", "Please enter both username and password.")
            return

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            self.root.destroy()
            self._open_dashboard()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.\n\nHint: admin / admin123")

    def _open_dashboard(self):
        from ui_dashboard import DashboardWindow
        root = tk.Tk()
        DashboardWindow(root)
        root.mainloop()


def main():
    database.initialize_db()
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
