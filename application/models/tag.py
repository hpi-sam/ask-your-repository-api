""" Access to Tag object from Neo4J """
from neomodel import StructuredNode, StringProperty, RelationshipFrom
from application.models.mixins import DefaultPropertyMixin, DefaultHelperMixin


class Tag(StructuredNode, DefaultPropertyMixin, DefaultHelperMixin):  # pylint:disable=abstract-method
    """ The class that manages Tags """
    # schema = ArtifactSchema does not exist yet
    name = StringProperty(required=True, unique_index=True)

    artifacts = RelationshipFrom('.Artifact', 'TAGGED_WITH')
