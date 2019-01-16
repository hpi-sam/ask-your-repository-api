""" Define responders that can be used in controllers """

from flask import make_response

def respond_with(resource):
    """ Responds with a collection of - or single json """
    if isinstance(resource, (list,)):
        if resource:
            return (resource[0].schema(resource.__class__, decorate=True)
                    .dump(resource, many=True).data)
        return []
    return resource.schema(resource.__class__, decorate=True).dump(resource).data

def no_content():
    """ Creates an empty response with
    application/json mimetype """

    response = make_response('', 204)
    response.mimetype = 'application/json'
    return response
