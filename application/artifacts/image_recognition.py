"""Image Recognition"""
import requests
import base64
import os
import json
from eventlet import spawn_n
from flask import current_app, copy_current_request_context, has_request_context

from application.artifacts.tags.tag import Tag
from application.artifacts.artifact_connector import ArtifactConnector
from application.artifacts.artifact_schema import ArtifactSchema


class ImageRecognizer:
    """Send images to google to gather additional tags"""

    @classmethod
    def auto_add_tags(cls, artifact):
        """Adds automatically generated tags to the artifact.
        Returns nothing and will not raise exceptions or errors encountered during the process"""
        if not has_request_context(): return

        temp = copy_current_request_context(cls._work_for_artifact)
        spawn_n(temp, artifact)

    @classmethod
    def _work_for_artifact(cls, artifact):
        """Private method called asynchronously for image recognition."""
        res = cls._call_google_api(artifact)
        label_annotations, text_annotations = cls._extract_tags(res)
        cls.add_tags_artifact(artifact, label_annotations, text_annotations)

    @classmethod
    def _call_google_api(cls, artifact):
        """Does API call to could vision api and returns the response body"""
        api_url = current_app.config.get("CLOUD_VISION_API_URL")
        api_key = current_app.config.get("CLOUD_VISION_API_KEY")

        upload_dir = current_app.config["UPLOAD_FOLDER"]
        file_path = f"{upload_dir}/{artifact.file_url}"

        with open(file_path, "rb") as file:
            file_content = file.read()
            image_content = base64.b64encode(file_content).decode('utf-8')

        querystring = {"key": api_key}
        payload = json.dumps({
            "requests": [
                {
                    "features": [
                        { "type": "LABEL_DETECTION" },
                        { "type": "TEXT_DETECTION" },
                    ],
                    "image": {
                        "content": image_content,
                    },
                },
            ]
        })

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
                    label_annotations.append({
                        "tag": label["description"],
                        "score": label["score"],
                        "topicality": label["topicality"],
                    })
            if "textAnnotations" in res_one:
                texts = res_one["textAnnotations"]
                for text in texts:
                    text_annotations.append(text["description"])
        return label_annotations, text_annotations

    @classmethod
    def add_tags_artifact(cls, artifact, label_annotations, text_annotations):
        """Adds annotations to an artifact"""
        builder = ArtifactConnector.for_artifact(artifact)
        builder.update_with(override_tags=False, text_tags=text_annotations)

        for label_annotation in label_annotations:
            created_tag = Tag.find_or_create_by(name=label_annotation["tag"])
            artifact.label_tags.connect(created_tag, {
                "score": label_annotation["score"],
                "topicality": label_annotation["topicality"],
            })
