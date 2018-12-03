"""
Defines all pytest fixtures here.
"""

import os
import datetime
import pytest
from dotenv import load_dotenv
from flask import current_app
from elasticsearch import Elasticsearch
from application import create_app
from .mock_elasticsearch import ElasticMock

load_dotenv()

use_db = False


def pytest_addoption(parser):
    """
    Parses the user input params when running the test command.
    Only --with-db possible so far.
    """

    parser.addoption("--with-db", action="store_true", default=False,
                     help="run with life databse")


@pytest.fixture(scope='module')
def test_client(request):
    """ Setup the testing app, testing context and client for all tests. """

    flask_app = create_app('test_config.cfg')
    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.

    testing_client = flask_app.test_client()

    testing_client.use_db = request.config.getoption('--with-db')
    # Establish an application context before running the tests.
    ctx = flask_app.app_context()
    ctx.push()

    yield testing_client  # this is where the testing happens!

    ctx.pop()


@pytest.fixture
def es_mock():
    """
    Fixture for mocking the system elasticsearch variable
    for each test and restore the content afterward
    """

    elastic_search = current_app.es
    current_app.es = ElasticMock()
    yield current_app.es
    current_app.es = elastic_search


#pylint: disable=redefined-outer-name

@pytest.fixture
def es_fixture(test_client):
    """
    Fixture for creating an actual Elasticsearch instance
    and creating some objects in it.
    """

    if not test_client.use_db:
        yield None
        return

    elastic_search = Elasticsearch(os.environ.get('ES_TEST_URL'))

    #pylint: disable=unexpected-keyword-arg

    elastic_search.indices.delete(index="artifact", ignore=[400, 404])

    elastic_search.indices.create(index="artifact", body={
        "mappings": {
            "image": {
                "properties": {
                    "tags": {"type": "text"},
                    "image_url": {"type": "text"},
                    "created_at": {
                        "type": "date",
                        "format": "strict_date_optional_time||epoch_millis"
                    }
                }
            }
        }
    })

    elastic_search.index(index="artifact", doc_type="image", id="1", refresh=True, body={
        "tags": "class diagram, uml, architecture",
        "file_url": "class_diagram.png",
        "created_at": (datetime.datetime.now() - datetime.timedelta(days=14)).isoformat()
    })

    elastic_search.index(index="artifact", doc_type="image", id="2", refresh=True, body={
        "tags": "use case diagram, uml, szenario",
        "file_url": "use_case_diagram.png",
        "created_at": (datetime.datetime.now() - datetime.timedelta(days=7)).isoformat()
    })

    yield elastic_search

    elastic_search.indices.delete(index="artifact")

    #pylint: enable=unexpected-keyword-arg


#pylint: enable=redefined-outer-name
