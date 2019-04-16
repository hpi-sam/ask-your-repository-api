"""Define validators for invites requests."""

from webargs import fields


def accept_invite_args():
    """Defines and validates params for accept invite"""
    return {"join_key": fields.String(required=True, location="view_args")}
