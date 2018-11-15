"""
Define all routes for artefacts here. Don't put logic into routes.
"""
from flask import jsonify, request, make_response
from . import artefact_blueprint
from . import artefacts_controller


@artefact_blueprint.route('/artefacts/<string:artefact_type>/<string:artefact_id>', methods=['GET'])
def show(artefact_type, artefact_id):
    "Route to get a single artefact"
    params = {"type": artefact_type, "id": artefact_id}
    response, status = artefacts_controller.show(params)
    return make_response(jsonify(response), status)


@artefact_blueprint.route('/artefacts/<string:artefact_type>', methods=['GET'])
def index(artefact_type):
    "Route to get several artefacts with filters"
    params = request.json or {}
    params["type"] = artefact_type
    response, status = artefacts_controller.index(params)
    return make_response(jsonify(response), status)


@artefact_blueprint.route('/artefacts/<string:artefact_type>', methods=['POST'])
def create(artefact_type):
    "Route to create an artefact"
    params = request.json
    params["type"] = artefact_type
    response, status = artefacts_controller.create(params)
    return make_response(jsonify(response), status)


@artefact_blueprint.route('/artefacts/<string:artefact_type>/<string:artefact_id>', methods=['PUT'])
def update(artefact_type, artefact_id):
    "Route to update an artefact"
    params = request.json
    params["type"] = artefact_type
    params["id"] = artefact_id
    response, status = artefacts_controller.update(params)
    return make_response(jsonify(response), status)


@artefact_blueprint.route('/artefacts/<string:artefact_type>/<string:artefact_id>',
                          methods=['DELETE'])
def delete(artefact_type, artefact_id):
    "Route to delete an artefact"
    params = {"type": artefact_type, "id": artefact_id}
    response, status = artefacts_controller.delete(params)
    return make_response(jsonify(response), status)
