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
    def all(cls):
        """
        Finds all es objects. Needs to fire two queries.
        One to get the number of objects and one two return the objects.
        Necessary because search has a default size value of 10.
        """

        get_all = current_app.es.search(
            index=cls.index,
        )
        size = get_all["hits"]["total"]
        result = current_app.es.search(
            index=cls.index,
            body={"from": 0, "size": size}
        )
        return cls.parse_search_response(result)

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
        return cls.parse_search_response(result)

    @classmethod
    def from_es(cls, es_response):
        """ Create a Resource from elastic_search """
        params = cls.parse_response(es_response)
        es_object = cls(params)
        es_object.id = params["id"]
        es_object.created_at = params["created_at"]
        es_object.updated_at = params["updated_at"]
        return es_object

    @classmethod
    def parse_response(cls, params):
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
    def parse_single_search_response(cls, single_response):
        """ Parses a single object from the elasticsearch response Array """
        resource = cls.parse_response(single_response)
        resource["score"] = single_response["_score"]
        return resource

    @classmethod
    def parse_search_response(cls, response):
        """ Parse array of dictionaries returned by elasticsearch """
        result = []
        for hit in response["hits"]["hits"]:
            resource = cls.parse_single_search_response(hit)
            result.append(resource)
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
