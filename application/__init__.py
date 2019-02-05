"""
Core function of the flask app.
All system wide variables and functions should be declared here.
All logic and features should go in this module
"""

# pylint: disable=wrong-import-order, no-name-in-module

import os

from elasticsearch import Elasticsearch
from flask import Flask, Blueprint
from flask_cors import CORS
from flask_restful import Api
from neomodel import config

from .extensions import socketio
from .routes import create_routes


def create_app(config_filename=None):
    """
    Creates the app using the specific config file of that environment.
    See instance directory.
    """
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)
    api_bp = Blueprint('api', __name__)
    api = Api(api_bp)
    create_routes(api)
    app.config.from_pyfile(config_filename)
    app.es = (Elasticsearch(app.config['ELASTICSEARCH_URL'])
              if app.config['ELASTICSEARCH_URL'] else None)
    config.DATABASE_URL = app.config['NEO4J_URL']
    app.register_blueprint(api_bp)
    register_extensions(app)

    if not os.path.isdir(app.config['UPLOAD_FOLDER']):
        os.mkdir(app.config['UPLOAD_FOLDER'])

    return app


def register_extensions(app):
    """ Registers all flask extensions """
    socketio.init_app(app)
