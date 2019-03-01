""" Access to Artifacts via Neo4J """

from neomodel import (StructuredNode, StringProperty, DateTimeProperty,
                      RelationshipTo, RelationshipFrom)

from application.models.mixins import DefaultPropertyMixin, DefaultHelperMixin
from application.schemas.artifact_schema import NeoArtifactSchema
from .elastic import ElasticSyncer


# pylint:disable=abstract-method
class Artifact(StructuredNode, DefaultPropertyMixin,
               DefaultHelperMixin):
    """ The class that manages artifacts """
    schema = NeoArtifactSchema
    file_url = StringProperty(required=True)
    file_date = DateTimeProperty()

    user_tags = RelationshipTo('.Tag', 'TAGGED_WITH')
    label_tags = RelationshipTo('.Tag', 'LABELED_WITH')
    text_tags = RelationshipTo('.Tag', 'CONTAINS_TEXT')
    team = RelationshipFrom('.Team', 'UPLOADED')

    # <--Serialization methods-->
    # These methods should eventually be moved to the corresponding schema
    @property
    def tags(self):
        """Returns union of all tag types as tags."""
        return list(self.user_tags) + list(self.label_tags) + list(self.text_tags)

    @property
    def team_id(self):
        """ Returns this artifacts teams id """
        teams = list(self.team)
        return teams[0].id_ if teams else None

    def post_save(self):
        """Sync with Elasticsearch"""
        super()
        ElasticSyncer.for_artifact(self).sync()

    def pre_delete(self):
        """Sync with Elasticsearch"""
        ElasticSyncer.for_artifact(self).delete()
