"""Defines schema for database Team objects"""
from marshmallow import fields, post_dump

from application.users.user_schema import USERS_SCHEMA
from application.base_schema import BaseSchema, output_decorator
from .drives.drive_schema import DRIVE_SCHEMA

class TeamSchema(BaseSchema):
    """Schema for importing and exporting Team objects"""

    id_ = fields.UUID(missing=None)
    name = fields.String()
    join_key = fields.String()
    members = fields.Nested(USERS_SCHEMA, many=True)
    drive = fields.Nested(DRIVE_SCHEMA)

    @output_decorator
    def transform_fields(self, data):
        """Transforms field for output"""
        data["id"] = data.pop("id_")
        return data

    @post_dump(pass_many=True)
    def dump_teams(self, data, many):
        """add a key for the returned collection"""
        if many:
            return {"teams": data, "teams_count": len(data)}
        return data


TEAM_SCHEMA = TeamSchema(decorate=True)
TEAMS_SCHEMA = TeamSchema(decorate=True, many=True)
