import unittest

from application import misc

def test_api_status():
    status = misc.api_status()
    assert status == True