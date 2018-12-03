"""
Defines all elasticsearch call tests.
Only runs when command --with-db is set.
"""

import datetime
import pytest
from elasticsearch.exceptions import NotFoundError
from flask import current_app
from application.artefacts.artefacts_controller import search_body_helper


def test_get_existing(es_fixture):
    """ Tests valid elasticsearch.get() """

    if not current_app.es:
        return

    response = es_fixture.get(
        index="artefact",
        doc_type="image",
        id="1"
    )

    assert response["found"]
    assert response["_source"]["file_url"] == "class_diagram.png"


def test_get_missing(es_fixture):
    """ Tests invalid elasticsearch.get() """

    if not current_app.es:
        return

    with pytest.raises(NotFoundError):
        es_fixture.get(
            index="artefact",
            doc_type="image",
            id="3"
        )


def test_create(es_fixture):
    """ Tests valid elasticsearch.create() """

    if not current_app.es:
        return

    response = es_fixture.create(index="artefact", doc_type="image", body={
        "text": "class diagram, uml, architecture",
        "id": "3",
        "file_url": "class_diagram.png",
        "created_at": (datetime.datetime.now() - datetime.timedelta(days=14)).isoformat()
    })

    assert response["result"] == "created"


def test_search_with_daterange(es_fixture):
    """ Tests valid elasticsearch.search() with daterange """

    if not current_app.es:
        return

    start_time = (datetime.datetime.now() -
                  datetime.timedelta(days=9)).isoformat()
    end_time = (datetime.datetime.now() -
                datetime.timedelta(days=6)).isoformat()
    daterange = {"gte": start_time, "lte": end_time}

    response = es_fixture.search(
        index="artefact",
        doc_type="image",
        body=search_body_helper("", daterange))

    assert (len(response["hits"]["hits"]) == 1
            and response["hits"]["hits"][0]["_source"]["file_url"] == "use_case_diagram.png")


def test_search_with_text(es_fixture):
    """ Tests valid elasticsearch.search() with search tesxt """

    if not current_app.es:
        return

    response = es_fixture.search(
        index="artefact",
        doc_type="image",
        body=search_body_helper("Class Diagram", {}))

    assert len(response["hits"]["hits"]
               ) == 2 and response["hits"]["hits"][0]["_source"]["file_url"] == "class_diagram.png"


def test_search_all(es_fixture):
    """ Tests valid elasticsearch.search() without parameters """

    if not current_app.es:
        return

    response = es_fixture.search(
        index="artefact",
        doc_type="image",
        body=search_body_helper("", {}))

    assert (len(response["hits"]["hits"]) == 2
            and response["hits"]["hits"][0]["_source"]["file_url"] == "use_case_diagram.png")


def test_update_existing(es_fixture):
    """ Tests valid elasticsearch.update() """

    if not current_app.es:
        return

    response = es_fixture.update(
        index="artefact",
        doc_type="image",
        id="1",
        body={
            "doc": {
                "file_url": "class_diagram_2.png"
            }
        }
    )

    assert response["result"] == "updated"


def test_update_missing(es_fixture):
    """ Tests invalid elasticsearch.update() """

    if not current_app.es:
        return

    with pytest.raises(NotFoundError):
        es_fixture.update(
            index="artefact",
            doc_type="image",
            id="3",
            body={
                "doc": {
                    "file_url": "class_diagram_2.png"
                }
            }
        )


def test_delete_existing(es_fixture):
    """ Tests valid elasticsearch.delete() """

    if not current_app.es:
        return

    response = es_fixture.delete(
        index="artefact",
        doc_type="image",
        id="1"
    )
    assert response["result"] == "deleted"


def test_delete_missing(es_fixture):
    """ Tests invalid elasticsearch.delete() """

    if not current_app.es:
        return

    with pytest.raises(NotFoundError):
        es_fixture.delete(
            index="artefact",
            doc_type="image",
            id="3"
        )
