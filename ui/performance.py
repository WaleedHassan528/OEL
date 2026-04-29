"""
Performance review UI — star rating widget + comments.
"""
import customtkinter as ctk
from tkinter import messagebox
from datetime import date
from services.performance_service import PerformanceService
from services.employee_service import EmployeeService
from services.auth_service import AuthService
from utils.helpers import format_date

BG       = "#121212"
BG_CARD  = "#1E1E2E"
ACCENT   = "#007BFF"
SUCCESS  = "#00C853"
WARNING  = "#FFA000"
DANGER   = "#F44336"
GOLD     = "#FFD700"
TEXT     = "#FFFFFF"
SUBTEXT  = "#9E9E9E"
INPUT_BG = "#0D0D1A"


class StarRating(ctk.CTkFrame):
    """Interactive 5-star rating widget."""

    def __init__(self, master, initial: int = 3, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._rating = initial
        self._stars  = []
        self._build()

    def _build(self):
        for i in range(1, 6):
            star = ctk.CTkLabel(
                self,
                text="★",
                font=ctk.CTkFont(size=28),
                text_color=GOLD if i <= self._rating else "#333333",
                cursor="hand2",
            )
            star.pack(side="left", padx=2)
            star.bind("<Button-1>", lambda e, v=i: self._set(v))
            star.bind("<Enter>",    lambda e, v=i: self._hover(v))
            star.bind("<Leave>",    lambda e: self._render())
            self._stars.append(star)

    def _set(self, value: int):
        self._rating = value
        self._render()

    def _hover(self, value: int):
        for i, s in enumerate(self._stars):
            s.configure(text_color=GOLD if (i + 1) <= value else "#333333")

    def _render(self):
        for i, s in enumerate(self._stars):
            s.configure(text_color=GOLD if (i + 1) <= self._rating else "#333333")

    @property
    def rating(self) -> int:
        return self._rating


class ReviewForm(ctk.CTkToplevel):
    """Modal to add/edit a performance review."""

    def __init__(self, master, on_save, review: dict | None = None):
        super().__init__(master)
        self.on_save = on_save
        self.review  = review
        self.title("Add Review" if not review else "Edit Review")
        self.geometry("440x500")
        self.resizable(False, False)
        self.configure(fg_color=BG)
        self.grab_set()
        self._build()

    def _build(self):
        ctk.CTkLabel(
            self,
            text="⭐  Performance Review",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=TEXT,
        ).pack(padx=24, pady=(20, 16), anchor="w")

        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="x", padx=24)

        r = self.review or {}

        # Employee selector
        ctk.CTkLabel(form, text="Employee *", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=SUBTEXT).pack(anchor="w", pady=(8, 2))

        emps = EmployeeService.get_all(status_filter="active")
        emp_names = [f"{e['emp_code']} — {e['full_name']}" for e in emps]
        self._emp_map = {f"{e['emp_code']} — {e['full_name']}": e['id'] for e in emps}

        default_emp = ""
        if r.get("employee_id"):
            for k, v in self._emp_map.items():
                if v == r["employee_id"]:
                    default_emp = k
                    break

        self.emp_var = ctk.StringVar(value=default_emp or (emp_names[0] if emp_names else ""))
        emp_menu = ctk.CTkOptionMenu(
            form, variable=self.emp_var, values=emp_names,
            fg_color=INPUT_BG, button_color=ACCENT,
            text_color=TEXT, dropdown_fg_color=BG_CARD,
            corner_radius=8, height=40,
        )
        emp_menu.pack(fill="x")
        if r.get("employee_id"):
            emp_menu.configure(state="disabled")

        # Rating
        ctk.CTkLabel(form, text="Rating *", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=SUBTEXT).pack(anchor="w", pady=(16, 6))

        self.star_widget = StarRating(form, initial=r.get("rating", 3))
        self.star_widget.pack(anchor="w")

        # Rating labels
        label_row = ctk.CTkFrame(form, fg_color="transparent")
        label_row.pack(anchor="w", pady=(2, 0))
        for txt in ["Poor", "Fair", "Good", "V.Good", "Excellent"]:
            ctk.CTkLabel(label_row, text=txt, font=ctk.CTkFont(size=9),
                         text_color=SUBTEXT, width=38).pack(side="left")

        # Review date
        ctk.CTkLabel(form, text="Review Date", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=SUBTEXT).pack(anchor="w", pady=(14, 2))
        self.date_e = ctk.CTkEntry(
            form, placeholder_text="YYYY-MM-DD", height=40, corner_radius=8,
            fg_color=INPUT_BG, border_color="#2A2A4A",
            text_color=TEXT, placeholder_text_color="#444466",
        )
        self.date_e.pack(fill="x")
        self.date_e.insert(0, r.get("review_date", str(date.today())))

        # Comments
        ctk.CTkLabel(form, text="Comments", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=SUBTEXT).pack(anchor="w", pady=(14, 2))
        self.comments_e = ctk.CTkTextbox(
            form, height=80, corner_radius=8,
            fg_color=INPUT_BG, border_color="#2A2A4A",
            text_color=TEXT,
        )
        self.comments_e.pack(fill="x")
        if r.get("comments"):
            self.comments_e.insert("1.0", r["comments"])

        self.err_lbl = ctk.CTkLabel(form, text="", text_color=DANGER,
                                     font=ctk.CTkFont(size=12))
        self.err_lbl.pack(anchor="w", pady=(8, 0))

        btn_row = ctk.CTkFrame(form, fg_color="transparent")
        btn_row.pack(fill="x", pady=(12, 0))

        ctk.CTkButton(btn_row, text="Cancel", fg_color="#2A2A4A", hover_color="#3A3A6A",
                      text_color=TEXT, corner_radius=8, height=40,
                      command=self.destroy).pack(side="left", expand=True, fill="x", padx=(0, 6))

        ctk.CTkButton(btn_row, text="Submit Review", fg_color=ACCENT, hover_color="#0056b3",
                      text_color=TEXT, corner_radius=8, height=40,
                      command=self._save).pack(side="left", expand=True, fill="x")

    def _save(self):
        comments = self.comments_e.get("1.0", "end-1c")

        if self.review:
            ok, msg = PerformanceService.update_review(
                self.review["id"],
                rating=self.star_widget.rating,
                comments=comments,
            )
        else:
            emp_id = self._emp_map.get(self.emp_var.get())
            if not emp_id:
                self.err_lbl.configure(text="⚠  Select an employee.")
                return
            current_user = AuthService.get_current_user()
            ok, msg = PerformanceService.add_review(
                emp_id=emp_id,
                reviewer_id=current_user.employee_id if current_user else None,
                rating=self.star_widget.rating,
                comments=comments,
                review_date=self.date_e.get(),
            )

        if ok:
            self.on_save()
            self.destroy()
        else:
            self.err_lbl.configure(text=f"⚠  {msg}")


def _stars_display(rating: int) -> str:
    return "★" * rating + "☆" * (5 - rating)


class PerformanceView(ctk.CTkFrame):
    """Performance review management view."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color=BG, corner_radius=0, **kwargs)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=30, pady=(24, 0))

        ctk.CTkLabel(hdr, text="⭐  Performance Reviews",
                     font=ctk.CTkFont(size=26, weight="bold"),
                     text_color=TEXT).pack(side="left")

        if AuthService.is_admin():
            ctk.CTkButton(
                hdr, text="+ Add Review",
                fg_color=ACCENT, hover_color="#0056b3",
                corner_radius=10, height=38,
                font=ctk.CTkFont(size=13, weight="bold"),
                command=lambda: ReviewForm(self, on_save=self.refresh),
            ).pack(side="right")

        self.list_frame = ctk.CTkScrollableFrame(self, fg_color=BG, corner_radius=0)
        self.list_frame.pack(fill="both", expand=True, padx=30, pady=(16, 24))

        self.count_lbl = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12),
                                       text_color=SUBTEXT)
        self.count_lbl.pack(anchor="w", padx=30, pady=(0, 8))

    def refresh(self):
        current_user = AuthService.get_current_user()
        if AuthService.is_admin():
            reviews = PerformanceService.get_all()
        else:
            emp_id  = current_user.employee_id if current_user else None
            reviews = PerformanceService.get_for_employee(emp_id) if emp_id else []

        for w in self.list_frame.winfo_children():
            w.destroy()

        for rev in reviews:
            self._add_card(rev)

        self.count_lbl.configure(text=f"Showing {len(reviews)} review(s)")

    def _add_card(self, rev: dict):
        card = ctk.CTkFrame(self.list_frame, fg_color=BG_CARD, corner_radius=12,
                            border_width=1, border_color="#2A2A3E")
        card.pack(fill="x", pady=5)
        card.bind("<Enter>", lambda _: card.configure(border_color=ACCENT))
        card.bind("<Leave>", lambda _: card.configure(border_color="#2A2A3E"))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=12)

        # Left info
        left = ctk.CTkFrame(inner, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True)

        name_row = ctk.CTkFrame(left, fg_color="transparent")
        name_row.pack(fill="x")

        ctk.CTkLabel(name_row, text=rev["emp_name"],
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT).pack(side="left")

        # Star display
        stars_lbl = ctk.CTkLabel(
            name_row,
            text=f"  {_stars_display(rev['rating'])}  {rev['rating']}/5",
            font=ctk.CTkFont(size=14),
            text_color=GOLD,
        )
        stars_lbl.pack(side="left", padx=12)

        meta = f"Reviewed by: {rev['reviewer_name']}   |   {format_date(rev['review_date'])}"
        ctk.CTkLabel(left, text=meta, font=ctk.CTkFont(size=11),
                     text_color=SUBTEXT).pack(anchor="w", pady=(2, 0))

        if rev["comments"]:
            ctk.CTkLabel(left, text=f"💬  {rev['comments']}",
                         font=ctk.CTkFont(size=12), text_color="#BBBBBB",
                         wraplength=500, justify="left").pack(anchor="w", pady=(6, 0))

        # Right actions
        if AuthService.is_admin():
            right = ctk.CTkFrame(inner, fg_color="transparent")
            right.pack(side="right")

            ctk.CTkButton(
                right, text="✏️", width=36, height=36, corner_radius=8,
                fg_color="#1E3A5F", hover_color=ACCENT, text_color=TEXT,
                command=lambda r=rev: ReviewForm(self, on_save=self.refresh, review=r),
            ).pack(side="left", padx=2)

            ctk.CTkButton(
                right, text="🗑", width=36, height=36, corner_radius=8,
                fg_color="#3E1E1E", hover_color=DANGER, text_color=TEXT,
                command=lambda rid=rev["id"]: self._delete(rid),
            ).pack(side="left", padx=2)

    def _delete(self, review_id: int):
        if messagebox.askyesno("Confirm", "Delete this review?"):
            ok, msg = PerformanceService.delete_review(review_id)
            if ok:
                self.refresh()
            else:
                messagebox.showerror("Error", msg)
