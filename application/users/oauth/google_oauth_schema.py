from marshmallow import fields
from application.base_schema import BaseSchema


class GoogleOAuthSchema(BaseSchema):
    """Schema for importing and exporting GoogleOAuth objects"""
    user_id = fields.String()
    has_offline_access = fields.Bool()
