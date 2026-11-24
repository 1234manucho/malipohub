from datetime import datetime
from decimal import Decimal
from flask import current_app

from extensions import db
from models import BulkBatch, Transaction, Approval, Payee
from services.intergrations import mpesa, bank
from services.notifications_service import notify_company_admins

APPROVAL_THRESHOLD = Decimal("50000")


def _fee_for(method: str) -> Decimal:
    return Decimal(str(current_app.config["FEE_MPESA" if method == "mpesa" else "FEE_BANK"]))


def _needs_approval(amount: Decimal) -> bool:
    return amount >= APPROVAL_THRESHOLD


def create_single_payment(company_id, user_id, payee: Payee, amount, method, description=""):
    amt = Decimal(str(amount))
    txn = Transaction(
        company_id=company_id, payee_id=payee.id,
        amount=amt, fee=_fee_for(method),
        recipient=payee.phone or payee.account_number,
        recipient_name=payee.name, method=method,
        status="pending", description=description, created_by=user_id,
    )
    db.session.add(txn)
    db.session.flush()

    if _needs_approval(amt):
        db.session.add(Approval(company_id=company_id, transaction_id=txn.id,
                                requested_by=user_id, status="pending"))
    else:
        txn.status = "queued"
    db.session.commit()
    return txn


def approve_transaction(txn: Transaction, approver_id):
    txn.approved_by = approver_id
    txn.approved_at = datetime.utcnow()
    txn.status = "queued"
    Approval.query.filter_by(transaction_id=txn.id, status="pending").update(
        {"status": "approved", "approver_id": approver_id, "decided_at": datetime.utcnow()}
    )
    db.session.commit()


def execute_transaction(txn: Transaction) -> bool:
    if txn.status not in ("queued", "processing", "pending"):
        return False
    txn.status = "processing"
    db.session.commit()

    try:
        if current_app.config["PAYMENTS_SIMULATE"]:
            ok, ref = True, f"SIM-{txn.reference}"
        elif txn.method == "mpesa":
            ok, ref = mpesa.disburse(txn)
        elif txn.method == "bank":
            ok, ref = bank.disburse(txn)
        else:
            ok, ref = False, None

        if ok:
            txn.status = "settled"
            txn.settled_at = datetime.utcnow()
            txn.external_ref = ref
        else:
            txn.status = "failed"
            txn.failure_reason = "Provider rejected"
        db.session.commit()
        return ok
    except Exception as exc:
        txn.status = "failed"
        txn.failure_reason = str(exc)[:250]
        db.session.commit()
        notify_company_admins(txn.company_id, "Payment failed", f"{txn.reference}: {exc}")
        return False


def create_bulk_batch(company_id, user_id, label, rows):
    batch = BulkBatch(company_id=company_id, label=label, created_by=user_id,
                      status="pending_approval")
    db.session.add(batch)
    db.session.flush()

    total = Decimal("0")
    for r in rows:
        amount = Decimal(str(r["amount"]))
        method = r.get("method", "mpesa")
        payee = Payee.query.filter_by(company_id=company_id, phone=r["phone_or_account"]).first()
        db.session.add(Transaction(
            company_id=company_id, batch_id=batch.id,
            payee_id=payee.id if payee else None,
            amount=amount, fee=_fee_for(method),
            recipient=r["phone_or_account"], recipient_name=r["name"],
            method=method, status="queued",
            description=r.get("reference", ""), created_by=user_id,
        ))
        total += amount

    batch.total_amount = total
    db.session.add(Approval(company_id=company_id, batch_id=batch.id,
                            requested_by=user_id, status="pending"))
    db.session.commit()
    return batch


def approve_batch(batch: BulkBatch, approver_id):
    batch.status = "processing"
    db.session.commit()
    for txn in list(batch.transactions):
        if txn.status != "settled":
            execute_transaction(txn)
    batch.status = "completed" if all(t.status == "settled" for t in batch.transactions) else "failed"
    batch.completed_at = datetime.utcnow()
    Approval.query.filter_by(batch_id=batch.id, status="pending").update(
        {"status": "approved", "approver_id": approver_id, "decided_at": datetime.utcnow()}
    )
    db.session.commit()
    return batch.status == "completed"