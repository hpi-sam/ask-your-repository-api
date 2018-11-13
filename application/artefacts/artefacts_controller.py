from flask import current_app
import uuid
import datetime

def index(params):
    if not current_app.es:
        return {"error":"search engine not available"}
    
    date_range = {
        "gte": params["date_range"]["start_date"],
        "lte": params["date_range"]["end_date"]
    } if "date_range" in params else {}

    result = current_app.es.search(
        index="artefact",
        doc_type=params["type"],
        body={
            "sort" : [
                "_score",
                { "created_at" : { "order": "desc"}}
            ],
            "query": {
                "bool": {
                    "filter": {
                        "range": {
                            "created_at": date_range
                        }
                    },        
                    "should": {
                        "match": {"tags": params["search"]}
                    } 
                }   
            }
        })
    return result["hits"]["hits"]

def create(params):
    if not current_app.es:
        return {"error":"search engine not available"}
    date = datetime.datetime.now().isoformat()
    return current_app.es.index(
        index="artefact", 
        doc_type=params["type"], 
        id=params["id"], 
        body={
            "text": params["tags"], 
            "file_url": params["file_url"],
            "created_at": date
        })