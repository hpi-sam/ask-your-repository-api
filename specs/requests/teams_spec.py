import sys
from io import BytesIO
from flask import current_app
from mamba import shared_context, included_context, description, context, before, after, it
from expects import expect, equal, have_key
from hamcrest import matches_regexp
from elasticsearch.exceptions import NotFoundError
from doublex import Mock, Stub, ANY_ARG
from specs.spec_helpers import Context
from application.models.team import Team
from specs.factories.elasticsearch import es_search_response, es_get_response
from specs.factories.uuid_fixture import get_uuid
from specs.factories.date_fixture import get_date, date_regex

sys.path.insert(0, 'specs')


with description('/teams') as self:

    with before.each:
        self.context = Context()
        current_app.es = Stub()

    with description('GET'):
        with before.each:
            Team.create(name='Blue')
            Team.create(name='Red')
            self.response = self.context.client().get("/teams")

        with it('responds with all teams'):
            print(self.response.json)


