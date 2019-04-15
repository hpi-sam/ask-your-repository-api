"""Define validators for invites requests."""

from webargs import fields


def accept_invite_args():
    """Defines and validates params for accept invite"""
    return {"join_key": fields.UUID(required=True, location="view_args")}
