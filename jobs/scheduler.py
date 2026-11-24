from datetime import datetime, timedelta
from apscheduler.triggers.date import DateTrigger
from sqlalchemy.exc import OperationalError, ProgrammingError

from extensions import scheduler
from models import ScheduledJob
from services.scheduling_service import execute_job, notify_preflight


def _job_runner(app, job_id):
    with app.app_context():
        job = ScheduledJob.query.get(job_id)
        if job and job.status == "scheduled":
            execute_job(job)


def _preflight_runner(app, job_id):
    with app.app_context():
        job = ScheduledJob.query.get(job_id)
        if job and job.status == "scheduled" and not job.preflight_notified:
            notify_preflight(job)


def schedule_job(app, job: ScheduledJob):
    scheduler.add_job(
        _job_runner, DateTrigger(run_date=job.run_at),
        args=[app, job.id], id=f"job-{job.id}", replace_existing=True,
    )
    preflight_at = job.run_at - timedelta(hours=24)
    if preflight_at > datetime.utcnow():
        scheduler.add_job(
            _preflight_runner, DateTrigger(run_date=preflight_at),
            args=[app, job.id], id=f"preflight-{job.id}", replace_existing=True,
        )


def load_pending_jobs(app):
    """Safe to call even before migrations/init-db have run."""
    with app.app_context():
        try:
            now = datetime.utcnow()
            pending = ScheduledJob.query.filter(
                ScheduledJob.status == "scheduled",
                ScheduledJob.run_at > now,
            ).all()
            for job in pending:
                schedule_job(app, job)
            app.logger.info("Loaded %d pending scheduled jobs.", len(pending))
        except (OperationalError, ProgrammingError) as exc:
            app.logger.warning(
                "Scheduled jobs table not available yet (%s). "
                "Run `flask --app app init-db` to create tables.", exc
            )