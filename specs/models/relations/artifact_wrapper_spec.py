""" Test the ArtifactBuilder class. Currently it's more of a wrapper than a builder sadly
    #refactor soon"""
from doublex import Mock
from doublex_expects import have_been_satisfied
from expects import expect, be_none, be_a, equal, contain
from flask import current_app
from hamcrest import has_key, anything
from mamba import description, before, after, it, context
from neomodel import db

from application.models.artifact import Artifact
from application.models.artifact_builder import ArtifactBuilder
from application.models.elastic_artifact import ElasticArtifact
from specs.factories.elasticsearch import es_get_response
from specs.spec_helpers import Context

with description('Artifact Wrapper') as self:
    with before.each:
        self.context = Context()

    with after.each:
        db.cypher_query("MATCH (a) DETACH DELETE a")
        if hasattr(self, 'context'):
            self.context.delete()

    with description("Building"):
        with before.each:
            self.artifact = ArtifactBuilder()
            self.artifact.build_with(file_url='asdf', type='image')

        with it('creates an elastic artifact'):
            expect(self.artifact.elastic).to_not(be_none)
            expect(self.artifact.elastic).to(be_a(ElasticArtifact))

        with it('creates a neo artifact'):
            expect(self.artifact.neo).to_not(be_none)
            expect(self.artifact.neo).to(be_a(Artifact))

    with description("Save"):
        with context('without tags'):
            with before.each:
                self.artifact = ArtifactBuilder()
                self.artifact.build_with(file_url='asdf', type='image')

                with Mock() as elastic_mock:
                    elastic_mock.index(index='artifact', doc_type='image', id=anything(),
                                       body=anything())
                current_app.es = elastic_mock
                self.artifact.save()

            with it('saves it to Elasticsearch'):
                expect(current_app.es).to(have_been_satisfied)

            with it('saves it to neo4j'):
                expect(Artifact.exists(file_url='asdf')).to(equal(True))

        with context('with tags'):
            with before.each:
                self.artifact = ArtifactBuilder()
                self.artifact.build_with(file_url='asdf', type='image', tags=['a', 's', 'd', 'f'])
                with Mock() as elastic_mock:
                    elastic_mock.index(index='artifact', doc_type='image', id=anything(),
                                       body=has_key('tags'))
                current_app.es = elastic_mock
                self.artifact.save()

            with it('saves tags in Elasticsearch'):
                expect(current_app.es).to(have_been_satisfied)

            with it('saves tags in Neo4j'):
                expect(self.artifact.neo.tags_list).to(contain('a', 's', 'd', 'f'))

    with description('find'):
        with before.each:
            self.artifact = ArtifactBuilder()
            self.artifact.build_with(file_url='asdf', type='image')
            ARTIFACT_ID = self.artifact.neo.id_
            with Mock() as elastic_mock:
                elastic_mock.get(index='artifact', doc_type='_all',
                                 id=anything()).returns(es_get_response(0))
            current_app.es = elastic_mock
            self.artifact = ArtifactBuilder.find(id=ARTIFACT_ID, force=False)

        with it('searches in elasticsearch'):
            expect(current_app.es).to(have_been_satisfied)

        with it('finds in neo4j'):
            expect(self.artifact.neo.file_url).to(equal('asdf'))

    with description('update'):
        with context('file_url'):
            with before.each:
                self.artifact = ArtifactBuilder()
                self.artifact.build_with(file_url='asdf', type='image')
                with Mock() as elastic_mock:
                    elastic_mock.index(index='artifact', doc_type='image', id=anything(),
                                       body=anything())
                    elastic_mock.update(index='artifact', doc_type='image', id=anything(),
                                        body=anything())
                current_app.es = elastic_mock
                self.artifact.save()
                self.artifact.update(file_url='blub')

            with it('updates in Elasticsearch'):
                expect(current_app.es).to(have_been_satisfied)

            with it('updates in neo4j'):
                expect(Artifact.exists(file_url='blub')).to(equal(True))
                expect(Artifact.exists(file_url='asdf')).to(equal(False))

        with context('tags'):
            with before.each:
                self.artifact = ArtifactBuilder()
                self.artifact.build_with(file_url='asdf', type='image')
                with Mock() as elastic_mock:
                    elastic_mock.index(index='artifact', doc_type='image', id=anything(),
                                       body=anything())
                    elastic_mock.update(index='artifact', doc_type='image', id=anything(),
                                        body=anything())
                current_app.es = elastic_mock
                self.artifact.save()
                self.artifact.update(tags=['a', 's', 'd', 'f'])

            with it('updates in Elasticsearch'):
                expect(current_app.es).to(have_been_satisfied)

            with it('updates in neo4j'):
                ARTIFACT = Artifact.find_by(file_url='asdf')
                expect(ARTIFACT.tags_list).to(contain('a', 's', 'd', 'f'))

            with context('updating again'):
                with before.each:
                    with Mock() as elastic_mock:
                        elastic_mock.update(index='artifact', doc_type='image', id=anything(),
                                            body=anything())
                    current_app.es = elastic_mock
                    self.artifact.update(tags=['l', 'm', 'a', 'o'])

                with it('saves new tags in elasticsearch'):
                    expect(current_app.es).to(have_been_satisfied)

                with it('saves new tags in neo4j'):
                    ARTIFACT = Artifact.find_by(file_url='asdf')
                    expect(ARTIFACT.tags_list).to(contain('a', 's', 'd', 'f', 'l', 'm', 'a', 'o'))

    with description('delete'):
        with before.each:
            self.artifact = ArtifactBuilder()
            self.artifact.build_with(file_url='asdf', type='image')
            with Mock() as elastic_mock:
                elastic_mock.index(index='artifact', doc_type='image', id=anything(),
                                   body=anything())
                elastic_mock.delete(index='artifact', doc_type='image', id=anything(),
                                    refresh='wait_for')
            current_app.es = elastic_mock
            self.artifact.save()
            self.artifact.delete()

        with it('deletes in Elasticsearch'):
            expect(current_app.es).to(have_been_satisfied)

        with it('deletes in neo4j'):
            expect(Artifact.exists(file_url='asdf')).to(equal(False))
