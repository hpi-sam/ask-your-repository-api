""" Default Properties for neomodels """
import datetime
from uuid import uuid4

from neomodel import DateTimeProperty, StringProperty


class DefaultPropertyMixin:
    """ Adds id_, created_at and updated_at"""
    id_ = StringProperty(unique_index=True, default=uuid4)
    created_at = DateTimeProperty(default_now=True)
    updated_at = DateTimeProperty(default_now=True)

    def pre_save(self):
        """ update timestamps before save """
        self.updated_at = datetime.datetime.now()
        if self.does_not_exist():
            # enables checking if both are equal
            # to check if manipulated since creation
            self.created_at = self.updated_at

    def does_not_exist(self):
        """ Check if self is already saved """
        return not hasattr(self, 'id')  # id is only populated if the node was saved once
