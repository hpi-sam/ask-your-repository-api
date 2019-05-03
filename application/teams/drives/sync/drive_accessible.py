from abc import ABC

from application.teams.drives.sync.adapter import DriveAdapter
from application.users.oauth.google_oauth import credentials_from_dict


class DriveAccessible(ABC):
    def __init__(self, drive, http=None):
        self.drive = drive
        self.team = drive.team.single()
        self.owner = drive.owner.single()
        self.drive_adapter = self._build_drive_adapter(http)

    def _build_drive_adapter(self, http):
        credentials = credentials_from_dict(self.owner.google.credentials)
        return DriveAdapter(credentials, http)
