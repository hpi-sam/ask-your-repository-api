"""Defines validators for password reset requests"""

from webargs import fields


def create_args():
    """Defines and validates params for create"""
    return {
        "email_or_username": fields.String(required=True),
        "base_url": fields.URL(required=True)
    }


def update_args():
    """Defines and validates params for update"""
    return {
        "reset_token": fields.String(required=True),
        "password": fields.String(required=True)
    }
