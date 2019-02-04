import uuid

from doublex import Mock
from doublex_expects import have_been_satisfied
from expects import expect, equal, be_none, be_a
from flask import current_app
from hamcrest import has_key, anything
from mamba import description, before, after, it, context
from py2neo import Node

from application.models.artifact import Artifact
from application.models.elastic_artifact import ElasticArtifact
from application.models.neo_artifact import NeoArtifact
from specs.factories.elasticsearch import es_get_response
from specs.models.custom_matcher import have_node
from specs.spec_helpers import Context

with description('Artifact Wrapper') as self:
    with before.each:
        self.context = Context()

    with after.each:
        current_app.graph.delete_all()
        if hasattr(self, 'context'):
            self.context.delete()

    with description("Initialize"):
        with before.each:
            self.artifact = Artifact(file_url='asdf', type='Image')

        with it('creates a neo artifact'):
            expect(self.artifact.neo).to_not(be_none)
            expect(self.artifact.neo).to(be_a(NeoArtifact))

        with it('creates an elastic artifact'):
            expect(self.artifact.elastic).to_not(be_none)
            expect(self.artifact.elastic).to(be_a(ElasticArtifact))

    with description("Save"):
        with context('without tags'):
            with before.each:
                self.artifact = Artifact(file_url='asdf', type='image')
                with Mock() as elastic_mock:
                    elastic_mock.index(index='artifact', doc_type='image', id=str(self.artifact.neo.id),
                                       body=anything())
                current_app.es = elastic_mock
                self.artifact.save()

            with it('saves it to Elasticsearch'):
                expect(current_app.es).to(have_been_satisfied)

            with it('saves it to Neo4j'):
                expect(current_app.graph).to(have_node(Node('NeoArtifact', url='asdf')))

        with context('with tags'):
            with before.each:
                self.artifact = Artifact(file_url='asdf', type='image', tags=['a', 's', 'd', 'f'])
                with Mock() as elastic_mock:
                    elastic_mock.index(index='artifact', doc_type='image', id=str(self.artifact.neo.id),
                                       body=has_key('tags'))
                current_app.es = elastic_mock
                self.artifact.save()

            with it('saves tags in Elasticsearch'):
                expect(current_app.es).to(have_been_satisfied)

            with it('saves tags in Neo4j'):
                expect(self.artifact.neo.tag_list()).to(equal(['a', 's', 'd', 'f']))

    with description('find'):
        with before.each:
            test_uuid = uuid.uuid4()
            with Mock() as elastic_mock:
                elastic_mock.get(index='artifact', doc_type='_all', id=str(test_uuid)).returns(es_get_response())
            current_app.es = elastic_mock
            self.artifact = Artifact.find(test_uuid, force=False)

        with it('searches in elasticsearch'):
            expect(current_app.es).to(have_been_satisfied)

    with description('update'):
        with context('file_url'):
            with before.each:
                self.artifact = Artifact(file_url='asdf', type='image')
                with Mock() as elastic_mock:
                    elastic_mock.index(index='artifact', doc_type='image', id=str(self.artifact.neo.id),
                                       body=anything())
                    elastic_mock.update(index='artifact', doc_type='image', id=str(self.artifact.neo.id),
                                        body=anything())
                current_app.es = elastic_mock
                self.artifact.save()
                self.artifact.update(file_url='blub')

            with it('updates in Elasticsearch'):
                expect(current_app.es).to(have_been_satisfied)

            with it('update in Neo4j'):
                expect(NeoArtifact.exists(url='blub')).to(equal(True))

        with context('tags'):
            with before.each:
                self.artifact = Artifact(file_url='asdf', type='image')
                with Mock() as elastic_mock:
                    elastic_mock.index(index='artifact', doc_type='image', id=str(self.artifact.neo.id),
                                       body=anything())
                    elastic_mock.update(index='artifact', doc_type='image', id=str(self.artifact.neo.id),
                                        body=anything())
                current_app.es = elastic_mock
                self.artifact.save()
                self.artifact.update(tags=['a', 's', 'd', 'f'])

            with it('updates in Elasticsearch'):
                expect(current_app.es).to(have_been_satisfied)

            with it('updates in Neo4j'):
                expect(self.artifact.neo.tag_list()).to(equal(['a', 's', 'd', 'f']))

        with context('label_annotations'):
            with before.each:
                self.artifact = Artifact(file_url='asdf', type='image')
                with Mock() as elastic_mock:
                    elastic_mock.index(index='artifact', doc_type='image', id=str(self.artifact.neo.id),
                                       body=anything())
                    elastic_mock.update(index='artifact', doc_type='image', id=str(self.artifact.neo.id),
                                        body=anything())
                current_app.es = elastic_mock
                self.artifact.save()
                self.artifact.update(label_annotations=['a', 's', 'd', 'f'])

            with it('updates in Elasticsearch'):
                expect(current_app.es).to(have_been_satisfied)

            with it('updates in Neo4j'):
                expect(self.artifact.neo.label_annotation_list()).to(equal(['a', 's', 'd', 'f']))

        with context('text_annotations'):
            with before.each:
                self.artifact = Artifact(file_url='asdf', type='image')
                with Mock() as elastic_mock:
                    elastic_mock.index(index='artifact', doc_type='image', id=str(self.artifact.neo.id),
                                       body=anything())
                    elastic_mock.update(index='artifact', doc_type='image', id=str(self.artifact.neo.id),
                                        body=anything())
                current_app.es = elastic_mock
                self.artifact.save()
                self.artifact.update(text_annotations=['a', 's', 'd', 'f'])

            with it('updates in Elasticsearch'):
                expect(current_app.es).to(have_been_satisfied)

            with it('updates in Neo4j'):
                expect(self.artifact.neo.text_annotation_list()).to(equal(['a', 's', 'd', 'f']))

    with description('delete'):
        with before.each:
            self.artifact = Artifact(file_url='asdf', type='image')
            with Mock() as elastic_mock:
                elastic_mock.index(index='artifact', doc_type='image', id=str(self.artifact.neo.id),
                                   body=anything())
                elastic_mock.delete(index='artifact', doc_type='image', id=str(self.artifact.neo.id),
                                    refresh='wait_for')
            current_app.es = elastic_mock
            self.artifact.save()
            self.artifact.delete()

        with it('deletes in Elasticsearch'):
            expect(current_app.es).to(have_been_satisfied)

        with it('deletes in Neo4j'):
            expect(len(NeoArtifact.all())).to(equal(0))
