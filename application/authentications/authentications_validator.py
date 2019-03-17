"""Defines validators for authentication requests"""

from webargs import fields


def create_args():
    """Defines and validates params for create or login"""
    return {
        "email_or_username": fields.String(required=True),
        "password": fields.String(required=True)
    }
