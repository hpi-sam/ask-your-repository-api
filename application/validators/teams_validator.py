""" Defines validators for team requests """

from webargs import fields, ValidationError


def get_args():
    """Defines and validates params for index"""
    return {}


def create_args():
    """Defines and validates params for create"""
    return {"name": fields.String(
        required=True,
        deserialize=validate_team_name
    )}


def validate_team_name(team_name):
    if len(team_name) < 1:
        raise ValidationError("Team name can't be empty")
    return team_name
