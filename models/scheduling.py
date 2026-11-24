from datetime import datetime
from extensions import db


class ScheduledJob(db.Model):
    __tablename__ = "scheduled_jobs"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False, index=True)
    job_type = db.Column(db.String(30), nullable=False)
    ref_id = db.Column(db.Integer)
    label = db.Column(db.String(120))
    run_at = db.Column(db.DateTime, nullable=False, index=True)
    recurrence = db.Column(db.String(20), default="once")
    status = db.Column(db.String(20), default="scheduled")
    preflight_notified = db.Column(db.Boolean, default=False)
    last_error = db.Column(db.String(255))
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    runs = db.relationship("JobRun", backref="job", lazy=True, cascade="all, delete-orphan")


class JobRun(db.Model):
    __tablename__ = "job_runs"
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("scheduled_jobs.id"), nullable=False, index=True)
    status = db.Column(db.String(20), default="started")
    message = db.Column(db.String(255))
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    finished_at = db.Column(db.DateTime)


class Notification(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    channel = db.Column(db.String(20), default="in_app")
    subject = db.Column(db.String(160))
    body = db.Column(db.Text)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)