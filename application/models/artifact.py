""" Access to Artifacts via Neo4J """

from neomodel import (StructuredNode, StringProperty, DateTimeProperty,
                      RelationshipTo, RelationshipFrom, cardinality)

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

    user_tags = RelationshipTo('.Tag', 'TAGGED_WITH', cardinality=cardinality.ZeroOrOne)
    label_tags = RelationshipTo('.Tag', 'LABELED_WITH', cardinality=cardinality.ZeroOrOne)
    text_tags = RelationshipTo('.Tag', 'CONTAINS_TEXT', cardinality=cardinality.ZeroOrOne)
    team = RelationshipFrom('.Team', 'UPLOADED', cardinality=cardinality.ZeroOrOne)
    user = RelationshipTo('.User', 'CREATED_BY', cardinality=cardinality.ZeroOrOne)

    # <--Serialization methods-->
    # These methods should eventually be moved to the corresponding schema
    @property
    def tags(self):
        """Returns union of all tag types as tags."""
        return list(self.user_tags) + list(self.label_tags) + list(self.text_tags)

    @property
    def team_id(self):
        """ Returns this artifacts teams id """
        team = self.team.single()  # pylint:disable=no-member
        return team.id_ if team else None

    @property
    def author(self):
        """ Returns this artifacts author """
        return self.user.single()  # pylint:disable=no-member

    @property
    def tags_list(self):
        """ Returns this artifacts tags as string array """
        tags_list = []
        for tag in self.tags:  # pylint:disable=not-an-iterable
            tags_list.append(tag.name)
        return tags_list

    def post_save(self):
        """Sync with Elasticsearch"""
        super()
        ElasticSyncer.for_artifact(self).sync()

    def pre_delete(self):
        """Sync with Elasticsearch"""
        ElasticSyncer.for_artifact(self).delete()
