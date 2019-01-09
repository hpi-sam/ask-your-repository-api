""" Tests for artifacts """

import sys
import datetime
from io import BytesIO
from flask import current_app
from mamba import shared_context, included_context, description, context, before, after, it
from expects import expect, equal, have_key
from hamcrest import matches_regexp
from elasticsearch.exceptions import NotFoundError
from doublex import Mock, Stub, ANY_ARG
from specs.spec_helpers import Context
from specs.factories.elasticsearch import es_search_response, es_get_response
from specs.factories.uuid_fixture import get_uuid
from specs.factories.date_fixture import get_date, date_regex
from application.models.artifact import Artifact

sys.path.insert(0, 'specs')


with description('/images') as self:

    with before.each:
        self.context = Context()

    with after.each:
        # If check to prevent tests from failing occasionally
        # Needs to be inspected!
        if current_app.es:
            for artifact in Artifact.all(create_objects=True):
                artifact.delete()
        if hasattr(self, "context"):
            self.context.delete()


    with description('/'):
        with before.each:
            self.path = "/images"

        with description('GET without database'):
            with before.each:
                self.es = current_app.es
                current_app.es = None
                self.response = self.context.client().get(self.path)

            with after.each:
                current_app.es = self.es

            with it('returns a 503 status code'):
                expect(self.response.status_code).to(equal(503))

        with description('GET'):
            with before.each:
                Artifact({'file_url': 'asdf', 'file_date': datetime.datetime.now(), 'type': 'image'}).save()

            with context('valid request'):
                with before.each:
                    self.response = self.context.client().get("/images")

                with it('returns a 200 status code'):
                    expect(self.response.status_code).to(equal(200))

            with shared_context('responds with error') as self:
                with before.each:
                    self.response = (self.context.client()
                                     .get(f'{self.path}?{self.param}={self.value}'))

                with it('returns a 422 status code'):
                    expect(self.response.status_code).to(equal(422))

                with it('returns a descriptive error message'):
                    expect(self.response.json).to(have_key("errors"))
                    expect(self.response.json["errors"]).to(have_key(f'{self.param}'))

            with context('invalid requests'):
                with description('paramter: limit | value: asdf'):
                    with before.each:
                        self.param = 'limit'
                        self.value = 'asdf'

                    with included_context('responds with error'):
                        pass

                with description('paramter: offset | value: asdf'):
                    with before.each:
                        self.param = 'offset'
                        self.value = 'asdf'

                    with included_context('responds with error'):
                        pass

        with description('POST'):
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

    with description('/:id'):
        with description('GET'):
            with context("the resource exists"):
                with before.each:
                    image = Artifact({'file_url': 'asdf', 'file_date': datetime.datetime.now(), 'type': 'image'})
                    image.save()
                    self.response = self.context.client().get(f"/images/{image.id}")

                with it('returns a 200 status code'):
                    expect(self.response.status_code).to(equal(200))

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
                        image = Artifact({'file_url': 'asdf', 'file_date': datetime.datetime.now(), 'type': 'image'})
                        image.save()
                        self.response = self.context.client().put(f"/images/{image.id}", json={
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
                        image = Artifact({'file_url': 'asdf', 'file_date': datetime.datetime.now(), 'type': 'image'})
                        image.save()
                        self.response = self.context.client().delete(f"/images/{image.id}")

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
