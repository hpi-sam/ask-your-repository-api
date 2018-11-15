"""
Core function of the flask app.
All system wide variables and functions should be declared here.
All logic and features should go in this module
"""
import os
from flask import Flask
from elasticsearch import Elasticsearch


def create_app(config_filename=None):
    """
    Creates the app using the specifig config file of that environment.
    See instance directory.
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile(config_filename)
    app.es = (Elasticsearch(app.config['ELASTICSEARCH_URL'])
              if app.config['ELASTICSEARCH_URL'] else None)
    register_blueprints(app)
    return app


def register_blueprints(app):
    """
    Register all new blueprints here.
    Blueprints are components of the app that belong together e.g. artefacts
    """
    from application.artefacts import artefact_blueprint
    from application.home import home_blueprint
    app.register_blueprint(artefact_blueprint)
    app.register_blueprint(home_blueprint)
