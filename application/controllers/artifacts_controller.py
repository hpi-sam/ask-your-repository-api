"""
Handles all logic of the artifacts api
"""
import os
import uuid
import datetime
import werkzeug
from flask import current_app
from webargs.flaskparser import use_args
from ..responders import no_content, respond_with
from ..errors import NotFound
from ..error_handling.es_connection import check_es_connection
from ..models.artifact import Artifact
from ..validators import artifacts_validator
from ..recognition.image_recognition import ImageRecognizer
from .application_controller import ApplicationController

class ArtifactsController(ApplicationController):
    """ Controller for Artifacts """

    method_decorators = [check_es_connection]

    def show(self, object_id):
        """Logic for getting a single artifact"""

        try:
            artifact = Artifact.find(object_id)
            return respond_with(artifact)
        except NotFound:
            return {"error": "not found"}, 404

    @use_args(artifacts_validator.search_args())
    def index(self, params):
        """Logic for querying several artifacts"""

        artifacts = Artifact.search(params)

        return {"images": respond_with(artifacts)}, 200

    @use_args(artifacts_validator.create_args())
    def create(self, params):
        """Logic for creating an artifact"""
        params = self.upload_file(params)
        artifact = Artifact(params)

        artifact.save()
        ImageRecognizer.auto_add_tags(artifact)
        return respond_with(artifact), 200

    @use_args(artifacts_validator.update_args())
    def update(self, params, object_id):
        """Logic for updating an artifact"""
        object_id = params.pop("id")
        try:
            artifact = Artifact.find(object_id)
            artifact.update(params)
            return no_content()
        except NotFound:
            return {"error": "not found"}, 404

    @use_args(artifacts_validator.update_many_args())
    def update_many(self, params):
        """ Logic for updating multiple artifacts at once """

        for update_data in params["artifacts"]:
            object_id = update_data.pop("id")
            try:
                artifact = Artifact.find(object_id)
                artifact.update(update_data)
            except NotFound:
                return {"error": f"failed at <{object_id}>: not found"}, 404

        return no_content()

    @use_args(artifacts_validator.delete_args())
    def delete(self, params, object_id):
        """Logic for deleting an artifact"""
        object_id = params["id"]
        try:
            artifact = Artifact.find(object_id)
            artifact.delete()
            return no_content()
        except NotFound:
            return {"error": "not found"}, 404

    @staticmethod
    def upload_file(params):
        """Saves an artifact to the file server and returns new params for artifact creation."""
        uploaded_file = params["file"]
        filename = str(uuid.uuid4()) + "_" + \
                   werkzeug.utils.secure_filename(uploaded_file.filename)
        file_url = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        uploaded_file.save(file_url)
        params["file_url"] = filename
        params["file_date"] = datetime.datetime.now()
        return params
