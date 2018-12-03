""" Defines all Routes """
from .base import add_resource, add_method
# from flask_restful import reqparse, abort, Api, Resource


def create_routes(api):
    """ Creates Routes. Called in __init__ """

    from application.controllers.home_controller import HomeController
    from application.controllers.artifacts_controller import ArtifactsController

    # api.add_resource(ArtifactsController, '/artifacts')
    # api.add_resource(controller.new_resource(name, method), url)
    add_method(api, '/', "show_status", HomeController, method="get")
    # add_resource(api, '/artifacts', ArtifactsController)
    add_resource(api, '/images', ArtifactsController)
    add_method(api, '/images/<object_id>/tags', "add_tags",
               ArtifactsController, method="post")
