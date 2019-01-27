""" Tests ESModel """

import sys
from flask import current_app
from mamba import description, before, after, it
from expects import expect, equal, raise_error, have_key, contain, have_len, be_above
from hamcrest import has_length, greater_than, contains, has_key, anything
from doublex import Mock, Stub, ANY_ARG
from application.models.elastic_artifact import ElasticArtifact
from application.errors import NotInitialized
from specs.spec_helpers import Context

sys.path.insert(0, 'specs')

with description('Artifact') as self:

    with before.each:
        self.context = Context()
        current_app.es = Stub()

    with after.each:
        if hasattr(self, "context"):
            self.context.delete()

    with description('update'):
        with before.each:
            with Mock() as elastic_mock:
                elastic_mock.index(body=anything(), doc_type=anything(), id=anything(), index='artifact')
                elastic_mock.update(body=anything(), doc_type=anything(), id=anything(), index='artifact')

            self.artifact = ElasticArtifact({"type": "image"})
            current_app.es = elastic_mock

        with it("raises NotInitialized error if it wasn't saved before"):
            expect(lambda: self.artifact.update({})).to(raise_error(NotInitialized))

        with it("returns True if it was saved before"):
            self.artifact.save()
            expect(self.artifact.update({})).to(equal(True))