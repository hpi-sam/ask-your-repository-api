"""Access to Drive objects in Ne4J"""
from neomodel import StructuredNode, StringProperty, cardinality, RelationshipFrom, RelationshipTo, BooleanProperty
from neomodel.exceptions import MultipleNodesReturned

from application.model_mixins import DefaultPropertyMixin, DefaultHelperMixin

# import application.artifacts.artifact.Artifact.DoesNotExist as ArtifactDoesNotExist
from application.teams.drives.contains_rel import ContainsRel
from application.teams.drives.sync.sync import Sync


class Drive(StructuredNode, DefaultPropertyMixin, DefaultHelperMixin):  # pylint:disable=abstract-method
    """The class that manages Drives"""

    drive_id = StringProperty(required=True)
    page_token = StringProperty()
    is_syncing = BooleanProperty(default=False)
    url = StringProperty()
    name = StringProperty()

    team_rel = RelationshipFrom("application.models.Team", "SYNCED_TO", cardinality=cardinality.ZeroOrOne)
    owner_rel = RelationshipFrom("application.models.User", "OWNS", cardinality=cardinality.ZeroOrOne)
    files = RelationshipTo(
        "application.models.Artifact", "CONTAINS", model=ContainsRel, cardinality=cardinality.ZeroOrMore
    )

    @property
    def team(self):
        return self.team_rel.single()

    @property
    def owner(self):
        return self.owner_rel.single()

    def find_artifact_by(self, gdrive_file_id, force=True):
        results = self.files.match(gdrive_file_id=gdrive_file_id)
        if len(results) > 1:
            raise MultipleNodesReturned
        if len(results) == 0:
            if force:
                raise Exception("ArtifactDoesNotExist")
            else:
                return None
        return results[0]

    @classmethod
    def sync_all(cls):
        for drive in Drive.nodes.filter(is_syncing=False):
            Sync(drive).sync_drive()
