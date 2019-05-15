"""Access to Year via Neo4J"""

from neomodel import StructuredNode, IntegerProperty, RelationshipTo, cardinality


class Year(StructuredNode):
    """The class that manages years"""

    value = IntegerProperty(required=True, unique_index=True)

    months = RelationshipTo("application.models.Month", "CHILD", cardinality=cardinality.ZeroOrMore)
