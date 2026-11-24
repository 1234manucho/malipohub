from datetime import datetime
from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from forms import TaskForm
from models import Attendance, Employee, Task
from blueprints.workforce import workforce_bp
from utils.decorators import company_required


@workforce_bp.route("/attendance")
@login_required
@company_required
def attendance():
    rows = (Attendance.query.filter_by(company_id=current_user.company_id)
            .order_by(Attendance.created_at.desc()).limit(100).all())
    return render_template("workforce/attendance.html", rows=rows)


@workforce_bp.route("/attendance/<int:eid>/clockin", methods=["POST"])
@login_required
@company_required
def clockin(eid):
    emp = Employee.query.get_or_404(eid)
    if emp.company_id != current_user.company_id:
        return redirect(url_for("workforce.attendance"))
    db.session.add(Attendance(company_id=current_user.company_id,
                              employee_id=emp.id, check_in=datetime.utcnow()))
    db.session.commit()
    flash("Clocked in.", "success")
    return redirect(url_for("workforce.attendance"))


@workforce_bp.route("/attendance/<int:aid>/clockout", methods=["POST"])
@login_required
@company_required
def clockout(aid):
    att = Attendance.query.get_or_404(aid)
    if att.company_id != current_user.company_id:
        return redirect(url_for("workforce.attendance"))
    att.check_out = datetime.utcnow()
    if att.check_in:
        att.hours_worked = round((att.check_out - att.check_in).total_seconds() / 3600, 2)
    db.session.commit()
    flash("Clocked out.", "success")
    return redirect(url_for("workforce.attendance"))


@workforce_bp.route("/tasks", methods=["GET", "POST"])
@login_required
@company_required
def tasks():
    form = TaskForm()
    form.employee_id.choices = [(0, "— unassigned —")] + [
        (e.id, e.full_name) for e in Employee.query.filter_by(company_id=current_user.company_id).all()
    ]
    if form.validate_on_submit():
        db.session.add(Task(
            company_id=current_user.company_id,
            employee_id=form.employee_id.data or None,
            title=form.title.data, description=form.description.data,
            due_on=form.due_on.data, created_by=current_user.id,
        ))
        db.session.commit()
        flash("Task created.", "success")
        return redirect(url_for("workforce.tasks"))
    rows = (Task.query.filter_by(company_id=current_user.company_id)
            .order_by(Task.created_at.desc()).all())
    return render_template("workforce/tasks.html", form=form, tasks=rows)