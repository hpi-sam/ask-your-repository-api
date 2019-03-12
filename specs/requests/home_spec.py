""" Tests for home """

from doublex import Mock, Stub, ANY_ARG
from expects import expect, equal, have_keys
from flask import current_app
from mamba import description, context, before, after, it

from specs.spec_helpers import Context

with description('/') as self:
    with before.each:
        self.context = Context()
        current_app.es = Stub()

    with after.each:
        # If check to prevent tests from failing occasionally
        # Needs to be inspected!
        if hasattr(self, "context"):
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
                "service_name": "artefact service",
                "database_status": "on"}))

    with context('databse unavailable'):
        with before.each:
            current_app.es = None
            self.response = self.context.client().get("/")

        with it('returns a 200 status code'):
            expect(self.response.status_code).to(equal(200))

        with it('returns database status off'):
            expect(self.response.json).to(have_keys({
                "service_name": "artefact service",
                "database_status": "off"}))
