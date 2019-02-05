""" Defines schema for database artifact objects """
from flask import current_app
from marshmallow import fields

from ..base import BaseSchema, output_decorator


class ArtifactSchema(BaseSchema):
    """ Schema for importing and exporting artifact objects """
    id = fields.UUID(missing=None)
    type = fields.String(missing="image")
    created_at = fields.DateTime(missing=None)
    updated_at = fields.DateTime(missing=None)
    file_url = fields.String(missing=None)
    team_id = fields.UUID(missing=None)
    tags = fields.List(fields.String(), missing=[], default=[])
    file_date = fields.DateTime(missing=None)
    score = fields.Integer()

    @output_decorator
    def transform_fields(self, data):
        """ Transforms field for output """
        data["url"] = self.build_url(data.pop("file_url"))
        return data

    @staticmethod
    def build_url(file_url):
        """ Schema: fileserver/id_filename """
        return current_app.config["FILE_SERVER"] + \
               "/" + file_url


class NeoArtifactSchema(BaseSchema):
    """ Schema for importing and exporting neo artifact objects """
    id_ = fields.String(missing=None)
    created_at = fields.DateTime(missing=None)
    updated_at = fields.DateTime(missing=None)
    file_url = fields.String(missing=None)
    team_id = fields.String(missing=None)
    tags_list = fields.List(fields.String(), missing=[], default=[])
    file_date = fields.DateTime(missing=None)

    @output_decorator
    def transform_fields(self, data):
        """ Transforms field for output """
        data["url"] = self.build_url(data.pop("file_url"))
        data["id"] = data.pop("id_")
        data["tags"] = data.pop("tags_list")
        return data

    @staticmethod
    def build_url(file_url):
        """ Schema: fileserver/id_filename """
        return current_app.config["FILE_SERVER"] + \
               "/" + file_url

