"""Define responders that can be used in views"""

from flask import make_response


def marshal_data(resource, schema):
    """Responds with a collection of - or single json"""
    return schema.dump(resource).data


def no_content():
    """Creates an empty response with
    application/json mimetype"""

    response = make_response("", 204)
    response.mimetype = "application/json"
    return response
