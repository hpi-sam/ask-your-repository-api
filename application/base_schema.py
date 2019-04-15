"""Defines wrapper for Routes and Resources"""

from flask import current_app
from marshmallow import Schema, post_load, post_dump


def output_decorator(decorator_function):
    """
    Decorator to define output transformation functions
    that are only called in respond_with (application.responders)
    """

    @post_dump
    def decorate(instance, data):
        if instance.decorate:
            return decorator_function(instance, data)
        return data

    return decorate


class BaseSchema(Schema):
    """Initialize Schemas with Schema(Model)"""

    def __init__(self, *args, model=None, decorate=False, create_objects=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
        self.decorate = decorate
        self.create_objects = create_objects

    @post_load
    def make_resource(self, data):
        """Builds an instance of the Model on schema.load"""
        if self.create_objects:
            return self.model(data)
        return data


@BaseSchema.error_handler
def handle_errors(schema, errors, obj):  # noqa
    """
    Logs errors that are caused when loading
    objects from the database using schema.load.
    Only happens if database is corrupted.
    """
    error_message = "The following errors occured while loading data from the database: {}".format(errors)
    current_app.logger.error(error_message)
    raise ValueError(error_message)
