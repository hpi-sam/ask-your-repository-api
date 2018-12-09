""" Defines mocked elasticsearch responses """
from specs.factories.uuid_fixture import get_uuid

def es_get_response():
    """ Creates an example body for a get request """
    return {"_id": f"{get_uuid(0)}",
            "_type": "image",
            "_source": {"tags": ["class_diagram", ""],
                        "created_at": "today",
                        "updated_at": "today",
                        "file_url": "test.png",
                        "file_date": "today"}}

def es_get_untagged_image_response():
    """ Creates an example body for a get request """
    return {"_id": "1",
            "_type": "image",
            "_source": {"tags": [],
                        "created_at": "today",
                        "updated_at": "today",
                        "file_url": "test.png",
                        "file_date": "today"}}

def es_search_response():
    """ Creates an example body for a search request """
    return {"hits": {"total": 12, "max_score": 1.0, "hits": [
        {"_index": "artifact",
         "_type": "image",
         "_id": f"{get_uuid(0)}",
         "_score": 1.0,
         "_source": {
             "created_at": "today",
             "updated_at": "today",
             "file_url": "class_diagram.png",
             "tags": ["uml", "class diagram"],
             "file_date": "today"}},
        {"_index": "artifact",
         "_type": "image",
         "_id": f"{get_uuid(0)}",

         "_score": 0.5,
         "_source": {
             "created_at": "yesterday",
             "updated_at": "yesterday",
             "file_url": "use_case_diagram.png",
             "tags": ["uml", "use case diagram"],
             "file_date": "yesterday"}}]}}

def es_search_all_response():
    """ Creates an example body for a search request """
    return {"hits": {"total": 12, "max_score": 1.0, "hits": [
        {"_index": "artifact",
         "_type": "image",
         "_id": f"{get_uuid(0)}",
         "_score": 1.0,
         "_source": {
             "created_at": "today",
             "updated_at": "today",
             "file_url": "class_diagram.png",
             "tags": ["uml", "class diagram"],
             "file_date": "today"}},
        {"_index": "artifact",
         "_type": "image",
         "_id": f"{get_uuid(0)}",
         "_score": 0.5,
         "_source": {
             "created_at": "yesterday",
             "updated_at": "yesterday",
             "file_url": "use_case_diagram.png",
             "tags": ["uml", "use case diagram", "tomato", "tree"],
             "file_date": "yesterday"}},
        {"_index": "artifact",
         "_type": "image",
         "_id": f"{get_uuid(0)}",
         "_score": 0.5,
         "_source": {
             "created_at": "yesterday",
             "updated_at": "yesterday",
             "file_url": "use_case_diagram.png",
             "tags": ["uml", "use case diagram", "tree", "tomato"],
             "file_date": "yesterday"}},
        {"_index": "artifact",
         "_type": "image",
         "_id": f"{get_uuid(0)}",
         "_score": 0.5,
         "_source": {
             "created_at": "yesterday",
             "updated_at": "yesterday",
             "file_url": "use_case_diagram.png",
             "tags": ["uml", "use case diagram", "tomato", "tree"],
             "file_date": "yesterday"}},
        {"_index": "artifact",
         "_type": "image",
         "_id": f"{get_uuid(0)}",
         "_score": 0.5,
         "_source": {
             "created_at": "yesterday",
             "updated_at": "yesterday",
             "file_url": "use_case_diagram.png",
             "tags": ["uml", "use case diagram", "tomato"],
             "file_date": "yesterday"}},
             {"_index": "artifact",
         "_type": "image",
         "_id": f"{get_uuid(0)}",
         "_score": 0.5,
         "_source": {
             "created_at": "yesterday",
             "updated_at": "yesterday",
             "file_url": "use_case_diagram.png",
             "tags": ["uml", "use case diagram"],
             "file_date": "yesterday"}},
        {"_index": "artifact",
         "_type": "image",
         "_id": f"{get_uuid(0)}",
         "_score": 0.5,
         "_source": {
             "created_at": "yesterday",
             "updated_at": "yesterday",
             "file_url": "use_case_diagram.png",
             "tags": ["class diagram", "tomato", "apple"],
             "file_date": "yesterday"}},
        {"_index": "artifact",
         "_type": "image",
         "_id": f"{get_uuid(0)}",
         "_score": 0.5,
         "_source": {
             "created_at": "yesterday",
             "updated_at": "yesterday",
             "file_url": "use_case_diagram.png",
             "tags": ["apple", "class diagram"],
             "file_date": "yesterday"}},
        {"_index": "artifact",
         "_type": "image",
         "_id": f"{get_uuid(0)}",
         "_score": 0.5,
         "_source": {
             "created_at": "yesterday",
             "updated_at": "yesterday",
             "file_url": "use_case_diagram.png",
             "tags": ["tomato", "class diagram", "apple"],
             "file_date": "yesterday"}},
        {"_index": "artifact",
         "_type": "image",
         "_id": f"{get_uuid(0)}",
         "_score": 0.5,
         "_source": {
             "created_at": "yesterday",
             "updated_at": "yesterday",
             "file_url": "use_case_diagram.png",
             "tags": ["tomato", "class diagram"],
             "file_date": "yesterday"}},
        {"_index": "artifact",
         "_type": "image",
         "_id": f"{get_uuid(0)}",
         "_score": 0.5,
         "_source": {
             "created_at": "yesterday",
             "updated_at": "yesterday",
             "file_url": "use_case_diagram.png",
             "tags": ["apple", "class diagram"],
             "file_date": "yesterday"}},
        {"_index": "artifact",
         "_type": "image",
         "_id": f"{get_uuid(0)}",
         "_score": 0.5,
         "_source": {
             "created_at": "yesterday",
             "updated_at": "yesterday",
             "file_url": "use_case_diagram.png",
             "tags": ["uml"],
             "file_date": "yesterday"}}]}}
