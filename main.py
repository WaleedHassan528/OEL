"""
EMS Pro — Employee Management System
Entry point. Initialises the database, seeds demo data, and launches the UI.

Usage:
    python main.py              # Launch the app
    python -m pytest tests/ -v  # Run unit tests
"""

import sys
import os

# ── Ensure project root is on sys.path ────────────────────────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def check_dependencies() -> bool:
    """Check that required packages are installed."""
    missing = []
    packages = {
        "customtkinter": "customtkinter",
        "sqlalchemy":    "SQLAlchemy",
        "PIL":           "Pillow",
    }
    for module, pkg in packages.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(pkg)

    if missing:
        print("=" * 60)
        print("Missing required packages. Install them with:")
        print(f"\n  pip install {' '.join(missing)}\n")
        print("=" * 60)
        return False
    return True


def main():
    if not check_dependencies():
        sys.exit(1)

    # ── Database setup & seed ─────────────────────────────────────────────────
    print("[EMS] Initialising database…")
    from database.db_setup import init_db
    init_db()

    print("[EMS] Seeding demo data if needed…")
    from database.seed_data import seed_database
    seed_database()

    # ── Launch UI ─────────────────────────────────────────────────────────────
    print("[EMS] Starting application…")
    import customtkinter as ctk
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    from ui.app import MainApp
    app = MainApp()

    # Centre window on screen
    app.update_idletasks()
    w, h = 1280, 800
    sw   = app.winfo_screenwidth()
    sh   = app.winfo_screenheight()
    x    = (sw - w) // 2
    y    = (sh - h) // 2
    app.geometry(f"{w}x{h}+{x}+{y}")

    app.mainloop()


if __name__ == "__main__":
    main()
