import pytest
from application import create_app
from elasticmock.fake_elasticsearch import FakeElasticsearch

@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app('test_config.cfg')
    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.

    ##########################################################################################
    ##                                  IMPORTANT!                                          ##
    ##  FakeElasticsearch is intendet to be used with ElasticSearch version 1.0.1           ##
    ##  If you run into trouble with testing, consider Downgrading ElasticSearch or         ##
    ##  fork the class from elasticmock and edit it.                                        ##
    ##########################################################################################

    # Mock all calls to ElasticSearch with FakeElasticsearch
    flask_app.es = FakeElasticsearch()

    testing_client = flask_app.test_client()
    
    # Establish an application context before running the tests.
    ctx = flask_app.app_context()
    ctx.push()

    yield testing_client  # this is where the testing happens!

    ctx.pop()
