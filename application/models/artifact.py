""" Elastic search artifact model wraps api into crud methods"""
from application.schemas.artifact_schema import ArtifactSchema
from .esmodel import ESModel

class Artifact(ESModel):
    """ Handles saving and searching """

    index = "artifact"
    schema = ArtifactSchema

    def __init__(self, params):
        """ Initializes the artifact """
        super().__init__(params)
        self.file_url = params.get("file_url", None)
        self.tags = params.get("tags", [])
        self.file_date = params.get("file_date", None)
        if "score" in params:
            self.score = params["score"]

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
        if search:
            search_query = {"match": {"tags": search}}
        else:
            search_query = {"match_all": {}}

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
                    "should": search_query
                }
            }
        }
        return body
