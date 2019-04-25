import io
import os

import magic
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from neomodel.match import NodeSet
from werkzeug.datastructures import FileStorage
from abc import ABC

from application.artifacts.artifact_creation import ArtifactCreator
from application.users.oauth.google_oauth import credentials_from_dict


class DriveAdapter:

    def __init__(self, credentials, http=None):
        self.service = self.drive_service(credentials, http)

    def drive_service(self, credentials, http=None):
        if http:
            return build("drive", "v3", http=http)
        else:
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

    def upload_file(self, filename, parent_folder):
        file_metadata = {'name': filename, 'parents': [parent_folder]}
        filepath = f"uploads/{filename}"
        mime = magic.Magic(mime=True)
        mime_type = mime.from_file(filepath)
        media = MediaFileUpload(f'uploads/{filename}',
                                mimetype=mime_type)
        file = self.service.files().create(body=file_metadata,
                                           media_body=media,
                                           fields='id').execute()
        return file['id']

    def delete_file(self, drive_file_id):
        try:
            print(self.service.files().delete(fileId=drive_file_id).execute())
        except Exception as e:
            print(e)
            """TODO: If 404 just ignore otherwise I don't know yet,
                      maybe print to logfile or something at least"""

    def compute_changes(self, initial_page_token, handle_change):
        page_token = initial_page_token
        while page_token is not None:
            response = (
                self.drive_access.service.changes().list(pageToken=page_token, fields="*", spaces="drive").execute()
            )
            changes = response.get("changes")
            page_token = response.get("nextPageToken")
            print(changes)
            for change in changes:
                handle_change(change)

            if "newStartPageToken" in response:
                return response.get("newStartPageToken")


class AbstractesDriveAccessDing(ABC):

    def __init__(self, drive, http=None):
        self.drive = drive
        self.team = drive.team.single()
        self.owner = drive.owner.single()
        self.drive_adapter = self._build_drive_adapter(http)

    def _build_drive_adapter(self,http):
        credentials = credentials_from_dict(self.owner.google.credentials)
        return DriveAdapter(self.credentials, http)


class DriveUploader(AbstractesDriveAccessDing):

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


class DriveDownloader(AbstractesDriveAccessDing):

    def __init__(self, *args, **kwargs):
        super(*args, **kwargs)
        self._initialize_start_page_token()

    def _initialize_start_page_token(self):
        if self.drive.page_token is None:
            self.drive.page_token = self.drive_adapter.start_page_token()["startPageToken"]
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
        except: # TODO: Can't import Artifact cyclic imports
            print("Artifact not Found, askyourcloud and google drive out of sync.")

    def _update_page_token(self):
        self.drive.page_token = self.drive_adapter.start_page_token()
        self.drive.save()

    def _sync_by_remote_changes(self):
        """
        Synchronize google drive changes to local artifacts.
        """
        self.drive.page_token = self.drive_adapter.compute_changes(self.drive.page_token,
                                                                   self._handle_change)
        self.drive.save()


    def sync_from_drive(self):
        """
        Synchronize all files from the drive.
        """
        if not self.drive.page_token:
            self.initialize_sync()
        self._sync_by_remote_changes()

    def _handle_change(self, change):
        """
        Handle a single google drive change
        :param change: a google drive api change response as dict
        """
        if self.drive.drive_id in change.get("file").get("parents"):
            if change.get("removed") or change.get("file").get("trashed"):
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
        creator = ArtifactCreator(file, owner_id=self.owner.id_, team_id=self.team.id_)
        artifact = creator.create_artifact()
        self.drive.files.connect(artifact, {"gdrive_file_id": image["id"]})


class Sync:

    def __init__(self,drive, http=None):
        """
        Create a Sync Object to allow initializing synchronization
        :param drive: The drive this sync object is for
        :param http: the http2 object to use. Can be used to mock the connection
        leave at None if you don't know what this is
        """
        self.uploader = DriveUploader(drive, http)
        self.downloader = DriveDownloader(drive, http)

    def initialize_sync(self):
        """
        Initialize google drive synchronization.
        Downloads all files from the drive and uploads all artifacts to the drive.
        """
        self.donwnloader.download_all()
        self.uploader.upload_all_missing()
