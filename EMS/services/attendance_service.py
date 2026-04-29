"""
Attendance service — mark, query, and summarize attendance.
"""
from datetime import date, timedelta
from database.db_setup import get_session
from database.models import Attendance, AttendanceStatus
from utils.helpers import parse_date


class AttendanceService:

    @staticmethod
    def get_all(limit: int = 200) -> list[dict]:
        """Return recent attendance records."""
        with get_session() as session:
            records = (
                session.query(Attendance)
                .order_by(Attendance.date.desc())
                .limit(limit)
                .all()
            )
            return [AttendanceService._to_dict(r) for r in records]

    @staticmethod
    def get_for_employee(emp_id: int, days: int = 30) -> list[dict]:
        """Return last N days of attendance for an employee."""
        since = date.today() - timedelta(days=days)
        with get_session() as session:
            records = (
                session.query(Attendance)
                .filter(
                    Attendance.employee_id == emp_id,
                    Attendance.date >= since,
                )
                .order_by(Attendance.date.desc())
                .all()
            )
            return [AttendanceService._to_dict(r) for r in records]

    @staticmethod
    def get_today() -> list[dict]:
        """All attendance records for today."""
        today = date.today()
        with get_session() as session:
            records = (
                session.query(Attendance)
                .filter(Attendance.date == today)
                .all()
            )
            return [AttendanceService._to_dict(r) for r in records]

    @staticmethod
    def mark(emp_id: int, att_date: str, check_in: str,
             check_out: str, status: str, notes: str = "") -> tuple[bool, str]:
        """Mark or update attendance for an employee on a given date."""
        d = parse_date(att_date)
        if not d:
            return False, "Invalid date format."
        if status not in [s.value for s in AttendanceStatus]:
            return False, f"Invalid status '{status}'."

        with get_session() as session:
            existing = session.query(Attendance).filter_by(
                employee_id=emp_id, date=d
            ).first()

            if existing:
                existing.check_in  = check_in
                existing.check_out = check_out
                existing.status    = status
                existing.notes     = notes
            else:
                record = Attendance(
                    employee_id=emp_id,
                    date=d,
                    check_in=check_in,
                    check_out=check_out,
                    status=status,
                    notes=notes,
                )
                session.add(record)
        return True, "Attendance recorded."

    @staticmethod
    def delete(record_id: int) -> tuple[bool, str]:
        with get_session() as session:
            record = session.query(Attendance).filter_by(id=record_id).first()
            if not record:
                return False, "Attendance record not found."
            session.delete(record)
        return True, "Attendance record deleted."

    @staticmethod
    def today_count() -> dict:
        """Return count of present/absent/late employees for today."""
        today = date.today()
        with get_session() as session:
            records = session.query(Attendance).filter(Attendance.date == today).all()
            counts = {"present": 0, "absent": 0, "late": 0, "half_day": 0}
            for r in records:
                if r.status in counts:
                    counts[r.status] += 1
            return counts

    @staticmethod
    def monthly_summary(emp_id: int, month: int, year: int) -> dict:
        """Summarize attendance for a month."""
        from calendar import monthrange
        _, days_in_month = monthrange(year, month)
        with get_session() as session:
            records = session.query(Attendance).filter(
                Attendance.employee_id == emp_id,
                Attendance.date >= date(year, month, 1),
                Attendance.date <= date(year, month, days_in_month),
            ).all()

            summary = {"present": 0, "absent": 0, "late": 0, "half_day": 0, "total": len(records)}
            for r in records:
                if r.status in summary:
                    summary[r.status] += 1
            return summary

    @staticmethod
    def _to_dict(r: Attendance) -> dict:
        emp_name = ""
        if r.employee:
            emp_name = r.employee.full_name
        return {
            "id":          r.id,
            "employee_id": r.employee_id,
            "emp_name":    emp_name,
            "date":        str(r.date),
            "check_in":    r.check_in,
            "check_out":   r.check_out,
            "status":      r.status,
            "notes":       r.notes,
        }
