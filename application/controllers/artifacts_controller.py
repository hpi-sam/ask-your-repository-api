"""
Handles all logic of the artifacts api
"""
import datetime
import os
import uuid
from pathlib import Path

import werkzeug
from flask import current_app
from flask_jwt_extended import jwt_optional, get_jwt_identity
from flask_socketio import emit
from webargs.flaskparser import use_args

from application.models import Artifact, Team
from application.models.elastic import ElasticSearcher
from .application_controller import ApplicationController
from ..error_handling.es_connection import check_es_connection
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
    artifacts = _search_artifacts(params)

    emit('START_PRESENTATION',
         respond_with(artifacts),
         room=str(params["team_id"]),
         broadcast=True
         )


def _search_artifacts(params):
    search_args = params.get('search')
    if search_args is not None:
        params['search'] = SynonymGenerator(search_args).get_synonyms()
        elastic_artifacts = ElasticSearcher.build_artifact_searcher(params).search()

        artifacts = []
        for elastic_artifact in elastic_artifacts:
            try:
                neo_artifact = Artifact.find_by(id_=elastic_artifact['_id'])
                setattr(neo_artifact, 'score', elastic_artifact['_score'])
                artifacts.append(neo_artifact)
            except Artifact.DoesNotExist:
                pass
                # es and neo out of sync have to resync
    else:
        artifacts = _find_multiple_by(params)
    return artifacts


def _find_multiple_by(params):
    team = Team.find_by(id_=params.get('team_id'), force=False)
    if team is None:
        artifacts = Artifact.nodes
    else:
        artifacts = team.artifacts
    _from = params.get('offset', 0)
    _to = params.get('limit', 10) + _from
    return artifacts.order_by('created_at')[_from:_to]


class ArtifactsController(ApplicationController):
    """ Controller for Artifacts """

    method_decorators = [check_es_connection]

    def show(self, object_id):
        """Logic for getting a single artifact"""
        try:
            artifact = Artifact.find_by(id_=object_id)
            return respond_with(artifact)
        except Artifact.DoesNotExist:
            return {"error": "not found"}, 404

    @use_args(artifacts_validator.search_args())
    def index(self, params):
        """Logic for querying several artifacts"""
        artifacts = _search_artifacts(params)

        if params['notify_clients']:
            socketio.emit('START_PRESENTATION',
                          room=str(params["team_id"]),
                          data=respond_with(artifacts)
                          )

        return {"images": respond_with(artifacts)}, 200

    @jwt_optional
    @use_args(artifacts_validator.create_args())
    def create(self, params):
        """Logic for creating an artifact"""
        metadata = self._upload_file(params)
        self._add_user_to_params(metadata)
        artifact = self._create_artifact(params, metadata)
        ImageRecognizer.auto_add_tags(artifact)
        return respond_with(artifact), 200

    def _add_user_to_params(self, params):
        user_id = get_jwt_identity()
        params['user_id'] = user_id

    def _create_artifact(self, params, metadata):
        params.update(metadata)
        artifact = ArtifactBuilder().build_with(**params)
        artifact.save()
        return artifact

    @use_args(artifacts_validator.update_args())
    def update(self, params, object_id):
        """Logic for updating an artifact"""
        object_id = params.pop("id")
        try:
            artifact = Artifact.find_by(id_=object_id)
            builder = ArtifactBuilder.for_artifact(artifact)
            builder.update_with(**params)
            return no_content()
        except Artifact.DoesNotExist:
            return {"error": "not found"}, 404

    @use_args(artifacts_validator.update_many_args())
    def update_many(self, params):
        """ Logic for updating multiple artifacts at once """

        for update_data in params["artifacts"]:
            object_id = update_data.pop("id")
            try:
                artifact = Artifact.find_by(id_=object_id)
                builder = ArtifactBuilder.for_artifact(artifact)
                builder.update_with(override_tags=False, **update_data)
            except Artifact.DoesNotExist:
                return {"error": f"failed at <{object_id}>: not found"}, 404

        return no_content()

    @use_args(artifacts_validator.delete_args())
    def delete(self, params, object_id):
        """Logic for deleting an artifact"""
        object_id = params["id"]
        try:
            artifact = Artifact.find_by(id_=object_id)
            filename_without_ext = os.path.splitext(artifact.file_url)[0]
            self._delete_files_starting_with(filename_without_ext)
            artifact.delete()
            return no_content()
        except Artifact.DoesNotExist:
            return {"error": "not found"}, 404

    def _delete_files_starting_with(self, start_string):
        for p in Path(current_app.config['UPLOAD_FOLDER']).glob(f"{start_string}*"):
            p.unlink()

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
