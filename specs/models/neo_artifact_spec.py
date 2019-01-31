from expects import expect, equal
from flask import current_app
from mamba import description, before, after, it, context
from py2neo import Node

from application.models.neo_artifact import NeoArtifact
from application.models.neo_tag import NeoTag
from specs.models.custom_matcher import be_uuid, have_node, have_relationship
from specs.spec_helpers import Context

node_name = "NeoArtifact"
with description('NeoArtifact') as self:
    with before.each:
        self.context = Context()

    with after.each:
        current_app.graph.delete_all()
        self.context.delete()

    with description('Constructing'):
        with context('with Default Constructor'):
            with before.each:
                self.artifact = NeoArtifact()
            with it('has a uuid'):
                expect(self.artifact.id).to(be_uuid())
            with it('has an empty url'):
                expect(self.artifact.url).to(equal(''))

        with context('with a custom url'):
            with before.each:
                self.artifact = NeoArtifact(url='https://i.redd.it/dsv32vpi0m821.jpg')
            with it('has an url'):
                expect(self.artifact.url).to(equal('https://i.redd.it/dsv32vpi0m821.jpg'))

    with description('saving'):
        with context('Creating new node'):
            with before.each:
                self.artifact = NeoArtifact(url='https://i.redd.it/dsv32vpi0m821.jpg')
                self.artifact.save()
            with it('creates a new node'):
                expect(current_app.graph).to(have_node(Node(node_name, url='https://i.redd.it/dsv32vpi0m821.jpg')))

        with context('Changing existing node'):
            with before.each:
                self.artifact = NeoArtifact(url='https://i.redd.it/dsv32vpi0m821.jpg')
                self.artifact.save()
                self.artifact.url = 'https://imgur.com/dMlIoZL'
                self.artifact.save()

            with it('saves new data in same node'):
                expect(current_app.graph).to(have_node(Node(node_name, url="https://imgur.com/dMlIoZL")))
                expect(current_app.graph).not_to(have_node(Node(node_name, url='https://i.redd.it/dsv32vpi0m821.jpg')))

    with description('tags'):
        with context('tag list'):
            with it('returns list of tag names as array'):
                artifact = NeoArtifact(url='https://i.redd.it/dsv32vpi0m821.jpg')
                artifact.tags.add(NeoTag(name='reddit'))
                expect(artifact.tag_list()).to(equal(['reddit']))

        with it('are empty at the start'):
            artifact = NeoArtifact(url='https://i.redd.it/dsv32vpi0m821.jpg')
            expect(list(artifact.tags)).to(equal([]))

        with it('can be added'):
            artifact = NeoArtifact(url='https://i.redd.it/dsv32vpi0m821.jpg')
            tag = NeoTag(name='reddit')
            artifact.tags.add(tag)
            expect(list(artifact.tags)).to(equal([tag]))

        with it('will be saved'):
            artifact = NeoArtifact(url='https://i.redd.it/dsv32vpi0m821.jpg')
            tag = NeoTag(name='reddit')
            artifact.tags.add(tag)
            artifact.save()
            expect(NeoTag.exists(name='reddit')).to(equal(True))

        with it('saves a relationship'):
            artifact = NeoArtifact(url='https://i.redd.it/dsv32vpi0m821.jpg')
            tag = NeoTag(name='reddit')
            artifact.tags.add(tag)
            artifact.save()
            expect(current_app.graph).to(have_relationship(artifact.__node__, 'TAGGED_WITH', tag.__node__))

        with it('can be accessed after reload'):
            artifact = NeoArtifact(url='https://i.redd.it/dsv32vpi0m821.jpg')
            tag = NeoTag(name='reddit')
            artifact.tags.add(tag)
            artifact.save()
            reloaded_artifact = NeoArtifact.find_by(url='https://i.redd.it/dsv32vpi0m821.jpg')
            expect(list(reloaded_artifact.tags)).to(equal([tag]))
