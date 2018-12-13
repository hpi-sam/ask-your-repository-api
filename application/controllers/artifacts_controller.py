"""
Handles all logic of the artefacts api
"""
import os
import uuid
import datetime
import werkzeug
from flask import current_app
from webargs.flaskparser import use_args
from application.errors import NotFound
import application.controllers.error_handling.request_parsing # pylint: disable=W0611
from application.base import respond_with
from application.models.artifact import Artifact
from application.controllers.error_handling.es_connection import check_es_connection
from application.validators import artifacts_validator
from .application_controller import ApplicationController

class ArtifactsController(ApplicationController):
    """ Controller for Artifacts """

    method_decorators = [check_es_connection]

    def show(self, object_id):
        "Logic for getting a single artifact"

        try:
            artifact = Artifact.find(object_id)
            return respond_with(artifact)
        except NotFound:
            return {"error": "not found"}, 404

    @use_args(artifacts_validator.search_args())
    def index(self, params):
        "Logic for querying several artifacts"

        artifacts = Artifact.search(params)

        return {"images": respond_with(artifacts)}, 200

    @use_args(artifacts_validator.create_args())
    def create(self, params):
        "Logic for creating an artifact"
        params["file_date"] = datetime.datetime.now()
        uploaded_file = params["file"]
        filename = str(uuid.uuid4()) + "_" + \
            werkzeug.utils.secure_filename(uploaded_file.filename)
        file_url = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        uploaded_file.save(file_url)
        params["file_url"] = filename
        artifact = Artifact(params)

        artifact.save()
        return respond_with(artifact), 200

    @use_args(artifacts_validator.update_args())
    def update(self, params, object_id):
        "Logic for updating an artifact"
        object_id = params.pop("id")
        try:
            artifact = Artifact.find(str(object_id))
            artifact.update(params)
            return '', 204
        except NotFound:
            return {"error": "not found"}, 404

    @use_args(artifacts_validator.delete_args())
    def delete(self, params, object_id):
        "Logic for deleting an artifact"
        object_id = params["id"]
        try:
            artifact = Artifact.find(str(object_id))
            artifact.delete()
            return '', 204
        except NotFound:
            return {"error": "not found"}, 404
