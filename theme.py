"""
theme.py — Color palette and widget style constants
"""

# ── Palette ───────────────────────────────────────────────────────────────────
BG_APP        = "#0D0D14"
BG_SIDEBAR    = "#111119"
BG_CARD       = "#181825"
BG_CARD2      = "#1E1E2E"
BG_INPUT      = "#1A1A28"
BG_HOVER      = "#222235"
BG_SELECTED   = "#1C2E4A"

BLUE          = "#007BFF"
BLUE_HOVER    = "#0066DD"
BLUE_DIM      = "#0D2A4A"
BLUE_TEXT     = "#60A5FA"

GREEN         = "#00C853"
GREEN_DIM     = "#0A2E1A"
GREEN_TEXT    = "#4ADE80"

RED           = "#FF4757"
RED_DIM       = "#2E0D12"
RED_TEXT      = "#F87171"

ORANGE        = "#FF8C00"
ORANGE_DIM    = "#2E1A00"
ORANGE_TEXT   = "#FBB040"

PURPLE        = "#9B59B6"
PURPLE_DIM    = "#1E0D2E"
PURPLE_TEXT   = "#C4B5FD"

BORDER        = "#2A2A3E"
BORDER_ACTIVE = "#007BFF"

TEXT_PRIMARY  = "#F0F0F5"
TEXT_SECOND   = "#8888AA"
TEXT_MUTED    = "#44445A"

# ── Typography ────────────────────────────────────────────────────────────────
FONT_TITLE  = ("Segoe UI", 26, "bold")
FONT_H2     = ("Segoe UI", 18, "bold")
FONT_H3     = ("Segoe UI", 14, "bold")
FONT_BODY   = ("Segoe UI", 13)
FONT_SMALL  = ("Segoe UI", 11)
FONT_TINY   = ("Segoe UI", 10)
FONT_MONO   = ("Consolas", 12)

# ── Radius ────────────────────────────────────────────────────────────────────
R_CARD    = 14
R_BUTTON  = 10
R_INPUT   = 8
R_BADGE   = 20

# ── Status badge colours ──────────────────────────────────────────────────────
STATUS_COLORS = {
    "present":  (GREEN_TEXT,  GREEN_DIM),
    "approved": (GREEN_TEXT,  GREEN_DIM),
    "pending":  (ORANGE_TEXT, ORANGE_DIM),
    "late":     (ORANGE_TEXT, ORANGE_DIM),
    "absent":   (RED_TEXT,    RED_DIM),
    "rejected": (RED_TEXT,    RED_DIM),
    "half_day": (PURPLE_TEXT, PURPLE_DIM),
    "paid":     (GREEN_TEXT,  GREEN_DIM),
    "unpaid":   (RED_TEXT,    RED_DIM),
}

DEPT_COLORS = ["#007BFF","#00C853","#FF6B6B","#FFC107","#9C27B0","#00BCD4","#FF5722","#607D8B"]
