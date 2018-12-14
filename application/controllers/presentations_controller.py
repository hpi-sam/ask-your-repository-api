"""
Handles logic for presentation http requests.
Uses socket.io to communicate with the frontend
"""

from flask import current_app
from webargs.flaskparser import use_args
from application.models.artifact import Artifact
from application.base import respond_with
from application.error_handling.es_connection import check_es_connection
from application.validators import presentations_validator
from .application_controller import ApplicationController


class PresentationsController(ApplicationController):
    """ Controller to handle presentation http request """

    method_decorators = [check_es_connection]

    @use_args(presentations_validator.create_args())
    def create(self, params):
        """ Creates a new presentation with remotely requested images """

        artifacts = Artifact.find_all(params["file_ids"])
        current_app.socketio.emit('START_PRESENTATION', respond_with(artifacts))
        return '', 204
