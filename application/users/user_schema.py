"""Defines schema for database Team objects"""
from marshmallow import fields, post_dump

from application.base import BaseSchema, output_decorator


class UserSchema(BaseSchema):
    """Schema for importing and exporting Team objects"""
    id_ = fields.UUID(missing=None)
    username = fields.String()
    email = fields.String()

    @output_decorator
    def transform_fields(self, data):
        """Transforms field for output"""
        data["id"] = data.pop("id_")
        return data

    @post_dump(pass_many=True)
    def dump_users(self, data, many):
        """add a key for the returned collection"""
        if many:
            return {'users': data, 'users_count': len(data)}
        return data


USER_SCHEMA = UserSchema(decorate=True)
USERS_SCHEMA = UserSchema(decorate=True, many=True)
