"""
Handles all logic of the artefacts api
"""

import datetime
from flask import current_app
from flask_restful import Resource, reqparse
from application.errors import NotFound, NotSaved
from .artifacts_helper import Artifact


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
    parser.add_argument("file_url")
    parser.add_argument("tags", action="append", default=[], location="json")
    return parser.parse_args()


def update_params():
    """ Defines and validates update params """
    parser = reqparse.RequestParser()
    parser.add_argument("file_url")
    parser.add_argument("tags", action="append", default=[])
    return parser.parse_args()


class ArtifactResource(Resource):
    """ Defines Routes on member """

    def get(self, artifact_id):
        "Logic for getting a single artifact"

        if not current_app.es:
            return {"error": "search engine not available"}, 503

        try:
            return vars(Artifact.find(artifact_id))
        except NotFound:
            return {"error": "not found"}, 404

    def put(self, artifact_id):
        "Logic for updating an artifact"

        if not current_app.es:
            return {"error": "search engine not available"}, 503

        params = update_params()
        try:
            artifact = Artifact.find(artifact_id)
            artifact.update(params)
            return '', 204
        except NotFound:
            return {"error": "not found"}, 404

    def delete(self, artifact_id):
        "Logic for deleting an artifact"

        if not current_app.es:
            return {"error": "search engine not available"}, 503

        try:
            artifact = Artifact.find(artifact_id)
            artifact.delete()
            return '', 204
        except NotFound:
            return {"error": "not found"}, 404


class ArtifactsResource(Resource):
    """ Defines Routes on collection """

    def get(self):
        "Logic for querying several artifacts"

        if not current_app.es:
            return {"error": "search engine not available"}, 503

        params = search_params()

        result = Artifact.search(params)

        return {"results": result}, 200

    def post(self):
        "Logic for creating an artifact"

        if not current_app.es:
            return {"error": "search engine not available"}, 503

        params = create_params()
        params["file_date"] = datetime.datetime.now().isoformat()
        # params["tags"] = ", ".join(params["tags"])
        artifact = Artifact(params)

        try:
            artifact.save()
            return vars(artifact), 200
        except NotSaved:
            return {"error": "artifact could not be saved"}, 404
