from .neo_ogm_model import NeoOGMModel
from py2neo.ogm import RelatedFrom, Property


class NeoTag(NeoOGMModel):
    node_label = "NeoTag"
    __primarylabel__ = "NeoTag"

    name = Property()

    images = RelatedFrom("NeoArtifact", "TAGGED_WITH")

    @classmethod
    def find_or_create_by(cls, name=''):
        tag = NeoTag.find_by(name=name)
        if tag is not None:
            return tag
        else:
            return NeoTag(name=name)

    def __init__(self,  name='', id=None):
        super().__init__(id=id)
        self.name = name
