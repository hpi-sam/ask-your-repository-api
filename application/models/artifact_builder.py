""" Abstracting Sync of Neo and Elastic"""
import uuid

from . import Artifact, Tag, Team
from .property_builder import PropertyBuilder


class ArtifactBuilder:
    """ This class helps with building Artifacts """

    @classmethod
    def for_artifact(cls, neo):
        """ Create an ArtifactBuilder for a specific Artifact """
        builder = cls()
        builder.neo = neo
        return builder

    def __init__(self):
        self.neo = None

    def build_with(self, **properties):
        """ builds self.neo and saves it"""
        props = PropertyBuilder(**properties)
        neo_properties = props.node_properties
        self.neo = Artifact(**neo_properties).save()
        self.build_relations(props.relationship_properties, False)
        return self.neo

    def build_relations(self, props, override_tags):
        """Create all relations on the artifact object as described in props."""
        self._set_full_tags(props, override_tags)
        if 'team_id' in props and props.get('team_id') is not None:
            self._connect_to_team(props['team_id'])

    def save(self):
        """Save both models"""
        self.neo.save()

    def _add_tags_to_neo(self, new_tags, tag_relation, override=False):
        if override:
            tag_relation.disconnect_all()
        for tag in new_tags:
            created_tag = Tag.find_or_create_by(name=tag)
            tag_relation.connect(created_tag)
        self.neo.save()

    def _set_full_tags(self, properties, override_tags):
        if 'user_tags' in properties:
            self._add_tags_to_neo(properties['user_tags'], self.neo.user_tags, override_tags)
        if 'label_tags' in properties:
            self._add_tags_to_neo(properties['label_tags'], self.neo.label_tags)
        if 'text_tags' in properties:
            self._add_tags_to_neo(properties['text_tags'], self.neo.text_tags)

    def update_with(self, override_tags=True, **properties):
        """Update both models"""
        props = PropertyBuilder(**properties)
        neo_properties = props.node_properties
        self.build_relations(props.relationship_properties, override_tags)
        self.neo.update(**neo_properties)

    @classmethod
    def find(cls, id, force=True):  # pylint: disable= invalid-name
        """Finds Artifact and creates instances"""
        artifact = ArtifactBuilder()
        if not isinstance(id, uuid.UUID):
            id = uuid.UUID(id)
        artifact.neo = Artifact.find_by(force=force, id_=str(id))
        return artifact

    def _overwrite_team(self, team_id):
        self.neo.team.disconnect_all()
        self._connect_to_team(team_id)

    def _connect_to_team(self, team_id):
        if not isinstance(team_id, uuid.UUID):
            team_id = uuid.UUID(team_id)
        self.neo.team.connect(Team.find_by(id_=str(team_id)))
        self.neo.save()
