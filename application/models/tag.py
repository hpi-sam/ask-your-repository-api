""" Access to Tag object from Neo4J """
from neomodel import StructuredNode, StringProperty, RelationshipFrom

from application.models.mixins import DefaultPropertyMixin, DefaultHelperMixin


# pylint:disable=abstract-method
class Tag(StructuredNode, DefaultPropertyMixin, DefaultHelperMixin):
    """ The class that manages Tags """
    name = StringProperty(required=True, unique_index=True)

    user_tagged_artifacts = RelationshipFrom('.Artifact', 'TAGGED_WITH')
    label_tagged_artifacts = RelationshipFrom('.Artifact', 'LABELED_WITH')
    text_tagged_artifacts = RelationshipFrom('.Artifact', 'CONTAINS_TEXT')

    @property
    def artifacts(self):
        """Return all connected artifacts."""
        return list(self.user_tagged_artifacts) + list(self.label_tagged_artifacts) + list(
            self.text_tagged_artifacts)
