"""Defines schema for database Person objects"""
from marshmallow import fields

from application.base_schema import BaseSchema


class PersonSchema(BaseSchema):
    """Schema for Person objects"""

    name = fields.String()


PERSON_SCHEMA = PersonSchema()
