"""
Define all methods for unit_testing the artefacts blueprint.
"""

import datetime

def test_artefacts_show(test_client, es_mock):
    """ GET /artefact/{id} """

    es_mock.mock(function_name="get", return_value={"_source":{"class_diagram.png":""}})

    response = test_client.get("/artefacts/1")

    assert response.status_code == 200


def test_artefacts_index_without_params(test_client, es_mock):
    """ GET /artefacts without any parameters """

    es_mock.mock(function_name="search", return_value={"hits":{"hits":[]}})

    response = test_client.get("/artefacts")

    assert response.status_code == 200

def test_artefacts_index_with_pagination(test_client, es_mock):
    """ GET /artefacts without any parameters """

    es_mock.mock(function_name="search", return_value={"hits":{"hits":[]}})

    response = test_client.get("/artefacts?search=&offset=0&limit=1")

    assert response.status_code == 200

def test_artefacts_index_with_range(test_client, es_mock):
    """ GET /artefacts with range paramters """

    es_mock.mock(function_name="search", return_value={"hits":{"hits":[]}})

    response = test_client.get("/artefacts?start_date={}&end_date={}&search=".format(
        (datetime.datetime.now() - datetime.timedelta(days=9)).isoformat(),
        (datetime.datetime.now() - datetime.timedelta(days=6)).isoformat()))


    assert response.status_code == 200


def test_artefacts_index_with_params(test_client, es_mock):
    """ GET /artefacts with search parameters """

    es_mock.mock(function_name="search", return_value={"hits":{"hits":[]}})

    response = test_client.get("/artefacts?type=image&search=class diagram")

    assert response.status_code == 200


def test_artefacts_create(test_client, es_mock):
    """ POST /artefacts """

    es_mock.mock(function_name="create", return_value={"result":"created"})

    response = test_client.post("/artefacts",
                                json={
                                    "type":"image",
                                    "id":"1",
                                    "tags":"uml, class diagram, architecture",
                                    "file_url": "class_diagram.png"})

    assert response.status_code == 201
    assert response.json["result"] == "created"


def test_artefacts_update(test_client, es_mock):
    """ PUT /artefacts/{id} """

    es_mock.mock(function_name="get", return_value={"_type":"image"})
    es_mock.mock(function_name="update", return_value={"result":"updated"})

    response = test_client.put("/artefacts/1",
                               json={"type":"image", "tags":"uml, class diagram, architecture"})

    assert response.status_code == 204


def test_artefacts_delete(test_client, es_mock):
    """ DELETE /artefacts/{id} """

    es_mock.mock(function_name="get", return_value={"_type":"image"})
    es_mock.mock(function_name="delete", return_value={"result":"deleted"})

    response = test_client.delete("/artefacts/1")

    assert response.status_code == 204
