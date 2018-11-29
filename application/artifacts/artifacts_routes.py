"""
Define all routes for artefacts here. Don't put logic into routes.
"""
from flask import jsonify, request, make_response, current_app
from werkzeug.datastructures import MultiDict
from . import artifact_blueprint
from . import artifacts_controller


@artifact_blueprint.route('/artifacts/<string:artifact_id>', methods=['GET'])
def show(artifact_id):
    "Route to get a single artifact"
    params = {"id": artifact_id}
    response, status = artifacts_controller.show(params)
    return make_response(jsonify(response), status)


@artifact_blueprint.route('/artifacts', methods=['GET'])
def index():
    "Route to get several artifacts with filters"
    params = request.args or MultiDict()
    response, status = artifacts_controller.index(params)
    return make_response(jsonify(response), status)


@artifact_blueprint.route('/artifacts', methods=['POST'])
def create():
    "Route to create an artifact"
    params = request.json
    response, status = artifacts_controller.create(params)
    return make_response(jsonify(response), status)


@artifact_blueprint.route('/artifacts/<string:artifact_id>', methods=['PUT'])
def update(artifact_id):
    "Route to update an artifact"
    params = request.json
    params["id"] = artifact_id
    response, status = artifacts_controller.update(params)
    return make_response(jsonify(response), status)


@artifact_blueprint.route('/artifacts/<string:artifact_id>',
                          methods=['DELETE'])
def delete(artifact_id):
    "Route to delete an artifact"
    params = {"id": artifact_id}
    response, status = artifacts_controller.delete(params)
    return make_response(jsonify(response), status)
