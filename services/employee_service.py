"""
Employee CRUD service.
"""
from datetime import date
from database.db_setup import get_session
from database.models import Employee, Department, EmployeeStatus
from utils.validators import (
    validate_name, validate_email, validate_phone,
    validate_salary, validate_emp_code, validate_date
)
from utils.helpers import generate_emp_code, parse_date


class EmployeeService:

    @staticmethod
    def get_all(status_filter: str | None = None) -> list[dict]:
        """Return all employees as list of dicts."""
        with get_session() as session:
            q = session.query(Employee)
            if status_filter:
                q = q.filter_by(status=status_filter)
            employees = q.order_by(Employee.first_name).all()
            return [EmployeeService._to_dict(e) for e in employees]

    @staticmethod
    def get_by_id(emp_id: int) -> dict | None:
        with get_session() as session:
            e = session.query(Employee).filter_by(id=emp_id).first()
            return EmployeeService._to_dict(e) if e else None

    @staticmethod
    def get_by_emp_code(emp_code: str) -> dict | None:
        with get_session() as session:
            e = session.query(Employee).filter_by(emp_code=emp_code.upper()).first()
            return EmployeeService._to_dict(e) if e else None

    @staticmethod
    def search(query: str) -> list[dict]:
        """Search employees by name, email or emp_code."""
        with get_session() as session:
            q_lower = f"%{query.lower()}%"
            employees = session.query(Employee).filter(
                (Employee.first_name.ilike(q_lower)) |
                (Employee.last_name.ilike(q_lower)) |
                (Employee.email.ilike(q_lower)) |
                (Employee.emp_code.ilike(q_lower))
            ).all()
            return [EmployeeService._to_dict(e) for e in employees]

    @staticmethod
    def create(data: dict) -> tuple[bool, str]:
        """Create a new employee. Returns (success, message|id)."""
        errors = EmployeeService._validate(data)
        if errors:
            return False, "\n".join(errors)

        with get_session() as session:
            # Check unique email
            if session.query(Employee).filter_by(email=data["email"].strip().lower()).first():
                return False, f"Email '{data['email']}' is already registered."

            # Auto-generate code if not provided
            emp_code = data.get("emp_code", "").strip().upper()
            if not emp_code:
                existing = [e.emp_code for e in session.query(Employee).all()]
                emp_code = generate_emp_code(existing)
            else:
                if session.query(Employee).filter_by(emp_code=emp_code).first():
                    return False, f"Employee code '{emp_code}' already exists."

            dept_id = data.get("department_id")
            if dept_id:
                dept = session.query(Department).filter_by(id=int(dept_id)).first()
                if not dept:
                    return False, "Selected department not found."

            hire_date = parse_date(data.get("hire_date", "")) or date.today()

            emp = Employee(
                emp_code=emp_code,
                first_name=data["first_name"].strip(),
                last_name=data["last_name"].strip(),
                email=data["email"].strip().lower(),
                phone=data.get("phone", "").strip(),
                salary=float(data.get("salary", 0)),
                position=data.get("position", "").strip(),
                department_id=int(dept_id) if dept_id else None,
                hire_date=hire_date,
                status=data.get("status", EmployeeStatus.ACTIVE.value),
            )
            session.add(emp)
            session.flush()
            return True, str(emp.id)

    @staticmethod
    def update(emp_id: int, data: dict) -> tuple[bool, str]:
        """Update an existing employee."""
        errors = EmployeeService._validate(data, is_update=True)
        if errors:
            return False, "\n".join(errors)

        with get_session() as session:
            emp = session.query(Employee).filter_by(id=emp_id).first()
            if not emp:
                return False, "Employee not found."

            # Check email uniqueness (excluding self)
            new_email = data.get("email", emp.email).strip().lower()
            conflict = session.query(Employee).filter(
                Employee.email == new_email, Employee.id != emp_id
            ).first()
            if conflict:
                return False, f"Email '{new_email}' is already in use."

            emp.first_name    = data.get("first_name", emp.first_name).strip()
            emp.last_name     = data.get("last_name",  emp.last_name).strip()
            emp.email         = new_email
            emp.phone         = data.get("phone",    emp.phone).strip()
            emp.position      = data.get("position", emp.position).strip()
            emp.salary        = float(data.get("salary", emp.salary))
            emp.status        = data.get("status",   emp.status)
            dept_id           = data.get("department_id")
            emp.department_id = int(dept_id) if dept_id else emp.department_id
            if data.get("hire_date"):
                emp.hire_date = parse_date(data["hire_date"]) or emp.hire_date

        return True, "Employee updated successfully."

    @staticmethod
    def delete(emp_id: int) -> tuple[bool, str]:
        """Soft-delete: mark employee as terminated."""
        with get_session() as session:
            emp = session.query(Employee).filter_by(id=emp_id).first()
            if not emp:
                return False, "Employee not found."
            emp.status = EmployeeStatus.TERMINATED.value
        return True, "Employee marked as terminated."

    @staticmethod
    def hard_delete(emp_id: int) -> tuple[bool, str]:
        """Permanently delete an employee and all related records."""
        with get_session() as session:
            emp = session.query(Employee).filter_by(id=emp_id).first()
            if not emp:
                return False, "Employee not found."
            session.delete(emp)
        return True, "Employee deleted permanently."

    @staticmethod
    def count() -> int:
        with get_session() as session:
            return session.query(Employee).filter_by(
                status=EmployeeStatus.ACTIVE.value
            ).count()

    @staticmethod
    def _validate(data: dict, is_update: bool = False) -> list[str]:
        errors = []
        for field, label in [("first_name", "First Name"), ("last_name", "Last Name")]:
            if data.get(field) is not None or not is_update:
                ok, msg = validate_name(data.get(field, ""), label)
                if not ok:
                    errors.append(msg)
        if data.get("email") is not None or not is_update:
            ok, msg = validate_email(data.get("email", ""))
            if not ok:
                errors.append(msg)
        if data.get("phone"):
            ok, msg = validate_phone(data["phone"])
            if not ok:
                errors.append(msg)
        if data.get("salary") is not None:
            ok, msg = validate_salary(str(data.get("salary", "")))
            if not ok:
                errors.append(msg)
        if data.get("hire_date"):
            ok, msg = validate_date(data["hire_date"], "Hire date")
            if not ok:
                errors.append(msg)
        return errors

    @staticmethod
    def _to_dict(e: Employee) -> dict:
        if e is None:
            return {}
        return {
            "id":            e.id,
            "emp_code":      e.emp_code,
            "first_name":    e.first_name,
            "last_name":     e.last_name,
            "full_name":     e.full_name,
            "email":         e.email,
            "phone":         e.phone,
            "hire_date":     str(e.hire_date) if e.hire_date else "",
            "salary":        e.salary,
            "position":      e.position,
            "status":        e.status,
            "department_id": e.department_id,
            "department_name": e.department.name if e.department else "—",
        }
