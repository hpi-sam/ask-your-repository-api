"""Access to Month via Neo4J"""

from neomodel import StructuredNode, IntegerProperty, RelationshipTo, RelationshipFrom, cardinality


class Month(StructuredNode):
    """The class that manages months"""

    value = IntegerProperty(required=True)

    year = RelationshipFrom("application.models.Year", "CHILD", cardinality=cardinality.One)
    next_month = RelationshipTo("application.models.Month", "NEXT", cardinality=cardinality.ZeroOrOne)
    days = RelationshipTo("application.models.Day", "CHILD", cardinality=cardinality.ZeroOrMore)
