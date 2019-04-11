"""Defines validators for team requests"""

from webargs import fields, validate


def index_args():
    """Defines and validates params for index"""
    return {}


def get_args():
    """Defines and validates params for show"""
    return {"id": fields.UUID(required=True, location="view_args")}


def create_args():
    """Defines and validates params for create"""
    return {"name": fields.String(required=True, validate=validate.Length(min=1))}


def update_args():
    """Defines and validates params for update"""
    return {
        "id": fields.UUID(required=True, location="view_args"),
        "name": fields.String(required=True, validate=validate.Length(min=1)),
    }
