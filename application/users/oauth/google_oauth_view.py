from flask import abort
from flask_apispec import MethodResource, marshal_with, use_kwargs
from application.users.users_view import check_user
from application.users.user import User
from application.users.user_schema import USER_SCHEMA
from application.users.oauth import google_oauth_validator
from application.users.oauth.google_oauth import GoogleOAuth, EmptyCredentialsError, RequestError, GoogleOAuthConflict


class GoogleOauthView(MethodResource):

    @use_kwargs(google_oauth_validator.create_args())
    @marshal_with(USER_SCHEMA)
    @check_user
    def put(self, **params):
        user = User.find(params['id'])
        try:
            google_oauth = GoogleOAuth.create_from_id_token(params['id_token'])
            google_oauth.user_rel.connect(user)
            return user
        except GoogleOAuthConflict as err:
            abort(409, err.message)

    @use_kwargs(google_oauth_validator.update_args())
    @marshal_with(USER_SCHEMA)
    @check_user
    def patch(self, **params):
        user = User.find(params['id'])
        google_auth = user.google
        if not google_auth:
            abort(404, 'google oauth not found')
        google_auth.set_credentials(params['auth_code'])
        google_auth.save()
        return user


class GoogleScopesView(MethodResource):

    @use_kwargs(google_oauth_validator.revoke_access_args())
    @marshal_with(USER_SCHEMA)
    @check_user
    def delete(self, **params):
        user = User.find(params['id'])
        google_auth = user.google
        if not google_auth:
            abort(404, 'google oauth not found')
        try:
            google_auth.revoke_access()
        except EmptyCredentialsError:
            abort(404, 'google oauth has no offline access')
        except RequestError:
            abort(502, 'could not revoke access')
        return user

