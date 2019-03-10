""" Find Artifacts in Elasticsearch """
from flask import current_app


class ElasticSearcher:  # pylint:disable=too-few-public-methods
    """ use search() to find things """

    def __init__(self, index, type):
        self.index = index
        self.type = type

    def search(self, params):
        """ Finds multiple artifacts by params.  """
        date_range = {}
        if "start_date" in params:
            date_range["gte"] = params["start_date"]
        if "end_date" in params:
            date_range["lte"] = params["end_date"]

        body = self._search_body_helper(params["search"], date_range,
                                        params["limit"], params["offset"], params['team_id'])

        result = current_app.es.search(
            # search_type is counteracting the sharding effect that messes with idf:
            # https://www.compose.com/articles/how-scoring-works-in-elasticsearch/
            search_type="dfs_query_then_fetch",
            index=self.index,
            doc_type=self.type,
            body=body)['hits']

        return result['hits']

    def _search_body_helper(
            self,
            search,
            daterange,
            limit=10,
            offset=0,
            team_id=None
    ):  # pylint: disable=too-many-arguments
        """ Defines a common body for search function """
        if search:
            search_query = {"match": {"tags": search}}
        else:
            search_query = {"match_all": {}}

        team_filter = {"team_id": str(team_id)}

        body = {
            "from": offset, "size": limit,
            "sort": [
                "_score",
                {"created_at": {"order": "desc"}}
            ],
            "query": {
                "bool": {
                    "filter": [
                        {"range": {
                            "created_at": daterange
                        }},
                        {"term": team_filter}
                    ],
                    "should": search_query
                }
            }
        }
        return body
