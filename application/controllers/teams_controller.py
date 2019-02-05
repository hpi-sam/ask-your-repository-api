"""
Handles all logic of the artefacts api
"""
from flask import current_app
from flask_socketio import join_room, leave_room
from webargs.flaskparser import use_args

from .application_controller import ApplicationController
from ..extensions import socketio
from ..models.team import Team
from ..responders import respond_with
from ..validators import teams_validator

@socketio.on("JOIN_TEAM")
def on_team_join(data):
    """ Logic for connecting to a Team with socketio """
    current_app.logger.info("Join Room: " + data["team_id"])
    join_room(str(data["team_id"]))

@socketio.on("LEAVE_TEAM")
def on_team_leave(data):
    """ Logic for leaving a Team with socketio """
    current_app.logger.info("Leave Room: " + data["team_id"])
    leave_room(str(data["team_id"]))


class TeamsController(ApplicationController):
    """ Controller for teams """

    def show(self, object_id):
        try:
            team = Team.find_by(id_=object_id)
            return respond_with(team), 200
        except Team.DoesNotExist:  # pylint:disable=no-member
            return {"error": "not found"}, 404

    @use_args(teams_validator.index_args())
    def index(self, params):  # pylint: disable=W0613
        """Logic for querying several teams"""
        teams = Team.all()
        return {"teams": respond_with(teams)}, 200

    @use_args(teams_validator.create_args())
    def create(self, params):
        """Logic for creating a team"""
        team = Team(name=params["name"]).save()
        return respond_with(team), 200

    @use_args(teams_validator.update_args())
    def update(self, params, object_id):
        """Logic for updating a team"""
        try:
            team = Team.find_by(id_=object_id)
            team.update(name=params["name"])
            return respond_with(team), 200
        except Team.DoesNotExist:  # pylint:disable=no-member
            return {"error": "not found"}, 404
