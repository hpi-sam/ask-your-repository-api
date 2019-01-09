""" Tests ESModel """

import sys
from mamba import description, before, after, it
from expects import expect, equal, raise_error
from application.models.artifact import Artifact
from application.errors import NotInitialized
from specs.spec_helpers import Context

sys.path.insert(0, 'specs')

with description('Artifact') as self:

    with before.each:
        self.context = Context()

    with after.each:
        for artifact in Artifact.all():
            artifact.delete()

    with description('update'):
        with before.each:
            self.artifact = Artifact({"type": "image"})

        with it("raises NotInitialized error if it wasn't saved before"):
            expect(lambda: self.artifact.update({})).to(raise_error(NotInitialized))

        with it("returns True if it was saved before"):
            self.artifact.save()
            expect(self.artifact.update({})).to(equal(True))
