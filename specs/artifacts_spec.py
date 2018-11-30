from flask import current_app
from mamba import description, before, after, it
from expects import expect, equal
from doublex_expects import *
from doublex import Mock

import sys
sys.path.insert(0, 'specs')

from specs.spec_helpers import Context
from specs.mock_elasticsearch import ElasticMock


with description('/artifacts') as self:

    with before.each: 
        self.context = Context()
        current_app.es = ElasticMock()

    with after.each:
            self.context.delete()

    with description('GET'):
        with before.each:
            current_app.es.mock(function_name="get",
                            return_value={"_source":{"class_diagram.png":""}})
            self.response = self.context.client().get("/artifacts/1")
            

        with it('returns a 200 status code'):
            expect(self.response.status_code).to(equal(200))

    with description('POST'):
        with before.each:
            current_app.es.mock(function_name="create",
                            return_value={})

            self.response = self.context.client().post("/artifacts",  json={
                "id": "asdf",
                "type": "image",
                "tags": [],
                "file_url": "asdf"})
            

        with it('returns a 201 status code'):
            expect(self.response.status_code).to(equal(201))
