from unittest.mock import patch, Mock, MagicMock
from application.users.user import User
from application.users.oauth.google_oauth import GoogleOAuth

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


def google_credentials_mock():
    global google_credentials
    mock = Mock()
    mock.configure_mock(**google_credentials)
    mock.refresh.return_value = None
    return mock


def google_flow_mock():
    global google_credentials
    mock = Mock()
    mock.configure_mock(credentials=google_credentials_mock())
    mock.fetch_token.return_value = None
    return mock


def google_revoke_access_request(status_code):
    mock = Mock(status_code=status_code)
    return mock


def google_revoke_access_patch(status_code=200):
    return patch('requests.post', return_value=google_revoke_access_request(status_code))


google_auth_patch = patch('google.oauth2.id_token.verify_oauth2_token', return_value=google_user_data)
google_flow_patch = patch('google_auth_oauthlib.flow.Flow.from_client_secrets_file',
                          return_value=google_flow_mock())
google_credentials_patch = patch('google.oauth2.credentials.Credentials', return_value=google_credentials_mock())


class UserFactory:

    @classmethod
    def create_user(cls, *args, **kwargs):
        return cls.build_user(*args, **kwargs).save()

    @classmethod
    def create_user_with_google(cls, *args, **kwargs ):
        global google_user_data
        user = cls.build_user(*args, **kwargs).save()
        google_oauth = GoogleOAuth(user_id=google_user_data['sub']).save()
        user.google_rel.connect(google_oauth)
        return user.save()

    @classmethod
    def build_user(cls, username="TestUser", email="test@example.com"):
        return User(username=username,
                        email=email,
                        password='test')
