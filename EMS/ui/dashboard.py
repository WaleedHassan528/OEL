"""
Dashboard — KPI cards + quick stats.
"""
import customtkinter as ctk
from services.employee_service import EmployeeService
from services.attendance_service import AttendanceService
from services.leave_service import LeaveService
from services.payroll_service import PayrollService
from datetime import date


# ── Shared colors ─────────────────────────────────────────────────────────────
BG       = "#121212"
BG_CARD  = "#1E1E2E"
ACCENT   = "#007BFF"
SUCCESS  = "#00C853"
WARNING  = "#FFA000"
DANGER   = "#F44336"
TEXT     = "#FFFFFF"
SUBTEXT  = "#9E9E9E"


class MetricCard(ctk.CTkFrame):
    """A single KPI card with icon, value, and label."""

    def __init__(self, master, icon: str, label: str, value: str,
                 accent_color: str = ACCENT, **kwargs):
        super().__init__(master, fg_color=BG_CARD, corner_radius=15,
                         border_width=1, border_color="#2A2A3E", **kwargs)
        self.configure(cursor="hand2")

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(padx=20, pady=18, fill="both", expand=True)

        # Icon circle
        icon_lbl = ctk.CTkLabel(
            inner, text=icon,
            font=ctk.CTkFont(size=32),
            text_color=accent_color,
        )
        icon_lbl.pack(anchor="w")

        self.value_lbl = ctk.CTkLabel(
            inner, text=value,
            font=ctk.CTkFont(family="Segoe UI", size=30, weight="bold"),
            text_color=TEXT,
        )
        self.value_lbl.pack(anchor="w", pady=(6, 0))

        ctk.CTkLabel(
            inner, text=label,
            font=ctk.CTkFont(size=12),
            text_color=SUBTEXT,
        ).pack(anchor="w")

        # Hover effect
        for widget in [self, inner, icon_lbl, self.value_lbl]:
            widget.bind("<Enter>", lambda e: self.configure(border_color=accent_color))
            widget.bind("<Leave>", lambda e: self.configure(border_color="#2A2A3E"))

    def update_value(self, new_value: str):
        self.value_lbl.configure(text=new_value)


class DashboardView(ctk.CTkFrame):
    """Main dashboard with KPI cards and quick attendance summary."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=BG, corner_radius=0, **kwargs)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        # ── Page header ───────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(24, 0))

        ctk.CTkLabel(
            header,
            text="Dashboard",
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
            text_color=TEXT,
        ).pack(side="left")

        today_str = date.today().strftime("%A, %B %d %Y")
        ctk.CTkLabel(
            header,
            text=today_str,
            font=ctk.CTkFont(size=13),
            text_color=SUBTEXT,
        ).pack(side="right", pady=8)

        # ── KPI grid ──────────────────────────────────────────────────────
        self.kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.kpi_frame.pack(fill="x", padx=30, pady=20)

        self.kpi_frame.columnconfigure((0, 1, 2, 3), weight=1, uniform="col")

        self.card_employees = MetricCard(
            self.kpi_frame, "👥", "Total Employees", "—",
            accent_color=ACCENT,
        )
        self.card_employees.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")

        self.card_present = MetricCard(
            self.kpi_frame, "✅", "Present Today", "—",
            accent_color=SUCCESS,
        )
        self.card_present.grid(row=0, column=1, padx=8, pady=8, sticky="nsew")

        self.card_leaves = MetricCard(
            self.kpi_frame, "📋", "Pending Leaves", "—",
            accent_color=WARNING,
        )
        self.card_leaves.grid(row=0, column=2, padx=8, pady=8, sticky="nsew")

        self.card_absent = MetricCard(
            self.kpi_frame, "❌", "Absent Today", "—",
            accent_color=DANGER,
        )
        self.card_absent.grid(row=0, column=3, padx=8, pady=8, sticky="nsew")

        # ── Second row ────────────────────────────────────────────────────
        self.kpi_frame.rowconfigure(1, weight=0)

        self.card_late = MetricCard(
            self.kpi_frame, "⏰", "Late Arrivals", "—",
            accent_color=WARNING,
        )
        self.card_late.grid(row=1, column=0, padx=8, pady=8, sticky="nsew")

        self.card_depts = MetricCard(
            self.kpi_frame, "🏢", "Departments", "—",
            accent_color="#9C27B0",
        )
        self.card_depts.grid(row=1, column=1, padx=8, pady=8, sticky="nsew")

        self.card_payroll = MetricCard(
            self.kpi_frame, "💰", "Payroll This Month", "—",
            accent_color=SUCCESS,
        )
        self.card_payroll.grid(row=1, column=2, padx=8, pady=8, sticky="nsew")

        self.card_reviews = MetricCard(
            self.kpi_frame, "⭐", "Avg Performance", "—",
            accent_color="#FFD700",
        )
        self.card_reviews.grid(row=1, column=3, padx=8, pady=8, sticky="nsew")

        # ── Attendance bar ────────────────────────────────────────────────
        att_section = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=15,
                                   border_width=1, border_color="#2A2A3E")
        att_section.pack(fill="x", padx=30, pady=(10, 20))

        ctk.CTkLabel(
            att_section,
            text="Today's Attendance Overview",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=TEXT,
        ).pack(anchor="w", padx=20, pady=(16, 6))

        self.att_bar_frame = ctk.CTkFrame(att_section, fg_color="transparent", height=30)
        self.att_bar_frame.pack(fill="x", padx=20, pady=(0, 16))

        self.att_legend = ctk.CTkLabel(
            att_section, text="", font=ctk.CTkFont(size=12), text_color=SUBTEXT
        )
        self.att_legend.pack(anchor="w", padx=20, pady=(0, 16))

        # ── Quick tips ────────────────────────────────────────────────────
        tips = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=15,
                            border_width=1, border_color="#2A2A3E")
        tips.pack(fill="x", padx=30, pady=(0, 24))

        ctk.CTkLabel(
            tips,
            text="Quick Tips",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=TEXT,
        ).pack(anchor="w", padx=20, pady=(16, 4))

        tip_texts = [
            "💡  Navigate using the sidebar to access all modules.",
            "🔑  Admin accounts can approve leaves and manage all employees.",
            "📊  Payroll is automatically calculated based on attendance.",
            "⭐  Performance reviews help track employee growth over time.",
        ]
        for t in tip_texts:
            ctk.CTkLabel(
                tips, text=t,
                font=ctk.CTkFont(size=12),
                text_color=SUBTEXT,
            ).pack(anchor="w", padx=24, pady=2)
        ctk.CTkLabel(tips, text="").pack(pady=6)

    def refresh(self):
        """Reload all metrics from the database."""
        try:
            total_emps = EmployeeService.count()
            self.card_employees.update_value(str(total_emps))

            att = AttendanceService.today_count()
            self.card_present.update_value(str(att.get("present", 0)))
            self.card_absent.update_value(str(att.get("absent", 0)))
            self.card_late.update_value(str(att.get("late", 0)))

            pending = LeaveService.pending_count()
            self.card_leaves.update_value(str(pending))

            # Departments count
            from services.department_service import DepartmentService
            dept_count = len(DepartmentService.get_all())
            self.card_depts.update_value(str(dept_count))

            # Payroll this month
            today = date.today()
            payrolls = PayrollService.get_all(month=today.month, year=today.year)
            total_payroll = sum(p["net_pay"] for p in payrolls)
            self.card_payroll.update_value(f"${total_payroll:,.0f}")

            # Avg performance
            from services.performance_service import PerformanceService
            all_reviews = PerformanceService.get_all()
            if all_reviews:
                avg = sum(r["rating"] for r in all_reviews) / len(all_reviews)
                self.card_reviews.update_value(f"{'★' * round(avg)} {avg:.1f}")
            else:
                self.card_reviews.update_value("—")

            # Attendance bar
            self._draw_att_bar(att, total_emps)

        except Exception as e:
            print(f"[Dashboard] Error refreshing: {e}")

    def _draw_att_bar(self, att: dict, total: int):
        """Draw a segmented color bar for attendance proportions."""
        for w in self.att_bar_frame.winfo_children():
            w.destroy()

        if total == 0:
            return

        segments = [
            ("present", SUCCESS),
            ("late",    WARNING),
            ("absent",  DANGER),
        ]
        total_recorded = sum(att.values()) or 1

        for key, color in segments:
            count = att.get(key, 0)
            pct   = count / max(total_recorded, 1)
            if pct > 0:
                seg = ctk.CTkFrame(
                    self.att_bar_frame,
                    fg_color=color,
                    corner_radius=6,
                    height=28,
                    width=max(int(pct * 600), 4),
                )
                seg.pack(side="left", padx=1)

        legend_parts = [
            f"✅ Present: {att.get('present',0)}",
            f"⏰ Late: {att.get('late',0)}",
            f"❌ Absent: {att.get('absent',0)}",
        ]
        self.att_legend.configure(text="   |   ".join(legend_parts))
