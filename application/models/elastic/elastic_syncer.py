from application.errors import NotFound
from application.schemas.artifact_schema import NeoArtifactSchema
import application.models.artifact
from ..elastic_artifact import ElasticArtifact


class ElasticSyncer:
    sync_disabled = True

    def __init__(self):
        self.artifacts = []

    @classmethod
    def for_artifact(cls, artifact):
        syncer = cls()
        syncer.artifacts = [artifact]
        return syncer

    @classmethod
    def for_artifacts(cls, artifacts):
        syncer = cls()
        syncer.artifacts = artifacts
        return syncer

    @classmethod
    def sync_everything(cls):
        syncer = cls()
        syncer.artifacts = application.models.artifact.Artifact.all()
        syncer.sync()

    def sync(self):
        if not ElasticSyncer.sync_disabled:
            for artifact in self.artifacts:
                try:
                    elastic_artifact = ElasticArtifact.find(artifact.id_)
                    elastic_artifact.update(self._artifact_dump(artifact))
                except NotFound:
                    self._create_elastic_artifact(artifact)

    def delete(self):
        if not ElasticSyncer.sync_disabled:
            for artifact in self.artifacts:
                try:
                    self._delete_artifact(artifact)
                except NotFound:
                    return

    def _delete_artifact(self, artifact):
        elastic_artifact = ElasticArtifact.find(artifact.id_)
        elastic_artifact.delete()

    def _create_elastic_artifact(self, artifact):
        params = self._artifact_dump(artifact)
        ElasticArtifact(params).save()

    def _artifact_dump(self, artifact):
        return NeoArtifactSchema(application.models.artifact.Artifact, decorate=True).dump(artifact).data
