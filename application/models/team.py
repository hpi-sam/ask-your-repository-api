"""" Access to the Team model """
import uuid
from flask import current_app
from py2neo import Node
from application.errors import NotFound
from application.schemas.team_schema import TeamSchema


class Team:
    """" Program representation of Team nodes in Neo4J """
    schema = TeamSchema

    @classmethod
    def all(cls):
        """ Returns all existing Team objects"""
        results = current_app.graph.run("MATCH (x:Team) RETURN x")
        return list(map(
            lambda result: Team(result['x']['name'], id_=result['x']['id']),
            results
        ))

    @classmethod
    def find_by(cls, force=False, id_='', name=''):
        """" Find a team by attribute """
        team_node = cls._find_team_node(id_=id_, name=name)
        if team_node:
            return Team(team_node['name'], id_=team_node['id'])
        return cls._not_found(force)

    @classmethod
    def exists(cls, id_='', name=''):
        """ Check if a team exists by attribute """
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
        """ Create a team object and save it in the database """
        new_team = Team(name)
        return new_team.save()

    def update(self, name=None):
        """ Change an attribute and save it in the database """
        if name:
            self.name = name
        self.save()

    def save(self):
        """ Save the team object to the database"""
        if Team.exists(id_=self.id_):
            self._update_node()
        else:
            self._create_node()
        return self

    def _update_node(self):
        current_app.graph.run(
            f"MATCH (x:Team {{ id: '{self.id_}' }}) SET x.name='{self.name}'")

    def _create_node(self):
        # note that ID is passed as id not id_ here
        # so in the database the field is still called id not id_
        # python has its own internal member id()
        # which we don't want to override so we use id_ throughout the program
        team_node = Node("Team", name=self.name, id=str(self.id_))
        current_app.graph.create(team_node)

    def __init__(self, name, id_=None):
        self.id_ = uuid.UUID(id_) if id_ else uuid.uuid4()
        self.name = name

    def delete(self):
        """ Delete this team object from the database if it is saved """
        if Team.exists(name=self.name):
            self._delete_node()
        return self

    def _delete_node(self):
        current_app.graph.run(f"MATCH (x:Team) WHERE x.id = '{self.id_}' DELETE x")
