""" Tests ESModel """

import sys
from flask import current_app
from mamba import description, before, after, it
from expects import expect, equal, raise_error
from doublex import Mock, Stub, ANY_ARG
from application.models.artifact import Artifact
from application.errors import NotInitialized
from specs.spec_helpers import Context
from specs.factories.elasticsearch import es_tags_equals_none_response
from specs.factories.uuid_fixture import get_uuid

sys.path.insert(0, 'specs')

with description('Artifact') as self:

    with before.each:
        self.context = Context()
        current_app.es = Stub()

    with after.each:
        self.context.delete()

    with description('update'):
        with before.each:
            with Mock() as elastic_mock:
                elastic_mock.update(ANY_ARG)
                elastic_mock.index(ANY_ARG)

            current_app.es = elastic_mock
            self.artifact = Artifact({"type": "image"})

        with it("raises NotInitialized error if it wasn't saved before"):
            expect(lambda: self.artifact.update({})).to(raise_error(NotInitialized))

        with it("returns True if it was saved before"):
            self.artifact.save()
            expect(self.artifact.update({})).to(equal(True))