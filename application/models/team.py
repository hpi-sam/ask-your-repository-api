""" Access to Team objects in Ne4J """
from neomodel import StructuredNode, StringProperty, RelationshipTo

from application.models.mixins import DefaultPropertyMixin, DefaultHelperMixin
from application.schemas.team_schema import TeamSchema


class Team(StructuredNode, DefaultPropertyMixin, DefaultHelperMixin):  # pylint:disable=abstract-method
    """ The class that manages Teams """
    schema = TeamSchema
    name = StringProperty(required=True)

    artifacts = RelationshipTo('.Artifact', 'UPLOADED')
    members = RelationshipTo('.User', 'HAS_MEMBER')
