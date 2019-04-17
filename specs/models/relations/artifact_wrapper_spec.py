""" Test the ArtifactConnector class. Currently it's more of a wrapper than a builder sadly
    #refactor soon"""
from expects import expect, be_none, be_a, equal, contain
from mamba import description, before, after, it, context
from neomodel import db

from application.artifacts.artifact import Artifact
from application.artifacts.artifact_connector import ArtifactConnector
from specs.spec_helpers import Context

with description("Artifact Wrapper") as self:
    with before.each:
        self.context = Context()

    with after.each:
        db.cypher_query("MATCH (a) DETACH DELETE a")
        if hasattr(self, "context"):
            self.context.delete()

    with description("Building"):
        with before.each:
            self.artifact = ArtifactConnector()
            self.artifact.build_with(file_url="asdf", type="image")

        with it("creates a neo artifact"):
            expect(self.artifact.neo).to_not(be_none)
            expect(self.artifact.neo).to(be_a(Artifact))

    with description("Save"):
        with context("without tags"):
            with before.each:
                self.artifact = ArtifactConnector()
                self.artifact.build_with(file_url="asdf", type="image")
                self.artifact.save()

            with it("saves it to neo4j"):
                expect(Artifact.exists(file_url="asdf")).to(equal(True))

        with context("with tags"):
            with before.each:
                self.artifact = ArtifactConnector()
                self.artifact.build_with(file_url="asdf", type="image", user_tags=["a", "s", "d", "f"])
                self.artifact.save()

            with it("saves tags in Neo4j"):
                expect(list(map(lambda x: x.name, self.artifact.neo.tags))).to(contain("a", "s", "d", "f"))

    with description("update"):
        with context("file_url"):
            with before.each:
                self.artifact = ArtifactConnector()
                self.artifact.build_with(file_url="asdf", type="image")
                self.artifact.save()
                self.artifact.update_with(file_url="blub")

            with it("updates in neo4j"):
                expect(Artifact.exists(file_url="blub")).to(equal(True))
                expect(Artifact.exists(file_url="asdf")).to(equal(False))

        with context("tags"):
            with before.each:
                self.artifact = ArtifactConnector()
                self.artifact.build_with(file_url="asdf", type="image")
                self.artifact.save()
                self.artifact.update_with(
                    user_tags=["a", "s", "d", "f"], label_tags=["x", "d"], text_tags=["r", "o", "f", "l"]
                )

            with it("updates user tags in neo4j"):
                ARTIFACT = Artifact.find_by(file_url="asdf")
                expect(list(map(lambda x: x.name, ARTIFACT.user_tags))).to(contain("a", "s", "d", "f"))

            with it("updates label tags in neo4j"):
                ARTIFACT = Artifact.find_by(file_url="asdf")
                expect(list(map(lambda x: x.name, ARTIFACT.label_tags))).to(contain("x", "d"))

            with it("updates text tags in neo4j"):
                ARTIFACT = Artifact.find_by(file_url="asdf")
                expect(list(map(lambda x: x.name, ARTIFACT.text_tags))).to(contain("r", "o", "f", "l"))

            with it("shows all tags from neo4j"):
                ARTIFACT = Artifact.find_by(file_url="asdf")
                expect(list(map(lambda x: x.name, ARTIFACT.tags))).to(contain("a", "x", "r"))

            with context("updating again"):
                with before.each:
                    self.artifact.update_with(user_tags=["l", "m", "a", "o"])

                with it("saves new tags in neo4j"):
                    ARTIFACT = Artifact.find_by(file_url="asdf")
                    expect(list(map(lambda x: x.name, ARTIFACT.user_tags))).to(contain("l", "m", "a", "o"))
