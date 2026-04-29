"""
Leave management UI — apply, approve, reject with status badges.
"""
import customtkinter as ctk
from tkinter import messagebox
from datetime import date
from services.leave_service import LeaveService
from services.employee_service import EmployeeService
from services.auth_service import AuthService
from utils.helpers import badge_color, format_date

BG       = "#121212"
BG_CARD  = "#1E1E2E"
ACCENT   = "#007BFF"
SUCCESS  = "#00C853"
WARNING  = "#FFA000"
DANGER   = "#F44336"
TEXT     = "#FFFFFF"
SUBTEXT  = "#9E9E9E"
INPUT_BG = "#0D0D1A"

LEAVE_TYPES = ["annual", "sick", "maternity", "unpaid", "other"]


class ApplyLeaveForm(ctk.CTkToplevel):
    """Modal to apply for a new leave."""

    def __init__(self, master, on_save):
        super().__init__(master)
        self.on_save = on_save
        self.title("Apply for Leave")
        self.geometry("420x520")
        self.resizable(False, False)
        self.configure(fg_color=BG)
        self.grab_set()
        self._build()

    def _build(self):
        ctk.CTkLabel(
            self, text="📋  Apply for Leave",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEXT,
        ).pack(padx=24, pady=(20, 16), anchor="w")

        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="x", padx=24)

        # Employee selector (admin sees all, employee sees self)
        ctk.CTkLabel(form, text="Employee *", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=SUBTEXT).pack(anchor="w", pady=(8, 2))

        current_user = AuthService.get_current_user()
        if AuthService.is_admin():
            emps = EmployeeService.get_all(status_filter="active")
        else:
            if current_user and current_user.employee_id:
                emp_d = EmployeeService.get_by_id(current_user.employee_id)
                emps = [emp_d] if emp_d else []
            else:
                emps = []

        emp_names = [f"{e['emp_code']} — {e['full_name']}" for e in emps]
        self._emp_map = {f"{e['emp_code']} — {e['full_name']}": e['id'] for e in emps}

        self.emp_var = ctk.StringVar(value=emp_names[0] if emp_names else "")
        ctk.CTkOptionMenu(
            form, variable=self.emp_var, values=emp_names,
            fg_color=INPUT_BG, button_color=ACCENT,
            text_color=TEXT, dropdown_fg_color=BG_CARD,
            corner_radius=8, height=40,
        ).pack(fill="x")

        # Leave type
        ctk.CTkLabel(form, text="Leave Type *", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=SUBTEXT).pack(anchor="w", pady=(12, 2))
        self.type_var = ctk.StringVar(value="annual")
        ctk.CTkOptionMenu(
            form, variable=self.type_var, values=LEAVE_TYPES,
            fg_color=INPUT_BG, button_color=ACCENT,
            text_color=TEXT, dropdown_fg_color=BG_CARD,
            corner_radius=8, height=40,
        ).pack(fill="x")

        def date_field(label, default=""):
            ctk.CTkLabel(form, text=label, font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=SUBTEXT).pack(anchor="w", pady=(12, 2))
            e = ctk.CTkEntry(
                form, placeholder_text="YYYY-MM-DD", height=40, corner_radius=8,
                fg_color=INPUT_BG, border_color="#2A2A4A",
                text_color=TEXT, placeholder_text_color="#444466",
            )
            e.pack(fill="x")
            e.insert(0, default)
            return e

        today = str(date.today())
        self.start_e = date_field("Start Date *", today)
        self.end_e   = date_field("End Date *",   today)

        ctk.CTkLabel(form, text="Reason", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=SUBTEXT).pack(anchor="w", pady=(12, 2))
        self.reason_e = ctk.CTkTextbox(
            form, height=70, corner_radius=8,
            fg_color=INPUT_BG, border_color="#2A2A4A",
            text_color=TEXT,
        )
        self.reason_e.pack(fill="x")

        self.err_lbl = ctk.CTkLabel(form, text="", text_color=DANGER,
                                     font=ctk.CTkFont(size=12))
        self.err_lbl.pack(anchor="w", pady=(8, 0))

        btn_row = ctk.CTkFrame(form, fg_color="transparent")
        btn_row.pack(fill="x", pady=(12, 0))

        ctk.CTkButton(btn_row, text="Cancel", fg_color="#2A2A4A", hover_color="#3A3A6A",
                      text_color=TEXT, corner_radius=8, height=40,
                      command=self.destroy).pack(side="left", expand=True, fill="x", padx=(0, 6))

        ctk.CTkButton(btn_row, text="Submit Request", fg_color=ACCENT, hover_color="#0056b3",
                      text_color=TEXT, corner_radius=8, height=40,
                      command=self._save).pack(side="left", expand=True, fill="x")

    def _save(self):
        emp_id = self._emp_map.get(self.emp_var.get())
        if not emp_id:
            self.err_lbl.configure(text="⚠  Please select an employee.")
            return

        reason = self.reason_e.get("1.0", "end-1c")
        ok, msg = LeaveService.apply(
            emp_id=emp_id,
            leave_type=self.type_var.get(),
            start_date=self.start_e.get(),
            end_date=self.end_e.get(),
            reason=reason,
        )
        if ok:
            self.on_save()
            self.destroy()
        else:
            self.err_lbl.configure(text=f"⚠  {msg}")


def _badge(parent, status: str) -> ctk.CTkLabel:
    color = badge_color(status)
    return ctk.CTkLabel(
        parent,
        text=f"  {status.upper()}  ",
        fg_color=color, corner_radius=6,
        font=ctk.CTkFont(size=10, weight="bold"),
        text_color=TEXT, width=85, height=22,
    )


class LeaveView(ctk.CTkFrame):
    """Leave management view."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=BG, corner_radius=0, **kwargs)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        # Header
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=30, pady=(24, 0))

        ctk.CTkLabel(
            hdr, text="🌴  Leave Management",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=TEXT,
        ).pack(side="left")

        ctk.CTkButton(
            hdr, text="+ Apply Leave",
            fg_color=ACCENT, hover_color="#0056b3",
            corner_radius=10, height=38,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=lambda: ApplyLeaveForm(self, on_save=self.refresh),
        ).pack(side="right")

        # Filter
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=30, pady=(16, 4))

        ctk.CTkLabel(bar, text="Filter:", text_color=SUBTEXT,
                     font=ctk.CTkFont(size=12)).pack(side="left")

        self.filter_var = ctk.StringVar(value="All")
        ctk.CTkOptionMenu(
            bar, variable=self.filter_var,
            values=["All", "pending", "approved", "rejected"],
            fg_color=BG_CARD, button_color=ACCENT,
            text_color=TEXT, dropdown_fg_color=BG_CARD,
            corner_radius=8, height=36, width=140,
            command=lambda _: self.refresh(),
        ).pack(side="left", padx=(8, 0))

        # Column headers
        cols = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=0)
        cols.pack(fill="x", padx=30, pady=(8, 2))

        for h_text, w in [("Employee", 180), ("Type", 90), ("From", 100),
                           ("To", 100), ("Days", 50), ("Status", 90),
                           ("Reason", 200), ("", 120)]:
            ctk.CTkLabel(
                cols, text=h_text, width=w,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=SUBTEXT, anchor="w",
            ).pack(side="left", padx=10, pady=8)

        self.list_frame = ctk.CTkScrollableFrame(
            self, fg_color=BG, corner_radius=0
        )
        self.list_frame.pack(fill="both", expand=True, padx=30, pady=(0, 24))

        self.count_lbl = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12),
                                       text_color=SUBTEXT)
        self.count_lbl.pack(anchor="w", padx=30, pady=(0, 8))

    def refresh(self):
        filt = self.filter_var.get() if hasattr(self, 'filter_var') else "All"
        sf   = None if filt == "All" else filt

        current_user = AuthService.get_current_user()
        if AuthService.is_admin():
            leaves = LeaveService.get_all(status_filter=sf)
        else:
            emp_id = current_user.employee_id if current_user else None
            leaves = LeaveService.get_for_employee(emp_id) if emp_id else []
            if sf:
                leaves = [l for l in leaves if l["status"] == sf]

        for w in self.list_frame.winfo_children():
            w.destroy()

        for lv in leaves:
            self._add_row(lv)

        self.count_lbl.configure(text=f"Showing {len(leaves)} leave request(s)")

    def _add_row(self, lv: dict):
        row = ctk.CTkFrame(self.list_frame, fg_color=BG_CARD, corner_radius=8,
                           border_width=1, border_color="#2A2A3E")
        row.pack(fill="x", pady=3)
        row.bind("<Enter>", lambda _: row.configure(border_color=ACCENT))
        row.bind("<Leave>", lambda _: row.configure(border_color="#2A2A3E"))

        cells = [
            (lv["emp_name"],                   180),
            (lv["leave_type"].capitalize(),     90),
            (format_date(lv["start_date"]),     100),
            (format_date(lv["end_date"]),       100),
            (str(lv["duration"]),               50),
        ]
        for text, w in cells:
            ctk.CTkLabel(row, text=text, width=w, font=ctk.CTkFont(size=12),
                         text_color=TEXT, anchor="w").pack(side="left", padx=10, pady=10)

        _badge(row, lv["status"]).pack(side="left", padx=10, pady=10)

        reason_text = (lv["reason"][:28] + "…") if len(lv.get("reason", "")) > 28 else lv.get("reason", "—")
        ctk.CTkLabel(row, text=reason_text, width=200, font=ctk.CTkFont(size=11),
                     text_color=SUBTEXT, anchor="w").pack(side="left", padx=10, pady=10)

        # Action buttons
        if AuthService.is_admin() and lv["status"] == "pending":
            btn_frame = ctk.CTkFrame(row, fg_color="transparent")
            btn_frame.pack(side="right", padx=10)

            ctk.CTkButton(
                btn_frame, text="✅ Approve", width=80, height=28,
                fg_color="#1E4A2E", hover_color=SUCCESS,
                text_color=TEXT, corner_radius=6, font=ctk.CTkFont(size=11),
                command=lambda lid=lv["id"]: self._approve(lid),
            ).pack(side="left", padx=2)

            ctk.CTkButton(
                btn_frame, text="❌ Reject", width=70, height=28,
                fg_color="#3E1E1E", hover_color=DANGER,
                text_color=TEXT, corner_radius=6, font=ctk.CTkFont(size=11),
                command=lambda lid=lv["id"]: self._reject(lid),
            ).pack(side="left", padx=2)

    def _approve(self, leave_id: int):
        current_user = AuthService.get_current_user()
        approver_id  = current_user.employee_id if current_user else 1
        ok, msg = LeaveService.approve(leave_id, approver_id)
        if ok:
            self.refresh()
        else:
            messagebox.showerror("Error", msg)

    def _reject(self, leave_id: int):
        current_user = AuthService.get_current_user()
        approver_id  = current_user.employee_id if current_user else 1
        ok, msg = LeaveService.reject(leave_id, approver_id)
        if ok:
            self.refresh()
        else:
            messagebox.showerror("Error", msg)
