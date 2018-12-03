""" Tests for artifacts """

import sys
from io import BytesIO
from flask import current_app
from mamba import description, before, after, it
from expects import expect, equal
from doublex import Mock, Stub, ANY_ARG
# pylint: disable=wrong-import-position
from specs.spec_helpers import Context
# pylint: enable=wrong-import-position

sys.path.insert(0, 'specs')


with description('/images') as self:

    with before.each:
        self.context = Context()
        current_app.es = Stub()

    with after.each:
        self.context.delete()

    with description('/'):
        with description('GET'):
            with before.each:
                with Mock() as elastic_mock:
                    elastic_mock.search(ANY_ARG).returns(
                        {"hits": {"hits": []}})

                current_app.es = elastic_mock
                self.response = self.context.client().get("/images")
            with it('returns a 200 status code'):
                expect(self.response.status_code).to(equal(200))

    with description('/1'):
        with description('GET'):
            with before.each:
                with Mock() as elastic_mock:
                    elastic_mock.get(
                        doc_type='_all', id='1',
                        index='artifact').returns(
                            {"_id": "asdf",
                             "_type": "image",
                             "_source": {"tags": ["class_diagram.png", ""],
                                         "created_at": "today",
                                         "updated_at": "today",
                                         "file_url": "asdf",
                                         "file_date": "today"}})
                current_app.es = elastic_mock
                self.response = self.context.client().get("/images/1")

            with it('returns a 200 status code'):
                expect(self.response.status_code).to(equal(200))

        with description('POST'):
            with before.each:
                with Mock() as elastic_mock:
                    elastic_mock.index(ANY_ARG).returns({})
                current_app.es = elastic_mock
                print(vars(current_app.url_map))
                self.response = self.context.client().post(
                    "/images", content_type='multipart/form-data', data={
                        "image": (BytesIO(b'oof'), 'helloworld.jpg'),
                        "tags": []
                    })

            with it('returns a 200 status code'):
                expect(self.response.status_code).to(equal(200))
