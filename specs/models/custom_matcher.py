from expects.matchers import Matcher
from uuid import UUID
from py2neo import NodeMatcher, Relationship, RelationshipMatcher

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


class have_relationship(Matcher):

    def __init__(self, node1, rel, node2):
        self.node1 = node1
        self.rel = rel
        self.node2 = node2

    def _match(self, graph):
        query = f"MATCH (node1{self.node1.labels} {{id:'{self.node1['id']}'}})-[relation:{self.rel}]->(node2{self.node2.labels}{{id:'{self.node2['id']}'}}) RETURN relation"
        relationship = graph.run(query).evaluate()
        if relationship is not None:
            return True, 'Relationship found'
        else:
            return False, 'Relationship not found'
