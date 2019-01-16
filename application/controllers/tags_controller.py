"""
Handles all logic of the artefacts api
"""
from webargs.flaskparser import use_args
from ..errors import NotFound
from ..error_handling.es_connection import check_es_connection
from ..models.artifact import Artifact
from ..validators import tags_validator
from .application_controller import ApplicationController

class TagsController(ApplicationController):
    """ Controller for Artifacts """

    method_decorators = [check_es_connection]

    @use_args(tags_validator.add_tags_args())
    def add_tags(self, params, object_id):
        """ Adds tags to an existing artifact """
        object_id = str(params.pop('id'))

        try:
            artifact = Artifact.find(object_id)
            existing_tags = artifact.tags or []

            new_list = existing_tags + list(set(params["tags"]) - set(existing_tags))

            artifact.update({"tags": new_list})
            return '', 204
        except NotFound:
            return {"error": "not found"}, 404

    @use_args(tags_validator.suggested_tags_args())
    def suggested_tags(self, params):
        """ Takes an array of tags and suggests tags based on that """
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
            return {"tags": self.most_frequent_tags(all_records, params['limit'])}, 200
        #raise NameError
        return {"tags": sorted_tags}, 200

    @staticmethod
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
