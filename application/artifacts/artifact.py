"""Access to Artifacts via Neo4J"""

from neomodel import StructuredNode, StringProperty, DateTimeProperty, RelationshipTo, RelationshipFrom, cardinality

from application.model_mixins import DefaultPropertyMixin, DefaultHelperMixin
from application.artifacts.artifact_schema import ArtifactSchema
from application.artifacts.elastic import ElasticSyncer


# pylint:disable=abstract-method
class Artifact(StructuredNode, DefaultPropertyMixin, DefaultHelperMixin):
    """The class that manages artifacts"""

    schema = ArtifactSchema
    file_url = StringProperty(required=True)
    file_date = DateTimeProperty()

    user_tags = RelationshipTo("application.models.Tag", "TAGGED_WITH", cardinality=cardinality.ZeroOrMore)
    label_tags = RelationshipTo("application.models.Tag", "LABELED_WITH", cardinality=cardinality.ZeroOrMore)
    text_tags = RelationshipTo("application.models.Tag", "CONTAINS_TEXT", cardinality=cardinality.ZeroOrMore)
    team = RelationshipFrom("application.models.Team", "UPLOADED", cardinality=cardinality.ZeroOrOne)
    user = RelationshipTo("application.models.User", "CREATED_BY", cardinality=cardinality.ZeroOrOne)
    drive_file = RelationshipTo('application.models.DriveFile', "HAS_DRIVE_FILE", cardinality=cardinality.ZeroOrOne)
    # <--Serialization methods-->
    # These methods should eventually be moved to the corresponding schema
    @property
    def tags(self):
        """Returns union of all tag types as tags."""
        return list(self.user_tags) + list(self.label_tags) + list(self.text_tags)

    @property
    def team_id(self):
        """Returns this artifacts teams id"""
        team = self.team.single()  # pylint:disable=no-member
        return team.id_ if team else None

    @property
    def author(self):
        """Returns this artifacts author"""
        return self.user.single()  # pylint:disable=no-member

    def post_save(self):
        """Sync with Elasticsearch"""
        super()
        ElasticSyncer.for_artifact(self).sync()

    def pre_delete(self):
        """Sync with Elasticsearch"""
        ElasticSyncer.for_artifact(self).delete()
