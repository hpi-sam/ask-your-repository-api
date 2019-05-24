"""
Handles all logic of the artifacts api
"""
import logging

from flask import abort, current_app
from flask_apispec import MethodResource, use_kwargs, marshal_with
from flask_jwt_extended import jwt_optional, get_jwt_identity, jwt_required
from flask_socketio import emit

from application.artifacts import artifacts_validator
from application.artifacts.artifact_connector import ArtifactConnector
from application.artifacts.artifact_recommendation import ArtifactRecommendator
from application.artifacts.artifact_creation import ArtifactCreator
from application.artifacts.artifact_schema import ARTIFACT_SCHEMA, ARTIFACTS_SCHEMA
from application.artifacts.elastic import ElasticSearcher
from application.artifacts.synonyms import SynonymGenerator
from application.errors import check_es_connection
from application.extensions import socketio
from application.responders import marshal_data, no_content
from application.socketio_parser import use_args as socketio_args
from application.teams.team import Team
from .artifact import Artifact
from .elastic.sync_jobs import resync_elasticsearch_eventually


@socketio.on("SYNCHRONIZED_SEARCH")
@socketio_args(artifacts_validator.search_args())
def synchronized_search(params):
    """Called from client when presentation mode is on"""
    artifacts = _search_artifacts(params)
    emit(
        "START_PRESENTATION",
        _socketio_data(artifacts, params.get("search")),
        room=str(params["team_id"]),
        broadcast=True,
    )


def _socketio_data(artifacts, search):
    """Returns the artifacts data with search included"""
    data = marshal_data(artifacts, ARTIFACTS_SCHEMA)
    data["search"] = search
    return data


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
                # neo and elasticsearch are out of sync so add a resync job
                resync_elasticsearch_eventually()
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
            current_app.redis.lpush('last_visited', artifact.id_)
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
            builder = ArtifactConnector.for_artifact(artifact)
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
            artifact.delete()
            return no_content()
        except Artifact.DoesNotExist:
            return abort(404, "artifact not found")

    @use_kwargs(artifacts_validator.related_args())
    @marshal_with(ARTIFACTS_SCHEMA)
    def related(self, **params):
        """Logic for getting the related artifacts of an artifact"""
        try:
            artifact = Artifact.find_by(id_=params["id"])
        except Artifact.DoesNotExist:
            return abort(404, "artifact not found")

        recommendator = ArtifactRecommendator(artifact)
        artifacts = recommendator.run(params["limit"])

        return artifacts

class ArtifactsView(MethodResource):
    """Controller for Artifacts"""

    method_decorators = [check_es_connection]

    @jwt_required
    @check_es_connection
    @use_kwargs(artifacts_validator.search_args())
    @marshal_with(ARTIFACTS_SCHEMA)
    def get(self, **params):
        """Logic for querying several artifacts"""
        query_logger = logging.getLogger("query_logger")
        query_logger.info(str(params), extra={"user": str(get_jwt_identity())})
        artifacts = _search_artifacts(params)

        if params["notify_clients"]:
            socketio.emit(
                "START_PRESENTATION", room=str(params["team_id"]), data=_socketio_data(artifacts, params.get("search"))
            )

        return artifacts

    @jwt_optional
    @use_kwargs(artifacts_validator.create_args())
    @marshal_with(ARTIFACT_SCHEMA)
    def post(self, **params):
        """Logic for creating an artifact"""
        creator = ArtifactCreator(
            params.pop("file"), owner_id=get_jwt_identity(), team_id=params.pop("team_id"), **params
        )
        return creator.create_artifact()

    @use_kwargs(artifacts_validator.update_many_args())
    @marshal_with(None, 204)
    def patch(self, **params):
        """Logic for updating multiple artifacts at once"""

        for update_data in params["artifacts"]:
            id = update_data.pop("id")
            try:
                artifact = Artifact.find_by(id_=id)
                builder = ArtifactConnector.for_artifact(artifact)
                builder.update_with(override_tags=False, **update_data)
            except Artifact.DoesNotExist:
                return abort(404, f"failed at <{id}>: not found")

        return no_content()
