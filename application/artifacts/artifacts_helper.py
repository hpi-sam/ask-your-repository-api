""" Defines helpers for Artifact saving and input validation """
import uuid
import datetime
from flask import current_app
from elasticsearch.exceptions import NotFoundError, ConflictError

def search_body_helper(search, daterange, limit=10, offset=0):
    """ Defines a common body for search function """

    body = {
        "from": offset, "size": limit,
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

def parse_params(params):
    result = {}
    result["id"] = params["_id"]
    result["type"] = params["_type"]
    result["created_at"] = params["_source"]["created_at"]
    result["updated_at"] = params["_source"]["updated_at"]
    result["file_url"] = params["_source"]["file_url"]
    result["tags"] = params["_source"]["tags"]
    return result

def parse_search_params(params):
    for hit in params["hits"]["hits"]:
        hit["id"] = hit.pop("_id")
        hit["type"] = hit.pop("_type")
        hit["score"] = hit.pop("_score")
        hit["created_at"] = hit["_source"]["created_at"]
        hit["file_url"] = hit["_source"]["file_url"]
        hit["tags"] = hit["_source"]["tags"]
        del hit["_source"]
        del hit["_index"]
    return params["hits"]["hits"]

class Artifact(object):
    """ Handles saving and searching """

    @classmethod
    def find(cls, artifact_id):
        """ Finds artifact by id """
        try:
            result = current_app.es.get(
                index="artifact",
                doc_type="_all",
                id=artifact_id
            )
            return Artifact.from_es(result)
        except NotFoundError:
            raise NotFound()

    @classmethod
    def search(cls, params):
        """ Finds multiple artifacts by params.  """
        date_range = {}
        if "start_date" in params:
            date_range["gte"] = params["start_date"]
        if "end_date" in params:
            date_range["lte"] = params["end_date"]
        result = current_app.es.search(
            index="artifact",
            doc_type=params["types"],
            body=search_body_helper(params["search"], date_range,
                                    params["limit"], params["offset"]))
        return parse_search_params(result)

    @classmethod
    def from_es(cls, es_params):
        """ Create a Resource from elastic_search """
        params = parse_params(es_params)
        artifact = Artifact(params)
        artifact.id = params["id"]
        artifact.created_at = params["created_at"]
        artifact.updated_at = params["updated_at"]
        return artifact


    def __init__(self, params):
        "Initialize model"
        self.id = None
        self.created_at = None
        self.updated_at = None
        self.artifact_type = params.get("type", None)
        self.file_url = params.get("file_url", None)
        self.tags = params.get("tags", None)
        self.file_date = params.get("file_date", None)

    def save(self):
        """ Save the Resource """
        self.id = self.id or str(uuid.uuid4())
        self.created_at = datetime.datetime.now().isoformat()
        self.updated_at = datetime.datetime.now().isoformat()
        body = {
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "file_url": self.file_url,
            "tags": self.tags,
            "file_date": self.file_date
        }
        try:
            current_app.es.index(
                index="artifact",
                doc_type=self.artifact_type,
                id=self.id,
                body=body)
            return self, 201
        except ConflictError:
            raise NotSaved

    def update(self, params):
        """ Update the Resource """
        if not self.id:
            raise NotInitialized

        self.updated_at = datetime.datetime.now().isoformat()
        current_app.es.update(
            index="artifact",
            doc_type=self.artifact_type,
            id=self.id,
            body={
                "doc": params
            })
        return True

    def delete(self):
        """ Delete the Resource """
        current_app.es.delete(
            index="artifact",
            doc_type=self.artifact_type,
            id=self.id)

class NotFound(Exception):
    """ Throw when the Resource could not be found """

class NotInitialized(Exception):
    """ Throw when update is called on unitinitialized Resource """

class NotSaved(Exception):
    """ Throw when Resource could not be saved """