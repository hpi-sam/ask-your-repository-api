"""
Handles all logic of the artefacts api
"""
from flask import request
from webargs import fields
from webargs.flaskparser import parser
from application.errors import NotFound
import application.error_handling.request_parsing # pylint: disable=W0611
from application.error_handling.es_connection import check_es_connection
from application.models.artifact import Artifact
from .application_controller import ApplicationController

def add_tags_args():
    """Defines and validates params for add_tags"""
    return {
        "id": fields.UUID(required=True, load_from='object_id', location='view_args'),
        "tags": fields.List(fields.String(), missing=[]),
    }

def suggested_tags_args():
    """ Defines and validates suggested tags params """
    return {
        "tags": fields.List(fields.String(), missing=[]),
        "min_support": fields.Number(missing=0.25, validate=lambda val: val <= 1),
        "limit": fields.Integer(missing=3)
    }

def most_frequent_tags(records, limit):
    """returns the most frequently used tags in a given list of artifacts"""
    tag_frequencies = {}
    for record in records:
        for tag in record["tags"]:
            if tag in tag_frequencies.keys():
                tag_frequencies[tag] += 1
            else:
                tag_frequencies[tag] = 1
    sorted_frequencies = sorted(tag_frequencies.items(),
                                key=lambda kv: kv[1], reverse=True)[:limit]
    sorted_tags = [frequency[0] for frequency in sorted_frequencies]
    return sorted_tags

class TagsController(ApplicationController):
    """ Controller for Artifacts """

    method_decorators = [check_es_connection]

    def add_tags(self, object_id): # pylint: disable=unused-argument
        """ Adds tags to an existing artifact """
        params = parser.parse(add_tags_args(), request)
        artifact_id = str(params.pop('id'))

        try:
            artifact = Artifact.find(artifact_id)
            existing_tags = artifact.tags or []

            new_list = existing_tags + list(set(params["tags"]) - set(existing_tags))

            artifact.update({"tags": new_list})
            return '', 204
        except NotFound:
            return {"error": "not found"}, 404

    def suggested_tags(self):    # pylint: disable=unused-argument
        """ Takes an array of tags and suggests tags based on that """
        params = parser.parse(suggested_tags_args(), request)
        current_tags = params['tags']

        current_tags = [tag for tag in current_tags if tag != ""]

        # all of this will be refactored in favor of a proper frequent
        # itemset mining algorithm, probably charm
        all_records = Artifact.all(create_objects=False) or []
        tag_frequencies = {}
        current_tags_frequency = 0

        for record in all_records:
            if (set(current_tags).intersection(set(record["tags"]))
                    and set(record["tags"]).difference(set(current_tags))):
                current_tags_frequency += 1
                for tag in set(record["tags"]).difference(set(current_tags)):
                    if tag in tag_frequencies.keys():
                        tag_frequencies[tag] += 1
                    else:
                        tag_frequencies[tag] = 1

        min_support_frequencies = {key:value for (key, value) in tag_frequencies.items()
                                   if value/current_tags_frequency >= params['min_support']}
        sorted_frequencies = sorted(min_support_frequencies.items(),
                                    key=lambda kv: kv[1], reverse=True)[:params['limit']]
        sorted_tags = [frequency[0] for frequency in sorted_frequencies]

        if not sorted_tags:
            #raise Exception
            return {"tags": most_frequent_tags(all_records, params['limit'])}, 200
        #raise NameError
        return {"tags": sorted_tags}, 200
