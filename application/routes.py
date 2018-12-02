""" Defines all Routes """
from .application_helpers import add_resource, add_method


def create_routes(api):
    """ Creates Routes. Called in __init__ """

    from application.home.home_controller import HomeController
    from application.artifacts.artifacts_controller import ArtifactsController

    add_method(api, '/', "show_status", HomeController, method="get")
    add_resource(api, '/artifacts', ArtifactsController)
