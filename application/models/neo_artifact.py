"""Access to Artifacts via Neo4J"""
from py2neo.ogm import Property, RelatedTo

from .neo_model import NeoModel
from .neo_tag import NeoTag


class NeoArtifact(NeoModel):
    """The Neo Artifact Model"""
    __primarylabel__ = "NeoArtifact"
    url = Property()
    tags = RelatedTo(NeoTag, "TAGGED_WITH")
    label_annotations = RelatedTo(NeoTag, "ANNOTATED_WITH_LABEL")
    text_annotations = RelatedTo(NeoTag, "ANNOTATED_WITH_TEXT")

    def __init__(self, url='', id=None):
        super().__init__(id=id)
        self.url = url
        self._tags = []

    def tag_list(self):
        """Return list of tags as strings"""
        array = list()
        for tag in self.tags:
            array.append(tag.name)
        return array

    def label_annotation_list(self):
        """Returns a list of label annotations as strings"""
        array = list()
        for annotation in self.label_annotations:
            array.append(annotation.name)
        return array

    def text_annotation_list(self):
        """Returns a list of text annotations as strings"""
        array = list()
        for annotation in self.text_annotations:
            array.append(annotation.name)
        return array

    def full_tag_list(self):
        """Returns a list of all tags, text annotations and label annotations as stings"""
        array = self.tag_list()
        array += self.label_annotation_list()
        array += self.text_annotation_list()
        return array
