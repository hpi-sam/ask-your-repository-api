from . import artefacts_blueprint
from . import artefacts_controller
from flask import jsonify, request

@artefacts_blueprint.route('/artefacts', methods=['POST'])
def create():
    params = request.json  
    return jsonify(artefacts_controller.create(params))

@artefacts_blueprint.route('/artefacts', methods=['GET'])
def index():
    params = request.json
    return jsonify(artefacts_controller.index(params))