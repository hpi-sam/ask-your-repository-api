""" Defines wrapper for Routes and Resources """

from flask import current_app
from flask_restful import Resource
from marshmallow import Schema, post_load, post_dump
from webargs.flaskparser import parser, abort


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
    """ Initialize Schemas with Schema(Model) """

    def __init__(self, model, *args, decorate=False, create_objects=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
        self.decorate = decorate
        self.create_objects = create_objects

    @post_load
    def make_resource(self, data):
        """ Builds an instance of the Model on schema.load """
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
    error_message = ("The following errors occured while loading data from the database: {}"
                     .format(errors))
    current_app.logger.error(error_message)
    raise ValueError(error_message)


@parser.error_handler
def handle_request_parsing_error(err, req, schema, status_code, headers):  # pylint: disable=unused-argument
    """webargs error handler that uses Flask-RESTful's abort function to return
    a JSON error response to the client.
    """
    abort(422, errors=err.messages)


def add_resource(api, url, controller, only=None):
    """
    Adds a restful resource, that is defined in the specified controller.
    Adds: #show, #index, #create, #update, #delete as default.
    Modify methods in Controller that inherits from ApplicationController.
    """
    api.add_resource(controller.collection(
        index=(not only or "index" in only),
        create=(not only or "create" in only)), url)
    api.add_resource(controller.member(
        show=(not only or "show" in only),
        update=(not only or "update" in only),
        delete=(not only or "delete" in only)), url + "/<object_id>")


def add_method(api, url, name, controller, method="get"):
    """
    Adds a single method to a controller.
    Controller and url do not have to be related, but it is recommended.
    """
    api.add_resource(controller.new_resource(name, method), url)


class ActionController:
    """
    All Controllers must inherit from Application Controller.
    Handles Routing to the right methods.
    Inspired by rails controllers.
    """

    method_decorators = []
    """ Defines decorators that get called for all actions """

    member_decorators = []
    """ Defines decorators that get called for member actions (show, update, delete)"""

    collection_decorators = []
    """ Defines decorators that get called for collection actions (index, create)"""

    def show(self, *args, **kwargs):
        """ Method for getting a single resource """

    def index(self, *args, **kwargs):
        """ Method for getting a single resource """

    def create(self, *args, **kwargs):
        """ Method for getting a single resource """

    def update(self, *args, **kwargs):
        """ Method for getting a single resource """

    def delete(self, *args, **kwargs):
        """ Method for getting a single resource """

    @classmethod
    def collection(cls, index=True, create=True):
        """ Creates the Collection class with allowed methods """
        methods = {}

        # adds the list of collection_decorators to the list of
        # all method decorators (preserves order)

        decorators = cls.method_decorators + \
                     list(set(cls.collection_decorators) - set(cls.method_decorators))
        methods["method_decorators"] = decorators

        if create:
            methods["post"] = cls().create

        if index:
            methods["get"] = cls().index

        collection_class = type(cls.__name__ + "Collection", (Resource,), methods)
        return collection_class

    @classmethod
    def member(cls, show=True, update=True, delete=True):
        """ Creates the member class with allowed methods """
        methods = {}

        # adds the list of member_decorators to the list of all method decorators (preserves order)
        decorators = cls.method_decorators + \
                     list(set(cls.member_decorators) - set(cls.method_decorators))
        methods["method_decorators"] = decorators

        if show:
            methods["get"] = cls().show

        if update:
            methods["patch"] = cls().update
            methods["put"] = cls().update

        if delete:
            methods["delete"] = cls().delete

        member_class = type(cls.__name__ + "Member", (Resource,), methods)
        return member_class

    @classmethod
    def new_resource(cls, name, method):
        """ Creates resource class for new method """

        methods = {}
        methods["method_decorators"] = cls.method_decorators
        methods[method] = getattr(cls(), name)
        new_class = type(cls.__name__ + name.capitalize(), (Resource,), methods)

        return new_class
