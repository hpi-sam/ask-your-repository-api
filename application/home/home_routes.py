from . import home_blueprint
from . import home_controller
from flask import jsonify, request

@home_blueprint.route('/', methods=['GET'])
def index():
    params = jsonify
    return jsonify(home_controller.index(params))
