""" Defines schema for database Team objects """
from marshmallow import fields

from ..base import BaseSchema


class TeamSchema(BaseSchema):
    """ Schema for importing and exporting Team objects """
    id = fields.UUID(missing=None)
    name = fields.String()
