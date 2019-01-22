"""
module to help with encoding the params in a requests
"""

def build_request(url, params):
    """
    Usage example: client().get('/images', {
        'search': 'hello'
    })
    """
    request = url
    if params:
        request += '?'
        key_value_list = list(params.items())
        for key, value in key_value_list[:-1]:
            request += f'{key}={value}&'
        key, value = key_value_list[-1] # pylint: disable=unbalanced-tuple-unpacking
        request += f'{key}={value}'
    return request
