from flask import current_app
from mamba import description, before, after, it, context
from expects import expect, equal, raise_error
import uuid
from doublex import Mock, Stub, ANY_ARG
from application.models.team import Team
from specs.spec_helpers import Context
from specs.models.custom_matcher import be_uuid, have_node
from flask import current_app
from py2neo import Node, NodeMatcher
from application.errors import NotFound

with description('Team') as self:
    with before.each:
        self.context = Context()

    with after.each:
        current_app.graph.delete_all()

    with description('Constructing'):
        with context('with Default Constructor'):
            with before.each:
                self.team = Team(name='Blue')
            with it('has a name'):
                expect(self.team.name).to(equal('Blue'))
            with it('has a uuid'):
                expect(self.team.id_).to(be_uuid())

        with context('with Constructor with an id'):
            with before.each:
                self.blues_id = uuid.uuid4()
                self.team = Team(name='Blue', id_=str(self.blues_id))
            with it('sets the id'):
                expect(self.team.id_).to(equal(self.blues_id))

    with description('saving'):
        with context('Creating new node'):
            with before.each:
                self.team = Team(name='Blue')
                self.team.save()
            with it('creates a new node'):
                expect(current_app.graph).to(have_node(Node("Team", name='Blue')))

        with context('Changing existing node'):
            with before.each:
                self.team = Team(name='Blue')
                self.team.save()
                self.team.name='Red'
                self.team.save()

            with it('saves new data in same node'):
                expect(current_app.graph).to(have_node(Node("Team", name="Red")))
                expect(current_app.graph).not_to(have_node(Node("Team", name="Blue")))

    with description('List Teams'):
        with before.each:
            Team(name='Blue').save()
            Team(name='Red').save()
            self.teams = Team.all()

        with it('returns list of 2'):
            expect(len(self.teams)).to(equal(2))

        with it('returns Team object list'):
            expect(self.teams[0].name).to(equal('Blue') | equal('Red'))
            expect(self.teams[1].name).to(equal('Red') | equal('Blue'))

    with description('Finding teams'):
        with before.each:
            self.blue = Team(name='Blue')
            self.blue.save()
            self.red = Team(name='Red')
            self.red.save()

        with context('Finding Team by name'):
            with before.each:
                self.found_red = Team.find_by(name='Red')
                self.found_blue = Team.find_by(name='Blue')

            with it('finds blue'):
                expect(self.found_blue.name).to(equal(self.blue.name))
                expect(self.found_blue.id_).to(equal(self.blue.id_))

            with it('finds red'):
                expect(self.found_red.name).to(equal(self.red.name))
                expect(self.found_red.id_).to(equal(self.red.id_))

        with context('Finding Team by id'):
            with before.each:
                self.found_red = Team.find_by(id_=str(self.red.id_))
                self.found_blue = Team.find_by(id_=str(self.blue.id_))

            with it('finds blue'):
                expect(self.found_blue.name).to(equal(self.blue.name))
                expect(self.found_blue.id_).to(equal(self.blue.id_))

            with it('finds red'):
                expect(self.found_red.name).to(equal(self.red.name))
                expect(self.found_red.id_).to(equal(self.red.id_))

        with description('Not Found'):
            with it('returns None with force false'):
                expect(Team.find_by(name='asdf')).to(equal(None))
            with it('throws exception with force true'):
                expect(lambda: Team.find_by(name='asdf', force=True)).to(raise_error(NotFound))

    with description('exists'):
        with before.each:
            Team(name='Blue').save()

        with it('Returns true if team exists'):
            expect(Team.exists(name='Blue')).to(equal(True))

        with it('Returns false if team does not exist'):
            expect(Team.exists(name='Red')).to(equal(False))

    with description('create'):
        with before.each:
            self.team = Team.create(name='Blue')

        with it('creates new node'):
            expect(current_app.graph).to(have_node(Node("Team", name='Blue')))

    with description('update'):
        with before.each:
            self.team = Team.create(name="Blue")
            self.team.update(name="Red")

        with it('saves new attributes'):
            expect(Team.exists(name="Red")).to(equal(True))
            expect(Team.exists(name="Blue")).to(equal(False))

    with description('delete'):
        with before.each:
            self.team = Team.create("Blue")
            self.team.delete()

        with it('deletes team'):
            expect(Team.exists(name='Blue')).to(equal(False))
