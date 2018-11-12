import pytest
from application import create_app
from flask import current_app
import datetime

def pytest_addoption(parser):
    parser.addoption("--with-db", action="store_true", default=False,
        help="run with life databse")

@pytest.fixture(scope='module')
def test_client(request):
    flask_app = create_app('test_config.cfg')
    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.

    testing_client = flask_app.test_client()

    print(request.config.getoption('--with-db'))

    testing_client.use_db = request.config.getoption('--with-db')
    # Establish an application context before running the tests.
    ctx = flask_app.app_context()
    ctx.push()

    yield testing_client  # this is where the testing happens!

    ctx.pop()