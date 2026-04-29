"""
Unit tests for PayrollService.
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

from services.payroll_service import PayrollService
from database.db_setup import get_session
from datetime import date

EMP_ID = None


def _seed():
    global EMP_ID
    with get_session() as session:
        dept = session.query(Department).first()
        if not dept:
            dept = Department(name="Finance", description="")
            session.add(dept)
            session.flush()

        emp = session.query(Employee).first()
        if not emp:
            emp = Employee(
                emp_code="EMP001",
                first_name="Pay",
                last_name="TestUser",
                email="payroll_test@company.com",
                salary=60000.0,
                department_id=dept.id,
            )
            session.add(emp)
            session.flush()
        EMP_ID = emp.id


class TestPayrollService(unittest.TestCase):

    def setUp(self):
        _seed()

    def test_generate_payroll_success(self):
        ok, result = PayrollService.generate(EMP_ID, month=1, year=2024)
        self.assertTrue(ok)
        self.assertIsInstance(result, dict)

    def test_payslip_has_required_fields(self):
        ok, result = PayrollService.generate(EMP_ID, month=2, year=2024)
        self.assertTrue(ok)
        required = ["emp_name", "base_salary", "net_pay", "allowances",
                    "deductions", "working_days", "fmt_net"]
        for field in required:
            self.assertIn(field, result, f"Missing field: {field}")

    def test_net_pay_positive(self):
        ok, result = PayrollService.generate(EMP_ID, month=3, year=2024)
        self.assertTrue(ok)
        self.assertGreater(result["net_pay"], 0)

    def test_net_pay_calculation(self):
        """Net = prorated_base + allowances - deductions."""
        ok, result = PayrollService.generate(EMP_ID, month=4, year=2024)
        self.assertTrue(ok)
        expected = result["prorated_base"] + result["allowances"] - result["deductions"]
        self.assertAlmostEqual(result["net_pay"], expected, places=2)

    def test_allowances_10_percent_of_base(self):
        """HRA allowance = 10% of base salary (+ any extras)."""
        ok, result = PayrollService.generate(EMP_ID, month=5, year=2024,
                                             extra_allowances=0.0)
        self.assertTrue(ok)
        expected_base_allowance = result["base_salary"] * 0.10
        self.assertGreaterEqual(result["allowances"], expected_base_allowance - 0.01)

    def test_invalid_month(self):
        ok, msg = PayrollService.generate(EMP_ID, month=13, year=2024)
        self.assertFalse(ok)
        self.assertIn("month", msg.lower())

    def test_invalid_year(self):
        ok, msg = PayrollService.generate(EMP_ID, month=1, year=1900)
        self.assertFalse(ok)
        self.assertIn("year", msg.lower())

    def test_nonexistent_employee(self):
        ok, msg = PayrollService.generate(99999, month=1, year=2024)
        self.assertFalse(ok)
        self.assertIn("not found", msg.lower())

    def test_duplicate_generate_updates_existing(self):
        """Generating payroll for same period twice should update, not duplicate."""
        PayrollService.generate(EMP_ID, month=6, year=2024)
        records_before = len(PayrollService.get_for_employee(EMP_ID))

        PayrollService.generate(EMP_ID, month=6, year=2024,
                                extra_allowances=500.0)
        records_after = len(PayrollService.get_for_employee(EMP_ID))

        self.assertEqual(records_before, records_after)

    def test_negative_allowance_rejected(self):
        ok, msg = PayrollService.generate(EMP_ID, month=7, year=2024,
                                          extra_allowances=-100.0)
        self.assertFalse(ok)

    def test_get_for_employee(self):
        PayrollService.generate(EMP_ID, month=8, year=2024)
        records = PayrollService.get_for_employee(EMP_ID)
        self.assertIsInstance(records, list)
        self.assertTrue(any(r["month"] == 8 for r in records))

    def test_get_all_with_month_filter(self):
        PayrollService.generate(EMP_ID, month=9, year=2024)
        records = PayrollService.get_all(month=9, year=2024)
        self.assertIsInstance(records, list)
        for r in records:
            self.assertEqual(r["month"], 9)

    def test_fmt_net_is_currency_string(self):
        ok, result = PayrollService.generate(EMP_ID, month=10, year=2024)
        self.assertTrue(ok)
        self.assertTrue(result["fmt_net"].startswith("$"))

    def test_working_days_reasonable(self):
        ok, result = PayrollService.generate(EMP_ID, month=1, year=2025)
        self.assertTrue(ok)
        # January 2025 has 23 working days
        self.assertGreaterEqual(result["working_days"], 20)
        self.assertLessEqual(result["working_days"], 23)


if __name__ == "__main__":
    unittest.main(verbosity=2)
