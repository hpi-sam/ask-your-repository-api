""" Custom Parser to validate socketio requests with webargs """

from webargs.core import Parser, get_value, dict2schema

try:
    from collections.abc import Mapping
except ImportError:
    from collections import Mapping


class SocketioParser(Parser):
    """ Only parses requests that are json / dictionaries """
    DEFAULT_LOCATIONS = ["json"]

    def parse_json(self, params, name, field):
        """ Parses a single element of the socketio request json """
        return get_value(params, name, field)

    # pylint: disable=too-many-arguments
    def use_args(
            self,
            argmap,
            locations=None,
            as_kwargs=False,
            validate=None,
            error_status_code=None,
            error_headers=None):
        """ Creates a decorator funtion for socketio on-methods """
        locations = locations or self.locations
        # Optimization: If argmap is passed as a dictionary, we only need
        # to generate a Schema once
        if isinstance(argmap, Mapping):
            argmap = dict2schema(argmap)()

        def decorator(func):

            def socket_wrapper(data, *args, **kwargs):
                # The first argument is either `self` or `request`
                parsed_args = self.parse(
                    argmap,
                    req=data,
                    locations=locations,
                    validate=validate,
                    error_status_code=error_status_code,
                    error_headers=error_headers,
                )
                if as_kwargs:
                    kwargs.update(parsed_args)
                    return func(*args, **kwargs)
                return func(parsed_args, *args, **kwargs)

            return socket_wrapper

        return decorator
    # pylint: enable=too-many-arguments


# pylint: disable=invalid-name
parser = SocketioParser()
use_args = parser.use_args
use_kwargs = parser.use_kwargs
# pylint: enable=invalid-name
