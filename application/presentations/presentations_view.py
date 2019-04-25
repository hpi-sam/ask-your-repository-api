"""
Handles logic for presentation http requests.
Uses socket.io to communicate with the frontend
"""

from flask_apispec import use_kwargs, marshal_with
from flask_apispec.views import MethodResource

from application.artifacts.artifact import Artifact
from application.artifacts.artifact_schema import ARTIFACTS_SCHEMA
from application.errors import check_es_connection
from application.extensions import socketio
from application.responders import marshal_data, no_content
from application.presentations import presentations_validator


class PresentationsView(MethodResource):
    """Controller to handle presentation http request"""

    method_decorators = [check_es_connection]

    @marshal_with(None, 204)
    @use_kwargs(presentations_validator.create_args())
    def post(self, **params):
        """Creates a new presentation with remotely requested images"""
        artifacts = []
        for artifact_id in params["file_ids"]:
            artifacts.append(Artifact.find_by(id_=artifact_id))

        socketio.emit("START_PRESENTATION", room=str(params["team_id"]), data=marshal_data(artifacts, ARTIFACTS_SCHEMA))
        return no_content()
