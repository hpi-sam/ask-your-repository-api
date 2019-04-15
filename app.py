""" Entry point for our application """
import logging

from application import create_app
from application.extensions import socketio

# Call the Application Factory function to construct a Flask application instance
# using the standard configuration defined in /instance/flask.cfg
app = create_app("development_config.cfg")  # pylint: disable=invalid-name

if __name__ != "__main__":
    gunicorn_logger = logging.getLogger("gunicorn.error")  # pylint: disable=invalid-name
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)  # pylint: disable=no-member

if __name__ == "__main__":
    socketio.run(host="0.0.0.0")  # pylint: disable=no-value-for-parameter
