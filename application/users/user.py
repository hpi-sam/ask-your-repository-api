"""Access to User objects in Ne4J"""
from neomodel import StructuredNode, StringProperty, RelationshipFrom, RelationshipTo, cardinality

from application.extensions import bcrypt
from application.model_mixins import DefaultPropertyMixin, DefaultHelperMixin
from application.users.user_schema import UserSchema


class User(StructuredNode, DefaultPropertyMixin, DefaultHelperMixin):  # pylint:disable=abstract-method
    """The class that manages Users"""

    schema = UserSchema
    username = StringProperty(required=True, unique_index=True)
    email = StringProperty(required=True, unique_index=True)
    password = StringProperty()

    teams = RelationshipFrom("application.models.Team", "HAS_MEMBER", cardinality=cardinality.ZeroOrMore)
    artifacts = RelationshipFrom("application.models.Artifact", "CREATED_BY", cardinality=cardinality.ZeroOrMore)
    google_rel = RelationshipTo("application.models.GoogleOAuth", "HAS_GOOGLE_OAUTH", cardinality=cardinality.ZeroOrOne)
    drives = RelationshipTo("application.models.Drive", "OWNS", cardinality=cardinality.ZeroOrMore)

    @property
    def google(self):
        """Returns GoogleOauth Node"""
        return self.google_rel.single()  # pylint:disable=no-member

    @property
    def has_password(self):
        """Password might be empty when a user was created with Google sign in"""
        return bool(self.password)

    @classmethod
    def find_by_email_or_username(cls, email_or_username):
        """Find a user by email or username and return the user or None"""
        return cls.find_by(username=email_or_username, force=False) or cls.find_by(email=email_or_username, force=False)

    def hash_password(self, password):
        """Hash a password"""
        return bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        """Get password from hash"""
        return bcrypt.check_password_hash(self.password, password.encode("utf-8"))

    def update(self, **properties):
        if "password" in properties:
            # This ensures that every saved password is hashed
            # If user.password is accessed directly this isn't ensured
            properties["password"] = self.hash_password(properties["password"])
        super().update(**properties)

    def pre_save(self):
        super()
        if self.does_not_exist() and self.has_password:
            self.password = self.hash_password(self.password)
