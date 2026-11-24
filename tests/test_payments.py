from decimal import Decimal
from extensions import db
from models import Company, User, Payee
from services.payments_service import (
    create_single_payment, approve_transaction, execute_transaction,
)


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


def test_small_payment_auto_queued(app):
    cid, uid, pid = _seed(app)
    with app.app_context():
        payee = Payee.query.get(pid)
        txn = create_single_payment(cid, uid, payee, Decimal("100"), "mpesa")
        assert txn.status == "queued"
        assert execute_transaction(txn) is True
        assert txn.status == "settled"


def test_large_payment_needs_approval(app):
    cid, uid, pid = _seed(app)
    with app.app_context():
        payee = Payee.query.get(pid)
        txn = create_single_payment(cid, uid, payee, Decimal("100000"), "mpesa")
        assert txn.status == "pending"
        approve_transaction(txn, uid)
        assert txn.status == "queued"
        assert execute_transaction(txn) is True