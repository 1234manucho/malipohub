from datetime import datetime, date
from extensions import db


class Employee(db.Model):
    __tablename__ = "employees"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    kra_pin = db.Column(db.String(20))
    nssf_no = db.Column(db.String(20))
    shif_no = db.Column(db.String(20))
    bank_account = db.Column(db.String(50))
    bank_name = db.Column(db.String(80))
    department = db.Column(db.String(80))
    position = db.Column(db.String(80))
    employment_type = db.Column(db.String(20), default="permanent")
    status = db.Column(db.String(20), default="active")
    hired_on = db.Column(db.Date, default=date.today)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    salaries = db.relationship("SalaryStructure", backref="employee", lazy=True, cascade="all, delete-orphan")
    payslips = db.relationship("Payslip", backref="employee", lazy=True)


class SalaryStructure(db.Model):
    __tablename__ = "salary_structures"
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False, index=True)
    gross_salary = db.Column(db.Numeric(12, 2), nullable=False)
    allowances = db.Column(db.Numeric(12, 2), default=0)
    effective_from = db.Column(db.Date, default=date.today)
    active = db.Column(db.Boolean, default=True)


class PayrollRun(db.Model):
    __tablename__ = "payroll_runs"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False, index=True)
    period = db.Column(db.String(20), nullable=False)
    label = db.Column(db.String(120))
    total_gross = db.Column(db.Numeric(14, 2), default=0)
    total_net = db.Column(db.Numeric(14, 2), default=0)
    status = db.Column(db.String(20), default="draft")
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    approved_at = db.Column(db.DateTime)

    payslips = db.relationship("Payslip", backref="payroll_run", lazy=True, cascade="all, delete-orphan")


class Payslip(db.Model):
    __tablename__ = "payslips"
    id = db.Column(db.Integer, primary_key=True)
    payroll_run_id = db.Column(db.Integer, db.ForeignKey("payroll_runs.id"), nullable=False, index=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("employees.id"), nullable=False, index=True)
    gross = db.Column(db.Numeric(12, 2), default=0)
    paye = db.Column(db.Numeric(12, 2), default=0)
    nssf = db.Column(db.Numeric(12, 2), default=0)
    shif = db.Column(db.Numeric(12, 2), default=0)
    housing_levy = db.Column(db.Numeric(12, 2), default=0)
    other_deductions = db.Column(db.Numeric(12, 2), default=0)
    net = db.Column(db.Numeric(12, 2), default=0)
    transaction_id = db.Column(db.Integer, db.ForeignKey("transactions.id"))