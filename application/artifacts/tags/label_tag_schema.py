"""Defines schema for database Team objects"""
from marshmallow import fields

from application.base_schema import BaseSchema


class LabelTagSchema(BaseSchema):
    """Schema for importing and exporting Tag objects"""

    name = fields.String()
    confidence = fields.Number()


TAG_SCHEMA = LabelTagSchema()
