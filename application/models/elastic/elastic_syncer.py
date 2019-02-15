""" Logic for synchronizing Neo with Elasticsearch"""
from flask import current_app

import application.models.artifact
from application.errors import NotFound
from application.models.elastic.elastic_artifact import ElasticArtifact
from application.schemas.artifact_schema import NeoArtifactSchema, ArtifactSchema


class ElasticSyncer:
    """ Synchronization class """

    @classmethod
    def sync_enabled(cls):
        """ Check if synchonization is enabled """
        return current_app.config["ES_SYNC"]

    @classmethod
    def set_sync_status(cls, sync):
        """ Set synchronization to enabled or disabled"""
        current_app.config["ES_SYNC"] = sync

    def __init__(self):
        self.artifacts = []

    @classmethod
    def for_artifact(cls, artifact):
        """ Create a Syncer for one artifact """
        syncer = cls()
        syncer.artifacts = [artifact]
        return syncer

    @classmethod
    def for_artifacts(cls, artifacts):
        """ Create a Syncer for multiple artifacts """
        syncer = cls()
        syncer.artifacts = artifacts
        return syncer

    @classmethod
    def sync_everything(cls):
        """ Synchronize all artifacts from neo to elasticsearch """
        syncer = cls()
        syncer.artifacts = application.models.artifact.Artifact.all()
        syncer.sync()

    def sync(self):
        """ Start the syncrhonization process """
        if ElasticSyncer.sync_enabled():
            self._sync_all(self.artifacts)

    def _sync_all(self, artifacts):
        for artifact in artifacts:
            self._update_or_create(artifact)

    def _update_or_create(self, artifact):
        try:
            self._update_artifact(artifact)
        except NotFound:
            self._create_elastic_artifact(artifact)

    def delete(self):
        """ Delete the artifacts this syncer was created for in ES """
        if ElasticSyncer.sync_enabled():
            self._delete_all(self.artifacts)

    def _delete_all(self, artifacts):
        for artifact in artifacts:
            self._safe_delete(artifact)

    def _safe_delete(self, artifact):
        try:
            self._delete_artifact(artifact)
        except NotFound:
            return

    def _update_artifact(self, artifact):
        elastic_artifact = ElasticArtifact.find(artifact.id_)
        elastic_artifact.update(self._artifact_dump(artifact))

    def _delete_artifact(self, artifact):
        elastic_artifact = ElasticArtifact.find(artifact.id_)
        elastic_artifact.delete()

    def _create_elastic_artifact(self, artifact):
        params = self._artifact_dump(artifact)
        ElasticArtifact(params).save()

    def _artifact_dump(self, artifact):
        data = NeoArtifactSchema(application.models.artifact.Artifact,
                                 decorate=False).dump(artifact).data
        data['type'] = 'image'
        data["id"] = data.pop("id_")
        data["tags"] = data.pop("tags_list")
        load_result = ArtifactSchema(ElasticArtifact, create_objects=False).load(data)
        return load_result.data
