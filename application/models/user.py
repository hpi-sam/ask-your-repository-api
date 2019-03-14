""" Access to User objects in Ne4J """
from neomodel import StructuredNode, StringProperty, RelationshipFrom, cardinality

from ..models.mixins import DefaultPropertyMixin, DefaultHelperMixin
from ..schemas.user_schema import UserSchema
from ..extensions import bcrypt

class User(StructuredNode, DefaultPropertyMixin, DefaultHelperMixin):  # pylint:disable=abstract-method
    """ The class that manages Users """
    schema = UserSchema
    username = StringProperty(required=True, unique_index=True)
    email = StringProperty(required=True, unique_index=True)
    password = StringProperty(required=True)

    teams = RelationshipFrom('.Team', 'HAS_MEMBER', cardinality=cardinality.ZeroOrMore)
    artifacts = RelationshipFrom('.Artifact', 'CREATED_BY', cardinality=cardinality.ZeroOrMore)

    @classmethod
    def find_by_email_or_username(cls, email_or_username):
        """Find a user by email or username and return the user or None"""
        return (cls.find_by(username=email_or_username, force=False)
                or cls.find_by(email=email_or_username, force=False))

    def generate_password(self, password):
        """ Hash a password """
        return bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """ Get password from hash """
        return bcrypt.check_password_hash(self.password, password.encode('utf-8'))

    def update_password(self, password, old_password):
        """ Update a password of a user to a new password """
        if old_password and self.check_password(old_password):
            self.password = self.generate_password(password)
            self.save()
            return True
        return False

    def pre_save(self):
        super()
        if self.does_not_exist():
            self.password = self.generate_password(self.password)
