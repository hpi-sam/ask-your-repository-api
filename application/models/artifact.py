""" Access to Artifacts via Neo4J """

from neomodel import (StructuredNode, StringProperty, DateTimeProperty,
                      RelationshipTo, RelationshipFrom)

from application.models.mixins import DefaultPropertyMixin, DefaultHelperMixin
from application.schemas.artifact_schema import NeoArtifactSchema


class Artifact(StructuredNode, DefaultPropertyMixin, DefaultHelperMixin):  # pylint:disable=abstract-method
    """ The class that manages artifacts """
    schema = NeoArtifactSchema
    file_url = StringProperty(required=True)
    file_date = DateTimeProperty()

    tags = RelationshipTo('.Tag', 'TAGGED_WITH')
    team = RelationshipFrom('.Team', 'UPLOADED')

    # <--Serialization methods-->
    # These methods should eventually be moved to the corresponding schema

    @property
    def team_id(self):
        """ Returns this artifacts teams id """
        teams = list(self.team)
        team_id = None
        if teams:
            team_id = teams[0].id_
        return team_id

    @property
    def tags_list(self):
        """ Returns this artifacts tags as string array """
        tags_list = []
        for tag in self.tags:  # pylint:disable=not-an-iterable
            tags_list.append(tag.name)
        return tags_list
