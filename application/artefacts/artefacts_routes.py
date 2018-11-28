"""
Define all routes for artefacts here. Don't put logic into routes.
"""
from flask import jsonify, request, make_response, current_app
from werkzeug.datastructures import MultiDict
from . import artefact_blueprint
from . import artefacts_controller


@artefact_blueprint.route('/artefacts/<string:artefact_id>', methods=['GET'])
def show(artefact_id):
    "Route to get a single artefact"
    params = {"id": artefact_id}
    response, status = artefacts_controller.show(params)
    return make_response(jsonify(response), status)


@artefact_blueprint.route('/artefacts', methods=['GET'])
def index():
    "Route to get several artefacts with filters"
    current_app.logger.info(request.args)
    params = request.args or MultiDict()
    current_app.logger.info(params)
    response, status = artefacts_controller.index(params)
    return make_response(jsonify(response), status)


@artefact_blueprint.route('/artefacts', methods=['POST'])
def create():
    "Route to create an artefact"
    params = request.json
    response, status = artefacts_controller.create(params)
    return make_response(jsonify(response), status)


@artefact_blueprint.route('/artefacts/<string:artefact_id>', methods=['PUT'])
def update(artefact_id):
    "Route to update an artefact"
    params = request.json
    params["id"] = artefact_id
    response, status = artefacts_controller.update(params)
    return make_response(jsonify(response), status)


@artefact_blueprint.route('/artefacts/<string:artefact_id>',
                          methods=['DELETE'])
def delete(artefact_id):
    "Route to delete an artefact"
    params = {"id": artefact_id}
    response, status = artefacts_controller.delete(params)
    return make_response(jsonify(response), status)
