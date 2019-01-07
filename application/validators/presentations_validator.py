""" Defines validators for presentation requests """

from webargs import fields

def create_args():
    """Defines and validates params for index"""
    return {
        "file_ids": fields.List(fields.UUID(), load_from="image_ids", location="json")
    }
