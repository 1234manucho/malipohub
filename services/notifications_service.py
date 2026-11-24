from datetime import datetime
from extensions import db
from models import Notification


def notify(company_id, user_id, subject, body, channel="in_app"):
    n = Notification(
        company_id=company_id, user_id=user_id, channel=channel,
        subject=subject, body=body, created_at=datetime.utcnow(),
    )
    db.session.add(n)
    db.session.commit()
    return n


def notify_company_admins(company_id, subject, body):
    from models import User
    admins = User.query.filter_by(company_id=company_id, role="admin").all()
    for a in admins:
        notify(company_id, a.id, subject, body)
    return admins