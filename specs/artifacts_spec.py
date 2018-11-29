from flask import current_app
from mamba import description, before, after, it
from expects import expect, equal

import sys
sys.path.insert(0, 'specs')

from specs.spec_helpers import Context
from specs.mock_elasticsearch import ElasticMock


with description('artifacts show') as self:
    with before.each:
        self.context = Context()
        current_app.es = ElasticMock()
        current_app.es.mock(function_name="get",
                            return_value={"_source":{"class_diagram.png":""}})

    with after.each:
        self.context.delete()

    with it('returns a 200 status code'):
        response = self.context.client().get("/artifacts/1")

        expect(response.status_code).to(equal(200))
