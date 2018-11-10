from flask import Blueprint
home_blueprint = Blueprint('home',__name__)

from . import home_routes