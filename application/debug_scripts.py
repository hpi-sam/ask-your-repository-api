from flask.cli import AppGroup
from application.teams.placeholder_drives.drive import Drive

# from application.teams.placeholder_drives.sync.uploader import DriveUploader
from application.teams.placeholder_drives.sync.downloader import DriveDownloader

# from application.teams.placeholder_drives.sync.sync import Sync


debug_cli = AppGroup("debug")


@debug_cli.command("debug1")
def something():
    drive = Drive.all()[0]
    drive.page_token = None
    DriveDownloader(drive)._initialize_start_page_token()


def add_debug_scripts(app):
    app.cli.add_command(debug_cli)
