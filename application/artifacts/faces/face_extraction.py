import face_recognition
import os
import numpy as np
from PIL import Image

from flask import current_app
from application.artifacts.faces.face import Face

class FaceExtractor:
  def __init__(self, artifact):
      self.artifact = artifact
      self.faces = []

  def _load_image(self):
      image_file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], self.artifact.file_url)
      self.image = Image.open(image_file_path)

  def _locate_faces(self):
      self.face_locations = face_recognition.face_locations(np.array(self.image))

  def _generate_face_file_name(self, face_index):
      """Generate filename for a resized image of given width"""
      [prefix, suffix] = self.artifact.file_url.rsplit(".", 1)
      return f"{prefix}_face{face_index}.{suffix}"

  def _store_face(self, face_index, face_location):
      bounding_box = (face_location[3], face_location[0], face_location[1], face_location[2])
      file_name = self._generate_face_file_name(face_index)
      file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], file_name)

      cropped = self.image.crop(bounding_box)
      cropped.save(file_path)

      width, height = self.image.size
      self.faces.append({
          "file_url": file_name,
          "bounding_box": (
              bounding_box[0] / width,
              bounding_box[1] / height,
              bounding_box[2] / width,
              bounding_box[3] / height)
      })

  def _store_faces(self):
      for face_index, face_location in enumerate(self.face_locations):
          self._store_face(face_index, face_location)

  def _save_face_to_db(self, data):
      face = Face(**data)
      face.save()
      self.artifact.faces.connect(face)

  def _save_faces_to_db(self):
      for face in self.faces:
          self._save_face_to_db(face)

  def run(self):
      self._load_image()
      self._locate_faces()
      self._store_faces()
      self._save_faces_to_db()
