"""
Handles logic for presentation http requests.
Uses socket.io to communicate with the frontend
"""

from webargs.flaskparser import use_args

from application.models.elastic.elastic_artifact import ElasticArtifact
from .application_controller import ApplicationController
from ..error_handling.es_connection import check_es_connection
from ..extensions import socketio
from ..responders import respond_with, no_content
from ..validators import presentations_validator


class PresentationsController(ApplicationController):
    """ Controller to handle presentation http request """

    method_decorators = [check_es_connection]

    @use_args(presentations_validator.create_args())
    def create(self, params):
        """ Creates a new presentation with remotely requested images """

        artifacts = ElasticArtifact.find_all(params["file_ids"])
        socketio.emit('START_PRESENTATION',
                      room=str(params["team_id"]),
                      data=respond_with(artifacts)
                      )
        return no_content()
