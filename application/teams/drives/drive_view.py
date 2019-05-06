from flask_apispec import MethodResource, use_kwargs, marshal_with
from flask_jwt_extended import jwt_required, get_jwt_identity
from neomodel.exceptions import AttemptedCardinalityViolation
from flask import abort
from .drive_schema import DriveSchema
from .drive_validator import create_args, delete_args
from ..team import Team
from .drive import Drive
from application.users.user import User
from application.responders import no_content


class DrivesView(MethodResource):
    @jwt_required
    @use_kwargs(create_args())
    @marshal_with(DriveSchema)
    def post(self, **params):
        current_user = User.find_by(id_=get_jwt_identity())
        if (not current_user.google) or (not current_user.google.has_offline_access):
            abort(403, "No google account connected")
        team_id = params.pop("team_id")
        drive = Drive(**params).save()
        try:
            team = Team.find_by(id_=team_id)
            team.drive_rel.connect(drive)
            team.save()
        except AttemptedCardinalityViolation:
            drive.delete()
            abort(409, "Team already has drive connected")
        drive.owner_rel.connect(User.find_by(id_=get_jwt_identity()))
        drive.save()
        return drive


class DriveView(MethodResource):
    @jwt_required
    @use_kwargs(delete_args())
    @marshal_with(None, 204)
    def delete(self, **params):
        drive = Drive.find_by(id_=params["drive_id"])
        if drive.owner == User.find_by(id_=get_jwt_identity()):
            try:
                Drive.find_by(id_=params["drive_id"]).delete()
                return no_content()
            except Drive.NotFound:
                abort(404, "Drive not Found")
        else:
            abort(403)
