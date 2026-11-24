"""Daraja (M-Pesa) client. Wire live calls here when credentials are ready."""
import base64
import requests
from flask import current_app


def _base_url():
    return ("https://sandbox.safaricom.co.ke"
            if current_app.config["MPESA_ENV"] == "sandbox"
            else "https://api.safaricom.co.ke")


def get_token():
    key = current_app.config["MPESA_CONSUMER_KEY"]
    secret = current_app.config["MPESA_CONSUMER_SECRET"]
    if not key or not secret:
        raise RuntimeError("M-Pesa credentials not configured")
    auth = base64.b64encode(f"{key}:{secret}".encode()).decode()
    r = requests.get(f"{_base_url()}/oauth/v1/generate?grant_type=client_credentials",
                     headers={"Authorization": f"Basic {auth}"}, timeout=20)
    r.raise_for_status()
    return r.json()["access_token"]


def disburse(txn):
    raise RuntimeError("Live M-Pesa disbursement not yet implemented")
