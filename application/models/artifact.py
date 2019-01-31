""" Abstracting Sync of Neo and Elastic"""
from .elastic_artifact import ElasticArtifact
from .neo_artifact import NeoArtifact
from .neo_tag import NeoTag


class Artifact:
    """ This class abstracts syncing of Neo and Elastic """

    def __init__(self, **properties):
        self.neo = NeoArtifact(url=properties.get('file_url', ''))
        properties['id'] = self.neo.id
        self._set_full_tags(properties)

        self.elastic = ElasticArtifact(properties)

    def save(self):
        """Save both models"""
        self.neo.save()
        self.elastic.save()

    def _add_tags_to_neo(self, tags):
        for tag in tags:
            self.neo.tags.add(NeoTag.find_or_create_by(name=tag))

    def _add_label_annotation_to_neo(self, annotations):
        for annotation in annotations:
            self.neo.label_annotations.add(NeoTag.find_or_create_by(name=annotation))

    def _add_text_annotation_to_neo(self, annotations):
        for annotation in annotations:
            self.neo.text_annotations.add(NeoTag.find_or_create_by(name=annotation))

    def _set_full_tags(self, properties):
        if 'tags' in properties:
            self._add_tags_to_neo(properties['tags'])
        if 'label_annotations' in properties:
            self._add_label_annotation_to_neo(properties['label_annotations'])
        if 'text_annotations' in properties:
            self._add_text_annotation_to_neo(properties['text_annotations'])

    def update(self, **properties):
        """Update both models"""
        if 'file_url' in properties:
            self.neo.update(url=properties['file_url'])
        self._set_full_tags(properties)
        self.neo.save()
        self.elastic.update(properties)

    @classmethod
    def search(cls, search_params):
        """Search for artifact in Elastic"""
        return ElasticArtifact.search(search_params)

    def delete(self):
        """Delete both models"""
        self.elastic.delete()
        self.neo.delete()

    @classmethod
    def find(cls, id, force=True):  # pylint: disable= invalid-name
        """Finds Artifact and creates instances"""
        artifact = Artifact()
        artifact.elastic = ElasticArtifact.find(id)
        if NeoArtifact.exists(id=id):
            artifact.neo = NeoArtifact.find_by(id=id, force=force)
        else:
            artifact.neo = NeoArtifact(url=artifact.elastic.file_url, id=str(artifact.elastic.id))
            artifact._add_tags_to_neo(artifact.elastic.tags)  # pylint: disable= protected-access
            artifact.neo.save()
        return artifact
