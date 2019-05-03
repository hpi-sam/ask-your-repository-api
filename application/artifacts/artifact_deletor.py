from .elastic.elastic_syncer import ElasticSyncer


class ArtifactDeletor:
    def __init__(self, artifact):
        self.artifact = artifact

    def delete(self):
        ElasticSyncer.for_artifact(self.artifact).delete()
