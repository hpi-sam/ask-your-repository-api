import sys
import uuid

from expects import expect, have_key, have_len, contain_only, equal, be, be_empty
from mamba import description, before, after, it
from neomodel import db

from application.models.user import User
from specs.spec_helpers import Context

sys.path.insert(0, 'specs')

with description('/users') as self:
    with before.each:
        self.context = Context()

    with after.each:
        db.cypher_query('MATCH (a) DETACH DELETE a')
        pass

    with description('GET'):
        with before.each:
            User(username='TestUser', email='test@example.com', password='test').save()
            User(username='TestUser2', email='test2@example.com', password='test').save()
            self.context.client().login('TestUser', 'test')
            self.response = self.context.client().get('/users')

        with it('responds with all users'):
            expect(self.response.json).to(have_key('users'))
            expect(self.response.json['users']).to(have_len(2))
            expect(self.response.json['users']).to(contain_only(
                have_key('username', 'TestUser'),
                have_key('username', 'TestUser2')
            ))

    with description('POST'):
        with description('valid request'):
            with before.each:
                self.response = self.context.client().post(
                    '/users',
                    data={'username': 'My User', 'email': 'test@example.com', 'password': 'test'})

            with it('responds with 200'):
                expect(self.response.status_code).to(equal(200))

            with it('responds with correct user'):
                expect(self.response.json).to(have_key('username', 'My User'))
                expect(self.response.json).to(have_key('email', 'test@example.com'))
                expect(self.response.json).to(have_key('id'))

            with it('does not return the password'):
                expect(self.response.json).not_to(have_key('password'))

            with it('saves the user'):
                expect(User.nodes.get_or_none(id_=self.response.json['id'],
                                              username='My User',
                                              email='test@example.com')
                      ).to_not(be(None))

        with description('invalid request'):
            with before.each:
                self.response = self.context.client().post(
                    '/users',
                    data={'username': ''})

            with it('declines empty name'):
                expect(self.response.status_code).to(equal(422))

            with it('does not save invalid users'):
                expect(User.nodes).to(be_empty)

    with description('/:id'):
        with description('GET'):
            with description('valid id'):
                with before.each:
                    self.user = User(username='TestUser',
                                     email='test@example.com',
                                     password='test').save()
                    self.context.client().login('TestUser', 'test')
                    self.response = self.context.client().get(f'/users/{self.user.id_}')

                with it('responds with 200'):
                    expect(self.response.status_code).to(equal(200))

                with it('responds with the correct user'):
                    expect(self.response.json).to(have_key('username', 'TestUser'))
                    expect(self.response.json).to(have_key('email', 'test@example.com'))
                    expect(self.response.json).to(have_key('id', uuid.UUID(self.user.id_).urn[9:]))

                with it('does not return the password'):
                    expect(self.response.json).not_to(have_key('password'))

            with description('invalid id'):
                with before.each:
                    # Creating but not saving user so that id is invalid
                    user = User(username='TestUser',
                                email='test@example.com',
                                password='test')
                    User(username='AdminUser',
                         email='test@example.com',
                         password='test').save()
                    self.context.client().login('AdminUser', 'test')
                    self.response = self.context.client().get(f'/users/{user.id_}')

                with it('responds error 404'):
                    expect(self.response.status_code).to(equal(404))

        with description('PUT'):
            with description('valid id'):
                with before.each:
                    self.user = User(username='TestUser',
                                     email='test@example.com',
                                     password='test').save()

                    self.context.client().login('TestUser', 'test')
                    self.response = self.context.client().put(
                        f'/users/{self.user.id_}',
                        data={'username': 'AnotherUser'})

                with it('responds with 200'):
                    expect(self.response.status_code).to(equal(200))

                with it('responds with the updated user'):
                    expect(self.response.json).to(have_key('username', 'AnotherUser'))
                    expect(self.response.json).to(have_key('email', 'test@example.com'))
                    expect(self.response.json).to(have_key('id', uuid.UUID(self.user.id_).urn[9:]))

                with it('does not return password'):
                    expect(self.response.json).not_to(have_key('password'))

                with description('User object'):
                    with before.each:
                        self.fresh_user = User.nodes.get(id_=self.user.id_)

                    with it('is updated correctly'):
                        expect(self.fresh_user.username).to(equal('AnotherUser'))

            with description('invalid id'):
                with before.each:
                    user = User(username='TestUser',
                                email='test@example.com',
                                password='test').save()
                    user.delete()
                    User(username='AdminUser',
                         email='test@example.com',
                         password='test').save()
                    self.context.client().login('AdminUser', 'test')
                    self.response = self.context.client().put(
                        f'/users/{user.id_}',
                        data={'username': 'AntotherUser'})

                with it('responds error 404'):
                    expect(self.response.status_code).to(equal(404))

            with description('invalid request'):
                with before.each:
                    user = User(username='TestUser',
                                email='test@example.com',
                                password='test').save()
                    self.context.client().login('TestUser', 'test')
                    self.response = self.context.client().put(
                        f'/users/{user.id_}',
                        data={'username': ''})

                with it('responds with 422 invalid request'):
                    expect(self.response.status_code).to(equal(422))
