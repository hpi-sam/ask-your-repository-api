from expects.matchers import Matcher
from uuid import UUID
from py2neo import NodeMatcher

# Read this for custom matcher documentation:
# https://expects.readthedocs.io/en/stable/custom-matchers.html


class be_uuid(Matcher):

    def _match(self, id_):
        try:
            UUID(str(id_), version=4)
            return True, ['is a uuidv4']
        except ValueError:
            return False, ['is not a uuidv4']


class have_node(Matcher):

    def __init__(self, node):
        self._node = node

    def _match(self, graph):
        if NodeMatcher(graph).match(*self._node.labels, **dict(self._node)).first():
            return True, 'Node found'
        else:
            return False, 'Node not found'
