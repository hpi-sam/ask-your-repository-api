from application.users.user import User


class UserFactory:
    @classmethod
    def create_user(cls, *args, **kwargs):
        return cls.build_user(*args, **kwargs).save()

    @classmethod
    def build_user(cls, username="TestUser", email="test@example.com"):
        return User(username=username, email=email, password="test")
