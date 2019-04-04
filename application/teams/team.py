"""Access to Team objects in Ne4J"""
from neomodel import StructuredNode, StringProperty, RelationshipTo, cardinality

from application.model_mixins import DefaultPropertyMixin, DefaultHelperMixin
from application.teams.team_schema import TeamSchema


class Team(StructuredNode, DefaultPropertyMixin, DefaultHelperMixin):  # pylint:disable=abstract-method
    """The class that manages Teams"""

    schema = TeamSchema
    name = StringProperty(required=True)
    join_key = StringProperty(required=False)

    artifacts = RelationshipTo("application.models.Artifact", "UPLOADED", cardinality=cardinality.ZeroOrMore)
    members = RelationshipTo("application.models.User", "HAS_MEMBER", cardinality=cardinality.ZeroOrMore)
