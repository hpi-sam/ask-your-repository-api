""" Defines all Routes """


def create_routes(app):
    """ Creates Routes. Called in __init__ """

    from .controllers.home_controller import HomeController
    from .controllers.artifacts_controller import ArtifactsController, ArtifactsByIDController
    from .controllers.authentications_controller import AuthenticationsController
    from .controllers.presentations_controller import PresentationsController
    from .controllers.tags_controller import TagsController
    from .controllers.teams_controller import TeamsController, TeamsByIDController
    from .controllers.users_controller import UsersController, UsersByIDController

    app.add_url_rule('/images', view_func=ArtifactsController.as_view('artifactscontroller'))
    app.add_url_rule('/images/<object_id>',
                     view_func=ArtifactsByIDController.as_view('artifactsbyidcontroller'))

    app.add_url_rule('/authentications',
                     view_func=AuthenticationsController.as_view('authentications'))
    app.add_url_rule('/presentations', view_func=PresentationsController.as_view('presentations'))
    app.add_url_rule('/images/<object_id>/tags', "add_tags",
                     TagsController().add_tags, methods=["POST", ])
    app.add_url_rule('/tags/suggested', "suggested_tags", TagsController().suggested_tags)
    app.add_url_rule('/', "show_status", HomeController().show_status)
    app.add_url_rule('/teams', view_func=TeamsController.as_view('teams'))
    app.add_url_rule('/teams/<object_id>', view_func=TeamsByIDController.as_view('team'))
    app.add_url_rule('/users', view_func=UsersController.as_view('users'))
    app.add_url_rule('/users/<object_id>', view_func=UsersByIDController.as_view('user'))
