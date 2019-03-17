""" Defines validators for user requests """

from webargs import fields, validate


def get_args():
    """Defines and validates params for show"""
    return {
        "id": fields.UUID(required=True, location='view_args'),
    }


def index_args():
    """Defines and validates params for index"""
    return {}


def create_args():
    """Defines and validates params for create"""
    return {
        "username": fields.String(required=True, validate=validate.Length(min=1)),
        "email": fields.Email(required=True),
        "password": fields.String(required=True)
    }


def update_args():
    """Defines and validates params for update"""
    return {
        "id": fields.UUID(required=True, load_from='id', location='view_args'),
        "username": fields.String(validate=validate.Length(min=1)),
        "email": fields.Email(),
        "password": fields.String(),
        "old_password": fields.String()
    }


def delete_args():
    """Defines and validates params for delete"""
    return {
        "id": fields.UUID(required=True, location='view_args')
    }
