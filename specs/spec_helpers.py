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

class ElasticMock:
    """
    Defines a class for Mocking elasticsearch calls.
    Simple create with es = ElasticMock()
    """

    def mock(self, function_name, return_value):
        """
        mock calls to es with es.mock(NAME_OF_FUNCTION_AS_STING, RETURN_VALUE)
        """

        my_lambda = lambda **kwargs: return_value
        self.add_mock_function(function_name, my_lambda)

    def add_mock_function(self, function_name, function_lambda):
        """
        Adds the function to the ElasticMock object
        by setting an attribute containing a lambda.
        """
        setattr(self, function_name, function_lambda)
