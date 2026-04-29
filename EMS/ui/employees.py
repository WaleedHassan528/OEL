"""
Employee CRUD UI — searchable table + card-based form.
"""
import customtkinter as ctk
from tkinter import messagebox
from services.employee_service import EmployeeService
from services.department_service import DepartmentService
from services.auth_service import AuthService
from utils.helpers import format_currency, format_date, badge_color

BG      = "#121212"
BG_CARD = "#1E1E2E"
ACCENT  = "#007BFF"
SUCCESS = "#00C853"
DANGER  = "#F44336"
TEXT    = "#FFFFFF"
SUBTEXT = "#9E9E9E"
INPUT_BG = "#0D0D1A"


class EmployeeForm(ctk.CTkToplevel):
    """Modal form for creating/editing an employee."""

    def __init__(self, master, on_save, employee: dict | None = None):
        super().__init__(master)
        self.on_save    = on_save
        self.employee   = employee
        self.is_edit    = employee is not None

        self.title("Edit Employee" if self.is_edit else "Add Employee")
        self.geometry("560x640")
        self.resizable(False, False)
        self.configure(fg_color=BG)
        self.grab_set()

        self._build()

    def _build(self):
        # Header
        hdr = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=0)
        hdr.pack(fill="x")
        ctk.CTkLabel(
            hdr,
            text="✏️  Edit Employee" if self.is_edit else "➕  Add Employee",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEXT,
        ).pack(padx=24, pady=16, anchor="w")

        # Scrollable content
        scroll = ctk.CTkScrollableFrame(self, fg_color=BG, corner_radius=0)
        scroll.pack(fill="both", expand=True, padx=0, pady=0)

        form = ctk.CTkFrame(scroll, fg_color="transparent")
        form.pack(fill="x", padx=24, pady=16)

        e = self.employee or {}

        self.fields = {}

        def row(label, key, placeholder="", default="", width=500):
            ctk.CTkLabel(form, text=label, font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=SUBTEXT).pack(anchor="w", pady=(8, 2))
            entry = ctk.CTkEntry(
                form, placeholder_text=placeholder,
                height=40, corner_radius=8,
                fg_color=INPUT_BG, border_color="#2A2A4A",
                text_color=TEXT, placeholder_text_color="#444466",
                font=ctk.CTkFont(size=13),
            )
            entry.pack(fill="x")
            entry.insert(0, str(e.get(key, default)))
            self.fields[key] = entry

        row("First Name *", "first_name",   "John")
        row("Last Name *",  "last_name",    "Doe")
        row("Email *",      "email",        "john@company.com")
        row("Phone",        "phone",        "+1-555-0100")
        row("Position",     "position",     "Software Engineer")
        row("Salary *",     "salary",       "60000")
        row("Employee Code","emp_code",     "EMP010 (auto if blank)")
        row("Hire Date",    "hire_date",    "YYYY-MM-DD")

        # Department dropdown
        ctk.CTkLabel(form, text="Department", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=SUBTEXT).pack(anchor="w", pady=(8, 2))
        depts = DepartmentService.get_all()
        dept_names = ["— None —"] + [d["name"] for d in depts]
        self._dept_map = {d["name"]: d["id"] for d in depts}

        current_dept = e.get("department_name", "— None —")
        self.dept_var = ctk.StringVar(value=current_dept if current_dept in dept_names else "— None —")
        dept_menu = ctk.CTkOptionMenu(
            form, variable=self.dept_var, values=dept_names,
            fg_color=INPUT_BG, button_color=ACCENT,
            text_color=TEXT, dropdown_fg_color=BG_CARD,
            corner_radius=8, height=40,
        )
        dept_menu.pack(fill="x")

        # Status dropdown
        ctk.CTkLabel(form, text="Status", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=SUBTEXT).pack(anchor="w", pady=(8, 2))
        self.status_var = ctk.StringVar(value=e.get("status", "active"))
        status_menu = ctk.CTkOptionMenu(
            form, variable=self.status_var,
            values=["active", "inactive", "terminated"],
            fg_color=INPUT_BG, button_color=ACCENT,
            text_color=TEXT, dropdown_fg_color=BG_CARD,
            corner_radius=8, height=40,
        )
        status_menu.pack(fill="x")

        # Error label
        self.error_lbl = ctk.CTkLabel(form, text="", text_color=DANGER,
                                       font=ctk.CTkFont(size=12))
        self.error_lbl.pack(anchor="w", pady=(8, 0))

        # Buttons
        btn_row = ctk.CTkFrame(form, fg_color="transparent")
        btn_row.pack(fill="x", pady=(12, 0))

        ctk.CTkButton(
            btn_row, text="Cancel",
            fg_color="#2A2A4A", hover_color="#3A3A6A",
            text_color=TEXT, corner_radius=8, height=40,
            command=self.destroy,
        ).pack(side="left", expand=True, fill="x", padx=(0, 6))

        ctk.CTkButton(
            btn_row, text="Save Employee",
            fg_color=ACCENT, hover_color="#0056b3",
            text_color=TEXT, corner_radius=8, height=40,
            command=self._save,
        ).pack(side="left", expand=True, fill="x")

    def _save(self):
        data = {k: v.get() for k, v in self.fields.items()}
        dept_name = self.dept_var.get()
        data["department_id"] = self._dept_map.get(dept_name)
        data["status"]        = self.status_var.get()

        if self.is_edit:
            ok, msg = EmployeeService.update(self.employee["id"], data)
        else:
            ok, msg = EmployeeService.create(data)

        if ok:
            self.on_save()
            self.destroy()
        else:
            self.error_lbl.configure(text=f"⚠  {msg}")


class EmployeeRow(ctk.CTkFrame):
    """A single row in the employee table."""

    def __init__(self, master, emp: dict, on_edit, on_delete, **kwargs):
        super().__init__(master, fg_color=BG_CARD, corner_radius=10,
                         border_width=1, border_color="#2A2A3E", **kwargs)

        self.bind("<Enter>", lambda _: self.configure(border_color=ACCENT))
        self.bind("<Leave>", lambda _: self.configure(border_color="#2A2A3E"))

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=10)

        # Avatar circle with initials
        initials = (emp["first_name"][0] + emp["last_name"][0]).upper()
        av = ctk.CTkLabel(
            inner, text=initials,
            width=42, height=42,
            fg_color=ACCENT, corner_radius=21,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT,
        )
        av.pack(side="left", padx=(0, 12))

        # Info
        info = ctk.CTkFrame(inner, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True)

        name_row = ctk.CTkFrame(info, fg_color="transparent")
        name_row.pack(fill="x")

        ctk.CTkLabel(
            name_row,
            text=emp["full_name"],
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=TEXT,
        ).pack(side="left")

        ctk.CTkLabel(
            name_row,
            text=f"  {emp['emp_code']}",
            font=ctk.CTkFont(size=11),
            text_color=SUBTEXT,
        ).pack(side="left")

        # Status badge
        bc = badge_color(emp["status"])
        ctk.CTkLabel(
            name_row,
            text=f" {emp['status'].upper()} ",
            fg_color=bc,
            corner_radius=6,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=TEXT,
            width=70, height=20,
        ).pack(side="right")

        details = f"📧 {emp['email']}   |   🏢 {emp['department_name']}   |   💼 {emp['position']}   |   💰 {format_currency(emp['salary'])}"
        ctk.CTkLabel(
            info, text=details,
            font=ctk.CTkFont(size=11),
            text_color=SUBTEXT,
        ).pack(anchor="w")

        # Action buttons
        btn_frame = ctk.CTkFrame(inner, fg_color="transparent")
        btn_frame.pack(side="right")

        if AuthService.is_admin():
            ctk.CTkButton(
                btn_frame, text="✏️",
                width=36, height=36, corner_radius=8,
                fg_color="#1E3A5F", hover_color=ACCENT,
                text_color=TEXT,
                command=lambda: on_edit(emp),
            ).pack(side="left", padx=2)

            ctk.CTkButton(
                btn_frame, text="🗑",
                width=36, height=36, corner_radius=8,
                fg_color="#3E1E1E", hover_color=DANGER,
                text_color=TEXT,
                command=lambda: on_delete(emp),
            ).pack(side="left", padx=2)


class EmployeeView(ctk.CTkFrame):
    """Main employee management view."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=BG, corner_radius=0, **kwargs)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        # Header
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=30, pady=(24, 0))

        ctk.CTkLabel(
            hdr, text="👥  Employees",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=TEXT,
        ).pack(side="left")

        if AuthService.is_admin():
            ctk.CTkButton(
                hdr, text="+ Add Employee",
                fg_color=ACCENT, hover_color="#0056b3",
                corner_radius=10, height=38,
                font=ctk.CTkFont(size=13, weight="bold"),
                command=self._open_add_form,
            ).pack(side="right")

        # Search + filter bar
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=30, pady=(16, 4))

        self.search_entry = ctk.CTkEntry(
            bar, placeholder_text="🔍  Search by name, email or code…",
            height=40, corner_radius=10,
            fg_color=BG_CARD, border_color="#2A2A4A",
            text_color=TEXT, placeholder_text_color=SUBTEXT,
            font=ctk.CTkFont(size=13),
        )
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind("<KeyRelease>", lambda _: self.refresh())

        self.status_filter = ctk.CTkOptionMenu(
            bar, values=["All", "active", "inactive", "terminated"],
            fg_color=BG_CARD, button_color=ACCENT,
            text_color=TEXT, dropdown_fg_color=BG_CARD,
            corner_radius=8, height=40, width=130,
            command=lambda _: self.refresh(),
        )
        self.status_filter.pack(side="left", padx=(8, 0))

        # Employee list
        self.list_frame = ctk.CTkScrollableFrame(
            self, fg_color=BG, corner_radius=0
        )
        self.list_frame.pack(fill="both", expand=True, padx=30, pady=(8, 24))

        # Count label
        self.count_lbl = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=12), text_color=SUBTEXT
        )
        self.count_lbl.pack(anchor="w", padx=30, pady=(0, 8))

    def refresh(self):
        query  = self.search_entry.get().strip() if hasattr(self, 'search_entry') else ""
        status = self.status_filter.get() if hasattr(self, 'status_filter') else "All"

        if query:
            employees = EmployeeService.search(query)
        elif status != "All":
            employees = EmployeeService.get_all(status_filter=status)
        else:
            employees = EmployeeService.get_all()

        # Clear list
        for w in self.list_frame.winfo_children():
            w.destroy()

        for emp in employees:
            row = EmployeeRow(
                self.list_frame, emp,
                on_edit=self._open_edit_form,
                on_delete=self._confirm_delete,
            )
            row.pack(fill="x", pady=4)

        self.count_lbl.configure(text=f"Showing {len(employees)} employee(s)")

    def _open_add_form(self):
        EmployeeForm(self, on_save=self.refresh)

    def _open_edit_form(self, emp: dict):
        EmployeeForm(self, on_save=self.refresh, employee=emp)

    def _confirm_delete(self, emp: dict):
        if not AuthService.is_admin():
            return
        if messagebox.askyesno(
            "Confirm Delete",
            f"Terminate employee '{emp['full_name']}'?\n\nThis will mark them as terminated.",
        ):
            ok, msg = EmployeeService.delete(emp["id"])
            if ok:
                self.refresh()
            else:
                messagebox.showerror("Error", msg)
