""" Define superclass models """

import datetime
import uuid

from flask import current_app

from elasticsearch.exceptions import NotFoundError  # noqa
from application.base import BaseSchema
from application.errors import NotFound, NotInitialized


class ESModel:
    """ Handles saving and searching """

    index = None
    schema = BaseSchema

    @classmethod
    def all(cls, create_objects=True):
        """
        Find all es objects. Needs to fire two queries.
        One to get the number of objects and one two return the objects.
        Necessary because search has a default size value of 10.
        :param bool create_objects: Boolean to define if a list of
            model dictionaries or objects should be returned.
        :returns: list of model dictionaries or objects
        """

        get_all = current_app.es.search(
            index=cls.index,
            body={"from": 0, "size": 1}
        )
        size = get_all["hits"]["total"]
        result = current_app.es.search(
            index=cls.index,
            body={"from": 0, "size": size}
        )
        return cls.create_multiple_from_search(result, create_objects=create_objects)

    @classmethod
    def find(cls, object_id, create_object=True):
        """
        Finds object by id
        :param bool create_object: Boolean to define if a
            model dictionary or objects should be returned.
        :returns model object or dictionary
        """
        try:
            result = current_app.es.get(
                index=cls.index,
                doc_type="_all",
                id=str(object_id)
            )
            return cls.create_from_es(result, create_object=create_object)
        except NotFoundError:
            raise NotFound()

    @classmethod
    def find_all(cls, image_ids=None, create_objects=True):
        """
        Find multiple objects by a list of ids
        :param bool create_objects: Boolean to define if a list of
            model dictionaries or objects should be returned.
        :returns: list of model dictionaries or objects
        """
        ids = [str(image_id) for image_id in image_ids]
        try:
            result = current_app.es.mget(
                index=cls.index,
                doc_type="_all",
                body={
                    "ids": ids
                }
            )
            return cls.create_multiple_from_mget(result, create_objects=create_objects)
        except NotFoundError:
            raise NotFound()

    @classmethod
    def search(cls, params, create_objects=True):
        """
        Finds multiple objects by params.
        :param bool create_objects: Boolean to define if a list of
            model dictionaries or objects should be returned.
        :returns: list of model dictionaries or objects
        """
        result = current_app.es.search(
            # search_type is counteracting the sharding effect that messes with idf:
            # https://www.compose.com/articles/how-scoring-works-in-elasticsearch/
            search_type="dfs_query_then_fetch",
            index=cls.index,
            doc_type=params["types"],
            body=params["search_body"])
        return cls.create_multiple_from_search(result, create_objects=create_objects)

    @classmethod
    def create_multiple_from_search(cls, es_response, create_objects=True):
        """
        Creates multipe model objects from an
        elasticsearch search query response
        """

        params = cls.parse_search_response(es_response)
        result = cls.schema(model=cls, many=True, create_objects=create_objects).load(params).data
        return result

    @classmethod
    def create_multiple_from_mget(cls, es_response, create_objects=True):
        """
        Creates multipe model objects from an
        elasticsearch mget query response
        """

        response = []
        for doc in es_response["docs"]:
            response.append(cls.parse_response(doc))

        return cls.schema(model=cls, many=True, create_objects=create_objects).load(response).data

    @classmethod
    def create_from_es(cls, es_response, create_object=True):
        """ Create a Resource from elastic_search """
        params = cls.parse_response(es_response)
        es_object = cls.schema(model=cls, create_objects=create_object).load(params).data
        return es_object

    @classmethod
    def parse_response(cls, params):
        """ Parse dictionary returned by elasticsearch """
        result = {}
        result["id"] = params["_id"]
        result["type"] = params["_type"]
        for (key, value) in params["_source"].items():
            result[key] = value

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
        self.id = params.get("id", None)
        self.created_at = params.get("created_at", None)
        self.updated_at = params.get("updated_at", None)
        self.type = params.get("type", None)

    def save(self):
        """ Save the Resource """
        self.id = self.id or uuid.uuid4()
        self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()
        body = self.schema(model=self.__class__).dump(self).data
        object_id = body.pop("id")
        object_type = body.pop("type")

        current_app.es.index(
            index=self.index,
            doc_type=object_type,
            id=object_id,
            body=body)
        return self, 201

    def update(self, params):
        """ Update the Resource """
        if not self.id:
            raise NotInitialized()

        self.updated_at = datetime.datetime.now()
        db_params = self.schema(model=self.__class__,
                                only=('id', 'type', 'updated_at')).dump(self).data
        if "updated_at" not in params:
            params["updated_at"] = db_params["updated_at"]
        current_app.es.update(
            index=self.index,
            doc_type=db_params["type"],
            id=db_params["id"],
            body={
                "doc": params
            })
        return True

    def delete(self):
        """ Delete the Resource """
        db_params = self.schema(model=self.__class__, only=('id', 'type')).dump(self).data
        current_app.es.delete(
            refresh='wait_for',
            index=self.index,
            doc_type=db_params["type"],
            id=db_params["id"], )
