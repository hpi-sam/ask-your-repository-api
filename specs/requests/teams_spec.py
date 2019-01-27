import sys
from flask import current_app
from mamba import description, before, after, it
from expects import *
from specs.spec_helpers import Context
from application.models.team import NeoTeam

sys.path.insert(0, 'specs')

with description('/teams') as self:
    with before.each:
        self.context = Context()

    with after.each:
        current_app.graph.delete_all()

    with description('GET'):
        with before.each:
            NeoTeam.create(name='Blue')
            NeoTeam.create(name='Red')
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
                expect(NeoTeam.exists(id=self.response.json["id"], name="My Team")).to(be(True))

        with description('invalid request'):
            with before.each:
                self.response = self.context.client().post(
                    "/teams",
                    data={"name": ""})

            with it('declines empty name'):
                expect(self.response.status_code).to(equal(422))

            with it('does not save invalid teams'):
                expect(NeoTeam.all()).to(be_empty)

    with description('/:id'):
        with description('GET'):
            with description('valid id'):
                with before.each:
                    self.team = NeoTeam.create(name='Blue')
                    self.response = self.context.client().get(f"/teams/{self.team.id}")

                with it('responds with 200'):
                    expect(self.response.status_code).to(equal(200))

                with it('responds with the correct team'):
                    expect(self.response.json).to(have_key("name", "Blue"))
                    expect(self.response.json).to(have_key("id", self.team.id.urn[9:]))

            with description('invalid id'):
                with before.each:
                    team = NeoTeam(name='Blue')  # Creating but not saving team so that id is invalid
                    self.response = self.context.client().get(f"/teams/{team.id}")

                with it('responds error 404'):
                    expect(self.response.status_code).to(equal(404))

        with description('PUT'):
            with description('valid id'):
                with before.each:
                    self.team = NeoTeam.create(name='Blue')
                    self.response = self.context.client().put(
                        f"/teams/{self.team.id}",
                        data={"name": "Red"})

                with it('responds with 200'):
                    expect(self.response.status_code).to(equal(200))

                with it('responds with the updated team'):
                    expect(self.response.json).to(have_key("name", "Red"))
                    expect(self.response.json).to(have_key("id", self.team.id.urn[9:]))

                with description('Team object'):
                    with before.each:
                        self.fresh_team = NeoTeam.find_by(id=self.team.id)

                    with it('is updated correctly'):
                        expect(self.fresh_team.name).to(equal("Red"))

            with description('invalid id'):
                with before.each:
                    team = NeoTeam.create(name="Red")
                    team.delete()
                    self.response = self.context.client().put(
                        f"/teams/{team.id}",
                        data={"name": "Blue"})

                with it('responds error 404'):
                    expect(self.response.status_code).to(equal(404))

            with description('invalid request'):
                with before.each:
                    team = NeoTeam.create(name="Red")
                    self.response = self.context.client().put(
                        f"/teams/{team.id}",
                        data={"name": ""})

                with it('responds with 422 invalid request'):
                    expect(self.response.status_code).to(equal(422))
