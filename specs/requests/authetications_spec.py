import sys
import uuid

from expects import expect, have_key, equal
from mamba import description, before, after, it
from neomodel import db

from application.users.user import User
from specs.spec_helpers import Context

sys.path.insert(0, 'specs')

with description('/authentications') as self:
    with before.each:
        self.context = Context()

    with after.each:
        db.cypher_query('MATCH (a) DETACH DELETE a')
        pass

    with description('POST or login'):
        with before.each:
            self.user = User(username='TestUser',
                             email='test@example.com',
                             password='test').save()

        with description('with email and password'):
            with before.each:
                self.response = self.context.client().post(
                    '/authentications',
                    data={'email_or_username': 'test@example.com', 'password': 'test'})

            with it('responds with 200'):
                expect(self.response.status_code).to(equal(200))

            with it('returns the user with token'):
                expect(self.response.json).to(have_key('username', 'TestUser'))
                expect(self.response.json).to(have_key('email', 'test@example.com'))
                expect(self.response.json).to(have_key('id', uuid.UUID(self.user.id_).urn[9:]))
                expect(self.response.json).to(have_key('token'))

        with description('with username and password'):
            with before.each:
                self.response = self.context.client().post(
                    '/authentications',
                    data={'email_or_username': 'TestUser', 'password': 'test'})

            with it('responds with 200'):
                expect(self.response.status_code).to(equal(200))

            with it('returns the user with token'):
                expect(self.response.json).to(have_key('username', 'TestUser'))
                expect(self.response.json).to(have_key('email', 'test@example.com'))
                expect(self.response.json).to(have_key('id', uuid.UUID(self.user.id_).urn[9:]))
                expect(self.response.json).to(have_key('token'))

        with description('with invalid username or email'):
            with before.each:
                self.response = self.context.client().post(
                    '/authentications',
                    data={'email_or_username': 'WrongUsername', 'password': 'test'})

            with it('responds with 401'):
                expect(self.response.status_code).to(equal(401))

            with it('returns an error message'):
                expect(self.response.json).to(equal({"error": "Bad username or password"}))

        with description('with invalid password'):
            with before.each:
                self.response = self.context.client().post(
                    '/authentications',
                    data={'email_or_username': 'TestUser', 'password': 'wrong_password'})

            with it('responds with 401'):
                expect(self.response.status_code).to(equal(401))

            with it('returns an error message'):
                expect(self.response.json).to(equal({"error": "Bad username or password"}))

    with description('DELETE or logout'):
        with description('when logged in'):
            with before.each:
                User(username='TestUser',
                     email='test@example.com',
                     password='test').save()
                user_response = self.context.client().post('/authentications',
                                          data={'email_or_username': 'TestUser',
                                                'password': 'test'})
                token = user_response.json["token"]

                self.response = self.context.client().delete(
                    '/authentications',
                    headers={'X-CSRF-TOKEN': token})
            with it('responds with 200'):
                expect(self.response.status_code).to(equal(200))

            with it('returns logged out json'):
                expect(self.response.json).to(equal({"logout": True}))

        with description('without being logged in'):
            with before.each:
                self.response = self.context.client().delete(
                    '/authentications')

            with it('responds with 401'):
                expect(self.response.status_code).to(equal(401))

            with it('returns message not allowed'):
                expect(self.response.json).to(equal({'msg': 'Missing cookie "access_token_cookie"'}))
