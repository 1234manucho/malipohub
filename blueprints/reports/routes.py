import csv
import io
from datetime import datetime, timedelta
from flask import render_template, Response
from flask_login import login_required, current_user

from models import Transaction
from blueprints.reports import reports_bp
from utils.decorators import company_required


@reports_bp.route("/")
@login_required
@company_required
def index():
    return render_template("reports/index.html")


@reports_bp.route("/cashflow.csv")
@login_required
@company_required
def cashflow_csv():
    since = datetime.utcnow() - timedelta(days=90)
    rows = (Transaction.query
            .filter(Transaction.company_id == current_user.company_id,
                    Transaction.created_at >= since)
            .order_by(Transaction.created_at.asc()).all())
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["date", "reference", "recipient", "method", "amount", "fee", "status"])
    for t in rows:
        w.writerow([t.created_at.isoformat(), t.reference, t.recipient,
                    t.method, t.amount, t.fee, t.status])
    return Response(buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=cashflow.csv"})