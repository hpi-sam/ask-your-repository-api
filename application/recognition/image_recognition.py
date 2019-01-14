"""Image Recognition"""
from eventlet import spawn_n
from requests import post
from application.schemas.artifact_schema import ArtifactSchema
from flask import current_app


class ImageRecognizer():
    @staticmethod
    def auto_add_tags(artifact):
        """Called by classes """
        spawn_n(ImageRecognizer._work_asynchronously, artifact)

    @staticmethod
    def _call_google_api(url):
        """Does API call to could vision api"""
        api_url = current_app.config.get('CLOUD_VISION_API_URL')
        api_key = current_app.config.get('CLOUD_VISION_API_KEY')
        r = post(url=api_url,
                 data={
                     "requests": [
                         {
                             "features": [
                                 {"type": "LABEL_DETECTION"},
                                 {"type": "TEXT_DETECTION"}
                             ],
                             "image": {
                                 "source": {"imageUri": url}
                             }
                         }
                     ]
                 },
                 params={'key': api_key})
        return r.json()

    @staticmethod
    def _work_asynchronously(artifact):
        """Private method called asynchronously for image recognition."""
        image_url = ArtifactSchema.build_url(artifact.file_url)
        res = ImageRecognizer._call_google_api(image_url)
        new_tags = ImageRecognizer._extract_tags(res)
        existing_tags = artifact.tags or []
        tags = existing_tags + new_tags
        artifact.update({"tags": tags})

    @staticmethod
    def _extract_tags(response):
        """Private method to extract new tags from Google api response."""
        tags = []
        labels = response['responses'][0]['labelAnnotations']
        for label in labels:
            tags.append(label['description'])
        texts = response['responses'][0]['textAnnotations']
        for text in texts:
            tags.append(text['description'])
        return tags
