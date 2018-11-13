import unittest
from flask import current_app
from application import home
from elasticsearch import Elasticsearch
import os
from dotenv import load_dotenv
load_dotenv()

def test_index_without_elasticsearch(test_client):
    response = test_client.get("/")
    print(response.data)
    assert response.status_code == 200
    assert response.json == {"service name":"artefact service", "database status": "off"}

def test_index_with_elasticsearch(test_client):
    if not test_client.use_db:
        return False
    
    current_app.es = Elasticsearch(os.environ.get('ES_TEST_URL'))

    response = test_client.get("/")
    print(response.data)
    assert response.status_code == 200
    assert response.json == {"service name":"artefact service", "database status": "on"}