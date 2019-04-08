from application.teams.team import Team
from specs.factories.user_factory import UserFactory


class TeamFactory:
    @classmethod
    def create_team(cls, *args, **kwargs):
        return cls.build_team(*args, **kwargs).save()

    @classmethod
    def build_team(cls, name="test", join_key="a1c1b2ad-c13e-4f9f-85c7-eb51efc189a6", members=[], traits=[]):
        team = Team(name=name, join_key=join_key).save()
        if "with_members" in traits:
            cls._add_members_to_team(team, 2)
        for member in members:
            team.members.connect(member)
        return team

    @classmethod
    def add_members_to_team(cls, team, amount):
        for i in range(amount):
            team.members.connect(UserFactory.create_user(username=f"TestUser{i}", email=f"test{i}@example.com"))
