""" Defines schema for database Team objects """
from marshmallow import fields

from ..base import BaseSchema, output_decorator
from .user_schema import UserSchema

class TeamSchema(BaseSchema):
    """ Schema for importing and exporting Team objects """
    id_ = fields.UUID(missing=None)
    name = fields.String()
    members = fields.Nested(UserSchema, many=True)

    @output_decorator
    def transform_fields(self, data):
        """ Transforms field for output """
        data["id"] = data.pop("id_")
        return data
