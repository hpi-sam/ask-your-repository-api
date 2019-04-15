import io
import os

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from application.users.oauth.google_oauth import credentials_from_dict
import uuid


class DriveAccess:
    drive_folder = 'g_drive_downloads'
    def __init__(self, credentials):
        os.makedirs(self.drive_folder, exist_ok=True)
        self.service = self.drive_service(credentials)

    def drive_service(self, credentials):
        return build('drive', 'v3', credentials=credentials)

    def list_images(self, drive_id):
        result = self.service.files().list(q=f"mimeType contains 'image' and parents='{drive_id}'").execute()
        print(result.get('files'))
        return result.get('files')

    def download_file(self, file_id, filename):
        request = self.service.files().get_media(fileId=file_id)
        fh = io.FileIO(f"{self.drive_folder}/{filename}", 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            "Download %d%%." % int(status.progress() * 100)

class ImageDownloader:
    def __init__(self, drive):
        self.owner = drive.owner.single()
        self.credentials = credentials_from_dict(self.owner.google_rel.single().credentials)
        self.drive_access = DriveAccess(self.credentials)
        self.drive = drive

    def download_all(self):
        images = self.drive_access.list_images(self.drive.drive_id)
        for image in images:
            self.drive_access.download_file(image['id'], f"{uuid.uuid4()}_{image['name']}")