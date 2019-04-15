"""Encapsulates how to search for artifacts"""


class ArtifactSearchBuilder:  # pylint:disable=too-few-public-methods
    """Builds elasticsearch search request bodies"""

    SEARCH_CONFIG = {"text_prio": 1, "label_prio": 2, "user_prio": 5, "synonyms_multiplier": 0.3}

    def __init__(
        self,
        team_id=None,
        offset=0,
        limit=10,  # pylint:disable=too-many-arguments
        search="",
        synonyms="",
        date_range=None,
    ):
        self.team_id = team_id
        self.offset = offset
        self.limit = limit
        self.search = search
        self.date_range = date_range
        self.synonyms = synonyms
        self.body = {}

    def build(self):
        """build the search body in attribute .body"""
        self._add_limit_offset()
        self.body["sort"] = self._sort()
        self.body["query"] = self._query()
        return self

    def _add_limit_offset(self):
        self.body["from"] = self.offset
        self.body["size"] = self.limit

    def _sort(self):
        return ["_score", {"created_at": {"order": "desc"}}]

    def _query(self):
        bool = {"filter": self._filter(), "should": self._tags_query()}
        return {"bool": bool}

    def _tags_query(self):
        if self.search == "":
            return {"match_all": {}}
        tags_query = [
            self._tags_multi_match(self.search),
            self._tags_multi_match(self.synonyms, boost=self.SEARCH_CONFIG["synonyms_multiplier"]),
        ]

        return tags_query

    def _tags_multi_match(self, search, boost=1.0):
        return {
            "multi_match": {
                "query": search,
                "fields": [
                    f"user_tags^{self.SEARCH_CONFIG['user_prio']}",
                    f"label_tags^{self.SEARCH_CONFIG['label_prio']}",
                    f"text_tags^{self.SEARCH_CONFIG['text_prio']}",
                ],
                "boost": boost,
            }
        }

    def _filter(self):
        filter = []
        if self.team_id is not None:
            filter.append(self._team_filter())
        if self.date_range is not None:
            filter.append(self._date_filter())
        return filter

    def _team_filter(self):
        return {"term": {"team_id.keyword": str(self.team_id)}}

    def _date_filter(self):
        return {"range": {"created_at": self.date_range}}
