import face_recognition
from flask import current_app

from application.artifacts.faces.face import Face
from application.artifacts.faces.person import Person


class FaceRecognition:
    @classmethod
    def run(cls):
        unrecognized_faces = Face.nodes.has(person=False)
        verified_faces = Face.nodes.filter(is_verified=True)

        verified_face_encodings = []
        upload_dir = current_app.config["UPLOAD_FOLDER"]

        for verified_face in verified_faces:
            file_path = f"{upload_dir}/{verified_face.file_url}"
            image = face_recognition.load_image_file(file_path)
            encodings = face_recognition.face_encodings(image)

            if (len(encodings) == 0): continue

            verified_face_encodings.append(encodings[0])

        for unrecognized_face in unrecognized_faces:
            file_path = f"{upload_dir}/{unrecognized_face.file_url}"
            image = face_recognition.load_image_file(file_path)
            encodings = face_recognition.face_encodings(image)

            if (len(encodings) == 0): continue

            results = face_recognition.compare_faces(verified_face_encodings, encodings[0])

            for index, result in enumerate(results):
                if result:
                    person = verified_faces[index].person.single()
                    person.faces.connect(unrecognized_face)
                    person.artifacts.connect(unrecognized_face.artifact.single())
