"""Access to Location via Neo4J"""

from neomodel import StructuredNode, StringProperty, ArrayProperty, BooleanProperty, FloatProperty, RelationshipTo, RelationshipFrom, cardinality

from application.model_mixins import DefaultPropertyMixin, DefaultHelperMixin


class Location(StructuredNode, DefaultPropertyMixin, DefaultHelperMixin):
    """The class that manages locations"""

    name = StringProperty(required=True)

    artifact = RelationshipFrom("application.models.Artifact", "LOCATED_AT", cardinality=cardinality.OneOrMore)
