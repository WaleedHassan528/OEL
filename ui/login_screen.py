"""
Login screen — polished dark mode login with RBAC.
"""
import customtkinter as ctk
from services.auth_service import AuthService


class LoginScreen(ctk.CTkFrame):
    """Full-screen login card."""

    # ── Colors ────────────────────────────────────────────────────────────────
    BG      = "#121212"
    CARD_BG = "#1A1A2E"
    ACCENT  = "#007BFF"
    SUCCESS = "#00C853"
    DANGER  = "#F44336"
    TEXT    = "#FFFFFF"
    SUBTEXT = "#9E9E9E"
    INPUT_BG = "#0D0D1A"

    def __init__(self, master, on_login_success):
        super().__init__(master, fg_color=self.BG, corner_radius=0)
        self.on_login_success = on_login_success
        self._build_ui()

    def _build_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ── Centered container ─────────────────────────────────────────────
        container = ctk.CTkFrame(
            self, fg_color=self.CARD_BG, corner_radius=20,
            border_width=1, border_color="#2A2A4A"
        )
        container.grid(row=0, column=0)
        container.configure(width=440, height=560)
        container.grid_propagate(False)

        # ── Logo / Title ───────────────────────────────────────────────────
        logo_frame = ctk.CTkFrame(container, fg_color="transparent")
        logo_frame.pack(pady=(40, 0))

        icon_lbl = ctk.CTkLabel(
            logo_frame,
            text="⬡",
            font=ctk.CTkFont(size=48),
            text_color=self.ACCENT,
        )
        icon_lbl.pack()

        ctk.CTkLabel(
            logo_frame,
            text="EMS Pro",
            font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
            text_color=self.TEXT,
        ).pack()

        ctk.CTkLabel(
            logo_frame,
            text="Employee Management System",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=self.SUBTEXT,
        ).pack(pady=(2, 0))

        # ── Form ──────────────────────────────────────────────────────────
        form = ctk.CTkFrame(container, fg_color="transparent")
        form.pack(padx=40, pady=30, fill="x")

        # Username
        ctk.CTkLabel(form, text="Username", font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=self.SUBTEXT).pack(anchor="w")
        self.username_entry = ctk.CTkEntry(
            form, placeholder_text="Enter username",
            height=44, corner_radius=10,
            fg_color=self.INPUT_BG, border_color=self.ACCENT,
            text_color=self.TEXT, placeholder_text_color="#555577",
            font=ctk.CTkFont(size=14),
        )
        self.username_entry.pack(fill="x", pady=(4, 14))

        # Password
        ctk.CTkLabel(form, text="Password", font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=self.SUBTEXT).pack(anchor="w")
        self.password_entry = ctk.CTkEntry(
            form, placeholder_text="Enter password",
            show="●", height=44, corner_radius=10,
            fg_color=self.INPUT_BG, border_color=self.ACCENT,
            text_color=self.TEXT, placeholder_text_color="#555577",
            font=ctk.CTkFont(size=14),
        )
        self.password_entry.pack(fill="x", pady=(4, 6))

        # Error label
        self.error_label = ctk.CTkLabel(
            form, text="", text_color=self.DANGER,
            font=ctk.CTkFont(size=12),
        )
        self.error_label.pack(anchor="w", pady=(0, 10))

        # Login button
        self.login_btn = ctk.CTkButton(
            form,
            text="Sign In",
            height=46,
            corner_radius=10,
            fg_color=self.ACCENT,
            hover_color="#0056b3",
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self._attempt_login,
        )
        self.login_btn.pack(fill="x")

        # Demo credentials hint
        hint = ctk.CTkFrame(container, fg_color="transparent")
        hint.pack(pady=(0, 20))
        ctk.CTkLabel(
            hint,
            text="Demo  →  admin / admin123   |   alice / pass123",
            font=ctk.CTkFont(size=11),
            text_color="#444466",
        ).pack()

        # Bind Enter key
        self.username_entry.bind("<Return>", lambda _: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda _: self._attempt_login())
        self.username_entry.focus()

    def _attempt_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        self.login_btn.configure(text="Signing in…", state="disabled")
        self.error_label.configure(text="")
        self.update()

        success, message = AuthService.login(username, password)

        self.login_btn.configure(text="Sign In", state="normal")

        if success:
            self.on_login_success()
        else:
            self.error_label.configure(text=f"⚠  {message}")
            self.password_entry.delete(0, "end")
            self.password_entry.focus()
