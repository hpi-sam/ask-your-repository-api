""" Defines all Routes """
def create_routes(api):
    """ Creates Routes. Called in __init__ """

    from application.home.home_controller import HomeResources
    from application.artifacts.artifacts_controller import ArtifactsResource, ArtifactResource

    api.add_resource(HomeResources, '/')
    api.add_resource(ArtifactsResource, '/artifacts')
    api.add_resource(ArtifactResource, '/artifacts/<artifact_id>')