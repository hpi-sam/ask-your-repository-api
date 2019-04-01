import sys
import uuid

from expects import expect, have_key, equal
from mamba import description, before, after, it
from neomodel import db

from application.users.user import User
from specs.factories.google_oauth_factory import GoogleOAuthFactory, google_user_data
from specs.factories.google_oauth_mocks import google_auth_patch, google_client_id_patch_load, \
    google_client_id_patch_open
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

        with description('with google id_token'):
            with google_client_id_patch_load, google_client_id_patch_open:
                with description('with existing user'):
                    with before.each:
                        google_oauth = GoogleOAuthFactory.create_google_oauth()
                        self.user.google_rel.connect(google_oauth)
                        with google_auth_patch, google_client_id_patch_load, \
                             google_client_id_patch_open:
                            self.response = self.context.client().post(
                                '/authentications',
                                data={'id_token': 'test_id_token'})

                    with it('responds with 200'):
                        expect(self.response.status_code).to(equal(200))

                    with it('returns the user with token'):
                        expect(self.response.json).to(have_key('username', self.user.username))
                        expect(self.response.json).to(have_key('email', self.user.email))
                        expect(self.response.json).to(
                            have_key('id', uuid.UUID(self.user.id_).urn[9:]))
                        expect(self.response.json).to(have_key('token'))

                    with it('returns has_password: True'):
                        expect(self.response.json).to(have_key('has_password', True))

                    with it('returns the user with google auth'):
                        expect(self.response.json).to(have_key('google', {
                            'user_id': google_user_data['sub'],
                            'has_offline_access': False
                        }))

                with description('with new user'):
                    with before.each:
                        with google_auth_patch, google_client_id_patch_load, \
                         google_client_id_patch_open:
                            self.response = self.context.client().post(
                                '/authentications',
                                data={'id_token': 'test_id_token'})

                    with it('responds with 200'):
                        expect(self.response.status_code).to(equal(200))

                    with it('returns the user with token'):
                        expect(self.response.json).to(
                            have_key('username', google_user_data['email']))
                        expect(self.response.json).to(have_key('email', google_user_data['email']))
                        expect(self.response.json).to(have_key('token'))

                    with it('returns has_password: True'):
                        expect(self.response.json).to(have_key('has_password', False))

                    with it('returns the user with google auth'):
                        expect(self.response.json).to(have_key('google', {
                            'user_id': google_user_data['sub'],
                            'has_offline_access': False
                        }))

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

        with description('with password missing'):
            with before.each:
                self.response = self.context.client().post(
                    '/authentications',
                    data={'email_or_username': 'TestUser'})

            with it('responds with 422'):
                expect(self.response.status_code).to(equal(422))

            with it('returns an error message'):
                expect(self.response.json).to(equal({'errors': {
                    'password': ['missing value for required field']}}))

        with description('with no params missing'):
            with before.each:
                self.response = self.context.client().post(
                    '/authentications')

            with it('responds with 422'):
                expect(self.response.status_code).to(equal(422))

            with it('returns an error message'):
                expect(self.response.json).to(equal({'errors': {
                    'login_params': ['id_token or email_or_username missing']}}))

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
                expect(self.response.json).to(
                    equal({'msg': 'Missing cookie "access_token_cookie"'}))
