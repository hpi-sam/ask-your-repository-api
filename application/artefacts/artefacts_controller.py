from flask import current_app
import uuid

def index(params):
    if not current_app.es:
        return {"error":"search engine not available"}
    return current_app.es.search(index="artefact", doc_type=params["type"], body={"query": {"match":{"text": params["search"]}}})

def create(params):
    if not current_app.es:
        return {"error":"search engine not available"}
    id = uuid.uuid4()
    return current_app.es.index(index="artefact", doc_type=params["type"], id=id, body={"text": params["tags"], "file_url": params["file_url"]})