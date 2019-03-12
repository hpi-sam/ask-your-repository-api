"""
Handles all logic of the user api
"""
from neomodel import exceptions
from flask_jwt_extended import jwt_required
from webargs.flaskparser import use_args

from .application_controller import ApplicationController
from .authentications_controller import validate_user
from ..models.user import User
from ..responders import respond_with, no_content
from ..validators import users_validator

class UsersController(ApplicationController):
    """ Controller for users """

    @jwt_required
    def show(self, object_id):
        try:
            user = User.find_by(id_=object_id)
            return respond_with(user), 200
        except User.DoesNotExist:  # pylint:disable=no-member
            return {"error": "not found"}, 404

    @jwt_required
    @use_args(users_validator.index_args())
    def index(self, params):  # pylint: disable=W0613
        """Logic for querying several users"""
        users = User.all()
        return {"users": respond_with(users)}, 200

    @use_args(users_validator.create_args())
    def create(self, params):
        """Logic for creating a user"""
        try:
            user = User(**params).save()
        except exceptions.UniqueProperty:
            return {"error": "Username or Email already taken"}, 409
        return respond_with(user), 200

    @jwt_required
    @use_args(users_validator.update_args())
    def update(self, params, object_id):
        """Logic for updating a user"""
        object_id = params.pop("id")
        try:
            user = User.find_by(id_=object_id)
            user.update(**params)
            return respond_with(user), 200
        except User.DoesNotExist:  # pylint:disable=no-member
            return {"error": "not found"}, 404

    @jwt_required
    @use_args(users_validator.delete_args())
    def delete(self, params, object_id):
        """Logic for deleting a user"""
        object_id = params["id"]
        try:
            user = User.find_by(id_=object_id)
            user.delete()
            return no_content()
        except User.DoesNotExist:  # pylint:disable=no-member
            return {"error": "not found"}, 404

    @jwt_required
    @use_args(users_validator.change_password_args())
    def change_password(self, params, object_id):
        """Logic for changing the password of a user"""
        object_id = params.pop("id")
        try:
            user = User.find_by(id_=object_id)
            if validate_user(user, params["old_password"]):
                user.update_password(password=params["new_password"])
                return respond_with(user), 200
            return {"error": "old password is not correct"}, 422
        except User.DoesNotExist:  # pylint:disable=no-member
            return {"error": "not found"}, 404
