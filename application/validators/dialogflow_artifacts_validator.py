""" Defines validators for artifact requests coming from dialogflow adapter """

from webargs import fields


def search_args():
    """Defines and validates params for index"""
    return {
        "search": fields.String(missing=None),
        "team_name": fields.String(required=True),
        "types": fields.String(load_from="type", missing="image"),
        "start_date": fields.DateTime(),
        "end_date": fields.DateTime(),
        "offset": fields.Integer(missing=0),
        "limit": fields.Integer(missing=12)
    }
