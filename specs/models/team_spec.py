from flask import current_app
from mamba import description, before, after, it, context
from expects import expect, equal, raise_error
from doublex import Mock, Stub, ANY_ARG
from application.models.team import Team
from specs.spec_helpers import Context
from specs.models.custom_matcher import be_uuid, have_node
from flask import current_app
from py2neo import Node, NodeMatcher

with description('Team') as self:
    with before.each:
        self.context = Context()

    with description('Constructor'):
        with context('Default'):
            with before.each:
                self.team = Team(name='Blue')
            with it('has a name'):
                expect(self.team.name).to(equal('Blue'))
            with it('has a uuid'):
                expect(self.team.id_).to(be_uuid())
        with context('with id'):
            with before.each:
                self.team = Team(name='Blue', id_='asdf')
            with it('sets the id'):
                expect(self.team.id_).to(equal('asdf'))

    with description('saving'):
        with context('Node doesn\'t exist yet'):
            with before.each:
                self.team = Team(name='Blue')
                self.team.save()
            with it('creates a new node'):
                expect(current_app.graph).to(have_node(Node("Team", name='Blue')))
