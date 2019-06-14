"""Access to Faces via Neo4J"""

from neomodel import StructuredNode, StringProperty, ArrayProperty, BooleanProperty, FloatProperty, RelationshipTo, RelationshipFrom, cardinality

from application.model_mixins import DefaultPropertyMixin, DefaultHelperMixin


class Face(StructuredNode, DefaultPropertyMixin, DefaultHelperMixin):
    """The class that manages faces"""

    bounding_box = ArrayProperty(required=True, base_property=FloatProperty())
    file_url = StringProperty(required=True)
    is_verified = BooleanProperty(default=False)

    artifact = RelationshipFrom("application.models.Artifact", "CONTAINS_FACE", cardinality=cardinality.One)
    person = RelationshipTo("application.models.Person", "BELONGS_TO", cardinality=cardinality.ZeroOrOne)
