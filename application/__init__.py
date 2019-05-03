"""
Core function of the flask app.
All system wide variables and functions should be declared here.
All logic and features should go in this module
"""

# pylint: disable=wrong-import-order, no-name-in-module

import os

from elasticsearch import Elasticsearch
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from neomodel import config, install_all_labels
from .debug_scripts import add_debug_scripts

from .background import add_background_jobs
from .extensions import socketio, bcrypt, mail
from .routes import create_routes


async def print_something():
    print("something")


def create_app(config_filename=None):
    """
    Creates the app using the specific config file of that environment.
    See instance directory.
    """
    app = Flask(__name__, instance_relative_config=True)
    CORS(app, supports_credentials=True)
    create_routes(app)
    app.config.from_pyfile(config_filename)
    app.es = Elasticsearch(app.config["ELASTICSEARCH_URL"]) if app.config["ELASTICSEARCH_URL"] else None
    config.DATABASE_URL = app.config["NEO4J_URL"]
    install_all_labels()
    JWTManager(app)
    register_extensions(app)
    register_error_handlers(app)
    add_background_jobs(app)
    add_debug_scripts(app)

    if not os.path.isdir(app.config["UPLOAD_FOLDER"]):
        os.mkdir(app.config["UPLOAD_FOLDER"])

    return app


def register_error_handlers(app):
    """Return validation errors as json as suggested here:
        https://webargs.readthedocs.io/en/latest/framework_support.html"""

    @app.errorhandler(422)
    @app.errorhandler(400)
    def handle_validation_error(err):  # pylint:disable=unused-variable
        if not hasattr(err, "data"):
            return jsonify({"error": err.description}), err.code
        headers = err.data.get("headers", None)
        messages = err.data.get("messages", ["Invalid request."])
        if headers:
            return jsonify({"errors": messages}), err.code, headers
        return jsonify({"errors": messages}), err.code

    @app.errorhandler(404)
    @app.errorhandler(409)
    @app.errorhandler(502)
    @app.errorhandler(503)
    def handle_not_found_error(err):  # pylint:disable=unused-variable
        return jsonify({"error": err.description}), err.code


def register_extensions(app):
    """Registers all flask extensions"""
    socketio.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
