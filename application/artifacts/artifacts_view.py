"""
Handles all logic of the artifacts api
"""
import logging
import datetime
import os
import uuid
from pathlib import Path
from PIL import Image

import werkzeug
from flask import current_app, abort
from flask_apispec import MethodResource, use_kwargs, marshal_with
from flask_jwt_extended import jwt_optional, get_jwt_identity
from flask_socketio import emit

from application.artifacts import artifacts_validator
from application.artifacts.artifact_builder import ArtifactBuilder
from application.artifacts.artifact_schema import ARTIFACT_SCHEMA, ARTIFACTS_SCHEMA
from application.artifacts.elastic import ElasticSearcher
from application.artifacts.image_recognition import ImageRecognizer
from application.artifacts.synonyms import SynonymGenerator
from application.errors import check_es_connection
from application.extensions import socketio
from application.responders import respond_with, no_content
from application.socketio_parser import use_args as socketio_args
from application.teams.team import Team
from .artifact import Artifact


@socketio.on("SYNCHRONIZED_SEARCH")
@socketio_args(artifacts_validator.search_args())
def synchronized_search(params):
    """Called from client when presentation mode is on"""
    artifacts = _search_artifacts(params)

    emit("START_PRESENTATION", respond_with(artifacts), room=str(params["team_id"]), broadcast=True)


def _search_artifacts(params):
    search_args = params.get("search")
    if search_args is not None:
        params["synonyms"] = SynonymGenerator(search_args).get_synonyms()
        elastic_artifacts = ElasticSearcher.build_artifact_searcher(params).search()

        artifacts = []
        for elastic_artifact in elastic_artifacts:
            try:
                neo_artifact = Artifact.find_by(id_=elastic_artifact["_id"])
                setattr(neo_artifact, "score", elastic_artifact["_score"])
                artifacts.append(neo_artifact)
            except Artifact.DoesNotExist:
                pass
                # es and neo out of sync have to resync
    else:
        artifacts = _find_multiple_by(params)
    return artifacts


def _find_multiple_by(params):
    team = Team.find_by(id_=params.get("team_id"), force=False)
    if team is None:
        artifacts = Artifact.nodes
    else:
        artifacts = team.artifacts
    _from = params.get("offset", 0)
    _to = params.get("limit", 10) + _from
    return artifacts.order_by("created_at")[_from:_to]


class ArtifactView(MethodResource):
    """Access Artifacts by id"""

    @use_kwargs(artifacts_validator.get_args())
    @marshal_with(ARTIFACT_SCHEMA)
    def get(self, **params):
        """Logic for getting a single artifact"""
        try:
            artifact = Artifact.find_by(id_=params["id"])
            return artifact
        except Artifact.DoesNotExist:
            return abort(404, "artifact not found")

    @use_kwargs(artifacts_validator.update_args())
    @marshal_with(None, code=204)
    def put(self, **params):
        """Logic for updating an artifact"""
        return self.patch(**params)

    @use_kwargs(artifacts_validator.update_args())
    @marshal_with(None, code=204)
    def patch(self, **params):
        """Logic for updating an artifact"""
        try:
            artifact = Artifact.find_by(id_=params.pop("id"))
            builder = ArtifactBuilder.for_artifact(artifact)
            builder.update_with(**params)
            return no_content()
        except Artifact.DoesNotExist:
            return abort(404, "artifact not found")

    @use_kwargs(artifacts_validator.delete_args())
    @marshal_with(None, 204)
    def delete(self, **params):
        """Logic for deleting an artifact"""
        try:
            artifact = Artifact.find_by(id_=params["id"])
            filename_without_ext = os.path.splitext(artifact.file_url)[0]
            self._delete_files_starting_with(filename_without_ext)
            artifact.delete()
            return no_content()
        except Artifact.DoesNotExist:
            return abort(404, "artifact not found")

    def _delete_files_starting_with(self, start_string):
        for p in Path(current_app.config["UPLOAD_FOLDER"]).glob(f"{start_string}*"):
            p.unlink()


class ArtifactsView(MethodResource):
    """Controller for Artifacts"""

    method_decorators = [check_es_connection]

    @jwt_optional
    @check_es_connection
    @use_kwargs(artifacts_validator.search_args())
    @marshal_with(ARTIFACTS_SCHEMA)
    def get(self, **params):
        """Logic for querying several artifacts"""
        query_logger = logging.getLogger('query_logger')
        print('halo i bims d1 logger')
        query_logger.info(f"search query: '{params['search']}' offset: {params['offset']} limit: {params['limit']} team: '{params['team_id']}' user: '{get_jwt_identity()}'")
        
        artifacts = _search_artifacts(params)

        if params["notify_clients"]:
            socketio.emit("START_PRESENTATION", room=str(params["team_id"]), data=respond_with(artifacts))

        return artifacts

    @jwt_optional
    @use_kwargs(artifacts_validator.create_args())
    @marshal_with(ARTIFACT_SCHEMA)
    def post(self, **params):
        """Logic for creating an artifact"""
        metadata = self._upload_file(params)
        self._add_user_to_params(metadata)
        artifact = self._create_artifact(params, metadata)
        ImageRecognizer.auto_add_tags(artifact)
        return artifact

    def _add_user_to_params(self, params):
        user_id = get_jwt_identity()
        params["user_id"] = user_id

    def _create_artifact(self, params, metadata):
        params.update(metadata)
        artifact = ArtifactBuilder().build_with(**params)
        artifact.save()
        return artifact

    @use_kwargs(artifacts_validator.update_many_args())
    @marshal_with(None, 204)
    def patch(self, **params):
        """Logic for updating multiple artifacts at once"""

        for update_data in params["artifacts"]:
            id = update_data.pop("id")
            try:
                artifact = Artifact.find_by(id_=id)
                builder = ArtifactBuilder.for_artifact(artifact)
                builder.update_with(override_tags=False, **update_data)
            except Artifact.DoesNotExist:
                return abort(404, f"failed at <{id}>: not found")

        return no_content()

    def _upload_file(self, params):
        file_saver = FileSaver(params["file"])
        file_saver.save()

        image_resizer = ImageResizer(file_saver.file_path)
        image_resizer.save_sizes()

        return file_saver.get_metadata()


class ImageResizer:  # pylint:disable=too-few-public-methods
    """Saves resized versions of an image to disk"""

    widths = [320, 480, 640, 750, 1080]

    def __init__(self, file_path):
        self.image = Image.open(file_path)
        self.original_file_name = file_path.split("/")[-1]

    def save_sizes(self):
        """Saves resized image for all defined widths"""
        for width in self.widths:
            height = self._calculate_height(width)
            resized_image = self.image.resize((width, height), Image.ANTIALIAS)
            resized_image.save(self._generate_file_path(width))
            resized_image.close()

    def _generate_file_path(self, width):
        file_name = self._generate_file_name(width)
        return os.path.join(current_app.config["UPLOAD_FOLDER"], file_name)

    def _generate_file_name(self, width):
        """Generate filename for a resized image of given width"""
        [prefix, suffix] = self.original_file_name.rsplit(".", 1)
        filename = f"{prefix}_{width}w.{suffix}"
        return filename

    def _calculate_height(self, width):
        """Calculate height of resized image with given width"""
        width_ratio = width / self.image.size[0]
        height = int(self.image.size[1] * width_ratio)
        return height


class FileSaver:
    """Saves a file to disk and creates according metadata"""

    def __init__(self, file):
        self.file = file
        self.file_date = None
        self.file_name = None
        self.file_path = None

    def save(self):
        """Saves an artifact to disk."""
        self._create_metadata()
        self._save_file()

    def get_metadata(self):
        """Get Metadata as hash (file_url and file_date)"""
        return {"file_url": self.file_name, "file_date": self.file_date}

    def _create_metadata(self):
        self.file_name = self._generate_filename()
        self.file_date = datetime.datetime.now()
        self.file_path = self._file_path()

    def _save_file(self):
        self.file.save(self.file_path)
        self.file.close()

    def _file_path(self):
        return os.path.join(current_app.config["UPLOAD_FOLDER"], self.file_name)

    def _generate_filename(self):
        return str(uuid.uuid4()) + "_" + werkzeug.utils.secure_filename(self.file.filename)
