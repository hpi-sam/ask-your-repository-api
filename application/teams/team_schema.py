"""Defines schema for database Team objects"""
from marshmallow import fields, post_dump

from application.users.user_schema import USERS_SCHEMA
from application.base_schema import BaseSchema, output_decorator


class TeamSchema(BaseSchema):
    """Schema for importing and exporting Team objects"""
    id_ = fields.UUID(missing=None)
    name = fields.String()
    members = fields.Nested(USERS_SCHEMA, many=True)

    @output_decorator
    def transform_fields(self, data):
        """Transforms field for output"""
        data["id"] = data.pop("id_")
        return data

    @post_dump(pass_many=True)
    def dump_teams(self, data, many):
        """add a key for the returned collection"""
        if many:
            for team in data:
                team["members"] = team["members"]["users"]
            return {'teams': data, 'teams_count': len(data)}
        data["members"] = data["members"]["users"]
        return data


TEAM_SCHEMA = TeamSchema(decorate=True)
TEAMS_SCHEMA = TeamSchema(decorate=True, many=True)
