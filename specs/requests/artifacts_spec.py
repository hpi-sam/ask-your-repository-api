""" Tests for artifacts """

import sys
from io import BytesIO
from flask import current_app
from mamba import shared_context, included_context, description, context, before, after, it
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
        with before.each:
            self.path = "/images"

        with description('GET without database'):
            with before.each:
                current_app.es = None
                self.response = self.context.client().get(self.path)

            with it('returns a 503 status code'):
                expect(self.response.status_code).to(equal(503))

        with description('GET'):
            with before.each:
                with Mock() as elastic_mock:
                    elastic_mock.search(ANY_ARG).returns(es_search_response())

            with shared_context('responds with error') as self:
                with before.each:
                    self.response = self.context.client().get(f'{self.path}?{self.param}={self.value}')

                with it('returns a 422 status code'):
                    expect(self.response.status_code).to(equal(422))
                
                with it('returns a descriptive error message'):
                    expect(self.response.json).to(have_key("errors"))
                    expect(self.response.json["errors"]).to(have_key(f'{self.param}'))

            with context('valid request'):
                with before.each:
                    with Mock() as elastic_mock:
                        elastic_mock.search(ANY_ARG).returns(
                            {"hits": {"total": 12, "max_score": 1.0, "hits": [
                                {"_index": "artifact",
                                "_type": "image",
                                "_id": 1,
                                "_score": 1.0,
                                "_source": {
                                    "created_at": "today",
                                    "updated_at": "today",
                                    "file_url": "class_diagram.png",
                                    "tags": ["uml", "class diagram"],
                                    "file_date": "today"}},
                                {"_index": "artifact",
                                "_type": "image",
                                "_id": 1,
                                "_score": 0.5,
                                "_source": {
                                    "created_at": "yesterday",
                                    "updated_at": "yesterday",
                                    "file_url": "use_case_diagram.png",
                                    "tags": ["uml", "use case diagram"],
                                    "file_date": "yesterday"}}]}})

                    current_app.es = elastic_mock
                    self.response = self.context.client().get("/images")

                with it('returns a 200 status code'):
                    expect(self.response.status_code).to(equal(200))
            
            with context('invalid requests'):                
                with description('paramter: limit value: asdf'):
                    with before.each:
                        self.param = 'limit'
                        self.value = 'asdf'

                    with included_context('responds with error'):
                        pass

                with description('paramter: offset value: asdf'):
                    with before.each:
                        self.param = 'offset'
                        self.value = 'asdf'

                    with included_context('responds with error'):
                        pass

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
                    print(self.response.json)
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

                with it('returns a 422 status code'):
                    expect(self.response.status_code).to(equal(422))

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
