"""Find Artifacts in Elasticsearch"""
from flask import current_app

from .artifact_search_builder import ArtifactSearchBuilder


class ElasticSearcher:  # pylint:disable=too-few-public-methods
    """use search() to find things"""

    @classmethod
    def build_artifact_searcher(cls, params):
        """Build a searcher for the artifact index"""
        date_range = {}
        if "start_date" in params:
            date_range["gte"] = params["start_date"]
        if "end_date" in params:
            date_range["lte"] = params["end_date"]

        search_builder = ArtifactSearchBuilder(search=params["search"],
                                               date_range=date_range,
                                               limit=params["limit"],
                                               offset=params["offset"],
                                               team_id=params["team_id"],
                                               synonyms=params['synonyms'])
        return cls('artifact', 'image', search_builder)

    def __init__(self, index, type, search_builder):
        self.index = index
        self.type = type
        self.search_builder = search_builder

    def search(self):
        """Finds multiple artifacts by params. """
        body = self.search_builder.build().body

        return current_app.es.search(
            # search_type is counteracting the sharding effect that messes with idf:
            # https://www.compose.com/articles/how-scoring-works-in-elasticsearch/
            search_type="dfs_query_then_fetch",
            index=self.index,
            doc_type=self.type,
            body=body)['hits']['hits']
