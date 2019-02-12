"""Image Recognition"""
import requests
from eventlet import spawn_n
from flask import copy_current_request_context
from flask import current_app

from application.schemas.artifact_schema import ArtifactSchema
from application.models.artifact_builder import ArtifactBuilder


class ImageRecognizer:
    @classmethod
    def auto_add_tags(cls, artifact):
        """Called by classes """
        temp = copy_current_request_context(cls._work_asynchronously)
        spawn_n(temp, artifact)

    @classmethod
    def _work_asynchronously(cls, artifact):
        """Private method called asynchronously for image recognition."""
        res = cls._call_google_api(artifact)
        current_app.logger.info('Google Response: ' + str(res))
        new_tags = cls._extract_tags(res)
        cls.add_tags_artifact(artifact, new_tags)
        current_app.logger.info('ML added the Tags: ' + str(new_tags))

    @classmethod
    def _call_google_api(cls, artifact):
        """Does API call to could vision api"""
        api_url = current_app.config.get('CLOUD_VISION_API_URL')
        api_key = current_app.config.get('CLOUD_VISION_API_KEY')
        file_url = ArtifactSchema.build_url(artifact.file_url)

        querystring = {"key": api_key}
        payload = '''{
     "requests": [
         {
             "features": [
                 {"type": "LABEL_DETECTION"},
                 {"type": "TEXT_DETECTION"}
             ],
             "image": {
                 "source": {"imageUri": "''' + file_url + '''"}
             }
         }
     ]
 }'''
        headers = {
            'Content-Type': "application/json"
        }
        response = requests.request("POST", api_url, data=payload, headers=headers, params=querystring)
        return response.json()

    @classmethod
    def _extract_tags(cls, response):
        """Private method to extract new tags from Google api response."""
        tags = []
        if 'responses' in response:
            res_one = response['responses'][0]
            if 'labelAnnotations' in res_one:
                labels = res_one['labelAnnotations']
                for label in labels:
                    tags.append(label['description'])
            if 'textAnnotations' in res_one:
                texts = res_one['textAnnotations']
                for text in texts:
                    tags.append(text['description'])
        return tags

    @classmethod
    def add_tags_artifact(cls, artifact, new_tags):
        existing_tags = artifact.tags_list or []
        tags = existing_tags + new_tags
        builder = ArtifactBuilder.for_artifact(artifact)
        builder.update_with(tags=tags)
