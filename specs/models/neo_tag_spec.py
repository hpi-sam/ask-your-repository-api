from mamba import description, before, after, it, context
from expects import expect, equal
from application.models.neo_tag import NeoTag
from specs.spec_helpers import Context
from specs.models.custom_matcher import be_uuid, have_node, have_relationship
from flask import current_app
from py2neo import Node

node_name = "NeoArtifact"
with description('NeoArtifact') as self:
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
