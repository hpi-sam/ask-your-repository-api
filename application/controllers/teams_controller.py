"""
Handles all logic of the artefacts api
"""
from webargs.flaskparser import use_args
from application.errors import NotFound
from application.error_handling.es_connection import check_es_connection
from application.models.artifact import Artifact
from application.validators import teams_validator
from .application_controller import ApplicationController
from application.models.team import Team
from application.base import respond_with

class TeamsController(ApplicationController):
    """ Controller for Artifacts """

    @use_args(teams_validator.get_args())
    def index(self, params):
        "Logic for querying several teams"

        teams = Team.all()

        return {"teams": respond_with(teams)}, 200