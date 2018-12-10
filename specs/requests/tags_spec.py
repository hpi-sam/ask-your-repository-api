""" Tests for artifacts """

import sys
from flask import current_app
from mamba import  description, context, before, after, it
from expects import expect, equal, have_key, contain_only, be_below_or_equal
from elasticsearch.exceptions import NotFoundError
from doublex import Mock, Stub
from specs.spec_helpers import Context
from specs.factories.elasticsearch import es_get_response, es_search_all_response
from specs.factories.uuid_fixture import get_uuid

sys.path.insert(0, 'specs')


with description('/images') as self:

    with before.each:
        self.context = Context()
        current_app.es = Stub()

    #with after.each:
     #   self.context.delete()

    with description('/:id/tags'):
        with context('valid request'):
            with description('POST'):
                with context("the resource exists"):
                    with before.each:
                        with Mock() as elastic_mock:
                            elastic_mock.get(
                                doc_type='_all', id=f'{get_uuid(0)}',
                                index='artifact').returns(es_get_response())

                            elastic_mock.update(
                                doc_type='image', id=f'{get_uuid(0)}', index='artifact',
                                body={'doc': {"tags": ["class_diagram", "", "new_tag"]}})

                        current_app.es = elastic_mock
                        self.response = self.context.client().post(f"/images/{get_uuid(0)}/tags",
                                                                json={"tags": [
                                                                    "new_tag", "class_diagram"
                                                                ]})

                    with it('returns a 204 status code'):
                        expect(self.response.status_code).to(equal(204))

                with context("the resource doesn't exists"):

                    with before.each:
                        with Mock() as elastic_mock:
                            elastic_mock.get(
                                doc_type='_all', id=f'{get_uuid(0)}',
                                index='artifact').raises(NotFoundError)
                        current_app.es = elastic_mock
                        self.response = self.context.client().post(f"/images/{get_uuid(0)}/tags",
                                                                json={"tags": [
                                                                    "new_tag", "class_diagram"
                                                                ]})

                    with it('returns a 404 status code'):
                        expect(self.response.status_code).to(equal(404))

                    with it('includes error message'):
                        expect(self.response.json).to(have_key("error"))

        with context('invalid request'):
            with before.each:
                self.response = self.context.client().post("/images/asdf/tags", json={
                    "tags": "1234"
                })
                    
            with it('responds with a 422'):
                expect(self.response.status_code).to(equal(422))
            
            with it('responds with correct error messages'):
                expect(self.response.json).to(have_key('errors'))
                # sending a single tag is fine it will be parsed to an array with only one element
                expect(self.response.json['errors']).to(have_key('object_id'))

    with description("/tags/suggested"):
        with description("GET"):
            with context("there are tags with a high enough interestingness"):
                with before.each:
                    with Mock() as elastic_mock:
                        elastic_mock.search(index="artifact").returns({
                            "hits": {
                                "total": 12
                            }
                        })
                        elastic_mock.search(index="artifact",
                                            body={"from": 0,
                                                  "size": 12}).returns(es_search_all_response())

                    current_app.es = elastic_mock
                    self.response = self.context.client().get(
                        "/tags/suggested?tags=class diagram&tags=uml")

                with it("returns a 200 status code"):
                    expect(self.response.status_code).to(equal(200))

                with it("returns <limit> tags at most"):
                    expect(len(self.response.json["tags"])).to(be_below_or_equal(3))

                with it("returns the correct tags"):
                    expect(self.response.json["tags"]).to(contain_only("use case diagram",
                                                                       "tomato",
                                                                       "apple"))

            with context("no other tags with a high enough interestingness"):
                with before.each:
                    with Mock() as elastic_mock:
                        elastic_mock.search(index="artifact").returns({
                            "hits": {
                                "total": 12
                            }
                        })
                        elastic_mock.search(index="artifact",
                                            body={"from": 0,
                                                  "size": 12}).returns(es_search_all_response())

                    current_app.es = elastic_mock
                    self.response = self.context.client().get("/tags/suggested")

                with it("returns a 200 status code"):
                    expect(self.response.status_code).to(equal(200))

                with it("returns <limit> tags at most"):
                    expect(len(self.response.json["tags"])).to(be_below_or_equal(3))

                with it("returns the most frequent tags"):
                    expect(self.response.json["tags"]).to(contain_only("tomato",
                                                                       "uml",
                                                                       "class diagram"))
