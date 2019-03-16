"""
Handles logic for presentation http requests.
Uses socket.io to communicate with the frontend
"""

from flask_apispec import use_kwargs, marshal_with
from flask_apispec.views import MethodResource

from application.models import Artifact
from ..error_handling.es_connection import check_es_connection
from ..extensions import socketio
from ..responders import respond_with, no_content
from ..validators import presentations_validator


class PresentationsView(MethodResource):
    """ Controller to handle presentation http request """

    method_decorators = [check_es_connection]

    @marshal_with(None, 204)
    @use_kwargs(presentations_validator.create_args())
    def post(self, **params):
        """ Creates a new presentation with remotely requested images """
        artifacts = []
        for artifact_id in params['file_ids']:
            artifacts.append(Artifact.find_by(id_=artifact_id))

        socketio.emit('START_PRESENTATION',
                      room=str(params["team_id"]),
                      data=respond_with(artifacts)
                      )
        return no_content()
