"""Access to Day via Neo4J"""

from neomodel import StructuredNode, IntegerProperty, RelationshipTo, RelationshipFrom, cardinality


class Day(StructuredNode):
    """The class that manages days"""

    value = IntegerProperty(required=True)

    month = RelationshipFrom("application.models.Month", "CHILD", cardinality=cardinality.One)
    next_day = RelationshipTo("application.models.Day", "NEXT", cardinality=cardinality.ZeroOrOne)
