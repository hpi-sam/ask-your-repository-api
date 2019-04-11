import sys
from expects import expect, have_key, equal, be
from mamba import description, before, after, it
from neomodel import db

from application.extensions import mail
from application.models import User
from specs.factories.user_factory import UserFactory
from specs.factories.jwt_token_fixture import reset_password_token, expired_reset_password_token
from specs.spec_helpers import Context

sys.path.insert(0, 'specs')

with description('/password_resets') as self:
    with before.each:
        self.context = Context()

    with after.each:
        db.cypher_query("MATCH (a) DETACH DELETE a")
        pass

    with description('POST'):
        with description('valid request'):
            with before.each:
                self.user = UserFactory.create_user()
                with mail.record_messages() as outbox:
                    self.outbox = outbox
                    self.response = self.context.client().post(
                        "/password_resets",
                        data={
                            "email_or_username": self.user.email,
                            "base_url": "http://localhost:3000/password_resets"
                        })

            with it('responds with 204'):
                expect(self.response.status_code).to(equal(204))

            with it('sends one email'):
                expect(len(self.outbox)).to(be(1))

            with it('sends email with subject "Reset Password"'):
                "Reset Password"
                expect(self.outbox[0].subject).to(equal("Reset Password"))

        with description('invalid request'):
            with before.each:
                with mail.record_messages() as outbox:
                    self.outbox = outbox
                    self.response = self.context.client().post(
                        "/password_resets",
                        data={
                            "email_or_username": "non_existing_user",
                            "base_url": "http://localhost:3000/password_resets"
                        })

            with it('responds with 404'):
                expect(self.response.status_code).to(equal(404))

            with it('returns a descriptive error message'):
                expect(self.response.json).to(have_key("error"))
                expect(self.response.json["error"]).to(equal("Could not find a user with that email address"))

    with description('PUT'):
        with description('valid jwt'):
            with before.each:
                self.user = UserFactory.create_user()
                self.response = self.context.client().put(
                    "/password_resets",
                    data={
                        "reset_token": reset_password_token(self.user),
                        "password": "new_password"
                    })

            with it('responds with 200'):
                expect(self.response.status_code).to(equal(200))

            with it('updates the users password'):
                expect(User.find(self.user.id_).check_password('new_password')).to(be(True))

        with description('invalid jwt'):
            with before.each:
                self.user = UserFactory.create_user()
                self.response = self.context.client().put(
                    "/password_resets",
                    data={
                        "reset_token": "invalid_jwt",
                        "password": "new_password"
                    })

            with it('responds with 400'):
                expect(self.response.status_code).to(equal(400))

            with it('responds with "Not a valid jwt token"'):
                expect(self.response.json).to(equal({'error': 'Not a valid jwt token'}))

        with description('expired jwt'):
            with before.each:
                self.user = UserFactory.create_user()
                self.response = self.context.client().put(
                    "/password_resets",
                    data={
                        "reset_token": expired_reset_password_token(self.user),
                        "password": "new_password"
                    })

            with it('responds with 400'):
                expect(self.response.status_code).to(equal(400))

            with it('responds with "Not enough segments"'):
                expect(self.response.json).to(equal({'error': 'Reset token expired'}))

        with description('expired jwt'):
            with before.each:
                self.user = UserFactory.create_user()
                self.response = self.context.client().put(
                    "/password_resets",
                    data={
                        "reset_token": expired_reset_password_token(self.user),
                        "password": "new_password"
                    })

            with it('responds with 400'):
                expect(self.response.status_code).to(equal(400))

            with it('responds with "Reset token expired"'):
                expect(self.response.json).to(equal({'error': 'Reset token expired'}))

        with description('already used jwt'):
            with before.each:
                self.user = UserFactory.create_user()
                token = reset_password_token(self.user)
                self.context.client().put(
                    "/password_resets",
                    data={
                        "reset_token": token,
                        "password": "new_password"
                    })
                self.response = self.context.client().put(
                    "/password_resets",
                    data={
                        "reset_token": token,
                        "password": "another_new_password"
                    })

            with it('responds with 400'):
                expect(self.response.status_code).to(equal(400))

            with it('responds with "Reset link can only be used once"'):
                expect(self.response.json).to(equal({'error': 'Reset link can only be used once'}))
