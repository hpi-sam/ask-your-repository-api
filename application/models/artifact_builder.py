""" Abstracting Sync of Neo and Elastic"""
import uuid

from . import Artifact, Tag, Team
from .elastic_artifact import ElasticArtifact


class ArtifactBuilder:
    """ This class abstracts syncing of Neo and Elastic """

    def __init__(self):
        self.elastic = None
        self.neo = None

    def build_with(self, **properties):
        """ builds self.neo and self.elastic neo is saved elastic not"""
        neo_properties = self._make_properties_neo_compatible(**properties)
        self.neo = Artifact(**neo_properties).save()
        if 'tags' in properties:
            self._add_tags_to_neo(properties['tags'])
        if 'team_id' in properties and properties.get('team_id') is not None:
            self._connect_to_team(properties['team_id'])
        properties['id'] = self.neo.id_
        self.elastic = ElasticArtifact(properties)

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
        self.elastic.save()
        self.neo.save()

    def _add_tags_to_neo(self, tags):
        for tag in tags:
            created_tag = Tag.find_or_create_by(name=tag)
            self.neo.tags.connect(created_tag)

    def update(self, **properties):
        """Update both models"""
        self.elastic.update(properties)
        neo_properties = self._make_properties_neo_compatible(**properties)
        if 'tags' in properties:
            self._add_tags_to_neo(properties['tags'])
        if 'team_id' in properties:
            self._connect_to_team(properties['team_id'])
        self.neo.update(**neo_properties)

    @classmethod
    def search(cls, search_params):
        """Search for artifact in Elastic"""
        return ElasticArtifact.search(search_params)

    def delete(self):
        """Delete both models"""
        self.elastic.delete()
        self.neo.delete()

    @classmethod
    def find_multiple(cls, params):
        """Find multiple neo artifacts with paramters limit, offset and team_id"""
        team = Team.find_by(params.get('team_id'))
        if team is None:
            artifacts = Artifact.nodes
        else:
            artifacts = team.artifacts
        _from = params.get('offset', 0)
        _to = params.get('limit', 10) + _from
        return artifacts.order_by('created_at')[_from:_to]

    @classmethod
    def find(cls, id, force=True):  # pylint: disable= invalid-name
        """Finds Artifact and creates instances"""
        artifact = ArtifactBuilder()
        artifact.elastic = ElasticArtifact.find(id)
        if not isinstance(id, uuid.UUID):
            id = uuid.UUID(id)
        artifact.neo = Artifact.find_by(force=force, id_=str(id))
        return artifact

    def _connect_to_team(self, team_id):
        if not isinstance(team_id, uuid.UUID):
            team_id = uuid.UUID(team_id)
        self.neo.team.connect(Team.find_by(id_=str(team_id)))
