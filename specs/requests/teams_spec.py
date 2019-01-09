import sys
from io import BytesIO
from flask import current_app
from mamba import shared_context, included_context, description, context, before, after, it
from expects import *
from hamcrest import matches_regexp
from elasticsearch.exceptions import NotFoundError
from doublex import Mock, Stub, ANY_ARG
from specs.spec_helpers import Context
from application.models.team import Team
from specs.factories.elasticsearch import es_search_response, es_get_response
from specs.factories.uuid_fixture import get_uuid
from specs.factories.date_fixture import get_date, date_regex

sys.path.insert(0, 'specs')

with description('/teams') as self:
    with before.each:
        self.context = Context()

    with after.each:
        current_app.graph.delete_all()

    with description('GET'):
        with before.each:
            Team.create(name='Blue')
            Team.create(name='Red')
            self.response = self.context.client().get("/teams")

        with it('responds with all teams'):
            expect(self.response.json).to(have_key("teams"))
            expect(self.response.json["teams"]).to(have_len(2))
            expect(self.response.json["teams"]).to(contain_only(
                have_key("name", "Blue"),
                have_key("name", "Red")
            ))

    with description('POST'):
        with description('valid request'):
            with before.each:
                self.response = self.context.client().post(
                    "/teams",
                    data={"name": "My Team"})

            with it('responds with 200'):
                expect(self.response.status_code).to(equal(200))

            with it('responds with correct team'):
                expect(self.response.json).to(have_key("name", "My Team"))
                expect(self.response.json).to(have_key("id"))

            with it('saves the team'):
                expect(Team.exists(id_=self.response.json["id"], name="My Name")).to(be(True))

        with description('invalid request'):
            with before.each:
                self.response = self.context.client().post(
                    "/teams",
                    data={"name": ""})

            with it('declines empty name'):
                expect(self.response.status_code).to(equal(422))

            with it('does not save invalid teams'):
                expect(Team.all()).to(be_empty)

    with description('/:id'):
        with description('GET'):
            with description('valid id'):
                with before.each:
                    self.team = Team.create(name='Blue')
                    self.response = self.context.client().get(f"/teams/{self.team.id_}")

                with it('responds with 200'):
                    expect(self.response.status_code).to(equal(200))

                with it('responds with the correct team'):
                    expect(self.response.json).to(have_key("name", "Blue"))
                    expect(self.response.json).to(have_key("id", self.team.id_.urn[9:]))

            with description('invalid id'):
                with before.each:
                    team = Team(name='Blue') # Creating but not saving team so that id is invalid
                    self.response = self.context.client().get(f"/teams/{team.id_}")

                with it('responds error 404'):
                    expect(self.response.status_code).to(equal(404))

        with description('PUT'):
            with description('valid id'):
                with before.each:
                    self.team = Team.create(name='Blue')
                    self.response = self.context.client().put(
                        f"/teams/{self.team.id_}",
                        data={"name": "Red"})

                with it('responds with 200'):
                    expect(self.response.status_code).to(equal(200))

                with it('responds with the updated team'):
                    expect(self.response.json).to(have_key("name", "Red"))
                    expect(self.response.json).to(have_key("id", self.team.id_.urn[9:]))

                with description('Team object'):
                    with before.each:
                        self.fresh_team = Team.find_by(id_=self.team.id_)

                    with it('is updated correctly'):
                        expect(self.fresh_team.name).to(equal("Red"))

            with description('invalid id'):
                with before.each:
                    team = Team.create(name="Red")
                    team.delete()
                    self.response = self.context.client().put(
                        f"/teams/{team.id_}",
                        data={"name": "Blue"})

                with it('responds error 404'):
                    expect(self.response.status_code).to(equal(404))

            with description('invalid request'):
                with before.each:
                    team = Team.create(name="Red")
                    self.response = self.context.client().put(
                        f"/teams/{team.id_}",
                        data={"name": ""})

                with it('responds with 422 invalid request'):
                    expect(self.response.status_code).to(equal(422))
