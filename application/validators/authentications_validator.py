""" Defines validators for authentication requests """

from webargs import fields

def create_args():
    """Defines and validates params for create or login"""
    return {
        "id_token": fields.String(),
        "email_or_username": fields.String(),
        "password": fields.String()
    }
