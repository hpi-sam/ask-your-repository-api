""" Defines validators for tags requests """

from webargs import fields


def add_tags_args():
    """Defines and validates params for add_tags"""
    return {
        "id": fields.UUID(required=True, load_from='object_id', location='view_args'),
        "tags": fields.List(fields.String(), missing=[]),
    }


def suggested_tags_args():
    """ Defines and validates suggested tags params """
    return {
        "team_id": fields.UUID(required=True),
        "tags": fields.List(fields.String(), missing=[]),
        "min_support": fields.Number(missing=0.25, validate=lambda val: val <= 1),
        "limit": fields.Integer(missing=3)
    }
