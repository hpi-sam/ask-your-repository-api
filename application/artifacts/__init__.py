"""
Initialize artefacts blueprint
"""

from flask import Blueprint

artifact_blueprint = Blueprint('artefacts', __name__)

#pylint: disable=wrong-import-position

from . import artifacts_routes

#pylint: enable=wrong-import-position
