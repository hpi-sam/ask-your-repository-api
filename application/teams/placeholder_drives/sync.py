import io
import os

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from werkzeug.datastructures import FileStorage

from application.artifacts.artifact_creation import ArtifactCreator
from application.users.oauth.google_oauth import credentials_from_dict


class DriveAccess:
    drive_folder = "g_drive_downloads"

    def __init__(self, credentials):
        os.makedirs(self.drive_folder, exist_ok=True)
        self.service = self.drive_service(credentials)

    def drive_service(self, credentials):
        return build("drive", "v3", credentials=credentials)

    def list_images(self, drive_id):
        result = self.service.files().list(q=f"mimeType contains 'image' and parents='{drive_id}'").execute()
        return result.get("files")

    def download_file(self, file_id, filename):
        print(file_id)
        request = self.service.files().get_media(fileId=file_id)
        file = FileStorage(io.BytesIO(), filename=filename)
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        file.seek(0)
        return file

    def start_page_token(self):
        return self.service.changes().getStartPageToken().execute().get("startPageToken")

    def get(self, file_id):
        print(self.service.files().get(file_id).execute())


# Upload File:
# Upload File
# Create DriveFile (save ID)
# Connect to Drive

# Delete remote File


class ImageSynchronizer:
    def __init__(self, drive):
        self.owner = drive.owner.single()
        self.credentials = credentials_from_dict(self.owner.google_rel.single().credentials)
        self.drive_access = DriveAccess(self.credentials)
        self.drive = drive
        self.team = drive.team.single()
        if drive.page_token is None:
            drive.page_token = self.drive_access.start_page_token()["startPageToken"]
            drive.save()

    def download_all(self):
        images = self.drive_access.list_images(self.drive.drive_id)
        for image in images:
            self.download_image(image)

    def sync_from_drive(self):
        self.compute_changes(self.handle_change)

    def handle_change(self, change):
        print(
            f'Change found for file: {change.get("fileId")} with name: '
            f'{change.get("file").get("name")}, parent is '
            f'{change.get("file").get("parents")}'
        )
        if change.get("removed") or change.get("file").get("trashed"):
            self.delete_artifact_by(change.get("fileId"))
        else:
            if not self.drive.find_artifact_by(change.get("fileId"), force=False):
                if "image" in change.get("file").get("mimeType"):
                    self.download_image(change.get("file"))

    def list_images(self):
        images = self.drive_access.list_images(self.drive.drive_id)
        return images

    def download_image(self, image):
        print("asdf")
        file = self.drive_access.download_file(image["id"], image["name"])
        creator = ArtifactCreator(file, owner_id=self.owner.id_, team_id=self.team.id_)
        artifact = creator.create_artifact()
        self.drive.files.connect(artifact, {"gdrive_file_id": image["id"]})

    def delete_artifact_by(self, gdrive_id):
        try:
            self.drive.find_artifact_by(gdrive_id).delete()
        except:
            print("Artifact not Found, askyourcloud and google drive out of sync.")

    def _update_page_token(self):
        self.drive.page_token = self.drive_access.start_page_token()
        self.drive.save()

    def upload_all(self):
        # TODO: For all artifacts without DriveFile:
        # TODO: Upload to GDRIVE
        pass

    # TODO: Local changes vs remote changes (other changes than add/delete?)

    def compute_changes(self, handle_change):
        page_token = self.drive.page_token
        while page_token is not None:
            response = (
                self.drive_access.service.changes().list(pageToken=page_token, fields="*", spaces="drive").execute()
            )
            changes = response.get("changes")
            page_token = response.get("nextPageToken")
            print(changes)
            for change in changes:
                if self.drive.drive_id in change.get("file").get("parents"):
                    handle_change(change)

            if "newStartPageToken" in response:
                self.drive.page_token = response.get("newStartPageToken")
                self.drive.save()

    def initialize_sync(self):
        self.download_all()
        self.upload_all()
