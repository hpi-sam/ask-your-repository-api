""" Defines wrapper for Routes and Resources """

from flask_restful import Resource


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
        if create:
            methods["post"] = cls().create

        if index:
            methods["get"] = cls().index

        collection_class = type("Collection", (Resource,), methods)
        return collection_class

    @classmethod
    def member(cls, show=True, update=True, delete=True):
        """ Creates the member class with allowed methods """
        methods = {}
        if show:
            methods["get"] = cls().show

        if update:
            methods["put"] = cls().update

        if delete:
            methods["delete"] = cls().delete

        member_class = type("Member", (Resource,), methods)
        return member_class

    @classmethod
    def new_resource(cls, name, method):
        """ Creates resource class for new method """

        methods = {}
        methods[method] = getattr(cls(), name)
        new_class = type(name.capitalize(), (Resource,), methods)

        return new_class
