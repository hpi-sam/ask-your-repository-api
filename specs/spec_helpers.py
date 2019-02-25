"""Defines helpers for specs."""

from flask import Request, current_app
from flask.testing import FlaskClient
from flask_jwt_extended import create_access_token, get_csrf_token
from flask_jwt_extended.config import config
from werkzeug.datastructures import MultiDict, FileStorage

from application import create_app

class TestingClient(FlaskClient):
    """ Adds login to the testing client class """

    def login(self, email_or_username, password):
        """ Login a testing user and return the token """
        user_response = self.post('/users/login',
                                  data={'email_or_username': email_or_username,
                                        'password': password})

        if user_response.status_code == 200:
            return user_response.json["token"]
        else:
            raise Exception('Invalid username or password')


class TestingFileStorage(FileStorage):
    """Taken from: http://www.prschmid.com/2013/05/unit-testing-flask-file-uploads-without.html
    This is a helper for testing upload behavior in your application. You
    can manually create it, and its save method is overloaded to set `saved`
    to the name of the file it was saved to. All of these parameters are
    optional, so only bother setting the ones relevant to your application.

    This was copied from Flask-Uploads.

    :param stream: A stream. The default is an empty stream.
    :param filename: The filename uploaded from the client. The default is the
                     stream's name.
    :param name: The name of the form field it was loaded from. The default is
                 ``None``.
    :param content_type: The content type it was uploaded as. The default is
                         ``application/octet-stream``.
    :param content_length: How long it is. The default is -1.
    :param headers: Multipart headers as a `werkzeug.Headers`. The default is
                    ``None``."""

    # pylint:disable=too-many-arguments, unused-argument
    def __init__(self, stream=None, filename=None, name=None,
                 content_type='application/octet-stream', content_length=-1,
                 headers=None):
        FileStorage.__init__(
            self, stream, filename, name=name,
            content_type=content_type, content_length=content_length,
            headers=None)
        self.saved = None

    def save(self, dst, buffer_size=16384):
        """
        This marks the file as saved by setting the `saved` attribute to the
        name of the file it was saved to.

        :param dst: The file to save to.
        :param buffer_size: Ignored.
        """
        if isinstance(dst, str):
            self.saved = dst
        else:
            self.saved = dst.name

    # pylint:enable=too-many-arguments, unused-argument


class TestingRequest(Request):  # pylint:disable=too-few-public-methods, too-many-ancestors
    """A testing request to use that will return a
    TestingFileStorage to test file uploading."""

    @property
    def files(self):
        # Consume input stream from the request if still unconsumed
        if 'form' not in self.__dict__:
            self._load_form_data()

        file_dictionary = MultiDict()
        files = self.__dict__.get('files')
        if files:
            for key, file_storage in files.items(multi=True):
                file_dictionary.add(key, TestingFileStorage(filename=file_storage.filename))

        return file_dictionary


class Context:
    """ Setup the testing app, testing context and client for all tests. """

    def __init__(self):
        """ Initializes the Application Context. """
        app = create_app('test_config.cfg')
        app.test_client_class = TestingClient
        app.request_class = TestingRequest
        self._ctx = app.app_context()
        self._ctx.push()
        self._client = app.test_client()

    def client(self):
        """ Returns a Werkzeug client to perform requests. """
        return self._client

    def delete(self):
        """ Deletes the context again. Make sure to call in after hook. """
        self._ctx.pop()
