"""
Initialize artefacts blueprint
"""

from flask import Blueprint

artefact_blueprint = Blueprint('artefacts', __name__)

#pylint: disable=wrong-import-position

from . import artefacts_routes

#pylint: enable=wrong-import-position
