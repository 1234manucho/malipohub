import secrets
from datetime import datetime


def generate(prefix="REF"):
    return f"{prefix}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(3).upper()}"