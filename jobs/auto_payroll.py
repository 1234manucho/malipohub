from models import PayrollRun
from services.payroll_service import mark_payroll_paid


def preflight(job):
    run = PayrollRun.query.get(job.ref_id)
    if not run:
        return False, "Payroll run missing"
    if run.status in ("paid", "cancelled"):
        return False, f"Payroll already {run.status}"
    if run.status not in ("approved", "draft"):
        return False, f"Payroll status {run.status}"
    return True, "ok"


def fire(job):
    run = PayrollRun.query.get(job.ref_id)
    mark_payroll_paid(run)
    return f"Payroll {run.period} marked paid"