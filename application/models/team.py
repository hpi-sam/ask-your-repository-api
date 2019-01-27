"""" Access to the Team model """
from py2neo.ogm import Property
from application.schemas.team_schema import TeamSchema
from .neo_model import NeoModel


class NeoTeam(NeoModel):
    """" Program representation of Team nodes in Neo4J """
    schema = TeamSchema
    __primarylabel__ = "Team"
    name = Property()

    def __init__(self, id=None, name=''):
        super().__init__(id=id)
        self.name = name
