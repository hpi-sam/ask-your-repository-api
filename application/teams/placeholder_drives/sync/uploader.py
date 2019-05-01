from neomodel import NodeSet

from application.teams.placeholder_drives.sync.abstraktes_drive_dingens import AbstractesDriveAccessDing


class DriveUploader(AbstractesDriveAccessDing):
    def upload_all_missing(self):
        """
        Uploads all missing artifacts to google drive.
        :return: None
        """
        self.drive.update(is_syncing=True)
        artifacts = NodeSet(self.drive.team.single().artifacts._new_traversal()).has(drive_folder=False)
        # The manual conversion to NodeSet is needed as .artifacts returns a RelationshipManager.
        # This Manager is not to 100% compatible to the NodeSet interface so to
        # support "has()" we need to convert manually. #PullRequestPlz
        for artifact in artifacts:
            if artifact in self.drive.files:
                return
            id = self.drive_adapter.upload_file(artifact.file_url, self.drive.drive_id)
            self.drive.files.connect(artifact, {"gdrive_file_id": id})
        self.drive.update(is_syncing=False)

    def _delete_all_files(self):
        """
        Deletes all files in google drive.
        """
        artifacts = self.drive.files
        for artifact in artifacts:
            self.delete_file_by(artifact)

    def delete_file_by(self, artifact):
        """
        Delete a file in google drive by artifact object
        :param artifact: the artifact object to delete in google drive
        """
        rel = self.drive.files.relationship(artifact)
        self.drive_adapter.delete_file(rel.gdrive_file_id)
        self.drive.files.disconnect(artifact)

    def delete_file_by_id(self, gdrive_file_id):
        self.drive_adapter.delete_file(gdrive_file_id)

    def created(self, artifact, **params):
        if "drive_file_id" in params:
            self.drive.files.connect(artifact, {"gdrive_file_id": params["drive_file_id"]})
