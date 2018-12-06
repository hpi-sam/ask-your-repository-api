""" Tests for home """

from flask import current_app
from mamba import description, context, before, after, it
from expects import expect, equal, have_keys
from doublex import Mock, Stub, ANY_ARG
from specs.spec_helpers import Context

with description('/') as self:

    with before.each:
        self.context = Context()
        current_app.es = Stub()

    with after.each:
        self.context.delete()

    with context('database mocked'):
        with before.each:
            with Mock() as elastic_mock:
                elastic_mock.search(ANY_ARG).returns(
                    {"hits": {"hits": []}})

            current_app.es = elastic_mock
            self.response = self.context.client().get("/")

        with it('returns a 200 status code'):
            expect(self.response.status_code).to(equal(200))

        with it('returns database status on'):
            expect(self.response.json).to(have_keys({
                "service name": "artefact service",
                "database status": "on"}))

    with context('databse unavailable'):
        with before.each:
            current_app.es = None
            self.response = self.context.client().get("/")

        with it('returns a 200 status code'):
            expect(self.response.status_code).to(equal(200))

        with it('returns database status off'):
            expect(self.response.json).to(have_keys({
                "service name": "artefact service",
                "database status": "off"}))
