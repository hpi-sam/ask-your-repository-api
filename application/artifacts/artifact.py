"""Access to Artifacts via Neo4J"""

from neomodel import StructuredNode, StringProperty, DateTimeProperty, RelationshipTo, RelationshipFrom, cardinality

from application.model_mixins import DefaultPropertyMixin, DefaultHelperMixin
from application.artifacts.artifact_schema import ArtifactSchema
from application.artifacts.elastic import ElasticSyncer
from application.teams.drives.contains_rel import ContainsRel
from application.artifacts.tags.labeled_with_rel import LabeledWithRel
from .artifact_deletor import ArtifactDeletor


class Artifact(StructuredNode, DefaultPropertyMixin, DefaultHelperMixin):
    """The class that manages artifacts"""

    schema = ArtifactSchema
    file_url = StringProperty(required=True)
    file_date = DateTimeProperty()

    user_tags = RelationshipTo("application.models.Tag", "TAGGED_WITH", cardinality=cardinality.ZeroOrMore)
    label_tags = RelationshipTo(
        "application.models.Tag", "LABELED_WITH", cardinality=cardinality.ZeroOrMore, model=LabeledWithRel
    )
    text_tags = RelationshipTo("application.models.Tag", "CONTAINS_TEXT", cardinality=cardinality.ZeroOrMore)
    team = RelationshipFrom("application.models.Team", "UPLOADED", cardinality=cardinality.ZeroOrOne)
    user = RelationshipTo("application.models.User", "CREATED_BY", cardinality=cardinality.ZeroOrOne)
    drive_folder = RelationshipFrom(
        "application.models.Drive", "CONTAINS", cardinality=cardinality.ZeroOrOne, model=ContainsRel
    )

    faces = RelationshipTo("application.models.Face", "CONTAINS_FACE", cardinality=cardinality.ZeroOrMore)
    persons = RelationshipFrom("application.models.Person", "APPEARS_IN", cardinality=cardinality.ZeroOrMore)
    locations = RelationshipTo("application.models.Location", "LOCATED_AT", cardinality=cardinality.ZeroOrMore)

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
    def labeled_with(self):
        new_label_tags = []
        for tag in self.label_tags:
            rel = self.label_tags.relationship(tag)
            new_label_tags.append({
                "name": tag.name,
                "confidence": rel.score,
            })
        return new_label_tags

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
        ArtifactDeletor(self).delete()
