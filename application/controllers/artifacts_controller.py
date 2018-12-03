"""
Handles all logic of the artefacts api
"""

import datetime
from flask import current_app, request
from flask_restful import reqparse, Resource
from application.errors import NotFound, NotSaved
from .application_controller import ApplicationController
from application.models.artifact import Artifact


def search_params():
    """ Defines and validates search params """
    parser = reqparse.RequestParser()
    parser.add_argument("searchTerm", default="", dest="search")
    parser.add_argument("type", action="append", dest="types")
    parser.add_argument("start_date")
    parser.add_argument("end_date")
    parser.add_argument("offset", type=int, default=0)
    parser.add_argument("limit", type=int, default=12)

    return parser.parse_args()


def create_params():
    """ Defines and validates create params """
    parser = reqparse.RequestParser()
    parser.add_argument("type", default="image")
    parser.add_argument("file_url", location="json")
    parser.add_argument("tags", action="append", default=[], location="json")
    return parser.parse_args()


def update_params():
    """ Defines and validates update params """
    parser = reqparse.RequestParser()
    parser.add_argument("file_url")
    parser.add_argument("tags", action="append", default=[])
    return parser.parse_args()


def add_tags_params():
    """ Defines and validates add tags params """
    parser = reqparse.RequestParser()
    parser.add_argument("tags", action="append", default=[])
    return parser.parse_args()


class ArtifactsController(ApplicationController):
    """ Controller for Artifacts """

    def show(self, object_id):
        "Logic for getting a single artifact"

        if not current_app.es:
            return {"error": "search engine not available"}, 503

        try:
            return vars(Artifact.find(object_id))
        except NotFound:
            return {"error": "not found"}, 404

    def index(self):
        "Logic for querying several artifacts"

        if not current_app.es:
            return {"error": "search engine not available"}, 503

        params = search_params()

        result = Artifact.search(params)

        return {"results": result}, 200

    def create(self):
        "Logic for creating an artifact"

        if not current_app.es:
            return {"error": "search engine not available"}, 503

        params = create_params()
        params["file_date"] = datetime.datetime.now().isoformat()
        print(params)
        # params["tags"] = ", ".join(params["tags"])
        artifact = Artifact(params)

        try:
            artifact.save()
            return vars(artifact), 200
        except NotSaved:
            return {"error": "artifact could not be saved"}, 404

    def update(self, object_id):
        "Logic for updating an artifact"

        if not current_app.es:
            return {"error": "search engine not available"}, 503

        params = update_params()
        try:
            artifact = Artifact.find(object_id)
            artifact.update(params)
            return '', 204
        except NotFound:
            return {"error": "not found"}, 404

    def delete(self, object_id):
        "Logic for deleting an artifact"

        if not current_app.es:
            return {"error": "search engine not available"}, 503

        try:
            artifact = Artifact.find(object_id)
            artifact.delete()
            return '', 204
        except NotFound:
            return {"error": "not found"}, 404

    def add_tags(self, object_id):
        """ Adds tags to an existing artifact """

        if not current_app.es:
            return {"error": "search engine not available"}, 503
        params = add_tags_params()
        try:
            artifact = Artifact.find(object_id)
            print(vars(artifact))
            new_list = getattr(artifact, "tags") + params["tags"]
            artifact.update({
                "tags": list(set(new_list))})
            return '', 204
        except NotFound:
            return {"error": "not found"}, 404
