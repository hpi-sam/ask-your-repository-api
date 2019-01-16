"""Rails like wrapper for routes"""
from ..base import ActionController


class ApplicationController(ActionController):
    """
    All Controllers must inherit from Application Controller.
    Handles Routing to the right methods.
    Inspired by rails controllers.


    def show(self, *args, **kwargs):
        Method for getting a single resource

    def index(self, *args, **kwargs):
        Method for getting a single resource

    def create(self, *args, **kwargs):
        Method for getting a single resource

    def update(self, *args, **kwargs):
        Method for getting a single resource

    def delete(self, *args, **kwargs):
        Method for getting a single resource
    """
