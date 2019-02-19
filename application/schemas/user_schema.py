""" Defines schema for database Team objects """
from marshmallow import fields

from ..base import BaseSchema, output_decorator


class UserSchema(BaseSchema):
    """ Schema for importing and exporting Team objects """
    id_ = fields.UUID(missing=None)
    username = fields.String()
    email = fields.String()

    @output_decorator
    def transform_fields(self, data):
        """ Transforms field for output """
        data["id"] = data.pop("id_")
        return data
