""" Defines schemas for all database objects """
from flask import current_app
from marshmallow import fields
from application.base import BaseSchema, output_decorator


class ArtifactSchema(BaseSchema):
    """ Schema for importing and exporting Artifact objects """
    id = fields.UUID(missing=None)
    type = fields.String(missing="image")
    created_at = fields.DateTime(missing=None)
    updated_at = fields.DateTime(missing=None)
    file_url = fields.String(missing=None)
    tags = fields.List(fields.String(), missing=[], default=[])
    file_date = fields.DateTime(missing=None)
    score = fields.Integer()

    @output_decorator
    def transform_fields(self, data):
        """ Transforms field for output """
        data["url"] = self.build_url(data.pop("file_url"))
        return data

    def build_url(self, file_url):
        """ Schema: fileserver/id_filename """
        return current_app.config["FILE_SERVER"] + \
                "/" + file_url


class TeamSchema(BaseSchema):
    """ Schema for importing and exporting Artifact objects """
    id_ = fields.UUID(missing=None)
    name = fields.String()

    @output_decorator
    def transform_fields(self, data):
        """ Transforms field for output """
        data['id'] = data.pop('id_')
        print(data)
        return data
