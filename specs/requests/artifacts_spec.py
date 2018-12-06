""" Tests for artifacts """

import sys
from io import BytesIO
from flask import current_app
from mamba import description, context, before, after, it
from expects import expect, equal, have_key
from elasticsearch.exceptions import NotFoundError
from doublex import Mock, Stub, ANY_ARG
from specs.spec_helpers import Context
from specs.factories.elasticsearch import es_search_response, es_get_response

sys.path.insert(0, 'specs')

with description('/images') as self:

    with before.each:
        self.context = Context()
        current_app.es = Stub()

    with after.each:
        self.context.delete()

    with description('/'):
        with description('GET without database'):
            with before.each:
                current_app.es = None
                self.response = self.context.client().get("/images")

            with it('returns a 503 status code'):
                expect(self.response.status_code).to(equal(503))

        with description('GET'):
            with before.each:
                with Mock() as elastic_mock:
                    elastic_mock.search(ANY_ARG).returns(es_search_response())

                current_app.es = elastic_mock
                self.response = self.context.client().get("/images")

            with it('returns a 200 status code'):
                expect(self.response.status_code).to(equal(200))

        with description('POST'):
            with before.each:
                with Mock() as elastic_mock:
                    elastic_mock.index(ANY_ARG).returns({})
                current_app.es = elastic_mock

            with context("with file attached"):
                with before.each:
                    self.response = self.context.client().post(
                        "/images", content_type='multipart/form-data', data={
                            "image": (BytesIO(b'oof'), 'helloworld.jpg'),
                            "tags": []
                        })

                with it('returns a 200 status code'):
                    expect(self.response.status_code).to(equal(200))

                with it("returns an id"):
                    expect(self.response.json).to(have_key("id"))

                with it("returns a file_url"):
                    expect(self.response.json).to(have_key("file_url"))

            with context("without file attached"):
                with before.each:
                    self.response = self.context.client().post(
                        "/images", content_type='multipart/form-data', data={
                            "tags": []
                        })

                with it('returns a 400 status code'):
                    expect(self.response.status_code).to(equal(400))

            with context("with malicious file attached"):
                with before.each:
                    self.response = self.context.client().post(
                        "/images", content_type='multipart/form-data', data={
                            "image": (BytesIO(b'oof'), 'malicious_file.exe')
                        })

                with it('returns a 422 status code'):
                    expect(self.response.status_code).to(equal(422))

    with description('/:id'):
        with description('GET'):
            with context("the resource exists"):
                with before.each:
                    with Mock() as elastic_mock:
                        elastic_mock.get(
                            doc_type='_all', id='1',
                            index='artifact').returns(es_get_response())
                    current_app.es = elastic_mock
                    self.response = self.context.client().get("/images/1")

                with it('returns a 200 status code'):
                    expect(self.response.status_code).to(equal(200))

            with context("the resource doesn't exists"):

                with before.each:
                    with Mock() as elastic_mock:
                        elastic_mock.get(
                            doc_type='_all', id='1',
                            index='artifact').raises(NotFoundError)
                    current_app.es = elastic_mock
                    self.response = self.context.client().get("/images/1")

                with it('returns a 404 status code'):
                    expect(self.response.status_code).to(equal(404))

                with it('includes error message'):
                    expect(self.response.json).to(have_key("error"))

        with description('UPDATE'):
            with context("the resource exists"):
                with before.each:
                    with Mock() as elastic_mock:
                        elastic_mock.get(
                            doc_type='_all', id='1',
                            index='artifact').returns(es_get_response())

                        elastic_mock.update(
                            doc_type='image', id='1', index='artifact',
                            body={'doc': {
                                'file_url': "test_updated.png",
                                "tags": ["added", "tags"]}})

                    current_app.es = elastic_mock
                    self.response = self.context.client().put("/images/1", json={
                        "tags": ["added", "tags"],
                        "file_url": "test_updated.png"
                    })

                with it('returns a 204 status code'):
                    expect(self.response.status_code).to(equal(204))

            with context("the resource doesn't exists"):

                with before.each:
                    with Mock() as elastic_mock:
                        elastic_mock.get(
                            doc_type='_all', id='1',
                            index='artifact').raises(NotFoundError)
                    current_app.es = elastic_mock
                    self.response = self.context.client().put("/images/1")

                with it('returns a 404 status code'):
                    expect(self.response.status_code).to(equal(404))

                with it('includes error message'):
                    expect(self.response.json).to(have_key("error"))

        with description('DELETE'):
            with context("the resource exists"):
                with before.each:
                    with Mock() as elastic_mock:
                        elastic_mock.get(
                            doc_type='_all', id='1',
                            index='artifact').returns(es_get_response())

                        elastic_mock.delete(
                            doc_type='image', id='1', index='artifact')

                    current_app.es = elastic_mock
                    self.response = self.context.client().delete("/images/1")

                with it('returns a 204 status code'):
                    expect(self.response.status_code).to(equal(204))

            with context("the resource doesn't exists"):

                with before.each:
                    with Mock() as elastic_mock:
                        elastic_mock.get(
                            doc_type='_all', id='1',
                            index='artifact').raises(NotFoundError)
                    current_app.es = elastic_mock
                    self.response = self.context.client().delete("/images/1")

                with it('returns a 404 status code'):
                    expect(self.response.status_code).to(equal(404))

                with it('includes error message'):
                    expect(self.response.json).to(have_key("error"))

    with description('/1/tags'):
        with description('POST'):
            with context("the resource exists"):
                with before.each:
                    with Mock() as elastic_mock:
                        elastic_mock.get(
                            doc_type='_all', id='1',
                            index='artifact').returns(es_get_response())

                        elastic_mock.update(
                            doc_type='image', id='1', index='artifact',
                            body={'doc': {"tags": ["class_diagram", "", "new_tag"]}})

                    current_app.es = elastic_mock
                    self.response = self.context.client().post("/images/1/tags",
                                                               json={"tags": [
                                                                   "new_tag", "class_diagram"
                                                               ]})

                with it('returns a 200 status code'):
                    expect(self.response.status_code).to(equal(204))

            with context("the resource doesn't exists"):

                with before.each:
                    with Mock() as elastic_mock:
                        elastic_mock.get(
                            doc_type='_all', id='1',
                            index='artifact').raises(NotFoundError)
                    current_app.es = elastic_mock
                    self.response = self.context.client().post("/images/1/tags",
                                                               json={"tags": [
                                                                   "new_tag", "class_diagram"
                                                               ]})

                with it('returns a 404 status code'):
                    expect(self.response.status_code).to(equal(404))

                with it('includes error message'):
                    expect(self.response.json).to(have_key("error"))
