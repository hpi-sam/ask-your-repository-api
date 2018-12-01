""" Define Custom Errors and Exceptions """

class NotFound(Exception):
    """ Throw when the Resource could not be found """

class NotInitialized(Exception):
    """ Throw when update is called on unitinitialized Resource """

class NotSaved(Exception):
    """ Throw when Resource could not be saved """
