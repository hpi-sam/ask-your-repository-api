""" Helpers for models """
import uuid

class DefaultHelperMixin:
    """ Default helpers for neomodels """

    @classmethod
    def all(cls):
        """ Returns all objects of this model """
        return list(cls.nodes)

    @classmethod
    def find(cls, uid, force=True):
        """ Find an object by uid """
        if not isinstance(uid, uuid.UUID):
            uid = uuid.UUID(uid)
        return cls.find_by(id_=str(uid), force=force)

    @classmethod
    def find_by(cls, force=True, **properties, ):
        """ Find an object by properties """
        if force:
            return cls.nodes.get(**properties)
        return cls.nodes.get_or_none(**properties)

    @classmethod
    def exists(cls, **properties):
        """ Check if an object exists by properties"""
        return cls.find_by(force=False, **properties) is not None

    @classmethod
    def find_or_create_by(cls, **properties):
        """ Find or creates the object by properties """
        object = cls.find_by(force=False, **properties)
        if object is None:
            object = cls(**properties).save()
        return object

    def update(self, **properties):
        """ changes the proprties and saves the object """
        for key, value in properties.items():
            setattr(self, key, value)
        self.save()
