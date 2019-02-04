""" Tests for artifacts with synonyms"""

from doublex import Mock
from doublex_expects import have_been_satisfied
from expects import expect, equal
from flask import current_app
from hamcrest import anything, has_entries, contains_string, only_contains
from mamba import description, before, after, it

from specs.factories.elasticsearch import es_search_response_synonyms
from specs.spec_helpers import Context

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
            return has_entries(
                query=has_entries(bool=has_entries(should=has_entries(
                    multi_match=has_entries(query=contains_string(tag),
                                            fields=only_contains("tags^2", "*_annotations"))))))


        with before.each:
            with Mock() as elastic_mock:
                elastic_mock.search(body=self.contains_tag("group"), doc_type='image', index='artifact',
                                    search_type=anything()).returns(es_search_response_synonyms())
                current_app.es = elastic_mock

            self.response = self.context.client().get("/images?search=team")

        with it('returns a 200 status code'):
            expect(self.response.status_code).to(equal(200))

        with it('respond with correct tags'):
            expect(self.response.json["images"][0]["tags"]).to(equal(["team", "group"]))

        with it('calls es search with synonyms'):
            expect(current_app.es).to(have_been_satisfied)
