from marshmallow import fields

from application.base_schema import BaseSchema, output_decorator
from application.users.user_schema import USER_SCHEMA


class DriveSchema(BaseSchema):
    drive_id = fields.String()
    owner = fields.Nested(USER_SCHEMA)
    url = fields.String()
    name = fields.String()
    id_ = fields.UUID()

    @output_decorator
    def transform_fields(self, data):
        """Transforms field for output"""
        data["id"] = data.pop("id_")
        return data


DRIVE_SCHEMA = DriveSchema(decorate=True)
