"""Image Recognition"""
from eventlet import spawn_n
from requests import post
from application.helpers.artifact_helper import build_url
from flask import current_app


def recognize_image(file_url, object_id):
    """Called by classes """
    spawn_n(_call_google_api, file_url, object_id)


def _call_google_api(file_url, artifact):
    """Private method called asynchronously for image recognition."""
    image_url = build_url(file_url)
    api_url = current_app.config.CLOUD_VISION_API_URL
    api_key = current_app.config.CLOUD_VISION_API_KEY

    r = post(url=api_url,
             data={
                 "requests": [
                     {
                         "features": [
                             {"type": "LABEL_DETECTION"},
                             {"type": "TEXT_DETECTION"}
                         ],
                         "image": {
                             "source": {"imageUri": image_url}
                         }
                     }
                 ]
             },
             params={'key': api_key})
    if r.status_code is not 200:
        return
    body = r.json()
    labels = body.responses[0].labelAnnotations
    new_tags = []
    for label in labels:
        new_tags.append(label.description)
    texts = body.responses[0].textAnnotations
    for text in texts:
        new_tags.append(text.description)
    existing_tags = artifact.tags or []
    tags = existing_tags + new_tags
    artifact.update({"tags": tags})
