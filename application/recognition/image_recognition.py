"""Image Recognition"""
from eventlet import spawn_n
from application.helpers.artifact_helper import build_url


def recognize_image(file_url):
    """Called by classes """
    spawn_n(_placeholder, file_url)


def _placeholder(file_url):
    """Private method called asynchronously for image recognition."""
    return
