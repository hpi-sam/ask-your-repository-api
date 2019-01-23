from .neo_ogm_model import NeoOGMModel
from .neo_tag import NeoTag
from py2neo.ogm import Property, RelatedTo


class NeoArtifact(NeoOGMModel):
    __primarylabel__ = "NeoArtifact"
    url = Property()
    tags = RelatedTo(NeoTag, "TAGGED_WITH")

    def __init__(self,  url='', id=None):
        super().__init__(id=id)
        self.url = url
        self._tags = []