""" Tests for artifacts """

import sys
from flask import current_app
from mamba import description, before, after, it
from expects import expect, equal
from doublex_expects import *
from doublex import Mock, Stub

sys.path.insert(0, 'specs')

#pylint: disable=wrong-import-position
from specs.spec_helpers import Context
#pylint: enable=wrong-import-position

with description('/artifacts') as self:

    with before.each:
        self.context = Context()
        current_app.es = Stub()

    with after.each:
        self.context.delete()

    with description('GET'):
        with before.each:
            with Mock() as elastic_mock:
                 elastic_mock.get(doc_type='_all', id='1', index='artifact').returns({"_source":{"class_diagram.png":""}})
            current_app.es = elastic_mock
            self.response = self.context.client().get("/artifacts/1")

        with it('returns a 200 status code'):
            expect(self.response.status_code).to(equal(200))

    with description('POST'):
        with before.each:
            with Mock() as elastic_mock:
                 elastic_mock.get(doc_type='_all', id='1', index='artifact').returns({"_source":{"class_diagram.png":""}})
            current_app.es = elastic_mock
            self.response = self.context.client().get("/artifacts/1")

        with it('returns a 200 status code'):
            expect(self.response.status_code).to(equal(200))
