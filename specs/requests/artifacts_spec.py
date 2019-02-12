""" Tests for artifacts """

import sys
from io import BytesIO

from doublex import Mock, Stub, ANY_ARG
from doublex_expects import have_been_satisfied
from elasticsearch.exceptions import NotFoundError
from expects import expect, equal, have_key, have_keys
from flask import current_app
from hamcrest import matches_regexp
from mamba import shared_context, included_context, description, context, before, after, it
from neomodel import db

from application.models import Artifact
from specs.factories.date_fixture import date_regex
from specs.factories.elasticsearch import es_search_response, es_get_response
from specs.factories.image_recognition import mock_image_recognition
from specs.factories.request_generator import build_request
from specs.factories.uuid_fixture import get_uuid
from specs.spec_helpers import Context

sys.path.insert(0, 'specs')


def create_artifact_with(id):
    return Artifact(id_=id, file_url='asdf').save()


with description('/images') as self:
    with before.each:
        self.context = Context()
        current_app.es = Stub()

    with after.each:
        db.cypher_query("MATCH (a) DETACH DELETE a")
        if hasattr(self, "context"):
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
            with shared_context('responds with error') as self:
                with before.each:
                    self.response = (self.context.client()
                                     .get(build_request(self.path, self.params)))

                with it('returns a 422 status code'):
                    expect(self.response.status_code).to(equal(422))

                with it('returns a descriptive error message'):
                    expect(self.response.json).to(have_key("errors"))
                    expect(self.response.json["errors"]).to(have_keys(*self.params.keys()))

            with context('valid request'):
                with before.each:
                    self.response = self.context.client().get("/images")

                with it('returns a 200 status code'):
                    expect(self.response.status_code).to(equal(200))

            with context('invalid requests'):
                with description('paramter: limit | value: asdf'):
                    with before.each:
                        self.params = {'limit': 'asdf'}

                    with included_context('responds with error'):
                        pass

                with description('paramter: offset | value: asdf'):
                    with before.each:
                        self.params = {'offset': 'asdf'}

                    with included_context('responds with error'):
                        pass

        with description('POST'):
            with context("with file attached"):
                with before.each:
                    with mock_image_recognition:
                        self.response = self.context.client().post(
                            "/images", content_type='multipart/form-data', data={
                                "image": (BytesIO(b'oof'), 'helloworld.jpg'),
                                "tags": []
                            })

                with it('returns a 200 status code'):
                    expect(self.response.status_code).to(equal(200))

                with it("returns an id"):
                    expect(self.response.json).to(have_key("id"))

                with it("doesn't return a file_url"):
                    # Regression test: Always return url
                    expect(self.response.json).not_to(have_key("file_url"))

                with it("returns a url"):
                    expect(self.response.json).to(have_key("url"))

                with it("returns an empty list for tags"):
                    expect(self.response.json.get("tags")).to(equal([]))

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

        with description('UPDATE MANY'):
            with context('valid request'):
                with context("all the resources exist"):
                    with before.each:
                        create_artifact_with(get_uuid(0))
                        create_artifact_with(get_uuid(1))
                        self.response = self.context.client().patch(f"/images", json={
                            "artifacts": [
                                {
                                    "id": get_uuid(0),
                                    "tags": ["blue", "red"]
                                },
                                {
                                    "id": get_uuid(1),
                                    "tags": ["blue", "green"]
                                }
                            ]
                        })

                    with it('returns a 204 status code'):
                        expect(self.response.status_code).to(equal(204))

                with context("a resource does not exists"):
                    with before.each:
                        self.response = self.context.client().patch(f"/images", json={
                            "artifacts": [{"id": get_uuid(0), "tags": ["blue", "red"]}]
                        })

                    with it('returns a 404 status code'):
                        expect(self.response.status_code).to(equal(404))

                    with it('includes error message'):
                        expect(self.response.json).to(have_key("error"))

            with context('invalid request'):
                with before.each:
                    self.response = self.context.client().patch("/images", json={
                        "artifacts": [{}]
                    })

                with it('responds with a 422'):
                    expect(self.response.status_code).to(equal(422))

                with it('responds with correct error messages'):
                    expect(self.response.json).to(have_key('errors'))
                    expect(self.response.json['errors']).to(have_key('artifacts'))

    with description('/:id'):
        with description('GET'):
            with context("the resource exists"):
                with before.each:
                    self.artifact = create_artifact_with(get_uuid(0))
                    self.response = self.context.client().get(f"/images/{get_uuid(0)}")

                with it('returns a 200 status code'):
                    expect(self.response.status_code).to(equal(200))

                with it('has correct json response'):
                    expect(self.response.json).to(have_keys('file_date', 'updated_at', 'created_at',
                                                            'url', 'team_id', 'id', 'tags'))

            with context("the resource doesn't exists"):
                with before.each:
                    self.response = self.context.client().get(f"/images/{get_uuid(0)}")

                with it('returns a 404 status code'):
                    expect(self.response.status_code).to(equal(404))

                with it('includes error message'):
                    expect(self.response.json).to(have_key("error"))

        with description('UPDATE'):
            with context('valid request'):
                with context("the resource exists"):
                    with before.each:
                        create_artifact_with(get_uuid(0))
                        self.response = self.context.client().put(f"/images/{get_uuid(0)}", json={
                            "tags": ["added", "tags"],
                            "file_url": "test_updated.png"
                        })

                    with it('returns a 204 status code'):
                        expect(self.response.status_code).to(equal(204))

                with context("the resource doesn't exists"):
                    with before.each:
                        self.response = self.context.client().put(f"/images/{get_uuid(0)}")

                    with it('returns a 404 status code'):
                        expect(self.response.status_code).to(equal(404))

                    with it('includes error message'):
                        expect(self.response.json).to(have_key("error"))

            with context('invalid request'):
                with before.each:
                    self.response = self.context.client().put("/images/asdf", json={
                        "tags": "1234"
                    })
                with it('responds with a 422'):
                    expect(self.response.status_code).to(equal(422))

                with it('responds with correct error messages'):
                    expect(self.response.json).to(have_key('errors'))
                    # sending a single tag is fine it will be
                    # parsed to an array with only one element
                    expect(self.response.json['errors']).to(have_key('object_id'))

        with description('DELETE'):
            with context("valid request"):
                with context("the resource exists"):
                    with before.each:
                       create_artifact_with(get_uuid(0))
                       self.response = self.context.client().delete(f"/images/{get_uuid(0)}")

                    with it('returns a 204 status code'):
                        expect(self.response.status_code).to(equal(204))

                with context("the resource doesn't exists"):
                    with before.each:
                        self.response = self.context.client().delete(f"/images/{get_uuid(0)}")

                    with it('returns a 404 status code'):
                        expect(self.response.status_code).to(equal(404))

                    with it('includes error message'):
                        expect(self.response.json).to(have_key("error"))

            with context('invalid request'):
                with before.each:
                    self.response = self.context.client().delete("/images/asdf")

                with it('responds with a 422'):
                    expect(self.response.status_code).to(equal(422))

                with it('responds with correct error messages'):
                    expect(self.response.json).to(have_key('errors'))
                    expect(self.response.json['errors']).to(have_key('object_id'))
