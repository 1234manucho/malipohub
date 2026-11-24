import csv
import io
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

from extensions import db
from forms import PayeeForm, PaymentForm, BulkUploadForm
from models import Payee, Transaction, BulkBatch
from services.payments_service import (
    create_single_payment, approve_transaction, approve_batch,
    execute_transaction, create_bulk_batch,
)
from blueprints.payments import payments_bp
from utils.decorators import company_required, role_required


@payments_bp.route("/payees", methods=["GET", "POST"])
@login_required
@company_required
def payees():
    form = PayeeForm()
    if form.validate_on_submit():
        db.session.add(Payee(
            company_id=current_user.company_id, name=form.name.data,
            phone=form.phone.data, account_number=form.account_number.data,
            bank_name=form.bank_name.data, method=form.method.data,
            tag=form.tag.data,
        ))
        db.session.commit()
        flash("Payee saved.", "success")
        return redirect(url_for("payments.payees"))
    items = Payee.query.filter_by(company_id=current_user.company_id).order_by(Payee.name).all()
    return render_template("payments/payees.html", form=form, payees=items)


@payments_bp.route("/single", methods=["GET", "POST"])
@login_required
@company_required
def single():
    form = PaymentForm()
    rows = Payee.query.filter_by(company_id=current_user.company_id).all()
    form.payee_id.choices = [(p.id, f"{p.name} · {p.phone or p.account_number}") for p in rows]

    if form.validate_on_submit():
        payee = Payee.query.get(form.payee_id.data)
        if not payee or payee.company_id != current_user.company_id:
            abort(400)
        txn = create_single_payment(current_user.company_id, current_user.id,
                                    payee, form.amount.data, form.method.data,
                                    form.description.data or "")
        flash(f"Payment {txn.reference} created ({txn.status}).", "success")
        return redirect(url_for("payments.history"))
    return render_template("payments/single.html", form=form)


@payments_bp.route("/bulk", methods=["GET", "POST"])
@login_required
@company_required
def bulk():
    form = BulkUploadForm()
    if form.validate_on_submit():
        upload = request.files.get("csv_file")
        if not upload or not upload.filename:
            flash("Attach a CSV (name, phone_or_account, amount, method, reference).", "danger")
            return render_template("payments/bulk.html", form=form)
        stream = io.StringIO(upload.stream.read().decode("utf-8-sig"))
        reader = csv.DictReader(stream)
        rows = []
        for row in reader:
            try:
                rows.append({
                    "name": row["name"].strip(),
                    "phone_or_account": row["phone_or_account"].strip(),
                    "amount": float(row["amount"]),
                    "method": (row.get("method") or "mpesa").strip().lower(),
                    "reference": (row.get("reference") or "").strip(),
                })
            except (KeyError, ValueError):
                flash(f"Skipping malformed row: {row}", "warning")
        if not rows:
            flash("No valid rows found.", "danger")
            return render_template("payments/bulk.html", form=form)
        batch = create_bulk_batch(current_user.company_id, current_user.id,
                                  form.label.data, rows)
        flash(f"Batch '{batch.label}' created ({len(rows)} items). Awaiting approval.", "success")
        return redirect(url_for("payments.batches"))
    return render_template("payments/bulk.html", form=form)


@payments_bp.route("/history")
@login_required
@company_required
def history():
    page = request.args.get("page", 1, type=int)
    q = (Transaction.query.filter_by(company_id=current_user.company_id)
         .order_by(Transaction.created_at.desc()))
    pagination = q.paginate(page=page, per_page=25, error_out=False)
    return render_template("payments/history.html", pagination=pagination)


@payments_bp.route("/batches")
@login_required
@company_required
def batches():
    rows = (BulkBatch.query.filter_by(company_id=current_user.company_id)
            .order_by(BulkBatch.created_at.desc()).all())
    return render_template("payments/batches.html", batches=rows)


@payments_bp.route("/batches/<int:bid>/approve", methods=["POST"])
@login_required
@company_required
@role_required("admin", "finance", "approver")
def approve_batch_route(bid):
    batch = BulkBatch.query.get_or_404(bid)
    if batch.company_id != current_user.company_id:
        abort(403)
    approve_batch(batch, current_user.id)
    flash("Batch processed.", "success")
    return redirect(url_for("payments.batches"))


@payments_bp.route("/transactions/<int:tid>/approve", methods=["POST"])
@login_required
@company_required
@role_required("admin", "finance", "approver")
def approve_txn(tid):
    txn = Transaction.query.get_or_404(tid)
    if txn.company_id != current_user.company_id:
        abort(403)
    approve_transaction(txn, current_user.id)
    flash("Approved and queued.", "success")
    return redirect(url_for("payments.history"))


@payments_bp.route("/transactions/<int:tid>/execute", methods=["POST"])
@login_required
@company_required
def execute_txn(tid):
    txn = Transaction.query.get_or_404(tid)
    if txn.company_id != current_user.company_id:
        abort(403)
    ok = execute_transaction(txn)
    flash("Settled." if ok else "Failed to settle.", "success" if ok else "danger")
    return redirect(url_for("payments.history"))