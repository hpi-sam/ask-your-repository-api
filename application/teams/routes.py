"""Provides Team functionality and routes"""
from flask import Blueprint

from .teams_view import TeamView, TeamsView
from application.teams.placeholder_drives.drive_view import DrivesView

TEAMS = Blueprint("teams", __name__)
TEAMS.add_url_rule("", view_func=TeamsView.as_view("teamsview"))
TEAMS.add_url_rule("/<id>", view_func=TeamView.as_view("teamview"))
TEAMS.add_url_rule("/<team_id>/drives", view_func=DrivesView.as_view("drivesview"))
