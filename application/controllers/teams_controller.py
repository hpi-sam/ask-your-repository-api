"""
Handles all logic of the artefacts api
"""
from webargs.flaskparser import use_args
from application.errors import NotFound
from application.validators import teams_validator
from application.models.team import Team
from application.base import respond_with
from .application_controller import ApplicationController


class TeamsController(ApplicationController):
    """ Controller for teams """

    def show(self, object_id):
        try:
            team = Team.find_by(force=True, id_=object_id)
            return respond_with(team), 200
        except NotFound:
            return {"error": "not found"}, 404

    @use_args(teams_validator.index_args())
    def index(self, params):  # pylint: disable=W0613
        """Logic for querying several teams"""
        teams = Team.all()
        return {"teams": respond_with(teams)}, 200

    @use_args(teams_validator.create_args())
    def create(self, params):
        """Logic for creating a team"""
        team = Team.create(name=params["name"])
        return respond_with(team), 200

    @use_args(teams_validator.update_args())
    def update(self, params, object_id):
        """Logic for updating a team"""
        try:
            team = Team.find_by(force=True, id_=object_id)
            team.update(name=params["name"])
            return respond_with(team), 200
        except NotFound:
            return {"error": "not found"}, 404
