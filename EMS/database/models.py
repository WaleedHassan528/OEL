"""
Database models using SQLAlchemy ORM.
Defines all tables with proper foreign key relationships.
"""
from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Float, Date, DateTime,
    ForeignKey, Text, Boolean, Enum
)
from sqlalchemy.orm import relationship, DeclarativeBase
import enum


class Base(DeclarativeBase):
    pass


# ─── Enumerations ─────────────────────────────────────────────────────────────

class UserRole(str, enum.Enum):
    ADMIN    = "admin"
    EMPLOYEE = "employee"


class EmployeeStatus(str, enum.Enum):
    ACTIVE     = "active"
    INACTIVE   = "inactive"
    TERMINATED = "terminated"


class AttendanceStatus(str, enum.Enum):
    PRESENT = "present"
    ABSENT  = "absent"
    LATE    = "late"
    HALF_DAY = "half_day"


class LeaveStatus(str, enum.Enum):
    PENDING  = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class LeaveType(str, enum.Enum):
    ANNUAL    = "annual"
    SICK      = "sick"
    MATERNITY = "maternity"
    UNPAID    = "unpaid"
    OTHER     = "other"


# ─── Models ───────────────────────────────────────────────────────────────────

class Department(Base):
    __tablename__ = "departments"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    name        = Column(String(100), unique=True, nullable=False)
    description = Column(Text, default="")
    created_at  = Column(DateTime, default=datetime.utcnow)

    employees = relationship("Employee", back_populates="department")

    def __repr__(self):
        return f"<Department(id={self.id}, name='{self.name}')>"


class Employee(Base):
    __tablename__ = "employees"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    emp_code      = Column(String(20), unique=True, nullable=False)
    first_name    = Column(String(50), nullable=False)
    last_name     = Column(String(50), nullable=False)
    email         = Column(String(120), unique=True, nullable=False)
    phone         = Column(String(20), default="")
    hire_date     = Column(Date, default=date.today)
    salary        = Column(Float, default=0.0)
    position      = Column(String(100), default="")
    status        = Column(String(20), default=EmployeeStatus.ACTIVE.value)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    created_at    = Column(DateTime, default=datetime.utcnow)
    updated_at    = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    department   = relationship("Department", back_populates="employees")
    user         = relationship("User", back_populates="employee", uselist=False)
    attendance   = relationship("Attendance", back_populates="employee", cascade="all, delete-orphan")
    leaves       = relationship("Leave", back_populates="employee", cascade="all, delete-orphan",
                                foreign_keys="Leave.employee_id")
    payrolls     = relationship("Payroll", back_populates="employee", cascade="all, delete-orphan")
    performances = relationship("Performance", back_populates="employee", cascade="all, delete-orphan",
                                foreign_keys="Performance.employee_id")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"<Employee(id={self.id}, name='{self.full_name}')>"


class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    username      = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    role          = Column(String(20), default=UserRole.EMPLOYEE.value)
    employee_id   = Column(Integer, ForeignKey("employees.id"), nullable=True)
    is_active     = Column(Boolean, default=True)
    last_login    = Column(DateTime, nullable=True)
    created_at    = Column(DateTime, default=datetime.utcnow)

    employee = relationship("Employee", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"


class Attendance(Base):
    __tablename__ = "attendance"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    date        = Column(Date, nullable=False, default=date.today)
    check_in    = Column(String(10), default="")   # HH:MM
    check_out   = Column(String(10), default="")   # HH:MM
    status      = Column(String(20), default=AttendanceStatus.PRESENT.value)
    notes       = Column(Text, default="")
    created_at  = Column(DateTime, default=datetime.utcnow)

    employee = relationship("Employee", back_populates="attendance")

    def __repr__(self):
        return f"<Attendance(emp={self.employee_id}, date={self.date}, status='{self.status}')>"


class Leave(Base):
    __tablename__ = "leaves"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    leave_type  = Column(String(20), default=LeaveType.ANNUAL.value)
    start_date  = Column(Date, nullable=False)
    end_date    = Column(Date, nullable=False)
    reason      = Column(Text, default="")
    status      = Column(String(20), default=LeaveStatus.PENDING.value)
    approved_by = Column(Integer, ForeignKey("employees.id"), nullable=True)
    created_at  = Column(DateTime, default=datetime.utcnow)
    updated_at  = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    employee = relationship("Employee", back_populates="leaves", foreign_keys=[employee_id])
    approver = relationship("Employee", foreign_keys=[approved_by])

    @property
    def duration_days(self):
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 0

    def __repr__(self):
        return f"<Leave(emp={self.employee_id}, type='{self.leave_type}', status='{self.status}')>"


class Payroll(Base):
    __tablename__ = "payroll"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    employee_id  = Column(Integer, ForeignKey("employees.id"), nullable=False)
    month        = Column(Integer, nullable=False)   # 1-12
    year         = Column(Integer, nullable=False)
    base_salary  = Column(Float, default=0.0)
    allowances   = Column(Float, default=0.0)
    deductions   = Column(Float, default=0.0)
    net_pay      = Column(Float, default=0.0)
    working_days = Column(Integer, default=0)
    present_days = Column(Integer, default=0)
    generated_on = Column(DateTime, default=datetime.utcnow)

    employee = relationship("Employee", back_populates="payrolls")

    def __repr__(self):
        return f"<Payroll(emp={self.employee_id}, {self.month}/{self.year}, net={self.net_pay})>"


class Performance(Base):
    __tablename__ = "performance"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    rating      = Column(Integer, default=3)   # 1-5
    comments    = Column(Text, default="")
    review_date = Column(Date, default=date.today)
    created_at  = Column(DateTime, default=datetime.utcnow)

    employee = relationship("Employee", back_populates="performances", foreign_keys=[employee_id])
    reviewer = relationship("Employee", foreign_keys=[reviewer_id])

    def __repr__(self):
        return f"<Performance(emp={self.employee_id}, rating={self.rating})>"
