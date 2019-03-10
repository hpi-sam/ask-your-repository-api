""" Logic for synchronizing Neo with Elasticsearch"""

from elasticsearch import exceptions  # pylint:disable=no-name-in-module
from flask import current_app  # pylint:disable=wrong-import-order

import application.models.artifact
from application.schemas.artifact_schema import ArtifactSchema


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
        except exceptions.NotFoundError:
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
        except exceptions.NotFoundError:
            return

    def _update_artifact(self, artifact):
        params = self._artifact_dump_refactored(artifact)
        self._elastic().update(params)

    def _delete_artifact(self, artifact):
        self._elastic().delete(artifact.id_)

    def _create_elastic_artifact(self, artifact):
        params = self._artifact_dump_refactored(artifact)
        self._elastic().create(params)

    def _artifact_dump_refactored(self, artifact):
        return ArtifactSchema(model=application.models.artifact.Artifact,
                              decorate=False).dump(artifact).data

    def _elastic(self):
        return ElasticAccess('artifact', 'image')


class ElasticAccess:
    """ Access to basic crud on elasticsearch """

    def __init__(self, index, type):
        self.index = index
        self.type = type

    def create(self, data):
        """ create a document """
        current_app.es.index(
            index=self.index,
            doc_type=self.type,
            id=data.pop('id_'),
            body=data)

    def update(self, data):
        """ update a document """
        current_app.es.update(
            index=self.index,
            doc_type=self.type,
            id=data.pop('id_'),
            body={
                "doc": data
            })

    def delete(self, id):  # pylint:disable= invalid-name
        """ delete a document """
        current_app.es.delete(
            refresh='wait_for',
            index=self.index,
            doc_type=self.type,
            id=str(id))
