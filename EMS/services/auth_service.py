"""
Authentication service — login, RBAC, session management.
"""
from datetime import datetime
from database.db_setup import get_session
from database.models import User, UserRole
from utils.helpers import verify_password, hash_password
from utils.validators import validate_username, validate_password


class AuthService:
    _current_user: User | None = None

    # ── Login ──────────────────────────────────────────────────────────────────

    @classmethod
    def login(cls, username: str, password: str) -> tuple[bool, str]:
        """
        Attempt to log in. Returns (success, message).
        On success, sets cls._current_user.
        """
        valid_u, err_u = validate_username(username)
        if not valid_u:
            return False, err_u
        valid_p, err_p = validate_password(password)
        if not valid_p:
            return False, err_p

        with get_session() as session:
            user = session.query(User).filter_by(
                username=username.strip(), is_active=True
            ).first()

            if not user:
                return False, "Invalid username or password."

            if not verify_password(password, user.password_hash):
                return False, "Invalid username or password."

            # Update last_login
            user.last_login = datetime.utcnow()
            session.commit()

            # Refresh to load attributes after commit expiration
            session.refresh(user)

            # Detach from session for use outside context
            session.expunge(user)
            cls._current_user = user

        return True, "Login successful."

    # ── Logout ─────────────────────────────────────────────────────────────────

    @classmethod
    def logout(cls):
        cls._current_user = None

    # ── Current User ────────────────────────────────────────────────────────────

    @classmethod
    def get_current_user(cls) -> User | None:
        return cls._current_user

    @classmethod
    def is_admin(cls) -> bool:
        return cls._current_user is not None and \
               cls._current_user.role == UserRole.ADMIN.value

    @classmethod
    def is_logged_in(cls) -> bool:
        return cls._current_user is not None

    # ── User Management ─────────────────────────────────────────────────────────

    @classmethod
    def create_user(cls, username: str, password: str, role: str,
                    employee_id: int | None = None) -> tuple[bool, str]:
        """Create a new user account (admin only)."""
        valid_u, err_u = validate_username(username)
        if not valid_u:
            return False, err_u
        valid_p, err_p = validate_password(password)
        if not valid_p:
            return False, err_p

        with get_session() as session:
            existing = session.query(User).filter_by(username=username.strip()).first()
            if existing:
                return False, f"Username '{username}' already exists."

            user = User(
                username=username.strip(),
                password_hash=hash_password(password),
                role=role,
                employee_id=employee_id,
            )
            session.add(user)
        return True, "User created successfully."

    @classmethod
    def change_password(cls, user_id: int, old_password: str,
                        new_password: str) -> tuple[bool, str]:
        """Change user password after verifying old password."""
        valid_p, err_p = validate_password(new_password)
        if not valid_p:
            return False, err_p

        with get_session() as session:
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                return False, "User not found."
            if not verify_password(old_password, user.password_hash):
                return False, "Incorrect current password."
            user.password_hash = hash_password(new_password)
        return True, "Password changed successfully."

    @classmethod
    def get_all_users(cls) -> list[dict]:
        """Retrieve list of all users."""
        with get_session() as session:
            users = session.query(User).all()
            return [
                {"id": u.id, "username": u.username, "role": u.role,
                 "employee_id": u.employee_id, "is_active": u.is_active}
                for u in users
            ]
