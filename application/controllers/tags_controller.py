"""
Handles all logic of the artefacts api
"""
from webargs.flaskparser import use_args

from application.models.elastic.elastic_artifact import ElasticArtifact
from .application_controller import ApplicationController
from ..error_handling.es_connection import check_es_connection
from ..models import Artifact, Team
from ..models.artifact_builder import ArtifactBuilder
from ..validators import tags_validator
from ..tagging import tag_suggestions

class TagsController(ApplicationController):
    """ Controller for Artifacts """

    method_decorators = [check_es_connection]

    @use_args(tags_validator.add_tags_args())
    def add_tags(self, params, object_id):
        """ Adds tags to an existing artifact """
        object_id = str(params.pop('id'))

        try:
            artifact = Artifact.find_by(id_=object_id)
            builder = ArtifactBuilder.for_artifact(artifact)
            existing_tags = artifact.tags or []

            new_list = existing_tags + list(set(params["tags"]) - set(existing_tags))

            builder.update_with(tags=new_list)
            return '', 204
        except Artifact.DoesNotExist:
            return {"error": "not found"}, 404

    @use_args(tags_validator.suggested_tags_args())
    def suggested_tags(self, params):
        """ Takes an array of tags and suggests tags based on that """
        current_tags = params['tags']
        team = Team.find(params['team_id'])
        current_tags = [tag for tag in current_tags if tag != ""]
        return tag_suggestions.find_tags(team, params['limit'], current_tags)


