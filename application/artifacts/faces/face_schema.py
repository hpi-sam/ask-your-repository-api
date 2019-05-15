"""Defines schema for database Face objects"""
from marshmallow import fields

from application.base_schema import BaseSchema, output_decorator
from application.artifacts.faces.person_schema import PersonSchema


class FaceSchema(BaseSchema):
    """Schema for Face objects"""

    id_ = fields.String()
    bounding_box = fields.Field()
    person = fields.Nested(PersonSchema, many=True, only="name", missing=None)

    @output_decorator
    def transform_fields(self, data):
        """Transforms field for output"""
        data["id"] = data.pop("id_")
        return data


FACE_SCHEMA = FaceSchema(decorate=True)
