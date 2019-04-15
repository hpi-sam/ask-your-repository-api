""" Tests for artifacts """

import sys

from doublex import Stub
from expects import expect, equal, have_key, contain_only, contain, be_below_or_equal
from flask import current_app
from mamba import description, context, before, after, it
from neomodel import db

from specs.factories.artifact_factory import ArtifactFactory
from specs.factories.team_factory import TeamFactory
from specs.factories.uuid_fixture import get_uuid
from specs.spec_helpers import Context

sys.path.insert(0, "specs")

with description("/images") as self:
    with before.each:
        self.context = Context()
        current_app.es = Stub()

    with after.each:
        # If check to prevent tests from failing occasionally
        # Needs to be inspected!
        db.cypher_query("MATCH (a) DETACH DELETE a")
        if hasattr(self, "context"):
            self.context.delete()

    with description("/:id/tags"):
        with context("valid request"):
            with description("POST"):
                with context("the resource exists"):
                    with before.each:
                        ArtifactFactory.create_artifact(id_=get_uuid(0))

                        self.response = self.context.client().post(
                            f"/images/{get_uuid(0)}/tags", json={"tags": ["new_tag", "class_diagram"]}
                        )

                    with it("returns a 204 status code"):
                        expect(self.response.status_code).to(equal(204))

                with context("the resource doesn't exists"):
                    with before.each:
                        self.response = self.context.client().post(
                            f"/images/{get_uuid(0)}/tags", json={"tags": ["new_tag", "class_diagram"]}
                        )

                    with it("returns a 404 status code"):
                        expect(self.response.status_code).to(equal(404))

                    with it("includes error message"):
                        expect(self.response.json).to(have_key("error"))

        with context("invalid request"):
            with before.each:
                self.response = self.context.client().post("/images/asdf/tags", json={"tags": "1234"})

            with it("responds with a 422"):
                expect(self.response.status_code).to(equal(422))

            with it("responds with correct error messages"):
                expect(self.response.json).to(have_key("errors"))
                # sending a single tag is fine it will be parsed to an array with only one element
                expect(self.response.json["errors"]).to(have_key("id"))

with description("images /tags/suggested GET"):
    with before.all:
        self.context = Context()
        current_app.es = Stub()
        self.team = TeamFactory.create_team()
        self.team.artifacts.connect(ArtifactFactory.create_artifact(user_tags=["blue", "red"]))
        self.team.artifacts.connect(ArtifactFactory.create_artifact(user_tags=["blue", "red"]))
        self.team.artifacts.connect(ArtifactFactory.create_artifact(user_tags=["blue", "green"]))
        self.team.artifacts.connect(ArtifactFactory.create_artifact(user_tags=["green", "red"]))
        self.team.artifacts.connect(ArtifactFactory.create_artifact(user_tags=["red", "black"]))
        self.team.artifacts.connect(ArtifactFactory.create_artifact(user_tags=["yellow", "purple"]))
        self.other_artifact = ArtifactFactory.create_artifact(user_tags=["pink"])

    with after.all:
        # If check to prevent tests from failing occasionally
        # Needs to be inspected!
        db.cypher_query("MATCH (a) DETACH DELETE a")
        if hasattr(self, "context"):
            self.context.delete()

    with context("without other tags in params"):
        with before.each:
            self.response = self.context.client().get(f"/tags/suggested?team_id={self.team.id_}")

        with it("returns a 200 status code"):
            expect(self.response.status_code).to(equal(200))

        with it("returns 3 tags at most by default"):
            expect(len(self.response.json["tags"])).to(be_below_or_equal(3))

        with it("returns the blue tag first"):
            expect(self.response.json["tags"][0]).to(equal("blue"))

        with it("returns blue green and red"):
            expect(self.response.json["tags"]).to(contain_only("blue", "green", "red"))

    with context("with limit 10"):
        with before.each:
            self.response = self.context.client().get(f"/tags/suggested?team_id={self.team.id_}&limit=10")

        with it("does not contain tags outside the team"):
            expect(self.response.json["tags"]).not_to(contain("pink"))

    with context("with tag blue in params"):
        with before.each:
            self.response = self.context.client().get(f"/tags/suggested?team_id={self.team.id_}&tags=blue&limit=1")

        with it("returns a 200 status code"):
            expect(self.response.status_code).to(equal(200))

        with it("returns <limit> tags at most"):
            expect(len(self.response.json["tags"])).to(be_below_or_equal(1))

        with it("returns red tag first"):
            expect(self.response.json["tags"]).to(contain_only("red"))

    with context("without team in params"):
        with before.each:
            self.response = self.context.client().get(f"/tags/suggested")

        with it("returns a 422 status code"):
            expect(self.response.status_code).to(equal(422))
