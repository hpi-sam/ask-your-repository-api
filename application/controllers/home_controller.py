"""
Handles all logic of the home api
"""

from flask import current_app
from .application_controller import ApplicationController


class HomeController(ApplicationController):
    """ Defines Routes on collection """

    def show_status(self):
        """
        Create a json description that is shown when connecting to the service without params
        """
        current_app.logger.debug("this is a DEBUG message")
        current_app.logger.info("this is an INFO message")
        current_app.logger.warning("this is a WARNING message")
        current_app.logger.error("this is an ERROR message")
        current_app.logger.critical("this is a CRITICAL message")

        database_status = "on" if current_app.es else "off"
        return {"service name": "artefact service",
                "database status": database_status}
