"""
Attendance management UI — list view with status badges, mark attendance form.
"""
import customtkinter as ctk
from tkinter import messagebox
from datetime import date
from services.attendance_service import AttendanceService
from services.employee_service import EmployeeService
from services.auth_service import AuthService
from utils.helpers import badge_color, format_date

BG      = "#121212"
BG_CARD = "#1E1E2E"
ACCENT  = "#007BFF"
SUCCESS = "#00C853"
WARNING = "#FFA000"
DANGER  = "#F44336"
TEXT    = "#FFFFFF"
SUBTEXT = "#9E9E9E"
INPUT_BG = "#0D0D1A"


class MarkAttendanceForm(ctk.CTkToplevel):
    """Modal to mark or edit an attendance record."""

    def __init__(self, master, on_save, record: dict | None = None):
        super().__init__(master)
        self.on_save = on_save
        self.record  = record
        self.title("Mark Attendance")
        self.geometry("420x520")
        self.resizable(False, False)
        self.configure(fg_color=BG)
        self.grab_set()
        self._build()

    def _build(self):
        ctk.CTkLabel(
            self, text="📅  Mark Attendance",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEXT,
        ).pack(padx=24, pady=(20, 16), anchor="w")

        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="x", padx=24)

        def field(label, placeholder, default=""):
            ctk.CTkLabel(form, text=label, font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=SUBTEXT).pack(anchor="w", pady=(8, 2))
            e = ctk.CTkEntry(
                form, placeholder_text=placeholder, height=40, corner_radius=8,
                fg_color=INPUT_BG, border_color="#2A2A4A",
                text_color=TEXT, placeholder_text_color="#444466",
            )
            e.pack(fill="x")
            e.insert(0, default)
            return e

        # Employee selection
        ctk.CTkLabel(form, text="Employee *", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=SUBTEXT).pack(anchor="w", pady=(8, 2))
        emps = EmployeeService.get_all(status_filter="active")
        emp_names = [f"{e['emp_code']} — {e['full_name']}" for e in emps]
        self._emp_map = {f"{e['emp_code']} — {e['full_name']}": e['id'] for e in emps}

        default_emp = ""
        if self.record:
            for k, v in self._emp_map.items():
                if v == self.record["employee_id"]:
                    default_emp = k
                    break

        self.emp_var = ctk.StringVar(value=default_emp or (emp_names[0] if emp_names else ""))
        ctk.CTkOptionMenu(
            form, variable=self.emp_var, values=emp_names,
            fg_color=INPUT_BG, button_color=ACCENT,
            text_color=TEXT, dropdown_fg_color=BG_CARD,
            corner_radius=8, height=40,
        ).pack(fill="x")

        r = self.record or {}
        self.date_e     = field("Date (YYYY-MM-DD) *", "2024-01-15", r.get("date", str(date.today())))
        self.checkin_e  = field("Check In (HH:MM)",    "09:00",      r.get("check_in", "09:00"))
        self.checkout_e = field("Check Out (HH:MM)",   "18:00",      r.get("check_out", "18:00"))

        ctk.CTkLabel(form, text="Status *", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=SUBTEXT).pack(anchor="w", pady=(8, 2))
        self.status_var = ctk.StringVar(value=r.get("status", "present"))
        ctk.CTkOptionMenu(
            form, variable=self.status_var,
            values=["present", "absent", "late", "half_day"],
            fg_color=INPUT_BG, button_color=ACCENT,
            text_color=TEXT, dropdown_fg_color=BG_CARD,
            corner_radius=8, height=40,
        ).pack(fill="x")

        self.err_lbl = ctk.CTkLabel(form, text="", text_color=DANGER,
                                     font=ctk.CTkFont(size=12))
        self.err_lbl.pack(anchor="w", pady=(8, 0))

        btn_row = ctk.CTkFrame(form, fg_color="transparent")
        btn_row.pack(fill="x", pady=(12, 0))

        ctk.CTkButton(btn_row, text="Cancel", fg_color="#2A2A4A", hover_color="#3A3A6A",
                      text_color=TEXT, corner_radius=8, height=40,
                      command=self.destroy).pack(side="left", expand=True, fill="x", padx=(0, 6))

        ctk.CTkButton(btn_row, text="Save", fg_color=ACCENT, hover_color="#0056b3",
                      text_color=TEXT, corner_radius=8, height=40,
                      command=self._save).pack(side="left", expand=True, fill="x")

    def _save(self):
        emp_key = self.emp_var.get()
        emp_id  = self._emp_map.get(emp_key)
        if not emp_id:
            self.err_lbl.configure(text="⚠  Please select an employee.")
            return

        ok, msg = AttendanceService.mark(
            emp_id=emp_id,
            att_date=self.date_e.get(),
            check_in=self.checkin_e.get(),
            check_out=self.checkout_e.get(),
            status=self.status_var.get(),
        )
        if ok:
            self.on_save()
            self.destroy()
        else:
            self.err_lbl.configure(text=f"⚠  {msg}")


def _status_badge(parent, status: str) -> ctk.CTkLabel:
    color = badge_color(status)
    return ctk.CTkLabel(
        parent,
        text=f" {status.upper().replace('_', ' ')} ",
        fg_color=color, corner_radius=6,
        font=ctk.CTkFont(size=10, weight="bold"),
        text_color=TEXT, width=80, height=22,
    )


class AttendanceView(ctk.CTkFrame):
    """Attendance list view with mark/edit controls."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=BG, corner_radius=0, **kwargs)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        # Header
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=30, pady=(24, 0))

        ctk.CTkLabel(
            hdr, text="📅  Attendance",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=TEXT,
        ).pack(side="left")

        if AuthService.is_admin():
            ctk.CTkButton(
                hdr, text="+ Mark Attendance",
                fg_color=ACCENT, hover_color="#0056b3",
                corner_radius=10, height=38,
                font=ctk.CTkFont(size=13, weight="bold"),
                command=lambda: MarkAttendanceForm(self, on_save=self.refresh),
            ).pack(side="right")

        # Filter bar
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=30, pady=(16, 4))

        ctk.CTkLabel(bar, text="Filter by status:", text_color=SUBTEXT,
                     font=ctk.CTkFont(size=12)).pack(side="left")

        self.status_filter = ctk.CTkOptionMenu(
            bar, values=["All", "present", "absent", "late", "half_day"],
            fg_color=BG_CARD, button_color=ACCENT,
            text_color=TEXT, dropdown_fg_color=BG_CARD,
            corner_radius=8, height=38, width=140,
            command=lambda _: self.refresh(),
        )
        self.status_filter.pack(side="left", padx=(8, 0))

        ctk.CTkButton(
            bar, text="🔄 Refresh",
            fg_color=BG_CARD, hover_color="#2A2A4A",
            text_color=TEXT, corner_radius=8, height=38, width=100,
            command=self.refresh,
        ).pack(side="right")

        # Column headers
        cols = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=0)
        cols.pack(fill="x", padx=30, pady=(8, 2))

        headers = [("Employee", 220), ("Date", 110), ("Check In", 90),
                   ("Check Out", 90), ("Status", 100), ("", 80)]
        for h_text, w in headers:
            ctk.CTkLabel(
                cols, text=h_text,
                width=w,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=SUBTEXT, anchor="w",
            ).pack(side="left", padx=10, pady=8)

        # Records list
        self.list_frame = ctk.CTkScrollableFrame(
            self, fg_color=BG, corner_radius=0
        )
        self.list_frame.pack(fill="both", expand=True, padx=30, pady=(0, 24))

        self.count_lbl = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12),
                                       text_color=SUBTEXT)
        self.count_lbl.pack(anchor="w", padx=30, pady=(0, 8))

    def refresh(self):
        records = AttendanceService.get_all(limit=200)
        status_f = self.status_filter.get() if hasattr(self, 'status_filter') else "All"
        if status_f != "All":
            records = [r for r in records if r["status"] == status_f]

        for w in self.list_frame.winfo_children():
            w.destroy()

        for rec in records:
            self._add_row(rec)

        self.count_lbl.configure(text=f"Showing {len(records)} record(s)")

    def _add_row(self, rec: dict):
        row = ctk.CTkFrame(self.list_frame, fg_color=BG_CARD, corner_radius=8,
                           border_width=1, border_color="#2A2A3E")
        row.pack(fill="x", pady=3)
        row.bind("<Enter>", lambda _: row.configure(border_color=ACCENT))
        row.bind("<Leave>", lambda _: row.configure(border_color="#2A2A3E"))

        widths = [220, 110, 90, 90, 100, 80]
        values = [
            rec["emp_name"], format_date(rec["date"]),
            rec["check_in"] or "—", rec["check_out"] or "—",
            None,  # badge
            None,  # delete btn
        ]

        for i, (val, w) in enumerate(zip(values, widths)):
            if i == 4:  # Status badge
                _status_badge(row, rec["status"]).pack(side="left", padx=10, pady=8)
            elif i == 5 and AuthService.is_admin():
                ctk.CTkButton(
                    row, text="🗑", width=36, height=30, corner_radius=6,
                    fg_color="#3E1E1E", hover_color=DANGER, text_color=TEXT,
                    command=lambda rid=rec["id"]: self._delete(rid),
                ).pack(side="left", padx=6, pady=8)
            else:
                ctk.CTkLabel(
                    row, text=str(val), width=w,
                    font=ctk.CTkFont(size=12), text_color=TEXT, anchor="w",
                ).pack(side="left", padx=10, pady=10)

    def _delete(self, record_id: int):
        if messagebox.askyesno("Confirm", "Delete this attendance record?"):
            ok, msg = AttendanceService.delete(record_id)
            if ok:
                self.refresh()
            else:
                messagebox.showerror("Error", msg)
