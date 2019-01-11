""" Define error handling if elasticsearch is unavailable """

from flask import current_app


def check_es_connection(func):
    """ Decorator that tests if elasticsearch is definded """

    def func_wrapper(*args, **kwargs):
        if not current_app.es:
            return {"error": "search engine not available"}, 503
        return func(*args, **kwargs)

    return func_wrapper
