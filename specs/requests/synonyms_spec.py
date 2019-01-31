""" Tests for artifacts with synonyms"""

from flask import current_app
from mamba import description, context, before, after, it
from expects import expect, equal
from hamcrest import anything, has_key, has_entries, contains_string
from doublex import Mock
from doublex_expects import have_been_satisfied
from specs.spec_helpers import Context
from specs.factories.elasticsearch import es_search_response_synonyms

with description('/images') as self:
    with before.each:
        self.context = Context()

    with after.each:
        # If check to prevent tests from failing occasionally
        # Needs to be inspected!
        current_app.graph.delete_all()
        if hasattr(self, "context"):
            self.context.delete()

    with description('Synonyms'):
        def contains_tag(self, tag):
            return has_entries(query= has_entries(bool=has_entries(should=has_entries(match=has_entries(tags = contains_string(tag))))))

        with before.each:
            with Mock() as elastic_mock:
                elastic_mock.search(body=self.contains_tag("group"), doc_type='image', index='artifact', search_type=anything()).returns(es_search_response_synonyms())
                current_app.es = elastic_mock

            self.response = self.context.client().get("/images?search=team")

        with it('returns a 200 status code'):
            expect(self.response.status_code).to(equal(200))

        with it('respond with correct tags'):
            expect(self.response.json["images"][0]["tags"]).to(equal(["team", "group"]))

        with it('calls es search with synonyms'):
            expect(current_app.es).to(have_been_satisfied)
