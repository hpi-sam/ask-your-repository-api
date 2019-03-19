"""Defines schema for database Team objects"""
from marshmallow import fields, post_dump

from application.base_schema import BaseSchema, output_decorator


class UserSchema(BaseSchema):
    """Schema for importing and exporting Team objects"""
    id_ = fields.UUID(missing=None)
    username = fields.String()
    email = fields.String()

    def __init__(self, *args, add_collection_key=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_collection_key = add_collection_key

    @output_decorator
    def transform_fields(self, data):
        """Transforms field for output"""
        data["id"] = data.pop("id_")
        return data

    @post_dump(pass_many=True)
    def dump_users(self, data, many):
        """add a key for the returned collection"""
        if many and self.add_collection_key:
            return {'users': data, 'users_count': len(data)}
        return data


USER_SCHEMA = UserSchema(decorate=True)
USERS_SCHEMA = UserSchema(decorate=True, many=True)
USERS_COLLECTION_SCHEMA = UserSchema(decorate=True, many=True, add_collection_key=True)
