"""Tests for the Tag model"""
import datetime

from expects import expect, equal, be_a, raise_error, contain_only, contain
from mamba import describe, it, before, after
from neomodel import db, UniqueProperty

from application.artifacts.tags.tag import Tag
from specs.models.custom_matcher import be_uuid
from specs.spec_helpers import Context

with describe("Tag Model") as self:
    with before.each:
        self.context = Context()

    with after.each:
        db.cypher_query("MATCH (a) DETACH DELETE a")
        if hasattr(self, 'context'):
            self.context.delete()

    with describe("Constructing"):
        with before.each:
            self.tag = Tag(name='asdf').save()
            self.tag.refresh()

        with it('exists'):
            expect(Tag.exists(name='asdf')).to(equal(True))

        with it('has correct file url'):
            expect(self.tag.name).to(equal('asdf'))

        with describe("Default attributes"):
            with it('has a uuid'):
                expect(self.tag.id_).to(be_uuid())

            with it('has a created_at timestamp'):
                expect(self.tag.created_at).to(be_a(datetime.datetime))

            with it('has a updated_at timestamp'):
                expect(self.tag.updated_at).to(be_a(datetime.datetime))

            with it('updated_at and created_at are equal'):
                expect(self.tag.updated_at).to(equal(self.tag.created_at))

        with it('creating multiple with same name throws error'):
            expect(lambda: Tag(name='asdf').save()).to(raise_error(UniqueProperty))

    with describe("Updating"):
        with before.each:
            self.tag = Tag(name='asdf').save()
            self.tag.update(name='blub')
            self.tag.refresh()

        with it('updated the url'):
            expect(self.tag.name).to(equal('blub'))

        with it('sets updated_at timestamp'):
            expect(self.tag.updated_at).to_not(equal(self.tag.created_at))

    with describe('finding'):
        with before.each:
            self.tag1 = Tag(name='asdf').save()
            self.tag2 = Tag(name='woop').save()
            self.tag3 = Tag(name='lulz')
        with describe('find by url'):
            with it('finds url asdf'):
                expect(Tag.find_by(name='asdf')).to(equal(self.tag1))
            with it('finds url woop'):
                expect(Tag.find_by(name='woop')).to(equal(self.tag2))
            with it('doesnt find url lulz'):
                expect(lambda: Tag.find_by(name='lulz')).to(raise_error(Tag.DoesNotExist))  # pylint:disable=no-member
            with it('doesnt find url lmao'):
                expect(lambda: Tag.find_by(name='lmao')).to(raise_error(Tag.DoesNotExist))  # pylint:disable=no-member

        with describe('find by id'):
            with it('finds tag1'):
                expect(Tag.find_by(id_=self.tag1.id_)).to(equal(self.tag1))
            with it('finds tag2'):
                expect(Tag.find_by(id_=self.tag2.id_)).to(equal(self.tag2))
            with it('doesnt find tag3'):
                expect(lambda: Tag.find_by(id_=self.tag3.id_)).to(raise_error(Tag.DoesNotExist))  # pylint:disable=no-member

    with describe('Retrieving multiple'):
        with before.each:
            self.tag1 = Tag(name='asdf').save()
            self.tag2 = Tag(name='woop').save()
            self.tag3 = Tag(name='lulz')
            self.all_tags = Tag.all()

        with it('returns list with all currently existing tags'):
            expect(self.all_tags).to(be_a(list))
            expect(self.all_tags).to(contain_only(self.tag1, self.tag2))
            expect(self.all_tags).to_not(contain(self.tag3))
