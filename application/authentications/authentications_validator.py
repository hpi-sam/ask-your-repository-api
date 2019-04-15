"""Defines validators for authentication requests"""

from marshmallow import fields, validates_schema, ValidationError, Schema


class LoginSchema(Schema):
    """Defines and validates params for create or login"""

    id_token = fields.String()
    email_or_username = fields.String()
    password = fields.String()
    set_cookies = fields.Bool(missing=True)

    @validates_schema
    def validates_login(self, data):
        """Validates that either email_or_username with password are in params or the google id_token"""
        if "email_or_username" in data:
            if "password" not in data:
                raise ValidationError("missing value for required field", ["password"])
        elif "id_token" not in data:
            raise ValidationError("id_token or email_or_username missing", ["login_params"])

    class Meta:  # pylint:disable=too-few-public-methods
        """Sets LoginSchema to strict mode"""

        strict = True
