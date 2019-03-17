"""Defines all Routes"""


def create_routes(app):
    """Creates Routes. Called in __init__"""

    from application.home.home_view import HomeView
    from application.artifacts import ARTIFACTS
    from application.users import USERS
    from application.teams import TEAMS
    from application.authentications import AUTHENTICATIONS
    from application.presentations import PRESENTATIONS
    from application.artifacts.tags.tags_view import TagsView

    app.register_blueprint(ARTIFACTS, url_prefix='/images')
    app.register_blueprint(USERS, url_prefix='/users')
    app.register_blueprint(TEAMS, url_prefix='/teams')
    app.register_blueprint(AUTHENTICATIONS, url_prefix='/authentications')
    app.register_blueprint(PRESENTATIONS, url_prefix='/presentations')

    app.add_url_rule('/tags/suggested', "suggested_tags", TagsView().suggested_tags)
    app.add_url_rule('/', "show_status", HomeView().show_status)
