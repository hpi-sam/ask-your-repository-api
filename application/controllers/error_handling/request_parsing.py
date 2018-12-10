from webargs.flaskparser import parser, abort

@parser.error_handler
def handle_request_parsing_error(err, req, schema): # pylint: disable=unused-argument
    """webargs error handler that uses Flask-RESTful's abort function to return
    a JSON error response to the client.
    """
    abort(422, errors=err.messages)