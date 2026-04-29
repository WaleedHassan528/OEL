"""
Unit tests for EmployeeService.
"""
import unittest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import database.db_setup as db_setup
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from database.models import Base, Department

_test_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

@event.listens_for(_test_engine, "connect")
def _fk(conn, _):
    conn.execute("PRAGMA foreign_keys=ON")

Base.metadata.create_all(bind=_test_engine)
db_setup.engine       = _test_engine
db_setup.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)

from services.employee_service import EmployeeService
from database.db_setup import get_session


def _seed_dept():
    with get_session() as session:
        existing = session.query(Department).filter_by(name="Engineering").first()
        if not existing:
            d = Department(name="Engineering", description="Dev team")
            session.add(d)
            session.flush()
            return d.id
        return existing.id


DEPT_ID = None

VALID_DATA = {
    "first_name":    "Jane",
    "last_name":     "Doe",
    "email":         "jane.doe@test.com",
    "phone":         "+1-555-1234",
    "position":      "Engineer",
    "salary":        "70000",
    "hire_date":     "2023-01-15",
}


class TestEmployeeService(unittest.TestCase):

    def setUp(self):
        global DEPT_ID
        DEPT_ID = _seed_dept()

    def _get_data(self, suffix: str = "") -> dict:
        data = VALID_DATA.copy()
        data["email"] = f"test{suffix}@company.com"
        data["department_id"] = DEPT_ID
        return data

    def test_create_employee_success(self):
        ok, result = EmployeeService.create(self._get_data("_c1"))
        self.assertTrue(ok)
        self.assertTrue(result.isdigit())

    def test_create_auto_emp_code(self):
        data = self._get_data("_c2")
        data.pop("emp_code", None)
        ok, emp_id = EmployeeService.create(data)
        self.assertTrue(ok)
        emp = EmployeeService.get_by_id(int(emp_id))
        self.assertTrue(emp["emp_code"].startswith("EMP"))

    def test_create_duplicate_email(self):
        data = self._get_data("_dup")
        EmployeeService.create(data)
        ok, msg = EmployeeService.create(data)
        self.assertFalse(ok)
        self.assertIn("already", msg.lower())

    def test_create_invalid_email(self):
        data = self._get_data("_bad")
        data["email"] = "not-an-email"
        ok, msg = EmployeeService.create(data)
        self.assertFalse(ok)

    def test_create_negative_salary(self):
        data = self._get_data("_neg")
        data["salary"] = "-500"
        ok, _ = EmployeeService.create(data)
        self.assertFalse(ok)

    def test_create_missing_first_name(self):
        data = self._get_data("_mn")
        data["first_name"] = ""
        ok, _ = EmployeeService.create(data)
        self.assertFalse(ok)

    def test_get_by_id(self):
        data = self._get_data("_get")
        _, emp_id = EmployeeService.create(data)
        emp = EmployeeService.get_by_id(int(emp_id))
        self.assertIsNotNone(emp)
        self.assertEqual(emp["email"], data["email"])

    def test_get_all_returns_list(self):
        EmployeeService.create(self._get_data("_all"))
        emps = EmployeeService.get_all()
        self.assertIsInstance(emps, list)
        self.assertGreater(len(emps), 0)

    def test_search(self):
        data = self._get_data("_search")
        data["first_name"] = "UniqueXYZ"
        EmployeeService.create(data)
        results = EmployeeService.search("UniqueXYZ")
        self.assertTrue(any("UniqueXYZ" in r["first_name"] for r in results))

    def test_update_employee(self):
        data = self._get_data("_upd")
        _, emp_id = EmployeeService.create(data)
        ok, msg = EmployeeService.update(int(emp_id), {"first_name": "UpdatedName", "salary": "80000"})
        self.assertTrue(ok)
        emp = EmployeeService.get_by_id(int(emp_id))
        self.assertEqual(emp["first_name"], "UpdatedName")
        self.assertEqual(emp["salary"], 80000.0)

    def test_soft_delete(self):
        data = self._get_data("_del")
        _, emp_id = EmployeeService.create(data)
        ok, _ = EmployeeService.delete(int(emp_id))
        self.assertTrue(ok)
        emp = EmployeeService.get_by_id(int(emp_id))
        self.assertEqual(emp["status"], "terminated")

    def test_count(self):
        initial = EmployeeService.count()
        EmployeeService.create(self._get_data("_cnt"))
        self.assertEqual(EmployeeService.count(), initial + 1)

    def test_get_nonexistent_employee(self):
        emp = EmployeeService.get_by_id(99999)
        self.assertIsNone(emp)

    def test_update_nonexistent_employee(self):
        ok, msg = EmployeeService.update(99999, {"first_name": "Ghost"})
        self.assertFalse(ok)
        self.assertIn("not found", msg.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
