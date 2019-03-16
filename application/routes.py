""" Defines all Routes """


def create_routes(app):
    """ Creates Routes. Called in __init__ """

    from .views.home_view import HomeView
    from .views.artifacts_view import ArtifactsView, ArtifactView
    from .views.authentications_view import AuthenticationsView
    from .views.presentations_view import PresentationsView
    from .views.tags_view import TagsView
    from .views.teams_view import TeamsView, TeamView
    from .views.users_view import UsersView, UserView

    app.add_url_rule('/images', view_func=ArtifactsView.as_view('artifactscontroller'))
    app.add_url_rule('/images/<id>',
                     view_func=ArtifactView.as_view('artifactsbyidcontroller'))

    app.add_url_rule('/authentications',
                     view_func=AuthenticationsView.as_view('authentications'))
    app.add_url_rule('/presentations', view_func=PresentationsView.as_view('presentations'))
    app.add_url_rule('/images/<id>/tags', "add_tags",
                     TagsView().add_tags, methods=["POST", ])
    app.add_url_rule('/tags/suggested', "suggested_tags", TagsView().suggested_tags)
    app.add_url_rule('/', "show_status", HomeView().show_status)
    app.add_url_rule('/teams', view_func=TeamsView.as_view('teams'))
    app.add_url_rule('/teams/<id>', view_func=TeamView.as_view('team'))
    app.add_url_rule('/users', view_func=UsersView.as_view('users'))
    app.add_url_rule('/users/<id>', view_func=UserView.as_view('user'))
