import datetime
import pytest
from elasticsearch import Elasticsearch
from flask import current_app
import os
from dotenv import load_dotenv
load_dotenv()

@pytest.fixture
def es_fixture(test_client):
    if not test_client.use_db:
        yield None
        return False

    es = Elasticsearch(os.environ.get('ES_TEST_URL'))

    es.indices.delete(index="artefact", ignore=[400,404])

    es.indices.create(index="artefact", body= {
        "mappings": {
            "image": { 
                "properties": { 
                    "tags": { "type": "text"  }, 
                    "image_url": { "type": "text"  },
                    "created_at":  {
                        "type":   "date", 
                        "format": "strict_date_optional_time||epoch_millis"
                    }
                }
            }
        }
    })

    es.index(index="artefact", doc_type="image", refresh=True, body={
        "tags": "class diagram, uml, architecture", 
        "file_url": "class_diagram.png",
        "created_at": (datetime.datetime.now() - datetime.timedelta(days=14)).isoformat()
    })

    es.index(index="artefact", doc_type="image", refresh=True, body={
        "tags": "use case diagram, uml, szenario", 
        "file_url": "use_case_diagram.png",
        "created_at": (datetime.datetime.now() - datetime.timedelta(days=7)).isoformat()
    })

    yield es

    es.indices.delete(index="artefact")



def test_index(test_client, es_fixture):
    if not current_app.es:
        return False

    response = es_fixture.index(index="artefact", doc_type="image", body={
        "text": "class diagram, uml, architecture", 
        "file_url": "class_diagram.png",
        "created_at": (datetime.datetime.now() - datetime.timedelta(days=14)).isoformat()
    })

    assert response["result"] == "created"

def test_search_with_daterange(test_client, es_fixture):
    if not current_app.es:
        return False

    response = es_fixture.search(
        index="artefact", 
        doc_type="image",
        body={
            "sort" : [
                "_score",
                { "created_at" : { "order": "desc"}}
            ],
            "query": {
                "bool": {
                    "filter": {
                        "range": {
                            "created_at": {
                                "gte": (datetime.datetime.now() - datetime.timedelta(days=9)).isoformat(),
                                "lte": (datetime.datetime.now() - datetime.timedelta(days=6)).isoformat()
                            }
                        }
                    },        
                    "should": {
                        "match": {"tags": ""}
                    } 
                }   
            }
        })

    assert len(response["hits"]["hits"]) == 1 and response["hits"]["hits"][0]["_source"]["file_url"] == "use_case_diagram.png"

    
def test_search_with_text(test_client, es_fixture):
    if not current_app.es:
        return False

    response = es_fixture.search(
        index="artefact", 
        doc_type="image", 
        body={
            "sort" : [
                "_score",
                { "created_at" : { "order": "desc"}}
            ],
            "query": {
                "bool": {
                    "filter": {
                        "range": {
                            "created_at": {}
                        }
                    },        
                    "should": {
                        "match": {"tags": "Class diagram"}
                    } 
                }   
            }
        })

    assert len(response["hits"]["hits"]) == 2 and response["hits"]["hits"][0]["_source"]["file_url"] == "class_diagram.png"

def test_search_all(test_client, es_fixture):
    if not current_app.es:
        return False

    response = es_fixture.search(
        index="artefact", 
        doc_type="image", 
        body={
            "sort" : [
                "_score",
                { "created_at" : { "order": "desc"}}
            ],
            "query": {
                "bool": {
                    "filter": {
                        "range": {
                            "created_at": {}
                        }
                    },        
                    "should": {
                        "match": {"tags": ""}
                    } 
                }   
            }
        })

    assert len(response["hits"]["hits"]) == 2 and response["hits"]["hits"][0]["_source"]["file_url"] == "use_case_diagram.png"