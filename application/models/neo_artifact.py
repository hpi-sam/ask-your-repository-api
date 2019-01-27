"""Access to Artifacts via Neo4J"""
from py2neo.ogm import Property, RelatedTo
from .neo_model import NeoModel
from .neo_tag import NeoTag


class NeoArtifact(NeoModel):
    """The Neo Artifact Model"""
    __primarylabel__ = "NeoArtifact"
    url = Property()
    tags = RelatedTo(NeoTag, "TAGGED_WITH")

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
