import datetime
from application.password_resets.password_reset_jwt_manager import encode_reset_token


def reset_password_token(user):
    """Creates a password reset token"""
    return encode_reset_token(user)


def expired_reset_password_token(user):
    """Creates an expired password reset token"""
    expires = datetime.timedelta(days=-1)
    return encode_reset_token(user, expires_delta=expires)
