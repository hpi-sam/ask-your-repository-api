"""
Initialize artifacts blueprint
"""

from flask import Blueprint

artifact_blueprint = Blueprint('artifacts', __name__)

#pylint: disable=wrong-import-position

from . import artifacts_routes

#pylint: enable=wrong-import-position
