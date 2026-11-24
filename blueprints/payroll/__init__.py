from flask import Blueprint

payroll_bp = Blueprint("payroll", __name__, url_prefix="/payroll")

from blueprints.payroll import routes  # noqa: E402,F401
