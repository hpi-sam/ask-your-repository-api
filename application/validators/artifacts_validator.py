""" Defines validators for artifact requests """

from webargs import ValidationError, fields

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


def get_args():
    return {
        "id": fields.UUID(required=True, load_from='object_id', location='view_args'),
    }


def search_args():
    """Defines and validates params for index"""
    return {
        "search": fields.String(missing=None),
        "team_id": fields.UUID(missing=None),
        "types": fields.String(load_from="type", missing="image"),
        "start_date": fields.DateTime(),
        "end_date": fields.DateTime(),
        "offset": fields.Integer(missing=0),
        "limit": fields.Integer(missing=12),
        "notify_clients": fields.Boolean(missing=False)
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
        "team_id": fields.UUID(missing=None),
        "user_tags": fields.List(fields.String(), load_from='tags')
    }


def update_args():
    """Defines and validates params for update"""
    return {
        "id": fields.UUID(required=True, load_from='object_id', location='view_args'),
        "user_tags": fields.List(fields.String(), missing=[], load_from='tags')
    }


def update_many_args():
    """Defines and validates params for update many"""
    return {
        "artifacts": fields.List(fields.Nested({
            "id": fields.UUID(required=True),
            "user_tags": fields.List(fields.String(), required=True, load_from='tags')
        }))
    }


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
