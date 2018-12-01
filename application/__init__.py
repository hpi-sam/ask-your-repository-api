"""
Core function of the flask app.
All system wide variables and functions should be declared here.
All logic and features should go in this module
"""
import os
from flask import Flask, Blueprint
from elasticsearch import Elasticsearch
from flask_restful import Api

def create_app(config_filename=None):
    """
    Creates the app using the specifig config file of that environment.
    See instance directory.
    """
    app = Flask(__name__, instance_relative_config=True)
    api_bp = Blueprint('api', __name__)
    api = Api(api_bp)
    add_resources(api)
    app.config.from_pyfile(config_filename)
    app.es = (Elasticsearch(app.config['ELASTICSEARCH_URL'])
              if app.config['ELASTICSEARCH_URL'] else None)
    app.register_blueprint(api_bp)
    return app

def add_resources(api):
    from application.home.home_controller import HomeResources
    from application.artifacts.artifacts_controller import ArtifactsResource, ArtifactResource
    api.add_resource(HomeResources, '/')
    api.add_resource(ArtifactsResource, '/artifacts')
    api.add_resource(ArtifactResource, '/artifacts/<artifact_id>')
