from doublex import Mock
from doublex_expects import have_been_satisfied
from elasticsearch import NotFoundError
from expects import expect
from flask import current_app
from hamcrest import anything
from mamba import describe, it, before, after, context
from neomodel import db

from application.models import Artifact
from application.models.elastic import ElasticSyncer
from specs.factories.elasticsearch import es_get_response
from specs.spec_helpers import Context

OFF = False
ON = True

with describe('ElasticSyncer') as self:
    with before.each:
        self.context = Context()

    with after.each:
        db.cypher_query("MATCH (a) DETACH DELETE a")
        ElasticSyncer.set_sync_status(OFF)
        if hasattr(self, 'context'):
            self.context.delete()

    with describe('calling sync'):
        with context('a simple artifact'):
            with context('when artifact does not exist yet'):
                with before.each:
                    self.artifact = Artifact(file_url='asdf').save()
                    ElasticSyncer.set_sync_status(ON)
                    self.syncer = ElasticSyncer.for_artifact(self.artifact)
                    with Mock() as elastic_mock:
                        elastic_mock.update(doc_type=anything(), id=self.artifact.id_,
                                            index='artifact', body=anything()).raises(NotFoundError)
                        elastic_mock.index(body=anything(), doc_type=anything(),
                                           id=anything(), index='artifact')
                    current_app.es = elastic_mock
                    self.syncer.sync()

                with it('syncs'):
                    expect(current_app.es).to(have_been_satisfied)

            with context('when artifact exists already'):
                with before.each:
                    self.artifact = Artifact(file_url='asdf').save()
                    ElasticSyncer.set_sync_status(ON)
                    self.syncer = ElasticSyncer.for_artifact(self.artifact)
                    with Mock() as elastic_mock:
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
                    ElasticSyncer.set_sync_status(ON)
                    self.syncer = ElasticSyncer.for_artifact(self.artifact)
                    with Mock() as elastic_mock:
                        elastic_mock.delete(doc_type=anything(), id=anything(),
                                            index='artifact', refresh='wait_for').raises(NotFoundError)
                    current_app.es = elastic_mock
                    self.syncer.delete()

                with it('deletes'):
                    expect(current_app.es).to(have_been_satisfied)

            with context('artifact does not exist'):
                with before.each:
                    self.artifact = Artifact(file_url='asdf').save()
                    ElasticSyncer.set_sync_status(ON)
                    self.syncer = ElasticSyncer.for_artifact(self.artifact)
                    with Mock() as elastic_mock:
                        elastic_mock.delete(doc_type=anything(), id=anything(),
                                            index='artifact', refresh='wait_for')
                    current_app.es = elastic_mock
                    self.syncer.delete()

                with it('doesnt crash'):
                    expect(current_app.es).to(have_been_satisfied)
