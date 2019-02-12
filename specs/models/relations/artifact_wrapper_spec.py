""" Test the ArtifactBuilder class. Currently it's more of a wrapper than a builder sadly
    #refactor soon"""
from expects import expect, be_none, be_a, equal, contain
from mamba import description, before, after, it, context
from neomodel import db

from application.models.artifact import Artifact
from application.models.artifact_builder import ArtifactBuilder
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

        with it('creates a neo artifact'):
            expect(self.artifact.neo).to_not(be_none)
            expect(self.artifact.neo).to(be_a(Artifact))

    with description("Save"):
        with context('without tags'):
            with before.each:
                self.artifact = ArtifactBuilder()
                self.artifact.build_with(file_url='asdf', type='image')
                self.artifact.save()

            with it('saves it to neo4j'):
                expect(Artifact.exists(file_url='asdf')).to(equal(True))

        with context('with tags'):
            with before.each:
                self.artifact = ArtifactBuilder()
                self.artifact.build_with(file_url='asdf', type='image', tags=['a', 's', 'd', 'f'])
                self.artifact.save()

            with it('saves tags in Neo4j'):
                expect(self.artifact.neo.tags_list).to(contain('a', 's', 'd', 'f'))

    with description('find'):
        with before.each:
            self.artifact = ArtifactBuilder()
            self.artifact.build_with(file_url='asdf', type='image')
            ARTIFACT_ID = self.artifact.neo.id_
            self.artifact = ArtifactBuilder.find(id=ARTIFACT_ID, force=False)

        with it('finds in neo4j'):
            expect(self.artifact.neo.file_url).to(equal('asdf'))

    with description('update'):
        with context('file_url'):
            with before.each:
                self.artifact = ArtifactBuilder()
                self.artifact.build_with(file_url='asdf', type='image')
                self.artifact.save()
                self.artifact.update(file_url='blub')

            with it('updates in neo4j'):
                expect(Artifact.exists(file_url='blub')).to(equal(True))
                expect(Artifact.exists(file_url='asdf')).to(equal(False))

        with context('tags'):
            with before.each:
                self.artifact = ArtifactBuilder()
                self.artifact.build_with(file_url='asdf', type='image')
                self.artifact.save()
                self.artifact.update(tags=['a', 's', 'd', 'f'])

            with it('updates in neo4j'):
                ARTIFACT = Artifact.find_by(file_url='asdf')
                expect(ARTIFACT.tags_list).to(contain('a', 's', 'd', 'f'))

            with context('updating again'):
                with before.each:
                    self.artifact.update(tags=['l', 'm', 'a', 'o'])

                with it('saves new tags in neo4j'):
                    ARTIFACT = Artifact.find_by(file_url='asdf')
                    expect(ARTIFACT.tags_list).to(contain('a', 's', 'd', 'f', 'l', 'm', 'a', 'o'))

    with description('delete'):
        with before.each:
            self.artifact = ArtifactBuilder()
            self.artifact.build_with(file_url='asdf', type='image')
            self.artifact.save()
            self.artifact.delete()

        with it('deletes in neo4j'):
            expect(Artifact.exists(file_url='asdf')).to(equal(False))
