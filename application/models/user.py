""" Access to User objects in Ne4J """
from neomodel import StructuredNode, StringProperty, EmailProperty, Relationship

from ..models.mixins import DefaultPropertyMixin, DefaultHelperMixin
from ..schemas.user_schema import UserSchema
from ..extensions import bcrypt

class User(StructuredNode, DefaultPropertyMixin, DefaultHelperMixin):  # pylint:disable=abstract-method
    """ The class that manages Users """
    schema = UserSchema
    username = StringProperty(required=True, unique_index=True)
    email = StringProperty(required=True, unique_index=True)
    password = StringProperty(required=True)

    teams = Relationship('.Team', 'MEMBER')

    def pre_save(self):
        super()
        self.password = bcrypt.generate_password_hash(self.password).decode('utf-8')
