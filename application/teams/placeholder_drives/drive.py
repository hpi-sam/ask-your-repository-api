"""Access to Drive objects in Ne4J"""
from neomodel import StructuredNode, StringProperty, cardinality, RelationshipFrom, RelationshipTo

from application.model_mixins import DefaultPropertyMixin, DefaultHelperMixin
from neomodel.exceptions import MultipleNodesReturned

# import application.artifacts.artifact.Artifact.DoesNotExist as ArtifactDoesNotExist
from application.teams.placeholder_drives.contains_rel import ContainsRel
from .sync import DriveUploader


class Drive(StructuredNode, DefaultPropertyMixin, DefaultHelperMixin):  # pylint:disable=abstract-method
    """The class that manages Drives"""

    drive_id = StringProperty(required=True)
    page_token = StringProperty()

    team = RelationshipFrom("application.models.Team", "SYNCED_TO", cardinality=cardinality.ZeroOrOne)
    owner = RelationshipFrom("application.models.User", "OWNS", cardinality=cardinality.ZeroOrOne)
    eligible_users = RelationshipFrom("application.models.User", "HAS_ACCESS", cardinality=cardinality.ZeroOrMore)
    files = RelationshipTo(
        "application.models.Artifact", "CONTAINS", model=ContainsRel, cardinality=cardinality.ZeroOrMore
    )

    def find_artifact_by(self, gdrive_file_id, force=True):
        results = self.files.match(gdrive_file_id=gdrive_file_id)
        if len(results) > 1:
            raise MultipleNodesReturned
        if len(results) is 0:
            if force:
                raise Exception("ArtifactDoesNotExist")
            else:
                return None
        return results[0]

    def sync(self):
        DriveUploader(self).upload_all_missing()

    def delete_if_necessary(self, artifact):
        try:
            DriveUploader(self).delete_file_by(artifact)
        except:
            print("Connection to google drive failed")
