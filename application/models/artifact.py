from .esmodel import ESModel
from flask import current_app

class Artifact(ESModel):
    """ Handles saving and searching """

    index = "artifact"
    members = [
        "file_url",
        "tags",
        "file_date"
    ]

    @classmethod
    def parse_params(cls, params):
        params = super().parse_params(params)
        params["file_url"] = current_app.config["FILE_SERVER"] + "/" + params["file_url"]
        print(params)
        return params

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
