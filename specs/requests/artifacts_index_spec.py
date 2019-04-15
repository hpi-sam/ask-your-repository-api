from doublex import Mock, Stub, ANY_ARG
from expects import expect, have_key, have_len, have_keys, contain, equal
from flask import current_app
from mamba import description, context, before, after, it
from neomodel import db

from application.artifacts.artifact import Artifact
from application.teams.team import Team
from application.artifacts.tags.tag import Tag
from specs.factories.elasticsearch import es_search_response
from specs.factories.request_generator import build_request
from specs.factories.user_factory import UserFactory
from specs.spec_helpers import Context

with description("/images") as self:
    with before.each:
        self.context = Context()
        current_app.es = Stub()

    with after.each:
        db.cypher_query("MATCH (a) DETACH DELETE a")
        if hasattr(self, "context"):
            self.context.delete()

    with description("not logged in"):
        with before.each:
            params = {"offset": 5, "limit": 10}
            self.response = self.context.client().get(build_request("/images", params))

        with it("rejects request"):
            expect(self.response.json["msg"]).to(contain("Missing Authorization Header"))
            expect(self.response.status_code).to(equal(401))

    with description("valid reuest"):
        with context("20 artifacts offset 5 limit 10 for a team"):
            with before.each:
                with Mock() as elastic_mock:
                    elastic_mock.search(ANY_ARG).returns(es_search_response())
                current_app.es = elastic_mock
                self.user = UserFactory.create_user()
                self.context.client().login(self.user)
                self.team = Team(name="Blue").save()
                self.artifacts = []
                for i in range(1, 21):
                    self.artifact = Artifact(file_url=f"url_{i}").save()
                    self.artifact.user_tags.connect(Tag.find_or_create_by(name=f"tag_{i % 5}"))
                    self.team.artifacts.connect(self.artifact)
                    self.artifacts.append(self.artifact)
                params = {"offset": 5, "limit": 10, "team_id": self.team.id_}
                self.response = self.context.client().get(build_request("/images", params))

            with it("responds with the correct images list"):
                expect(self.response.json).to(have_key("images"))

            with it("responds with 10 images"):
                expect(self.response.json["images"]).to(have_len(10))

            with it("has the correct image in first place"):
                image = self.artifacts[5]
                expect(self.response.json["images"][0]).to(
                    have_keys(
                        id=image.id_,
                        url=contain(image.file_url),
                        team_id=image.team_id,
                        tags=list(map(lambda x: x.name, image.tags)),
                    )
                )
