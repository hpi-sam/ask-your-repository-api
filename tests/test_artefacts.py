import unittest
from flask import jsonify, current_app
from application import artefacts
import pytest

@pytest.fixture
def populate_elasticsearc():
    current_app.es.index(index="artefact", doc_type="image", id=1234, body={"text": "cat, tiger, big, red", "file_url": "cat.png"})
    current_app.es.index(index="artefact", doc_type="image", id=1235, body={"text": "yellow, cat", "file_url": "another_cat.png"})

def test_artefacts_index_without_params(test_client, populate_elasticsearc):
    response = test_client.get("/artefacts", json={"type": 'image', "search": ""})

    print(response.json)
    assert response.status_code == 200
    assert response.json["hits"]["hits"][0]["_id"] == 1234 and response.json["hits"]["hits"][1]["_id"] == 1235

def test_artefacts_index_with_params(test_client, populate_elasticsearc):
    response = test_client.get("/artefacts", json={"type": 'image', "search": ""})

    assert response.status_code == 200
    assert response.json["hits"]["hits"][0]["_source"]["file_url"] == "cat.png"
    assert response.json["hits"]["hits"][0]["_source"]["text"] == "cat, tiger, big, red"


def test_artefacts_create(test_client):
    current_app.es.index(index="artefact", doc_type="image", id=1234, body={"text": "cat, tiger, big, red", "file_url": "cat.png"})

    response = test_client.post("/artefacts", json={"type": 'image', "tags":"yellow, cat", "file_url": "another_cat.pn"})

    assert response.status_code == 200
    assert response.json["created"] == True

