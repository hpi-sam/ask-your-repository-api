import uuid
import os

import sys
from expects import expect, have_key, have_len, contain_only, equal, be, be_empty, contain
from mamba import description, before, after, it
import responses
from neomodel import db

from application.teams.team import Team
from specs.factories.team_factory import TeamFactory
from specs.factories.user_factory import UserFactory
from specs.spec_helpers import Context

sys.path.insert(0, 'specs')


def create_and_login_test_user(client):
    user = UserFactory.create_user()
    client.login(user)
    return user


with description('/teams') as self:
    with before.each:
        self.context = Context()

    with after.each:
        db.cypher_query("MATCH (a) DETACH DELETE a")
        pass

    with description('GET'):
        with before.each:
            user = create_and_login_test_user(self.context.client())
            TeamFactory.create_team(name="Blue", members=[user])
            TeamFactory.create_team(name="Red", members=[user])
            TeamFactory.create_team(name="Yellow")
            self.response = self.context.client().get("/teams")

        with it('responds with all my teams'):
            expect(self.response.json).to(have_key("teams"))
            expect(self.response.json["teams"]).to(contain_only(
                have_key("name", "Blue"),
                have_key("name", "Red")
            ))

        with it('doesnt respond with other teams'):
            expect(self.response.json["teams"]).to(have_len(2))
            expect(self.response.json["teams"]).to_not(contain(have_key("name", "Yellow")))

    with description('POST'):
        with description('valid request'):
            with before.each:
                self.user = create_and_login_test_user(self.context.client())
                self.response = self.context.client().post(
                    "/teams",
                    data={"name": "My Team"})
            with it('responds with 200'):
                expect(self.response.status_code).to(equal(200))

            with it('responds with correct team'):
                expect(self.response.json).to(have_key("name", "My Team"))
                expect(self.response.json).to(have_key("id"))

            with it('saves the team'):
                expect(Team.nodes.get_or_none(id_=self.response.json["id"], name="My Team")).to_not(be(None))

            with it('adds logged in user as member'):
                team = Team.nodes.get_or_none(id_=self.response.json["id"], name="My Team")
                expect(list(team.members)).to(contain(self.user))
        with description('notify dialogflow adapter'):
            with before.each:
                current_app.config['DIALOGFLOW_NOTIFY'] = True
                self.DIALOGFLOW_URL = os.environ.get('DIALOGFLOW_ADAPTER') + '/teams'
                self.response_mock = responses.RequestsMock()
                self.response_mock.__enter__() # starts the mocking context

                self.response_mock.add(responses.POST, self.DIALOGFLOW_URL, json={'blub': 'blub'}, status=200)
                self.response = self.context.client().post(
                    "/teams",
                    data={"name": "My Team"})

            with after.each:
                # ends the mocking context (basically the same as with ...)
                self.response_mock.__exit__(None, None, None)
                current_app.config['DIALOGFLOW_NOTIFY'] = False

            with it('notifies dialogflow adapter of team creation'):
                expect(len(self.response_mock.calls)).to(equal(1))
                expect(self.response_mock.calls[0].request.url).to(equal(self.DIALOGFLOW_URL))
                expect(self.response_mock.calls[0].response.status_code).to(equal(200))

        with description('invalid request'):
            with before.each:
                create_and_login_test_user(self.context.client())
                self.response = self.context.client().post(
                    "/teams",
                    data={"name": ""})

            with it('declines empty name'):
                expect(self.response.status_code).to(equal(422))

            with it('does not save invalid teams'):
                expect(Team.nodes).to(be_empty)

    with description('/:id'):
        with description('GET'):
            with description('valid id'):
                with before.each:
                    self.team = TeamFactory.create_team(name='Blue')
                    TeamFactory.add_members_to_team(self.team, 2)
                    self.response = self.context.client().get(f"/teams/{self.team.id_}")

                with it('responds with 200'):
                    expect(self.response.status_code).to(equal(200))

                with it('responds with the correct team'):
                    expect(self.response.json).to(have_key("name", "Blue"))
                    expect(self.response.json).to(have_key("id", uuid.UUID(self.team.id_).urn[9:]))

                with it('includes members in response'):
                    expect(self.response.json).to(have_key("members"))
                    expect(self.response.json['members']).to(have_len(2))

            with description('invalid id'):
                with before.each:
                    team = Team(name='Blue')  # Creating but not saving team so that id is invalid
                    self.response = self.context.client().get(f"/teams/{team.id_}")

                with it('responds error 404'):
                    expect(self.response.status_code).to(equal(404))

        with description('PUT'):
            with description('valid id'):
                with before.each:
                    self.team = Team(name='Blue').save()
                    self.response = self.context.client().put(
                        f"/teams/{self.team.id_}",
                        data={"name": "Red"})

                with it('responds with 200'):
                    expect(self.response.status_code).to(equal(200))

                with it('responds with the updated team'):
                    expect(self.response.json).to(have_key("name", "Red"))
                    expect(self.response.json).to(have_key("id", uuid.UUID(self.team.id_).urn[9:]))

                with description('Team object'):
                    with before.each:
                        self.fresh_team = Team.nodes.get(id_=self.team.id_)

                    with it('is updated correctly'):
                        expect(self.fresh_team.name).to(equal("Red"))

            with description('invalid id'):
                with before.each:
                    team = Team(name="Red").save()
                    team.delete()
                    self.response = self.context.client().put(
                        f"/teams/{team.id_}",
                        data={"name": "Blue"})

                with it('responds error 404'):
                    expect(self.response.status_code).to(equal(404))

            with description('invalid request'):
                with before.each:
                    team = Team(name="Red").save()
                    self.response = self.context.client().put(
                        f"/teams/{team.id_}",
                        data={"name": ""})

                with it('responds with 422 invalid request'):
                    expect(self.response.status_code).to(equal(422))
