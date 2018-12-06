""" Elastic search artifact model wraps api into crud methods"""
from flask import current_app
from .esmodel import ESModel

def build_url(url):
    """ Schema: fileserver/id_filename """
    return current_app.config["FILE_SERVER"] + \
            "/" + url

class Artifact(ESModel):
    """ Handles saving and searching """

    index = "artifact"
    members = [
        "file_url",
        "tags",
        "file_date"
    ]

    @classmethod
    def parse_search_params(cls, params):
        """ Parse array of dictionaries returned by elasticsearch """
        result = []
        for hit in params["hits"]["hits"]:
            resource = cls.parse_params(hit)
            resource["url"] = resource.pop("file_url")
            resource["score"] = hit["_score"]
            result.append(resource)
        return result

    @classmethod
    def search(cls, params):
        """ Finds multiple artifacts by params.  """
        date_range = {}
        if "start_date" in params:
            date_range["gte"] = params["start_date"]
        if "end_date" in params:
            date_range["lte"] = params["end_date"]

        body = cls.search_body_helper(params["search"], date_range,
                                      params["limit"], params["offset"])

        return super(Artifact, cls).search(
            {"types": params["types"], "search_body": body})

    @classmethod
    def search_body_helper(cls, search, daterange, limit=10, offset=0):
        """ Defines a common body for search function """

        body = {
            "from": offset, "size": limit,
            "sort": [
                "_score",
                {"created_at": {"order": "desc"}}
            ],
            "query": {
                "bool": {
                    "filter": {
                        "range": {
                            "created_at": daterange
                        }
                    },
                    "should": {
                        "match": {"tags": search}
                    }
                }
            }
        }
        return body

    def to_json(self):
        """ Parses the object to a dictionary """
        result = vars(self).copy()
        result["url"] = build_url(result.pop("file_url"))
        return result
