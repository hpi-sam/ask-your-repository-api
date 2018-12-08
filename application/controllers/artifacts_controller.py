"""
Handles all logic of the artefacts api
"""
import os
import uuid
import datetime
import werkzeug
from flask import current_app, request
from flask_restful import reqparse
from application.errors import NotFound
from application.models.artifact import Artifact
from .application_controller import ApplicationController
from webargs import fields, validate, ValidationError
from webargs.flaskparser import use_args, use_kwargs, parser, abort

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


def search_params():
    """ Defines and validates search params """
    parser = reqparse.RequestParser(bundle_errors=True)
    parser.add_argument("search", default="")
    parser.add_argument("type", action="append", dest="types")
    parser.add_argument("start_date")
    parser.add_argument("end_date")
    parser.add_argument("offset", type=int, default=0)
    parser.add_argument("limit", type=int, default=12)

    return parser.parse_args()

def search_args():
    return {
        "search": fields.String(missing=""),
        "types": fields.String(load_from="type", missing="artifact"),
        "start_date": fields.DateTime(),
        "end_date": fields.DateTime(),
        "offset": fields.Integer(missing=0),
        "limit": fields.Integer(missing=12)
    }


def create_params():
    """ Defines and validates create params """
    parser = reqparse.RequestParser()
    parser.add_argument("type", default="image")
    parser.add_argument("image", dest="file", required=True,
                        type=werkzeug.datastructures.FileStorage, location='files')
    parser.add_argument("tags", action="append", default=[])
    return parser.parse_args()

def create_args():
    return {
        "type": fields.String(missing="image"),
        "file": fields.Function(
            deserialize=validate_image,
            required=True,
            location='files',
            load_from='image'),
        "tags": fields.List(fields.String())
    }

def validate_image(image):
    if not allowed_file(image.filename):
        raise ValidationError('Invalid require data: image')
    return image

def update_params():
    """ Defines and validates update params """
    parser = reqparse.RequestParser()
    parser.add_argument("file_url")
    parser.add_argument("tags", action="append", default=[])
    return parser.parse_args()

def update_args():
    return {
        "id": fields.UUID(required=True, load_from='object_id', location='view_args'),
        "tags": fields.List(fields.String(), missing=[]),
        "file_url": fields.Function(deserialize=validate_file_name)
    }

def validate_file_name(filename):
    if not allowed_file(filename):
        raise ValidationError('Errornous file_url')
    return filename

def add_tags_params():
    """ Defines and validates add tags params """
    parser = reqparse.RequestParser()
    parser.add_argument("tags", action="append", default=[])
    return parser.parse_args()


def allowed_file(filename):
    """checks if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def check_es(func):
    """ Decorator that tests if elasticsearch is definded """
    def func_wrapper(*args, **kwargs):
        if not current_app.es:
            return {"error": "search engine not available"}, 503
        return func(*args, **kwargs)

    return func_wrapper

@parser.error_handler
def handle_request_parsing_error(err, req, schema):
    """webargs error handler that uses Flask-RESTful's abort function to return
    a JSON error response to the client.
    """
    abort(422, errors=err.messages)

class ArtifactsController(ApplicationController):
    """ Controller for Artifacts """

    method_decorators = [check_es]

    def show(self, object_id):
        "Logic for getting a single artifact"

        try:
            return Artifact.find(object_id).to_json()
        except NotFound:
            return {"error": "not found"}, 404

    def index(self):
        "Logic for querying several artifacts"
        
            
        params = parser.parse(search_args(), request)
        print(params)

        #params = search_params()

        result = Artifact.search(params)

        return {"images": result}, 200

    def create(self):
        "Logic for creating an artifact"
        params = parser.parse(create_args(), request)
        print(params)

        # params = create_params()

        params["file_date"] = datetime.datetime.now().isoformat()
        uploaded_file = params["file"]
        if not allowed_file(uploaded_file.filename):
            return {"error": "file is not allowed"}, 422

        filename = str(uuid.uuid4()) + "_" + \
            werkzeug.utils.secure_filename(uploaded_file.filename)
        file_url = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        uploaded_file.save(file_url)
        params["file_url"] = filename
        artifact = Artifact(params)

        artifact.save()
        return vars(artifact), 200

    def update(self, object_id):
        "Logic for updating an artifact"
        print(request)
        params = parser.parse(update_args(), request)
        artifact_id = str(params.pop('id'))
        # params = update_params()
        try:
            artifact = Artifact.find(artifact_id)
            artifact.update(params)
            return '', 204
        except NotFound:
            return {"error": "not found"}, 404

    def delete(self, object_id):
        "Logic for deleting an artifact"

        try:
            artifact = Artifact.find(object_id)
            artifact.delete()
            return '', 204
        except NotFound:
            return {"error": "not found"}, 404

    def add_tags(self, object_id):
        """ Adds tags to an existing artifact """

        params = add_tags_params()
        try:
            artifact = Artifact.find(object_id)
            existing_tags = getattr(artifact, "tags")
            new_list = existing_tags + list(set(params["tags"]) - set(existing_tags))

            artifact.update({"tags": new_list})
            return '', 204
        except NotFound:
            return {"error": "not found"}, 404
