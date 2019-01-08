""" Defines validators for team requests """

from webargs import fields, ValidationError


def index_args():
    """Defines and validates params for index"""
    return {}


def create_args():
    """Defines and validates params for create"""
    return {"name": fields.Function(
        required=True,
        deserialize=validate_team_name
    )}

def update_args():
    """Defines and validates params for update"""
    return {
        "id": fields.UUID(required=True, load_from='object_id', location='view_args'),
        "name": fields.Function(deserialize=validate_team_name)
    }

def validate_team_name(team_name):
    if not isinstance(team_name, str):
        raise ValidationError("Team name must be a string")

    if len(team_name) < 1:
        raise ValidationError("Team name can't be empty")

    return team_name
