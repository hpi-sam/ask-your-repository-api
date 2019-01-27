"""
Handles all logic of the dialogflow_artifacts api
"""

from webargs.flaskparser import use_args
from ..extensions import socketio
from ..responders import respond_with
from ..error_handling.es_connection import check_es_connection
from ..models.artifact import Artifact
from ..models.team import NeoTeam
from ..validators import dialogflow_artifacts_validator
from .application_controller import ApplicationController


class DialogflowArtifactsController(ApplicationController):
    """ Controller for Artifacts """

    method_decorators = [check_es_connection]

    @use_args(dialogflow_artifacts_validator.search_args())
    def index(self, params):
        "Logic for querying several artifacts"

        team = NeoTeam.find_by(name=params.pop('team_name'))
        params["team_id"] = team.id
        artifacts = Artifact.search(params)

        socketio.emit('START_PRESENTATION',
                      room=str(params["team_id"]),
                      data=respond_with(artifacts)
                      )
        return respond_with(artifacts)
