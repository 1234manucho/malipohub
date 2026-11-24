from datetime import datetime
from decimal import Decimal
from extensions import db
from models import Employee, PayrollRun, Payslip, SalaryStructure


def _active_salary(employee: Employee):
    return (SalaryStructure.query
            .filter_by(employee_id=employee.id, active=True)
            .order_by(SalaryStructure.effective_from.desc()).first())


def _statutory(gross: Decimal):
    """Simplified — replace with graduated PAYE bands when ready."""
    nssf = min(gross * Decimal("0.06"), Decimal("2160"))
    shif = gross * Decimal("0.0275")
    housing = gross * Decimal("0.015")
    taxable = max(Decimal("0"), gross - nssf - shif - housing)
    paye = taxable * Decimal("0.10")  # placeholder flat 10%
    return paye, nssf, shif, housing


def generate_payroll(company_id, user_id, period: str, label: str = ""):
    employees = Employee.query.filter_by(company_id=company_id, status="active").all()
    run = PayrollRun(company_id=company_id, period=period, label=label or period,
                     created_by=user_id, status="draft")
    db.session.add(run)
    db.session.flush()

    total_gross, total_net = Decimal("0"), Decimal("0")
    for emp in employees:
        sal = _active_salary(emp)
        if not sal:
            continue
        gross = Decimal(str(sal.gross_salary)) + Decimal(str(sal.allowances or 0))
        paye, nssf, shif, housing = _statutory(gross)
        net = gross - paye - nssf - shif - housing
        db.session.add(Payslip(
            payroll_run_id=run.id, employee_id=emp.id,
            gross=gross, paye=paye, nssf=nssf, shif=shif,
            housing_levy=housing, net=net,
        ))
        total_gross += gross
        total_net += net

    run.total_gross = total_gross
    run.total_net = total_net
    db.session.commit()
    return run


def approve_payroll(run: PayrollRun, approver_id):
    run.status = "approved"
    run.approved_by = approver_id
    run.approved_at = datetime.utcnow()
    db.session.commit()
    return run


def mark_payroll_paid(run: PayrollRun):
    run.status = "paid"
    db.session.commit()
    return run