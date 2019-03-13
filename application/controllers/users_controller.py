"""
Handles all logic of the user api
"""
from flask import abort
from flask_apispec import MethodResource, marshal_with, use_kwargs
from flask_jwt_extended import jwt_required
from neomodel import exceptions

from ..models.user import User
from ..responders import no_content
from ..schemas.user_schema import UserSchema
from ..validators import users_validator


class UsersByIDController(MethodResource):
    """Access Users by id"""

    @jwt_required
    @use_kwargs(users_validator.get_args())
    @marshal_with(UserSchema(decorate=True))
    def get(self, **params):
        """ get a single user """
        try:
            return User.find_by(id_=params['id'])
        except User.DoesNotExist:  # pylint:disable=no-member
            return abort(404, 'user not found')

    @jwt_required
    @use_kwargs(users_validator.update_args())
    @marshal_with(UserSchema(decorate=True))
    def patch(self, **params):
        """Logic for updating a user"""
        id = params.pop("id")
        try:
            user = User.find_by(id_=id)
            user.update(**params)
            return user
        except User.DoesNotExist:  # pylint:disable=no-member
            return abort(404, 'user not found')

    @jwt_required
    @use_kwargs(users_validator.update_args())
    @marshal_with(UserSchema(decorate=True))
    def put(self, **params):
        """Logic for updating a user"""
        id = params.pop("id")
        try:
            user = User.find_by(id_=id)
            if "password" in params:
                password = params.pop("password")
                old_password = params.pop("old_password", None)
                success = user.update_password(password, old_password)
                print(success)
                if not success:
                    return {"error": "old password is not correct"}, 422
            user.update(**params)
            return user
        except User.DoesNotExist:  # pylint:disable=no-member
            return abort(404, 'user not found')

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


class UsersController(MethodResource):
    """ Controller for users """

    @jwt_required
    @use_kwargs(users_validator.index_args())
    @marshal_with(UserSchema(decorate=True, many=True))
    def get(self, **params):  # pylint: disable=W0613
        """Logic for querying several users"""
        return User.all()

    @use_kwargs(users_validator.create_args())
    @marshal_with(UserSchema(decorate=True))
    def post(self, **params):
        """Logic for creating a user"""
        try:
            user = User(**params).save()
        except exceptions.UniqueProperty:
            return abort(409, "Username or Email already taken")
        return user
