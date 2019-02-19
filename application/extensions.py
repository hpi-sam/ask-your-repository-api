"""Extensions module. Each extension is initialized in the app factory located in __init__.py."""
from flask_socketio import SocketIO
from flask_bcrypt  import Bcrypt

# pylint: disable=invalid-name
socketio = SocketIO()
bcrypt = Bcrypt()
# pylint: enable=invalid-name
