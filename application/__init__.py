"""
Core function of the flask app.
All system wide variables and functions should be declared here.
All logic and features should go in this module
"""
import os
from flask import Flask, Blueprint
from elasticsearch import Elasticsearch
from flask_restful import Api
from flask_cors import CORS
from flask_socketio import SocketIO
from py2neo import Database
from .routes import create_routes
from .extensions import socketio

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
    app.graph = (Database(app.config['NEO4J_URL']).default_graph
                 if app.config['NEO4J_URL'] else None)
    app.register_blueprint(api_bp)
	register_extensions(app)

    if not os.path.isdir(app.config['UPLOAD_FOLDER']):
        os.mkdir(app.config['UPLOAD_FOLDER'])

    return app

def register_extensions(app):
    """ Registers all flask extensions """
    socketio.init_app(app)
