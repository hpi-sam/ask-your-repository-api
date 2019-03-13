""" Defines validators for user requests """

from webargs import fields, ValidationError


def get_args():
    return {
        "id": fields.UUID(required=True, load_from='object_id', location='view_args'),
    }


def index_args():
    """Defines and validates params for index"""
    return {}


def create_args():
    """Defines and validates params for create"""
    return {
        "username": fields.Function(required=True, deserialize=validate_user_name),
        "email": fields.Email(required=True),
        "password": fields.String(required=True)
    }


def update_args():
    """Defines and validates params for update"""
    return {
        "id": fields.UUID(required=True, load_from='object_id', location='view_args'),
        "username": fields.Function(deserialize=validate_user_name),
        "email": fields.Email(),
        "password": fields.String(),
        "old_password": fields.String()
    }


def delete_args():
    """Defines and validates params for delete"""
    return {
        "id": fields.UUID(required=True, load_from='object_id', location='view_args')
    }


def validate_user_name(user_name):
    if not isinstance(user_name, str):
        raise ValidationError("User name must be a string")

    if len(user_name) < 1:
        raise ValidationError("User name can't be empty")

    return user_name
