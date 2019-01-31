""" Tests for presentation requestes """

import sys

from doublex import Mock, Stub
from expects import expect, equal
from flask import current_app
from mamba import description, before, after, it

from specs.factories.elasticsearch import es_find_all_response
from specs.factories.uuid_fixture import get_uuid
from specs.spec_helpers import Context

sys.path.insert(0, 'specs')

with description('/presentations') as self:
    with before.each:
        self.context = Context()
        current_app.es = Stub()

    with after.each:
        # If check to prevent tests from failing occasionally
        # Needs to be inspected!
        if hasattr(self, "context"):
            self.context.delete()

    with description('/'):
        with description('POST'):
            with before.each:
                with Mock() as elastic_mock:
                    elastic_mock.mget(index="artifact", doc_type="_all", body={
                        "ids": [get_uuid(0), get_uuid(1), get_uuid(2)]
                    }).returns(es_find_all_response())

                    current_app.es = elastic_mock

                # with Mock() as socket_mock:
                #   socket_mock.emit(ANY_ARG)
                #  socketio = socket_mock

                self.response = self.context.client().post("/presentations", json={
                    "file_ids": [get_uuid(0), get_uuid(1), get_uuid(2)]
                })

            with it('returns a 204 status code'):
                expect(self.response.status_code).to(equal(204))
