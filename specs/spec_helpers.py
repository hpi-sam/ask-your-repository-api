""" Defines helpers for specs """
from application import create_app


class Context:
    """ Setup the testing app, testing context and client for all tests. """

    def __init__(self):
        """ Initializes the Application Context. """
        app = create_app('test_config.cfg')
        self._ctx = app.app_context()
        self._ctx.push()
        self._client = app.test_client()

    def client(self):
        """ Returns a Werkzeug client to perform requests. """
        return self._client

    def delete(self):
        """ Deletes the context again. Make sure to call in after hook. """
        self._ctx.pop()
