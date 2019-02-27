""" Abstracting Sync of Neo and Elastic"""
import uuid

from . import Artifact, Tag, Team


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
        neo_properties = self._make_properties_neo_compatible(**properties)
        self.neo = Artifact(**neo_properties).save()
        if 'tags' in properties:
            self._add_tags_to_neo(properties['tags'])
        if 'team_id' in properties and properties.get('team_id') is not None:
            self._connect_to_team(properties['team_id'])
        properties['id'] = self.neo.id_
        return self.neo

    def _make_properties_neo_compatible(self, **properties):
        if 'type' in properties:
            properties.pop('type')
        if 'file' in properties:
            properties.pop('file')
        if 'team_id' in properties:
            properties.pop('team_id')
        if 'tags' in properties:
            properties.pop('tags')
        return properties

    def save(self):
        """Save both models"""
        self.neo.save()

    def _add_tags_to_neo(self, tags):
        for tag in tags:
            created_tag = Tag.find_or_create_by(name=tag)
            self.neo.tags.connect(created_tag)
        self.neo.save()

    def _overwrite_tags_in_neo(self, tags):
        self.neo.tags.disconnect_all()
        self._add_tags_to_neo(tags)

    def update_with(self, override_tags=True, **properties):
        """Update both models"""
        neo_properties = self._make_properties_neo_compatible(**properties)
        if 'tags' in properties:
            if override_tags:
                self._overwrite_tags_in_neo(properties['tags'])
            else:
                self._add_tags_to_neo(properties['tags'])
        if 'team_id' in properties:
            self._overwrite_team(properties['team_id'])
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
