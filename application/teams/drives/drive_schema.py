from marshmallow import fields

from application.base_schema import BaseSchema
from ..team_schema import TEAM_SCHEMA
from application.users.user_schema import USER_SCHEMA


class DriveSchema(BaseSchema):
    drive_id = fields.String()
    team = fields.Nested(TEAM_SCHEMA)
    owner = fields.Nested(USER_SCHEMA)

DRIVE_SCHEMA = DriveSchema(decorate=True)