from application.models.elastic import ElasticSyncer

from expects import expect, equal, be_a, raise_error, contain_only, contain
from mamba import describe, it, before, after, context
from neomodel import db
from doublex import Mock
from doublex_expects import have_been_satisfied
from flask import current_app

from hamcrest import anything

from application.models import Artifact
from specs.spec_helpers import Context
from specs.factories.elasticsearch import es_get_response
from elasticsearch import NotFoundError

with describe('ElasticSyncer') as self:
    with before.each:
        self.context = Context()

    with after.each:
        db.cypher_query("MATCH (a) DETACH DELETE a")
        if hasattr(self, 'context'):
            self.context.delete()
        ElasticSyncer.sync_disabled=True

    with describe('calling sync'):
        with context('a simple artifact'):
            with context('when artifact does not exist yet'):
                with before.each:
                    self.artifact = Artifact(file_url='asdf').save()
                    ElasticSyncer.sync_disabled = False
                    self.syncer = ElasticSyncer.for_artifact(self.artifact)
                    with Mock() as elastic_mock:
                        elastic_mock.get(doc_type=anything(), id=self.artifact.id_,
                                         index='artifact').raises(NotFoundError)
                        elastic_mock.index(body=anything(), doc_type=anything(),
                                           id=anything(), index='artifact')
                    current_app.es = elastic_mock
                    self.syncer.sync()

                with it('syncs'):
                    expect(current_app.es).to(have_been_satisfied)

            with context('when artifact exists already'):
                with before.each:
                    self.artifact = Artifact(file_url='asdf').save()
                    ElasticSyncer.sync_disabled = False
                    self.syncer = ElasticSyncer.for_artifact(self.artifact)
                    with Mock() as elastic_mock:
                        elastic_mock.get(doc_type=anything(), id=self.artifact.id_,
                                         index='artifact').returns(es_get_response(0))
                        elastic_mock.update(body=anything(), doc_type=anything(),
                                           id=anything(), index='artifact')
                    current_app.es = elastic_mock
                    self.syncer.sync()

                with it('syncs'):
                    expect(current_app.es).to(have_been_satisfied)

    with describe('calling delete'):
        with context('a simple artifact'):
            with context('artifact exists'):
                with before.each:
                    self.artifact = Artifact(file_url='asdf').save()
                    ElasticSyncer.sync_disabled = False
                    self.syncer = ElasticSyncer.for_artifact(self.artifact)
                    with Mock() as elastic_mock:
                        elastic_mock.get(doc_type=anything(), id=self.artifact.id_,
                                         index='artifact').returns(es_get_response(0))
                        elastic_mock.delete(doc_type=anything(), id=anything(),
                                            index='artifact', refresh='wait_for')
                    current_app.es = elastic_mock
                    self.syncer.delete()

                with it('deletes'):
                    expect(current_app.es).to(have_been_satisfied)

            with context('artifact does not exist'):
                with before.each:
                    self.artifact = Artifact(file_url='asdf').save()
                    ElasticSyncer.sync_disabled = False
                    self.syncer = ElasticSyncer.for_artifact(self.artifact)
                    with Mock() as elastic_mock:
                        elastic_mock.get(doc_type=anything(), id=self.artifact.id_,
                                         index='artifact').raises(NotFoundError)
                    current_app.es = elastic_mock
                    self.syncer.delete()

                with it('doesnt crash'):
                    expect(current_app.es).to(have_been_satisfied)
