"""
Payroll UI — payslip generator with a beautiful preview modal.
"""
import customtkinter as ctk
from tkinter import messagebox
from datetime import date
from services.payroll_service import PayrollService
from services.employee_service import EmployeeService
from services.auth_service import AuthService
from utils.helpers import format_currency, month_name

BG       = "#121212"
BG_CARD  = "#1E1E2E"
ACCENT   = "#007BFF"
SUCCESS  = "#00C853"
WARNING  = "#FFA000"
DANGER   = "#F44336"
TEXT     = "#FFFFFF"
SUBTEXT  = "#9E9E9E"
INPUT_BG = "#0D0D1A"


class PayslipPreview(ctk.CTkToplevel):
    """Beautiful payslip preview modal."""

    def __init__(self, master, payslip: dict):
        super().__init__(master)
        self.payslip = payslip
        self.title("Payslip Preview")
        self.geometry("500x680")
        self.resizable(False, False)
        self.configure(fg_color=BG)
        self.grab_set()
        self._build()

    def _build(self):
        # Payslip card
        card = ctk.CTkScrollableFrame(self, fg_color=BG, corner_radius=0)
        card.pack(fill="both", expand=True, padx=20, pady=20)

        p = self.payslip

        # ── Header ──────────────────────────────────────────────────────────
        hdr = ctk.CTkFrame(card, fg_color=ACCENT, corner_radius=12)
        hdr.pack(fill="x", pady=(0, 4))

        ctk.CTkLabel(
            hdr, text="⬡ EMS Pro",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=TEXT,
        ).pack(pady=(18, 2))

        ctk.CTkLabel(
            hdr, text="PAYSLIP",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#CCEEFF",
        ).pack()

        ctk.CTkLabel(
            hdr, text=f"{p['month_name']} {p['year']}",
            font=ctk.CTkFont(size=11),
            text_color="#CCEEFF",
        ).pack(pady=(0, 16))

        # ── Employee Info ────────────────────────────────────────────────────
        info = ctk.CTkFrame(card, fg_color=BG_CARD, corner_radius=10)
        info.pack(fill="x", pady=(8, 4))
        info.columnconfigure((0, 1), weight=1)

        def info_row(parent, label, value, row, col=0):
            f = ctk.CTkFrame(parent, fg_color="transparent")
            f.grid(row=row, column=col, padx=16, pady=6, sticky="w")
            ctk.CTkLabel(f, text=label, font=ctk.CTkFont(size=11),
                         text_color=SUBTEXT).pack(anchor="w")
            ctk.CTkLabel(f, text=str(value), font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=TEXT).pack(anchor="w")

        info_row(info, "Employee",   p["emp_name"],  0, 0)
        info_row(info, "Employee ID",p["emp_code"],  0, 1)
        info_row(info, "Position",   p["position"],  1, 0)
        info_row(info, "Department", p["department"],1, 1)
        info_row(info, "Generated",  p["generated_on"], 2, 0)

        # ── Attendance ───────────────────────────────────────────────────────
        att = ctk.CTkFrame(card, fg_color=BG_CARD, corner_radius=10)
        att.pack(fill="x", pady=4)

        ctk.CTkLabel(att, text="Attendance Summary",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=TEXT).pack(anchor="w", padx=16, pady=(12, 4))

        att_row = ctk.CTkFrame(att, fg_color="transparent")
        att_row.pack(fill="x", padx=16, pady=(0, 12))

        for label, val, color in [
            ("Working Days", p["working_days"], SUBTEXT),
            ("Present",      p["present_days"], SUCCESS),
            ("Absent",       p["absent_days"],  DANGER),
        ]:
            col = ctk.CTkFrame(att_row, fg_color="#0D0D1A", corner_radius=8)
            col.pack(side="left", expand=True, fill="x", padx=4)
            ctk.CTkLabel(col, text=str(val), font=ctk.CTkFont(size=20, weight="bold"),
                         text_color=color).pack(pady=(10, 2))
            ctk.CTkLabel(col, text=label, font=ctk.CTkFont(size=10),
                         text_color=SUBTEXT).pack(pady=(0, 10))

        # ── Earnings / Deductions ────────────────────────────────────────────
        earnings = ctk.CTkFrame(card, fg_color=BG_CARD, corner_radius=10)
        earnings.pack(fill="x", pady=4)

        ctk.CTkLabel(earnings, text="Earnings & Deductions",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=TEXT).pack(anchor="w", padx=16, pady=(12, 4))

        def earn_row(parent, label, value, color=TEXT):
            r = ctk.CTkFrame(parent, fg_color="transparent")
            r.pack(fill="x", padx=16, pady=3)
            ctk.CTkLabel(r, text=label, font=ctk.CTkFont(size=12),
                         text_color=SUBTEXT).pack(side="left")
            ctk.CTkLabel(r, text=value, font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=color).pack(side="right")

        earn_row(earnings, "Base Salary",          p["fmt_base"])
        earn_row(earnings, "Prorated (Attendance)",p["fmt_prorated"])
        earn_row(earnings, "+ Housing Allowance",  p["fmt_allowances"], SUCCESS)
        earn_row(earnings, "— Tax",                p["fmt_tax"], DANGER)
        earn_row(earnings, "— Other Deductions",   format_currency(p["deductions"] - p["tax"]))

        # Separator
        sep = ctk.CTkFrame(earnings, fg_color="#2A2A4A", height=1)
        sep.pack(fill="x", padx=16, pady=8)
        ctk.CTkLabel(earnings, text="", height=4).pack()

        # ── Net Pay ─────────────────────────────────────────────────────────
        net = ctk.CTkFrame(card, fg_color=SUCCESS, corner_radius=10)
        net.pack(fill="x", pady=4)

        ctk.CTkLabel(net, text="NET PAY",
                     font=ctk.CTkFont(size=12),
                     text_color="#003A1A").pack(pady=(14, 2))

        ctk.CTkLabel(net, text=p["fmt_net"],
                     font=ctk.CTkFont(size=28, weight="bold"),
                     text_color=TEXT).pack(pady=(0, 14))

        # Close button
        ctk.CTkButton(
            card, text="Close",
            fg_color=BG_CARD, hover_color="#2A2A4A",
            text_color=TEXT, corner_radius=8, height=40,
            command=self.destroy,
        ).pack(fill="x", pady=(16, 0))


class PayrollView(ctk.CTkFrame):
    """Payroll management view — generate and view payslips."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=BG, corner_radius=0, **kwargs)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        # Header
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=30, pady=(24, 0))

        ctk.CTkLabel(hdr, text="💰  Payroll",
                     font=ctk.CTkFont(size=26, weight="bold"),
                     text_color=TEXT).pack(side="left")

        # Generator panel
        gen = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=15,
                           border_width=1, border_color="#2A2A3E")
        gen.pack(fill="x", padx=30, pady=(20, 8))

        ctk.CTkLabel(gen, text="Generate Payslip",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=TEXT).pack(anchor="w", padx=20, pady=(16, 8))

        controls = ctk.CTkFrame(gen, fg_color="transparent")
        controls.pack(fill="x", padx=20, pady=(0, 16))

        # Employee dropdown
        ctk.CTkLabel(controls, text="Employee:", text_color=SUBTEXT,
                     font=ctk.CTkFont(size=12)).grid(row=0, column=0, padx=(0, 8), sticky="w")

        emps = EmployeeService.get_all(status_filter="active")
        emp_names = [f"{e['emp_code']} — {e['full_name']}" for e in emps]
        self._emp_map = {f"{e['emp_code']} — {e['full_name']}": e['id'] for e in emps}

        self.emp_var = ctk.StringVar(value=emp_names[0] if emp_names else "")
        ctk.CTkOptionMenu(
            controls, variable=self.emp_var, values=emp_names,
            fg_color=INPUT_BG, button_color=ACCENT,
            text_color=TEXT, dropdown_fg_color=BG_CARD,
            corner_radius=8, height=36, width=220,
        ).grid(row=0, column=1, padx=8)

        # Month
        ctk.CTkLabel(controls, text="Month:", text_color=SUBTEXT,
                     font=ctk.CTkFont(size=12)).grid(row=0, column=2, padx=(16, 8), sticky="w")
        self.month_var = ctk.StringVar(value=str(date.today().month))
        ctk.CTkOptionMenu(
            controls, variable=self.month_var,
            values=[str(i) for i in range(1, 13)],
            fg_color=INPUT_BG, button_color=ACCENT,
            text_color=TEXT, dropdown_fg_color=BG_CARD,
            corner_radius=8, height=36, width=70,
        ).grid(row=0, column=3, padx=4)

        # Year
        ctk.CTkLabel(controls, text="Year:", text_color=SUBTEXT,
                     font=ctk.CTkFont(size=12)).grid(row=0, column=4, padx=(8, 4), sticky="w")
        self.year_var = ctk.StringVar(value=str(date.today().year))
        ctk.CTkOptionMenu(
            controls, variable=self.year_var,
            values=[str(y) for y in range(2022, date.today().year + 2)],
            fg_color=INPUT_BG, button_color=ACCENT,
            text_color=TEXT, dropdown_fg_color=BG_CARD,
            corner_radius=8, height=36, width=90,
        ).grid(row=0, column=5, padx=4)

        ctk.CTkButton(
            controls, text="⚡ Generate",
            fg_color=ACCENT, hover_color="#0056b3",
            text_color=TEXT, corner_radius=8, height=36,
            command=self._generate,
        ).grid(row=0, column=6, padx=(16, 0))

        # Column headers
        cols = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=0)
        cols.pack(fill="x", padx=30, pady=(8, 2))

        for h_text, w in [("Employee", 200), ("Period", 120), ("Base Salary", 120),
                           ("Allowances", 110), ("Deductions", 110),
                           ("Net Pay", 120), ("", 90)]:
            ctk.CTkLabel(cols, text=h_text, width=w,
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=SUBTEXT, anchor="w").pack(side="left", padx=10, pady=8)

        # Records list
        self.list_frame = ctk.CTkScrollableFrame(self, fg_color=BG, corner_radius=0)
        self.list_frame.pack(fill="both", expand=True, padx=30, pady=(0, 24))

        self.count_lbl = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12),
                                       text_color=SUBTEXT)
        self.count_lbl.pack(anchor="w", padx=30, pady=(0, 8))

    def refresh(self):
        records = PayrollService.get_all()

        for w in self.list_frame.winfo_children():
            w.destroy()

        for pr in records:
            self._add_row(pr)

        self.count_lbl.configure(text=f"Showing {len(records)} payroll record(s)")

    def _add_row(self, pr: dict):
        row = ctk.CTkFrame(self.list_frame, fg_color=BG_CARD, corner_radius=8,
                           border_width=1, border_color="#2A2A3E")
        row.pack(fill="x", pady=3)
        row.bind("<Enter>", lambda _: row.configure(border_color=ACCENT))
        row.bind("<Leave>", lambda _: row.configure(border_color="#2A2A3E"))

        for text, w in [
            (pr["emp_name"],                         200),
            (f"{pr['month_name']} {pr['year']}",     120),
            (format_currency(pr["base_salary"]),     120),
            (format_currency(pr["allowances"]),      110),
            (format_currency(pr["deductions"]),      110),
        ]:
            ctk.CTkLabel(row, text=text, width=w, font=ctk.CTkFont(size=12),
                         text_color=TEXT, anchor="w").pack(side="left", padx=10, pady=10)

        ctk.CTkLabel(
            row, text=pr["fmt_net"], width=120,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=SUCCESS, anchor="w",
        ).pack(side="left", padx=10, pady=10)

        ctk.CTkButton(
            row, text="📄 View", width=80, height=30, corner_radius=6,
            fg_color=BG_CARD, hover_color=ACCENT,
            text_color=TEXT, font=ctk.CTkFont(size=11),
            command=lambda p=pr: self._view_payslip(p),
        ).pack(side="right", padx=10, pady=8)

    def _generate(self):
        emp_key = self.emp_var.get()
        emp_id  = self._emp_map.get(emp_key)
        if not emp_id:
            messagebox.showerror("Error", "Please select an employee.")
            return

        try:
            month = int(self.month_var.get())
            year  = int(self.year_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid month or year.")
            return

        ok, result = PayrollService.generate(emp_id, month, year)
        if ok:
            self.refresh()
            PayslipPreview(self, result)
        else:
            messagebox.showerror("Error", result)

    def _view_payslip(self, pr: dict):
        """Re-generate (or fetch) payslip for preview."""
        ok, result = PayrollService.generate(
            pr["employee_id"], pr["month"], pr["year"]
        )
        if ok:
            PayslipPreview(self, result)
        else:
            messagebox.showerror("Error", result)
