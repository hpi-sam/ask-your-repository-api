"""Extensions module. Each extension is initialized in the app factory located in __init__.py."""
from flask_socketio import SocketIO

socketio = SocketIO()  # pylint: disable=invalid-name
