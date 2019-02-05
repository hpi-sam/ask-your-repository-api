"""
Handles all logic of the artifacts api
"""
import datetime
import os
import uuid

import werkzeug
from flask import current_app
from flask_socketio import emit
from webargs.flaskparser import use_args

from .application_controller import ApplicationController
from ..error_handling.es_connection import check_es_connection
from ..errors import NotFound
from ..extensions import socketio
from ..models.artifact_builder import ArtifactBuilder
from ..recognition.image_recognition import ImageRecognizer
from ..responders import no_content, respond_with
from ..socketio_parser import use_args as socketio_args
from ..synonyms.synonyms import SynonymGenerator
from ..validators import artifacts_validator


@socketio.on("SYNCHRONIZED_SEARCH")
@socketio_args(artifacts_validator.search_args())
def synchronized_search(params):
    """ Called from client when presentation mode is on """
    artifacts = ArtifactBuilder.search(params)

    emit('START_PRESENTATION',
         respond_with(artifacts),
         room=str(params["team_id"]),
         broadcast=True
         )


class ArtifactsController(ApplicationController):
    """ Controller for Artifacts """

    method_decorators = [check_es_connection]

    def show(self, object_id):
        """Logic for getting a single artifact"""
        try:
            artifact = ArtifactBuilder.find(object_id)
            return respond_with(artifact.neo)
        except NotFound:
            return {"error": "not found"}, 404

    @use_args(artifacts_validator.search_args())
    def index(self, params):
        """Logic for querying several artifacts"""
        search_args = params.get('search')
        if search_args is not None:
            params['search'] = SynonymGenerator(search_args).get_synonyms()

        if search_args is None:
            artifacts = ArtifactBuilder.find_multiple(params)
        else:
            artifacts = ArtifactBuilder.search(params)

        if params['notify_clients']:
            socketio.emit('START_PRESENTATION',
                          room=str(params["team_id"]),
                          data=respond_with(artifacts)
                          )

        return {"images": respond_with(artifacts)}, 200

    @use_args(artifacts_validator.create_args())
    def create(self, params):
        """Logic for creating an artifact"""
        metadata = self._upload_file(params)
        artifact = self._create_artifact(params, metadata)
        ImageRecognizer.auto_add_tags(artifact.elastic)
        return respond_with(artifact.neo), 200

    def _create_artifact(self, params, metadata):
        params.update(metadata)
        artifact = ArtifactBuilder()
        artifact.build_with(**params)
        artifact.save()
        return artifact

    @use_args(artifacts_validator.update_args())
    def update(self, params, object_id):
        """Logic for updating an artifact"""
        object_id = params.pop("id")
        try:
            artifact = ArtifactBuilder.find(object_id)
            artifact.update(**params)
            return no_content()
        except NotFound:
            return {"error": "not found"}, 404

    @use_args(artifacts_validator.update_many_args())
    def update_many(self, params):
        """ Logic for updating multiple artifacts at once """

        for update_data in params["artifacts"]:
            object_id = update_data.pop("id")
            try:
                artifact = ArtifactBuilder.find(object_id)
                artifact.update(**update_data)
            except NotFound:
                return {"error": f"failed at <{object_id}>: not found"}, 404

        return no_content()

    @use_args(artifacts_validator.delete_args())
    def delete(self, params, object_id):
        """Logic for deleting an artifact"""
        object_id = params["id"]
        try:
            artifact = ArtifactBuilder.find(object_id)
            artifact.delete()
            return no_content()
        except NotFound:
            return {"error": "not found"}, 404

    def _upload_file(self, params):
        file_saver = FileSaver(params['file'])
        file_saver.save()
        return file_saver.get_metadata()


class FileSaver:
    """Saves a file to disk and creates according metadata"""

    def __init__(self, file):
        self.file = file
        self.file_date = None
        self.filename = None

    def save(self):
        """Saves an artifact to disk."""
        self._create_metadata()
        self._save_file()

    def get_metadata(self):
        """Get Metadata as hash (file_url and file_date)"""
        return {'file_url': self.filename,
                'file_date': self.file_date}

    def _create_metadata(self):
        self.filename = self._generate_filename()
        self.file_date = datetime.datetime.now()

    def _save_file(self):
        file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], self.filename)
        self.file.save(file_path)

    def _generate_filename(self):
        return str(uuid.uuid4()) + "_" + \
               werkzeug.utils.secure_filename(self.file.filename)
