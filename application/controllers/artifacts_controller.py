"""
Handles all logic of the artefacts api
"""
import os
import uuid
import datetime
import werkzeug
from flask import current_app, request
from flask_restful import reqparse
from application.errors import NotFound, NotSaved
from application.models.artifact import Artifact
from .application_controller import ApplicationController

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


def search_params():
    """ Defines and validates search params """
    parser = reqparse.RequestParser()
    parser.add_argument("search", default="")
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
    parser.add_argument("image", dest="file", required=True,
                        type=werkzeug.datastructures.FileStorage, location='files')
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


def allowed_file(filename):
    """checks if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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

        return {"images": result}, 200

    def create(self):
        "Logic for creating an artifact"

        if not current_app.es:
            return {"error": "search engine not available"}, 503

        params = create_params()

        params["file_date"] = datetime.datetime.now().isoformat()
        uploaded_file = params["file"]
        if not allowed_file(uploaded_file.filename):
            return {"error": "file is not not allowed"}, 400

        filename = str(uuid.uuid4()) + "_" + \
            werkzeug.utils.secure_filename(uploaded_file.filename)
        file_url = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        uploaded_file.save(file_url)
        params["file_url"] = filename
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
            existing_tags = getattr(artifact, "tags")
            new_list = existing_tags + list(set(params["tags"]) - set(existing_tags))

            artifact.update({"tags": new_list})
            return '', 204
        except NotFound:
            return {"error": "not found"}, 404
