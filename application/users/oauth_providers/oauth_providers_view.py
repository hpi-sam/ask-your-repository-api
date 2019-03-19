from flask import abort
from flask_apispec import MethodResource, marshal_with, use_kwargs
from application.users.user import User
from application.users.user_schema import USER_SCHEMA
from application.users.oauth_providers import oauth_providers_validator
from application.users.oauth_providers.oauth_provider import OAuthProvider


class OAuthProvidersView(MethodResource):

    @use_kwargs(oauth_providers_validator.create_args())
    @marshal_with(USER_SCHEMA)
    def post(self, **params):
        user = User.find(params['id'])
        auth_provider = OAuthProvider.create_from_id_token(name=params['provider'], id_token=params['id_token'])
        auth_provider.user.connect(user)
        auth_provider.save()
        return user


class OAuthProviderView(MethodResource):

    @use_kwargs(oauth_providers_validator.update_args())
    @marshal_with(USER_SCHEMA)
    def patch(self, **params):
        user = User.find(params['id'])
        try:
            auth_provider = user.oauth_providers.get(name=params['provider'])
            auth_provider.credentials = auth_provider.retrieve_credentials(params['auth_code'])
            auth_provider.save()
        except OAuthProvider.DoesNotExist:
            abort(404, 'provider not found')
        return user

    def put(self, **params):
        self.patch(**params)


class OAuthScopes(MethodResource):

    @use_kwargs(oauth_providers_validator.revoke_access_args())
    @marshal_with(USER_SCHEMA)
    def delete(self, **params):
        user = User.find(params['id'])
        auth_provider = user.oauth_providers.get(name=params['provider'])
        success = auth_provider.revoke_access()
        if not success:
            abort(502, 'could not revoke access')
        return user

