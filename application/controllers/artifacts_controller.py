"""
Handles all logic of the artefacts api
"""
import os
import uuid
import datetime
import werkzeug
from flask import current_app, request
from application.errors import NotFound
import application.controllers.error_handling.request_parsing # pylint: disable=W0611
from application.models.artifact import Artifact
from application.controllers.error_handling.es_connection import check_es_connection
from .application_controller import ApplicationController
from application.validators import artifacts_validator

class ArtifactsController(ApplicationController):
    """ Controller for Artifacts """

    method_decorators = [check_es_connection]

    def show(self, object_id):
        "Logic for getting a single artifact"

        try:
            return Artifact.find(object_id).to_json()
        except NotFound:
            return {"error": "not found"}, 404

    def index(self):
        "Logic for querying several artifacts"
        params = artifacts_validator.search_args()

        result = Artifact.search(params)

        return {"images": result}, 200

    def create(self):
        "Logic for creating an artifact"
        params = artifacts_validator.create_args()

        params["file_date"] = datetime.datetime.now().isoformat()
        uploaded_file = params["file"]
        filename = str(uuid.uuid4()) + "_" + \
            werkzeug.utils.secure_filename(uploaded_file.filename)
        file_url = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        uploaded_file.save(file_url)
        params["file_url"] = filename
        artifact = Artifact(params)

        artifact.save()
        return vars(artifact), 200

    def update(self, object_id): # pylint: disable=unused-argument
        "Logic for updating an artifact"
        params = artifacts_validator.update_args()
        artifact_id = str(params.pop('id'))
        try:
            artifact = Artifact.find(artifact_id)
            artifact.update(params)
            return '', 204
        except NotFound:
            return {"error": "not found"}, 404

    def delete(self, object_id): # pylint: disable=unused-argument
        "Logic for deleting an artifact"

        params = artifacts_validator.delete_args()
        artifact_id = str(params.pop('id'))

        try:
            artifact = Artifact.find(artifact_id)
            artifact.delete()
            return '', 204
        except NotFound:
            return {"error": "not found"}, 404
