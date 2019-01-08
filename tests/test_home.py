"""
Defines tests for home blueprint
"""

import os
from dotenv import load_dotenv
from flask import current_app
from elasticsearch import Elasticsearch

load_dotenv()


def test_index_without_elasticsearch(test_client):
    """ Test home index json if elasticsearch not defined """

    response = test_client.get("/")
    assert response.status_code == 200
    assert response.json == {
        "service name": "artefact service", "database status": "off"}


def test_index_with_elasticsearch(test_client):
    """ Test home index json if elasticsearch defined """

    if not test_client.use_db:
        pass

    current_app.es = Elasticsearch(os.environ.get('ES_TEST_URL'))

    response = test_client.get("/")
    assert response.status_code == 200
    assert response.json == {
        "service name": "artefact service", "database status": "on"}
