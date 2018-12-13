""" Defines validators for artifact requests """

from flask import request
from webargs.flaskparser import parser
from webargs import fields, ValidationError

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def validator(validator_fields):
    """ Generator to create a function that validates the request """
    def validate():
        return parser.parse(validator_fields(), request)
    return validate

@validator
def search_args():
    """Defines and validates params for index"""
    return {
        "search": fields.String(missing=None),
        "types": fields.String(load_from="type", missing="image"),
        "start_date": fields.DateTime(),
        "end_date": fields.DateTime(),
        "offset": fields.Integer(missing=0),
        "limit": fields.Integer(missing=12)
    }

@validator
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

@validator
def update_args():
    """Defines and validates params for update"""
    return {
        "id": fields.UUID(required=True, load_from='object_id', location='view_args'),
        "tags": fields.List(fields.String(), missing=[]),
        "file_url": fields.Function(deserialize=validate_file_name)
    }

@validator
def delete_args():
    """Defines and validates params for delete"""
    return {
        "id": fields.UUID(required=True, load_from='object_id', location='view_args')
    }

def validate_image(image):
    """validator for uploaded files"""
    validate_file_name(image.filename)
    return image

def validate_file_name(filename):
    """validator for uploaded file names"""
    if not allowed_file(filename):
        raise ValidationError('Errornous file_url')
    return filename

def allowed_file(filename):
    """checks if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
