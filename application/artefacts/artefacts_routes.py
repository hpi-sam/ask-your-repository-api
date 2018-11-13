from . import artefacts_blueprint
from . import artefacts_controller
from flask import jsonify, request, make_response

@artefacts_blueprint.route('/artefacts/<string:type>/<string:id>', methods=['GET'])
def show(type,id):
    params = {"type": type, "id": id }
    response, status = artefacts_controller.show(params)
    return make_response(jsonify(response), status)


@artefacts_blueprint.route('/artefacts/<string:type>', methods=['POST'])
def create(type):
    params = request.json
    params["type"] = type
    response, status = artefacts_controller.create(params)
    return make_response(jsonify(response), status)

@artefacts_blueprint.route('/artefacts/<string:type>', methods=['GET'])
def index(type):
    params = request.json
    params["type"] = type
    response, status = artefacts_controller.index(params)
    return make_response(jsonify(response), status)

@artefacts_blueprint.route('/artefacts/<string:type>/<string:id>', methods=['PUT'])
def update(type, id):
    params = request.json
    params["type"] = type
    params["id"] = id
    response, status = artefacts_controller.update(params)
    return make_response(jsonify(response), status)


@artefacts_blueprint.route('/artefacts/<string:type>/<string:id>', methods=['DELETE'])
def delete(type, id):
    params = {"type": type, "id": id }
    response, status = artefacts_controller.delete(params)
    return make_response(jsonify(response), status)