from flask.cli import AppGroup


debug_cli = AppGroup("debug")


@debug_cli.command("something")
def something():
    pass
    # Whatever you want to execute, put your code here and call "poetry run flask debug something".
    # It's like flask shell but loads from a file :P


def add_debug_scripts(app):
    app.cli.add_command(debug_cli)
