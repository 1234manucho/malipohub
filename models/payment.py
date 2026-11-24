from datetime import datetime
from extensions import db
from utils.references import generate as gen_ref


class Account(db.Model):
    __tablename__ = "accounts"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    account_type = db.Column(db.String(30), default="internal")
    balance = db.Column(db.Numeric(14, 2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    transactions = db.relationship("Transaction", backref="account", lazy=True)


class Payee(db.Model):
    __tablename__ = "payees"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    account_number = db.Column(db.String(50))
    bank_name = db.Column(db.String(80))
    method = db.Column(db.String(20), default="mpesa")
    tag = db.Column(db.String(40))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class BulkBatch(db.Model):
    __tablename__ = "bulk_batches"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False, index=True)
    label = db.Column(db.String(120), nullable=False)
    total_amount = db.Column(db.Numeric(14, 2), default=0)
    status = db.Column(db.String(20), default="draft")
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    transactions = db.relationship("Transaction", backref="batch", lazy=True)


class Transaction(db.Model):
    __tablename__ = "transactions"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False, index=True)
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"))
    batch_id = db.Column(db.Integer, db.ForeignKey("bulk_batches.id"), index=True)
    payee_id = db.Column(db.Integer, db.ForeignKey("payees.id"))
    amount = db.Column(db.Numeric(14, 2), nullable=False)
    fee = db.Column(db.Numeric(10, 2), default=0)
    recipient = db.Column(db.String(100))
    recipient_name = db.Column(db.String(120))
    method = db.Column(db.String(20), default="mpesa")
    status = db.Column(db.String(20), default="pending")
    reference = db.Column(db.String(50), unique=True, default=lambda: gen_ref("TXN"))
    external_ref = db.Column(db.String(80))
    failure_reason = db.Column(db.String(255))
    description = db.Column(db.String(255))
    approved_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    approved_at = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    settled_at = db.Column(db.DateTime)


class Approval(db.Model):
    __tablename__ = "approvals"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False, index=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey("transactions.id"))
    batch_id = db.Column(db.Integer, db.ForeignKey("bulk_batches.id"))
    requested_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    approver_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    status = db.Column(db.String(20), default="pending")
    comment = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    decided_at = db.Column(db.DateTime)