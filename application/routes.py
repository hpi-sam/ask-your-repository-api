""" Defines all Routes """
from .base import add_resource, add_method
# from flask_restful import reqparse, abort, Api, Resource


def create_routes(api):
    """ Creates Routes. Called in __init__ """

    from application.controllers.home_controller import HomeController
    from application.controllers.artifacts_controller import ArtifactsController
    from application.controllers.tags_controller import TagsController

    add_method(api, '/', "show_status", HomeController, method="get")
    add_resource(api, '/images', ArtifactsController)
    add_method(api, '/images/<object_id>/tags', "add_tags",
               TagsController, method="post")
    add_method(api, "/images/<object_id>/suggestions", "suggested_tags",
               TagsController, method="get")
