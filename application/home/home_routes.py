"""
Defines the home route
"""

from flask import jsonify
from . import home_blueprint
from . import home_controller

@home_blueprint.route('/', methods=['GET'])
def index():
    """ Returns a json object of service information"""
    return jsonify(home_controller.index())
