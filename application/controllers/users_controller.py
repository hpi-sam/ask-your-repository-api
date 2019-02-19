"""
Handles all logic of the user api
"""
from flask import current_app, jsonify
from flask_jwt_extended import jwt_required, create_access_token, set_access_cookies, get_csrf_token
from webargs.flaskparser import use_args

from .application_controller import ApplicationController
from ..models.user import User
from ..responders import respond_with, no_content
from ..validators import users_validator
from ..extensions import bcrypt

class UsersController(ApplicationController):
    """ Controller for users """

    @jwt_required
    def show(self, object_id):
        try:
            user = User.find_by(id_=object_id)
            return respond_with(user), 200
        except User.DoesNotExist:  # pylint:disable=no-member
            return {"error": "not found"}, 404

    #@jwt_required
    @use_args(users_validator.index_args())
    def index(self, params):  # pylint: disable=W0613
        """Logic for querying several users"""
        users = User.all()
        return {"users": respond_with(users)}, 200

    @use_args(users_validator.create_args())
    def create(self, params):
        """Logic for creating a user"""
        user = User(**params).save()
        return respond_with(user), 200

    @jwt_required
    @use_args(users_validator.update_args())
    def update(self, params, object_id):
        """Logic for updating a user"""
        try:
            user = User.find_by(id_=object_id)
            user.update(**params)
            return respond_with(user), 200
        except User.DoesNotExist:  # pylint:disable=no-member
            return {"error": "not found"}, 404

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

    @use_args(users_validator.login_args())
    def login(self, params):
        try:
            user = User.find_by(email=params["email"])
            if not bcrypt.check_password_hash(user.password, params["password"]):
                return {"error": "Bad username or password"}, 401
            access_token = create_access_token(identity=user.id_)
            response = respond_with(user)
            response["token"] = get_csrf_token(access_token)

            set_access_cookies(jsonify(response), access_token)
            return response, 200

        except User.DoesNotExist:  # pylint:disable=no-member
            return {"error": "Bad username or password"}, 401
