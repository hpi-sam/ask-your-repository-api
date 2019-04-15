"""Defines validators for password reset requests"""

from webargs import fields


def send_reset_link_args():
    """Defines and validates params for sending a password reset link"""
    return {"email_or_username": fields.String(required=True), "base_url": fields.URL(required=True)}


def update_password_args():
    """Defines and validates params for updating a password"""
    return {"reset_token": fields.String(required=True), "password": fields.String(required=True)}
