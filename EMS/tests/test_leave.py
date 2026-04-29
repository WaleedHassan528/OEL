"""
Unit tests for LeaveService.
"""
import unittest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import database.db_setup as db_setup
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from database.models import Base, Department, Employee

_test_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

@event.listens_for(_test_engine, "connect")
def _fk(conn, _):
    conn.execute("PRAGMA foreign_keys=ON")

Base.metadata.create_all(bind=_test_engine)
db_setup.engine       = _test_engine
db_setup.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)

from services.leave_service import LeaveService
from database.db_setup import get_session
from datetime import date, timedelta

EMP_ID = None


def _seed():
    global EMP_ID
    with get_session() as session:
        dept = session.query(Department).first()
        if not dept:
            dept = Department(name="HR", description="Human Resources")
            session.add(dept)
            session.flush()

        emp = session.query(Employee).first()
        if not emp:
            emp = Employee(
                emp_code="EMP001",
                first_name="Test",
                last_name="User",
                email="leavetest@test.com",
                salary=50000.0,
                department_id=dept.id,
            )
            session.add(emp)
            session.flush()
        EMP_ID = emp.id


class TestLeaveService(unittest.TestCase):

    def setUp(self):
        _seed()

    def _future_range(self, offset_start=30, offset_end=35):
        s = str(date.today() + timedelta(days=offset_start))
        e = str(date.today() + timedelta(days=offset_end))
        return s, e

    def test_apply_leave_success(self):
        s, e = self._future_range(10, 12)
        ok, result = LeaveService.apply(EMP_ID, "annual", s, e, "Holiday")
        self.assertTrue(ok)
        self.assertTrue(result.isdigit())

    def test_apply_invalid_date_range(self):
        ok, msg = LeaveService.apply(EMP_ID, "annual", "2024-06-20", "2024-06-10", "Bad range")
        self.assertFalse(ok)
        self.assertIn("after", msg.lower())

    def test_apply_invalid_leave_type(self):
        s, e = self._future_range(20, 22)
        ok, msg = LeaveService.apply(EMP_ID, "vacation_plus", s, e, "reason")
        self.assertFalse(ok)
        self.assertIn("invalid", msg.lower())

    def test_apply_overlap_rejected(self):
        s, e = self._future_range(40, 45)
        LeaveService.apply(EMP_ID, "annual", s, e, "First request")
        # Overlapping second request
        s2, e2 = self._future_range(42, 44)
        ok, msg = LeaveService.apply(EMP_ID, "sick", s2, e2, "Overlap")
        self.assertFalse(ok)
        self.assertIn("overlapping", msg.lower())

    def test_get_for_employee(self):
        s, e = self._future_range(50, 52)
        LeaveService.apply(EMP_ID, "sick", s, e, "Sick day")
        leaves = LeaveService.get_for_employee(EMP_ID)
        self.assertIsInstance(leaves, list)
        self.assertGreater(len(leaves), 0)

    def test_approve_leave(self):
        s, e = self._future_range(60, 62)
        _, leave_id = LeaveService.apply(EMP_ID, "annual", s, e, "Approve me")
        ok, msg = LeaveService.approve(int(leave_id), EMP_ID)
        self.assertTrue(ok)

    def test_reject_leave(self):
        s, e = self._future_range(70, 72)
        _, leave_id = LeaveService.apply(EMP_ID, "unpaid", s, e, "Reject me")
        ok, msg = LeaveService.reject(int(leave_id), EMP_ID)
        self.assertTrue(ok)

    def test_cannot_approve_already_approved(self):
        s, e = self._future_range(80, 82)
        _, leave_id = LeaveService.apply(EMP_ID, "annual", s, e, "Double approve")
        LeaveService.approve(int(leave_id), EMP_ID)
        ok, msg = LeaveService.approve(int(leave_id), EMP_ID)
        self.assertFalse(ok)
        self.assertIn("already", msg.lower())

    def test_pending_count(self):
        initial = LeaveService.pending_count()
        s, e = self._future_range(90, 91)
        LeaveService.apply(EMP_ID, "annual", s, e, "Pending test")
        self.assertEqual(LeaveService.pending_count(), initial + 1)

    def test_delete_pending_leave(self):
        s, e = self._future_range(100, 101)
        _, leave_id = LeaveService.apply(EMP_ID, "sick", s, e, "Delete me")
        ok, _ = LeaveService.delete(int(leave_id))
        self.assertTrue(ok)

    def test_cannot_delete_approved_leave(self):
        s, e = self._future_range(110, 112)
        _, leave_id = LeaveService.apply(EMP_ID, "annual", s, e, "No delete")
        LeaveService.approve(int(leave_id), EMP_ID)
        ok, msg = LeaveService.delete(int(leave_id))
        self.assertFalse(ok)
        self.assertIn("approved", msg.lower())

    def test_get_all_returns_list(self):
        leaves = LeaveService.get_all()
        self.assertIsInstance(leaves, list)

    def test_get_all_with_status_filter(self):
        leaves = LeaveService.get_all(status_filter="pending")
        for lv in leaves:
            self.assertEqual(lv["status"], "pending")


if __name__ == "__main__":
    unittest.main(verbosity=2)
