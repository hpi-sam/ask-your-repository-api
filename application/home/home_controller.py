from flask import current_app

def index(params):
    database_status = "on" if current_app.es else "of"
    return {"service name":"artefact service", "database status": database_status}