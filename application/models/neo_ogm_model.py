import uuid
from application.errors import NotFound
from flask import current_app
from py2neo.ogm import GraphObject, Property, Related, RelatedTo, RelatedFrom


class NeoOGMModel(GraphObject):
    node_label = ""
    __primarykey__ = "id"

    _id = Property('id')

    @property
    def id(self):
        return uuid.UUID(self._id)

    @id.setter
    def id(self, id):
        self._id = str(id)

    @classmethod
    def all(cls):
        return list(cls._find_all())

    @classmethod
    def find_by(cls, force=False, **properties):
        properties = cls.parse_properties(properties)
        return cls._parse_match(cls._find_object_by(**properties), force)

    @classmethod
    def _find_object_by(cls, **properties):
        return cls._find_all_by(**properties).first()

    @classmethod
    def _find_all_by(cls, **properties):
        return cls._find_all().where(**properties)

    @classmethod
    def _find_all(cls):
        return cls.match(current_app.graph)

    @classmethod
    def _parse_match(cls, match, force=False):
        return match if match else cls._not_found(force)

    @classmethod
    def parse_properties(cls, properties):
        if 'id' in properties:
            properties['id'] = str(properties['id'])
        return properties

    @classmethod
    def exists(cls, **properties):
        """ Check if a model exists by attribute """
        return bool(cls.find_by(**properties))

    @classmethod
    def create(cls, **properties):
        return cls(**properties).save()

    @classmethod
    def _not_found(cls, force=False):
        if force:
            raise NotFound()
        else:
            return None

    def update(self, **properties):
        """ Update and save attributes of a model """
        for key, value in properties.items():
            setattr(self, key, value)
        self.save()
        return self

    def delete(self):
        """ Delete the model in database """
        current_app.graph.delete(self)

    def __init__(self, id=None):
        self.id = uuid.UUID(id) if id else uuid.uuid4()

    def save(self):
        """ Save the model object to the database"""
        current_app.graph.push(self)
        return self

    def __eq__(self, other):
        return self.id == other.id
