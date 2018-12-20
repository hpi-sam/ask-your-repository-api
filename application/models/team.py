"""" Access to the Team model """
import uuid
from flask import current_app
from py2neo import Node
from application.errors import NotFound


class Team:
    """" Program representation of Team nodes in Neo4J """

    @classmethod
    def all(cls):
        results = current_app.graph.run("MATCH (x:Team) RETURN x")
        return list(map(
            lambda result: Team(result['x']['name'], id_=result['x']['id']),
            results
        ))

    @classmethod
    def find_by(cls, force=False, id_='', name=''):
        team_node = cls._find_team_node(id_=id_, name=name)
        if team_node:
            return Team(team_node['name'], id_=team_node['id'])
        return cls._not_found(force)

    @classmethod
    def exists(cls, id_='', name=''):
        return bool(cls._find_team_node(id_=id_, name=name))

    @classmethod
    def _not_found(cls, force=False):
        if force:
            raise NotFound()
        else:
            return None

    @classmethod
    def _find_team_node(cls, id_='', name=''):
        query = f"MATCH (x:Team) WHERE x.name = '{name}' OR x.id = '{id_}' RETURN x"
        return current_app.graph.run(query).evaluate()

    @classmethod
    def create(cls, name):
        new_team = Team(name)
        return new_team.save()

    def update(self, name=None):
        if name:
            self.name = name
        self.save()

    def save(self):
        self._update_node() if Team.exists(name=self.name) else self._create_node()
        return self

    def _update_node(self):
        current_app.graph.run(
            f"MATCH (x:Team {{ id: '{self.id_}' }}) SET x.name='{self.name}'")

    def _create_node(self):
        team_node = Node("Team", name=self.name, id_=str(self.id_))
        current_app.graph.create(team_node)

    def __init__(self, name, id_=None):
        self.id_ = id_ if id_ else uuid.uuid4()
        self.name = name
