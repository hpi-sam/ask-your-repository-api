""" Tests for presentation requestes """

import sys

from expects import expect, equal
from mamba import description, before, after, it
from neomodel import db

from specs.factories.artifact_factory import ArtifactFactory
from specs.factories.uuid_fixture import get_uuid
from specs.spec_helpers import Context

sys.path.insert(0, 'specs')

with description('/presentations') as self:
    with before.each:
        self.context = Context()

    with after.each:
        # If check to prevent tests from failing occasionally
        # Needs to be inspected!
        if hasattr(self, "context"):
            self.context.delete()
        db.cypher_query('MATCH (a) DETACH DELETE a')

    with description('/'):
        with description('POST'):
            with before.each:
                ids = [get_uuid(0), get_uuid(1), get_uuid(2)]
                for id in ids:
                    ArtifactFactory.create_artifact(id_=id)

                # with Mock() as socket_mock:
                #   socket_mock.emit(ANY_ARG)
                #  socketio = socket_mock

                self.response = self.context.client().post("/presentations", json={
                    "file_ids": ids
                })

            with it('returns a 204 status code'):
                expect(self.response.status_code).to(equal(204))
