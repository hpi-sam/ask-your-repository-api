"""
Handles all logic of the artefacts api
"""

import datetime
from flask import current_app
from elasticsearch.exceptions import NotFoundError, ConflictError


def show(params):
    "Logic for getting a single artefact"

    if not current_app.es:
        return {"error": "search engine not available"}, 503

    try:
        result = current_app.es.get(
            index="artefact",
            doc_type="_all",
            id=params["id"]
        )
        return result, 200
    except NotFoundError:
        return {"error": "not found"}, 404


def index(params):
    "Logic for querying several artefacts"

    if not current_app.es:
        return {"error": "search engine not available"}, 503

    date_range = {}
    if "start_date" in params:
        date_range["gte"] = params["start_date"]
    if "end_date" in params:
        date_range["lte"] = params["end_date"]

    artefact_types = params.get("types", "")
    result = current_app.es.search(
        index="artefact",
        doc_type=artefact_types,
        body=search_body_helper(params.get("search", ""), date_range))

    return {"results": result["hits"]["hits"]}, 200


def create(params):
    "Logic for creating an artefact"

    if not current_app.es:
        return {"error": "search engine not available"}, 503

    date = datetime.datetime.now().isoformat()
    artefact_type = params.get("type", "image")
    body = {
        "tags": params["tags"],
        "file_url": params["file_url"],
        "created_at": date
    }

    try:
        result = current_app.es.create(
            index="artefact",
            doc_type=artefact_type,
            id=params["id"],
            body=body)
        result["_source"] = body
        return result, 201
    except ConflictError:
        return {"error": "document already exists"}, 404


def update(params):
    "Logic for updating an artefact"

    if not current_app.es:
        return {"error": "search engine not available"}, 503

    update_params = {}
    if "tags" in params:
        update_params["tags"] = params["tags"]
    if "file_url" in params:
        update_params["file_url"] = params["file_url"]

    try:
        result = current_app.es.get(
            index="artefact",
            doc_type="_all",
            id=params["id"]
        )
    except NotFoundError:
        return {"error": "not found"}, 404

    current_app.es.update(
        index="artefact",
        doc_type=result["_type"],
        id=params["id"],
        body={
            "doc": update_params
        })
    return '', 204


def delete(params):
    "Logic for deleting an artefact"

    if not current_app.es:
        return {"error": "search engine not available"}, 503

    try:
        result = current_app.es.get(
            index="artefact",
            doc_type="_all",
            id=params["id"]
        )
    except NotFoundError:
        return {"error": "not found"}, 404

    current_app.es.delete(
        index="artefact",
        doc_type=result["_type"],
        id=params["id"])
    return '', 204

def search_body_helper(search, daterange):
    """ Defines a common body for search function """

    body = {
        "sort": [
            "_score",
            {"created_at": {"order": "desc"}}
        ],
        "query": {
            "bool": {
                "filter": {
                    "range": {
                        "created_at": daterange
                    }
                },
                "should": {
                    "match": {"tags": search}
                }
            }
        }
    }
    return body
