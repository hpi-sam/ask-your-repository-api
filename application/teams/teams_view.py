"""
Handles all logic of the artefacts api
"""
import requests

from flask import current_app, abort
from flask_apispec import use_kwargs, marshal_with
from flask_apispec.views import MethodResource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_socketio import join_room, leave_room

from application.extensions import socketio
from application.teams.team import Team
from application.users.user import User
from application.teams.team_schema import TEAM_SCHEMA, TEAMS_SCHEMA
from application.teams import teams_validator


@socketio.on("ENTER_TEAM_SPACE")
def on_enter_team_space(data):
    """Logic for connecting to a Team with socketio"""
    current_app.logger.info("Join Room: " + data["team_id"])
    join_room(str(data["team_id"]))


@socketio.on("EXIT_TEAM_SPACE")
def on_exit_team_space(data):
    """Logic for leaving a Team with socketio"""
    current_app.logger.info("Leave Room: " + data["team_id"])
    leave_room(str(data["team_id"]))


class TeamView(MethodResource):
    """Access teams by id"""

    @use_kwargs(teams_validator.get_args())
    @marshal_with(TEAM_SCHEMA)
    def get(self, **params):
        """get a single team"""
        try:
            team = Team.find_by(id_=params["id"])
            return team
        except Team.DoesNotExist:  # pylint:disable=no-member
            return abort(404, "team not found")

    @use_kwargs(teams_validator.update_args())
    @marshal_with(TEAM_SCHEMA)
    def patch(self, **params):
        """Logic for updating a team"""
        return self.put(**params)

    @use_kwargs(teams_validator.update_args())
    @marshal_with(TEAM_SCHEMA)
    def put(self, **params):
        """Logic for updating a team"""
        try:
            team = Team.find_by(id_=params.pop("id"))
            team.update(**params)
            return team
        except Team.DoesNotExist:  # pylint:disable=no-member
            return abort(404, "team not found")


class TeamsView(MethodResource):
    """Controller for teams"""

    @jwt_required
    @use_kwargs(teams_validator.index_args())
    @marshal_with(TEAMS_SCHEMA)
    def get(self, **params):  # pylint: disable=W0613
        """Logic for querying several teams"""
        user = User.find_by(id_=get_jwt_identity())
        teams = list(user.teams)
        return teams

    @jwt_required
    @use_kwargs(teams_validator.create_args())
    @marshal_with(TEAM_SCHEMA)
    def post(self, **params):
        """Logic for creating a team"""
        team = Team(**params).save()
        user = User.find_by(id_=get_jwt_identity())
        team.members.connect(user)  # pylint:disable=no-member
        _notify_of_team_creation(team)
        return team

def _notify_of_team_creation(team):
    """Notify registered services of Team creation"""
    if current_app.config["DIALOGFLOW_NOTIFY"]:
        try:
            service_url = current_app.config["DIALOGFLOW_ADAPTER"] + "/teams"
            requests.post(service_url, json={"id": str(team.id_), "name": team.name})
        except requests.ConnectionError:
            current_app.logger.info("Couldn't connect to tobito!")

class MembersView(MethodResource):
    """Controller for members"""

    @use_kwargs(teams_validator.update_member_args())
    @marshal_with(TEAM_SCHEMA)
    def post(self, **params):
        """Logic for adding a single team member"""
        member_id = params['member']
        team_id = params['id']
        team = Team.find(team_id)
        member = User.find(member_id)

        if member in team.members:
            return abort(409, 'user already in team')

        team.members.connect(member)
        return team

class AllTeamsView(MethodResource):
    """Controller for members"""

    @marshal_with(TEAMS_SCHEMA)
    def get(self):  # pylint: disable=W0613
        """Logic for querying several teams"""
        return Team.nodes
