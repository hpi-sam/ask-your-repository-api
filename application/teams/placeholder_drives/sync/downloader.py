from application.artifacts.artifact_creation import ArtifactCreator
from application.teams.placeholder_drives.sync.abstraktes_drive_dingens import AbstractesDriveAccessDing
from application.artifacts.artifact import Artifact


class DriveDownloader(AbstractesDriveAccessDing):
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
            self._download_image(image)

    def delete_artifact_by(self, gdrive_id):
        """
        Delete an artifact based on its google drive file id
        :param gdrive_id: The google drive file id to delete
        """
        try:
            self.drive.find_artifact_by(gdrive_id).delete()
        except Exception as e:
            print(e)
            print(type(e))
            print("Artifact not Found, askyourcloud and google drive out of sync.")

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
        if change.get("removed"):
            self.delete_artifact_by(change.get("fileId"))
        if change.get("file") is not None:
            if self.drive.drive_id in change.get("file").get("parents", []):
                if change.get("file").get("trashed"):
                    self.delete_artifact_by(change.get("fileId"))
                else:
                    if not self.drive.find_artifact_by(change.get("fileId"), force=False):
                        if "image" in change.get("file").get("mimeType"):
                            self._download_image(change.get("file"))

    def _download_image(self, image):
        """
        Downloads a single image
        :param image: a dict containing a google drive api image object
        """
        file = self.drive_adapter.download_file(image["id"], image["name"])
        creator = ArtifactCreator(file, owner_id=self.owner.id_, team_id=self.team.id_, drive_file_id=image["id"])
        artifact = creator.create_artifact()
