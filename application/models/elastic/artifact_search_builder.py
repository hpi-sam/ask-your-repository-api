""" Encapsulates how to search for artifacts """


class ArtifactSearchBuilder:  # pylint:disable=too-few-public-methods
    """ Builds elasticsearch search request bodies """

    def __init__(self, team_id=None, offset=0,  # pylint:disable=too-many-arguments
                 limit=10, search="", date_range=None):
        self.team_id = team_id
        self.offset = offset
        self.limit = limit
        self.search = search
        self.date_range = date_range
        self.body = {}

    def build(self):
        """ build the search body in attribute .body """
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
        bool = dict()
        bool["filter"] = self._filter()
        bool["should"] = self._tags_query()
        return {"bool": bool}

    def _tags_query(self):
        if self.search == "":
            return {"match_all": {}}
        return {"match": {"tags": self.search}}

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
