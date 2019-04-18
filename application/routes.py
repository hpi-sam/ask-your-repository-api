"""Defines all Routes"""


def create_routes(app):
    """Creates Routes. Called in __init__"""

    from application.home.home_view import HomeView
    from application.artifacts.aritfact_routes import ARTIFACTS
    from application.users.users_routes import USERS
    from application.teams.teams_routes import TEAMS
    from application.authentications.authentications_routes import AUTHENTICATIONS
    from application.password_resets.password_resets_routes import PASSWORD_RESETS
    from application.presentations.presentations_routes import PRESENTATIONS
    from application.invites.invites_routes import INVITES
    from application.artifacts.tags.tags_view import TagsView

    app.register_blueprint(ARTIFACTS, url_prefix="/images")
    app.register_blueprint(USERS, url_prefix="/users")
    app.register_blueprint(TEAMS, url_prefix="/teams")
    app.register_blueprint(AUTHENTICATIONS, url_prefix="/authentications")
    app.register_blueprint(PRESENTATIONS, url_prefix="/presentations")
    app.register_blueprint(INVITES, url_prefix="/invites")
    app.register_blueprint(PASSWORD_RESETS, url_prefix="/password_resets")

    app.add_url_rule("/tags/suggested", "suggested_tags", TagsView().suggested_tags)
    app.add_url_rule("/", "show_status", HomeView().show_status)
