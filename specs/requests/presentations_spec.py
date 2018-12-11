""" Tests for presentation requestes """

import sys
from flask import current_app
from mamba import description, before, after, it
from expects import expect, equal
from doublex import Mock, Stub, ANY_ARG
from specs.spec_helpers import Context
from specs.factories.elasticsearch import es_find_all_response

sys.path.insert(0, 'specs')


with description('/presentations') as self:

    with before.each:
        self.context = Context()
        current_app.es = Stub()

    with after.each:
        self.context.delete()

    with description('/'):
        with description('POST'):
            with before.each:
                with Mock() as elastic_mock:
                    elastic_mock.mget(index="artifact", doc_type="_all", body={
                        "ids": ["1", "2", "3"]
                    }).returns(es_find_all_response())

                    current_app.es = elastic_mock

                with Mock() as socket_mock:
                    socket_mock.emit(ANY_ARG)
                    current_app.socketio = socket_mock

                self.response = self.context.client().post("/presentations", data={
                    "file_ids": ["1", "2", "3"]
                })

            with it('returns a 204 status code'):
                expect(self.response.status_code).to(equal(204))
