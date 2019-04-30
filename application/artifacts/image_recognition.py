"""Image Recognition"""
import requests
from eventlet import spawn_n
from flask import copy_current_request_context, has_request_context
from flask import current_app

from application.artifacts.artifact_connector import ArtifactConnector
from application.artifacts.artifact_schema import ArtifactSchema


class ImageRecognizer:
    """Send images to google to gather additional tags"""

    @classmethod
    def auto_add_tags(cls, artifact):
        """Adds automatically generated tags to the artifact.
        Returns nothing and will not raise exceptions or errors encountered during the process"""
        if has_request_context():
            temp = copy_current_request_context(cls._work_for_artifact)
            spawn_n(temp, artifact)
        else:
            cls._work_for_artifact(artifact)

    @classmethod
    def _work_for_artifact(cls, artifact):
        """Private method called asynchronously for image recognition."""
        res = cls._call_google_api(artifact)
        current_app.logger.info("Google Response: " + str(res))
        label_annotations, text_annotations = cls._extract_tags(res)
        cls.add_tags_artifact(artifact, label_annotations, text_annotations)
        current_app.logger.info(
            "ML added the labels: " + str(label_annotations) + " Extracted text was: " + str(text_annotations)
        )

    @classmethod
    def _call_google_api(cls, artifact):
        """Does API call to could vision api and returns the response body"""
        api_url = current_app.config.get("CLOUD_VISION_API_URL")
        api_key = current_app.config.get("CLOUD_VISION_API_KEY")
        file_url = ArtifactSchema.build_url(artifact.file_url)

        querystring = {"key": api_key}
        payload = (
            '''{
     "requests": [
         {
             "features": [
                 {"type": "LABEL_DETECTION"},
                 {"type": "TEXT_DETECTION"}
             ],
             "image": {
                 "source": {"imageUri": "'''
            + file_url
            + """"}
             }
         }
     ]
 }"""
        )
        headers = {"Content-Type": "application/json"}
        response = requests.request("POST", api_url, data=payload, headers=headers, params=querystring)
        return response.json()

    @classmethod
    def _extract_tags(cls, response):
        """Returns new label and text annotations extracted from Google api response body"""
        label_annotations = []
        text_annotations = []
        if "responses" in response:
            res_one = response["responses"][0]
            if "labelAnnotations" in res_one:
                labels = res_one["labelAnnotations"]
                for label in labels:
                    label_annotations.append(label["description"])
            if "textAnnotations" in res_one:
                texts = res_one["textAnnotations"]
                for text in texts:
                    text_annotations.append(text["description"])
        return label_annotations, text_annotations

    @classmethod
    def add_tags_artifact(cls, artifact, label_annotations, text_annotations):
        """Adds annotations to an artifact"""
        builder = ArtifactConnector.for_artifact(artifact)
        builder.update_with(override_tags=False, label_tags=label_annotations, text_tags=text_annotations)
