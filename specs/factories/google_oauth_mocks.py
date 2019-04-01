from unittest.mock import patch, Mock

from specs.factories.google_oauth_factory import google_user_data, google_credentials


def google_credentials_mock():
    mock = Mock()
    mock.configure_mock(**google_credentials)
    mock.refresh.return_value = None
    return mock


def google_flow_mock():
    mock = Mock()
    mock.configure_mock(credentials=google_credentials_mock())
    mock.fetch_token.return_value = None
    return mock


def google_revoke_access_request(status_code):
    mock = Mock(status_code=status_code)
    return mock


def google_revoke_access_patch(status_code=200):
    return patch('requests.post', return_value=google_revoke_access_request(status_code))


def google_client_id_return():
    return ["id1", "id2"]


google_auth_patch = patch('google.oauth2.id_token.verify_oauth2_token',
                          return_value=google_user_data)
google_flow_patch = patch('google_auth_oauthlib.flow.Flow.from_client_secrets_file',
                          return_value=google_flow_mock())
google_credentials_patch = patch('google.oauth2.credentials.Credentials',
                                 return_value=google_credentials_mock())
google_client_id_patch_load = patch('json.load', return_value=google_client_id_return())
google_client_id_patch_open = patch('application.users.oauth.google_oauth.open')
