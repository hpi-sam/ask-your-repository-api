"""
Handles logic for presentation http requests.
Uses socket.io to communicate with the frontend
"""

from webargs.flaskparser import use_args
from ..extensions import socketio
from ..models.artifact import Artifact
from ..responders import respond_with, no_content
from ..error_handling.es_connection import check_es_connection
from ..validators import presentations_validator
from .application_controller import ApplicationController


class PresentationsController(ApplicationController):
    """ Controller to handle presentation http request """

    method_decorators = [check_es_connection]

    @use_args(presentations_validator.create_args())
    def create(self, params):
        """ Creates a new presentation with remotely requested images """

        artifacts = Artifact.find_all(params["file_ids"])
        socketio.emit('START_PRESENTATION',
                      room=str(params["team_id"]),
                      data=respond_with(artifacts)
                      )
        return no_content()
