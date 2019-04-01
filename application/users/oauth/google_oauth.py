import json

import google.auth.transport.requests
import google.oauth2.credentials
import google.oauth2.id_token
import google_auth_oauthlib.flow
import requests
from flask import current_app
from google.auth.exceptions import RefreshError
from neomodel import StructuredNode, StringProperty, JSONProperty, RelationshipFrom, cardinality

from application.model_mixins import DefaultPropertyMixin, DefaultHelperMixin


def validate_google_id_token(token):
    """Validates a google id_token.
    See https://developers.google.com/identity/sign-in/web/backend-auth?hl=de for reference.
    """
    info = None
    client_ids = json.load(open(current_app.config['CLIENT_IDS_PATH']))
    for client in client_ids:
        info = validate_google_id_token_with_client_id(token, client) or info
    return info


def validate_google_id_token_with_client_id(token, client_id):
    try:
        id_info = google.oauth2.id_token.verify_oauth2_token(token,
                                                             google.auth.transport.requests.Request(),
                                                             client_id)
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
    return google.oauth2.credentials.Credentials(**credentials)


class GoogleOAuthConflict(Exception):

    def __init__(self, message):
        self.message = message


class EmptyCredentialsError(Exception):
    pass


class RequestError(Exception):
    pass


class GoogleOAuth(StructuredNode, DefaultPropertyMixin, DefaultHelperMixin):
    user_id = StringProperty(required=True)
    credentials = JSONProperty()

    user_rel = RelationshipFrom('application.models.User', 'HAS_GOOGLE_OAUTH',
                                cardinality=cardinality.One)

    @classmethod
    def create_from_id_token(cls, token):
        google_id, _ = validate_google_id_token(token)
        existing_google_oauth = cls.find_by(user_id=google_id, force=False)
        if existing_google_oauth:
            raise GoogleOAuthConflict(f"User: {existing_google_oauth.user.username} "
                                      f"is already connected with that google account")
        return cls(user_id=google_id).save()

    @property
    def user(self):
        return self.user_rel.single()

    @property
    def has_offline_access(self):
        if not self.credentials:
            return False
        credentials = credentials_from_dict(self.credentials)
        request = google.auth.transport.requests.Request()
        try:
            credentials.refresh(request)
            return True
        except RefreshError:
            return False

    def set_credentials(self, auth_code):
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            current_app.config['CLIENT_SECRET_PATH'],
            scopes=None,
            redirect_uri='postmessage')
        flow.fetch_token(code=auth_code)
        self.credentials = credentials_to_dict(flow.credentials)

    def revoke_access(self):
        if not self.credentials:
            raise EmptyCredentialsError
        revoke = requests.post('https://accounts.google.com/o/oauth2/revoke',
                               params={'token': self.credentials['token']},
                               headers={'content-type': 'application/x-www-form-urlencoded'})
        if not revoke.status_code == 200:
            raise RequestError
        self.credentials = None
        self.save()
