"""Define Custom Errors and Exceptions"""
from flask import current_app, abort


class NotFound(Exception):
    """Throw when the Resource could not be found"""


class NotInitialized(Exception):
    """Throw when update is called on unitinitialized Resource"""


class NotSaved(Exception):
    """Throw when Resource could not be saved"""


def check_es_connection(func):
    """Decorator that tests if elasticsearch is definded"""

    def func_wrapper(*args, **kwargs):
        if not current_app.es:
            return abort(503, "search engine not available")
        return func(*args, **kwargs)

    return func_wrapper
