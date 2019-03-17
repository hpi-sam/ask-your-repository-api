""" Find suggested tags """
from neomodel import db


def find_tags(team, limit, tags=None):
    """ find tags in a given team
    :param team: instance of Team model, only tags used in that team will be returned
    :param limit: how many tags to fetch
    :param tags: refines the search to favor related tags
    :return: list of tag names eg. ['cat', 'blue', 'sky']
    """
    sorted_tags = tags_by_team_and_tags(team, limit, tags) if tags else tags_by_team(team, limit)
    return sorted_tags


def tags_by_team(team, limit, excluded_tags=None):
    """ Find tags by a given team with excluded tags """
    query = _collect_artifacts_query() + _collect_tags_query()
    result, meta = team.cypher(query, {'limit': limit, 'tags': excluded_tags or []})  # pylint:disable=unused-variable
    tags = [sorted_tag[0] for sorted_tag in result]
    return tags


def _collect_artifacts_query():
    return (
        'MATCH (team) WHERE id(team)={self} '
        'MATCH (team)-[:UPLOADED]->(artifact) '
        'WITH collect(artifact) AS artifacts, count(artifact) AS max_count '
    )


def tags_by_team_and_tags(team, limit, tags):
    """ Find tags... """
    query = _collect_artifacts_with_tags_query() + _collect_tags_query()
    tag_dictionary = {}
    for _ in range(1, len(tags) + 1):
        results, meta = db.cypher_query(query, {'tags': tags, 'match_count': 1,  # pylint:disable=unused-variable
                                                'limit': limit, 'team_id': team.id})
        _add_to_dictionary(results, tag_dictionary)

    sorted_results = sorted(tag_dictionary.items(),
                            key=lambda collection: collection[1], reverse=True)[:limit]

    sorted_tags = [sorted_tag[0] for sorted_tag in sorted_results]
    # If there aren't enough related tags for the given tag(s) we fill it up with not related_tags
    if len(sorted_tags) < limit:
        additional_tags = tags_by_team(team, limit - len(sorted_tags), excluded_tags=(tags + sorted_tags))
        # additional_tags are always weighted less then related_tags
        sorted_tags += additional_tags

    return sorted_tags


def _collect_artifacts_with_tags_query():
    return (
        'MATCH (team) WHERE id(team)={team_id} '
        'MATCH (team)-[:UPLOADED]->(artifact:Artifact), (tag:Tag) '
        'WHERE tag.name IN {tags} AND (size((artifact)-[:TAGGED_WITH]->(tag)) >= {match_count}) '
        'WITH collect(artifact) AS artifacts, count(artifact) AS max_count '
    )


def _collect_tags_query():
    return (
        'UNWIND artifacts AS artifact '
        'MATCH (artifact)-[:TAGGED_WITH]->(tag) '
        'WHERE NOT tag.name IN {tags} '
        'WITH tag.name AS tag_name, (toFloat(count(artifact))/max_count) AS p '
        'WITH tag_name, p, (1.0 - p) AS p_neg '
        'RETURN tag_name, ((-p * log(p) / log(2)) - (p_neg * log(p_neg) / log(2))) AS entropy '
        'ORDER BY entropy DESC '
        'LIMIT {limit}'
    )


def _add_to_dictionary(results, dictionary):
    for item in results:
        if item[1] > dictionary.get(item[0], 0.0):
            dictionary[item[0]] = item[1]
