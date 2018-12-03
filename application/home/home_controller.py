"""
Handles all logic of the home api
"""

from flask import current_app
from flask_restful import Resource


class HomeResources(Resource):
    """ Defines Routes on collection """

    def get(self):
        "Create a json description that is shown when connecting to the service without params"
        database_status = "on" if current_app.es else "off"
        return {"service name": "artefact service",
                "database status": database_status}
