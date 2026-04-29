"""
Leave management service.
"""
from datetime import date
from database.db_setup import get_session
from database.models import Leave, LeaveStatus, LeaveType
from utils.validators import validate_date_range
from utils.helpers import parse_date


class LeaveService:

    @staticmethod
    def get_all(status_filter: str | None = None) -> list[dict]:
        with get_session() as session:
            q = session.query(Leave)
            if status_filter:
                q = q.filter_by(status=status_filter)
            leaves = q.order_by(Leave.created_at.desc()).all()
            return [LeaveService._to_dict(lv) for lv in leaves]

    @staticmethod
    def get_for_employee(emp_id: int) -> list[dict]:
        with get_session() as session:
            leaves = (
                session.query(Leave)
                .filter_by(employee_id=emp_id)
                .order_by(Leave.created_at.desc())
                .all()
            )
            return [LeaveService._to_dict(lv) for lv in leaves]

    @staticmethod
    def apply(emp_id: int, leave_type: str, start_date: str,
              end_date: str, reason: str) -> tuple[bool, str]:
        """Submit a leave request."""
        valid, err = validate_date_range(start_date, end_date)
        if not valid:
            return False, err

        if leave_type not in [lt.value for lt in LeaveType]:
            return False, f"Invalid leave type '{leave_type}'."

        s_date = parse_date(start_date)
        e_date = parse_date(end_date)

        with get_session() as session:
            # Check for overlapping approved/pending leaves
            overlapping = session.query(Leave).filter(
                Leave.employee_id == emp_id,
                Leave.status.in_([LeaveStatus.PENDING.value, LeaveStatus.APPROVED.value]),
                Leave.start_date <= e_date,
                Leave.end_date   >= s_date,
            ).first()
            if overlapping:
                return False, "There is already an active/pending leave overlapping this period."

            lv = Leave(
                employee_id=emp_id,
                leave_type=leave_type,
                start_date=s_date,
                end_date=e_date,
                reason=reason.strip(),
                status=LeaveStatus.PENDING.value,
            )
            session.add(lv)
            session.flush()
            return True, str(lv.id)

    @staticmethod
    def approve(leave_id: int, approver_id: int) -> tuple[bool, str]:
        with get_session() as session:
            lv = session.query(Leave).filter_by(id=leave_id).first()
            if not lv:
                return False, "Leave request not found."
            if lv.status != LeaveStatus.PENDING.value:
                return False, f"Leave is already '{lv.status}'."
            lv.status      = LeaveStatus.APPROVED.value
            lv.approved_by = approver_id
        return True, "Leave approved."

    @staticmethod
    def reject(leave_id: int, approver_id: int) -> tuple[bool, str]:
        with get_session() as session:
            lv = session.query(Leave).filter_by(id=leave_id).first()
            if not lv:
                return False, "Leave request not found."
            if lv.status != LeaveStatus.PENDING.value:
                return False, f"Leave is already '{lv.status}'."
            lv.status      = LeaveStatus.REJECTED.value
            lv.approved_by = approver_id
        return True, "Leave rejected."

    @staticmethod
    def delete(leave_id: int) -> tuple[bool, str]:
        with get_session() as session:
            lv = session.query(Leave).filter_by(id=leave_id).first()
            if not lv:
                return False, "Leave request not found."
            if lv.status == LeaveStatus.APPROVED.value:
                return False, "Cannot delete an approved leave."
            session.delete(lv)
        return True, "Leave request deleted."

    @staticmethod
    def pending_count() -> int:
        with get_session() as session:
            return session.query(Leave).filter_by(
                status=LeaveStatus.PENDING.value
            ).count()

    @staticmethod
    def _to_dict(lv: Leave) -> dict:
        return {
            "id":           lv.id,
            "employee_id":  lv.employee_id,
            "emp_name":     lv.employee.full_name if lv.employee else "—",
            "leave_type":   lv.leave_type,
            "start_date":   str(lv.start_date),
            "end_date":     str(lv.end_date),
            "duration":     lv.duration_days,
            "reason":       lv.reason,
            "status":       lv.status,
            "approved_by":  lv.approved_by,
            "created_at":   str(lv.created_at),
        }
