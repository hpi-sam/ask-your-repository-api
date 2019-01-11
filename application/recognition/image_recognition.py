"""Image Recognition"""
from eventlet import spawn_n
from requests import post
from application.helpers.artifact_helper import build_url
from flask import current_app


def recognize_image(file_url, object_id):
    """Called by classes """
    spawn_n(_work_asynchronously, file_url, object_id)


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


def _work_asynchronously(file_url, artifact):
    """Private method called asynchronously for image recognition."""
    image_url = build_url(file_url)
    res = _call_google_api(image_url)
    labels = res['responses'][0]['labelAnnotations']
    new_tags = []
    for label in labels:
        new_tags.append(label['description'])
    texts = res['responses'][0]['textAnnotations']
    for text in texts:
        new_tags.append(text['description'])
    existing_tags = artifact.tags or []
    tags = existing_tags + new_tags
    artifact.update({"tags": tags})
