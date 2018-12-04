""" Define superclass models """

import uuid
import datetime
from flask import current_app
from elasticsearch.exceptions import NotFoundError
from application.errors import NotFound, NotInitialized


class ESModel():
    """ Handles saving and searching """

    index = None
    members = []

    @classmethod
    def find(cls, object_id):
        """ Finds object by id """
        try:
            result = current_app.es.get(
                index=cls.index,
                doc_type="_all",
                id=object_id
            )
            return cls.from_es(result)
        except NotFoundError:
            raise NotFound()

    @classmethod
    def search(cls, params):
        """ Finds multiple objects by params.  """
        result = current_app.es.search(
            index=cls.index,
            doc_type=params["types"],
            body=params["search_body"])
        return cls.parse_search_params(result)

    @classmethod
    def from_es(cls, es_params):
        """ Create a Resource from elastic_search """
        params = cls.parse_params(es_params)
        es_object = cls(params)
        es_object.id = params["id"]
        es_object.created_at = params["created_at"]
        es_object.updated_at = params["updated_at"]
        return es_object

    @classmethod
    def parse_params(cls, params):
        """ Parse dictionary returned by elasticsearch """
        result = {}
        result["id"] = params["_id"]
        result["type"] = params["_type"]
        result["created_at"] = params["_source"]["created_at"]
        result["updated_at"] = params["_source"]["updated_at"]
        for member in cls.members:
            result[member] = params["_source"][member]

        return result

    @classmethod
    def parse_search_params(cls, params):
        """ Parse array of dictionaries returned by elasticsearch """
        result = []
        for hit in params["hits"]["hits"]:
            result.append(cls.parse_params(hit))
        return result

    def __init__(self, params):
        "Initialize model"
        self.id = None
        self.created_at = None
        self.updated_at = None
        self.type = params["type"]
        for member in self.members:
            setattr(self, member, params.get(member, None))

    def save(self):
        """ Save the Resource """
        self.id = self.id or str(uuid.uuid4())
        self.created_at = datetime.datetime.now().isoformat()
        self.updated_at = datetime.datetime.now().isoformat()
        body = vars(self).copy()
        del body["id"]
        del body["type"]

        current_app.es.index(
            index=self.index,
            doc_type=self.type,
            id=self.id,
            body=body)
        return self, 201

    def update(self, params):
        """ Update the Resource """
        if not self.id:
            raise NotInitialized()

        self.updated_at = datetime.datetime.now().isoformat()
        current_app.es.update(
            index=self.index,
            doc_type=self.type,
            id=self.id,
            body={
                "doc": params
            })
        return True

    def delete(self):
        """ Delete the Resource """
        current_app.es.delete(
            index=self.index,
            doc_type=self.type,
            id=self.id)
