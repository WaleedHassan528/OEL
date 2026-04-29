"""
Main application window — sidebar navigation + view container.
"""
import customtkinter as ctk
from services.auth_service import AuthService
from ui.login_screen import LoginScreen
from ui.dashboard    import DashboardView
from ui.employees    import EmployeeView
from ui.attendance   import AttendanceView
from ui.leave        import LeaveView
from ui.payroll      import PayrollView
from ui.performance  import PerformanceView
from ui.departments  import DepartmentView

# ── Design Tokens ─────────────────────────────────────────────────────────────
BG_SIDEBAR  = "#0D0D1A"
BG_MAIN     = "#121212"
ACCENT      = "#007BFF"
SUCCESS     = "#00C853"
TEXT        = "#FFFFFF"
SUBTEXT     = "#9E9E9E"
HOVER_BG    = "#1E1E3A"
ACTIVE_BG   = "#1A2A4A"

NAV_ITEMS = [
    ("dashboard",   "⬡",  "Dashboard"),
    ("employees",   "👥", "Employees"),
    ("attendance",  "📅", "Attendance"),
    ("leave",       "🌴", "Leave"),
    ("payroll",     "💰", "Payroll"),
    ("performance", "⭐", "Performance"),
    ("departments", "🏢", "Departments"),
]


class SidebarButton(ctk.CTkFrame):
    """A single sidebar navigation item."""

    def __init__(self, master, icon: str, label: str,
                 on_click, active: bool = False, **kwargs):
        super().__init__(master, fg_color="transparent", corner_radius=10, **kwargs)
        self._active    = False
        self._on_click  = on_click
        self._icon_lbl  = None
        self._text_lbl  = None
        self._build(icon, label)
        if active:
            self.set_active(True)

    def _build(self, icon: str, label: str):
        self.configure(cursor="hand2")
        inner = ctk.CTkFrame(self, fg_color="transparent", corner_radius=10)
        inner.pack(fill="x", padx=6, pady=2)

        self._icon_lbl = ctk.CTkLabel(
            inner, text=icon,
            font=ctk.CTkFont(size=18),
            width=32,
            text_color=SUBTEXT,
        )
        self._icon_lbl.pack(side="left", padx=(12, 6), pady=10)

        self._text_lbl = ctk.CTkLabel(
            inner, text=label,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=SUBTEXT,
            anchor="w",
        )
        self._text_lbl.pack(side="left", pady=10)

        # Hover
        for widget in [self, inner, self._icon_lbl, self._text_lbl]:
            widget.bind("<Button-1>", lambda e: self._on_click())
            widget.bind("<Enter>",    lambda e: self._on_hover(True))
            widget.bind("<Leave>",    lambda e: self._on_hover(False))

    def _on_hover(self, entered: bool):
        if not self._active:
            new_color = HOVER_BG if entered else "transparent"
            self.configure(fg_color=new_color)

    def set_active(self, active: bool):
        self._active = active
        if active:
            self.configure(fg_color=ACTIVE_BG)
            self._icon_lbl.configure(text_color=ACCENT)
            self._text_lbl.configure(text_color=TEXT,
                                      font=ctk.CTkFont(size=13, weight="bold"))
        else:
            self.configure(fg_color="transparent")
            self._icon_lbl.configure(text_color=SUBTEXT)
            self._text_lbl.configure(text_color=SUBTEXT,
                                      font=ctk.CTkFont(size=13, weight="normal"))


class MainApp(ctk.CTk):
    """Root application window."""

    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("EMS Pro — Employee Management System")
        self.geometry("1280x800")
        self.minsize(1100, 700)
        self.configure(fg_color=BG_MAIN)

        self._current_view  = None
        self._sidebar_btns  : dict[str, SidebarButton] = {}
        self._active_key    = "dashboard"

        self._show_login()

    # ── Login Flow ─────────────────────────────────────────────────────────────

    def _show_login(self):
        for w in self.winfo_children():
            w.destroy()
        login = LoginScreen(self, on_login_success=self._show_main)
        login.pack(fill="both", expand=True)

    def _show_main(self):
        for w in self.winfo_children():
            w.destroy()
        self._build_layout()
        self._navigate("dashboard")

    # ── Layout ─────────────────────────────────────────────────────────────────

    def _build_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ── Sidebar ─────────────────────────────────────────────────────────
        sidebar = ctk.CTkFrame(
            self, fg_color=BG_SIDEBAR, corner_radius=0, width=220
        )
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        # Logo
        logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        logo_frame.pack(pady=(24, 16), padx=16, fill="x")

        ctk.CTkLabel(
            logo_frame, text="⬡ EMS Pro",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=ACCENT,
        ).pack(anchor="w")

        ctk.CTkLabel(
            logo_frame, text="Management System",
            font=ctk.CTkFont(size=10),
            text_color=SUBTEXT,
        ).pack(anchor="w")

        # Separator
        ctk.CTkFrame(sidebar, fg_color="#1A1A3A", height=1).pack(fill="x", padx=16, pady=4)

        # Nav items
        nav_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        nav_frame.pack(fill="x", pady=8)

        # Filter items based on role
        user = AuthService.get_current_user()
        is_admin = AuthService.is_admin()

        for key, icon, label in NAV_ITEMS:
            # Employees and Departments hidden for non-admin
            if not is_admin and key in ("departments",):
                continue

            btn = SidebarButton(
                nav_frame, icon=icon, label=label,
                on_click=lambda k=key: self._navigate(k),
            )
            btn.pack(fill="x", padx=8)
            self._sidebar_btns[key] = btn

        # Push logout to bottom
        sidebar.pack_propagate(False)

        # User info + logout
        bottom = ctk.CTkFrame(sidebar, fg_color="transparent")
        bottom.pack(side="bottom", fill="x", padx=12, pady=16)

        ctk.CTkFrame(bottom, fg_color="#1A1A3A", height=1).pack(fill="x", pady=(0, 12))

        if user:
            role_color = ACCENT if is_admin else SUCCESS
            ctk.CTkLabel(
                bottom,
                text=f"👤  {user.username}",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=TEXT,
            ).pack(anchor="w", padx=4)

            ctk.CTkLabel(
                bottom,
                text=f"  {user.role.upper()}",
                fg_color=role_color,
                corner_radius=6,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=TEXT, width=70, height=20,
            ).pack(anchor="w", padx=4, pady=(2, 8))

        ctk.CTkButton(
            bottom,
            text="⏻  Sign Out",
            fg_color="#1E1E2E", hover_color=HOVER_BG,
            text_color=SUBTEXT, corner_radius=8, height=36,
            font=ctk.CTkFont(size=12),
            command=self._logout,
        ).pack(fill="x")

        # ── Main content area ───────────────────────────────────────────────
        self.content_frame = ctk.CTkFrame(self, fg_color=BG_MAIN, corner_radius=0)
        self.content_frame.grid(row=0, column=1, sticky="nsew")

    # ── Navigation ─────────────────────────────────────────────────────────────

    def _navigate(self, key: str):
        if self._active_key == key and self._current_view:
            # Refresh instead of recreating
            if hasattr(self._current_view, "refresh"):
                self._current_view.refresh()
            return

        # Update sidebar
        for k, btn in self._sidebar_btns.items():
            btn.set_active(k == key)

        self._active_key = key

        # Destroy current view
        if self._current_view:
            self._current_view.destroy()

        # Create new view
        view_map = {
            "dashboard":   DashboardView,
            "employees":   EmployeeView,
            "attendance":  AttendanceView,
            "leave":       LeaveView,
            "payroll":     PayrollView,
            "performance": PerformanceView,
            "departments": DepartmentView,
        }

        ViewClass = view_map.get(key, DashboardView)
        self._current_view = ViewClass(self.content_frame)
        self._current_view.pack(fill="both", expand=True)

    # ── Logout ─────────────────────────────────────────────────────────────────

    def _logout(self):
        AuthService.logout()
        self._current_view  = None
        self._sidebar_btns  = {}
        self._show_login()
