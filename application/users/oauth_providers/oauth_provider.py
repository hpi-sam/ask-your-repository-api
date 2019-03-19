from application.model_mixins import DefaultPropertyMixin, DefaultHelperMixin
from neomodel import StructuredNode, StringProperty, JSONProperty, RelationshipFrom, cardinality
from application.users.oauth_providers.google_oauth import GoogleOAuth


def get_provider(provider_name):
    """Returns the provider by provider_name.
    Register new providers here"""
    if provider_name == 'google':
        return GoogleOAuth()


class OAuthProvider(StructuredNode, DefaultPropertyMixin, DefaultHelperMixin):
    """Currently only supports google"""
    name = StringProperty(required=True)
    user_id = StringProperty(required=True)
    credentials = JSONProperty()

    user = RelationshipFrom('application.models.User', 'HAS_OAUTH_PROVIDER', cardinality=cardinality.One)

    @classmethod
    def create_from_id_token(cls, name, id_token):
        user_id = get_provider(name).retrieve_user_id(id_token)
        return cls(name=name, user_id=user_id).save()

    @property
    def has_offline_access(self):
        return get_provider(self.name).has_offline_access(self.credentials)

    def retrieve_credentials(self, auth_code):
        """Retrieves the credentials from an auth_code"""
        return get_provider(self.name).retrieve_credentials(auth_code)

    def revoke_access(self):
        """Revokes access for the OAuth provider"""
        success = get_provider(self.name).revoke_access(self.credentials)
        self.credentials = None
        return success
