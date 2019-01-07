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
    """ Controller for teams """

    def show(self, object_id):
        try:
            return respond_with(Team.find_by(force=True, id_=object_id)), 200
        except NotFound:
            return {"error": "not found"}, 404

    @use_args(teams_validator.get_args())
    def index(self, params):
        """Logic for querying several teams"""
        teams = Team.all()
        return {"teams": respond_with(teams)}, 200

    @use_args(teams_validator.create_args())
    def create(self, params):
        """Logic for creating a team"""
        team = Team.create(name=params["name"])
        return respond_with(team), 200
