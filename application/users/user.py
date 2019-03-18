"""Access to User objects in Ne4J"""
from flask import current_app
from neomodel import StructuredNode, StringProperty, JSONProperty, RelationshipFrom, cardinality
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError

from application.extensions import bcrypt
from application.model_mixins import DefaultPropertyMixin, DefaultHelperMixin
from application.users.user_schema import UserSchema


class User(StructuredNode, DefaultPropertyMixin, DefaultHelperMixin):  # pylint:disable=abstract-method
    """The class that manages Users"""
    schema = UserSchema
    username = StringProperty(required=True, unique_index=True)
    email = StringProperty(required=True, unique_index=True)
    password = StringProperty(required=True)
    google_id = StringProperty()
    google_api_credentials = JSONProperty()

    teams = RelationshipFrom('application.models.Team', 'HAS_MEMBER', cardinality=cardinality.ZeroOrMore)
    artifacts = RelationshipFrom('application.models.Artifact', 'CREATED_BY', cardinality=cardinality.ZeroOrMore)

    @classmethod
    def find_by_email_or_username(cls, email_or_username):
        """Find a user by email or username and return the user or None"""
        return (cls.find_by(username=email_or_username, force=False)
                or cls.find_by(email=email_or_username, force=False))

    @property
    def connected_to_drive(self):
        if not self.google_api_credentials:
            return False
        credentials = credentials_from_dict(self.google_api_credentials)
        request = Request()
        try:
            credentials.refresh(request)
            return True
        except RefreshError:
            return False

    def hash_password(self, password):
        """Hash a password"""
        return bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Get password from hash"""
        return bcrypt.check_password_hash(self.password, password.encode('utf-8'))

    def update(self, **properties):
        if 'password' in properties:
            # This ensures that every saved password is hashed
            # If user.password is accessed directly this isn't ensured
            properties['password'] = self.hash_password(properties['password'])
        super().update(**properties)

    def pre_save(self):
        super()
        if self.does_not_exist():
            self.password = self.hash_password(self.password)


def get_google_credentials(auth_code):
    flow = Flow.from_client_secrets_file(
        current_app.config['CLIENT_SECRET_PATH'],
        scopes=None,
        redirect_uri='postmessage')
    flow.fetch_token(code=auth_code)
    return credentials_to_dict(flow.credentials)


def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}


def credentials_from_dict(credentials):
    return Credentials(**credentials)
