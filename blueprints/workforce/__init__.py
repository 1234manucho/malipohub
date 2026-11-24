from flask import Blueprint

workforce_bp = Blueprint("workforce", __name__, url_prefix="/workforce")

from blueprints.workforce import routes  # noqa: E402,F401
