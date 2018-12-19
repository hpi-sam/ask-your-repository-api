from application.errors import NotFound, NotInitialized
from flask import current_app
from py2neo import Graph, Node
import uuid


class Team:

    @classmethod
    def all(cls):
        results = current_app.graph.run("MATCH (x:Team) RETURN x")
        teams = []
        for result in results:
            team = Team(result['x']['name'])
            team.id = result['x']['id']
            teams.append(team)
        return teams

    @classmethod
    def find_by(cls, force=False, id='', name=''):
        team_node = current_app.graph.run(
            f"MATCH (x:Team) WHERE x.name = '{name}' OR x.id = '{id}' RETURN x").evaluate()
        if team_node:
            team = Team(team_node['name'])
            team.id = team_node['id']
            return team
        else:
            if force:
                raise NotFound()
            else:
                return None

    @classmethod
    def exists(cls, id='', name=''):
        try:
            cls.find_by(id=id, name=name, force=True)
            return True
        except NotFound:
            return False

    @classmethod
    def create(cls, name):
        new_team = Team(name)
        new_team.save()
        return new_team

    def update(self, name=None):
        if name:
            self.name = name
        self.save()

    def save(self):
        if Team.exists(name=self.name):
            current_app.graph.run(
                f"MATCH (x:Team {{ id: '{self.id}' }}) SET x.name='{self.name}'")
        else:
            team_node = Node("Team", name=self.name, id=str(self.id))
            current_app.graph.create(team_node)
        return self

    def __init__(self, name):
        self.id = uuid.uuid4()
        self.name = name
