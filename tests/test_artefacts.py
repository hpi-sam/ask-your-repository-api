import unittest
from flask import jsonify, current_app
from application import artefacts
import datetime
from mock_elasticsearch import ElasticMock
import pytest

@pytest.fixture
def es_mock():
    es = current_app.es
    current_app.es = ElasticMock()
    yield current_app.es
    current_app.es = es

def test_artefacts_index_without_params(test_client, es_mock):
    es_mock.mock(function="search", return_value={"hits":{"hits":[]}})

    response = test_client.get("/artefacts", json={"type": 'image', "search": ""})

    assert response.status_code == 200

def test_artefacts_index_with_range(test_client, es_mock):
    es_mock.mock(function="search", return_value={"hits":{"hits":[]}})

    response = test_client.get("/artefacts", json={
        "type": 'image', 
        "date_range": {
            "start_date": (datetime.datetime.now() - datetime.timedelta(days=9)).isoformat(),
            "end_date": (datetime.datetime.now() - datetime.timedelta(days=6)).isoformat()
        },
        "search": ""})

    assert response.status_code == 200

def test_artefacts_index_with_params(test_client, es_mock):
    es_mock.mock(function="search", return_value={"hits":{"hits":[]}})

    response = test_client.get("/artefacts", json={"type": 'image', "search": "class diagram"})

    assert response.status_code == 200


def test_artefacts_create(test_client, es_mock):
    es_mock.mock(function="index", return_value={"result":"created"})

    response = test_client.post("/artefacts", json={"id":"1","type": 'image', "tags":"uml, class diagram, architecture", "file_url": "class_diagram.png"})

    assert response.status_code == 200
    assert response.json["result"] == "created"

