from flask import Flask
from elasticsearch import Elasticsearch
import os
from os import popen
import subprocess

######################################
#### Application Factory Function ####
######################################
 
def create_app(config_filename=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile(config_filename)
    app.es = Elasticsearch(app.config['ELASTICSEARCH_URL']) if app.config['ELASTICSEARCH_URL'] else None
    register_blueprints(app)
    return app

def register_blueprints(app):
    from application.artefacts import artefacts_blueprint
    from application.home import home_blueprint
    app.register_blueprint(artefacts_blueprint)
    app.register_blueprint(home_blueprint)