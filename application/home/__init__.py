"""
Initialize home blueprint
"""
from flask import Blueprint

home_blueprint = Blueprint('home', __name__)

#pylint: disable=wrong-import-position

from . import home_routes

#pylint: disable=wrong-import-position
