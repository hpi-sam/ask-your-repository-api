"""Some nice helper matchers"""
from uuid import UUID

from expects.matchers import Matcher


# Read this for custom matcher documentation:
# https://expects.readthedocs.io/en/stable/custom-matchers.html


class be_uuid(Matcher):  # noqa
    """Check if an ID conforms to uuid4 standards"""

    def _match(self, id_):
        try:
            UUID(str(id_), version=4)
            return True, ["is a uuidv4"]
        except ValueError:
            return False, ["is not a uuidv4"]
