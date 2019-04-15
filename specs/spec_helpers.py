"""Defines helpers for specs."""

from flask.testing import FlaskClient

from application import create_app


class TestingClient(FlaskClient):
    """ Adds login to the testing client class """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.csrf_token = None

    def login(self, user):
        """ Login a testing user all requests of this client will be authenticated with that user"""
        user_response = self.post("/authentications", data={"email_or_username": user.email, "password": "test"})

        if user_response.status_code != 200:
            raise Exception("Invalid username or password")
        self.csrf_token = user_response.json["csrf_token"]

    def logout(self):
        """ Logout a currently logged in user """
        self.csrf_token = None

    def get(self, *args, **kwargs):
        if self.csrf_token is not None:
            return super().get(*args, headers={"X-CSRF-TOKEN": self.csrf_token}, **kwargs)
        return super().get(*args, **kwargs)

    def put(self, *args, **kwargs):
        if self.csrf_token is not None:
            return super().put(*args, headers={"X-CSRF-TOKEN": self.csrf_token}, **kwargs)
        return super().put(*args, **kwargs)

    def post(self, *args, **kwargs):
        if self.csrf_token is not None:
            return super().post(*args, headers={"X-CSRF-TOKEN": self.csrf_token}, **kwargs)
        return super().post(*args, **kwargs)

    def patch(self, *args, **kwargs):
        if self.csrf_token is not None:
            return super().patch(*args, headers={"X-CSRF-TOKEN": self.csrf_token}, **kwargs)
        return super().patch(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.csrf_token is not None:
            return super().delete(*args, headers={"X-CSRF-TOKEN": self.csrf_token}, **kwargs)
        return super().delete(*args, **kwargs)


class Context:
    """ Setup the testing app, testing context and client for all tests. """

    def __init__(self):
        """ Initializes the Application Context. """
        app = create_app("test_config.cfg")
        app.test_client_class = TestingClient
        self._ctx = app.app_context()
        self._ctx.push()
        self._client = app.test_client()

    def client(self):
        """ Returns a Werkzeug client to perform requests. """
        return self._client

    def delete(self):
        """ Deletes the context again. Make sure to call in after hook. """
        self._ctx.pop()
