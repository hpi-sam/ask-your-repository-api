"""Defines validators for user requests"""

from webargs import fields, validate, ValidationError
from webargs.flaskparser import abort


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
        "old_password": fields.String(),
        "id_token": fields.String(),
        "auth_code": fields.String()
    }


def delete_args():
    """Defines and validates params for delete"""
    return {
        "id": fields.UUID(required=True, location='view_args')
    }


def raise_old_password_was_wrong():
    """Raises a valid HTTPException"""
    return abort(422, exc=ValidationError("old password is not correct"),
                 messages={'old_password': ['Was not correct']})
