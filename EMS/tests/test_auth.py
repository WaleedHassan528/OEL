"""
Unit tests for AuthService.
Uses an in-memory SQLite database.
"""
import unittest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Patch DB to use in-memory SQLite
import database.db_setup as db_setup
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from database.models import Base

_test_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

@event.listens_for(_test_engine, "connect")
def _fk_pragma(conn, _):
    conn.execute("PRAGMA foreign_keys=ON")

Base.metadata.create_all(bind=_test_engine)
db_setup.engine       = _test_engine
db_setup.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)

from services.auth_service import AuthService
from utils.helpers import hash_password
from database.db_setup import get_session
from database.models import User, UserRole


def _create_test_user(username: str, password: str, role: str = UserRole.ADMIN.value):
    with get_session() as session:
        existing = session.query(User).filter_by(username=username).first()
        if not existing:
            session.add(User(
                username=username,
                password_hash=hash_password(password),
                role=role,
            ))


class TestAuthService(unittest.TestCase):

    def setUp(self):
        """Ensure a test admin user exists."""
        _create_test_user("testadmin", "admin123", UserRole.ADMIN.value)
        _create_test_user("testuser",  "pass1234", UserRole.EMPLOYEE.value)
        AuthService.logout()

    def test_login_success(self):
        ok, msg = AuthService.login("testadmin", "admin123")
        self.assertTrue(ok)
        self.assertIn("success", msg.lower())

    def test_login_sets_current_user(self):
        AuthService.login("testadmin", "admin123")
        user = AuthService.get_current_user()
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "testadmin")

    def test_login_wrong_password(self):
        ok, msg = AuthService.login("testadmin", "wrongpass")
        self.assertFalse(ok)
        self.assertIn("invalid", msg.lower())

    def test_login_nonexistent_user(self):
        ok, msg = AuthService.login("nobody", "anypass")
        self.assertFalse(ok)

    def test_login_empty_username(self):
        ok, msg = AuthService.login("", "admin123")
        self.assertFalse(ok)

    def test_logout_clears_user(self):
        AuthService.login("testadmin", "admin123")
        AuthService.logout()
        self.assertIsNone(AuthService.get_current_user())

    def test_is_admin_true(self):
        AuthService.login("testadmin", "admin123")
        self.assertTrue(AuthService.is_admin())

    def test_is_admin_false_for_employee(self):
        AuthService.login("testuser", "pass1234")
        self.assertFalse(AuthService.is_admin())

    def test_is_logged_in_false_initially(self):
        self.assertFalse(AuthService.is_logged_in())

    def test_is_logged_in_true_after_login(self):
        AuthService.login("testadmin", "admin123")
        self.assertTrue(AuthService.is_logged_in())

    def test_create_user_success(self):
        ok, _ = AuthService.create_user("newuser99", "secure123", UserRole.EMPLOYEE.value)
        self.assertTrue(ok)

    def test_create_user_duplicate(self):
        AuthService.create_user("dupuser", "pass123", UserRole.EMPLOYEE.value)
        ok, msg = AuthService.create_user("dupuser", "pass456", UserRole.EMPLOYEE.value)
        self.assertFalse(ok)
        self.assertIn("already", msg.lower())

    def test_get_all_users_returns_list(self):
        users = AuthService.get_all_users()
        self.assertIsInstance(users, list)
        self.assertGreater(len(users), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
