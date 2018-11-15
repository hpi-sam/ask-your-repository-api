"""
Define all methods for unit_testing the artefacts blueprint.
"""

import datetime

def test_artefacts_show(test_client, es_mock):
    """ GET /artefact/{type}/{id} """

    es_mock.mock(function_name="get", return_value={"_source":{"class_diagram.png":""}})

    response = test_client.get("/artefacts/image/1")

    assert response.status_code == 200


def test_artefacts_index_without_params(test_client, es_mock):
    """ GET /artefacts/{type} without any parameters """

    es_mock.mock(function_name="search", return_value={"hits":{"hits":[]}})

    response = test_client.get("/artefacts/image", json={"search": ""})

    assert response.status_code == 200


def test_artefacts_index_with_range(test_client, es_mock):
    """ GET /artefacts/{type} with range paramters """

    es_mock.mock(function_name="search", return_value={"hits":{"hits":[]}})

    response = test_client.get("/artefacts/image", json={
        "date_range": {
            "start_date": (datetime.datetime.now() - datetime.timedelta(days=9)).isoformat(),
            "end_date": (datetime.datetime.now() - datetime.timedelta(days=6)).isoformat()
        },
        "search": ""})

    assert response.status_code == 200


def test_artefacts_index_with_params(test_client, es_mock):
    """ GET /artefacts/{type} with search parameters """

    es_mock.mock(function_name="search", return_value={"hits":{"hits":[]}})

    response = test_client.get("/artefacts/image", json={"search": "class diagram"})

    assert response.status_code == 200


def test_artefacts_create(test_client, es_mock):
    """ POST /artefacts/{type} """

    es_mock.mock(function_name="create", return_value={"result":"created"})

    response = test_client.post("/artefacts/image",
                                json={
                                    "id":"1",
                                    "tags":"uml, class diagram, architecture",
                                    "file_url": "class_diagram.png"})

    assert response.status_code == 201
    assert response.json["result"] == "created"


def test_artefacts_update(test_client, es_mock):
    """ PUT /artefacts/{type}/{id} """

    es_mock.mock(function_name="update", return_value={"result":"updated"})

    response = test_client.put("/artefacts/image/1",
                               json={"tags":"uml, class diagram, architecture"})

    assert response.status_code == 204


def test_artefacts_delete(test_client, es_mock):
    """ DELETE /artefacts/{type}/{id} """

    es_mock.mock(function_name="delete", return_value={"result":"deleted"})

    response = test_client.delete("/artefacts/image/1")

    assert response.status_code == 204
