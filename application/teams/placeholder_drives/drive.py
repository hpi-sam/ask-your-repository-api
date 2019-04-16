"""Access to Drive objects in Ne4J"""
from neomodel import StructuredNode, StringProperty, RelationshipTo, cardinality, RelationshipFrom

from application.model_mixins import DefaultPropertyMixin, DefaultHelperMixin


class Drive(StructuredNode, DefaultPropertyMixin, DefaultHelperMixin):  # pylint:disable=abstract-method
    """The class that manages Drives"""

    drive_id = StringProperty(required=True)
    page_token = StringProperty()

    team = RelationshipFrom("application.models.Team", "SYNCED_TO", cardinality=cardinality.ZeroOrOne)
    owner = RelationshipFrom("application.models.User", "OWNS", cardinality=cardinality.ZeroOrOne)
    eligible_users = RelationshipFrom("application.models.User", "HAS_ACCESS", cardinality=cardinality.ZeroOrMore)
    files = RelationshipTo('DriveFile', "CONTAINS_FILE", cardinality=cardinality.ZeroOrMore)

class DriveFile(StructuredNode, DefaultPropertyMixin, DefaultHelperMixin):  # pylint:disable=abstract-method
    drive_id = StringProperty(required=True)

    folder = RelationshipFrom('Drive', "CONTAINS_FILE", cardinality=cardinality.ZeroOrOne)
    artifact = RelationshipFrom('application.models.Artifact', "HAS_DRIVE_FILE", cardinality=cardinality.ZeroOrMore)