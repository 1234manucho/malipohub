from datetime import datetime, timedelta
from decimal import Decimal
from extensions import db
from models import Company, User, Payee, Transaction
from services.payments_service import create_single_payment, approve_transaction
from services.scheduling_service import create_job, preflight, execute_job


def _seed(app):
    with app.app_context():
        c = Company(name="T")
        db.session.add(c)
        db.session.flush()
        u = User(company_id=c.id, email="a@b.c", full_name="U", role="admin")
        u.set_password("password123")
        db.session.add(u)
        db.session.flush()
        p = Payee(company_id=c.id, name="P", phone="254700000001", method="mpesa")
        db.session.add(p)
        db.session.commit()
        return c.id, u.id, p.id


def test_scheduled_payment_fires_and_settles(app):
    cid, uid, pid = _seed(app)
    with app.app_context():
        payee = Payee.query.get(pid)
        txn = create_single_payment(cid, uid, payee, Decimal("100"), "mpesa")
        # auto-queued (small amount)
        job = create_job(cid, uid, "single_payment", txn.id,
                         run_at=datetime.utcnow() + timedelta(minutes=5))
        ok, reason = preflight(job)
        assert ok is True, reason
        run = execute_job(job)
        assert run.status == "ok"
        assert Transaction.query.get(txn.id).status == "settled"


def test_preflight_pauses_unapproved_large_payment(app):
    cid, uid, pid = _seed(app)
    with app.app_context():
        payee = Payee.query.get(pid)
        txn = create_single_payment(cid, uid, payee, Decimal("100000"), "mpesa")
        # pending — needs approval
        job = create_job(cid, uid, "single_payment", txn.id,
                         run_at=datetime.utcnow() + timedelta(minutes=5))
        ok, reason = preflight(job)
        assert ok is False
        assert "approval" in reason.lower()