"""" Access to the Team model """
from application.schemas.team_schema import TeamSchema
from .neo_ogm_model import NeoOGMModel
from py2neo.ogm import Property


class Team(NeoOGMModel):
    """" Program representation of Team nodes in Neo4J """
    schema = TeamSchema
    __primarylabel__ = "Team"
    name = Property()

    def __init__(self, id=None, name=''):
        super().__init__(id=id)
        self.name = name
