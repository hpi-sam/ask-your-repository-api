"""Abstracting Sync of Neo and Elastic"""
import datetime
import os
import uuid

import werkzeug
from PIL import Image
from flask import current_app

from application.artifacts.artifact_connector import ArtifactConnector
from application.artifacts.image_recognition import ImageRecognizer


class ImageResizer:
    """Saves resized versions of an image to disk"""

    widths = [320, 480, 640, 750, 1080]

    def __init__(self, file_path):
        self.image = Image.open(file_path)
        self.original_file_name = file_path.split("/")[-1]

    def save_sizes(self):
        """Saves resized image for all defined widths"""
        for width in self.widths:
            height = self._calculate_height(width)
            resized_image = self.image.resize((width, height), Image.ANTIALIAS)
            resized_image.save(self._generate_file_path(width))
            resized_image.close()

    def _generate_file_path(self, width):
        file_name = self._generate_file_name(width)
        return os.path.join(current_app.config["UPLOAD_FOLDER"], file_name)

    def _generate_file_name(self, width):
        """Generate filename for a resized image of given width"""
        [prefix, suffix] = self.original_file_name.rsplit(".", 1)
        filename = f"{prefix}_{width}w.{suffix}"
        return filename

    def _calculate_height(self, width):
        """Calculate height of resized image with given width"""
        width_ratio = width / self.image.size[0]
        height = int(self.image.size[1] * width_ratio)
        return height


class FileSaver:
    """Saves a file to disk and creates according metadata"""

    def __init__(self, file):
        self.file = file
        self.file_date = None
        self.file_name = None
        self.file_path = None

    def save(self):
        """Saves an artifact to disk."""
        self._create_metadata()
        self._save_file()

    def get_metadata(self):
        """Get Metadata as hash (file_url and file_date)"""
        return {"file_url": self.file_name, "file_date": self.file_date}

    def _create_metadata(self):
        self.file_name = self._generate_filename()
        self.file_date = datetime.datetime.now()
        self.file_path = self._file_path()

    def _save_file(self):
        self.file.save(self.file_path)
        self.file.close()

    def _file_path(self):
        return os.path.join(current_app.config["UPLOAD_FOLDER"], self.file_name)

    def _generate_filename(self):
        return str(uuid.uuid4()) + "_" + werkzeug.utils.secure_filename(self.file.filename)


class ArtifactCreator:
    """Creates an artifact by file, owner_id and team_id.
    The file is saved and resized before creating the artifact in the database.
    All optional parameters are passed to the ArtifactConnector.
    The file has to be a werkzeug.datastructures.FileStorage object."""

    def __init__(self, file, owner_id, team_id, **optional):
        self.file = file
        self.owner_id = owner_id
        self.team_id = team_id
        self.additional_params = optional

    def create_artifact(self):
        """ Starts the creation process. """
        file_metadata = self._upload_file()
        artifact = self._save_to_db(file_metadata)
        ImageRecognizer.auto_add_tags(artifact)
        return artifact

    def _save_to_db(self, file_metadata):
        artifact = ArtifactConnector().build_with(
            user_id=self.owner_id, team_id=self.team_id, **{**self.additional_params, **file_metadata}
        )
        artifact.save()
        return artifact

    def _upload_file(self):
        file_saver = FileSaver(self.file)
        file_saver.save()

        image_resizer = ImageResizer(file_saver.file_path)
        image_resizer.save_sizes()

        return file_saver.get_metadata()
