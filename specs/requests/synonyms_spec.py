""" Tests for artifacts with synonyms"""

from doublex import Mock
from doublex_expects import have_been_satisfied
from expects import expect, equal
from flask import current_app
from hamcrest import anything, has_entries, contains_string, has_item
from mamba import description, before, after, it
from neomodel import db

from specs.factories.elasticsearch import es_search_response_synonyms
from specs.factories.artifact_factory import ArtifactFactory
from specs.factories.user_factory import UserFactory
from specs.spec_helpers import Context
from specs.factories.uuid_fixture import get_uuid

with description("/images") as self:
    with before.each:
        self.context = Context()
        self.user = UserFactory.create_user()
        self.context.client().login(self.user)

    with after.each:
        # If check to prevent tests from failing occasionally
        # Needs to be inspected!
        db.cypher_query("MATCH (a) DETACH DELETE a")
        if hasattr(self, "context"):
            self.context.delete()

    with description("Synonyms"):

        def contains_tag(self, tag):
            return has_entries(
                query=has_entries(
                    bool=has_entries(should=has_item(has_entries(multi_match=has_entries(query=contains_string(tag)))))
                )
            )

        with before.each:
            ArtifactFactory.create_artifact(id_=get_uuid(0), user_tags=["group", "team"])
            ArtifactFactory.create_artifact(id_=get_uuid(1), user_tags=["group"])

            with Mock() as elastic_mock:
                elastic_mock.search(
                    body=self.contains_tag("group"), doc_type="image", index="artifact", search_type=anything()
                ).returns(es_search_response_synonyms())
                current_app.es = elastic_mock

            self.response = self.context.client().get("/images?search=team")

        with it("returns a 200 status code"):
            expect(self.response.status_code).to(equal(200))

        with it("responds with image that matches synonym of given search term"):
            expect(self.response.json["images"][1]["tags"]).to(equal(["group"]))

        with it("calls es search with synonyms"):
            expect(current_app.es).to(have_been_satisfied)
