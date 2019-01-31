"""Accessing tags in neo"""
from py2neo.ogm import RelatedFrom, Property

from .neo_model import NeoModel


class NeoTag(NeoModel):
    """The Tag Model"""
    node_label = "NeoTag"
    __primarylabel__ = "NeoTag"

    name = Property()

    tagged_images = RelatedFrom("NeoArtifact", "TAGGED_WITH")
    label_annotated_images = RelatedFrom("NeoArtifact", "ANNOTATED_WITH_LABEL")
    text_annotated_images = RelatedFrom("NeoArtifact", "ANNOTATED_WITH_TEXT")



    def __init__(self, name='', id=None):
        super().__init__(id=id)
        self.name = name
