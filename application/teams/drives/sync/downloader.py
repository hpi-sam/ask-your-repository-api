from application.artifacts.artifact_creation import ArtifactCreator
from .drive_accessible import DriveAccessible


class DriveDownloader(DriveAccessible):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._initialize_start_page_token()

    def _initialize_start_page_token(self):
        if self.drive.page_token is None:
            self.drive.page_token = self.drive_adapter.start_page_token()
            self.drive.save()

    def images_in_drive(self):
        """
        List all images in the corresponding google drive
        :return: A list of all file objects that are images in the google drive folder
        """
        images = self.drive_adapter.list_images(self.drive.drive_id)
        return images

    def download_all(self):
        """
        Download all images from google drive and save them as artifacts.
        """
        for image in self.images_in_drive():
            if not image["trashed"]:
                self._download_image(image)

    def delete_artifact_by(self, gdrive_id):
        """
        Delete an artifact based on its google drive file id
        :param gdrive_id: The google drive file id to delete
        """
        try:
            self.drive.find_artifact_by(gdrive_id).delete()
        except Exception:
            pass
            # This can happen as google drive handles trashing and removing separately.
            # So the delete action might be executed twice.

    def _update_page_token(self):
        self.drive.page_token = self.drive_adapter.start_page_token()
        self.drive.save()

    def sync_by_remote_changes(self):
        """
        Synchronize google drive changes to local artifacts.
        """
        self.drive.page_token = self.drive_adapter.compute_changes(self.drive.page_token, self._handle_change)
        self.drive.save()

    def is_sync_initialized(self):
        return bool(self.drive.page_token)

    def _handle_change(self, change):
        """
        Handle a single google drive change
        :param change: a google drive api change response as dict
        """
        if self.change_should_be_trashed(change):
            self.delete_artifact_by(change.get("fileId"))
        elif self.change_should_be_downloaded(change):
            self._download_image(change.get("file"))
        else:
            pass

    def change_should_be_downloaded(self, change):
        if self.change_contains_file(change) and self.file_should_be_downloaded(change.get("file")):
            return True
        else:
            return False

    def file_should_be_downloaded(self, file):
        if self.file_is_image(file) and self.file_is_in_folder(file) and not self.file_is_downloaded(file):
            return True
        else:
            return False

    def change_should_be_trashed(self, change):
        if change.get("removed"):
            return True
        elif (
            self.change_contains_file(change)
            and self.file_is_in_folder(change.get("file"))
            and self.file_is_trashed(change.get("file"))
        ):
            return True
        else:
            return False

    def file_is_in_folder(self, file):
        return self.drive.drive_id in file.get("parents", [])

    def file_is_image(self, file):
        return "image" in file.get("mimeType")

    def file_is_downloaded(self, file):
        if self.drive.find_artifact_by(file.get("id"), force=False):
            return True
        else:
            return False

    def file_is_trashed(self, file):
        return file.get("trashed")

    def change_contains_file(self, change):
        return change.get("file") is not None

    def _download_image(self, image):
        """
        Downloads a single image
        :param image: a dict containing a google drive api image object
        """
        file = self.drive_adapter.download_file(image["id"], image["name"])
        creator = ArtifactCreator(file, owner_id=self.owner.id_, team_id=self.team.id_)
        artifact = creator.create_artifact()
        self.drive.files.connect(artifact, {"gdrive_file_id": image["id"]})
        self.drive_adapter.add_properties_to_file(image["id"], elija_id=artifact.id_)
