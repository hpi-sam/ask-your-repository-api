"""
Handles all logic of the user api
"""
from functools import wraps
from flask import abort
from flask_apispec import MethodResource, marshal_with, use_kwargs
from flask_jwt_extended import jwt_required
from neomodel import exceptions

from application.responders import no_content
from application.users import users_validator
from application.users.user import User
from application.users.user_schema import USER_SCHEMA, USERS_COLLECTION_SCHEMA


def check_user(func):
    """capture User.DoesNotExist exception"""

    @wraps(func)
    def wrapped_function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except User.DoesNotExist:  # pylint:disable=no-member
            return abort(404, "user not found")

    return wrapped_function


class UserView(MethodResource):
    """Access Users by id"""

    @jwt_required
    @use_kwargs(users_validator.get_args())
    @marshal_with(USER_SCHEMA)
    @check_user
    def get(self, **params):
        """get a single user"""
        return User.find(params["id"])

    @jwt_required
    @use_kwargs(users_validator.update_args())
    @marshal_with(USER_SCHEMA)
    @check_user
    def patch(self, **params):
        """Logic for updating a user"""
        user = User.find_by(id_=params.pop("id"))
        if "password" in params:
            if not user.check_password(params.pop("old_password", None)):
                return users_validator.raise_old_password_was_wrong()
        user.update(**params)
        return user

    @jwt_required
    @use_kwargs(users_validator.update_args())
    @marshal_with(USER_SCHEMA)
    def put(self, **params):
        """Logic for updating a user"""
        return self.patch(**params)

    @jwt_required
    @use_kwargs(users_validator.delete_args())
    @marshal_with(None, 204)
    @check_user
    def delete(self, **params):
        """Logic for deleting a user"""
        user = User.find(params["id"])
        user.delete()
        return no_content()


class UsersView(MethodResource):
    """Controller for users"""

    @jwt_required
    @use_kwargs(users_validator.index_args())
    @marshal_with(USERS_COLLECTION_SCHEMA)
    def get(self, **params):  # pylint: disable=W0613
        """Logic for querying several users"""
        return User.all()

    @use_kwargs(users_validator.create_args())
    @marshal_with(USER_SCHEMA)
    def post(self, **params):
        """Logic for creating a user"""
        try:
            user = User(**params).save()
        except exceptions.UniqueProperty:
            return abort(409, "Username or Email already taken")
        return user
