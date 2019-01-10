"""Defines helper methods used with artifacts"""
from flask import current_app


def build_url(file_url):
    """ Schema: fileserver/id_filename """
    return current_app.config["FILE_SERVER"] + \
        "/" + file_url
