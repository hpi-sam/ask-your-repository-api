from .drive_view import DrivesView


def add_routes(blueprint):
    blueprint.add_url_rule('/<team_id>/drives', view_func=DrivesView.as_view('drivesview'))
    return blueprint
