from models import BulkBatch, Transaction
from services.payments_service import approve_batch, execute_transaction


def preflight(job):
    if job.job_type == "bulk_disbursement":
        batch = BulkBatch.query.get(job.ref_id)
        if not batch:
            return False, "Batch missing"
        if batch.status == "completed":
            return False, "Batch already completed"
        return True, "ok"
    if job.job_type == "single_payment":
        txn = Transaction.query.get(job.ref_id)
        if not txn:
            return False, "Transaction missing"
        if txn.status in ("settled", "cancelled"):
            return False, f"Already {txn.status}"
        if txn.status == "pending" and txn.approved_by is None:
            return False, "Awaiting approval"
        return True, "ok"
    return False, f"Unknown type {job.job_type}"


def fire(job):
    if job.job_type == "bulk_disbursement":
        batch = BulkBatch.query.get(job.ref_id)
        approve_batch(batch, approver_id=job.created_by)
        return f"Batch {batch.id} processed"
    if job.job_type == "single_payment":
        txn = Transaction.query.get(job.ref_id)
        execute_transaction(txn)
        return f"Txn {txn.reference} → {txn.status}"
    raise RuntimeError(f"Unknown job type {job.job_type}")