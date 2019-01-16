""" Defines schema for database Team objects """
from marshmallow import fields
from ..base import BaseSchema, output_decorator


class TeamSchema(BaseSchema):
    """ Schema for importing and exporting Team objects """
    id_ = fields.UUID(missing=None)
    name = fields.String()

    @output_decorator
    def transform_fields(self, data):
        """ Transforms field for output """
        data['id'] = data.pop('id_')
        return data
