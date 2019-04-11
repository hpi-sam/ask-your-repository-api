from flask_apispec import MethodResource, use_kwargs, marshal_with
from .drive_schema import DriveSchema

from .drive_validator import create_args
from ..team import Team


class DrivesView(MethodResource):
    @use_kwargs(create_args())
    @marshal_with(DriveSchema)
    def post(self, **params):
        print(params)
        drive = {"drive_id": params.get("folder_id"),
                 "team": Team.find_by(id_=params.get("team_id"))}
        return drive


class DriveView(MethodResource):
    def delete(self):
        pass
