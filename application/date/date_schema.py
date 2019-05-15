"""Defines schema for database date objects"""
from marshmallow import fields

from application.base_schema import BaseSchema


class DateSchema(BaseSchema):
    """Schema for date objects aggregate from the neo4j time tree"""

    day = fields.Number()
    month = fields.Number()
    year = fields.Number()


DATE_SCHEMA = DateSchema()
