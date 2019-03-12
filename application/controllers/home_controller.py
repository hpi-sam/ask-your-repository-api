"""
Handles all logic of the home api
"""

from flask import current_app
from flask_apispec import marshal_with
from marshmallow import Schema, fields


class StatusSchema(Schema):
    """ Schema for the service status """
    service_name = fields.String()
    database_status = fields.String()


class HomeController(): # pylint:disable=too-few-public-methods
    """ Defines Routes on collection """

    @marshal_with(StatusSchema)
    def show_status(self):
        """
        Create a json description that is shown when connecting to the service without params
        """
        database_status = "on" if current_app.es else "off"
        return {"service_name": "artefact service",
                "database_status": database_status}
