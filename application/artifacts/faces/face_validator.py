"""Defines validators for face requests"""

from webargs import fields


def verify_args():
    """Defines and validates params for verify"""
    return {
        "id": fields.UUID(required=True, location="view_args"),
        "name": fields.String(required=True),
    }
