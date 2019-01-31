from expects import expect, equal
from flask import current_app
from mamba import description, before, after, it
from py2neo import Node

from application.models.neo_tag import NeoTag
from specs.models.custom_matcher import have_node
from specs.spec_helpers import Context

with description('NeoTag') as self:
    with before.each:
        self.context = Context()

    with after.each:
        pass
        current_app.graph.delete_all()

    with description('Constructing'):
        with it('creates a TagNode'):
            self.tag = NeoTag(name='asdf')
            self.tag.save()
            expect(current_app.graph).to(have_node(Node("NeoTag", name='asdf')))

        with it('creates tags with same name only once'):
            self.tag1 = NeoTag.find_or_create_by(name='lmao')
            self.tag1.save()
            self.tag2 = NeoTag.find_or_create_by(name='lmao')
            self.tag2.save()
            expect(self.tag1.id).to(equal(self.tag2.id))
