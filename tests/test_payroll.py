from extensions import db
from models import Company, User, Employee, SalaryStructure
from services.payroll_service import generate_payroll


def _seed(app):
    with app.app_context():
        c = Company(name="T")
        db.session.add(c)
        db.session.flush()
        u = User(company_id=c.id, email="a@b.c", full_name="U", role="admin")
        u.set_password("password123")
        db.session.add(u)
        db.session.flush()
        emp = Employee(company_id=c.id, full_name="E", status="active")
        db.session.add(emp)
        db.session.flush()
        db.session.add(SalaryStructure(employee_id=emp.id, gross_salary=50000))
        db.session.commit()
        return c.id, u.id


def test_payroll_run_totals(app):
    cid, uid = _seed(app)
    with app.app_context():
        run = generate_payroll(cid, uid, "2026-03")
        assert run.total_gross > 0
        assert run.total_net > 0
        assert len(run.payslips) == 1
        assert run.payslips[0].net <= run.payslips[0].gross