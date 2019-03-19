import requests
from flask import current_app
from google.oauth2 import id_token
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError


def validate_google_id_token(token):
    """Validates a google id_token.
    See https://developers.google.com/identity/sign-in/web/backend-auth?hl=de for reference.
    """
    try:
        id_info = id_token.verify_oauth2_token(token,
                                               Request(),
                                               current_app.config['CLIENT_ID'])
        if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        # ID token is valid. Get the user's Google Account ID  and email from the decoded token.
        return id_info['sub'], id_info['email']
    except ValueError:
        pass


def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}


def credentials_from_dict(credentials):
    return Credentials(**credentials)


class GoogleOAuth():
    def __init__(self, *args, **kwargs):
        self.name = 'google'
        super().__init__(*args, **kwargs)

    def has_offline_access(self, credentials):
        if not credentials:
            return False
        credentials = credentials_from_dict(credentials)
        request = Request()
        try:
            credentials.refresh(request)
            return True
        except RefreshError:
            return False

    def retrieve_credentials(self, auth_code):
        flow = Flow.from_client_secrets_file(
            current_app.config['CLIENT_SECRET_PATH'],
            scopes=None,
            redirect_uri='postmessage')
        flow.fetch_token(code=auth_code)
        return credentials_to_dict(flow.credentials)

    def retrieve_user_id(self, id_token):
        google_id, _ = validate_google_id_token(id_token)
        return google_id

    def revoke_access(self, credentials):
        credentials = Credentials(**credentials)

        revoke = requests.post('https://accounts.google.com/o/oauth2/revoke',
                               params={'token': credentials.token},
                               headers={'content-type': 'application/x-www-form-urlencoded'})
        print(getattr(revoke, 'status_code'))
        return getattr(revoke, 'status_code') == 200
