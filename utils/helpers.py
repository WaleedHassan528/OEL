"""
Shared utility helpers — password hashing, formatting, constants.
"""
import hashlib
import secrets
from datetime import datetime, date


# ─── Password Hashing (sha256 + salt, no bcrypt dependency risk) ──────────────

def hash_password(plain: str) -> str:
    """Hash a plaintext password with a random salt using SHA-256."""
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + plain).encode()).hexdigest()
    return f"{salt}:{hashed}"


def verify_password(plain: str, stored_hash: str) -> bool:
    """Verify a plaintext password against a stored hash."""
    try:
        salt, hashed = stored_hash.split(":", 1)
        return hashlib.sha256((salt + plain).encode()).hexdigest() == hashed
    except Exception:
        return False


# ─── Formatting ───────────────────────────────────────────────────────────────

def format_currency(amount: float, symbol: str = "$") -> str:
    """Format a number as currency string."""
    return f"{symbol}{amount:,.2f}"


def format_date(d) -> str:
    """Format a date/datetime to DD Mon YYYY string."""
    if d is None:
        return "—"
    if isinstance(d, str):
        try:
            d = datetime.strptime(d, "%Y-%m-%d").date()
        except ValueError:
            return d
    return d.strftime("%d %b %Y")


def parse_date(date_str: str) -> date | None:
    """Parse YYYY-MM-DD string to date object."""
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    return None


def month_name(month_num: int) -> str:
    """Return full month name from number."""
    months = ["January","February","March","April","May","June",
              "July","August","September","October","November","December"]
    if 1 <= month_num <= 12:
        return months[month_num - 1]
    return str(month_num)


def today_str() -> str:
    """Return today's date as YYYY-MM-DD string."""
    return date.today().strftime("%Y-%m-%d")


def generate_emp_code(existing_codes: list[str]) -> str:
    """Auto-generate a unique employee code like EMP009."""
    nums = []
    for code in existing_codes:
        try:
            nums.append(int(code.replace("EMP", "")))
        except ValueError:
            pass
    next_num = max(nums, default=0) + 1
    return f"EMP{next_num:03d}"


def truncate(text: str, max_len: int = 30) -> str:
    """Truncate a string and add ellipsis if too long."""
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."


def badge_color(status: str) -> str:
    """Return a color hex for a given status badge."""
    mapping = {
        "approved": "#00C853",
        "present":  "#00C853",
        "active":   "#00C853",
        "pending":  "#FFA000",
        "late":     "#FFA000",
        "half_day": "#FFA000",
        "rejected": "#F44336",
        "absent":   "#F44336",
        "inactive": "#F44336",
        "terminated":"#9E9E9E",
    }
    return mapping.get(status.lower(), "#9E9E9E")
