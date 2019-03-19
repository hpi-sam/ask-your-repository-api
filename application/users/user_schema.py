"""Defines schema for database Team objects"""
from marshmallow import fields, post_dump
from application.base_schema import BaseSchema, output_decorator


def providers_to_dict(user_data):
    providers = user_data.get('oauth_providers')
    if not providers:
        return
    user_data['oauth_providers'] = {}
    for provider in providers:
        name = provider.pop('name')
        user_data['oauth_providers'][name] = provider


class OAuthProviderSchema(BaseSchema):
    name = fields.String()
    user_id = fields.String()
    has_offline_access = fields.Bool()


class UserSchema(BaseSchema):
    """Schema for importing and exporting Team objects"""
    id_ = fields.UUID(missing=None)
    username = fields.String()
    email = fields.String()
    oauth_providers = fields.Nested(OAuthProviderSchema, many=True)

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
            for user in data:
                providers_to_dict(user)
            return {'users': data, 'users_count': len(data)}
        providers_to_dict(data)
        return data


USER_SCHEMA = UserSchema(decorate=True)
USERS_SCHEMA = UserSchema(decorate=True, many=True)
USERS_COLLECTION_SCHEMA = UserSchema(decorate=True, many=True, add_collection_key=True)
