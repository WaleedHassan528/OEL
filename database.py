"""
database.py — SQLAlchemy models + seed data for EMS
"""
import hashlib, random
from datetime import date, datetime, timedelta
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Date,
    DateTime, ForeignKey, Text, Boolean
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()
engine = create_engine("sqlite:///ems.db", connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)

# ── Models ────────────────────────────────────────────────────────────────────

class Department(Base):
    __tablename__ = "departments"
    id          = Column(Integer, primary_key=True)
    name        = Column(String(100), unique=True, nullable=False)
    description = Column(Text, default="")
    employees   = relationship("Employee", back_populates="department",
                               foreign_keys="Employee.department_id")

class Employee(Base):
    __tablename__ = "employees"
    id            = Column(Integer, primary_key=True)
    employee_id   = Column(String(20), unique=True, nullable=False)
    first_name    = Column(String(50), nullable=False)
    last_name     = Column(String(50), nullable=False)
    email         = Column(String(100), unique=True, nullable=False)
    phone         = Column(String(20), default="")
    position      = Column(String(100), default="")
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    hire_date     = Column(Date, default=date.today)
    salary        = Column(Float, default=0.0)
    is_active     = Column(Boolean, default=True)
    avatar_color  = Column(String(7), default="#007BFF")

    department   = relationship("Department", back_populates="employees",
                                foreign_keys=[department_id])
    user         = relationship("User", back_populates="employee", uselist=False)
    attendance   = relationship("Attendance", back_populates="employee")
    leaves       = relationship("Leave", back_populates="employee")
    payrolls     = relationship("Payroll", back_populates="employee")
    performances = relationship("Performance", back_populates="employee")

class User(Base):
    __tablename__ = "users"
    id            = Column(Integer, primary_key=True)
    username      = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    role          = Column(String(20), default="employee")   # admin / employee
    employee_id   = Column(Integer, ForeignKey("employees.id"), nullable=True)
    is_active     = Column(Boolean, default=True)
    last_login    = Column(DateTime)
    employee      = relationship("Employee", back_populates="user")

class Attendance(Base):
    __tablename__ = "attendance"
    id          = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    date        = Column(Date, default=date.today)
    check_in    = Column(String(10))
    check_out   = Column(String(10))
    status      = Column(String(20), default="present")  # present/absent/late/half_day
    notes       = Column(Text, default="")
    employee    = relationship("Employee", back_populates="attendance")

class Leave(Base):
    __tablename__ = "leaves"
    id          = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    leave_type  = Column(String(50), nullable=False)
    start_date  = Column(Date, nullable=False)
    end_date    = Column(Date, nullable=False)
    reason      = Column(Text, default="")
    status      = Column(String(20), default="pending")  # pending/approved/rejected
    applied_on  = Column(DateTime, default=datetime.utcnow)
    employee    = relationship("Employee", back_populates="leaves")

class Payroll(Base):
    __tablename__ = "payroll"
    id               = Column(Integer, primary_key=True)
    employee_id      = Column(Integer, ForeignKey("employees.id"), nullable=False)
    month            = Column(Integer, nullable=False)
    year             = Column(Integer, nullable=False)
    basic_salary     = Column(Float, default=0.0)
    hra              = Column(Float, default=0.0)
    transport        = Column(Float, default=0.0)
    medical          = Column(Float, default=0.0)
    bonus            = Column(Float, default=0.0)
    tax_deduction    = Column(Float, default=0.0)
    other_deductions = Column(Float, default=0.0)
    net_salary       = Column(Float, default=0.0)
    is_paid          = Column(Boolean, default=False)
    employee         = relationship("Employee", back_populates="payrolls")

class Performance(Base):
    __tablename__ = "performance"
    id               = Column(Integer, primary_key=True)
    employee_id      = Column(Integer, ForeignKey("employees.id"), nullable=False)
    review_period    = Column(String(50), default="")
    rating           = Column(Integer, default=3)
    communication    = Column(Integer, default=3)
    technical_skills = Column(Integer, default=3)
    teamwork         = Column(Integer, default=3)
    leadership       = Column(Integer, default=3)
    comments         = Column(Text, default="")
    goals            = Column(Text, default="")
    review_date      = Column(Date, default=date.today)
    employee         = relationship("Employee", back_populates="performances")

# ── Helpers ───────────────────────────────────────────────────────────────────

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def verify_pw(pw: str, hashed: str) -> bool:
    return hash_pw(pw) == hashed

def authenticate(username: str, password: str):
    with Session() as db:
        u = db.query(User).filter_by(username=username, is_active=True).first()
        if u and verify_pw(password, u.password_hash):
            u.last_login = datetime.utcnow()
            db.commit()
            return {"id": u.id, "username": u.username, "role": u.role,
                    "employee_id": u.employee_id}
    return None

# ── CRUD wrappers ─────────────────────────────────────────────────────────────

def get_employees(active_only=True):
    with Session() as db:
        q = db.query(Employee)
        if active_only: q = q.filter_by(is_active=True)
        rows = q.all()
        db.expunge_all()
        return rows

def get_departments():
    with Session() as db:
        rows = db.query(Department).all()
        db.expunge_all()
        return rows

def create_employee_record(data: dict):
    with Session() as db:
        e = Employee(**data)
        db.add(e); db.commit(); db.refresh(e); db.expunge(e)
        return e

def update_employee_record(emp_id: int, data: dict):
    with Session() as db:
        e = db.query(Employee).get(emp_id)
        if e:
            for k, v in data.items(): setattr(e, k, v)
            db.commit()

def deactivate_employee(emp_id: int):
    with Session() as db:
        e = db.query(Employee).get(emp_id)
        if e: e.is_active = False; db.commit()

def get_all_attendance(days=30):
    start = date.today() - timedelta(days=days)
    with Session() as db:
        rows = db.query(Attendance).filter(Attendance.date >= start)\
                 .order_by(Attendance.date.desc()).all()
        db.expunge_all(); return rows

def mark_attendance(emp_id, status, check_in=None, check_out=None, notes=""):
    today = date.today()
    with Session() as db:
        existing = db.query(Attendance).filter_by(employee_id=emp_id, date=today).first()
        if existing:
            existing.status=status; existing.check_in=check_in
            existing.check_out=check_out; existing.notes=notes
        else:
            db.add(Attendance(employee_id=emp_id, date=today,
                              status=status, check_in=check_in,
                              check_out=check_out, notes=notes))
        db.commit()

def get_all_leaves():
    with Session() as db:
        rows = db.query(Leave).order_by(Leave.applied_on.desc()).all()
        db.expunge_all(); return rows

def create_leave_request(emp_id, leave_type, start, end, reason):
    with Session() as db:
        l = Leave(employee_id=emp_id, leave_type=leave_type,
                  start_date=start, end_date=end, reason=reason)
        db.add(l); db.commit()

def update_leave_status(leave_id, status):
    with Session() as db:
        l = db.query(Leave).get(leave_id)
        if l: l.status = status; db.commit()

def get_payroll(month, year):
    with Session() as db:
        rows = db.query(Payroll).filter_by(month=month, year=year).all()
        db.expunge_all(); return rows

def generate_payroll_for(emp_id, month, year):
    with Session() as db:
        existing = db.query(Payroll).filter_by(employee_id=emp_id,
                                                month=month, year=year).first()
        if existing: db.expunge(existing); return existing
        emp = db.query(Employee).get(emp_id)
        if not emp: return None
        basic = emp.salary / 12
        hra   = basic * 0.40; transport = 1500.0; medical = 1250.0
        tax   = basic * 0.20; net = basic + hra + transport + medical - tax
        p = Payroll(employee_id=emp_id, month=month, year=year,
                    basic_salary=round(basic,2), hra=round(hra,2),
                    transport=transport, medical=medical,
                    tax_deduction=round(tax,2), net_salary=round(net,2))
        db.add(p); db.commit(); db.refresh(p); db.expunge(p); return p

def get_performances():
    with Session() as db:
        rows = db.query(Performance).order_by(Performance.review_date.desc()).all()
        db.expunge_all(); return rows

def save_performance(data: dict):
    with Session() as db:
        p = Performance(**data); db.add(p); db.commit()

def dashboard_metrics():
    with Session() as db:
        total    = db.query(Employee).filter_by(is_active=True).count()
        present  = db.query(Attendance).filter_by(date=date.today(), status="present").count()
        pending  = db.query(Leave).filter_by(status="pending").count()
        depts    = db.query(Department).count()
        from sqlalchemy import func
        avg_sal  = db.query(func.avg(Employee.salary)).filter_by(is_active=True).scalar() or 0
        return {"total": total, "present": present, "pending_leaves": pending,
                "departments": depts, "avg_salary": round(avg_sal, 2),
                "att_rate": round(present/total*100 if total else 0, 1)}

# ── Init & Seed ───────────────────────────────────────────────────────────────

def init_db():
    Base.metadata.create_all(engine)
    with Session() as db:
        if db.query(User).count() == 0:
            _seed(db)

def _seed(db):
    depts = [Department(name=n, description=d) for n, d in [
        ("Engineering","Software & architecture"),
        ("Human Resources","Talent management"),
        ("Marketing","Brand & growth"),
        ("Finance","Financial analysis"),
        ("Operations","Business operations"),
    ]]
    for d in depts: db.add(d)
    db.flush()

    colors = ["#007BFF","#00C853","#FF6B6B","#FFC107","#9C27B0","#00BCD4","#FF5722","#607D8B"]
    emp_data = [
        ("EMP001","Alex","Morrison","alex.m@company.com","+1-555-0101","Senior Engineer",95000,0),
        ("EMP002","Sarah","Chen","sarah.c@company.com","+1-555-0102","HR Manager",75000,1),
        ("EMP003","Marcus","Williams","marcus.w@company.com","+1-555-0103","Marketing Lead",80000,2),
        ("EMP004","Priya","Patel","priya.p@company.com","+1-555-0104","Financial Analyst",70000,3),
        ("EMP005","James","O'Brien","james.ob@company.com","+1-555-0105","DevOps Engineer",90000,0),
        ("EMP006","Luna","Rodriguez","luna.r@company.com","+1-555-0106","UI/UX Designer",78000,0),
        ("EMP007","David","Kim","david.k@company.com","+1-555-0107","Product Manager",105000,0),
        ("EMP008","Aisha","Johnson","aisha.j@company.com","+1-555-0108","Data Scientist",98000,0),
    ]
    hire_dates = [date(2021,3,15),date(2020,7,1),date(2022,1,10),date(2021,9,20),
                  date(2019,5,5),date(2023,2,14),date(2020,11,30),date(2022,8,8)]
    emps = []
    for i,(eid,fn,ln,em,ph,pos,sal,di) in enumerate(emp_data):
        e = Employee(employee_id=eid, first_name=fn, last_name=ln, email=em,
                     phone=ph, position=pos, salary=sal, department_id=depts[di].id,
                     hire_date=hire_dates[i], avatar_color=colors[i])
        db.add(e); emps.append(e)
    db.flush()

    db.add(User(username="admin", password_hash=hash_pw("admin123"),
                role="admin", employee_id=emps[0].id))
    for e in emps[1:]:
        db.add(User(username=e.email.split("@")[0],
                    password_hash=hash_pw("emp123"),
                    role="employee", employee_id=e.id))
    db.flush()

    today = date.today()
    statuses = ["present","present","present","late","present","present","absent","present"]
    for idx, emp in enumerate(emps):
        for offset in range(30):
            d = today - timedelta(days=offset)
            if d.weekday() < 5:
                st_ = statuses[idx] if random.random() > 0.08 else "absent"
                db.add(Attendance(employee_id=emp.id, date=d,
                                  check_in="09:00" if st_!="absent" else None,
                                  check_out="18:00" if st_!="absent" else None,
                                  status=st_))

    leave_types = ["Annual Leave","Sick Leave","Personal Leave","Emergency Leave"]
    leave_statuses = ["approved","pending","rejected","approved","pending"]
    for i, emp in enumerate(emps[:5]):
        db.add(Leave(employee_id=emp.id, leave_type=leave_types[i%4],
                     start_date=today+timedelta(days=random.randint(1,10)),
                     end_date=today+timedelta(days=random.randint(11,20)),
                     reason="Personal reasons", status=leave_statuses[i%5]))

    for emp in emps:
        basic=emp.salary/12; hra=basic*0.40; tax=basic*0.20
        net=basic+hra+1500+1250-tax
        db.add(Payroll(employee_id=emp.id, month=today.month, year=today.year,
                       basic_salary=round(basic,2), hra=round(hra,2),
                       transport=1500, medical=1250, tax_deduction=round(tax,2),
                       net_salary=round(net,2), is_paid=random.choice([True,False])))

    periods = ["Q1 2025","Q2 2025","Q3 2025","Q4 2024"]
    for i, emp in enumerate(emps):
        db.add(Performance(employee_id=emp.id, review_period=periods[i%4],
                           rating=random.randint(3,5),
                           communication=random.randint(3,5),
                           technical_skills=random.randint(3,5),
                           teamwork=random.randint(3,5),
                           leadership=random.randint(2,5),
                           comments="Strong contributor with consistent delivery.",
                           goals="Expand technical scope and mentor junior members.",
                           review_date=today-timedelta(days=random.randint(10,90))))
    db.commit()
    print("✅ Database seeded.")
