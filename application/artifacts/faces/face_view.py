"""
Handles all logic of the faces api
"""
from flask import abort
from flask_apispec import MethodResource, use_kwargs, marshal_with
from flask_jwt_extended import jwt_required

from application.responders import no_content
from application.artifacts.faces import face_validator
from application.artifacts.faces.face import Face
from application.artifacts.faces.person import Person

class FaceView(MethodResource):
    """Controller for Faces"""

    @jwt_required
    @use_kwargs(face_validator.verify_args())
    @marshal_with(None, 204)
    def verify(self, **params):
        """Logic for verifying a face and connecting it's person"""
        try:
            face = Face.find_by(id_=params["id"])
            face.update(is_verified=True)

            try:
                person = Person.find_by(name=params["name"])
            except Person.DoesNotExist:
                person = Person(name=params["name"])
                person.save()

            person.faces.connect(face)
            person.artifacts.connect(face.artifact.single())

            return no_content()
        except Face.DoesNotExist:
            return abort(404, "face not found")
