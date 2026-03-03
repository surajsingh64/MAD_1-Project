from flask import Blueprint

company_bp = Blueprint(
    "company",
    __name__,
    url_prefix="/company"
)

from . import routes