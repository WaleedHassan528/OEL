"""
Performance review service.
"""
from datetime import date
from database.db_setup import get_session
from database.models import Performance
from utils.validators import validate_rating
from utils.helpers import parse_date


class PerformanceService:

    @staticmethod
    def get_all() -> list[dict]:
        with get_session() as session:
            reviews = session.query(Performance).order_by(
                Performance.review_date.desc()
            ).all()
            return [PerformanceService._to_dict(r) for r in reviews]

    @staticmethod
    def get_for_employee(emp_id: int) -> list[dict]:
        with get_session() as session:
            reviews = session.query(Performance).filter_by(
                employee_id=emp_id
            ).order_by(Performance.review_date.desc()).all()
            return [PerformanceService._to_dict(r) for r in reviews]

    @staticmethod
    def add_review(emp_id: int, reviewer_id: int | None,
                   rating: int, comments: str,
                   review_date: str | None = None) -> tuple[bool, str]:
        """Add a new performance review."""
        ok, err = validate_rating(rating)
        if not ok:
            return False, err

        r_date = parse_date(review_date) if review_date else date.today()
        if r_date is None:
            return False, "Invalid review date."

        with get_session() as session:
            pf = Performance(
                employee_id=emp_id,
                reviewer_id=reviewer_id,
                rating=int(rating),
                comments=comments.strip(),
                review_date=r_date,
            )
            session.add(pf)
        return True, "Review submitted."

    @staticmethod
    def update_review(review_id: int, rating: int,
                      comments: str) -> tuple[bool, str]:
        ok, err = validate_rating(rating)
        if not ok:
            return False, err

        with get_session() as session:
            pf = session.query(Performance).filter_by(id=review_id).first()
            if not pf:
                return False, "Review not found."
            pf.rating   = int(rating)
            pf.comments = comments.strip()
        return True, "Review updated."

    @staticmethod
    def delete_review(review_id: int) -> tuple[bool, str]:
        with get_session() as session:
            pf = session.query(Performance).filter_by(id=review_id).first()
            if not pf:
                return False, "Review not found."
            session.delete(pf)
        return True, "Review deleted."

    @staticmethod
    def average_rating(emp_id: int) -> float:
        with get_session() as session:
            reviews = session.query(Performance).filter_by(employee_id=emp_id).all()
            if not reviews:
                return 0.0
            return round(sum(r.rating for r in reviews) / len(reviews), 1)

    @staticmethod
    def _to_dict(r: Performance) -> dict:
        return {
            "id":          r.id,
            "employee_id": r.employee_id,
            "emp_name":    r.employee.full_name if r.employee else "—",
            "reviewer_id": r.reviewer_id,
            "reviewer_name": r.reviewer.full_name if r.reviewer else "Management",
            "rating":      r.rating,
            "comments":    r.comments,
            "review_date": str(r.review_date),
        }
