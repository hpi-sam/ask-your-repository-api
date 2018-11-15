import unittest
from flask import jsonify, current_app
from application import artefacts
import datetime
from .mock_elasticsearch import ElasticMock
import pytest

@pytest.fixture
def es_mock():
    es = current_app.es
    current_app.es = ElasticMock()
    yield current_app.es
    current_app.es = es


def test_artefacts_show(test_client, es_mock):
    es_mock.mock(function="get", return_value={"_source":{"class_diagram.png":""}})

    response = test_client.get("/artefacts/image/1")

    assert response.status_code == 200


def test_artefacts_index_without_params(test_client, es_mock):
    es_mock.mock(function="search", return_value={"hits":{"hits":[]}})

    response = test_client.get("/artefacts/image", json={"search": ""})

    assert response.status_code == 200


def test_artefacts_index_with_range(test_client, es_mock):
    es_mock.mock(function="search", return_value={"hits":{"hits":[]}})

    response = test_client.get("/artefacts/image", json={
        "date_range": {
            "start_date": (datetime.datetime.now() - datetime.timedelta(days=9)).isoformat(),
            "end_date": (datetime.datetime.now() - datetime.timedelta(days=6)).isoformat()
        },
        "search": ""})

    assert response.status_code == 200


def test_artefacts_index_with_params(test_client, es_mock):
    es_mock.mock(function="search", return_value={"hits":{"hits":[]}})

    response = test_client.get("/artefacts/image", json={"search": "class diagram"})

    assert response.status_code == 200


def test_artefacts_create(test_client, es_mock):
    es_mock.mock(function="create", return_value={"result":"created"})

    response = test_client.post("/artefacts/image", json={"id":"1", "tags":"uml, class diagram, architecture", "file_url": "class_diagram.png"})

    assert response.status_code == 201
    assert response.json["result"] == "created"


def test_artefacts_update(test_client, es_mock):
    es_mock.mock(function="update", return_value={"result":"updated"})

    response = test_client.put("/artefacts/image/1", json={"tags":"uml, class diagram, architecture"})

    assert response.status_code == 204


def test_artefacts_delete(test_client, es_mock):
    es_mock.mock(function="delete", return_value={"result":"deleted"})

    response = test_client.delete("/artefacts/image/1")

    assert response.status_code == 204