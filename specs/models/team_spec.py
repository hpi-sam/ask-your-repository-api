"""Tests for the team model"""
import datetime

from expects import expect, equal, be_a, raise_error, contain_only, contain
from mamba import describe, it, before, after
from neomodel import db

from application.teams.team import Team
from specs.models.custom_matcher import be_uuid
from specs.spec_helpers import Context

with describe("Team Model") as self:
    with before.each:
        self.context = Context()

    with after.each:
        db.cypher_query("MATCH (a) DETACH DELETE a")
        if hasattr(self, "context"):
            self.context.delete()

    with describe("Constructing"):
        with before.each:
            self.team = Team(name="asdf").save()
            self.team.refresh()

        with it("exists"):
            expect(Team.exists(name="asdf")).to(equal(True))

        with it("has correct file url"):
            expect(self.team.name).to(equal("asdf"))

        with describe("Default attributes"):
            with it("has a uuid"):
                expect(self.team.id_).to(be_uuid())

            with it("has a created_at timestamp"):
                expect(self.team.created_at).to(be_a(datetime.datetime))

            with it("has a updated_at timestamp"):
                expect(self.team.updated_at).to(be_a(datetime.datetime))

            with it("updated_at and created_at are equal"):
                expect(self.team.updated_at).to(equal(self.team.created_at))

    with describe("Updating"):
        with before.each:
            self.team = Team(name="asdf").save()
            self.team.update(name="blub")
            self.team.refresh()

        with it("updated the url"):
            expect(self.team.name).to(equal("blub"))

        with it("sets updated_at timestamp"):
            expect(self.team.updated_at).to_not(equal(self.team.created_at))

    with describe("finding"):
        with before.each:
            self.team1 = Team(name="asdf").save()
            self.team2 = Team(name="woop").save()
            self.team3 = Team(name="lulz")
        with describe("find by url"):
            with it("finds url asdf"):
                expect(Team.find_by(name="asdf")).to(equal(self.team1))
            with it("finds url woop"):
                expect(Team.find_by(name="woop")).to(equal(self.team2))
            with it("doesnt find url lulz"):
                expect(lambda: Team.find_by(name="lulz")).to(raise_error(Team.DoesNotExist))  # pylint:disable=no-member
            with it("doesnt find url lmao"):
                expect(lambda: Team.find_by(name="lmao")).to(raise_error(Team.DoesNotExist))  # pylint:disable=no-member

        with describe("find by id"):
            with it("finds team1"):
                expect(Team.find_by(id_=self.team1.id_)).to(equal(self.team1))
            with it("finds team2"):
                expect(Team.find_by(id_=self.team2.id_)).to(equal(self.team2))
            with it("doesnt find team3"):
                expect(lambda: Team.find_by(id_=self.team3.id_)).to(
                    raise_error(Team.DoesNotExist)
                )  # pylint:disable=no-member

    with describe("Retrieving multiple"):
        with before.each:
            self.team1 = Team(name="asdf").save()
            self.team2 = Team(name="woop").save()
            self.team3 = Team(name="lulz")
            self.all_teams = Team.all()

        with it("returns list with all currently existing teams"):
            expect(self.all_teams).to(be_a(list))
            expect(self.all_teams).to(contain_only(self.team1, self.team2))
            expect(self.all_teams).to_not(contain(self.team3))
