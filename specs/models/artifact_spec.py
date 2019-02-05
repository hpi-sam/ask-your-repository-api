"""Tests for the Artifact model"""
import datetime

from expects import expect, equal, be_a, raise_error, contain_only, contain
from mamba import describe, it, before, after
from neomodel import db

from application.models import Artifact
from specs.models.custom_matcher import be_uuid
from specs.spec_helpers import Context

with describe("Artifact Model") as self:
    with before.each:
        self.context = Context()

    with after.each:
        db.cypher_query("MATCH (a) DETACH DELETE a")
        if hasattr(self, 'context'):
            self.context.delete()

    with describe("Constructing"):
        with before.each:
            self.artifact = Artifact(file_url='asdf').save()
            self.artifact.refresh()

        with it('exists'):
            expect(Artifact.exists(file_url='asdf')).to(equal(True))

        with it('has correct file url'):
            expect(self.artifact.file_url).to(equal('asdf'))

        with describe("Default attributes"):
            with it('has a uuid'):
                expect(self.artifact.id_).to(be_uuid())

            with it('has a created_at timestamp'):
                expect(self.artifact.created_at).to(be_a(datetime.datetime))

            with it('has a updated_at timestamp'):
                expect(self.artifact.updated_at).to(be_a(datetime.datetime))

            with it('updated_at and created_at are equal'):
                expect(self.artifact.updated_at).to(equal(self.artifact.created_at))

    with describe("Updating"):
        with before.each:
            self.artifact = Artifact(file_url='asdf').save()
            self.artifact.update(file_url='blub')
            self.artifact.refresh()

        with it('updated the url'):
            expect(self.artifact.file_url).to(equal('blub'))

        with it('sets updated_at timestamp'):
            expect(self.artifact.updated_at).to_not(equal(self.artifact.created_at))

    with describe('finding'):
        with before.each:
            self.artifact1 = Artifact(file_url='asdf').save()
            self.artifact2 = Artifact(file_url='woop').save()
            self.artifact3 = Artifact(file_url='lulz')
        with describe('find by url'):
            with it('finds url asdf'):
                expect(Artifact.find_by(file_url='asdf')).to(equal(self.artifact1))
            with it('finds url woop'):
                expect(Artifact.find_by(file_url='woop')).to(equal(self.artifact2))
            with it('doesnt find url lulz'):
                expect(lambda: Artifact.find_by(file_url='lulz')).to(
                    raise_error(Artifact.DoesNotExist))  # pylint:disable=no-member
            with it('doesnt find url lmao'):
                expect(lambda: Artifact.find_by(file_url='lmao')).to(
                    raise_error(Artifact.DoesNotExist))  # pylint:disable=no-member

        with describe('find by id'):
            with it('finds artifact1'):
                expect(Artifact.find_by(id_=self.artifact1.id_)).to(equal(self.artifact1))
            with it('finds artifact2'):
                expect(Artifact.find_by(id_=self.artifact2.id_)).to(equal(self.artifact2))
            with it('doesnt find artifact3'):
                expect(lambda: Artifact.find_by(id_=self.artifact3.id_)).to(
                    raise_error(Artifact.DoesNotExist))  # pylint:disable=no-member

    with describe('Retrieving multiple'):
        with before.each:
            self.artifact1 = Artifact(file_url='asdf').save()
            self.artifact2 = Artifact(file_url='woop').save()
            self.artifact3 = Artifact(file_url='lulz')
            self.all_artifacts = Artifact.all()

        with it('returns list with all currently existing artifacts'):
            expect(self.all_artifacts).to(be_a(list))
            expect(self.all_artifacts).to(contain_only(self.artifact1, self.artifact2))
            expect(self.all_artifacts).to_not(contain(self.artifact3))
