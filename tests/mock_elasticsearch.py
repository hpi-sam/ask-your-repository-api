"""
Define all helpers for mocking Elasticsearch here.
"""


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
