from application.users.oauth.google_oauth import GoogleOAuth
from specs.factories.user_factory import UserFactory
google_credentials = {
    'token': 'test_token',
    'refresh_token': 'test_refresh_token',
    'token_uri': 'test_token_uri',
    'client_id': 'test_client_id',
    'client_secret': 'test_client_secret',
    'scopes': 'test_scope_1 test_scope2'
}

google_user_data = {
    'iss': 'accounts.google.com',
    'sub': 'google_user_id',
    'email': 'test_user@example.com'
}


class GoogleOAuthFactory:

    @classmethod
    def create_google_oauth(cls, *args, **kwargs):
        return cls.build_google_oauth(*args, **kwargs).save()

    @classmethod
    def create_user_with_google(cls, *args, credentials=None, **kwargs):
        user = UserFactory.create_user(*args, **kwargs)
        google_oauth = cls.create_google_oauth(credentials=credentials)
        user.google_rel.connect(google_oauth)
        return user

    @classmethod
    def build_google_oauth(cls, user_id=google_user_data['sub'],  credentials=None):
        return GoogleOAuth(user_id=user_id, credentials=credentials)
