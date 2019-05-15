"""Defines schema for database Location objects"""
from marshmallow import fields

from application.base_schema import BaseSchema


class LocationSchema(BaseSchema):
    """Schema for Location objects"""

    name = fields.String()


LOCATION_SCHEMA = LocationSchema()
