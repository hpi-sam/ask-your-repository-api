from mamba import description, before, it

from application.teams.placeholder_drives.drive import Drive
from application.teams.placeholder_drives.sync import DriveAccess, ImageSynchronizer
from application.users.oauth.google_oauth import credentials_from_dict
from specs.spec_helpers import Context

with description("drive") as self:
    with before.each:
        self.context = Context()

    with description("downloading"):
        with it("downloads something"):
            ImageSynchronizer(Drive.all()[3]).download_all()
