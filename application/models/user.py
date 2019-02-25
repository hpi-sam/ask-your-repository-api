""" Access to User objects in Ne4J """
from neomodel import StructuredNode, StringProperty, RelationshipFrom

from ..models.mixins import DefaultPropertyMixin, DefaultHelperMixin
from ..schemas.user_schema import UserSchema
from ..extensions import bcrypt

class User(StructuredNode, DefaultPropertyMixin, DefaultHelperMixin):  # pylint:disable=abstract-method
    """ The class that manages Users """
    schema = UserSchema
    username = StringProperty(required=True, unique_index=True)
    email = StringProperty(required=True, unique_index=True)
    password = StringProperty(required=True)

    teams = RelationshipFrom('.Team', 'HAS_MEMBER')

    @classmethod
    def find_by_email_or_username(cls, email_or_username):
        """Find a user by email or username and return the user or None"""
        return (cls.find_by(username=email_or_username, force=False)
                or cls.find_by(email=email_or_username, force=False))

    def pre_save(self):
        super()
        self.password = bcrypt.generate_password_hash(self.password).decode('utf-8')
