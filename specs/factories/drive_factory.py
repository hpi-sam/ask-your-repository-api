from application.teams.drives.drive import Drive
from .google_oauth_factory import GoogleOAuthFactory, google_credentials
from .team_factory import TeamFactory


class DriveFactory:
    @classmethod
    def create_drive(cls, user=None, team=None):
        drive = Drive(drive_id="1HTeLgrLX3L3QvvTd7Q6f9Sbaalvq4HU0").save()
        if user:
            drive.owner_rel.connect(user)
        else:
            user = GoogleOAuthFactory.create_user_with_google(credentials=google_credentials)
            drive.owner_rel.connect(user)
        if team:
            drive.team_rel.connect(team)
        else:
            team = TeamFactory.create_team(members=[user])
            drive.team_rel.connect(team)
        drive.save()
        return drive
