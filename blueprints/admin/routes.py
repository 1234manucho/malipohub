from flask import render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from extensions import db
from models import User, ActivityLog
from blueprints.admin import admin_bp
from utils.decorators import company_required, role_required

VALID_ROLES = {"admin", "finance", "approver", "manager", "viewer", "employee"}


@admin_bp.route("/users")
@login_required
@company_required
@role_required("admin")
def users():
    rows = (User.query.filter_by(company_id=current_user.company_id)
            .order_by(User.created_at.desc()).all())
    return render_template("admin/users.html", users=rows)


@admin_bp.route("/users/<int:uid>/role/<string:role>", methods=["POST"])
@login_required
@company_required
@role_required("admin")
def change_role(uid, role):
    user = User.query.get_or_404(uid)
    if user.company_id != current_user.company_id:
        abort(403)
    if role not in VALID_ROLES:
        abort(400)
    user.role = role
    db.session.commit()
    flash(f"Role updated to {role}.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/audit")
@login_required
@company_required
@role_required("admin")
def audit():
    rows = (ActivityLog.query.filter_by(company_id=current_user.company_id)
            .order_by(ActivityLog.created_at.desc()).limit(200).all())
    return render_template("admin/audit.html", logs=rows)