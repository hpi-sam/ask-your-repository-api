import sys

from expects import expect, have_key, equal, contain
from mamba import description, before, after, it
from neomodel import db

from specs.factories.team_factory import TeamFactory
from specs.factories.user_factory import UserFactory
from specs.spec_helpers import Context

sys.path.insert(0, 'specs')


def create_and_login_test_user(client):
    user = UserFactory.create_user()
    client.login(user)
    return user


with description('/invites') as self:
    with before.each:
        self.context = Context()

    with after.each:
        db.cypher_query("MATCH (a) DETACH DELETE a")
        pass

    with description('/:id'):
        with description('POST'):
            with description('member not part of team'):
                with before.each:
                    self.team = TeamFactory.create_team(name='Blue')
                    self.user = create_and_login_test_user(self.context.client())
                    print('USER: ' + str(self.user))
                    self.response = self.context.client().post(
                        "/invites/" + str(self.team.join_key))

                with it('responds with 200'):
                    expect(self.response.status_code).to(equal(200))

                with it('responds with the correct team'):
                    expect(self.response.json).to(have_key("name", "Blue"))

                with it('includes added member'):
                    expect(self.response.json).to(have_key("members"))
                    expect([user['id'] for user in self.response.json['members']]).to(
                        contain(str(self.user.id_)))

            with description('member already part of team'):
                with before.each:
                    self.team = TeamFactory.create_team(name='Blue')
                    self.user = create_and_login_test_user(self.context.client())
                    self.team.members.connect(self.user)
                    self.response = self.context.client().post(
                        "/invites/" + str(self.team.join_key))

                with it('responds with 409'):
                    expect(self.response.status_code).to(equal(409))
