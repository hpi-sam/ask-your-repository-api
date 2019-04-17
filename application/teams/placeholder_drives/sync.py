import io
import os
import uuid

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from application.users.oauth.google_oauth import credentials_from_dict
from application.artifacts.artifact_creation import FileSaver


class DriveAccess:
    drive_folder = "g_drive_downloads"

    def __init__(self, credentials):
        os.makedirs(self.drive_folder, exist_ok=True)
        self.service = self.drive_service(credentials)

    def drive_service(self, credentials):
        return build("drive", "v3", credentials=credentials)

    def list_images(self, drive_id):
        result = self.service.files().list(q=f"mimeType contains 'image' and parents='{drive_id}'").execute()
        print(result.get("files"))
        return result.get("files")

    def download_file(self, file_id, filepath):
        request = self.service.files().get_media(fileId=file_id)
        fh = io.FileIO(filepath, "wb")
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            "Download %d%%." % int(status.progress() * 100)

    def start_page_token(self):
        return self.service.changes().getStartPageToken().execute()

    def get(self, file_id):
        return self.service.files().get(file_id).execute()


# Download File:
# Download File
# Create Artifact
# Create DriveFile (save ID)
# Connect to Drive

# Upload File:
# Upload File
# Create DriveFile (save ID)
# Connect to Drive

# Delete File:
# Find deleted DriveFile.drive_id
# Delete Artifact and downloaded File
# Delete DriveFile


class ImageSynchronizer:
    def __init__(self, drive):
        self.owner = drive.owner.single()
        self.credentials = credentials_from_dict(self.owner.google_rel.single().credentials)
        self.drive_access = DriveAccess(self.credentials)
        self.drive = drive
        if drive.page_token is None:
            drive.page_token = self.drive_access.start_page_token()["startPageToken"]
            drive.save()

    def download_all(self):
        images = self.drive_access.list_images(self.drive.drive_id)
        for image in images:
            self.download_image(image)

    def download_image(self, image):
        download_file = DriveDownloadFile(self.drive_access, image)
        file_saver = FileSaver(download_file)
        file_saver.save()
        # TODO: Implement actually creating artifacts from downloaded files
        # def create_artifact_from_file? (user= user, team= team, file= file)

    def upload_all(self):
        # TODO: For all artifacts without DriveFile:
        # TODO: Upload to GDRIVE
        pass

    # TODO: Local changes vs remote changes (other changes than add/delete?)

    def retrieve_changes(self):
        page_token = self.drive.page_token
        response = self.drive_access.service.changes().list(pageToken=page_token, fields="*", spaces="drive").execute()
        print(response)
        for change in response.get("changes"):
            print(f'Change found for file: {change.get("fileId")} with name: '
                  f'{change.get("file").get("name")}, parent is '
                  f'{change.get("file").get("parents")}')
        if "newStartPageToken" in response:
            saved_start_page_token = response.get("newStartPageToken")
        page_token = response.get("nextPageToken")
        self.drive.page_token = page_token

    def initialize_sync(self):
        self.download_all()
        self.upload_all()

class DriveDownloadFile():

    def __init__(self, drive_access, image):
        self.drive_access = drive_access
        self._image = image
        self.file_id = image['id']
        self.filename = image['name']

    def save(self, filename):
        self.drive_access.download_file(self.file_id, filename)

    def close(self):
        pass