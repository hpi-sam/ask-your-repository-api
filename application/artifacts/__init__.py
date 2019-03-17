"""Provides Artifact functionality and routes"""
from flask import Blueprint

from .artifacts_view import ArtifactView, ArtifactsView
from .tags.tags_view import TagsView

ARTIFACTS = Blueprint('artifacts', __name__)
ARTIFACTS.add_url_rule('', view_func=ArtifactsView.as_view('artifactsview'))
ARTIFACTS.add_url_rule('/<id>', view_func=ArtifactView.as_view('artifactview'))

ARTIFACTS.add_url_rule('/<id>/tags', "add_tags", TagsView().add_tags, methods=["POST", ])
