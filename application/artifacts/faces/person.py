"""Access to Persons via Neo4J"""

from neomodel import StructuredNode, StringProperty, RelationshipTo, RelationshipFrom, cardinality

from application.model_mixins import DefaultPropertyMixin, DefaultHelperMixin


class Person(StructuredNode, DefaultPropertyMixin, DefaultHelperMixin):
    """The class that manages persons"""

    name = StringProperty(required=True)

    faces = RelationshipFrom("application.models.Face", "BELONGS_TO", cardinality=cardinality.OneOrMore)
    artifacts = RelationshipFrom("application.models.Artifact", "CONTAINS_FACE", cardinality=cardinality.ZeroOrMore)
