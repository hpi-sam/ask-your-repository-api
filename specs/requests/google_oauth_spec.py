import sys
from expects import expect, have_key, have_len, contain_only, equal, be, be_empty
from mamba import description, before, after, it
from neomodel import db

from application.users.user import User
from specs.factories.user_factory import UserFactory, google_auth_patch, \
    google_flow_patch, google_user_data, google_credentials_patch, google_credentials, google_revoke_access_patch
from specs.spec_helpers import Context

sys.path.insert(0, 'specs')

with description('/users/<id>/oauth_providers/google') as self:
    with before.each:
        self.context = Context()

    with after.each:
        db.cypher_query('MATCH (a) DETACH DELETE a')
        pass

    with description('PUT'):
        with description('valid id_token'):
            with before.each:
                user = UserFactory.create_user(username='TestUser2', email='test2@example.com')
                self.context.client().login(user)
                with google_auth_patch:
                    self.response = self.context.client().put(
                        f'/users/{user.id_}/oauths/google',
                        data={'id_token': 'test_id_token'})

            with it('responds with 200'):
                expect(self.response.status_code).to(equal(200))

            with it('responds with a user that includes google credentials'):
                expect(self.response.json).to(
                    have_key('google',
                             {'has_offline_access': False, 'user_id': google_user_data['sub']}))

    with description('PATCH'):
        with description('valid auth_code'):
            with before.each:
                user = UserFactory.create_user_with_google(username='TestUser2', email='test2@example.com')
                self.context.client().login(user)
                with google_flow_patch, google_credentials_patch:
                    self.response = self.context.client().patch(
                        f'/users/{user.id_}/oauths/google',
                        data={'auth_code': 'test_auth_code'})

            with it('responds with 200'):
                expect(self.response.status_code).to(equal(200))

            with it('responds with a user that includes google credentials'):
                expect(self.response.json).to(
                    have_key('google',
                             {'has_offline_access': True, 'user_id': google_user_data['sub']}))

        with description('google not connected'):
            with before.each:
                user = UserFactory.create_user(username='TestUser2', email='test2@example.com')
                self.context.client().login(user)
                with google_flow_patch, google_credentials_patch:
                    self.response = self.context.client().patch(
                        f'/users/{user.id_}/oauths/google',
                        data={'auth_code': 'test_auth_code'})

            with it('responds with 404'):
                expect(self.response.status_code).to(equal(404))

            with it('responds with google oauth not found'):
                expect(self.response.json).to(
                    have_key('error', 'google oauth not found'))

    with description('/scopes DELETE'):
        with description('valid auth_code'):
            with before.each:
                user = UserFactory.create_user_with_google(username='TestUser2', email='test2@example.com')
                google = user.google
                google.credentials = google_credentials
                google.save()
                with google_credentials_patch:
                    self.context.client().login(user)
                with google_revoke_access_patch(status_code=200), google_credentials_patch:
                    self.response = self.context.client().delete(
                        f'/users/{user.id_}/oauths/google/scopes')

            with it('responds with 200'):
                expect(self.response.status_code).to(equal(200))

            with it('responds with a user that includes google credentials'):
                expect(self.response.json).to(
                    have_key('google',
                             {'has_offline_access': False, 'user_id': google_user_data['sub']}))

        with description('google provider not connected'):
            with before.each:
                user = UserFactory.create_user(username='TestUser2', email='test2@example.com')
                self.context.client().login(user)
                with google_credentials_patch:
                    self.response = self.context.client().delete(
                        f'/users/{user.id_}/oauths/google/scopes')

            with it('responds with 404'):
                expect(self.response.status_code).to(equal(404))

            with it('responds with google oauth not found'):
                expect(self.response.json).to(
                    have_key('error', 'google oauth not found'))

        with description('google request access error'):
            with before.each:
                user = UserFactory.create_user_with_google(username='TestUser2', email='test2@example.com')
                google = user.google
                google.credentials = google_credentials
                google.save()
                with google_credentials_patch:
                    self.context.client().login(user)
                with google_revoke_access_patch(status_code=400), google_credentials_patch:
                    self.response = self.context.client().delete(
                        f'/users/{user.id_}/oauths/google/scopes')

            with it('responds with 502'):
                expect(self.response.status_code).to(equal(502))

            with it('responds with could not revoke access'):
                expect(self.response.json).to(
                    have_key('error', 'could not revoke access'))
