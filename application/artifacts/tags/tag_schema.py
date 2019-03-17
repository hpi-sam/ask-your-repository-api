"""Defines schema for database Team objects"""
from marshmallow import fields

from application.base import BaseSchema


class TagSchema(BaseSchema):
    """Schema for importing and exporting Tag objects"""
    name = fields.String()


TAG_SCHEMA = TagSchema()
