"""
Handles all logic of the artefacts api
"""
from flask import current_app
from flask_apispec.views import MethodResource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_socketio import join_room, leave_room
from webargs.flaskparser import use_args

from ..extensions import socketio
from ..models import Team, User
from ..responders import respond_with
from ..validators import teams_validator


@socketio.on("ENTER_TEAM_SPACE")
def on_enter_team_space(data):
    """ Logic for connecting to a Team with socketio """
    current_app.logger.info("Join Room: " + data["team_id"])
    join_room(str(data["team_id"]))


@socketio.on("EXIT_TEAM_SPACE")
def on_exit_team_space(data):
    """ Logic for leaving a Team with socketio """
    current_app.logger.info("Leave Room: " + data["team_id"])
    leave_room(str(data["team_id"]))


class TeamsByIDController(MethodResource):
    """Access teams by id"""
    def get(self, object_id):
        """ get a single team """
        try:
            team = Team.find_by(id_=object_id)
            return respond_with(team), 200
        except Team.DoesNotExist:  # pylint:disable=no-member
            return {"error": "not found"}, 404

    @use_args(teams_validator.update_args())
    def patch(self, params, object_id):
        """Logic for updating a team"""
        try:
            team = Team.find_by(id_=object_id)
            team.update(name=params["name"])
            return respond_with(team), 200
        except Team.DoesNotExist:  # pylint:disable=no-member
            return {"error": "not found"}, 404

    @use_args(teams_validator.update_args())
    def put(self, params, object_id):
        """Logic for updating a team"""
        try:
            team = Team.find_by(id_=object_id)
            team.update(name=params["name"])
            return respond_with(team), 200
        except Team.DoesNotExist:  # pylint:disable=no-member
            return {"error": "not found"}, 404


class TeamsController(MethodResource):
    """ Controller for teams """

    @jwt_required
    @use_args(teams_validator.index_args())
    def get(self, params):  # pylint: disable=W0613
        """Logic for querying several teams"""
        user = User.find_by(id_=get_jwt_identity())
        teams = list(user.teams)
        return {"teams": respond_with(teams)}, 200

    @jwt_required
    @use_args(teams_validator.create_args())
    def post(self, params):
        """Logic for creating a team"""
        team = Team(name=params["name"]).save()
        user = User.find_by(id_=get_jwt_identity())
        team.members.connect(user)  # pylint:disable=no-member
        return respond_with(team), 200
