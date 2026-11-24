from flask import render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from forms import ScheduleForm
from models import ScheduledJob
from services.scheduling_service import create_job, execute_job
from blueprints.scheduling import scheduling_bp
from utils.decorators import company_required, role_required


@scheduling_bp.route("/")
@login_required
@company_required
def index():
    rows = (ScheduledJob.query.filter_by(company_id=current_user.company_id)
            .order_by(ScheduledJob.run_at.asc()).all())
    return render_template("scheduling/jobs.html", jobs=rows)


@scheduling_bp.route("/new", methods=["GET", "POST"])
@login_required
@company_required
@role_required("admin", "finance")
def new_job():
    form = ScheduleForm()
    if form.validate_on_submit():
        create_job(company_id=current_user.company_id, user_id=current_user.id,
                   job_type=form.job_type.data, ref_id=form.ref_id.data,
                   run_at=form.run_at.data, recurrence=form.recurrence.data,
                   label=form.label.data or "")
        flash("Job scheduled.", "success")
        return redirect(url_for("scheduling.index"))
    return render_template("scheduling/job_form.html", form=form)


@scheduling_bp.route("/<int:jid>/run-now", methods=["POST"])
@login_required
@company_required
@role_required("admin", "finance")
def run_now(jid):
    job = ScheduledJob.query.get_or_404(jid)
    if job.company_id != current_user.company_id:
        abort(403)
    run = execute_job(job)
    flash(f"Job executed: {run.status} — {run.message or ''}",
          "success" if run.status == "ok" else "warning")
    return redirect(url_for("scheduling.index"))