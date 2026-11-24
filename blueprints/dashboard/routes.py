from datetime import datetime, timedelta
from flask import render_template
from flask_login import login_required, current_user
from sqlalchemy import func

from extensions import db
from models import Transaction, Employee, Item, ScheduledJob
from blueprints.dashboard import dashboard_bp


@dashboard_bp.route("/")
@login_required
def index():
    company_id = current_user.company_id
    since = datetime.utcnow() - timedelta(days=30)

    spend_30d = (db.session.query(func.coalesce(func.sum(Transaction.amount), 0))
                 .filter(Transaction.company_id == company_id,
                         Transaction.status == "settled",
                         Transaction.settled_at >= since).scalar() or 0)
    pending = Transaction.query.filter_by(company_id=company_id, status="queued").count()
    employees = Employee.query.filter_by(company_id=company_id, status="active").count()
    low_stock = Item.query.filter(Item.company_id == company_id,
                                  Item.stock_qty <= Item.reorder_level).count()

    recent_txns = (Transaction.query.filter_by(company_id=company_id)
                   .order_by(Transaction.created_at.desc()).limit(10).all())
    upcoming_jobs = (ScheduledJob.query.filter_by(company_id=company_id, status="scheduled")
                     .order_by(ScheduledJob.run_at.asc()).limit(5).all())

    return render_template("dashboard/index.html",
                           spend_30d=spend_30d, pending=pending,
                           employees=employees, low_stock=low_stock,
                           recent_txns=recent_txns, upcoming_jobs=upcoming_jobs)