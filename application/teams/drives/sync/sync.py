import json

from application.teams.drives.sync.downloader import DriveDownloader
from application.teams.drives.sync.uploader import DriveUploader


def print_to_file(file_name, response):
    with open(f"{file_name}", "w") as fe:
        fe.write(json.dumps(response))


class Sync:
    def __init__(self, drive, http=None):
        """
        Create a Sync Object to allow initializing synchronization
        :param drive: The drive this sync object is for
        :param http: the http2 object to use. Can be used to mock the connection
        leave at None if you don't know what this is
        """
        self.drive = drive
        self.uploader = DriveUploader(drive, http)
        self.downloader = DriveDownloader(drive, http)

    def initialize_sync(self):
        """
        Initialize google drive synchronization.
        Downloads all files from the drive and uploads all artifacts to the drive.
        """
        self.donwnloader.download_all()
        self.uploader.upload_all_missing()

    def sync_drive(self):
        """
        Synchronize all files from the drive.
        """
        self.drive.update(is_syncing=True)
        if not self.downloader.is_sync_initialized():
            self.initialize_sync()
        self.downloader.sync_by_remote_changes()
        self.uploader.sync_to_drive()
        self.drive.update(is_syncing=False)
