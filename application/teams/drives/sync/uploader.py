from neomodel import NodeSet

from application.teams.drives.sync.abstraktes_drive_dingens import DriveAccessible


class DriveUploader(DriveAccessible):
    def sync_to_drive(self):
        self.upload_all_missing()
        self.delete_all_deleted()

    def upload_all_missing(self):
        """
        Uploads all missing artifacts to google drive.
        :return: None
        """
        artifacts = NodeSet(self.drive.team.single().artifacts._new_traversal()).has(drive_folder=False)
        # The manual conversion to NodeSet is needed as .artifacts returns a RelationshipManager.
        # This Manager is not to 100% compatible to the NodeSet interface so to
        # support "has()" we need to convert manually. #PullRequestPlz
        for artifact in artifacts:
            if artifact in self.drive.files:
                return
            id = self.drive_adapter.upload_file(artifact.file_url, self.drive.drive_id)
            self.drive.files.connect(artifact, {"gdrive_file_id": id})
            self.drive_adapter.add_properties_to_file(id, elija_id=artifact.id_)

    def delete_all_deleted(self):
        print("Trying to delete images")
        for image in self.drive_adapter.list_images(self.drive.drive_id):
            if self.image_should_be_deleted(image):
                print(f"Found image to be deleted: {image}")
                self.drive_adapter.delete_file(image["id"])

    def image_should_be_deleted(self, file):
        if self.file_is_in_folder(file) and not self.file_is_downloaded(file) and self.file_has_elija_id(file):
            return True
        else:
            return False

    def file_has_elija_id(self, file):
        props = file.get("appProperties")
        if props is not None:
            if props.get("elija_id"):
                return True
        return False

    def file_is_in_folder(self, file):
        return self.drive.drive_id in file.get("parents")

    def file_is_downloaded(self, file):
        if self.drive.find_artifact_by(file.get("id"), force=False):
            return True
        else:
            return False

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
