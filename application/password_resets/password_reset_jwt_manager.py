"""Defines a custom jwt encoder and decoder for password reset links"""

import datetime
from flask import current_app
from flask_jwt_extended.config import config
from flask_jwt_extended.exceptions import JWTDecodeError
import jwt
from application.models import User


def encode_reset_token(user, expires_delta=None):
    """Encodes a jwt reset token"""
    _check_flask_jwt_extended()
    verification = password_verification(user.password)
    if not expires_delta:
        expires_delta = datetime.timedelta(days=1)
    now = datetime.datetime.utcnow()
    identity_claim_key = config.identity_claim_key

    token_data = {
        "iat": now,
        "nbf": now,
        "jti": verification,
        "type": "password_reset",
        "exp": now + expires_delta,
        identity_claim_key: user.id_,
    }
    return jwt.encode(token_data, config.encode_key, config.algorithm, json_encoder=config.json_encoder).decode("utf-8")


def _decode_reset_token(reset_token):
    """Decodes a jwt reset token"""
    _check_flask_jwt_extended()
    try:
        data = jwt.decode(
            reset_token,
            config.decode_key,
            algorithms=[config.algorithm],
            audience=config.audience,
            leeway=config.leeway,
        )

        if config.identity_claim_key not in data:
            raise JWTDecodeError("Missing claim: {}".format(config.identity_claim_key))
        if data.get("type") != "password_reset":
            raise JWTDecodeError("Token is not a reset token")
        return data
    except jwt.exceptions.DecodeError:
        raise JWTDecodeError("Not a valid jwt token")


def get_user_from_reset_token(reset_token):
    """Returns a user from a reset_token"""
    _check_flask_jwt_extended()
    decoded_token = _decode_reset_token(reset_token)
    user = User.find(decoded_token[config.identity_claim_key])
    if not decoded_token["jti"] == password_verification(user.password):
        raise JWTDecodeError("Reset link can only be used once")
    return user


def _check_flask_jwt_extended():
    """Checks if flask-jwt-extended extensions was initialized.
    Necessary for config variables."""
    if not current_app.extensions.get("flask-jwt-extended"):
        raise RuntimeError("You must initialize a JWTManager with this flask " "application before using this method")


def password_verification(password):
    """Returns users password hash or empty string.
    It is used to check if a password reset link has already used, because the users password hash
    would have been changed."""
    return password if password else ""
