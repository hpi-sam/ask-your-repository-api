""" Defines mocked elasticsearch responses """

def es_get_response():
    """ Creates an example body for a get request """
    return {"_id": "dc5434f4-1239-41b2-87a1-c8df49f94ab2",
            "_type": "image",
            "_source": {"tags": ["class_diagram", ""],
                        "created_at": "today",
                        "updated_at": "today",
                        "file_url": "test.png",
                        "file_date": "today"}}

def es_search_response():
    """ Creates an example body for a search request """
    return {"hits": {"total": 12, "max_score": 1.0, "hits": [
        {"_index": "artifact",
         "_type": "image",
         "_id": 'dc5434f4-1239-41b2-87a1-c8df49f94ab2',
         "_score": 1.0,
         "_source": {
             "created_at": "today",
             "updated_at": "today",
             "file_url": "class_diagram.png",
             "tags": ["uml", "class diagram"],
             "file_date": "today"}},
        {"_index": "artifact",
         "_type": "image",
         "_id": 'dc5434f4-1239-41b2-87a1-c8df49f94ab2',
         "_score": 0.5,
         "_source": {
             "created_at": "yesterday",
             "updated_at": "yesterday",
             "file_url": "use_case_diagram.png",
             "tags": ["uml", "use case diagram"],
             "file_date": "yesterday"}}]}}
