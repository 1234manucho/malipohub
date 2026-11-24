from datetime import datetime
from extensions import db
from models import ScheduledJob, JobRun
from services.notifications_service import notify_company_admins
from jobs import auto_payroll, auto_disburse, auto_reorder

DISPATCH = {
    "payroll": auto_payroll,
    "bulk_disbursement": auto_disburse,
    "single_payment": auto_disburse,
    "reorder": auto_reorder,
}


def create_job(company_id, user_id, job_type, ref_id, run_at,
               recurrence="once", label=""):
    job = ScheduledJob(company_id=company_id, job_type=job_type, ref_id=ref_id,
                       run_at=run_at, recurrence=recurrence, label=label,
                       created_by=user_id)
    db.session.add(job)
    db.session.commit()
    return job


def preflight(job: ScheduledJob) -> tuple[bool, str]:
    module = DISPATCH.get(job.job_type)
    if not module:
        return False, "Unknown job type"
    return module.preflight(job)


def execute_job(job: ScheduledJob) -> JobRun:
    run = JobRun(job_id=job.id, status="started")
    db.session.add(run)
    db.session.commit()

    ok, reason = preflight(job)
    if not ok:
        run.status = "paused"
        run.message = reason
        run.finished_at = datetime.utcnow()
        job.status = "paused"
        job.last_error = reason
        db.session.commit()
        notify_company_admins(job.company_id, "Scheduled job paused",
                              f"{job.job_type}#{job.ref_id}: {reason}")
        return run

    try:
        module = DISPATCH[job.job_type]
        message = module.fire(job)
        run.status = "ok"
        run.message = (message or "ok")[:255]
        run.finished_at = datetime.utcnow()
        job.status = "done"
    except Exception as exc:
        run.status = "failed"
        run.message = str(exc)[:250]
        run.finished_at = datetime.utcnow()
        job.status = "failed"
        job.last_error = run.message
    db.session.commit()
    return run


def notify_preflight(job: ScheduledJob):
    ok, reason = preflight(job)
    notify_company_admins(
        job.company_id, "Scheduled job in 24h",
        f"Job {job.job_type}#{job.ref_id} will fire at {job.run_at}.\nPreflight: {reason}",
    )
    job.preflight_notified = True
    db.session.commit()