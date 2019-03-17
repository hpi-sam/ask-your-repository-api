"""
Handles all logic of the user api
"""
from flask import abort
from flask_apispec import MethodResource, marshal_with, use_kwargs
from flask_jwt_extended import jwt_required
from neomodel import exceptions

from application.responders import no_content
from application.users import users_validator
from application.users.user import User
from application.users.user_schema import USER_SCHEMA, USERS_SCHEMA


class UserView(MethodResource):
    """Access Users by id"""

    @jwt_required
    @use_kwargs(users_validator.get_args())
    @marshal_with(USER_SCHEMA)
    def get(self, **params):
        """ get a single user """
        try:
            return User.find_by(id_=params['id'])
        except User.DoesNotExist:  # pylint:disable=no-member
            return abort(404, 'user not found')

    @jwt_required
    @use_kwargs(users_validator.update_args())
    @marshal_with(USER_SCHEMA)
    def patch(self, **params):
        """Logic for updating a user"""
        try:
            user = User.find_by(id_=params.pop("id"))
            if "password" in params:
                if not user.check_password(params.pop('old_password', None)):
                    return users_validator.raise_old_password_was_wrong()
            user.update(**params)
            return user
        except User.DoesNotExist:  # pylint:disable=no-member
            return abort(404, 'user not found')

    @jwt_required
    @use_kwargs(users_validator.update_args())
    @marshal_with(USER_SCHEMA)
    def put(self, **params):
        """Logic for updating a user"""
        return self.patch(**params)

    @jwt_required
    @use_kwargs(users_validator.delete_args())
    @marshal_with(None, 204)
    def delete(self, **params):
        """Logic for deleting a user"""
        id = params["id"]
        try:
            user = User.find_by(id_=id)
            user.delete()
            return no_content()
        except User.DoesNotExist:  # pylint:disable=no-member
            return abort(404, 'user not found')


class UsersView(MethodResource):
    """ Controller for users """

    @jwt_required
    @use_kwargs(users_validator.index_args())
    @marshal_with(USERS_SCHEMA)
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
