"""
Handles logic for presentation http requests.
Uses socket.io to communicate with the frontend
"""

from flask import current_app, request
from webargs import fields
from webargs.flaskparser import parser
from application.models.artifact import Artifact
from application.controllers.error_handling.es_connection import check_es_connection
from .application_controller import ApplicationController

def create_args():
    """Defines and validates params for index"""
    return {
        "file_ids": fields.List(fields.String(), load_from="image_ids")
    }

class PresentationsController(ApplicationController):
    """ Controller to handle presentation http request """

    method_decorators = [check_es_connection]

    def create(self):
        """ Creates a new presentation with remotely requested images """
        params = parser.parse(create_args(), request)

        artifacts = Artifact.find_all(params["file_ids"])
        response = []
        for artifact in artifacts:
            response.append(artifact.to_json())

        current_app.socketio.emit('START_PRESENTATION', response)
        return '', 204
