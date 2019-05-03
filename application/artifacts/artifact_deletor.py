from .elastic.elastic_syncer import ElasticSyncer
from application.teams.placeholder_drives.sync.uploader import DriveUploader
from httplib2 import ServerNotFoundError
from flask import current_app


class ArtifactDeletor:
    def __init__(self, artifact):
        self.artifact = artifact

    def delete(self):
        ElasticSyncer.for_artifact(self.artifact).delete()