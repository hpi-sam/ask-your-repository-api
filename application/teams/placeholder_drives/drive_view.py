from flask_apispec import MethodResource, use_kwargs, marshal_with
from flask_jwt_extended import jwt_required, get_jwt_identity
from neomodel.exceptions import AttemptedCardinalityViolation
from flask import abort
from .drive_schema import DriveSchema

from .drive_validator import create_args
from ..team import Team
from .drive import Drive
from application.users.user import User


class DrivesView(MethodResource):

    @jwt_required
    @use_kwargs(create_args())
    @marshal_with(DriveSchema)
    def post(self, **params):
        print(params)
        drive = Drive(drive_id = params.get("drive_id")).save()
        try:
            team = Team.find_by(id_=params.get("team_id"))
            team.drive.connect(drive)
            team.save()
        except AttemptedCardinalityViolation:
            abort(409, 'Team already has drive connected')
        drive.owner.connect(User.find_by(id_=get_jwt_identity()))
        drive.save()
        return drive


class DriveView(MethodResource):
    def delete(self):
        pass
