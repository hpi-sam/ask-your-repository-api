""" Defines all Routes """
from .base import add_resource, add_method


# from flask_restful import reqparse, abort, Api, Resource


def create_routes(api):
    """ Creates Routes. Called in __init__ """

    from .controllers.home_controller import HomeController
    from .controllers.artifacts_controller import ArtifactsController
    from .controllers.tags_controller import TagsController
    from .controllers.presentations_controller import PresentationsController
    from .controllers.teams_controller import TeamsController

    add_method(api, '/', "show_status", HomeController, method="get")
    add_resource(api, '/images', ArtifactsController)
    add_method(api, '/images', "update_many", ArtifactsController, method="patch")
    add_resource(api, '/teams', TeamsController)
    add_resource(api, '/presentations', PresentationsController, only="create")
    add_method(api, '/images/<object_id>/tags', "add_tags",
               TagsController, method="post")
    add_method(api, "/tags/suggested", "suggested_tags",
               TagsController, method="get")
