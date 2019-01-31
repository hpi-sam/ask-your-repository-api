""" Tests for artifacts """

import sys

from doublex import Mock, Stub, ANY_ARG
from expects import expect, equal, have_key, have_keys
from flask import current_app
from mamba import shared_context, included_context, description, context, before, after, it

from application.models.team import NeoTeam
from specs.factories.elasticsearch import es_search_response
from specs.factories.request_generator import build_request
from specs.spec_helpers import Context

sys.path.insert(0, 'specs')

with description('/dialogflow_images') as self:
    with before.each:
        self.context = Context()
        current_app.es = Stub()

    with after.each:
        # If check to prevent tests from failing occasionally
        # Needs to be inspected!
        if hasattr(self, "context"):
            self.context.delete()

    with description('/'):
        with before.each:
            self.path = "/dialogflow_images"
            self.team = NeoTeam.create(name='test_team')
            self.params = {"team_name": self.team.name}

        with after.each:
            self.team.delete()

        with description('GET without database'):
            with before.each:
                current_app.es = None
                self.response = self.context.client().get(build_request(self.path, self.params))

            with it('returns a 503 status code'):
                expect(self.response.status_code).to(equal(503))

        with description('GET'):
            with before.each:
                with Mock() as elastic_mock:
                    elastic_mock.search(ANY_ARG).returns(es_search_response())

                    current_app.es = elastic_mock

            with shared_context('responds with error') as self:
                with before.each:
                    self.response = (self.context.client()
                                     .get(build_request(self.path, self.params)))

                with it('returns a 422 status code'):
                    expect(self.response.status_code).to(equal(422))

                with it('returns a descriptive error message'):
                    expect(self.response.json).to(have_key("errors"))
                    expect(self.response.json["errors"]).to(have_keys(*self.params.keys()))

            with context('valid request'):
                with before.each:
                    self.response = self.context.client().get(build_request(self.path, self.params))

                with it('returns a 200 status code'):
                    expect(self.response.status_code).to(equal(200))

            with context('invalid requests'):
                with description('team_name missing'):
                    with before.each:
                        self.params = {}

                    with included_context('responds with error'):
                        pass

                with description('paramter: limit | value: asdf'):
                    with before.each:
                        self.params = {'limit': 'asdf'}

                    with included_context('responds with error'):
                        pass

                with description('paramter: offset | value: asdf'):
                    with before.each:
                        self.params = {'offset': 'asdf'}

                    with included_context('responds with error'):
                        pass
