"""This module provides easy access to all models and
thereby simplifies importing across packages"""
from .artifacts.artifact import Artifact  # noqa
from .teams.team import Team  # noqa
from .users.user import User  # noqa
from .users.oauth_providers.oauth_provider import OAuthProvider #noqa
from .artifacts.tags.tag import Tag  # noqa
