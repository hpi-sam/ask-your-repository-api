from .elastic.elastic_syncer import ElasticSyncer
from application.teams.placeholder_drives.sync.uploader import DriveUploader
from httplib2 import ServerNotFoundError
from flask import current_app


class ArtifactDeletor:
    def __init__(self, artifact):
        self.artifact = artifact
        self.drive = artifact.drive_folder.single()

    def delete(self):
        ElasticSyncer.for_artifact(self.artifact).delete()

        if self.drive:
            rel = self.drive.files.relationship(self.artifact)

            def send_delete_request():
                try:
                    DriveUploader(self.drive).delete_file_by_id(rel.gdrive_file_id)
                except ServerNotFoundError:
                    print("Connection to google drive failed")

            current_app.sync_scheduler.add_job(send_delete_request)
            self.drive.files.disconnect(self.artifact)
