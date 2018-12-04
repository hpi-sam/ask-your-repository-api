""" Tests ESModel """

import sys
from flask import current_app
from mamba import description, before, after, it
from expects import expect, equal, raise_error
from application.models.esmodel import ESModel
from application.errors import NotInitialized
from doublex import Mock, Stub, ANY_ARG
from specs.spec_helpers import Context

sys.path.insert(0, 'specs')

with description('ESModel') as self:

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
            self.es_model = ESModel({"type": "image"})
            self.es_model.index = "artifact"

        with it("raises NotInitialized error if it wasn't saved before"):
            expect(lambda: self.es_model.update({})).to(raise_error(NotInitialized))

        with it("returns True if it was saved before"):
            self.es_model.save()
            expect(self.es_model.update({})).to(equal(True))
