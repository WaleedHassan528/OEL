"""
Department hub — card-based layout showing departments and employee counts.
"""
import customtkinter as ctk
from tkinter import messagebox
from services.department_service import DepartmentService
from services.auth_service import AuthService

BG       = "#121212"
BG_CARD  = "#1E1E2E"
ACCENT   = "#007BFF"
SUCCESS  = "#00C853"
DANGER   = "#F44336"
TEXT     = "#FFFFFF"
SUBTEXT  = "#9E9E9E"
INPUT_BG = "#0D0D1A"

DEPT_COLORS = [ACCENT, "#9C27B0", SUCCESS, "#FF6D00", "#00BCD4",
               "#E91E63", "#FF9800", "#4CAF50"]


class DeptForm(ctk.CTkToplevel):
    """Modal form for adding/editing a department."""

    def __init__(self, master, on_save, dept: dict | None = None):
        super().__init__(master)
        self.on_save = on_save
        self.dept    = dept
        self.title("Edit Department" if dept else "Add Department")
        self.geometry("400x320")
        self.resizable(False, False)
        self.configure(fg_color=BG)
        self.grab_set()
        self._build()

    def _build(self):
        ctk.CTkLabel(
            self,
            text="🏢  Department",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEXT,
        ).pack(padx=24, pady=(20, 16), anchor="w")

        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="x", padx=24)

        d = self.dept or {}

        ctk.CTkLabel(form, text="Department Name *", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=SUBTEXT).pack(anchor="w", pady=(8, 2))
        self.name_e = ctk.CTkEntry(
            form, placeholder_text="Engineering", height=40, corner_radius=8,
            fg_color=INPUT_BG, border_color="#2A2A4A",
            text_color=TEXT, placeholder_text_color="#444466",
        )
        self.name_e.pack(fill="x")
        self.name_e.insert(0, d.get("name", ""))

        ctk.CTkLabel(form, text="Description", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=SUBTEXT).pack(anchor="w", pady=(14, 2))
        self.desc_e = ctk.CTkTextbox(
            form, height=80, corner_radius=8,
            fg_color=INPUT_BG, border_color="#2A2A4A",
            text_color=TEXT,
        )
        self.desc_e.pack(fill="x")
        if d.get("description"):
            self.desc_e.insert("1.0", d["description"])

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
        name = self.name_e.get()
        desc = self.desc_e.get("1.0", "end-1c")

        if self.dept:
            ok, msg = DepartmentService.update(self.dept["id"], name, desc)
        else:
            ok, msg = DepartmentService.create(name, desc)

        if ok:
            self.on_save()
            self.destroy()
        else:
            self.err_lbl.configure(text=f"⚠  {msg}")


class DeptCard(ctk.CTkFrame):
    """A department card widget."""

    def __init__(self, master, dept: dict, color: str,
                 on_edit, on_delete, **kwargs):
        super().__init__(
            master, fg_color=BG_CARD, corner_radius=15,
            border_width=2, border_color="#2A2A3E",
            width=220, height=170,
            **kwargs
        )
        self.grid_propagate(False)
        self.configure(cursor="hand2")

        # Hover effects
        self.bind("<Enter>", lambda _: self.configure(border_color=color))
        self.bind("<Leave>", lambda _: self.configure(border_color="#2A2A3E"))

        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(padx=16, pady=14, fill="both", expand=True)

        # Color accent bar
        bar = ctk.CTkFrame(inner, fg_color=color, corner_radius=4, height=4)
        bar.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            inner, text="🏢",
            font=ctk.CTkFont(size=30),
            text_color=color,
        ).pack(anchor="w")

        ctk.CTkLabel(
            inner, text=dept["name"],
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=TEXT,
        ).pack(anchor="w", pady=(4, 0))

        desc = (dept["description"][:40] + "…") if len(dept.get("description", "")) > 40 else dept.get("description", "")
        ctk.CTkLabel(
            inner, text=desc or "No description",
            font=ctk.CTkFont(size=10),
            text_color=SUBTEXT,
        ).pack(anchor="w")

        count_frame = ctk.CTkFrame(inner, fg_color="transparent")
        count_frame.pack(fill="x", pady=(8, 0))

        ctk.CTkLabel(
            count_frame,
            text=str(dept.get("employee_count", 0)),
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=color,
        ).pack(side="left")

        ctk.CTkLabel(
            count_frame, text=" employees",
            font=ctk.CTkFont(size=11),
            text_color=SUBTEXT,
        ).pack(side="left", pady=6)

        if AuthService.is_admin():
            btn_row = ctk.CTkFrame(count_frame, fg_color="transparent")
            btn_row.pack(side="right")

            ctk.CTkButton(
                btn_row, text="✏️", width=30, height=28, corner_radius=6,
                fg_color="#1E3A5F", hover_color=ACCENT, text_color=TEXT,
                command=lambda: on_edit(dept),
            ).pack(side="left", padx=1)

            ctk.CTkButton(
                btn_row, text="🗑", width=30, height=28, corner_radius=6,
                fg_color="#3E1E1E", hover_color=DANGER, text_color=TEXT,
                command=lambda: on_delete(dept),
            ).pack(side="left", padx=1)


class DepartmentView(ctk.CTkFrame):
    """Department hub view."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=BG, corner_radius=0, **kwargs)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=30, pady=(24, 0))

        ctk.CTkLabel(hdr, text="🏢  Department Hub",
                     font=ctk.CTkFont(size=26, weight="bold"),
                     text_color=TEXT).pack(side="left")

        if AuthService.is_admin():
            ctk.CTkButton(
                hdr, text="+ Add Department",
                fg_color=ACCENT, hover_color="#0056b3",
                corner_radius=10, height=38,
                font=ctk.CTkFont(size=13, weight="bold"),
                command=lambda: DeptForm(self, on_save=self.refresh),
            ).pack(side="right")

        self.grid_frame = ctk.CTkScrollableFrame(self, fg_color=BG, corner_radius=0)
        self.grid_frame.pack(fill="both", expand=True, padx=30, pady=(20, 24))

        self.count_lbl = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12),
                                       text_color=SUBTEXT)
        self.count_lbl.pack(anchor="w", padx=30, pady=(0, 8))

    def refresh(self):
        depts = DepartmentService.get_employee_counts()

        for w in self.grid_frame.winfo_children():
            w.destroy()

        # Arrange in a responsive grid (4 columns)
        cols = 4
        for i, dept in enumerate(depts):
            color = DEPT_COLORS[i % len(DEPT_COLORS)]
            card  = DeptCard(
                self.grid_frame, dept, color,
                on_edit=lambda d: DeptForm(self, on_save=self.refresh, dept=d),
                on_delete=self._confirm_delete,
            )
            card.grid(row=i // cols, column=i % cols, padx=8, pady=8, sticky="nsew")

        for c in range(cols):
            self.grid_frame.columnconfigure(c, weight=1)

        self.count_lbl.configure(text=f"{len(depts)} department(s)")

    def _confirm_delete(self, dept: dict):
        if messagebox.askyesno(
            "Confirm Delete",
            f"Delete department '{dept['name']}'?\n"
            "All employees must be reassigned first."
        ):
            ok, msg = DepartmentService.delete(dept["id"])
            if ok:
                self.refresh()
            else:
                messagebox.showerror("Cannot Delete", msg)
