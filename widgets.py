"""
widgets.py — Reusable custom CTk widgets
"""
import tkinter as tk
import customtkinter as ctk
from theme import *

# ── Card Frame ────────────────────────────────────────────────────────────────

class Card(ctk.CTkFrame):
    def __init__(self, master, **kw):
        super().__init__(master,
            fg_color=kw.pop("fg_color", BG_CARD),
            corner_radius=kw.pop("corner_radius", R_CARD),
            border_width=kw.pop("border_width", 1),
            border_color=kw.pop("border_color", BORDER),
            **kw)

# ── Section Title ─────────────────────────────────────────────────────────────

class SectionTitle(ctk.CTkLabel):
    def __init__(self, master, text, **kw):
        super().__init__(master, text=text,
            font=FONT_H2,
            text_color=TEXT_PRIMARY,
            **kw)

# ── Sub-title ─────────────────────────────────────────────────────────────────

class SubTitle(ctk.CTkLabel):
    def __init__(self, master, text, **kw):
        super().__init__(master, text=text,
            font=FONT_SMALL,
            text_color=TEXT_SECOND,
            **kw)

# ── Metric Card ───────────────────────────────────────────────────────────────

class MetricCard(ctk.CTkFrame):
    def __init__(self, master, icon, value, label, accent=BLUE, **kw):
        super().__init__(master,
            fg_color=BG_CARD, corner_radius=R_CARD,
            border_width=1, border_color=BORDER, **kw)
        # accent top bar via canvas
        bar = tk.Canvas(self, height=3, bg=accent,
                        highlightthickness=0, bd=0)
        bar.pack(fill="x", padx=0, pady=(0,0))
        ctk.CTkLabel(self, text=icon, font=("Segoe UI", 28),
                     text_color=accent).pack(anchor="w", padx=18, pady=(14,0))
        ctk.CTkLabel(self, text=str(value), font=("Segoe UI", 32, "bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=18, pady=(2,0))
        ctk.CTkLabel(self, text=label, font=FONT_SMALL,
                     text_color=TEXT_SECOND).pack(anchor="w", padx=18, pady=(0,14))

# ── Status Badge ──────────────────────────────────────────────────────────────

class Badge(ctk.CTkLabel):
    ICONS = {"present":"●","approved":"✓","pending":"◐",
             "late":"◑","absent":"✕","rejected":"✕","half_day":"◑",
             "paid":"✓","unpaid":"✕"}

    def __init__(self, master, status: str, **kw):
        status = status.lower()
        fg, bg = STATUS_COLORS.get(status, (TEXT_SECOND, BG_CARD2))
        icon   = self.ICONS.get(status, "•")
        super().__init__(master,
            text=f" {icon}  {status.replace('_',' ').title()} ",
            font=FONT_TINY,
            text_color=fg,
            fg_color=bg,
            corner_radius=R_BADGE,
            **kw)

# ── Avatar Canvas ─────────────────────────────────────────────────────────────

class AvatarLabel(tk.Canvas):
    def __init__(self, master, name: str, color: str, size=48, **kw):
        super().__init__(master, width=size, height=size,
                         bg=BG_CARD, highlightthickness=0, **kw)
        r = size // 2
        self.create_oval(0, 0, size, size, fill=color, outline="")
        initials = "".join(p[0].upper() for p in name.split()[:2])
        font_size = max(10, size // 3)
        self.create_text(r, r, text=initials,
                         fill="white", font=("Segoe UI", font_size, "bold"))

# ── Styled Button ─────────────────────────────────────────────────────────────

class PrimaryButton(ctk.CTkButton):
    def __init__(self, master, **kw):
        kw.setdefault("fg_color", BLUE)
        kw.setdefault("hover_color", BLUE_HOVER)
        kw.setdefault("text_color", "white")
        kw.setdefault("corner_radius", R_BUTTON)
        kw.setdefault("font", FONT_BODY)
        kw.setdefault("height", 36)
        super().__init__(master, **kw)

class DangerButton(ctk.CTkButton):
    def __init__(self, master, **kw):
        kw.setdefault("fg_color", RED)
        kw.setdefault("hover_color", "#CC2233")
        kw.setdefault("text_color", "white")
        kw.setdefault("corner_radius", R_BUTTON)
        kw.setdefault("font", FONT_BODY)
        kw.setdefault("height", 36)
        super().__init__(master, **kw)

class GhostButton(ctk.CTkButton):
    def __init__(self, master, **kw):
        kw.setdefault("fg_color", BG_CARD2)
        kw.setdefault("hover_color", BG_HOVER)
        kw.setdefault("text_color", TEXT_SECOND)
        kw.setdefault("corner_radius", R_BUTTON)
        kw.setdefault("border_width", 1)
        kw.setdefault("border_color", BORDER)
        kw.setdefault("font", FONT_BODY)
        kw.setdefault("height", 36)
        super().__init__(master, **kw)

# ── Input Row helper ──────────────────────────────────────────────────────────

def labeled_entry(master, label, row, col=0, width=240, default="", padx=8, pady=5):
    ctk.CTkLabel(master, text=label, font=FONT_SMALL,
                 text_color=TEXT_SECOND).grid(row=row, column=col*2,
                 sticky="w", padx=(padx,4), pady=pady)
    var = ctk.StringVar(value=default)
    e = ctk.CTkEntry(master, textvariable=var, width=width,
                     fg_color=BG_INPUT, border_color=BORDER,
                     text_color=TEXT_PRIMARY, font=FONT_BODY,
                     corner_radius=R_INPUT)
    e.grid(row=row, column=col*2+1, sticky="ew", padx=(0,padx), pady=pady)
    return var

def labeled_combo(master, label, values, row, col=0, width=240, padx=8, pady=5):
    ctk.CTkLabel(master, text=label, font=FONT_SMALL,
                 text_color=TEXT_SECOND).grid(row=row, column=col*2,
                 sticky="w", padx=(padx,4), pady=pady)
    var = ctk.StringVar(value=values[0] if values else "")
    c = ctk.CTkComboBox(master, values=values, variable=var, width=width,
                        fg_color=BG_INPUT, border_color=BORDER,
                        text_color=TEXT_PRIMARY, font=FONT_BODY,
                        button_color=BLUE, button_hover_color=BLUE_HOVER,
                        dropdown_fg_color=BG_CARD2, corner_radius=R_INPUT)
    c.grid(row=row, column=col*2+1, sticky="ew", padx=(0,padx), pady=pady)
    return var

# ── Scrollable table ──────────────────────────────────────────────────────────

class TableFrame(ctk.CTkScrollableFrame):
    HDR_BG  = "#16162A"
    ROW_BG  = BG_CARD
    ROW_ALT = BG_CARD2

    def __init__(self, master, columns: list[tuple], **kw):
        """columns = [(header_text, width), ...]"""
        kw.setdefault("fg_color", BG_CARD)
        kw.setdefault("corner_radius", R_CARD)
        super().__init__(master, **kw)
        self.columns = columns
        self._draw_header()

    def _draw_header(self):
        hdr = ctk.CTkFrame(self, fg_color=self.HDR_BG, corner_radius=0, height=34)
        hdr.pack(fill="x", padx=0, pady=(0,1))
        for i, (txt, w) in enumerate(self.columns):
            ctk.CTkLabel(hdr, text=txt.upper(), font=("Segoe UI",10,"bold"),
                         text_color=TEXT_SECOND, width=w,
                         anchor="w").pack(side="left", padx=(12 if i==0 else 6, 0))

    def populate(self, rows: list[list], badge_cols: dict = None):
        """rows: list of cell value lists. badge_cols: {col_idx: status_str}"""
        for w in self.winfo_children()[1:]:   # keep header
            w.destroy()
        for ri, row in enumerate(rows):
            bg = self.ROW_BG if ri % 2 == 0 else self.ROW_ALT
            rframe = ctk.CTkFrame(self, fg_color=bg, corner_radius=0, height=38)
            rframe.pack(fill="x", padx=0, pady=0)
            for ci, (cell, (_, w)) in enumerate(zip(row, self.columns)):
                if badge_cols and ci in badge_cols:
                    badge_status = str(cell).lower()
                    Badge(rframe, badge_status, width=w).pack(
                        side="left", padx=(12 if ci==0 else 6, 0), pady=4)
                else:
                    ctk.CTkLabel(rframe, text=str(cell), font=FONT_SMALL,
                                 text_color=TEXT_PRIMARY, width=w,
                                 anchor="w").pack(
                        side="left", padx=(12 if ci==0 else 6, 0))

# ── Sidebar nav button ─────────────────────────────────────────────────────────

class NavButton(ctk.CTkButton):
    def __init__(self, master, icon, label, command, **kw):
        self._active = False
        super().__init__(master,
            text=f"  {icon}  {label}",
            anchor="w",
            fg_color="transparent",
            hover_color=BG_HOVER,
            text_color=TEXT_SECOND,
            corner_radius=10,
            font=("Segoe UI", 13),
            height=42,
            command=command,
            **kw)

    def set_active(self, active: bool):
        self._active = active
        if active:
            self.configure(fg_color=BG_SELECTED, text_color=BLUE_TEXT,
                           border_width=1, border_color=BLUE_DIM)
        else:
            self.configure(fg_color="transparent", text_color=TEXT_SECOND,
                           border_width=0)

# ── Star rating widget ────────────────────────────────────────────────────────

class StarRating(ctk.CTkFrame):
    def __init__(self, master, value=3, max_stars=5, size=22,
                 on_change=None, readonly=False, **kw):
        kw.setdefault("fg_color", "transparent")
        super().__init__(master, **kw)
        self.value = value
        self._stars = []
        self._cb    = on_change
        for i in range(1, max_stars + 1):
            lbl = ctk.CTkLabel(self, text="★", font=("Segoe UI", size),
                               cursor="hand2" if not readonly else "arrow")
            lbl.pack(side="left", padx=1)
            if not readonly:
                lbl.bind("<Button-1>", lambda e, v=i: self._click(v))
                lbl.bind("<Enter>", lambda e, v=i: self._hover(v))
                lbl.bind("<Leave>", lambda e: self._render(self.value))
            self._stars.append(lbl)
        self._render(value)

    def _render(self, upto):
        for i, lbl in enumerate(self._stars):
            lbl.configure(text_color=ORANGE_TEXT if i < upto else TEXT_MUTED)

    def _hover(self, v):  self._render(v)

    def _click(self, v):
        self.value = v
        self._render(v)
        if self._cb: self._cb(v)

    def get(self): return self.value
