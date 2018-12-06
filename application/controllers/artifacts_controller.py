"""
Handles all logic of the artefacts api
"""
import os
import uuid
import datetime
import werkzeug
from flask import current_app, request
from webargs import fields, ValidationError
from webargs.flaskparser import parser, abort
from application.errors import NotFound
from application.models.artifact import Artifact
from .application_controller import ApplicationController

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def search_args():
    """Defines and validates params for index"""
    return {
        "search": fields.String(missing=""),
        "types": fields.String(load_from="type", missing="artifact"),
        "start_date": fields.DateTime(),
        "end_date": fields.DateTime(),
        "offset": fields.Integer(missing=0),
        "limit": fields.Integer(missing=12)
    }

def create_args():
    """Defines and validates params for create"""
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
    """validator for uploaded files"""
    validate_file_name(image.filename)
    return image

def update_args():
    """Defines and validates params for update"""
    return {
        "id": fields.UUID(required=True, load_from='object_id', location='view_args'),
        "tags": fields.List(fields.String(), missing=[]),
        "file_url": fields.Function(deserialize=validate_file_name)
    }

def validate_file_name(filename):
    """validator for uploaded file names"""
    if not allowed_file(filename):
        raise ValidationError('Errornous file_url')
    return filename

def delete_args():
    """Defines and validates params for delete"""
    return {
        "id": fields.UUID(required=True, load_from='object_id', location='view_args')
    }

def add_tags_args():
    """Defines and validates params for add_tags"""
    return {
        "id": fields.UUID(required=True, load_from='object_id', location='view_args'),
        "tags": fields.List(fields.String(), missing=[]),
    }

def suggested_tags_args():
    """ Defines and validates suggested tags params """
    return {
        "tags": fields.List(fields.String(), missing=[]),
    }

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
def handle_request_parsing_error(err, req, schema): # pylint: disable=unused-argument
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

        result = Artifact.search(params)

        return {"images": result}, 200

    def create(self):
        "Logic for creating an artifact"
        params = parser.parse(create_args(), request)

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

    def update(self, object_id): # pylint: disable=unused-argument
        "Logic for updating an artifact"
        params = parser.parse(update_args(), request)
        artifact_id = str(params.pop('id'))
        try:
            artifact = Artifact.find(artifact_id)
            artifact.update(params)
            return '', 204
        except NotFound:
            return {"error": "not found"}, 404

    def delete(self, object_id): # pylint: disable=unused-argument
        "Logic for deleting an artifact"

        params = parser.parse(delete_args(), request)
        artifact_id = str(params.pop('id'))

        try:
            artifact = Artifact.find(artifact_id)
            artifact.delete()
            return '', 204
        except NotFound:
            return {"error": "not found"}, 404

    def add_tags(self, object_id): # pylint: disable=unused-argument
        """ Adds tags to an existing artifact """
        params = parser.parse(add_tags_args(), request)
        artifact_id = str(params.pop('id'))

        try:
            artifact = Artifact.find(artifact_id)
            existing_tags = artifact.tags

            new_list = existing_tags + list(set(params["tags"]) - set(existing_tags))

            artifact.update({"tags": new_list})
            return '', 204
        except NotFound:
            return {"error": "not found"}, 404

    def suggested_tags(self, object_id):
        """ Takes an array of tags and suggests tags based on that """
        params = parser.parse(suggested_tags_args(), request)

        all_records = Artifact.all()
        return all_records, 200
