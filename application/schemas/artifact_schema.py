""" Defines schema for database artifact objects """
from flask import current_app
from marshmallow import fields

from .tag_schema import TagSchema
from ..base import BaseSchema, output_decorator
from .user_schema import UserSchema


class ArtifactSchema(BaseSchema):
    """ Schema for importing and exporting neo artifact objects """
    id_ = fields.String(missing=None)
    created_at = fields.DateTime(missing=None)
    updated_at = fields.DateTime(missing=None)
    file_url = fields.String(missing=None)
    team_id = fields.String(missing=None)
    author = fields.Nested(UserSchema, only=["username"], missing=None)
    tags = fields.Nested(TagSchema, many=True, only='name')
    label_tags = fields.Nested(TagSchema, many=True, only='name')
    user_tags = fields.Nested(TagSchema, many=True, only='name')
    text_tags = fields.Nested(TagSchema, many=True, only='name')
    file_date = fields.DateTime(missing=None)
    score = fields.Number()

    @output_decorator
    def transform_fields(self, data):
        """ Transforms field for output """
        data["url"] = self.build_url(data.pop("file_url"))
        data["id"] = data.pop("id_")
        return data

    @staticmethod
    def build_url(file_url):
        """ Schema: fileserver/id_filename """
        return current_app.config["FILE_SERVER"] + \
               "/" + file_url
