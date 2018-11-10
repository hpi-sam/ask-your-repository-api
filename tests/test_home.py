import unittest
from flask import jsonify
from application import home

def test_api_status(test_client):
    response = test_client.get("/")
    print(response.data)
    assert response.status_code == 200
    assert response.json == {"service name":"artefact service", "database status": "on"}