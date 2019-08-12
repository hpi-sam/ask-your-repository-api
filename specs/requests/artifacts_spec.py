""" Tests for artifacts """

import os
import sys

from PIL import Image
from doublex import Stub
from expects import expect, equal, have_key, have_keys
from flask import current_app
from mamba import shared_context, included_context, description, context, before, after, it
from neomodel import db

from application.artifacts.artifact import Artifact
from specs.factories.artifact_factory import ArtifactFactory
from specs.factories.image_factory import ImageFactory
from specs.factories.image_recognition import mock_image_recognition
from specs.factories.request_generator import build_request
from specs.factories.user_factory import UserFactory
from specs.factories.uuid_fixture import get_uuid
from specs.spec_helpers import Context

sys.path.insert(0, "specs")


def clear_upload_dir():
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    for file_name in os.listdir(upload_dir):
        file_path = os.path.join(upload_dir, file_name)
        if os.path.isfile(file_path):
            os.unlink(file_path)


with description("/images") as self:
    with before.each:
        self.context = Context()
        current_app.es = Stub()
        self.user = UserFactory.create_user()
        self.context.client().login(self.user)

    with after.each:
        clear_upload_dir()
        db.cypher_query("MATCH (a) DETACH DELETE a")
        if hasattr(self, "context"):
            self.context.delete()

    with description("/"):
        with before.each:
            self.path = "/images"

        with description("GET without database"):
            with before.each:
                current_app.es = None
                self.response = self.context.client().get(self.path)

            with it("returns a 503 status code"):
                expect(self.response.status_code).to(equal(503))

        with description("GET"):
            with shared_context("responds with error") as self:
                with before.each:
                    self.response = self.context.client().get(build_request(self.path, self.params))

                with it("returns a 422 status code"):
                    expect(self.response.status_code).to(equal(422))

                with it("returns a descriptive error message"):
                    expect(self.response.json).to(have_key("errors"))
                    expect(self.response.json["errors"]).to(have_keys(*self.params.keys()))

            with context("valid request"):
                with before.each:
                    self.response = self.context.client().get("/images")

                with it("returns a 200 status code"):
                    expect(self.response.status_code).to(equal(200))

            with context("invalid requests"):
                with description("paramter: limit | value: asdf"):
                    with before.each:
                        self.params = {"limit": "asdf"}

                    with included_context("responds with error"):
                        pass

                with description("paramter: offset | value: asdf"):
                    with before.each:
                        self.params = {"offset": "asdf"}

                    with included_context("responds with error"):
                        pass

        with description("POST"):
            with context("with file attached"):
                with before.each:
                    with mock_image_recognition:
                        self.response = self.context.client().post(
                            "/images",
                            content_type="multipart/form-data",
                            data={"image": (ImageFactory.load_fixture("goat.jpg"), "goat.jpg"), "tags": []},
                        )

                with it("returns a 200 status code"):
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

                with it("saves the image to the configured uploads directory"):
                    file_name = self.response.json.get("url").split("/")[-1]
                    file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], file_name)
                    expect(os.path.isfile(file_path)).to(equal(True))

                with description("resized image versions"):
                    with before.each:
                        self.widths = [320, 640, 1080]

                        original_file_name = self.response.json.get("url").split("/")[-1]
                        [self.prefix, self.suffix] = original_file_name.rsplit(".", 1)

                    with it("saves resized versions of the image to the configured uploads directory"):
                        for width in self.widths:
                            file_name = f"{self.prefix}_{width}w.{self.suffix}"
                            file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], file_name)
                            expect(os.path.isfile(file_path)).to(equal(True))

                    with it("saves resized versions with correct widths"):
                        for width in self.widths:
                            file_name = f"{self.prefix}_{width}w.{self.suffix}"
                            file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], file_name)
                            image = Image.open(file_path)
                            expect(image.width).to(equal(width))
                            image.close()

            with context("without file attached"):
                with before.each:
                    self.response = self.context.client().post(
                        "/images", content_type="multipart/form-data", data={"tags": []}
                    )

                with it("returns a 422 status code"):
                    expect(self.response.status_code).to(equal(422))

            with context("with malicious file attached"):
                with before.each:
                    self.response = self.context.client().post(
                        "/images",
                        content_type="multipart/form-data",
                        data={"image": (ImageFactory.load_fixture("goat.jpg"), "malicious_file.exe")},
                    )

                with it("returns a 422 status code"):
                    expect(self.response.status_code).to(equal(422))

            with description("logged in"):
                with before.each:
                    with mock_image_recognition:
                        self.response = self.context.client().post(
                            "/images",
                            content_type="multipart/form-data",
                            data={"image": (ImageFactory.load_fixture("goat.jpg"), "goat.jpg"), "tags": []},
                        )

                with it("returns a 200 status code"):
                    expect(self.response.status_code).to(equal(200))

                with it("connects the user and returns the user_id"):
                    expect(self.response.json).to(have_key("author", {"username": self.user.username}))

                with it("persists the user in the database"):
                    uid = self.response.json["id"]
                    expect(Artifact.find(uid).author.username).to(equal(self.user.username))

        with description("UPDATE MANY"):
            with context("valid request"):
                with context("all the resources exist"):
                    with before.each:
                        ArtifactFactory.create_artifact(id_=get_uuid(0))
                        ArtifactFactory.create_artifact(id_=get_uuid(1))
                        self.response = self.context.client().patch(
                            f"/images",
                            json={
                                "artifacts": [
                                    {"id": get_uuid(0), "tags": ["blue", "red"]},
                                    {"id": get_uuid(1), "tags": ["blue", "green"]},
                                ]
                            },
                        )

                    with it("returns a 204 status code"):
                        expect(self.response.status_code).to(equal(204))

                with context("a resource does not exists"):
                    with before.each:
                        self.response = self.context.client().patch(
                            f"/images", json={"artifacts": [{"id": get_uuid(0), "tags": ["blue", "red"]}]}
                        )

                    with it("returns a 404 status code"):
                        expect(self.response.status_code).to(equal(404))

                    with it("includes error message"):
                        expect(self.response.json).to(have_key("error"))

            with context("invalid request"):
                with before.each:
                    self.response = self.context.client().patch("/images", json={"artifacts": [{}]})

                with it("responds with a 422"):
                    expect(self.response.status_code).to(equal(422))

                with it("responds with correct error messages"):
                    expect(self.response.json).to(have_key("errors"))
                    expect(self.response.json["errors"]).to(have_key("artifacts"))

    with description("/:id"):
        with description("GET"):
            with context("the resource exists"):
                with before.each:
                    self.artifact = ArtifactFactory.create_artifact(id_=get_uuid(0))
                    self.response = self.context.client().get(f"/images/{get_uuid(0)}")

                with it("returns a 200 status code"):
                    expect(self.response.status_code).to(equal(200))

                with it("has correct json response"):
                    expect(self.response.json).to(
                        have_keys(
                            "file_date",
                            "updated_at",
                            "created_at",
                            "url",
                            "team_id",
                            "id",
                            "tags",
                            "user_tags",
                            "label_tags",
                            "text_tags",
                        )
                    )

            with context("the resource doesn't exists"):
                with before.each:
                    self.response = self.context.client().get(f"/images/{get_uuid(0)}")

                with it("returns a 404 status code"):
                    expect(self.response.status_code).to(equal(404))

                with it("includes error message"):
                    expect(self.response.json).to(have_key("error"))

        with description("UPDATE"):
            with context("valid request"):
                with context("the resource exists"):
                    with before.each:
                        ArtifactFactory.create_artifact(id_=get_uuid(0))
                        self.response = self.context.client().put(
                            f"/images/{get_uuid(0)}", json={"tags": ["added", "tags"], "file_url": "test_updated.png"}
                        )

                    with it("returns a 204 status code"):
                        expect(self.response.status_code).to(equal(204))

                with context("the resource doesn't exists"):
                    with before.each:
                        self.response = self.context.client().put(f"/images/{get_uuid(0)}")

                    with it("returns a 404 status code"):
                        expect(self.response.status_code).to(equal(404))

                    with it("includes error message"):
                        expect(self.response.json).to(have_key("error"))

            with context("invalid request"):
                with before.each:
                    self.response = self.context.client().put("/images/asdf", json={"tags": "1234"})
                with it("responds with a 422"):
                    expect(self.response.status_code).to(equal(422))

                with it("responds with correct error messages"):
                    expect(self.response.json).to(have_key("errors"))
                    # sending a single tag is fine it will be
                    # parsed to an array with only one element
                    expect(self.response.json["errors"]).to(have_key("id"))

        with description("DELETE"):
            with context("valid request"):
                with context("the resource exists"):
                    with before.each:
                        ArtifactFactory.create_artifact(id_=get_uuid(0))
                        self.response = self.context.client().delete(f"/images/{get_uuid(0)}")

                    with it("returns a 204 status code"):
                        expect(self.response.status_code).to(equal(204))

                with context("the resource doesn't exists"):
                    with before.each:
                        self.response = self.context.client().delete(f"/images/{get_uuid(0)}")

                    with it("returns a 404 status code"):
                        expect(self.response.status_code).to(equal(404))

                    with it("includes error message"):
                        expect(self.response.json).to(have_key("error"))

            with context("invalid request"):
                with before.each:
                    self.response = self.context.client().delete("/images/asdf")

                with it("responds with a 422"):
                    expect(self.response.status_code).to(equal(422))

                with it("responds with correct error messages"):
                    expect(self.response.json).to(have_key("errors"))
                    expect(self.response.json["errors"]).to(have_key("id"))
